from __future__ import annotations

import argparse
import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import networkx as nx
from argumind_metrics import (
    ComponentSpan,
    FaithfulnessIntervention,
    RelationTriple,
    counterfactual_faithfulness_rate,
    macro_f1_components,
    macro_f1_relations,
    partial_length_correlation,
    quadratic_weighted_kappa,
    spearman_correlation,
)
from argumind_nlp.dag_decoder import run_stage_1_structure
from argumind_nlp.reasoning import analyze_clean_text

from research.runners.determinism import load_corpus_split, set_global_seed, verify_manifest_sha256
from research.runners.hf_inference import predict_with_hf_models


def _run_e01(
    data_dir: Path,
    split: str,
    arch: str,
    output_dir: Path,
    bio_model_dir: Path | None = None,
    nli_model_dir: Path | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    docs, by_doc_nodes, by_doc_edges, _, _ = load_corpus_split(data_dir, split)
    pred_spans: list[ComponentSpan] = []
    gold_spans: list[ComponentSpan] = []
    pred_rels: list[RelationTriple] = []
    gold_rels: list[RelationTriple] = []
    predictions: list[dict[str, Any]] = []
    cycle_violations = 0

    for doc_id, doc in docs.items():
        clean_text = str(doc["clean_text"])
        if bio_model_dir is not None and bio_model_dir.exists():
            doc_spans, doc_rels = predict_with_hf_models(
                doc_id, clean_text, bio_model_dir, nli_model_dir
            )
            pred_spans.extend(doc_spans)
            pred_rels.extend(doc_rels)
            n_pred_nodes, n_pred_edges = len(doc_spans), len(doc_rels)
        else:
            nodes, edges = run_stage_1_structure(clean_text)
            g = nx.DiGraph()
            for n in nodes:
                if n.node_type in {"Claim", "ExplicitPremise", "Evidence"}:
                    pred_spans.append(ComponentSpan(doc_id, n.start_char, n.end_char, n.node_type))
                g.add_node(n.node_key)
            for e in edges:
                src_k = (
                    e.source_key
                    if e.source_key.startswith(f"{doc_id}_")
                    else f"{doc_id}_{e.source_key}"
                )
                tgt_k = (
                    e.target_key
                    if e.target_key.startswith(f"{doc_id}_")
                    else f"{doc_id}_{e.target_key}"
                )
                pred_rels.append(
                    RelationTriple(doc_id, src_k, tgt_k, e.relation_type)
                )
                if e.relation_type == "Support":
                    g.add_edge(e.source_key, e.target_key)
            if not nx.is_directed_acyclic_graph(g):
                cycle_violations += 1
            n_pred_nodes, n_pred_edges = len(nodes), len(edges)

        for gn in by_doc_nodes.get(doc_id, []):
            if gn.get("start_char") is not None and gn["node_type"] in {
                "Claim",
                "ExplicitPremise",
                "Evidence",
            }:
                gold_spans.append(
                    ComponentSpan(
                        doc_id, int(gn["start_char"]), int(gn["end_char"]), str(gn["node_type"])
                    )
                )
        for ge in by_doc_edges.get(doc_id, []):
            gold_rels.append(
                RelationTriple(
                    doc_id,
                    str(ge["source_node_id"]),
                    str(ge["target_node_id"]),
                    str(ge["relation_type"]),
                )
            )
        predictions.append(
            {"doc_id": doc_id, "arch": arch, "pred_nodes": n_pred_nodes, "pred_edges": n_pred_edges}
        )

    comp_exact = macro_f1_components(pred_spans, gold_spans, iou_threshold=1.0)
    comp_p50 = macro_f1_components(pred_spans, gold_spans, iou_threshold=0.5)
    rel_f1 = macro_f1_relations(pred_rels, gold_rels)
    metrics = {
        "component_macro_f1_exact": comp_exact["macro_f1"],
        "component_macro_f1_iou50": comp_p50["macro_f1"],
        "relation_macro_f1": rel_f1["macro_f1"],
        "cycle_rate": float(cycle_violations / max(1, len(docs))),
        "n_docs": len(docs),
    }
    return predictions, metrics


def _run_e03(
    data_dir: Path, split: str, arch: str, exp_id: str
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    docs, _, _, _, by_doc_scores = load_corpus_split(data_dir, split)
    sys_vals: list[int] = []
    gold_vals: list[int] = []
    doc_sys_avg: list[float] = []
    doc_gold_avg: list[float] = []
    word_counts: list[int] = []
    interventions: list[FaithfulnessIntervention] = []
    predictions: list[dict[str, Any]] = []

    for doc_id, doc in docs.items():
        clean_text = str(doc["clean_text"])
        nodes, edges, gaps, scores = analyze_clean_text(clean_text, generate_counterarguments=True)
        score_map = {str(s["dimension"]): int(s["ai_score"]) for s in scores}
        refs_map = {
            str(s["dimension"]): tuple(str(r) for r in list(s["grounded_refs"])) for s in scores
        }

        doc_s: list[int] = []
        doc_g: list[int] = []
        for gs in by_doc_scores.get(doc_id, []):
            dim = str(gs["dimension"])
            if dim in score_map:
                sys_vals.append(score_map[dim])
                gold_vals.append(int(gs["gold_score"]))
                doc_s.append(score_map[dim])
                doc_g.append(int(gs["gold_score"]))
        if doc_s and doc_g:
            doc_sys_avg.append(sum(doc_s) / len(doc_s))
            doc_gold_avg.append(sum(doc_g) / len(doc_g))
            word_counts.append(int(doc["word_count"]))

        # Counterfactual ablation untuk E-03b: hapus span node Evidence pertama dari teks
        ev_node = next(
            (n for n in nodes if n["node_type"] == "Evidence" and n["start_char"] is not None), None
        )
        if ev_node is not None:
            s_c, e_c = int(ev_node["start_char"]), int(ev_node["end_char"])
            ablated_text = (clean_text[:s_c] + " " + clean_text[e_c:]).strip()
            _, _, _, ablated_scores = analyze_clean_text(
                ablated_text, generate_counterarguments=True
            )
            ab_map = {str(s["dimension"]): int(s["ai_score"]) for s in ablated_scores}
            ab_refs = {
                str(s["dimension"]): tuple(str(r) for r in list(s["grounded_refs"]))
                for s in ablated_scores
            }
            ev_dim = "EvidenceAdequacy"
            interventions.append(
                FaithfulnessIntervention(
                    score_before=score_map[ev_dim],
                    score_after=ab_map[ev_dim],
                    deleted_node_key=str(ev_node["node_key"]),
                    grounded_refs_after=ab_refs[ev_dim],
                )
            )
            _ = refs_map

        predictions.append({"doc_id": doc_id, "arch": arch, "scores": scores, "n_gaps": len(gaps)})

    qwk = quadratic_weighted_kappa(gold_vals, sys_vals) if sys_vals else 0.0
    rho = spearman_correlation(doc_gold_avg, doc_sys_avg) if len(doc_sys_avg) >= 2 else 0.0
    len_corr = (
        partial_length_correlation(doc_sys_avg, doc_gold_avg, word_counts)
        if len(doc_sys_avg) >= 2
        else 0.0
    )
    faith = counterfactual_faithfulness_rate(interventions) if interventions else 0.0
    metrics = {
        "exp_id": exp_id,
        "qwk_score": qwk,
        "spearman_rho": rho,
        "partial_corr_length": len_corr,
        "faithfulness_rate": faith,
        "n_interventions": len(interventions),
    }
    return predictions, metrics


def run_experiment(
    exp_id: str,
    arch: str,
    data_dir: Path,
    split: str,
    seed: int,
    output_dir: Path,
    bio_model_dir: Path | None = None,
    nli_model_dir: Path | None = None,
) -> dict[str, Any]:
    """Runner standar eksperimen sesuai EXPERIMENT_PLAN.md#3 & REPRODUCIBILITY.md."""
    t0 = time.perf_counter()
    set_global_seed(seed)
    manifest_hashes = verify_manifest_sha256(data_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if exp_id in {"E-01", "E-02a", "E-02b"}:
        predictions, metrics = _run_e01(
            data_dir, split, arch, output_dir, bio_model_dir, nli_model_dir
        )
    elif exp_id in {"E-03a", "E-03b"}:
        predictions, metrics = _run_e03(data_dir, split, arch, exp_id)
    else:
        raise ValueError(f"exp_id tidak dikenali: {exp_id}")

    duration_ms = round((time.perf_counter() - t0) * 1000.0, 2)
    metrics["latency_total_ms"] = duration_ms

    config = {
        "exp_id": exp_id,
        "arch": arch,
        "split": split,
        "seed": seed,
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "manifest_sha256": manifest_hashes,
    }
    (output_dir / "config_locked.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    (output_dir / "predictions.jsonl").write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in predictions) + "\n",
        encoding="utf-8",
    )
    (output_dir / "metrics_raw.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    log_msg = (
        f"[{config['timestamp_utc']}] COMPLETED exp={exp_id} "
        f"arch={arch} seed={seed} duration_ms={duration_ms}\n"
    )
    (output_dir / "run.log").write_text(log_msg, encoding="utf-8")
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Argumind Standard Experiment Runner")
    parser.add_argument(
        "--exp-id", required=True, choices=["E-01", "E-02a", "E-02b", "E-03a", "E-03b"]
    )
    parser.add_argument("--arch", required=True)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--split", default="test", choices=["train", "dev", "test"])
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--graph-source", default="predicted")
    parser.add_argument("--pred-graph-dir", type=Path, default=None)
    parser.add_argument("--bio-model-dir", type=Path, default=None)
    parser.add_argument("--nli-model-dir", type=Path, default=None)
    args = parser.parse_args()
    metrics = run_experiment(
        exp_id=args.exp_id,
        arch=args.arch,
        data_dir=args.data_dir,
        split=args.split,
        seed=args.seed,
        output_dir=args.output_dir,
        bio_model_dir=args.bio_model_dir,
        nli_model_dir=args.nli_model_dir,
    )
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
