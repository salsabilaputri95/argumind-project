Tujuan: Menetapkan strategi pengujian perangkat lunak dan evaluasi riset, target cakupan kode, perintah eksekusi, checklist *Definition of Done*, lokasi fixture/mock, serta aturan verifikasi wajib bagi agen/pengembang pada proyek Argumind.
Status dan tanggal: Draft v1.0 | 2026-11-18
Sumber kebenaran untuk: Pipeline pengujian otomatis (`C-WEB`, `C-API`, `C-NLP`, `packages/evaluation-metrics`) dan syarat kelulusan fitur `F-01`–`F-07`.

# Standar Pengujian & Verifikasi (Testing): Argumind Platform

---

## 1. Matriks Jenis Pengujian (Test Types)

| Jenis Tes | Tool & Versi (`ASUMSI`) | Objek yang Diuji | Lokasi & Konvensi Penamaan File |
|---|---|---|---|
| **Unit Test (Frontend)** | `Vitest ^2.1` + `@testing-library/react ^16.0` | Fungsi utilitas span, store `Zustand`, validator `Zod`, dan state komponen UI (`P-01`–`P-07`). | `apps/web/src/**/__tests__/*.test.ts(x)` |
| **Unit Test (Backend & NLP)** | `pytest ^8.3` + `pytest-asyncio ^0.24` | Pra-pemrosesan 6 tahap (`word_count 300..2500`), `pii_redaction`, algoritma Chu-Liu/Edmonds DAG (`no self-loop`), dan validator `grounded_refs`. | `apps/api/tests/unit/test_*.py`, `apps/nlp-worker/tests/unit/test_*.py` |
| **Unit Test Metrik Riset** | `pytest ^8.3` + `hypothesis ^6.115` | Ketepatan rumus matematis `Macro-F1`, `QWK`, $\alpha_{\text{Krip}}$, `BERTScore-F1`, $\rho_{YL \cdot H}$, dan `FaithfulnessRate`. | `packages/evaluation-metrics/tests/test_*.py` |
| **Integration Test (API & DB)** | `pytest` + `httpx.AsyncClient` + `testcontainers` (`Postgres 16`, `Redis 7.4`) | Kontrak endpoint (`→ docs/DATA_MODEL.md#5b-tabel-endpoint-utama`), isolasi RBAC (`OWN`, `ORG`, `BLIND`), rotasi JWT/CSRF, dan stream `SSE`. | `apps/api/tests/integration/test_*_api.py` |
| **End-to-End (E2E) & A11y** | `Playwright ^1.48` + `@axe-core/playwright ^4.10` | Alur penuh `F-01`–`F-07`, sorotan dua arah teks-graf ($\le 100\text{ ms}$), responsivitas `375px`/`768px`/`1440px`, dan audit kontras WCAG 2.1 AA. | `tests/e2e/*.spec.ts` |
| **Load & Latency Test** | `k6 ^0.54` | Anggaran latensi Tahap 1 `p95 <= 4.0s` dan pipeline penuh `p95 <= 15.0s` (`→ docs/ARCHITECTURE.md#8-target-non-fungsional-terukur-arsitektur--frontend`). | `tests/load/pipeline_latency.k6.js` |

---

## 2. Perintah Eksekusi dan Target Cakupan (Coverage) per Lapisan

PR atau tugas dinyatakan **GAGAL** jika cakupan baris (*line coverage*) atau cabang (*branch coverage*) turun di bawah angka target berikut:

| Lapisan / Paket | Perintah Eksekusi | Target Line Coverage | Target Branch Coverage |
|---|---|---|---|
| **Paket Skema & Metrik Riset (`packages/*`)** | `pytest packages/evaluation-metrics --cov=packages/evaluation-metrics --cov-fail-under=95` | `>= 95.0%` | `>= 90.0%` |
| **Backend API & Auth Policy (`apps/api`)** | `pytest apps/api/tests --cov=apps/api/src --cov-fail-under=85` | `>= 85.0%` | `>= 80.0%` |
| **NLP Worker & DAG Decoder (`apps/nlp-worker`)** | `pytest apps/nlp-worker/tests --cov=apps/nlp-worker/src --cov-fail-under=85` | `>= 85.0%` | `>= 80.0%` |
| **Web Frontend (`apps/web`)** | `pnpm --filter web test:coverage` | `>= 80.0%` | `>= 75.0%` |
| **E2E & Aksesibilitas (`tests/e2e`)** | `pnpm exec playwright test` | `100%` dari 3 Alur Utama (`→ docs/PAGES_AND_FLOWS.md#5-alur-utama-pengguna-end-to-end-flows`) | Seluruh jalur gagal (`403`, `422`, `504`) wajib teruji |

---

## 3. Checklist *Definition of Done* (DoD) Berurutan

Setiap fitur (`F-01`–`F-07`) atau perbaikan bug WAJIB melewati 8 langkah berikut secara berurutan sebelum ditandai selesai:
1. [ ] **Lint Bersih (`0 warning, 0 error`):** `pnpm lint` (ESLint) dan `ruff check . && ruff format --check .` lulus tanpa pengecualian.
2. [ ] **Typecheck Ketat Lulus:** `pnpm typecheck` (`tsc --noEmit`) dan `mypy apps/ packages/` lulus dengan `0` error.
3. [ ] **Build Produksi Berhasil:** `pnpm --filter web build` berhasil dan ukuran bundle awal $\le 180\text{ KB}$ (kanvas `@xyflow/react` $\le 120\text{ KB}$ gzipped).
4. [ ] **Seluruh Tes & Target Coverage Lulus:** Unit test, integration test, dan E2E test lulus 100% memenuhi ambang tabel Bagian 2.
5. [ ] **Verifikasi Responsif 3 Ukuran Layar:** Halaman diuji pada viewport Playwright **`375x812 px` (Mobile — otomatis beralih ke Card List View)**, **`768x1024 px` (Tablet — collapsible drawer)**, dan **`1440x900 px` (Desktop — Split Pane 3 kolom)**.
6. [ ] **Audit Aksesibilitas WCAG 2.1 AA Lulus:** `@axe-core/playwright` melaporkan `0` pelanggaran; navigasi `Tab`/`Arrow` dan `--focus-ring` pada node graf berfungsi.
7. [ ] **State Layar & Error Terverifikasi:** State `Loading` (*skeleton*), `Empty`, `Error` (`RFC 9457` + `trace_id`), dan `403` bekerja sesuai spesifikasi.
8. [ ] **Dokumentasi Progres Diperbarui:** Status item terkait dicentang pada `→ docs/PROGRESS.md` (atau `→ research/RESEARCH_PROGRESS.md` untuk tugas riset).

---

## 4. Lokasi Fixture, Mock, dan Seed Data

- **Fixture Dokumen & Graf Standar:** `tests/fixtures/documents/` (berisi sampel deterministik: `valid_academic_500w.txt`, `valid_policy_1200w.docx`, `invalid_short_215w.txt`, `corrupt_scan.pdf`, dan `sample_graph_run.json`).
- **Mock Respons `EXT-LLM`:** `tests/fixtures/llm_mocks/` (menyimpan respons JSON deterministik untuk uji `F-03`–`F-05` serta payload cacat tanpa `grounded_refs` untuk menguji penolakan `422 ERR_UNFAITHFUL_SCORE`).
- **Database Seed Pengembangan:** `infra/migrations/seed_dev.py` (membuat 1 organisasi, 4 akun untuk tiap peran `author`/`reviewer`/`annotator`/`org_admin`, dan 2 dokumen contoh). JANGAN menjalankan `seed_dev.py` pada environment `prod`.

---

## 5. Aturan Wajib bagi Agen AI dan Pengembang (Verification Rules)

1. **Jalankan Verifikasi Sendiri:** Agen/pengembang WAJIB mengeksekusi perintah lint, typecheck, dan test secara langsung di terminal sebelum menyatakan pekerjaan selesai.
2. **Laporkan Output Nyata:** Sertakan ringkasan hasil eksekusi aktual (jumlah tes lulus, durasi, dan persentase coverage). **JANGAN** mengklaim tes lulus tanpa pernah menjalankannya.
3. **Integritas Pengujian:** **JANGAN PERNAH** menghapus tes yang gagal, menambahkan `.skip` / `@pytest.mark.skip`, melonggarkan assertion, menggunakan `# type: ignore` / `@ts-expect-error`, atau menurunkan ambang `--cov-fail-under` hanya agar pipeline terlihat hijau. Perbaiki akar masalah pada kode implementasi.

---

## 6. Pengujian Evaluasi Penelitian (Research Evaluation Gates)

Sebelum menjalankan eksperimen `E-01`–`E-03b` (`→ research/EXPERIMENT_PLAN.md`), paket `packages/evaluation-metrics` WAJIB lulus *toy-data verification test* berikut:
1. **Uji Invariant Metrik:** Memastikan perhitungan `Macro-F1` ($\text{IoU} = 1.0$ dan $\text{IoU} \ge 0.5$), `QWK`, $\alpha_{\text{Krip}}$, $\rho_{YL \cdot H}$, dan `FaithfulnessRate` pada matriks input sintetis menghasilkan nilai yang sama persis hingga `6` desimal (`toleransi 1e-6`) dengan perhitungan analitik manual.
2. **Uji Regresi Baseline (`B1`–`B5`) vs Model (`M1`–`M3`):** Skrip `pytest research/tests/test_runner_smoke.py` WAJIB menguji *pipeline* dari ujung ke ujung pada `3` dokumen sintetis untuk memastikan format `config_locked.json`, `predictions.jsonl`, dan `metrics_raw.json` valid sebelum menggunakan kuota GPU/LLM penuh.

---

## 7. Pertanyaan Terbuka

1. `TODO(Q-TEST-01 — Browser Target E2E di CI)`: Apakah eksekusi Playwright pada setiap Pull Request cukup dijalankan pada `Chromium` + `Mobile Safari (WebKit)` untuk kecepatan CI ($\le 5\text{ menit}$), sedangkan suite penuh (`Chromium`, `Firefox`, `WebKit`) dijalankan sebelum rilis ke `staging`/`prod`?
