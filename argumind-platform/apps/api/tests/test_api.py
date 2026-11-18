from __future__ import annotations

from collections.abc import AsyncIterator, Generator
from contextlib import asynccontextmanager

import httpx
import pytest
from argumind_api.auth.security import generate_totp_code
from argumind_api.main import app
from argumind_api.store import repo


def _sample_text_350w() -> str:
    base = (
        "Oleh: Andi Pratama (NIM 210099)\n\n"
        "Pemerintah wajib memprioritaskan pembangunan transportasi publik berbasis rel "
        "di kota besar. Berdasarkan data survei mobilitas tahun 2025, kemacetan menyerap "
        "30% waktu produktif pekerja. Namun, perluasan jalan tol justru memicu peningkatan "
        "volume kendaraan pribadi setiap tahunnya. "
    )
    filler = (
        "Investasi angkutan massal menciptakan akses yang adil bagi masyarakat berpenghasilan "
        "menengah. Studi kebijakan menunjukkan subsidi operasional bus listrik menurunkan "
        "emisi karbon perkotaan. "
    ) * 16
    return base + filler


@pytest.fixture(autouse=True)
def reset_repo() -> Generator[None, None, None]:
    repo.documents.clear()
    repo.versions.clear()
    repo.runs.clear()
    repo.audit_logs.clear()
    repo.revoked_jtis.clear()
    repo.active_refresh_tokens.clear()
    yield


@asynccontextmanager
async def _login_client(email: str) -> AsyncIterator[tuple[httpx.AsyncClient, str]]:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post(
            "/api/v1/auth/login", json={"email": email, "password": "Argumind123!"}
        )
        assert resp.status_code == 200
        yield client, str(resp.json()["csrf_token"])


@pytest.mark.asyncio
async def test_auth_mfa_refresh_reuse_and_logout() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        r_admin = await client.post(
            "/api/v1/auth/login",
            json={"email": "admin@argumind.id", "password": "Argumind123!"},
        )
        assert r_admin.status_code == 200
        assert r_admin.json()["mfa_required"] is True
        challenge = r_admin.json()["mfa_challenge_token"]
        code = generate_totp_code("JBSWY3DPEHPK3PXP")
        r_mfa = await client.post(
            "/api/v1/auth/mfa/verify",
            json={"mfa_challenge_token": challenge, "totp_code": code},
        )
        assert r_mfa.status_code == 200
        csrf = r_mfa.json()["csrf_token"]

        r_me = await client.get("/api/v1/auth/me")
        assert r_me.status_code == 200
        assert r_me.json()["role"] == "org_admin"

        old_refresh = client.cookies.get("argumind_refresh_token")
        assert old_refresh is not None
        r_ref = await client.post("/api/v1/auth/refresh", headers={"X-CSRF-Token": csrf})
        assert r_ref.status_code == 200

        # Uji reuse detection: memakai ulang refresh token lama wajib ditolak (401)
        client.cookies.set("argumind_refresh_token", old_refresh)
        r_reuse = await client.post("/api/v1/auth/refresh")
        assert r_reuse.status_code == 401

        r_out = await client.post("/api/v1/auth/logout", headers={"X-CSRF-Token": csrf})
        assert r_out.status_code == 200
        assert (await client.get("/api/v1/auth/me")).status_code == 401


@pytest.mark.asyncio
async def test_upload_word_bounds_analyze_and_sse_stream() -> None:
    async with _login_client("author@argumind.id") as (client, csrf):
        assert (await client.get("/health")).status_code == 200
        r_short = await client.post(
            "/api/v1/documents",
            headers={"X-CSRF-Token": csrf},
            data={
                "title": "Terlalu Pendek",
                "domain_strata": "academic",
                "text": "Cuma sepuluh kata.",
            },
        )
        assert r_short.status_code == 422
        assert r_short.json()["code"] == "ERR_WORD_COUNT_BOUNDS"

        r_ok = await client.post(
            "/api/v1/documents",
            headers={"X-CSRF-Token": csrf},
            data={
                "title": "Kajian Subsidi Transportasi",
                "domain_strata": "policy_business",
                "research_opt_in": "true",
                "text": _sample_text_350w(),
            },
        )
        assert r_ok.status_code == 201
        doc_id = r_ok.json()["document"]["id"]

        r_list = await client.get("/api/v1/documents?limit=10&offset=0")
        assert r_list.status_code == 200
        assert r_list.json()["meta"]["total"] == 1

        r_analyze = await client.post(
            f"/api/v1/documents/{doc_id}/versions/1/analyze",
            headers={"X-CSRF-Token": csrf},
            json={"generate_counterarguments": True},
        )
        assert r_analyze.status_code == 202
        job_id = r_analyze.json()["job_id"]

        r_stream = await client.get(f"/api/v1/jobs/{job_id}/stream")
        assert r_stream.status_code == 200
        assert "event: stage_1_structure" in r_stream.text
        assert "event: stage_2_implicit_gaps" in r_stream.text
        assert "event: stage_3_scoring_complete" in r_stream.text

        r_run = await client.get(f"/api/v1/runs/{job_id}")
        assert r_run.status_code == 200
        body = r_run.json()
        assert "[REDACTED_NAME]" in body["clean_text"]
        assert len(body["scores"]) == 4
        assert all(len(s["grounded_refs"]) >= 1 for s in body["scores"])

        # Author dapat memberi feedback node N-01
        r_fb = await client.patch(
            f"/api/v1/runs/{job_id}/nodes/N-01/feedback",
            headers={"X-CSRF-Token": csrf},
            json={"user_feedback": "ACCEPTED"},
        )
        assert r_fb.status_code == 200
        assert r_fb.json()["user_feedback"] == "ACCEPTED"

        # Author tidak boleh override skor rubrik (403)
        r_forbid = await client.patch(
            f"/api/v1/runs/{job_id}/scores/EvidenceAdequacy",
            headers={"X-CSRF-Token": csrf},
            json={"human_override_score": 5, "override_note": "Mencoba ubah nilai sendiri."},
        )
        assert r_forbid.status_code == 403


@pytest.mark.asyncio
async def test_reviewer_override_and_double_blind_adjudication_f06() -> None:
    async with _login_client("author@argumind.id") as (c_auth, csrf_auth):
        r_doc = await c_auth.post(
            "/api/v1/documents",
            headers={"X-CSRF-Token": csrf_auth},
            data={
                "title": "Esai Uji Anotasi",
                "domain_strata": "academic",
                "text": _sample_text_350w(),
            },
        )
        doc_id = r_doc.json()["document"]["id"]
        doc_ver_id = r_doc.json()["version"]["id"]
        r_ai = await c_auth.post(
            f"/api/v1/documents/{doc_id}/versions/1/analyze",
            headers={"X-CSRF-Token": csrf_auth},
            json={"generate_counterarguments": True},
        )
        ai_run_id = r_ai.json()["job_id"]

    async with _login_client("reviewer@argumind.id") as (c_rev, csrf_rev):
        r_short_note = await c_rev.patch(
            f"/api/v1/runs/{ai_run_id}/scores/EvidenceAdequacy",
            headers={"X-CSRF-Token": csrf_rev},
            json={"human_override_score": 4, "override_note": "pendek"},
        )
        assert r_short_note.status_code == 422

        r_override = await c_rev.patch(
            f"/api/v1/runs/{ai_run_id}/scores/EvidenceAdequacy",
            headers={"X-CSRF-Token": csrf_rev},
            json={
                "human_override_score": 4,
                "override_note": "Bukti survei 2025 sudah memadai untuk konteks lokal.",
            },
        )
        assert r_override.status_code == 200
        assert r_override.json()["human_override_score"] == 4

    clean_text = repo.versions[doc_ver_id].clean_text
    s0_end = clean_text.index(".") + 1
    s1_start = clean_text.find("Pemerintah")
    s1_end = clean_text.index(".", s1_start) + 1
    payload_valid = {
        "nodes": [
            {
                "node_key": "N-01",
                "node_type": "Claim",
                "start_char": s1_start,
                "end_char": s1_end,
                "text_content": clean_text[s1_start:s1_end],
            },
            {
                "node_key": "N-02",
                "node_type": "ExplicitPremise",
                "start_char": 0,
                "end_char": s0_end,
                "text_content": clean_text[0:s0_end],
            },
        ],
        "edges": [
            {
                "edge_key": "E-01",
                "source_key": "N-02",
                "target_key": "N-01",
                "relation_type": "Support",
                "confidence": 0.9,
            }
        ],
        "gaps": [],
        "scores": [
            {
                "dimension": "ClarityOfClaim",
                "ai_score": 4,
                "grounded_refs": ["N-01"],
                "rationale": "Klaim N-01 tertulis jelas.",
            },
            {
                "dimension": "EvidenceAdequacy",
                "ai_score": 3,
                "grounded_refs": ["N-02"],
                "rationale": "Didukung premis N-02.",
            },
        ],
    }

    async with _login_client("annotator1@argumind.id") as (c_ann1, csrf_a1):
        assert (await c_ann1.get(f"/api/v1/runs/{ai_run_id}")).status_code == 403
        r_put1 = await c_ann1.put(
            f"/api/v1/annotations/{doc_ver_id}",
            headers={"X-CSRF-Token": csrf_a1},
            json=payload_valid,
        )
        assert r_put1.status_code == 200
        ann1_run_id = r_put1.json()["run_id"]

    async with _login_client("annotator2@argumind.id") as (c_ann2, csrf_a2):
        assert (await c_ann2.get(f"/api/v1/runs/{ann1_run_id}")).status_code == 403
        async with _login_client("reviewer@argumind.id") as (c_rev_early, csrf_early):
            r_early_adj = await c_rev_early.post(
                f"/api/v1/annotations/{doc_ver_id}/adjudicate",
                headers={"X-CSRF-Token": csrf_early},
                json=payload_valid,
            )
            assert r_early_adj.status_code == 422

        cyclic_payload = {
            **payload_valid,
            "edges": [
                {
                    "edge_key": "E-01",
                    "source_key": "N-02",
                    "target_key": "N-01",
                    "relation_type": "Support",
                    "confidence": 0.9,
                },
                {
                    "edge_key": "E-02",
                    "source_key": "N-01",
                    "target_key": "N-02",
                    "relation_type": "Support",
                    "confidence": 0.8,
                },
            ],
        }
        r_cyc = await c_ann2.put(
            f"/api/v1/annotations/{doc_ver_id}",
            headers={"X-CSRF-Token": csrf_a2},
            json=cyclic_payload,
        )
        assert r_cyc.status_code == 422
        assert r_cyc.json()["code"] == "ERR_CYCLE_DETECTED"

        r_put2 = await c_ann2.put(
            f"/api/v1/annotations/{doc_ver_id}",
            headers={"X-CSRF-Token": csrf_a2},
            json=payload_valid,
        )
        assert r_put2.status_code == 200

    async with _login_client("reviewer@argumind.id") as (c_rev2, csrf_rev2):
        r_runs = await c_rev2.get(
            f"/api/v1/runs?doc_version_id={doc_ver_id}&run_source=human_annotator"
        )
        assert r_runs.status_code == 200
        assert r_runs.json()["meta"]["total"] == 2
        r_adj = await c_rev2.post(
            f"/api/v1/annotations/{doc_ver_id}/adjudicate",
            headers={"X-CSRF-Token": csrf_rev2},
            json=payload_valid,
        )
        assert r_adj.status_code == 201
        assert r_adj.json()["run_source"] == "gold_adjudicated"
        assert r_adj.json()["agreement_metrics"]["krippendorff_alpha"] == 1.0
        assert r_adj.json()["agreement_metrics"]["qwk"] == 1.0
