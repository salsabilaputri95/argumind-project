from __future__ import annotations

import hashlib
import json
from pathlib import Path


def _build_doc_entry(
    doc_id: str, split: str, strata: str, author_idx: int, claim: str, premise: str, evidence: str
) -> tuple[
    dict[str, object],
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
]:
    filler = (
        "Analisis kebijakan transportasi perkotaan memerlukan perencanaan anggaran jangka panjang "
        "yang transparan. Kualitas layanan publik bergantung pada sinkronisasi regulasi daerah, "
        "kesiapan infrastruktur, serta pengawasan partisipatif. "
    ) * 18
    clean_text = f"{claim} {premise} {evidence}\n\n{filler}".strip()
    c_start, c_end = 0, len(claim)
    p_start = c_end + 1
    p_end = p_start + len(premise)
    e_start = p_end + 1
    e_end = e_start + len(evidence)
    words = len(clean_text.split())
    doc = {
        "doc_id": doc_id,
        "split": split,
        "anon_author_id": f"anon_author_{author_idx:012x}",
        "anon_source_org": "org_acad_01" if strata == "academic" else "org_pol_01",
        "domain_strata": strata,
        "length_strata": "short" if words <= 800 else "medium",
        "word_count": words,
        "char_length": len(clean_text),
        "clean_text": clean_text,
        "paragraph_offsets": [
            {"para_id": 1, "sent_id": "S-01", "start_char": c_start, "end_char": c_end},
            {"para_id": 1, "sent_id": "S-02", "start_char": p_start, "end_char": p_end},
            {"para_id": 1, "sent_id": "S-03", "start_char": e_start, "end_char": e_end},
        ],
    }
    nodes = [
        {
            "node_id": f"{doc_id}_N-01",
            "doc_id": doc_id,
            "node_type": "Claim",
            "start_char": c_start,
            "end_char": c_end,
            "text_content": claim,
            "evidence_strength": None,
            "target_node_id": None,
        },
        {
            "node_id": f"{doc_id}_N-02",
            "doc_id": doc_id,
            "node_type": "ExplicitPremise",
            "start_char": p_start,
            "end_char": p_end,
            "text_content": premise,
            "evidence_strength": None,
            "target_node_id": None,
        },
        {
            "node_id": f"{doc_id}_N-03",
            "doc_id": doc_id,
            "node_type": "Evidence",
            "start_char": e_start,
            "end_char": e_end,
            "text_content": evidence,
            "evidence_strength": 4,
            "target_node_id": None,
        },
    ]
    edges = [
        {
            "edge_id": f"{doc_id}_E-01",
            "doc_id": doc_id,
            "source_node_id": f"{doc_id}_N-02",
            "target_node_id": f"{doc_id}_N-01",
            "relation_type": "Support",
        },
        {
            "edge_id": f"{doc_id}_E-02",
            "doc_id": doc_id,
            "source_node_id": f"{doc_id}_N-03",
            "target_node_id": f"{doc_id}_N-02",
            "relation_type": "Support",
        },
    ]
    gaps = [
        {
            "gap_id": f"{doc_id}_G-01",
            "doc_id": doc_id,
            "gap_type": "MissingCounterargumentConsideration",
            "severity": "Medium",
            "target_ref": f"{doc_id}_N-01",
        },
    ]
    scores = [
        {
            "doc_id": doc_id,
            "dimension": "ClarityOfClaim",
            "gold_score": 4,
            "expert_rater_scores": [4, 4, 4] if split == "test" else None,
            "grounded_refs": [f"{doc_id}_N-01"],
        },
        {
            "doc_id": doc_id,
            "dimension": "PremiseSupportAndCoherence",
            "gold_score": 4,
            "expert_rater_scores": [4, 3, 4] if split == "test" else None,
            "grounded_refs": [f"{doc_id}_N-02"],
        },
        {
            "doc_id": doc_id,
            "dimension": "EvidenceAdequacy",
            "gold_score": 4,
            "expert_rater_scores": [4, 4, 4] if split == "test" else None,
            "grounded_refs": [f"{doc_id}_N-03"],
        },
        {
            "doc_id": doc_id,
            "dimension": "CounterargumentAndLimitationAwareness",
            "gold_score": 2,
            "expert_rater_scores": [2, 2, 3] if split == "test" else None,
            "grounded_refs": [f"{doc_id}_G-01"],
        },
    ]
    return doc, nodes, edges, gaps, scores


def write_seed_corpus(target_dir: Path) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    specs = [
        ("doc_0001", "train", "academic", 1),
        ("doc_0002", "train", "policy_business", 2),
        ("doc_0003", "train", "academic", 3),
        ("doc_0004", "train", "policy_business", 4),
        ("doc_0005", "train", "academic", 5),
        ("doc_0006", "train", "policy_business", 6),
        ("doc_0007", "train", "academic", 7),
        ("doc_0008", "train", "policy_business", 8),
        ("doc_0009", "dev", "academic", 9),
        ("doc_0010", "dev", "policy_business", 10),
        ("doc_0011", "test", "academic", 11),
        ("doc_0012", "test", "policy_business", 12),
    ]
    all_docs, all_nodes, all_edges, all_gaps, all_scores = [], [], [], [], []
    for doc_id, split, strata, idx in specs:
        claim = (
            "Pemerintah daerah wajib memperluas jalur transportasi umum berbasis rel "
            "untuk menekan emisi."
        )
        premise = (
            "Peningkatan kapasitas angkutan massal mengurangi ketergantungan pekerja "
            "pada kendaraan pribadi."
        )
        evidence = (
            "Berdasarkan laporan BPS 2025, biaya komuter menyerap 28% pendapatan pekerja perkotaan."
        )
        d, ns, es, gs, scs = _build_doc_entry(doc_id, split, strata, idx, claim, premise, evidence)
        all_docs.append(d)
        all_nodes.extend(ns)
        all_edges.extend(es)
        all_gaps.extend(gs)
        all_scores.extend(scs)

    files = {
        "documents.jsonl": all_docs,
        "nodes.jsonl": all_nodes,
        "edges.jsonl": all_edges,
        "gaps.jsonl": all_gaps,
        "rubric_scores.jsonl": all_scores,
    }
    manifest_lines: list[str] = []
    for fname, rows in files.items():
        fpath = target_dir / fname
        content_bytes = ("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n").encode(
            "utf-8"
        )
        fpath.write_bytes(content_bytes)
        digest = hashlib.sha256(content_bytes).hexdigest()
        manifest_lines.append(f"{digest}  {fname}")
    (target_dir / "manifest.sha256").write_bytes(
        ("\n".join(manifest_lines) + "\n").encode("utf-8")
    )


if __name__ == "__main__":
    write_seed_corpus(Path("research/data/processed/v1.0"))
