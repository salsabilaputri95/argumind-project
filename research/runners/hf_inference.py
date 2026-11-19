from __future__ import annotations

from pathlib import Path

from argumind_metrics import ComponentSpan, RelationTriple
from argumind_nlp.dag_decoder import ExtractedNode, decode_minimum_spanning_dag

from research.runners.train_indobert_bio import decode_bio_spans
from research.runners.train_nli_relations import ID_TO_REL


def predict_with_hf_models(
    doc_id: str,
    clean_text: str,
    bio_model_dir: Path,
    nli_model_dir: Path | None,
) -> tuple[list[ComponentSpan], list[RelationTriple]]:
    """Inferensi menggunakan checkpoint IndoBERT BIO & Cross-Encoder NLI hasil fine-tuning."""
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
        logits = bio_mod(
            input_ids=enc["input_ids"].to(device),
            attention_mask=enc["attention_mask"].to(device),
        ).logits[0]
        tag_ids = torch.argmax(logits, dim=-1).cpu().tolist()
    spans = decode_bio_spans(doc_id, offsets, tag_ids)

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
        scored: list[tuple[str, str, str, float, dict[str, float]]] = []
        with torch.no_grad():
            for a in extracted:
                for b in extracted:
                    if a.node_key == b.node_key:
                        continue
                    pair_enc = nli_tok(
                        a.text_content,
                        b.text_content,
                        truncation=True,
                        max_length=256,
                        return_tensors="pt",
                    ).to(device)
                    probs = torch.softmax(nli_mod(**pair_enc).logits[0], dim=-1).cpu().tolist()
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
