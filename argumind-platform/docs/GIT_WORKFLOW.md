Tujuan: Menetapkan strategi percabangan Git, aturan *Conventional Commits*, standar Pull Request, penandaan rilis SemVer & jurnal, pembatasan kerja agen AI, serta proteksi branch untuk monorepo Argumind.
Status dan tanggal: Draft v1.0 | 2026-11-18
Sumber kebenaran untuk: Konvensi Git, syarat penggabungan kode (*merge gates*), dan penandaan commit artefak eksperimen (`E-01`–`E-03b`).

# Alur Kerja Git (Git Workflow): Argumind Platform & Research

## 1. Strategi Branching dan Pola Penamaan Branch

- **Diagram Satu Baris (Trunk-Based Development):**
  `feature/fix/ai branch (berumur <= 3 hari)` $\xrightarrow{\text{PR + CI Gate + Squash Merge}}$ `main (selalu siap deploy)` $\xrightarrow{\text{Git Tag SemVer}}$ `staging / prod & Arsip Jurnal`
- **Format Nama Branch Wajib:** `<tipe>/<id-fitur-atau-isu>-<deskripsi-kebab-case>` (khusus agen AI wajib diawali `ai/<tipe>/...`).

| Tipe Branch | Tujuan Penggunaan | Contoh Benar (`WAJIB`) | Contoh Salah (`JANGAN`) |
|---|---|---|---|
| `feat` | Implementasi fitur baru (`F-01`–`F-07`). | `feat/F-02-argument-graph-canvas` | `feature/GraphCanvas`, `f02` |
| `fix` | Perbaikan bug pada kode aplikasi atau skrip. | `fix/F-04-empty-grounded-refs-check` | `bugfix/fix-score`, `hotfix1` |
| `docs` | Pembuatan/pembaruan spesifikasi `docs/` atau `research/`. | `docs/ADR-05-hybrid-pipeline-spec` | `update-docs` |
| `chore` | Pembaruan dependensi, skrip CI, atau konfigurasi build. | `chore/ci-playwright-axe-gate` | `misc-changes` |
| `exp` | Implementasi runner eksperimen riset (`E-01`–`E-03b`). | `exp/E-01-indobert-dag-ablation` | `test-model` |

---

## 2. Standar *Conventional Commits*

- **Format Wajib:** `<tipe>(<scope>): <deskripsi imperatif singkat <= 72 karakter> [opsional: (#ID)]`
- **Tipe yang Diizinkan:** `feat`, `fix`, `docs`, `refactor`, `test`, `perf`, `chore`, `ci`.
- **Daftar Scope Resmi Monorepo:** `web` (`C-WEB`), `api` (`C-API`), `nlp` (`C-NLP`), `schemas` (`packages/shared-schemas`), `metrics` (`packages/evaluation-metrics`), `db` (`infra/migrations`), `research` (`research/`), `docs` (`docs/`), `ci`.
- **Contoh Benar (`WAJIB`):**
  - `feat(nlp): enforce chu-liu-edmonds acyclic decoding on support edges (F-02)`
  - `fix(api): reject rubric score payload with empty grounded_refs (F-04)`
- **Contoh Salah (`JANGAN`):**
  - `update code` *(tanpa tipe, scope, dan deskripsi spesifik)*
  - `Feat(Web): Added Graph Component.` *(huruf kapital pada tipe/scope, bentuk lampau, diakhiri titik)*

---

## 3. Standar Pull Request (PR) dan Strategi Merge

1. **Batas Ukuran PR:** Maksimal **`<= 400` baris berubah** (penambahan + penghapusan, di luar `lockfile` dan migrasi otomatis). Jika fitur melebihi `400` baris, pecah menjadi beberapa PR bertahap (mis. PR skema DB $\rightarrow$ PR endpoint API $\rightarrow$ PR komponen UI).
2. **Syarat Merge Wajib (*Merge Gates*):**
   - Minimal **`1` persetujuan (*approval*)** dari manusia untuk PR kode standar; minimal **`2` persetujuan** untuk perubahan `infra/migrations/`, `auth/`, atau metrik riset (`packages/evaluation-metrics`).
   - Seluruh tahapan CI (`lint`, `typecheck`, `build`, `unit/integration/e2e test`, dan ambang coverage `→ docs/TESTING.md#2-perintah-eksekusi-dan-target-cakupan-coverage-per-lapisan`) berstatus **LULUS (Hijau)**.
   - `0` konflik merge terhadap `HEAD` terbaru dari `main` (`git rebase origin/main`) dan seluruh diskusi review telah berstatus `Resolved`.
3. **Strategi Merge:** WAJIB menggunakan **`Squash and Merge`** ke `main` agar setiap PR menghasilkan tepat 1 commit atomik yang bersih di riwayat `main` (commit merge berantakan dilarang).

### Template Checklist PR (`.github/pull_request_template.md`)
```markdown
- [ ] Merujuk ID Fitur / Eksperimen / ADR terkait: `F-xx` / `E-xx` / `ADR-xx`
- [ ] Lulus DoD 8 langkah di `docs/TESTING.md` (lint, typecheck, build, test coverage, 375/768/1440px, WCAG AA)
- [ ] Tidak membocorkan PII, secret, atau mengubah isi `research/data/raw/`
- [ ] `docs/PROGRESS.md` atau `research/RESEARCH_PROGRESS.md` telah diperbarui
```

---

## 4. Penandaan Rilis (SemVer & Artefak Jurnal Ilmiah)

- **Skema Versi (`SemVer 2.0.0`):** `vMAJOR.MINOR.PATCH` (mis. `v0.1.0` untuk Fase 1 anotasi, `v1.0.0` untuk rilis MVP penuh).
  - `MAJOR`: Perubahan tidak kompatibel pada kontrak API atau skema korpus.
  - `MINOR`: Penambahan fitur baru (`F-01`–`F-07`) yang kompatibel ke belakang.
  - `PATCH`: Perbaikan bug tanpa mengubah kontrak skema.
- **Tag Khusus Reprodusibilitas Jurnal:** Saat membekukan hasil eksperimen `E-01`–`E-03b` untuk naskah publikasi, Peneliti Utama WAJIB membuat *signed annotated tag*:
  - `git tag -s v1.0.0-paper-submission -m "Frozen code & evaluation metrics for journal submission"`
  - Commit hash dari tag ini WAJIB sama dengan yang tercatat di `EXPERIMENT_LOG.md` dan `REPRODUCIBILITY.md`.

---

## 5. Aturan Perubahan oleh Agen AI (`AI-Agent Governance`)

Setiap agen pengodean otomatis WAJIB mematuhi 5 batasan berikut:
1. **Branch Terpisah:** Agen WAJIB bekerja di branch berawalan `ai/<tipe>/<id>-<slug>` (mis. `ai/feat/F-01-word-count-validator`).
2. **Dilarang Push ke `main`:** Agen **JANGAN PERNAH** melakukan `git push` langsung ke `main` atau menggunakan `--force` pada branch bersama.
3. **Commit Kecil & Teruji:** Buat commit per unit logis yang sudah lulus `lint` dan `test` lokal; JANGAN menggabungkan perubahan dari dua fitur berbeda dalam satu commit.
4. **Pelabelan Transparan:** Setiap commit oleh agen WAJIB menyertakan trailer `Co-Authored-By: AI-Agent <noreply@argumind.id>` dan PR wajib diberi label **`ai-assisted`**.
5. **Larangan Mengubah Konfigurasi Inti Tanpa Izin:** Agen **JANGAN** mengubah aturan di `tsconfig.json`, `eslint.config.mjs`, `pyproject.toml`, `.github/workflows/`, atau `docs/_WRITING_RULES.md` tanpa instruksi eksplisit dari pengguna manusia.

---

## 6. Aturan Proteksi Branch dan Tag (`Repository Rulesets`)

- **Branch `main`:** Wajib mengaktifkan *Require pull request before merging*, *Require status checks to pass*, *Require linear history*, *Block force pushes*, dan *Restrict deletions*.
- **Tag `v*-paper-*` dan `corpus-v*`:** Dikunci sebagai *Immutable Tags* (tidak dapat dihapus atau dipindahkan ke commit lain oleh siapa pun setelah dipublikasikan).

---

## 7. Pertanyaan Terbuka

1. `TODO(Q-GIT-01 — Platform Hosting Git & CI)`: Apakah repositori utama akan di-host di **GitHub** (menggunakan GitHub Actions) atau **GitLab Self-Hosted** institusi (menggunakan GitLab CI)?
