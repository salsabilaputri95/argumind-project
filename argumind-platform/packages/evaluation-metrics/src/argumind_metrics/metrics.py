from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

import numpy as np

COMPONENT_CLASSES: tuple[str, ...] = ("Claim", "ExplicitPremise", "Evidence")
RELATION_CLASSES: tuple[str, ...] = ("Support", "Attack")


@dataclass(frozen=True)
class ComponentSpan:
    """Span komponen argumen untuk evaluasi RQ1."""

    doc_id: str
    start_char: int
    end_char: int
    label: str


@dataclass(frozen=True)
class RelationTriple:
    """Relasi berarah antar-komponen argumen untuk evaluasi RQ1."""

    doc_id: str
    source_key: str
    target_key: str
    relation: str


@dataclass(frozen=True)
class FaithfulnessIntervention:
    """Hasil satu intervensi ablasi kontrafaktual pada dimensi rubrik (RQ3)."""

    score_before: int
    score_after: int
    deleted_node_key: str
    grounded_refs_after: tuple[str, ...]


def compute_span_iou(pred: ComponentSpan, gold: ComponentSpan) -> float:
    """Hitung Intersection-over-Union karakter antara dua span pada dokumen yang sama."""
    if pred.doc_id != gold.doc_id or pred.label != gold.label:
        return 0.0
    inter_start = max(pred.start_char, gold.start_char)
    inter_end = min(pred.end_char, gold.end_char)
    intersection = max(0, inter_end - inter_start)
    if intersection == 0:
        return 0.0
    union = (pred.end_char - pred.start_char) + (gold.end_char - gold.start_char) - intersection
    return float(intersection / union) if union > 0 else 0.0


def _prf_for_counts(tp: int, fp: int, fn: int) -> float:
    denom = (2 * tp) + fp + fn
    return float((2 * tp) / denom) if denom > 0 else 0.0


def macro_f1_components(
    preds: Sequence[ComponentSpan],
    golds: Sequence[ComponentSpan],
    iou_threshold: float = 1.0,
) -> dict[str, float]:
    """Macro-F1 komponen argumen (Exact IoU=1.0 atau Partial IoU>=0.5) sesuai METHODOLOGY.md#6B."""
    per_class: dict[str, float] = {}
    for cls in COMPONENT_CLASSES:
        cls_preds = [p for p in preds if p.label == cls]
        cls_golds = [g for g in golds if g.label == cls]
        matched_gold: set[int] = set()
        tp = 0
        for p in cls_preds:
            best_idx, best_iou = -1, 0.0
            for idx, g in enumerate(cls_golds):
                if idx in matched_gold:
                    continue
                iou = compute_span_iou(p, g)
                if iou >= iou_threshold and iou > best_iou:
                    best_idx, best_iou = idx, iou
            if best_idx >= 0:
                matched_gold.add(best_idx)
                tp += 1
        fp = len(cls_preds) - tp
        fn = len(cls_golds) - tp
        per_class[cls] = _prf_for_counts(tp, fp, fn)
    per_class["macro_f1"] = float(sum(per_class.values()) / len(COMPONENT_CLASSES))
    return per_class


def macro_f1_relations(
    preds: Sequence[RelationTriple],
    golds: Sequence[RelationTriple],
) -> dict[str, float]:
    """Macro-F1 relasi berarah Support dan Attack sesuai METHODOLOGY.md#6B."""
    per_class: dict[str, float] = {}
    for rel in RELATION_CLASSES:
        pred_set = {(r.doc_id, r.source_key, r.target_key) for r in preds if r.relation == rel}
        gold_set = {(r.doc_id, r.source_key, r.target_key) for r in golds if r.relation == rel}
        tp = len(pred_set & gold_set)
        fp = len(pred_set - gold_set)
        fn = len(gold_set - pred_set)
        per_class[rel] = _prf_for_counts(tp, fp, fn)
    per_class["macro_f1"] = float(sum(per_class.values()) / len(RELATION_CLASSES))
    return per_class


def quadratic_weighted_kappa(
    y_true: Sequence[int],
    y_pred: Sequence[int],
    min_rating: int = 1,
    max_rating: int = 5,
) -> float:
    """Rumus QWK eksak sesuai research/METHODOLOGY.md#6B.4."""
    if len(y_true) != len(y_pred) or len(y_true) == 0:
        raise ValueError("y_true dan y_pred wajib non-kosong dengan panjang sama.")
    k = (max_rating - min_rating) + 1
    hist_true = np.zeros(k, dtype=np.float64)
    hist_pred = np.zeros(k, dtype=np.float64)
    observed = np.zeros((k, k), dtype=np.float64)
    for t, p in zip(y_true, y_pred, strict=True):
        ti, pi = t - min_rating, p - min_rating
        observed[ti, pi] += 1.0
        hist_true[ti] += 1.0
        hist_pred[pi] += 1.0
    n = float(len(y_true))
    observed /= n
    expected = np.outer(hist_true, hist_pred) / (n * n)
    idx = np.arange(k, dtype=np.float64)
    weights = ((idx[:, None] - idx[None, :]) ** 2) / float((k - 1) ** 2)
    denom = float(np.sum(weights * expected))
    if denom == 0.0:
        return 1.0 if np.array_equal(y_true, y_pred) else 0.0
    return float(1.0 - (np.sum(weights * observed) / denom))


def krippendorff_alpha(
    ratings_matrix: Sequence[Sequence[int | None]],
    level: Literal["nominal", "ordinal", "interval"] = "nominal",
) -> float:
    """Hitung Krippendorff's alpha = 1 - D_o / D_e (baris=anotator, kolom=unit)."""
    if not ratings_matrix or not ratings_matrix[0]:
        raise ValueError("Matriks rating wajib tidak kosong.")
    n_units = len(ratings_matrix[0])
    total_vals = [v for row in ratings_matrix for v in row if v is not None]
    if len(set(total_vals)) <= 1:
        return 1.0
    n_total = 0
    obs_disagreement = 0.0
    all_pairs_values: list[int] = []
    for u in range(n_units):
        unit_vals = [row[u] for row in ratings_matrix if row[u] is not None]
        m_u = len(unit_vals)
        if m_u < 2:
            continue
        n_total += m_u
        all_pairs_values.extend(unit_vals)
        unit_diff = sum(
            _metric_delta(a, b, level)
            for i, a in enumerate(unit_vals)
            for j, b in enumerate(unit_vals)
            if i != j
        )
        obs_disagreement += unit_diff / float(m_u - 1)
    if n_total < 2:
        return 0.0
    d_o = obs_disagreement / float(n_total)
    n_vals = len(all_pairs_values)
    exp_sum = sum(
        _metric_delta(all_pairs_values[i], all_pairs_values[j], level)
        for i in range(n_vals)
        for j in range(n_vals)
        if i != j
    )
    d_e = exp_sum / float(n_vals * (n_vals - 1))
    return 1.0 if d_e == 0.0 else float(1.0 - (d_o / d_e))


def _metric_delta(a: int, b: int, level: Literal["nominal", "ordinal", "interval"]) -> float:
    if level == "nominal":
        return 0.0 if a == b else 1.0
    return float((a - b) ** 2)


def _average_ranks(values: Sequence[float]) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    n = len(arr)
    order = np.argsort(arr, kind="mergesort")
    sorted_vals = arr[order]
    ranks = np.empty(n, dtype=np.float64)
    i = 0
    while i < n:
        j = i + 1
        while j < n and sorted_vals[j] == sorted_vals[i]:
            j += 1
        avg_rank = 0.5 * (i + j - 1) + 1.0
        ranks[order[i:j]] = avg_rank
        i = j
    return ranks


def spearman_correlation(x: Sequence[float], y: Sequence[float]) -> float:
    """Hitung korelasi peringkat Spearman sesuai research/METHODOLOGY.md#6B.5."""
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("Panjang x dan y wajib sama dan >= 2.")
    rx = _average_ranks(x)
    ry = _average_ranks(y)
    dx = rx - float(np.mean(rx))
    dy = ry - float(np.mean(ry))
    denom = float(np.sqrt(np.sum(dx**2) * np.sum(dy**2)))
    return 0.0 if denom == 0.0 else float(np.sum(dx * dy) / denom)


def partial_length_correlation(
    system_scores: Sequence[float],
    human_scores: Sequence[float],
    word_counts: Sequence[int],
) -> float:
    """Korelasi parsial panjang kata L terhadap skor Y dengan mengontrol skor pakar H."""
    word_floats = [float(w) for w in word_counts]
    r_yl = spearman_correlation(system_scores, word_floats)
    r_yh = spearman_correlation(system_scores, human_scores)
    r_lh = spearman_correlation(word_floats, human_scores)
    denom = float(np.sqrt(max(1e-12, (1.0 - r_yh**2) * (1.0 - r_lh**2))))
    return float((r_yl - (r_yh * r_lh)) / denom)


def counterfactual_faithfulness_rate(
    interventions: Sequence[FaithfulnessIntervention],
) -> float:
    """Proporsi intervensi ablasi di mana skor turun dan node terhapus hilang dari grounded_refs."""
    if not interventions:
        raise ValueError("Daftar intervensi wajib tidak kosong.")
    faithful = sum(
        1
        for item in interventions
        if item.score_after < item.score_before
        and item.deleted_node_key not in item.grounded_refs_after
    )
    return float(faithful / len(interventions))


def paired_bootstrap_test(
    scores_model: Sequence[float],
    scores_baseline: Sequence[float],
    n_bootstrap: int = 10_000,
    seed: int = 42,
) -> dict[str, float]:
    """Uji signifikansi paired bootstrap dua arah (METHODOLOGY.md#5B)."""
    if len(scores_model) != len(scores_baseline) or len(scores_model) == 0:
        raise ValueError("Skor model dan baseline wajib berpasangan dan non-kosong.")
    arr_m = np.asarray(scores_model, dtype=np.float64)
    arr_b = np.asarray(scores_baseline, dtype=np.float64)
    diffs = arr_m - arr_b
    observed = float(np.mean(diffs))
    rng = np.random.default_rng(seed)
    n = len(diffs)
    boot_means = np.empty(n_bootstrap, dtype=np.float64)
    for i in range(n_bootstrap):
        sample_idx = rng.integers(0, n, size=n)
        boot_means[i] = float(np.mean(diffs[sample_idx]))
    ci_low, ci_high = np.percentile(boot_means, [2.5, 97.5])
    centered = boot_means - observed
    p_value = float(np.mean(np.abs(centered) >= abs(observed)))
    return {
        "observed_diff": observed,
        "ci_95_low": float(ci_low),
        "ci_95_high": float(ci_high),
        "p_value": p_value,
    }
