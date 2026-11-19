Tujuan: Melacak status implementasi fitur (`F-01`–`F-07`), fase rilis aktif, langkah kerja berikutnya, hambatan (*blockers*), dan 10 log aktivitas terakhir untuk platform Argumind.
Status dan tanggal: Aktif | 2026-11-18
Sumber kebenaran untuk: Titik mulai sesi pengembangan baru (`argumind-platform/`) dan status kelulusan fitur.

# Pelacak Progres Pengembangan (PROGRESS.md): Argumind Platform

- **Tanggal Pembaruan Terakhir:** `2026-11-19`
- **Fase Aktif Saat Ini:** **Fase 2 — Inti Penalaran Implisit, Rubrik Terjelaskan, & Kontraargumen (Minggu 4–6)**

### Langkah Berikutnya (Maks 3 — Mulai dari Sini pada Sesi Baru)
1. **Integrasi Checkpoint IndoBERT/NLI & Penyelesaian `F-03`–`F-05`:** Hubungkan bobot hasil fine-tuning Colab (`research/outputs/colab_*/best_*`) serta endpoint `EXT-LLM` (*zero data retention*) pada `apps/nlp-worker/src/argumind_nlp/reasoning.py` untuk rekonstruksi `ImplicitPremise`, `ReasoningGap`, skor rubrik, dan `Counterargument`.
2. **Verifikasi Build Frontend (`C-WEB`):** Jalankan `npm install --no-bin-links` di dalam `argumind-platform/apps/web`, pastikan `typecheck`, `lint`, dan `build` lulus, lalu uji E2E Playwright (`375px`, `768px`, `1440px`).
3. **Ekspansi Korpus Latih (`IndoArg-Analytical-v1`):** Gunakan ruang kerja anotasi `F-06` untuk memperbesar partisi `train` dari 8 dokumen benih menuju target korpus penuh ($N=400$) agar model BIO mencapai konvergensi optimal.

---

## 1. Checklist Progres per Fase Rilis

Format: `- [ ] ID deskripsi | pemilik | status` (`todo`, `doing`, `done`, `blocked`). Roadmap mengacu pada `→ docs/PRD.md#7c-fase-rilis-roadmap-8-minggu`.

### Fase 0 — Dokumentasi Spesifikasi & Arsitektur (Minggu 0)
- [x] `SPEC-01` Penyusunan seluruh 11 dokumen spesifikasi `docs/` + `AGENTS.md` | Tech Lead & AI Agent | `done`

### Fase 1 — Fondasi Monorepo, Segmentasi Dasar, & Alat Anotasi Riset (Minggu 1–3)
- [x] `INFRA-01` Scaffolding monorepo (`.venv`, `pyproject.toml`, Docker Compose, skema SQL 9 tabel, `shared-schemas`, `evaluation-metrics` cov 97%) | Backend Lead | `done`
- [x] `AUTH-01` Autentikasi JWT `RS256` Cookie `HttpOnly`, rotasi refresh token, MFA `TOTP`, dan middleware RBAC (`P-01`, `test_api` cov 90%) | Backend Lead | `done`
- [x] `F-01` Unggah dokumen (`.txt`/`.md`/`.docx`/`.pdf`), validasi `300..2500` kata, `pii_redaction`, & segmentasi komponen (`P-02`, `nlp-worker` cov 92%) | NLP & Backend | `done`
- [x] `F-02` Pemetaan relasi `Support`/`Attack` (Chu-Liu/Edmonds DAG) & kanvas `@xyflow/react` + `tokens.css` (`P-03`) | Frontend & NLP | `done`
- [x] `F-06` Ruang kerja anotasi *double-blind* (`P-05`), kalkulator $\alpha_{\text{Krip}}$/`QWK`, & konsol adjudikasi (`P-06`) | Fullstack | `done`

### Fase 2 — Inti Penalaran Implisit, Rubrik Terjelaskan, & Kontraargumen (Minggu 4–6)
- [ ] `F-03` Deteksi `ImplicitPremise` & 6 kategori `ReasoningGap` terkondisi sub-graf NLI + streaming `SSE` Tahap 2 | NLP Lead | `doing` (stub deterministik aktif)
- [ ] `F-04` Penilaian rubrik 4 dimensi skala `1..5` dengan validasi wajib `grounded_refs` & form override `reviewer` | NLP & Fullstack | `doing` (API & panel dasar aktif)
- [ ] `F-05` Generator kontraargumen terarah (`1..3` `Counterargument` per node target) | NLP & Frontend | `todo`

### Fase 3 — Perbandingan Revisi, Ekspor, & Uji Pilot (Minggu 7–8)
- [ ] `F-07` Halaman perbandingan revisi draf (`vA` vs `vB`) & ekspor laporan `.pdf`/`.json` $\le 3\text{s}$ (`P-04`) | Frontend & Backend | `todo`
- [ ] `ADMIN-01` Panel organisasi (`P-07`), manajemen kuota bulanan, & ekspor korpus riset (`research_opt_in = true`) | Fullstack | `todo`
- [ ] `QA-01` Audit penuh E2E Playwright (`375px`, `768px`, `1440px`), WCAG 2.1 AA, dan uji beban `k6` (`p95 <= 15s`) | QA & Tech Lead | `todo`

---

## 2. Tabel Blocker Aktif

| ID Blocker | Masalah / Keputusan yang Memblokir | Dampak terhadap Pengembangan | Butuh Keputusan Dari |
|---|---|---|---|
| **BLK-01** | Konfirmasi penyedia `EXT-LLM` produksi (`TODO(Q-METH-02)`, `TODO(Q-ARCH-02)`). | Memblokir implementasi penuh inferensi LLM pada `F-03`–`F-05` di Fase 2. | Peneliti Utama & Arsitek |
| **BLK-02** | Pengesahan status `ADR-01` s.d. `ADR-04` dari `Diusulkan` menjadi `Diterima` (`TODO(Q-ADR-01)`). | Menunggu konfirmasi akhir arsitek. | Tech Lead / Pengguna |

---

## 3. Log Aktivitas Terakhir (Maks 10 Entri — Selebihnya Pindah ke `docs/PROGRESS_ARCHIVE.md`)

1. `2026-11-19` — Menyelesaikan fine-tuning GPU T4 Google Colab (`IndoBERT BIO` + `Cross-Encoder NLI`), evaluasi `E-01` & `E-03b` (`seed 42`), merapikan `research/outputs/`, dan mencatat `[LOG-20261119-02]` & `[LOG-20261119-03]`.
2. `2026-11-18` — Menyelesaikan implementasi Fase 1 (`INFRA-01`, `AUTH-01`, `F-01`, `F-02`, `F-06`), 17/17 tes Python lulus (92% cov), Ruff 0 error, serta notebook Colab pelatihan IndoBERT/NLI.
2. `2026-11-18` — Menyelesaikan `AGENTS.md`, `docs/PROGRESS.md`, dan `research/RESEARCH_PROGRESS.md`.
3. `2026-11-18` — Menyelesaikan `docs/CODE_STYLE.md`, `docs/TESTING.md`, dan `docs/GIT_WORKFLOW.md`.
4. `2026-11-18` — Menyelesaikan `docs/PAGES_AND_FLOWS.md`, `docs/DESIGN_SYSTEM.md` (+ `color-palette-preview.html`), dan `docs/DECISIONS.md` (`ADR-01`–`ADR-06`).
5. `2026-11-18` — Menyelesaikan `docs/ARCHITECTURE.md`, `docs/DATA_MODEL.md`, dan `docs/ROLES_PERMISSIONS.md`.
6. `2026-11-17` — Menyelesaikan `docs/_WRITING_RULES.md` dan `docs/PRD.md` (`F-01`–`F-07`).
