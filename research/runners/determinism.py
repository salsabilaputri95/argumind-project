from __future__ import annotations

import hashlib
import json
import os
import random
from pathlib import Path
from typing import Any

import numpy as np


def set_global_seed(seed: int) -> None:
    """Kunci random seed global untuk reprodusibilitas (REPRODUCIBILITY.md#5)."""
    os.environ["PYTHONHASHSEED"] = str(seed)
    os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        torch.use_deterministic_algorithms(True, warn_only=True)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    except ImportError:
        pass


def verify_manifest_sha256(data_dir: Path) -> dict[str, str]:
    """Verifikasi checksum manifest.sha256 sebelum eksperimen dijalankan."""
    manifest_path = data_dir / "manifest.sha256"
    if not manifest_path.exists():
        raise FileNotFoundError(f"manifest.sha256 tidak ditemukan di {data_dir}")
    hashes: dict[str, str] = {}
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        expected_hash, rel_name = stripped.split(maxsplit=1)
        filename = rel_name.lstrip("*").strip()
        target = data_dir / filename
        if not target.exists():
            raise FileNotFoundError(f"File korpus hilang: {target}")
        raw_bytes = target.read_bytes()
        actual_raw = hashlib.sha256(raw_bytes).hexdigest()
        actual_lf = hashlib.sha256(raw_bytes.replace(b"\r\n", b"\n")).hexdigest()
        if expected_hash not in {actual_raw, actual_lf}:
            raise RuntimeError(
                f"Checksum mismatch pada {filename}: expected {expected_hash}, got {actual_lf}"
            )
        hashes[filename] = expected_hash
    return hashes


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Baca berkas JSONL menjadi list dictionary."""
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def load_corpus_split(
    data_dir: Path, split: str
) -> tuple[
    dict[str, dict[str, Any]],
    dict[str, list[dict[str, Any]]],
    dict[str, list[dict[str, Any]]],
    dict[str, list[dict[str, Any]]],
    dict[str, list[dict[str, Any]]],
]:
    """Muat korpus terverifikasi berdasarkan partisi train/dev/test."""
    docs = {
        str(d["doc_id"]): d
        for d in read_jsonl(data_dir / "documents.jsonl")
        if d.get("split") == split
    }
    by_doc_nodes: dict[str, list[dict[str, Any]]] = {k: [] for k in docs}
    for row in read_jsonl(data_dir / "nodes.jsonl"):
        did = str(row["doc_id"])
        if did in by_doc_nodes:
            by_doc_nodes[did].append(row)

    by_doc_edges: dict[str, list[dict[str, Any]]] = {k: [] for k in docs}
    for row in read_jsonl(data_dir / "edges.jsonl"):
        did = str(row["doc_id"])
        if did in by_doc_edges:
            by_doc_edges[did].append(row)

    by_doc_gaps: dict[str, list[dict[str, Any]]] = {k: [] for k in docs}
    for row in read_jsonl(data_dir / "gaps.jsonl"):
        did = str(row["doc_id"])
        if did in by_doc_gaps:
            by_doc_gaps[did].append(row)

    by_doc_scores: dict[str, list[dict[str, Any]]] = {k: [] for k in docs}
    for row in read_jsonl(data_dir / "rubric_scores.jsonl"):
        did = str(row["doc_id"])
        if did in by_doc_scores:
            by_doc_scores[did].append(row)

    return docs, by_doc_nodes, by_doc_edges, by_doc_gaps, by_doc_scores
