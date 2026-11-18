from __future__ import annotations

from argumind_nlp.dag_decoder import DecodedEdge, ExtractedNode, run_stage_1_structure


def build_implicit_and_gaps(
    nodes: list[ExtractedNode],
    edges: list[DecodedEdge],
    generate_counterarguments: bool = True,
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    """Bangun ImplicitPremise/Counterargument, ReasoningGap, dan RubricScore."""
    node_dicts: list[dict[str, object]] = [
        {
            "node_key": n.node_key,
            "node_type": n.node_type,
            "start_char": n.start_char,
            "end_char": n.end_char,
            "text_content": n.text_content,
            "evidence_strength": n.evidence_strength,
            "target_node_key": None,
            "user_feedback": "PENDING",
        }
        for n in nodes
    ]
    edge_dicts: list[dict[str, object]] = [
        {
            "edge_key": e.edge_key,
            "source_key": e.source_key,
            "target_key": e.target_key,
            "relation_type": e.relation_type,
            "confidence": e.confidence,
            "nli_probs": e.nli_probs,
        }
        for e in edges
    ]
    gaps: list[dict[str, object]] = []

    claims = [n for n in nodes if n.node_type == "Claim"]
    evidences = [n for n in nodes if n.node_type == "Evidence"]
    support_targets = {e.target_key for e in edges if e.relation_type == "Support"}

    # F-03: Deteksi ImplicitPremise pada edge Support berketidakpastian >= 0.40
    ip_idx = 1
    gap_idx = 1
    for e in edges:
        uncertain = float(e.nli_probs.get("neutral", 0.0)) + float(
            e.nli_probs.get("contradict", 0.0)
        )
        if e.relation_type == "Support" and uncertain >= 0.30:
            ip_key = f"IP-{ip_idx:02d}"
            node_dicts.append(
                {
                    "node_key": ip_key,
                    "node_type": "ImplicitPremise",
                    "start_char": None,
                    "end_char": None,
                    "text_content": (
                        f"Asumsi penghubung diperlukan agar {e.source_key} "
                        f"memvalidasi {e.target_key}."
                    ),
                    "evidence_strength": None,
                    "target_node_key": e.target_key,
                    "user_feedback": "PENDING",
                }
            )
            gaps.append(
                {
                    "gap_key": f"G-{gap_idx:02d}",
                    "gap_type": "HastyGeneralization",
                    "severity": "Medium",
                    "target_node_key": None,
                    "target_edge_key": e.edge_key,
                    "explanation": f"Relasi {e.edge_key} memerlukan penguatan asumsi {ip_key}.",
                }
            )
            ip_idx += 1
            gap_idx += 1

    for c in claims:
        if c.node_key not in support_targets:
            gaps.append(
                {
                    "gap_key": f"G-{gap_idx:02d}",
                    "gap_type": "UnsupportedClaim",
                    "severity": "High",
                    "target_node_key": c.node_key,
                    "target_edge_key": None,
                    "explanation": f"Klaim {c.node_key} belum ditopang premis/bukti eksplisit.",
                }
            )
            gap_idx += 1

    if not evidences and claims:
        gaps.append(
            {
                "gap_key": f"G-{gap_idx:02d}",
                "gap_type": "WeakEvidence",
                "severity": "High",
                "target_node_key": claims[0].node_key,
                "target_edge_key": None,
                "explanation": "Dokumen belum menyertakan bukti empiris atau data terukur.",
            }
        )
        gap_idx += 1

    if generate_counterarguments and claims:
        node_dicts.append(
            {
                "node_key": "CA-01",
                "node_type": "Counterargument",
                "start_char": None,
                "end_char": None,
                "text_content": (
                    f"Pertimbangkan skenario pengecualian terhadap klaim {claims[0].node_key}."
                ),
                "evidence_strength": None,
                "target_node_key": claims[0].node_key,
                "user_feedback": "PENDING",
            }
        )

    return node_dicts, edge_dicts, gaps


def compute_graph_grounded_scores(
    nodes: list[dict[str, object]],
    edges: list[dict[str, object]],
    gaps: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Hitung skor rubrik 4 dimensi dengan grounded_refs wajib non-kosong (F-04)."""
    node_keys = [str(n["node_key"]) for n in nodes]
    claim_keys = [str(n["node_key"]) for n in nodes if n["node_type"] == "Claim"]
    premise_keys = [str(n["node_key"]) for n in nodes if n["node_type"] == "ExplicitPremise"]
    evidence_keys = [str(n["node_key"]) for n in nodes if n["node_type"] == "Evidence"]
    attack_keys = [str(e["edge_key"]) for e in edges if e["relation_type"] == "Attack"]
    gap_keys = [str(g["gap_key"]) for g in gaps]
    fallback_ref = node_keys[0] if node_keys else "N-01"

    clarity_score = 4 if claim_keys else 2
    coherence_score = max(1, min(5, 3 + (1 if len(edges) >= 2 else 0) - min(2, len(gaps))))
    evidence_score = max(1, min(5, 1 + len(evidence_keys)))
    counter_score = 4 if attack_keys else 2

    return [
        {
            "dimension": "ClarityOfClaim",
            "ai_score": clarity_score,
            "grounded_refs": claim_keys[:3] or [fallback_ref],
            "rationale": f"Teridentifikasi {len(claim_keys)} klaim eksplisit pada argumen.",
            "human_override_score": None,
            "reviewer_id": None,
            "override_note": None,
        },
        {
            "dimension": "PremiseSupportAndCoherence",
            "ai_score": coherence_score,
            "grounded_refs": (premise_keys[:2] + gap_keys[:2]) or [fallback_ref],
            "rationale": f"Terdapat {len(edges)} relasi argumen dan {len(gaps)} celah penalaran.",
            "human_override_score": None,
            "reviewer_id": None,
            "override_note": None,
        },
        {
            "dimension": "EvidenceAdequacy",
            "ai_score": evidence_score,
            "grounded_refs": (evidence_keys[:3] or gap_keys[:1] or [fallback_ref]),
            "rationale": f"Dokumen memuat {len(evidence_keys)} komponen bukti terstruktur.",
            "human_override_score": None,
            "reviewer_id": None,
            "override_note": None,
        },
        {
            "dimension": "CounterargumentAndLimitationAwareness",
            "ai_score": counter_score,
            "grounded_refs": attack_keys[:2] or [fallback_ref],
            "rationale": (
                "Argumen mempertimbangkan sudut pandang tandingan."
                if attack_keys
                else "Belum ditemukan pembahasan kontraargumen eksplisit di dalam teks."
            ),
            "human_override_score": None,
            "reviewer_id": None,
            "override_note": None,
        },
    ]


def analyze_clean_text(
    clean_text: str, generate_counterarguments: bool = True
) -> tuple[
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
]:
    """Jalankan pipeline penuh F-01 s.d. F-04 secara deterministik."""
    nodes, edges = run_stage_1_structure(clean_text)
    node_dicts, edge_dicts, gaps = build_implicit_and_gaps(nodes, edges, generate_counterarguments)
    scores = compute_graph_grounded_scores(node_dicts, edge_dicts, gaps)
    return node_dicts, edge_dicts, gaps, scores
