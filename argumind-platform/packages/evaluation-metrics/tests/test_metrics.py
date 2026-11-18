from __future__ import annotations

import pytest
from argumind_metrics import (
    ComponentSpan,
    FaithfulnessIntervention,
    RelationTriple,
    compute_span_iou,
    counterfactual_faithfulness_rate,
    krippendorff_alpha,
    macro_f1_components,
    macro_f1_relations,
    paired_bootstrap_test,
    partial_length_correlation,
    quadratic_weighted_kappa,
    spearman_correlation,
)
from argumind_schemas import (
    ArgumentEdgeSchema,
    ArgumentNodeSchema,
    GapType,
    NodeType,
    ReasoningGapSchema,
    RubricDimension,
    RubricScoreSchema,
    SeverityLevel,
)


def test_component_iou_and_macro_f1() -> None:
    gold = [
        ComponentSpan("d1", 0, 20, "Claim"),
        ComponentSpan("d1", 21, 51, "ExplicitPremise"),
        ComponentSpan("d1", 52, 82, "Evidence"),
    ]
    pred_exact = list(gold)
    res_exact = macro_f1_components(pred_exact, gold, iou_threshold=1.0)
    assert res_exact["macro_f1"] == pytest.approx(1.0, abs=1e-6)

    pred_partial = [
        ComponentSpan("d1", 0, 15, "Claim"),  # IoU = 15/20 = 0.75
        ComponentSpan("d1", 21, 51, "ExplicitPremise"),
        ComponentSpan("d1", 100, 120, "Evidence"),  # IoU = 0.0
    ]
    assert compute_span_iou(pred_partial[0], gold[0]) == pytest.approx(0.75, abs=1e-6)
    assert compute_span_iou(pred_partial[0], gold[1]) == 0.0
    res_p50 = macro_f1_components(pred_partial, gold, iou_threshold=0.5)
    assert res_p50["Claim"] == pytest.approx(1.0, abs=1e-6)
    assert res_p50["Evidence"] == pytest.approx(0.0, abs=1e-6)
    assert res_p50["macro_f1"] == pytest.approx(2.0 / 3.0, abs=1e-6)


def test_relation_macro_f1() -> None:
    golds = [
        RelationTriple("d1", "N-02", "N-01", "Support"),
        RelationTriple("d1", "N-03", "N-01", "Attack"),
    ]
    preds = [
        RelationTriple("d1", "N-02", "N-01", "Support"),
        RelationTriple("d1", "N-03", "N-02", "Attack"),
    ]
    res = macro_f1_relations(preds, golds)
    assert res["Support"] == pytest.approx(1.0, abs=1e-6)
    assert res["Attack"] == pytest.approx(0.0, abs=1e-6)
    assert res["macro_f1"] == pytest.approx(0.5, abs=1e-6)


def test_qwk_analytical_values() -> None:
    assert quadratic_weighted_kappa([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]) == pytest.approx(
        1.0, abs=1e-6
    )
    assert quadratic_weighted_kappa([3, 3, 3], [3, 3, 3]) == pytest.approx(1.0, abs=1e-6)
    qwk = quadratic_weighted_kappa([1, 2, 3, 4, 5], [1, 2, 4, 4, 5])
    assert 0.85 < qwk < 1.0
    with pytest.raises(ValueError):
        quadratic_weighted_kappa([], [])


def test_krippendorff_alpha_nominal_and_ordinal() -> None:
    perfect = [[1, 2, 3, 1], [1, 2, 3, 1], [1, 2, 3, None]]
    assert krippendorff_alpha(perfect, level="nominal") == pytest.approx(1.0, abs=1e-6)
    disagreed = [[1, 2, 1, 2], [2, 1, 2, 1]]
    alpha = krippendorff_alpha(disagreed, level="nominal")
    assert alpha < 0.0
    assert krippendorff_alpha([[2, 3, 4, 5], [2, 3, 4, 5]], level="ordinal") == pytest.approx(
        1.0, abs=1e-6
    )
    with pytest.raises(ValueError):
        krippendorff_alpha([])


def test_spearman_and_partial_length_correlation() -> None:
    human = [1.0, 2.0, 3.0, 4.0, 5.0]
    system = [1.1, 2.1, 2.9, 4.2, 4.9]
    words = [350, 900, 1200, 1400, 2100]
    assert spearman_correlation(human, system) == pytest.approx(1.0, abs=1e-6)
    partial = partial_length_correlation(system, human, words)
    assert abs(partial) <= 1.0


def test_counterfactual_faithfulness_and_bootstrap() -> None:
    interventions = [
        FaithfulnessIntervention(4, 2, "N-03", ("N-01", "G-01")),
        FaithfulnessIntervention(4, 4, "N-04", ("N-01", "N-04")),
        FaithfulnessIntervention(5, 3, "N-05", ("N-01",)),
        FaithfulnessIntervention(3, 1, "N-06", ("N-02",)),
    ]
    assert counterfactual_faithfulness_rate(interventions) == pytest.approx(0.75, abs=1e-6)
    boot = paired_bootstrap_test([0.82, 0.85, 0.80, 0.88, 0.84], [0.70, 0.71, 0.69, 0.72, 0.70])
    assert boot["observed_diff"] > 0.10
    assert boot["p_value"] < 0.05


def test_shared_schemas_validation() -> None:
    claim = ArgumentNodeSchema(
        node_key="N-01",
        node_type=NodeType.CLAIM,
        start_char=0,
        end_char=12,
        text_content="Klaim utama.",
    )
    assert claim.node_key == "N-01"
    with pytest.raises(ValueError):
        ArgumentNodeSchema(
            node_key="N-02",
            node_type=NodeType.IMPLICIT_PREMISE,
            start_char=0,
            end_char=5,
            text_content="Invalid span",
            target_node_key="N-01",
        )
    with pytest.raises(ValueError):
        ArgumentEdgeSchema(
            edge_key="E-01",
            source_key="N-01",
            target_key="N-01",
            relation_type="Support",
            confidence=0.9,
        )
    with pytest.raises(ValueError):
        RubricScoreSchema(
            dimension=RubricDimension.EVIDENCE_ADEQUACY,
            ai_score=2,
            grounded_refs=[],
            rationale="Kosong tidak boleh.",
        )
    gap = ReasoningGapSchema(
        gap_key="G-01",
        gap_type=GapType.WEAK_EVIDENCE,
        severity=SeverityLevel.MEDIUM,
        target_node_key="N-01",
        explanation="Bukti masih lemah.",
    )
    assert gap.gap_key == "G-01"
