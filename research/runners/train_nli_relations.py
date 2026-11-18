from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from argumind_metrics import RelationTriple, macro_f1_relations
from argumind_nlp.dag_decoder import ExtractedNode, decode_minimum_spanning_dag
from argumind_nlp.preprocessing import generate_relation_candidates

from research.runners.determinism import load_corpus_split, set_global_seed, verify_manifest_sha256

REL_LABELS: tuple[str, ...] = ("Support", "Attack", "NoRelation")
REL_TO_ID: dict[str, int] = {lbl: idx for idx, lbl in enumerate(REL_LABELS)}
ID_TO_REL: dict[int, str] = {idx: lbl for idx, lbl in enumerate(REL_LABELS)}


def build_relation_pairs(
    data_dir: Path, split: str, max_para_distance: int = 3
) -> tuple[list[dict[str, Any]], list[RelationTriple]]:
    """Bangun pasangan kandidat (source, target) beserta label Support/Attack/NoRelation."""
    docs, by_doc_nodes, by_doc_edges, _, _ = load_corpus_split(data_dir, split)
    pairs: list[dict[str, Any]] = []
    golds: list[RelationTriple] = []

    for doc_id, doc in docs.items():
        offsets = doc.get("paragraph_offsets", [])
        doc_nodes = [
            n
            for n in by_doc_nodes.get(doc_id, [])
            if n.get("start_char") is not None
            and n["node_type"] in {"Claim", "ExplicitPremise", "Evidence"}
        ]
        node_map = {str(n["node_id"]): n for n in doc_nodes}
        edge_lookup: dict[tuple[str, str], str] = {}
        for e in by_doc_edges.get(doc_id, []):
            src, tgt, rel = (
                str(e["source_node_id"]),
                str(e["target_node_id"]),
                str(e["relation_type"]),
            )
            edge_lookup[(src, tgt)] = rel
            if rel in {"Support", "Attack"}:
                golds.append(RelationTriple(doc_id, src, tgt, rel))

        def _find_para(start_char: int, para_offsets: list[dict[str, Any]]) -> int:
            for s in para_offsets:
                if int(s["start_char"]) <= start_char <= int(s["end_char"]):
                    return int(s["para_id"])
            return 1

        node_para = [
            (str(n["node_id"]), _find_para(int(n["start_char"]), offsets)) for n in doc_nodes
        ]
        for src_id, tgt_id in generate_relation_candidates(node_para, max_para_distance):
            label_str = edge_lookup.get((src_id, tgt_id), "NoRelation")
            pairs.append(
                {
                    "doc_id": doc_id,
                    "source_id": src_id,
                    "target_id": tgt_id,
                    "text_a": str(node_map[src_id]["text_content"]),
                    "text_b": str(node_map[tgt_id]["text_content"]),
                    "label": REL_TO_ID[label_str],
                }
            )
    return pairs, golds


def train_nli_relations(
    data_dir: Path,
    output_dir: Path,
    model_name: str = "indobenchmark/indobert-base-p2",
    seed: int = 42,
    epochs: int = 8,
    batch_size: int = 16,
    lr: float = 2e-5,
) -> dict[str, Any]:
    """Fine-tuning Cross-Encoder NLI + Class-Weighted Loss & Dekode Chu-Liu/Edmonds (F-02)."""
    import numpy as np
    import torch
    from torch.utils.data import DataLoader
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    set_global_seed(seed)
    verify_manifest_sha256(data_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name, num_labels=len(REL_LABELS), id2label=ID_TO_REL, label2id=REL_TO_ID
    ).to(device)

    train_pairs, _ = build_relation_pairs(data_dir, "train")
    dev_pairs, dev_golds = build_relation_pairs(data_dir, "dev")
    test_pairs, test_golds = build_relation_pairs(data_dir, "test")

    counts = np.bincount([int(p["label"]) for p in train_pairs], minlength=3).astype(np.float32)
    counts = np.maximum(counts, 1.0)
    weights = torch.tensor(
        counts.sum() / (len(REL_LABELS) * counts), dtype=torch.float32, device=device
    )
    loss_fn = torch.nn.CrossEntropyLoss(weight=weights)

    def _collate(batch: list[dict[str, Any]]) -> dict[str, Any]:
        enc = tokenizer(
            [x["text_a"] for x in batch],
            [x["text_b"] for x in batch],
            truncation=True,
            padding=True,
            max_length=256,
            return_tensors="pt",
        )
        enc["labels"] = torch.tensor([x["label"] for x in batch], dtype=torch.long)
        return dict(enc)

    train_loader = DataLoader(train_pairs, batch_size=batch_size, shuffle=True, collate_fn=_collate)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)

    def _eval_split(pairs: list[dict[str, Any]], golds: list[RelationTriple]) -> dict[str, float]:
        model.eval()
        by_doc: dict[str, list[tuple[str, str, str, float, dict[str, float]]]] = {}
        doc_nodes_seen: dict[str, set[str]] = {}
        with torch.no_grad():
            for p in pairs:
                enc = tokenizer(
                    p["text_a"], p["text_b"], truncation=True, max_length=256, return_tensors="pt"
                ).to(device)
                probs = torch.softmax(model(**enc).logits[0], dim=-1).cpu().tolist()
                pred_idx = int(np.argmax(probs))
                rel_name = ID_TO_REL[pred_idx]
                conf = float(probs[pred_idx])
                did = str(p["doc_id"])
                by_doc.setdefault(did, []).append(
                    (
                        str(p["source_id"]),
                        str(p["target_id"]),
                        rel_name,
                        conf,
                        {
                            "entail": float(probs[0]),
                            "neutral": float(probs[2]),
                            "contradict": float(probs[1]),
                        },
                    )
                )
                doc_nodes_seen.setdefault(did, set()).update(
                    [str(p["source_id"]), str(p["target_id"])]
                )

        decoded_preds: list[RelationTriple] = []
        for did, scored in by_doc.items():
            dummy_nodes = [
                ExtractedNode(nk, "Claim", 0, 1, "", 1, None) for nk in sorted(doc_nodes_seen[did])
            ]
            for edge in decode_minimum_spanning_dag(dummy_nodes, scored):
                decoded_preds.append(
                    RelationTriple(did, edge.source_key, edge.target_key, edge.relation_type)
                )
        return macro_f1_relations(decoded_preds, golds)

    best_f1 = -1.0
    ckpt_dir = output_dir / "best_nli_model"
    for _epoch in range(1, epochs + 1):
        model.train()
        for batch in train_loader:
            optimizer.zero_grad()
            logits = model(
                input_ids=batch["input_ids"].to(device),
                attention_mask=batch["attention_mask"].to(device),
            ).logits
            loss = loss_fn(logits, batch["labels"].to(device))
            loss.backward()
            optimizer.step()
        dev_res = _eval_split(dev_pairs, dev_golds)
        if dev_res["macro_f1"] > best_f1:
            best_f1 = dev_res["macro_f1"]
            model.save_pretrained(ckpt_dir)
            tokenizer.save_pretrained(ckpt_dir)

    if ckpt_dir.exists():
        model = AutoModelForSequenceClassification.from_pretrained(ckpt_dir).to(device)
    test_res = _eval_split(test_pairs, test_golds)
    summary = {
        "model_name": model_name,
        "seed": seed,
        "dev_best_relation_macro_f1": best_f1,
        "test_relation_macro_f1": test_res,
        "checkpoint_dir": str(ckpt_dir),
    }
    (output_dir / "eval_nli.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fine-tune Cross-Encoder NLI Relation Classifier (F-02)"
    )
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--model-name", type=str, default="indobenchmark/indobert-base-p2")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=2e-5)
    args = parser.parse_args()
    res = train_nli_relations(
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        model_name=args.model_name,
        seed=args.seed,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
    )
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
