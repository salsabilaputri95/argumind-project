from __future__ import annotations

import json
import time
import uuid
from collections.abc import AsyncIterator
from datetime import UTC, datetime

from argumind_nlp.preprocessing import extract_text_from_bytes, preprocess_document
from argumind_nlp.reasoning import analyze_clean_text
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from argumind_api.auth.dependencies import get_current_user, require_role
from argumind_api.auth.policies import assert_document_scope
from argumind_api.errors import ArgumindDomainError
from argumind_api.store import (
    AnalysisRunRecord,
    DocumentRecord,
    DocumentVersionRecord,
    UserRecord,
    repo,
)

router = APIRouter(prefix="/api/v1", tags=["documents"])


class AnalyzeRequest(BaseModel):
    generate_counterarguments: bool = True


@router.post("/documents", status_code=201)
async def create_document(
    title: str = Form(..., min_length=2, max_length=255),
    domain_strata: str = Form(default="academic"),
    research_opt_in: bool = Form(default=False),
    text: str | None = Form(default=None),
    file: UploadFile | None = File(default=None),
    current_user: UserRecord = Depends(require_role("author", "reviewer", "org_admin")),
) -> dict[str, object]:
    if domain_strata not in {"academic", "policy_business"}:
        raise ArgumindDomainError(
            422, "ERR_INVALID_STRATA", "Invalid Strata", "domain_strata tidak valid."
        )
    if file is not None:
        filename = file.filename or "upload.txt"
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "txt"
        raw_bytes = await file.read()
        raw_text = extract_text_from_bytes(raw_bytes, ext)
        source_format = ext
    elif text is not None:
        raw_text = text
        source_format = "txt"
    else:
        raise ArgumindDomainError(
            400, "ERR_CORRUPT_FILE", "Empty Input", "Wajib mengisi teks atau file."
        )

    prep = preprocess_document(raw_text, redact=True, enforce_bounds=True)
    now = datetime.now(UTC).isoformat()
    doc_id = str(uuid.uuid4())
    ver_id = str(uuid.uuid4())
    doc = DocumentRecord(
        id=doc_id,
        org_id=current_user.org_id,
        author_id=current_user.id,
        title=title.strip(),
        domain_strata=domain_strata,
        research_opt_in=research_opt_in,
        created_at=now,
    )
    offsets: list[dict[str, int | str]] = [
        {
            "para_id": s.para_id,
            "sent_id": s.sent_id,
            "start_char": s.start_char,
            "end_char": s.end_char,
        }
        for s in prep.sentences
    ]
    ver = DocumentVersionRecord(
        id=ver_id,
        document_id=doc_id,
        version_number=1,
        source_format=source_format,
        raw_s3_key=None,
        clean_text=prep.clean_text,
        content_sha256=prep.content_sha256,
        word_count=prep.word_count,
        paragraph_offsets=offsets,
        created_at=now,
    )
    repo.documents[doc_id] = doc
    repo.versions[ver_id] = ver
    return {
        "document": {
            "id": doc.id,
            "title": doc.title,
            "domain_strata": doc.domain_strata,
            "research_opt_in": doc.research_opt_in,
            "created_at": doc.created_at,
        },
        "version": {
            "id": ver.id,
            "version_number": ver.version_number,
            "source_format": ver.source_format,
            "word_count": ver.word_count,
            "content_sha256": ver.content_sha256,
        },
    }


@router.get("/documents")
def list_documents(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    domain_strata: str | None = Query(default=None),
    sort: str = Query(default="-created_at"),
    current_user: UserRecord = Depends(get_current_user),
) -> dict[str, object]:
    visible: list[DocumentRecord] = []
    for doc in repo.documents.values():
        if current_user.role == "author" and doc.author_id != current_user.id:
            continue
        if current_user.role != "author" and doc.org_id != current_user.org_id:
            continue
        if domain_strata and doc.domain_strata != domain_strata:
            continue
        visible.append(doc)
    reverse = sort.startswith("-")
    visible.sort(key=lambda d: d.created_at, reverse=reverse)
    page = visible[offset : offset + limit]
    items: list[dict[str, object]] = []
    for d in page:
        versions = [v for v in repo.versions.values() if v.document_id == d.id]
        latest_ver = max(versions, key=lambda v: v.version_number) if versions else None
        runs = [r for r in repo.runs.values() if latest_ver and r.doc_version_id == latest_ver.id]
        ai_run = next((r for r in runs if r.run_source == "ai_hybrid"), None)
        items.append(
            {
                "id": d.id,
                "title": d.title,
                "domain_strata": d.domain_strata,
                "research_opt_in": d.research_opt_in,
                "created_at": d.created_at,
                "latest_version_number": latest_ver.version_number if latest_ver else 1,
                "latest_version_id": latest_ver.id if latest_ver else None,
                "word_count": latest_ver.word_count if latest_ver else 0,
                "latest_run_id": ai_run.id
                if (ai_run and current_user.role != "annotator")
                else None,
                "status": ai_run.status
                if (ai_run and current_user.role != "annotator")
                else "READY",
            }
        )
    return {"data": items, "meta": {"total": len(visible), "limit": limit, "offset": offset}}


@router.post("/documents/{doc_id}/versions/{ver}/analyze", status_code=202)
def analyze_document_version(
    doc_id: str,
    ver: int,
    body: AnalyzeRequest,
    current_user: UserRecord = Depends(require_role("author", "reviewer")),
) -> dict[str, object]:
    doc = repo.documents.get(doc_id)
    if not doc:
        raise ArgumindDomainError(404, "ERR_NOT_FOUND", "Not Found", "Dokumen tidak ditemukan.")
    assert_document_scope(doc, current_user, write=False)
    doc_ver = next(
        (v for v in repo.versions.values() if v.document_id == doc_id and v.version_number == ver),
        None,
    )
    if not doc_ver:
        raise ArgumindDomainError(
            404, "ERR_NOT_FOUND", "Version Not Found", "Versi tidak ditemukan."
        )

    t0 = time.perf_counter()
    nodes, edges, gaps, scores = analyze_clean_text(
        doc_ver.clean_text, body.generate_counterarguments
    )
    latency_ms = int((time.perf_counter() - t0) * 1000)
    run_id = str(uuid.uuid4())
    repo.runs[run_id] = AnalysisRunRecord(
        id=run_id,
        doc_version_id=doc_ver.id,
        run_source="ai_hybrid",
        actor_user_id=current_user.id,
        status="COMPLETED",
        model_versions={"encoder": "indobert-heuristic-v1", "nli": "dag-edmonds-v1"},
        latency_ms=latency_ms,
        created_at=datetime.now(UTC).isoformat(),
        nodes=nodes,
        edges=edges,
        gaps=gaps,
        scores=scores,
    )
    return {"job_id": run_id, "status": "QUEUED", "stream_url": f"/api/v1/jobs/{run_id}/stream"}


@router.get("/jobs/{job_id}/stream")
async def stream_analysis_job(
    job_id: str,
    current_user: UserRecord = Depends(require_role("author", "reviewer")),
) -> StreamingResponse:
    run = repo.runs.get(job_id)
    if not run:
        raise ArgumindDomainError(404, "ERR_NOT_FOUND", "Job Not Found", "Job analisis tidak ada.")
    ver = repo.versions[run.doc_version_id]
    doc = repo.documents[ver.document_id]
    assert_document_scope(doc, current_user, write=False)

    async def _event_generator() -> AsyncIterator[str]:
        s1_nodes = [
            n for n in run.nodes if n["node_type"] in {"Claim", "ExplicitPremise", "Evidence"}
        ]
        s2_nodes = [
            n for n in run.nodes if n["node_type"] in {"ImplicitPremise", "Counterargument"}
        ]
        s1 = json.dumps({"nodes": s1_nodes, "edges": run.edges})
        s2 = json.dumps({"nodes": s2_nodes, "gaps": run.gaps})
        s3 = json.dumps({"run_id": run.id, "scores": run.scores})
        yield f"event: stage_1_structure\ndata: {s1}\n\n"
        yield f"event: stage_2_implicit_gaps\ndata: {s2}\n\n"
        yield f"event: stage_3_scoring_complete\ndata: {s3}\n\n"

    return StreamingResponse(_event_generator(), media_type="text/event-stream")
