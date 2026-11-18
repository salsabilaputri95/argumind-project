from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from argumind_api.auth.security import hash_password


@dataclass
class OrganizationRecord:
    id: str
    name: str
    slug: str
    monthly_doc_quota: int


@dataclass
class UserRecord:
    id: str
    org_id: str | None
    email: str
    full_name: str
    role: str
    password_hash: str
    totp_secret: str
    mfa_required: bool = False


@dataclass
class DocumentRecord:
    id: str
    org_id: str | None
    author_id: str
    title: str
    domain_strata: str
    research_opt_in: bool
    created_at: str


@dataclass
class DocumentVersionRecord:
    id: str
    document_id: str
    version_number: int
    source_format: str
    raw_s3_key: str | None
    clean_text: str
    content_sha256: str
    word_count: int
    paragraph_offsets: list[dict[str, int | str]]
    created_at: str


@dataclass
class AnalysisRunRecord:
    id: str
    doc_version_id: str
    run_source: str
    actor_user_id: str | None
    status: str
    model_versions: dict[str, str]
    latency_ms: int | None
    created_at: str
    nodes: list[dict[str, object]]
    edges: list[dict[str, object]]
    gaps: list[dict[str, object]]
    scores: list[dict[str, object]]


@dataclass
class AuditLogRecord:
    event_id: str
    timestamp: str
    actor_user_id: str | None
    actor_role: str
    org_id: str | None
    action_code: str
    target_resource_type: str
    target_resource_id: str
    metadata_diff: dict[str, object]


class InMemoryRepository:
    """Penyimpanan terstruktur sementara untuk dev/test sesuai skema DATA_MODEL.md."""

    def __init__(self) -> None:
        self.orgs: dict[str, OrganizationRecord] = {}
        self.users: dict[str, UserRecord] = {}
        self.users_by_email: dict[str, str] = {}
        self.documents: dict[str, DocumentRecord] = {}
        self.versions: dict[str, DocumentVersionRecord] = {}
        self.runs: dict[str, AnalysisRunRecord] = {}
        self.audit_logs: list[AuditLogRecord] = []
        self.revoked_jtis: set[str] = set()
        self.active_refresh_tokens: dict[str, str] = {}
        self.seed_defaults()

    def seed_defaults(self) -> None:
        org_id = "01933e00-0000-7000-8000-000000000001"
        self.orgs[org_id] = OrganizationRecord(
            id=org_id, name="Universitas Argumind", slug="univ-argumind", monthly_doc_quota=100
        )
        default_pw = hash_password("Argumind123!")
        seed_users = [
            UserRecord(
                id="01933e00-0000-7000-8000-000000000011",
                org_id=org_id,
                email="author@argumind.id",
                full_name="Mahasiswa Penulis",
                role="author",
                password_hash=default_pw,
                totp_secret="JBSWY3DPEHPK3PXP",
            ),
            UserRecord(
                id="01933e00-0000-7000-8000-000000000012",
                org_id=org_id,
                email="reviewer@argumind.id",
                full_name="Dosen Penilai",
                role="reviewer",
                password_hash=default_pw,
                totp_secret="JBSWY3DPEHPK3PXP",
            ),
            UserRecord(
                id="01933e00-0000-7000-8000-000000000013",
                org_id=org_id,
                email="annotator1@argumind.id",
                full_name="Anotator Satu",
                role="annotator",
                password_hash=default_pw,
                totp_secret="JBSWY3DPEHPK3PXP",
            ),
            UserRecord(
                id="01933e00-0000-7000-8000-000000000014",
                org_id=org_id,
                email="annotator2@argumind.id",
                full_name="Anotator Dua",
                role="annotator",
                password_hash=default_pw,
                totp_secret="JBSWY3DPEHPK3PXP",
            ),
            UserRecord(
                id="01933e00-0000-7000-8000-000000000015",
                org_id=org_id,
                email="admin@argumind.id",
                full_name="Admin Institusi",
                role="org_admin",
                password_hash=default_pw,
                totp_secret="JBSWY3DPEHPK3PXP",
                mfa_required=True,
            ),
        ]
        for u in seed_users:
            self.users[u.id] = u
            self.users_by_email[u.email] = u.id

    def record_audit(
        self,
        actor_user_id: str | None,
        actor_role: str,
        org_id: str | None,
        action_code: str,
        target_resource_type: str,
        target_resource_id: str,
        metadata_diff: dict[str, object] | None = None,
    ) -> None:
        self.audit_logs.append(
            AuditLogRecord(
                event_id=str(uuid.uuid4()),
                timestamp=datetime.now(UTC).isoformat(),
                actor_user_id=actor_user_id,
                actor_role=actor_role,
                org_id=org_id,
                action_code=action_code,
                target_resource_type=target_resource_type,
                target_resource_id=target_resource_id,
                metadata_diff=metadata_diff or {},
            )
        )


repo = InMemoryRepository()
