from __future__ import annotations

import io

import docx
import networkx as nx
import pytest
from argumind_nlp import (
    DocumentProcessingError,
    align_bio_tags,
    decode_minimum_spanning_dag,
    extract_text_from_bytes,
    generate_relation_candidates,
    preprocess_document,
    redact_pii,
    run_stage_1_structure,
    segment_sentences,
)


def _make_sample_essay(repeat: int = 25) -> str:
    intro = (
        "Oleh: Budi Santoso (NIM 20451122)\nEmail: budi.santoso@kampus.ac.id\n\n"
        "Pemerintah daerah wajib mengalihkan subsidi BBM ke transportasi umum "
        "menurut UU No. 22 tahun 2009. "
        "Berdasarkan data BPS tahun 2025, biaya komuter menyerap 28% pendapatan pekerja perkotaan. "
        "Namun, pengalihan mendadak tanpa kesiapan armada harus dikritik "
        "agar tidak membebani warga. "
    )
    body = (
        "Peningkatan layanan bus kota menurunkan kemacetan harian di koridor utama. "
        "Survei menunjukkan bahwa 72% responden bersedia beralih "
        "jika waktu tunggu di bawah 10 menit. "
    ) * repeat
    return intro + "\n\n" + body


def test_preprocess_6_stages_and_pii_redaction() -> None:
    raw = _make_sample_essay(22)
    doc = preprocess_document(raw, redact=True, enforce_bounds=True)
    assert 300 <= doc.word_count <= 2500
    assert "[REDACTED_NAME]" in doc.clean_text
    assert "[REDACTED_EMAIL]" in doc.clean_text
    assert "[REDACTED_ID]" in doc.clean_text
    assert "Budi Santoso" not in doc.clean_text
    assert len(doc.content_sha256) == 64
    assert len(doc.sentences) > 10
    for s in doc.sentences:
        assert doc.clean_text[s.start_char : s.end_char] == s.text


def test_indonesian_abbreviations_not_split() -> None:
    text = (
        "Berdasarkan UU No. 27 Tahun 2022, Prof. Adi dkk. meneliti Rp. 1000 per warga pada hlm. 12."
    )
    sents = segment_sentences(text)
    assert len(sents) == 1
    assert redact_pii("Hubungi +6281234567890") == "Hubungi [REDACTED_ID]"


def test_quality_gate_word_count_bounds() -> None:
    with pytest.raises(DocumentProcessingError) as exc_info:
        preprocess_document("Esai terlalu pendek hanya sepuluh kata saja.", enforce_bounds=True)
    assert exc_info.value.status_code == 422
    assert exc_info.value.code == "ERR_WORD_COUNT_BOUNDS"


def test_bio_alignment_and_pair_candidates() -> None:
    offsets = [(0, 10), (11, 20), (21, 30), (31, 40)]
    gold = [(0, 20, "Claim"), (31, 40, "Evidence")]
    tags = align_bio_tags(offsets, gold)
    assert tags == ["B-Claim", "I-Claim", "O", "B-Evidence"]
    pairs = generate_relation_candidates(
        [("N-01", 1), ("N-02", 2), ("N-03", 6)], max_para_distance=3
    )
    assert ("N-01", "N-02") in pairs
    assert ("N-01", "N-03") not in pairs


def test_extract_docx_and_corrupt_files() -> None:
    buf = io.BytesIO()
    d = docx.Document()
    d.add_paragraph("Paragraf satu tentang kebijakan publik.")
    d.save(buf)
    extracted = extract_text_from_bytes(buf.getvalue(), "docx")
    assert "kebijakan publik" in extracted
    assert extract_text_from_bytes(b"Teks UTF-8 valid", "txt") == "Teks UTF-8 valid"

    with pytest.raises(DocumentProcessingError) as err:
        extract_text_from_bytes(b"not-a-pdf", "pdf")
    assert err.value.code == "ERR_CORRUPT_FILE"


def test_dag_decoder_guarantees_acyclic_support() -> None:
    raw = _make_sample_essay(22)
    doc = preprocess_document(raw, redact=True, enforce_bounds=True)
    nodes, edges = run_stage_1_structure(doc.clean_text)
    assert len(nodes) >= 3
    assert len(edges) >= 1
    # Buat siklus buatan untuk menguji Chu-Liu/Edmonds wajib memutus siklus
    cyclic_scores = [
        ("N-01", "N-02", "Support", 0.90, {"entail": 0.9, "neutral": 0.1, "contradict": 0.0}),
        ("N-02", "N-01", "Support", 0.85, {"entail": 0.85, "neutral": 0.15, "contradict": 0.0}),
        ("N-03", "N-01", "Attack", 0.80, {"entail": 0.1, "neutral": 0.1, "contradict": 0.8}),
    ]
    decoded = decode_minimum_spanning_dag(nodes[:3], cyclic_scores)
    g = nx.DiGraph()
    for e in decoded:
        assert e.source_key != e.target_key
        if e.relation_type == "Support":
            g.add_edge(e.source_key, e.target_key)
    assert nx.is_directed_acyclic_graph(g)
