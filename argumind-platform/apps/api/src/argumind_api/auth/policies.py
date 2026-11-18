from __future__ import annotations

from argumind_api.errors import ArgumindDomainError
from argumind_api.store import AnalysisRunRecord, DocumentRecord, UserRecord, repo


def _forbid(
    user: UserRecord, resource_type: str, resource_id: str, reason: str
) -> ArgumindDomainError:
    repo.record_audit(
        actor_user_id=user.id,
        actor_role=user.role,
        org_id=user.org_id,
        action_code="ACCESS_FORBIDDEN_SCOPE",
        target_resource_type=resource_type,
        target_resource_id=resource_id,
        metadata_diff={"reason": reason},
    )
    return ArgumindDomainError(403, "ERR_ROLE_FORBIDDEN", "Access Forbidden", reason)


def assert_document_scope(doc: DocumentRecord, user: UserRecord, write: bool = False) -> None:
    """Tegakkan scope OWN (author), ORG (reviewer/org_admin), dan BLIND (annotator)."""
    if user.role == "author":
        if doc.author_id != user.id:
            raise _forbid(
                user, "documents", doc.id, "Author hanya dapat mengakses dokumen miliknya."
            )
        return
    if user.role in {"reviewer", "org_admin"}:
        if doc.org_id != user.org_id:
            raise _forbid(user, "documents", doc.id, "Akses lintas organisasi ditolak.")
        if write and user.role == "reviewer" and doc.author_id != user.id:
            raise _forbid(
                user, "documents", doc.id, "Reviewer hanya dapat mengubah dokumen miliknya."
            )
        return
    if user.role == "annotator":
        if write or doc.org_id != user.org_id:
            raise _forbid(user, "documents", doc.id, "Anotator hanya memiliki akses baca blind.")
        return
    raise _forbid(user, "documents", doc.id, "Peran tidak dikenali.")


def assert_run_scope(run: AnalysisRunRecord, doc: DocumentRecord, user: UserRecord) -> None:
    """Tegakkan isolasi double-blind annotator pada F-06 dan scope OWN/ORG."""
    if doc.org_id != user.org_id and doc.author_id != user.id:
        raise _forbid(user, "analysis_runs", run.id, "Akses lintas organisasi ditolak.")

    if user.role == "annotator":
        # Anotator DILARANG membaca output ai_hybrid atau anotasi milik rekan anotator lain
        if run.run_source == "ai_hybrid":
            raise _forbid(user, "analysis_runs", run.id, "Anotator tidak boleh melihat hasil AI.")
        if run.run_source == "human_annotator" and run.actor_user_id != user.id:
            raise _forbid(
                user,
                "analysis_runs",
                run.id,
                "Mode double-blind: akses ke anotasi milik anotator lain dilarang.",
            )
        return

    if user.role == "author":
        if doc.author_id != user.id or run.run_source != "ai_hybrid":
            raise _forbid(
                user, "analysis_runs", run.id, "Author hanya mengakses hasil analisis miliknya."
            )
