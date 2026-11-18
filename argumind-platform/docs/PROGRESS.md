Tujuan: Melacak status implementasi fitur (`F-01`–`F-07`), fase rilis aktif, langkah kerja berikutnya, hambatan (*blockers*), dan 10 log aktivitas terakhir untuk platform Argumind.
Status dan tanggal: Aktif | 2026-11-18
Sumber kebenaran untuk: Titik mulai sesi pengembangan baru (`argumind-platform/`) dan status kelulusan fitur.

# Pelacak Progres Pengembangan (PROGRESS.md): Argumind Platform

- **Tanggal Pembaruan Terakhir:** `2026-11-18`
- **Fase Aktif Saat Ini:** **Pra-Fase 1 (Spesifikasi Selesai $\rightarrow$ Siap Scaffolding Monorepo & Fase 1)**

### Langkah Berikutnya (Maks 3 — Mulai dari Sini pada Sesi Baru)
1. **Inisialisasi Monorepo & Skema Bersama:** Buat kerangka direktori `apps/web`, `apps/api`, `apps/nlp-worker`, `packages/shared-schemas`, dan `packages/evaluation-metrics` beserta `tsconfig.json`, `pyproject.toml`, dan `docker-compose.yml` (`→ docs/ARCHITECTURE.md#3-pohon-folder-monorepo`).
2. **Migrasi Database & RBAC Dasar:** Implementasikan migrasi Alembic untuk 9 tabel di `→ docs/DATA_MODEL.md#1-skema-entitas-database-postgresql-16` serta middleware JWT `HttpOnly` + scope `OWN`/`ORG`/`BLIND` (`→ docs/ROLES_PERMISSIONS.md`).
3. **Implementasi `F-01` & `F-06` (Fase 1):** Bangun pipeline pra-pemrosesan 6 tahap (`word_count 300..2500`, `pii_redaction`) dan halaman ruang kerja anotasi *double-blind* (`P-05`, `P-06`) agar pengumpulan korpus riset dapat dimulai.

---

## 1. Checklist Progres per Fase Rilis

Format: `- [ ] ID deskripsi | pemilik | status` (`todo`, `doing`, `done`, `blocked`). Roadmap mengacu pada `→ docs/PRD.md#7c-fase-rilis-roadmap-8-minggu`.

### Fase 0 — Dokumentasi Spesifikasi & Arsitektur (Minggu 0)
- [x] `SPEC-01` Penyusunan seluruh 11 dokumen spesifikasi `docs/` + `AGENTS.md` | Tech Lead & AI Agent | `done`

### Fase 1 — Fondasi Monorepo, Segmentasi Dasar, & Alat Anotasi Riset (Minggu 1–3)
- [ ] `INFRA-01` Scaffolding monorepo, Docker Compose (`Postgres 16`, `Redis 7.4`), dan skema OpenAPI/Pydantic/Zod | Backend Lead | `todo`
- [ ] `AUTH-01` Autentikasi JWT `RS256` Cookie `HttpOnly`, OIDC SSO, MFA `TOTP`, dan middleware RBAC (`P-01`) | Backend Lead | `todo`
- [ ] `F-01` Unggah dokumen (`.txt`/`.md`/`.docx`/`.pdf`), validasi `300..2500` kata, `pii_redaction`, & segmentasi komponen (`P-02`) | NLP & Backend | `todo`
- [ ] `F-02` Pemetaan relasi `Support`/`Attack` (Chu-Liu/Edmonds DAG) & kanvas `@xyflow/react` + `tokens.css` (`P-03`) | Frontend & NLP | `todo`
- [ ] `F-06` Ruang kerja anotasi *double-blind* (`P-05`), kalkulator $\alpha_{\text{Krip}}$/`QWK`, & konsol adjudikasi (`P-06`) | Fullstack | `todo`

### Fase 2 — Inti Penalaran Implisit, Rubrik Terjelaskan, & Kontraargumen (Minggu 4–6)
- [ ] `F-03` Deteksi `ImplicitPremise` & 6 kategori `ReasoningGap` terkondisi sub-graf NLI + streaming `SSE`Tahap 2 | NLP Lead | `todo`
- [ ] `F-04` Penilaian rubrik 4 dimensi skala `1..5` dengan validasi wajib `grounded_refs` & form override `reviewer` | NLP & Fullstack | `todo`
- [ ] `F-05` Generator kontraargumen terarah (`1..3` `Counterargument` per node target) | NLP & Frontend | `todo`

### Fase 3 — Perbandingan Revisi, Ekspor, & Uji Pilot (Minggu 7–8)
- [ ] `F-07` Halaman perbandingan revisi draf (`vA` vs `vB`) & ekspor laporan `.pdf`/`.json` $\le 3\text{s}$ (`P-04`) | Frontend & Backend | `todo`
- [ ] `ADMIN-01` Panel organisasi (`P-07`), manajemen kuota bulanan, & ekspor korpus riset (`research_opt_in = true`) | Fullstack | `todo`
- [ ] `QA-01` Audit penuh E2E Playwright (`375px`, `768px`, `1440px`), WCAG 2.1 AA, dan uji beban `k6` (`p95 <= 15s`) | QA & Tech Lead | `todo`

---

## 2. Tabel Blocker Aktif

| ID Blocker | Masalah / Keputusan yang Memblokir | Dampak terhadap Pengembangan | Butuh Keputusan Dari |
|---|---|---|---|
| **BLK-01** | Konfirmasi *checkpoint* model `IndoBERT`/NLI dan penyedia `EXT-LLM` (`TODO(Q-METH-02)`, `TODO(Q-ARCH-02)`). | Memblokir konfigurasi worker `C-NLP` untuk `F-01`–`F-05`. | Peneliti Utama & Arsitek |
| **BLK-02** | Pengesahan status `ADR-01` s.d. `ADR-04` dari `Diusulkan` menjadi `Diterima` (`TODO(Q-ADR-01)`). | Memblokir penguncian versi akhir pada `package.json` dan `pyproject.toml`. | Tech Lead / Pengguna |

---

## 3. Log Aktivitas Terakhir (Maks 10 Entri — Selebihnya Pindah ke `docs/PROGRESS_ARCHIVE.md`)

1. `2026-11-18` — Menyelesaikan `AGENTS.md`, `docs/PROGRESS.md`, dan `research/RESEARCH_PROGRESS.md`.
2. `2026-11-18` — Menyelesaikan `docs/CODE_STYLE.md`, `docs/TESTING.md`, dan `docs/GIT_WORKFLOW.md`.
3. `2026-11-18` — Menyelesaikan `docs/PAGES_AND_FLOWS.md`, `docs/DESIGN_SYSTEM.md` (+ `color-palette-preview.html`), dan `docs/DECISIONS.md` (`ADR-01`–`ADR-06`).
4. `2026-11-18` — Menyelesaikan `docs/ARCHITECTURE.md`, `docs/DATA_MODEL.md`, dan `docs/ROLES_PERMISSIONS.md`.
5. `2026-11-17` — Menyelesaikan `docs/_WRITING_RULES.md` dan `docs/PRD.md` (`F-01`–`F-07`).
