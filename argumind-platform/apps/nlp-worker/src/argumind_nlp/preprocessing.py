from __future__ import annotations

import hashlib
import io
import re
import unicodedata
from dataclasses import dataclass

MIN_WORD_COUNT = 300
MAX_WORD_COUNT = 2500

ABBREV_PATTERN = re.compile(r"\b(?:UU\s+No|No|Rp|Prof|Dr|Ir|Hj|H|dkk|hlm|dll|dsb|tsb|Yth|Sdr)\.$")
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
ID_RE = re.compile(r"\b(?:NIM|NIP|NIK|NPM)\s*[:#-]?\s*[A-Z0-9-]{5,20}\b", re.IGNORECASE)
PHONE_RE = re.compile(r"(?<!\w)(?:\+62|62|0)8[1-9][0-9]{7,10}\b")
AUTHOR_LINE_RE = re.compile(
    r"^((?:Oleh|Penulis|Nama|Disusun\s+oleh)\s*:\s*)([^\n(]+)",
    re.IGNORECASE | re.MULTILINE,
)


class DocumentProcessingError(Exception):
    """Kesalahan pra-pemrosesan dengan kode RFC 9457."""

    def __init__(self, status_code: int, code: str, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.code = code
        self.detail = detail


@dataclass(frozen=True)
class SentenceSpan:
    sent_id: str
    para_id: int
    start_char: int
    end_char: int
    text: str


@dataclass(frozen=True)
class PreprocessedDocument:
    clean_text: str
    content_sha256: str
    word_count: int
    sentences: tuple[SentenceSpan, ...]


def extract_text_from_bytes(raw_bytes: bytes, source_format: str) -> str:
    """Tahap 1a: Ekstrak teks mentah dari txt/md/docx/pdf berbasis teks."""
    fmt = source_format.lower().lstrip(".")
    if fmt in {"txt", "md"}:
        try:
            return raw_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise DocumentProcessingError(
                400, "ERR_CORRUPT_FILE", "File bukan UTF-8 valid."
            ) from exc
    if fmt == "docx":
        import docx  # type: ignore[import-untyped]

        try:
            doc = docx.Document(io.BytesIO(raw_bytes))
            return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except Exception as exc:
            raise DocumentProcessingError(400, "ERR_CORRUPT_FILE", "File DOCX rusak.") from exc
    if fmt == "pdf":
        import pymupdf  # type: ignore[import-untyped]

        try:
            pdf = pymupdf.open(stream=raw_bytes, filetype="pdf")
            text = "\n\n".join(str(page.get_text("text")) for page in pdf)
        except Exception as exc:
            raise DocumentProcessingError(
                400, "ERR_CORRUPT_FILE", "File PDF tidak terbaca."
            ) from exc
        if not text.strip():
            raise DocumentProcessingError(
                400, "ERR_CORRUPT_FILE", "PDF pindaian tanpa lapisan teks tidak didukung."
            )
        return text
    raise DocumentProcessingError(
        400, "ERR_CORRUPT_FILE", f"Format {source_format} tidak didukung."
    )


def normalize_encoding(text: str) -> str:
    """Tahap 1b: Normalisasi Unicode NFKC tanpa case folding (METHODOLOGY.md#4B.1)."""
    normalized = unicodedata.normalize("NFKC", text).replace("\r\n", "\n").replace("\r", "\n")
    cleaned = "".join(ch if (ch == "\n" or ord(ch) >= 32) else " " for ch in normalized)
    return re.sub(r"[ \t]+", " ", cleaned).strip()


def redact_pii(text: str) -> str:
    """Tahap 2: Samarkan email, NIM/NIP, telepon, dan nama penulis di header."""
    redacted = EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    redacted = ID_RE.sub("[REDACTED_ID]", redacted)
    redacted = PHONE_RE.sub("[REDACTED_ID]", redacted)
    return AUTHOR_LINE_RE.sub(r"\1[REDACTED_NAME]", redacted)


def segment_sentences(clean_text: str) -> tuple[SentenceSpan, ...]:
    """Tahap 3: Segmentasi paragraf dan kalimat dengan indeks karakter absolut."""
    spans: list[SentenceSpan] = []
    sent_idx = 1
    para_id = 1
    pos = 0
    for block in clean_text.split("\n\n"):
        if not block.strip():
            pos += len(block) + 2
            continue
        start = pos
        i = 0
        while i < len(block):
            ch = block[i]
            is_end = ch in ".!?" and (i + 1 == len(block) or block[i + 1].isspace())
            if is_end:
                candidate = block[start - pos : i + 1].strip()
                if not ABBREV_PATTERN.search(candidate):
                    abs_start = pos + block.find(candidate, start - pos)
                    spans.append(
                        SentenceSpan(
                            sent_id=f"S-{sent_idx:02d}",
                            para_id=para_id,
                            start_char=abs_start,
                            end_char=abs_start + len(candidate),
                            text=candidate,
                        )
                    )
                    sent_idx += 1
                    start = pos + i + 1
            i += 1
        tail = block[start - pos :].strip()
        if tail:
            abs_start = pos + block.find(tail, start - pos)
            spans.append(
                SentenceSpan(
                    sent_id=f"S-{sent_idx:02d}",
                    para_id=para_id,
                    start_char=abs_start,
                    end_char=abs_start + len(tail),
                    text=tail,
                )
            )
            sent_idx += 1
        para_id += 1
        pos += len(block) + 2
    return tuple(spans)


def validate_quality_gate(clean_text: str) -> int:
    """Tahap 4: Validasi panjang kata wajib antara 300 dan 2500 kata."""
    words = re.findall(r"\b\w+\b", clean_text)
    count = len(words)
    if count < MIN_WORD_COUNT or count > MAX_WORD_COUNT:
        raise DocumentProcessingError(
            422,
            "ERR_WORD_COUNT_BOUNDS",
            (
                f"Dokumen memiliki {count} kata. "
                f"Batas wajib adalah {MIN_WORD_COUNT} hingga {MAX_WORD_COUNT} kata."
            ),
        )
    return count


def align_bio_tags(
    token_offsets: list[tuple[int, int]],
    gold_spans: list[tuple[int, int, str]],
) -> list[str]:
    """Tahap 5: Konversi offset sub-kata ke label sekuens BIO."""
    labels: list[str] = []
    for tok_start, tok_end in token_offsets:
        if tok_end <= tok_start:
            labels.append("O")
            continue
        assigned = "O"
        for span_start, span_end, span_label in gold_spans:
            if tok_start < span_end and tok_end > span_start:
                prefix = "B-" if tok_start <= span_start else "I-"
                assigned = f"{prefix}{span_label}"
                break
        labels.append(assigned)
    return labels


def generate_relation_candidates(
    node_para_map: list[tuple[str, int]],
    max_para_distance: int = 3,
) -> list[tuple[str, str]]:
    """Tahap 6: Bangkitkan pasangan kandidat berarah (a != b) dengan jarak <= 3 paragraf."""
    pairs: list[tuple[str, str]] = []
    for src_key, src_para in node_para_map:
        for tgt_key, tgt_para in node_para_map:
            if src_key != tgt_key and abs(src_para - tgt_para) <= max_para_distance:
                pairs.append((src_key, tgt_key))
    return pairs


def preprocess_document(
    raw_text: str,
    redact: bool = True,
    enforce_bounds: bool = True,
) -> PreprocessedDocument:
    """Jalankan Tahap 1-4 pra-pemrosesan secara berurutan."""
    norm = normalize_encoding(raw_text)
    clean_text = redact_pii(norm) if redact else norm
    word_count = (
        validate_quality_gate(clean_text)
        if enforce_bounds
        else len(re.findall(r"\b\w+\b", clean_text))
    )
    sha256 = hashlib.sha256(clean_text.encode("utf-8")).hexdigest()
    sentences = segment_sentences(clean_text)
    return PreprocessedDocument(
        clean_text=clean_text,
        content_sha256=sha256,
        word_count=word_count,
        sentences=sentences,
    )
