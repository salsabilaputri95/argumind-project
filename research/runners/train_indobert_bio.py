from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from argumind_metrics import ComponentSpan, macro_f1_components
from argumind_nlp.preprocessing import align_bio_tags

from research.runners.determinism import load_corpus_split, set_global_seed, verify_manifest_sha256

BIO_LABELS: tuple[str, ...] = (
    "O",
    "B-Claim",
    "I-Claim",
    "B-ExplicitPremise",
    "I-ExplicitPremise",
    "B-Evidence",
    "I-Evidence",
)
LABEL_TO_ID: dict[str, int] = {lbl: idx for idx, lbl in enumerate(BIO_LABELS)}
ID_TO_LABEL: dict[int, str] = {idx: lbl for idx, lbl in enumerate(BIO_LABELS)}


def decode_bio_spans(
    doc_id: str,
    offsets: list[tuple[int, int]],
    tag_ids: list[int],
) -> list[ComponentSpan]:
    """Konversi prediksi label BIO token kembali menjadi ComponentSpan berbasis karakter."""
    spans: list[ComponentSpan] = []
    cur_label: str | None = None
    cur_start: int = 0
    cur_end: int = 0

    for (tok_start, tok_end), tid in zip(offsets, tag_ids, strict=False):
        if tok_end <= tok_start:
            continue
        tag = ID_TO_LABEL.get(int(tid), "O")
        if tag.startswith("B-"):
            if cur_label is not None:
                spans.append(ComponentSpan(doc_id, cur_start, cur_end, cur_label))
            cur_label = tag[2:]
            cur_start = tok_start
            cur_end = tok_end
        elif tag.startswith("I-") and cur_label == tag[2:]:
            cur_end = tok_end
        else:
            if cur_label is not None:
                spans.append(ComponentSpan(doc_id, cur_start, cur_end, cur_label))
                cur_label = None
    if cur_label is not None:
        spans.append(ComponentSpan(doc_id, cur_start, cur_end, cur_label))
    return spans


def encode_split_examples(
    data_dir: Path,
    split: str,
    tokenizer: Any,
    max_length: int = 512,
    stride: int = 128,
) -> tuple[list[dict[str, Any]], list[ComponentSpan]]:
    """Tokenisasi sliding-window dan sejajarkan label BIO untuk IndoBERT."""
    docs, by_doc_nodes, _, _, _ = load_corpus_split(data_dir, split)
    examples: list[dict[str, Any]] = []
    gold_spans: list[ComponentSpan] = []

    for doc_id, doc in docs.items():
        clean_text = str(doc["clean_text"])
        raw_spans: list[tuple[int, int, str]] = []
        for n in by_doc_nodes.get(doc_id, []):
            if n.get("start_char") is not None and n.get("end_char") is not None:
                s_c, e_c, n_type = int(n["start_char"]), int(n["end_char"]), str(n["node_type"])
                if n_type in {"Claim", "ExplicitPremise", "Evidence"}:
                    raw_spans.append((s_c, e_c, n_type))
                    gold_spans.append(ComponentSpan(doc_id, s_c, e_c, n_type))

        tokenized = tokenizer(
            clean_text,
            return_offsets_mapping=True,
            truncation=True,
            max_length=max_length,
            stride=stride,
            return_overflowing_tokens=True,
            padding="max_length",
        )
        for win_idx in range(len(tokenized["input_ids"])):
            offsets = [(int(a), int(b)) for a, b in tokenized["offset_mapping"][win_idx]]
            bio_strs = align_bio_tags(offsets, raw_spans)
            label_ids = [
                -100 if (a == 0 and b == 0) else LABEL_TO_ID.get(tag, 0)
                for (a, b), tag in zip(offsets, bio_strs, strict=True)
            ]
            examples.append(
                {
                    "doc_id": doc_id,
                    "input_ids": tokenized["input_ids"][win_idx],
                    "attention_mask": tokenized["attention_mask"][win_idx],
                    "labels": label_ids,
                    "offsets": offsets,
                }
            )
    return examples, gold_spans


def train_indobert_bio(
    data_dir: Path,
    output_dir: Path,
    model_name: str = "indobenchmark/indobert-base-p2",
    seed: int = 42,
    epochs: int = 10,
    batch_size: int = 16,
    lr: float = 2e-5,
    max_length: int = 512,
    stride: int = 128,
    patience: int = 3,
) -> dict[str, Any]:
    """Fine-tuning IndoBERT untuk segmentasi komponen argumen BIO (F-01)."""
    import torch
    from torch.utils.data import DataLoader
    from transformers import (
        AutoModelForTokenClassification,
        AutoTokenizer,
        get_linear_schedule_with_warmup,
    )

    set_global_seed(seed)
    verify_manifest_sha256(data_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForTokenClassification.from_pretrained(
        model_name, num_labels=len(BIO_LABELS), id2label=ID_TO_LABEL, label2id=LABEL_TO_ID
    ).to(device)

    train_ex, _ = encode_split_examples(data_dir, "train", tokenizer, max_length, stride)
    dev_ex, dev_golds = encode_split_examples(data_dir, "dev", tokenizer, max_length, stride)
    test_ex, test_golds = encode_split_examples(data_dir, "test", tokenizer, max_length, stride)

    def _collate(batch: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "input_ids": torch.tensor([x["input_ids"] for x in batch], dtype=torch.long),
            "attention_mask": torch.tensor([x["attention_mask"] for x in batch], dtype=torch.long),
            "labels": torch.tensor([x["labels"] for x in batch], dtype=torch.long),
        }

    train_loader = DataLoader(train_ex, batch_size=batch_size, shuffle=True, collate_fn=_collate)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    total_steps = max(1, len(train_loader) * epochs)
    scheduler = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=int(0.10 * total_steps), num_training_steps=total_steps
    )

    def _eval_split(examples: list[dict[str, Any]], golds: list[ComponentSpan]) -> dict[str, float]:
        model.eval()
        preds: list[ComponentSpan] = []
        with torch.no_grad():
            for ex in examples:
                inp = torch.tensor([ex["input_ids"]], dtype=torch.long, device=device)
                mask = torch.tensor([ex["attention_mask"]], dtype=torch.long, device=device)
                logits = model(input_ids=inp, attention_mask=mask).logits[0]
                tag_ids = torch.argmax(logits, dim=-1).cpu().tolist()
                preds.extend(decode_bio_spans(str(ex["doc_id"]), ex["offsets"], tag_ids))
        return macro_f1_components(preds, golds, iou_threshold=0.5)

    best_f1 = -1.0
    no_improve = 0
    ckpt_dir = output_dir / "best_model"
    for _epoch in range(1, epochs + 1):
        model.train()
        for batch in train_loader:
            optimizer.zero_grad()
            out = model(
                input_ids=batch["input_ids"].to(device),
                attention_mask=batch["attention_mask"].to(device),
                labels=batch["labels"].to(device),
            )
            out.loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()
        dev_scores = _eval_split(dev_ex, dev_golds)
        if dev_scores["macro_f1"] > best_f1:
            best_f1 = dev_scores["macro_f1"]
            no_improve = 0
            model.save_pretrained(ckpt_dir)
            tokenizer.save_pretrained(ckpt_dir)
        else:
            no_improve += 1
            if no_improve >= patience:
                break

    if ckpt_dir.exists():
        model = AutoModelForTokenClassification.from_pretrained(ckpt_dir).to(device)
    test_scores = _eval_split(test_ex, test_golds)
    summary = {
        "model_name": model_name,
        "seed": seed,
        "dev_best_macro_f1_iou50": best_f1,
        "test_macro_f1_iou50": test_scores,
        "checkpoint_dir": str(ckpt_dir),
    }
    (output_dir / "eval_bio.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fine-tune IndoBERT BIO component extractor (F-01)"
    )
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--model-name", type=str, default="indobenchmark/indobert-base-p2")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=2e-5)
    args = parser.parse_args()
    res = train_indobert_bio(
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
