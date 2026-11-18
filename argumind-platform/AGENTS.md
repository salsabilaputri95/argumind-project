Tujuan: Menjadi instruksi operasional utama bagi agen AI dan pengembang saat membaca dokumentasi, menulis kode, menjalankan tes, dan memperbarui progres di repositori Argumind.
Status dan tanggal: Draft v1.0 | 2026-11-18
Sumber kebenaran untuk: Peta pembacaan dokumen per tugas, daftar perintah kerja monorepo, serta sepuluh perintah wajib dan sepuluh larangan agen.

# Panduan Operasional Agen AI (AGENTS.md): Argumind Monorepo

## 1. Ringkasan Proyek & Stack Teknologi

**Ringkasan Satu Kalimat:** Argumind adalah platform dan proyek riset pemetaan graf struktur argumen (`Claim`, `ExplicitPremise`, `ImplicitPremise`, `Evidence`), deteksi celah penalaran, serta penilaian rubrik kualitas penalaran terjelaskan pada teks analitis Bahasa Indonesia.

- **Stack Terkunci (`→ docs/ARCHITECTURE.md#2-komponen-sistem-dan-diagram-komponen`):**
  - **Frontend (`C-WEB`):** Next.js `15.x` (App Router), React `19.x`, TypeScript `5.7.x`, Tailwind CSS `4.x`, `@xyflow/react ^12.3.x`, `elkjs ^0.9.x`, `TanStack Query ^5.60.x`, `Zustand ^5.0.x`, `Zod ^3.23.x`.
  - **Backend & Worker (`C-API`, `C-NLP`):** Python `3.12.7`, FastAPI `0.115.x`, Pydantic `2.10.x`, SQLAlchemy `2.0.x` (Async) + Alembic `1.14.x`, PyTorch `2.5.1+cu124`, Transformers `4.46.2`, NetworkX `3.4.2`, Celery `5.4.x`.
  - **Data & Broker (`C-DB`, `C-CACHE`):** PostgreSQL `16.x`, Redis `7.4.x`.

---

## 2. Tabel Perintah Standar Monorepo

| Aksi | Perintah Frontend (`C-WEB` / TS) | Perintah Backend, Worker, & Riset (Python) |
|---|---|---|
| **Install** | `pnpm install --frozen-lockfile` | `pip install --no-cache-dir -r research/requirements.lock` |
| **Dev** | `pnpm --filter web dev` | `uvicorn apps.api.src.main:app --reload --port 8000` |
| **Build** | `pnpm --filter web build` | `docker compose -f infra/docker/docker-compose.yml build` |
| **Lint** | `pnpm lint` | `ruff check . && ruff format --check .` |
| **Typecheck** | `pnpm typecheck` (`tsc --noEmit`) | `mypy apps/ packages/ research/` |
| **Test** | `pnpm --filter web test:coverage && pnpm exec playwright test` | `pytest apps/ packages/ --cov-fail-under=85` (`95` untuk `packages/`) |

---

## 3. Peta Jenis Tugas → File Dokumentasi yang Wajib Dibaca

| Jenis Tugas yang Dikerjakan | File yang WAJIB Dibaca Sebelum Menulis Kode/Teks |
|---|---|
| **Memulai sesi baru / mencari tugas berikutnya** | `docs/PROGRESS.md` (untuk platform) atau `research/RESEARCH_PROGRESS.md` (untuk riset). |
| **Menambah/mengubah halaman UI, komponen, atau kanvas graf (`C-WEB`)** | `docs/PAGES_AND_FLOWS.md`, `docs/DESIGN_SYSTEM.md`, `docs/CODE_STYLE.md`, `docs/ROLES_PERMISSIONS.md`. |
| **Menambah/mengubah endpoint API, skema DB, atau migrasi (`C-API`, `C-DB`)** | `docs/DATA_MODEL.md`, `docs/ROLES_PERMISSIONS.md`, `docs/ARCHITECTURE.md`, `docs/CODE_STYLE.md`. |
| **Mengimplementasikan pipeline NLP, DAG, atau prompt LLM (`C-NLP`)** | `research/METHODOLOGY.md`, `docs/DATA_MODEL.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`. |
| **Menjalankan eksperimen riset (`E-01`–`E-03b`) atau metrik evaluasi** | `research/EXPERIMENT_PLAN.md`, `research/EXPERIMENT_LOG.md`, `research/REPRODUCIBILITY.md`, `research/DATASET.md`. |
| **Menulis atau memperbarui dokumen spesifikasi/naskah ilmiah** | `docs/_WRITING_RULES.md`, `research/RESEARCH_BRIEF.md`, `research/AI_USAGE.md`, `research/JOURNAL_TARGET.md`. |
| **Membuat commit, branch, atau Pull Request** | `docs/GIT_WORKFLOW.md`, `docs/TESTING.md`. |

---

## 4. Sepuluh Aturan WAJIB (Mandatory Directives)

1. **WAJIB** membaca `docs/PROGRESS.md` atau `research/RESEARCH_PROGRESS.md` pada awal sesi untuk mengetahui fase aktif dan langkah berikutnya.
2. **WAJIB** membaca hanya file dokumentasi yang relevan sesuai Tabel Bagian 3 sebelum memulai implementasi.
3. **WAJIB** menghindari pembacaan ulang file yang sudah dibaca di dalam percakapan yang sama kecuali file tersebut telah dimodifikasi.
4. **WAJIB** bekerja pada branch terpisah berformat `ai/<tipe>/<id>-<slug>` dan menggunakan format *Conventional Commits* (`→ docs/GIT_WORKFLOW.md#1-strategi-branching-dan-pola-penamaan-branch`).
5. **WAJIB** menegakkan kontrak skema `grounded_refs` (`>= 1` ID valid), batas kata (`300..2500`), dan graf DAG asiklik (`source_id != target_id`) sesuai `→ docs/DATA_MODEL.md#4-aturan-validasi-lintas-field-dan-indeks-database`.
6. **WAJIB** menerapkan filter scope otorisasi server (`OWN`, `ORG`, `BLIND`) pada setiap query database sesuai `→ docs/ROLES_PERMISSIONS.md#3-aturan-scope-data-data-isolation-rules`.
7. **WAJIB** menggunakan variabel CSS dari `tokens.css` dan mematuhi kontras WCAG 2.1 AA serta responsivitas `375px`/`768px`/`1440px` (`→ docs/DESIGN_SYSTEM.md`).
8. **WAJIB** menjalankan sendiri verifikasi `lint`, `typecheck`, `build`, dan `test` serta melaporkan output aktualnya sebelum mengklaim tugas selesai (`→ docs/TESTING.md#5-aturan-wajib-bagi-agen-ai-dan-pengembang-verification-rules`).
9. **WAJIB** mencatat setiap eksekusi eksperimen (sukses maupun gagal) secara *append-only* tanpa pembulatan ke `→ research/EXPERIMENT_LOG.md` dan penggunaan AI ke `→ research/AI_USAGE.md`.
10. **WAJIB** memperbarui status checklist dan log satu baris pada `docs/PROGRESS.md` (atau `research/RESEARCH_PROGRESS.md`) setiap kali selesai mengerjakan satu tugas.

---

## 5. Sepuluh LARANGAN Keras (Strict Prohibitions)

1. **JANGAN** menginstal atau menggunakan library di luar daftar resmi `→ docs/ARCHITECTURE.md#4-daftar-library-utama-dan-alternatif-yang-ditolak` tanpa persetujuan tertulis dan ADR baru di `docs/DECISIONS.md`.
2. **JANGAN** mengubah file konfigurasi inti (`tsconfig.json`, `eslint.config.mjs`, `pyproject.toml`, `.github/workflows/`, `docs/_WRITING_RULES.md`) tanpa izin eksplisit pengguna.
3. **JANGAN** mengubah, menimpa, atau menghapus berkas apa pun di dalam direktori `research/data/raw/` (`→ research/DATASET.md`).
4. **JANGAN** mengarang data eksperimen, membulatkan angka metrik mentah, atau mengarang sitasi/DOI yang belum terverifikasi di `references.bib` (`→ research/AI_USAGE.md#2-daftar-larangan-keras-bagi-agen-ai-strictly-prohibited-actions`).
5. **JANGAN** melakukan `git push` langsung ke branch `main` atau menggunakan `--force` (`→ docs/GIT_WORKFLOW.md#5-aturan-perubahan-oleh-agen-ai-ai-agent-governance`).
6. **JANGAN** menghapus, men-skip (`.skip`), atau melemahkan assertion pada tes yang gagal agar terlihat lulus (`→ docs/TESTING.md#5-aturan-wajib-bagi-agen-ai-dan-pengembang-verification-rules`).
7. **JANGAN** menggunakan tipe `any` di TypeScript atau fungsi tanpa anotasi tipe di Python (`→ docs/CODE_STYLE.md#2-konfigurasi-kunci-formatter-linter-dan-type-checker`).
8. **JANGAN** menyimpan token JWT di `localStorage`/`sessionStorage` atau mencatat PII dan `clean_text` ke dalam log aplikasi (`→ docs/CODE_STYLE.md#5-penanganan-error-dan-standar-logging-terstruktur`).
9. **JANGAN** mengirimkan dokumen pengguna/mahasiswa ke API LLM pihak ketiga tanpa kebijakan *zero data retention* atau sebelum melewati `pii_redaction` (`→ research/ETHICS.md`).
10. **JANGAN** menghapus entri lama pada dokumen berstatus *append-only* (`DECISIONS.md`, `EXPERIMENT_LOG.md`, `AI_USAGE.md`, dan log audit).

---

## 6. Rujukan *Definition of Done* (DoD)

Suatu tugas **HANYA** boleh ditandai `done` jika telah lulus seluruh **8 langkah berurutan *Definition of Done*** yang ditetapkan di `→ docs/TESTING.md#3-checklist-definition-of-done-dod-berurutan`.
