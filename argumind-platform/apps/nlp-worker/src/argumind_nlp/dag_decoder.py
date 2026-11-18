from __future__ import annotations

import re
from dataclasses import dataclass

import networkx as nx

from argumind_nlp.preprocessing import SentenceSpan, generate_relation_candidates, segment_sentences

EVIDENCE_MARKERS = re.compile(
    r"\b(?:berdasarkan|menurut|data|bps|survei|studi|penelitian|laporan|uu\s+no|pasal|%\b|\d{4})\b",
    re.IGNORECASE,
)
CLAIM_MARKERS = re.compile(
    r"\b(?:harus|wajib|perlu|seharusnya|kesimpulannya|oleh\s+karena\s+itu|dengan\s+demikian|menunjukkan\s+bahwa|mengakibatkan)\b",
    re.IGNORECASE,
)
ATTACK_MARKERS = re.compile(
    r"\b(?:namun|tetapi|sebaliknya|akan\s+tetapi|di\s+sisi\s+lain|menolak|membantah|meskipun|kritik)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ExtractedNode:
    node_key: str
    node_type: str
    start_char: int
    end_char: int
    text_content: str
    para_id: int
    evidence_strength: int | None


@dataclass(frozen=True)
class DecodedEdge:
    edge_key: str
    source_key: str
    target_key: str
    relation_type: str
    confidence: float
    nli_probs: dict[str, float]


def classify_sentence_component(
    sentence: SentenceSpan, is_boundary: bool
) -> tuple[str, int | None]:
    """Klasifikasi heuristik awal komponen argumen (fallback saat IndoBERT belum dimuat)."""
    text = sentence.text
    if EVIDENCE_MARKERS.search(text):
        has_num = bool(re.search(r"\d+(?:[.,]\d+)?%?", text))
        return "Evidence", 4 if has_num else 3
    if CLAIM_MARKERS.search(text) or is_boundary:
        return "Claim", None
    return "ExplicitPremise", None


def extract_components(sentences: tuple[SentenceSpan, ...]) -> list[ExtractedNode]:
    """Ekstrak daftar komponen argumen berindeks karakter valid dari kalimat tersegmentasi."""
    nodes: list[ExtractedNode] = []
    total = len(sentences)
    for idx, sent in enumerate(sentences):
        node_type, ev_strength = classify_sentence_component(sent, idx == 0 or idx == total - 1)
        nodes.append(
            ExtractedNode(
                node_key=f"N-{idx + 1:02d}",
                node_type=node_type,
                start_char=sent.start_char,
                end_char=sent.end_char,
                text_content=sent.text,
                para_id=sent.para_id,
                evidence_strength=ev_strength,
            )
        )
    return nodes


def score_candidate_edge(
    src: ExtractedNode, tgt: ExtractedNode
) -> tuple[str, float, dict[str, float]]:
    """Skor pasangan kandidat (source -> target) beserta distribusi probabilitas NLI."""
    if src.node_key == tgt.node_key:
        return "NoRelation", 0.0, {"entail": 0.0, "neutral": 1.0, "contradict": 0.0}
    if tgt.node_type != "Claim" and src.node_type == "Claim":
        return "NoRelation", 0.15, {"entail": 0.15, "neutral": 0.75, "contradict": 0.10}
    if ATTACK_MARKERS.search(src.text_content) and tgt.node_type == "Claim":
        return "Attack", 0.82, {"entail": 0.08, "neutral": 0.10, "contradict": 0.82}
    if src.node_type in {"ExplicitPremise", "Evidence"} and tgt.node_type in {
        "Claim",
        "ExplicitPremise",
    }:
        dist_penalty = min(0.25, 0.06 * abs(src.para_id - tgt.para_id))
        conf = round(max(0.51, 0.88 - dist_penalty), 3)
        neutral = round(max(0.08, 1.0 - conf - 0.04), 3)
        return "Support", conf, {"entail": conf, "neutral": neutral, "contradict": 0.04}
    return "NoRelation", 0.25, {"entail": 0.25, "neutral": 0.65, "contradict": 0.10}


def decode_minimum_spanning_dag(
    nodes: list[ExtractedNode],
    scored_edges: list[tuple[str, str, str, float, dict[str, float]]],
) -> list[DecodedEdge]:
    """Dekode Chu-Liu/Edmonds via virtual root agar graf Support dijamin bebas siklus (DAG)."""
    virtual_root = "__ROOT__"
    arbor_graph = nx.DiGraph()
    arbor_graph.add_node(virtual_root)
    for node in nodes:
        arbor_graph.add_node(node.node_key)
        arbor_graph.add_edge(virtual_root, node.node_key, weight=0.01)

    edge_meta: dict[tuple[str, str], tuple[str, float, dict[str, float]]] = {}
    attack_edges: list[tuple[str, str, str, float, dict[str, float]]] = []

    for src, tgt, rel, conf, probs in scored_edges:
        if src == tgt or rel == "NoRelation" or conf < 0.50:
            continue
        if rel == "Support":
            # Orientasi di arborescence: target -> source agar tiap source <= 1 parent
            arbor_graph.add_edge(tgt, src, weight=float(conf))
            edge_meta[(src, tgt)] = (rel, conf, probs)
        elif rel == "Attack":
            attack_edges.append((src, tgt, rel, conf, probs))

    decoded: list[DecodedEdge] = []
    edge_idx = 1
    if edge_meta:
        arb = nx.maximum_spanning_arborescence(arbor_graph, attr="weight")
        for tgt, src in arb.edges():
            if tgt == virtual_root or (src, tgt) not in edge_meta:
                continue
            rel, conf, probs = edge_meta[(src, tgt)]
            decoded.append(DecodedEdge(f"E-{edge_idx:02d}", src, tgt, rel, conf, probs))
            edge_idx += 1

    for src, tgt, rel, conf, probs in attack_edges:
        if src != tgt:
            decoded.append(DecodedEdge(f"E-{edge_idx:02d}", src, tgt, rel, conf, probs))
            edge_idx += 1
    return decoded


def run_stage_1_structure(clean_text: str) -> tuple[list[ExtractedNode], list[DecodedEdge]]:
    """Eksekusi F-01 & F-02 tahap awal: ekstrak node + dekode Chu-Liu/Edmonds DAG."""
    sentences = segment_sentences(clean_text)
    nodes = extract_components(sentences)
    node_map = {n.node_key: n for n in nodes}
    pairs = generate_relation_candidates(
        [(n.node_key, n.para_id) for n in nodes], max_para_distance=3
    )
    scored: list[tuple[str, str, str, float, dict[str, float]]] = []
    for src_k, tgt_k in pairs:
        rel, conf, probs = score_candidate_edge(node_map[src_k], node_map[tgt_k])
        scored.append((src_k, tgt_k, rel, conf, probs))
    edges = decode_minimum_spanning_dag(nodes, scored)
    return nodes, edges
