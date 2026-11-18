from __future__ import annotations

import uuid
from datetime import UTC, datetime

import networkx as nx
from argumind_metrics import krippendorff_alpha, quadratic_weighted_kappa
from argumind_schemas import (
    ArgumentEdgeSchema,
    ArgumentNodeSchema,
    FeedbackStatus,
    ReasoningGapSchema,
    RubricDimension,
    RubricScoreSchema,
)
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from argumind_api.auth.dependencies import get_current_user, require_role
from argumind_api.auth.policies import assert_document_scope, assert_run_scope
from argumind_api.errors import ArgumindDomainError
from argumind_api.store import AnalysisRunRecord, UserRecord, repo

router = APIRouter(prefix="/api/v1", tags=["runs"])


class FeedbackPatchRequest(BaseModel):
    user_feedback: FeedbackStatus


class ScoreOverrideRequest(BaseModel):
    human_override_score: int = Field(..., ge=1, le=5)
    override_note: str = Field(..., min_length=10)


class GraphSubmissionRequest(BaseModel):
    nodes: list[ArgumentNodeSchema]
    edges: list[ArgumentEdgeSchema]
    gaps: list[ReasoningGapSchema] = Field(default_factory=list)
    scores: list[RubricScoreSchema]


def _serialize_run(run: AnalysisRunRecord) -> dict[str, object]:
    ver = repo.versions[run.doc_version_id]
    doc = repo.documents[ver.document_id]
    final_vals = [
        int(s["human_override_score"])
        if s.get("human_override_score") is not None
        else int(s["ai_score"])
        for s in run.scores
    ]
    overall = round(sum(final_vals) / len(final_vals), 2) if final_vals else 0.0
    return {
        "run_id": run.id,
        "doc_id": doc.id,
        "doc_title": doc.title,
        "doc_version_id": run.doc_version_id,
        "run_source": run.run_source,
        "actor_user_id": run.actor_user_id,
        "status": run.status,
        "clean_text": ver.clean_text,
        "overall_score": overall,
        "nodes": run.nodes,
        "edges": run.edges,
        "gaps": run.gaps,
        "scores": run.scores,
    }


def _validate_graph_submission(body: GraphSubmissionRequest, clean_text: str) -> None:
    node_keys = {n.node_key for n in body.nodes}
    gap_keys = {g.gap_key for g in body.gaps}
    valid_refs = node_keys | gap_keys
    text_len = len(clean_text)

    for n in body.nodes:
        if n.start_char is not None and n.end_char is not None:
            if n.end_char > text_len or clean_text[n.start_char : n.end_char] != n.text_content:
                raise ArgumindDomainError(
                    422,
                    "ERR_INVALID_SPAN",
                    "Invalid Span",
                    f"Span {n.node_key} tidak cocok dengan clean_text.",
                )

    dag = nx.DiGraph()
    dag.add_nodes_from(node_keys)
    for e in body.edges:
        if e.source_key not in node_keys or e.target_key not in node_keys:
            raise ArgumindDomainError(
                422, "ERR_INVALID_EDGE", "Unknown Node", f"Edge {e.edge_key} merujuk node fiktif."
            )
        if e.relation_type == "Support":
            dag.add_edge(e.source_key, e.target_key)
    if not nx.is_directed_acyclic_graph(dag):
        raise ArgumindDomainError(
            422, "ERR_CYCLE_DETECTED", "Cycle Detected", "Graf relasi Support wajib asiklik (DAG)."
        )

    for s in body.scores:
        if not s.grounded_refs or not all(ref in valid_refs for ref in s.grounded_refs):
            raise ArgumindDomainError(
                422,
                "ERR_UNFAITHFUL_SCORE",
                "Invalid Grounded Refs",
                f"Skor {s.dimension} wajib merujuk node_key atau gap_key valid.",
            )


@router.get("/runs")
def list_runs(
    doc_version_id: str | None = Query(default=None),
    run_source: str | None = Query(default=None),
    current_user: UserRecord = Depends(get_current_user),
) -> dict[str, object]:
    items: list[dict[str, object]] = []
    for run in repo.runs.values():
        if doc_version_id and run.doc_version_id != doc_version_id:
            continue
        if run_source and run.run_source != run_source:
            continue
        ver = repo.versions[run.doc_version_id]
        doc = repo.documents[ver.document_id]
        try:
            assert_run_scope(run, doc, current_user)
        except ArgumindDomainError:
            continue
        items.append(_serialize_run(run))
    return {"data": items, "meta": {"total": len(items)}}


@router.get("/runs/{run_id}")
def get_run(run_id: str, current_user: UserRecord = Depends(get_current_user)) -> dict[str, object]:
    run = repo.runs.get(run_id)
    if not run:
        raise ArgumindDomainError(
            404, "ERR_NOT_FOUND", "Run Not Found", "Sesi analisis tidak ditemukan."
        )
    ver = repo.versions[run.doc_version_id]
    doc = repo.documents[ver.document_id]
    assert_run_scope(run, doc, current_user)
    return _serialize_run(run)


@router.patch("/runs/{run_id}/nodes/{node_key}/feedback")
def update_node_feedback(
    run_id: str,
    node_key: str,
    body: FeedbackPatchRequest,
    current_user: UserRecord = Depends(require_role("author", "reviewer")),
) -> dict[str, object]:
    run = repo.runs.get(run_id)
    if not run:
        raise ArgumindDomainError(404, "ERR_NOT_FOUND", "Run Not Found", "Sesi tidak ditemukan.")
    doc = repo.documents[repo.versions[run.doc_version_id].document_id]
    assert_run_scope(run, doc, current_user)
    for node in run.nodes:
        if node["node_key"] == node_key:
            node["user_feedback"] = body.user_feedback.value
            return node
    raise ArgumindDomainError(
        404, "ERR_NOT_FOUND", "Node Not Found", f"Node {node_key} tidak ditemukan."
    )


@router.patch("/runs/{run_id}/scores/{dimension}")
def override_rubric_score(
    run_id: str,
    dimension: RubricDimension,
    body: ScoreOverrideRequest,
    current_user: UserRecord = Depends(require_role("reviewer")),
) -> dict[str, object]:
    run = repo.runs.get(run_id)
    if not run:
        raise ArgumindDomainError(404, "ERR_NOT_FOUND", "Run Not Found", "Sesi tidak ditemukan.")
    doc = repo.documents[repo.versions[run.doc_version_id].document_id]
    assert_run_scope(run, doc, current_user)
    for score in run.scores:
        if score["dimension"] == dimension.value:
            prev_ai = score["ai_score"]
            score["human_override_score"] = body.human_override_score
            score["reviewer_id"] = current_user.id
            score["override_note"] = body.override_note.strip()
            repo.record_audit(
                current_user.id,
                current_user.role,
                current_user.org_id,
                "SCORE_OVERRIDE_UPDATED",
                "rubric_scores",
                run.id,
                {"ai_score": prev_ai, "human_override_score": body.human_override_score},
            )
            return score
    raise ArgumindDomainError(404, "ERR_NOT_FOUND", "Dimension Not Found", "Dimensi tidak ada.")


@router.put("/annotations/{doc_ver_id}")
def submit_blind_annotation(
    doc_ver_id: str,
    body: GraphSubmissionRequest,
    current_user: UserRecord = Depends(require_role("annotator")),
) -> dict[str, object]:
    ver = repo.versions.get(doc_ver_id)
    if not ver:
        raise ArgumindDomainError(
            404, "ERR_NOT_FOUND", "Version Not Found", "Versi dokumen tidak ada."
        )
    doc = repo.documents[ver.document_id]
    assert_document_scope(doc, current_user, write=False)
    _validate_graph_submission(body, ver.clean_text)

    existing = next(
        (
            r
            for r in repo.runs.values()
            if r.doc_version_id == doc_ver_id
            and r.run_source == "human_annotator"
            and r.actor_user_id == current_user.id
        ),
        None,
    )
    run_id = existing.id if existing else str(uuid.uuid4())
    record = AnalysisRunRecord(
        id=run_id,
        doc_version_id=doc_ver_id,
        run_source="human_annotator",
        actor_user_id=current_user.id,
        status="COMPLETED",
        model_versions={"annotator_id": current_user.id},
        latency_ms=0,
        created_at=datetime.now(UTC).isoformat(),
        nodes=[n.model_dump(mode="json") for n in body.nodes],
        edges=[e.model_dump(mode="json") for e in body.edges],
        gaps=[g.model_dump(mode="json") for g in body.gaps],
        scores=[s.model_dump(mode="json") for s in body.scores],
    )
    repo.runs[run_id] = record
    return _serialize_run(record)


@router.post("/annotations/{doc_ver_id}/adjudicate", status_code=201)
def adjudicate_annotations(
    doc_ver_id: str,
    body: GraphSubmissionRequest,
    current_user: UserRecord = Depends(require_role("reviewer", "org_admin")),
) -> dict[str, object]:
    ver = repo.versions.get(doc_ver_id)
    if not ver:
        raise ArgumindDomainError(
            404, "ERR_NOT_FOUND", "Version Not Found", "Versi dokumen tidak ada."
        )
    doc = repo.documents[ver.document_id]
    assert_document_scope(doc, current_user, write=False)
    _validate_graph_submission(body, ver.clean_text)

    annotator_runs = [
        r
        for r in repo.runs.values()
        if r.doc_version_id == doc_ver_id and r.run_source == "human_annotator"
    ]
    if len(annotator_runs) < 2:
        raise ArgumindDomainError(
            422,
            "ERR_INSUFFICIENT_ANNOTATIONS",
            "Need 2 Annotators",
            "Minimal 2 anotator wajib selesai sebelum adjudikasi.",
        )

    r1_scores = [int(s["ai_score"]) for s in annotator_runs[0].scores]
    r2_scores = [int(s["ai_score"]) for s in annotator_runs[1].scores]
    alpha = (
        krippendorff_alpha([r1_scores, r2_scores], level="ordinal")
        if r1_scores and r2_scores
        else 1.0
    )
    qwk = (
        quadratic_weighted_kappa(r1_scores, r2_scores)
        if len(r1_scores) == len(r2_scores) and r1_scores
        else 1.0
    )

    run_id = str(uuid.uuid4())
    record = AnalysisRunRecord(
        id=run_id,
        doc_version_id=doc_ver_id,
        run_source="gold_adjudicated",
        actor_user_id=current_user.id,
        status="COMPLETED",
        model_versions={"adjudicator_id": current_user.id},
        latency_ms=0,
        created_at=datetime.now(UTC).isoformat(),
        nodes=[n.model_dump(mode="json") for n in body.nodes],
        edges=[e.model_dump(mode="json") for e in body.edges],
        gaps=[g.model_dump(mode="json") for g in body.gaps],
        scores=[s.model_dump(mode="json") for s in body.scores],
    )
    repo.runs[run_id] = record
    repo.record_audit(
        current_user.id,
        current_user.role,
        current_user.org_id,
        "GOLD_STANDARD_ADJUDICATED",
        "analysis_runs",
        run_id,
        {"krippendorff_alpha": round(alpha, 4), "qwk": round(qwk, 4)},
    )
    return {
        **_serialize_run(record),
        "agreement_metrics": {"krippendorff_alpha": round(alpha, 4), "qwk": round(qwk, 4)},
    }
