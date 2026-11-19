from __future__ import annotations

from pathlib import Path

from argumind_metrics import ComponentSpan, RelationTriple
from argumind_nlp.dag_decoder import (
    ExtractedNode,
    decode_minimum_spanning_dag,
    run_stage_1_structure,
)
from argumind_nlp.preprocessing import segment_sentences

from research.runners.train_indobert_bio import ID_TO_LABEL, decode_bio_spans
from research.runners.train_nli_relations import ID_TO_REL


def _consolidate_sentence_spans(
    doc_id: str,
    clean_text: str,
    offsets: list[tuple[int, int]],
    logits_list: list[list[float]],
    tag_ids: list[int],
    max_spans: int = 12,
) -> list[ComponentSpan]:
    """Konsolidasikan prediksi token BIO IndoBERT ke rentang kalimat valid & batasi fragmen."""
    raw_spans = [
        sp
        for sp in decode_bio_spans(doc_id, offsets, tag_ids)
        if (sp.end_char - sp.start_char) >= 25
    ]
    if 1 <= len(raw_spans) <= max_spans:
        return raw_spans

    # Sentence-level BIO pooling dari distribusi logit IndoBERT
    sentences = segment_sentences(clean_text)
    pooled_spans: list[tuple[float, ComponentSpan]] = []
    label_Score_idx = {
        "Claim": (1, 2),
        "ExplicitPremise": (3, 4),
        "Evidence": (5, 6),
    }
    for sent in sentences:
        tok_indices = [
            idx
            for idx, (s_c, e_c) in enumerate(offsets)
            if e_c > s_c and s_c >= sent.start_char and e_c <= sent.end_char
        ]
        if not tok_indices:
            continue
        best_lbl = "O"
        best_score = -1e9
        for lbl, (b_idx, i_idx) in label_Score_idx.items():
            score = sum(
                max(logits_list[t][b_idx], logits_list[t][i_idx]) - logits_list[t][0]
                for t in tok_indices
            ) / len(tok_indices)
            if score > best_score:
                best_score = score
                best_lbl = lbl
        if best_lbl != "O" and best_score > -1.5:
            pooled_spans.append(
                (best_score, ComponentSpan(doc_id, sent.start_char, sent.end_char, best_lbl))
            )

    if pooled_spans:
        pooled_spans.sort(key=lambda x: x[0], reverse=True)
        top_spans = [sp for _, sp in pooled_spans[:max_spans]]
        top_spans.sort(key=lambda sp: sp.start_char)
        return top_spans

    # Fallback ke ekstraksi struktur tahap 1 jika model awal memprediksi semua 'O'
    stage1_nodes, _ = run_stage_1_structure(clean_text)
    return [
        ComponentSpan(doc_id, n.start_char, n.end_char, n.node_type)
        for n in stage1_nodes[:max_spans]
    ]


def predict_with_hf_models(
    doc_id: str,
    clean_text: str,
    bio_model_dir: Path,
    nli_model_dir: Path | None,
) -> tuple[list[ComponentSpan], list[RelationTriple]]:
    """Inferensi cepat (batched) memakai checkpoint IndoBERT BIO & Cross-Encoder NLI."""
    import numpy as np
    import torch
    from transformers import (
        AutoModelForSequenceClassification,
        AutoModelForTokenClassification,
        AutoTokenizer,
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    bio_tok = AutoTokenizer.from_pretrained(bio_model_dir)
    bio_mod = AutoModelForTokenClassification.from_pretrained(bio_model_dir).to(device).eval()

    enc = bio_tok(
        clean_text,
        return_offsets_mapping=True,
        truncation=True,
        max_length=512,
        return_tensors="pt",
    )
    offsets = [(int(a), int(b)) for a, b in enc["offset_mapping"][0].tolist()]
    with torch.no_grad():
        logits_tensor = bio_mod(
            input_ids=enc["input_ids"].to(device),
            attention_mask=enc["attention_mask"].to(device),
        ).logits[0]
        tag_ids = torch.argmax(logits_tensor, dim=-1).cpu().tolist()
        logits_list = logits_tensor.cpu().tolist()

    _ = ID_TO_LABEL
    spans = _consolidate_sentence_spans(doc_id, clean_text, offsets, logits_list, tag_ids)

    rels: list[RelationTriple] = []
    if nli_model_dir is not None and len(spans) >= 2:
        nli_tok = AutoTokenizer.from_pretrained(nli_model_dir)
        nli_mod = (
            AutoModelForSequenceClassification.from_pretrained(nli_model_dir).to(device).eval()
        )
        extracted = [
            ExtractedNode(
                f"{doc_id}_N-{i + 1:02d}",
                sp.label,
                sp.start_char,
                sp.end_char,
                clean_text[sp.start_char : sp.end_char],
                1,
                None,
            )
            for i, sp in enumerate(spans)
        ]
        candidate_pairs = [
            (a, b) for a in extracted for b in extracted if a.node_key != b.node_key
        ]
        scored: list[tuple[str, str, str, float, dict[str, float]]] = []
        batch_size = 32
        with torch.no_grad():
            for start_idx in range(0, len(candidate_pairs), batch_size):
                batch_pairs = candidate_pairs[start_idx : start_idx + batch_size]
                pair_enc = nli_tok(
                    [p[0].text_content for p in batch_pairs],
                    [p[1].text_content for p in batch_pairs],
                    truncation=True,
                    padding=True,
                    max_length=256,
                    return_tensors="pt",
                ).to(device)
                batch_probs = torch.softmax(nli_mod(**pair_enc).logits, dim=-1).cpu().tolist()
                for (a, b), probs in zip(batch_pairs, batch_probs, strict=True):
                    idx = int(np.argmax(probs))
                    scored.append(
                        (
                            a.node_key,
                            b.node_key,
                            ID_TO_REL[idx],
                            float(probs[idx]),
                            {
                                "entail": float(probs[0]),
                                "neutral": float(probs[2]),
                                "contradict": float(probs[1]),
                            },
                        )
                    )
        for edge in decode_minimum_spanning_dag(extracted, scored):
            rels.append(
                RelationTriple(doc_id, edge.source_key, edge.target_key, edge.relation_type)
            )
    return spans, rels
