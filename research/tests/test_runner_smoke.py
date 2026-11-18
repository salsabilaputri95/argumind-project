from __future__ import annotations

import json
from pathlib import Path

from research.runners.determinism import verify_manifest_sha256
from research.runners.generate_seed_corpus import write_seed_corpus
from research.runners.run_experiment import run_experiment


def test_seed_corpus_and_experiment_runner_smoke(tmp_path: Path) -> None:
    data_dir = tmp_path / "corpus"
    write_seed_corpus(data_dir)
    hashes = verify_manifest_sha256(data_dir)
    assert len(hashes) == 5

    out_e01 = tmp_path / "outputs" / "E-01"
    m1 = run_experiment(
        exp_id="E-01",
        arch="M1_ArgumindHybrid",
        data_dir=data_dir,
        split="test",
        seed=42,
        output_dir=out_e01,
    )
    assert m1["cycle_rate"] == 0.0
    assert m1["n_docs"] == 2
    for fname in ("config_locked.json", "predictions.jsonl", "metrics_raw.json", "run.log"):
        assert (out_e01 / fname).exists()

    out_e03b = tmp_path / "outputs" / "E-03b"
    m3 = run_experiment(
        exp_id="E-03b",
        arch="M3_GraphGroundedScoring",
        data_dir=data_dir,
        split="test",
        seed=42,
        output_dir=out_e03b,
    )
    assert "qwk_score" in m3
    assert "faithfulness_rate" in m3
    saved = json.loads((out_e03b / "metrics_raw.json").read_text(encoding="utf-8"))
    assert saved["exp_id"] == "E-03b"
