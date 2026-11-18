from __future__ import annotations

import os
import uuid

from argumind_nlp.preprocessing import DocumentProcessingError
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from argumind_api.errors import ArgumindDomainError
from argumind_api.routers.auth_router import router as auth_router
from argumind_api.routers.documents_router import router as documents_router
from argumind_api.routers.runs_router import router as runs_router


def _problem_response(status: int, code: str, title: str, detail: str) -> JSONResponse:
    trace_id = f"req_{uuid.uuid4().hex[:10]}"
    slug = code.lower().replace("_", "-")
    return JSONResponse(
        status_code=status,
        content={
            "type": f"https://argumind.id/errors/{slug}",
            "title": title,
            "status": status,
            "code": code,
            "detail": detail,
            "trace_id": trace_id,
        },
        media_type="application/problem+json",
    )


def create_app() -> FastAPI:
    app = FastAPI(title="Argumind Core API", version="0.1.0")
    allowed_origins = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in allowed_origins if o.strip()],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(ArgumindDomainError)
    async def handle_domain_error(_: Request, exc: ArgumindDomainError) -> JSONResponse:
        return _problem_response(exc.status_code, exc.code, exc.title, exc.detail)

    @app.exception_handler(DocumentProcessingError)
    async def handle_doc_error(_: Request, exc: DocumentProcessingError) -> JSONResponse:
        return _problem_response(exc.status_code, exc.code, "Document Processing Error", exc.detail)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        return _problem_response(422, "ERR_VALIDATION", "Validation Error", str(exc.errors()))

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(auth_router)
    app.include_router(documents_router)
    app.include_router(runs_router)
    return app


app = create_app()
