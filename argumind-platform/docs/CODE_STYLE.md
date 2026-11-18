Tujuan: Menetapkan konvensi penamaan, konfigurasi kunci linter/type-checker, batas ukuran dan pola komponen, urutan import, standar logging/error, aturan komentar, serta daftar anti-pattern terlarang untuk kode TypeScript (`C-WEB`) dan Python (`C-API`, `C-NLP`).
Status dan tanggal: Draft v1.0 | 2026-11-18
Sumber kebenaran untuk: Konvensi penulisan kode lintas monorepo `argumind-platform/` dan aturan review pull request.

# Standar & Gaya Kode (Code Style): Argumind Platform

---

## 1. Tabel Konvensi Penamaan (Naming Conventions)

| Objek Kode | Bahasa / Lingkup | Konvensi Eksplisit | Contoh Benar (`WAJIB`) | Contoh Salah (`JANGAN`) |
|---|---|---|---|---|
| **File Komponen React** | TypeScript (`apps/web`) | `PascalCase.tsx` | `ArgumentGraphCanvas.tsx`, `RubricScoreAccordion.tsx` | `argumentGraphCanvas.tsx`, `rubric-score.tsx` |
| **File Hook & Utilitas TS** | TypeScript (`apps/web`) | `camelCase.ts` (Hook wajib diawali `use`) | `useArgumentStream.ts`, `formatSpanOffset.ts` | `UseArgumentStream.ts`, `format_span.ts` |
| **File Route Next.js** | Next.js App Router | `kebab-case` folder + nama cadangan Next.js | `app/documents/[docId]/versions/[ver]/workspace/page.tsx` | `app/Documents/WorkspacePage.tsx` |
| **File Modul Python** | Python (`apps/api`, `nlp-worker`) | `snake_case.py` | `dag_decoder.py`, `pii_redactor.py`, `rubric_validator.py` | `DagDecoder.py`, `pii-redactor.py` |
| **Komponen & Tipe / Interface / Class** | TS & Python (`Pydantic` / `SQLAlchemy`) | `PascalCase` (tanpa awalan `I` pada interface) | `interface ArgumentNode`, `class RubricScoreCreate` | `interface IArgumentNode`, `class rubric_score_create` |
| **Variabel & Fungsi (TS)** | TypeScript | `camelCase` (boolean wajib awalan `is`, `has`, `can`, `should`) | `const isBlindMode = true;`, `function scrollToSpan()` | `const blind_mode = true;`, `function ScrollToSpan()` |
| **Variabel & Fungsi (Python)** | Python | `snake_case` | `def compute_macro_f1():`, `grounded_refs_count = 2` | `def computeMacroF1():`, `GroundedRefsCount = 2` |
| **Konstanta Global & Enum Key** | TS & Python | `UPPER_SNAKE_CASE` | `MAX_WORD_COUNT = 2500`, `MIN_WORD_COUNT = 300` | `maxWordCount = 2500`, `Min_Word_Count = 300` |
| **Tabel & Kolom Database** | PostgreSQL (`→ docs/DATA_MODEL.md`) | Tabel: `plural_snake_case`; Kolom: `singular_snake_case` | `argument_nodes.start_char`, `rubric_scores.ai_score` | `ArgumentNode.startChar`, `rubricScores.AIScore` |

---

## 2. Konfigurasi Kunci Formatter, Linter, dan Type-Checker

Aturan pemformatan spasi, titik koma, dan kutip ditegakkan otomatis oleh alat di bawah ini (JANGAN didebatkan manual di PR; rujuk langsung file konfigurasinya):

| Alat | File Konfigurasi Acuan | Nilai Kunci Wajib (Non-Negotiable) |
|---|---|---|
| **TypeScript (`tsc`)** | `apps/web/tsconfig.json`, `packages/shared-schemas/tsconfig.json` | `"strict": true`, `"noUncheckedIndexedAccess": true`, `"exactOptionalPropertyTypes": true`, `"noImplicitOverride": true`. Penggunaan tipe `any` dilarang keras (`@typescript-eslint/no-explicit-any: "error"`). |
| **ESLint + Prettier** | `apps/web/eslint.config.mjs`, `.prettierrc` | Mengaktifkan `eslint-plugin-jsx-a11y` (aturan aksesibilitas WCAG AA sebagai `error`) dan `@tanstack/eslint-plugin-query`. |
| **Ruff (Linter & Formatter Python)** | `pyproject.toml` (`[tool.ruff]`) | `line-length = 100`, `target-version = "py312"`, aturan aktif: `E`, `F`, `I` (isort), `B` (bugbear), `UP` (pyupgrade), `S` (bandit security), `ASYNC` (aturan async FastAPI). |
| **Mypy (Static Typing Python)** | `pyproject.toml` (`[tool.mypy]`) | `strict = true`, `disallow_untyped_defs = true`, `plugins = ["pydantic.mypy", "sqlalchemy.ext.mypy.plugin"]`. Seluruh fungsi Python WAJIB memiliki anotasi tipe argumen dan nilai kembalian (`-> ReturnType`). |

---

## 3. Pola Komponen, Batas Ukuran, Props, dan Hooks

1. **Batas Ukuran File dan Fungsi:**
   - Satu file komponen `.tsx` atau modul `.py` WAJIB $\le 200$ baris kode bersih (di luar blok import). Jika melewati `200` baris, pecah sub-komponen atau fungsi bantu ke file terpisah.
   - Satu fungsi atau komponen React WAJIB $\le 50$ baris dengan kompleksitas siklomatik $\le 10$.
2. **Pemisahan UI dan Logika Bisnis:**
   - Komponen presentasi di `apps/web/src/components/` hanya menerima data lewat `props` dan memanggil callback; JANGAN memanggil `fetch` atau menghitung logika graf di dalam komponen render.
   - Orkestrasi `SSE` (`useArgumentStream`), sinkronisasi `Zustand`, dan mutasi `TanStack Query` WAJIB diisolasi di dalam `apps/web/src/hooks/`.
3. **Aturan Props dan Hooks:**
   - Maksimal `6` props per komponen (jika lebih, kelompokkan ke dalam objek domain terketik atau gunakan *compound components*).
   - Gunakan *named export* (`export function ArgumentNodeCard(...)`), kecuali untuk file rute wajib Next.js (`page.tsx`, `layout.tsx`) yang mengharuskan `export default`.

```tsx
// Contoh minimal pola komponen bersih:
export interface NodeBadgeProps {
  readonly nodeKey: string;
  readonly nodeType: NodeType;
}
export function NodeBadge({ nodeKey, nodeType }: NodeBadgeProps): React.JSX.Element {
  return <span data-node-key={nodeKey}>{ `${nodeType} • ${nodeKey}` }</span>;
}
```

---

## 4. Aturan dan Urutan Import

Urutan grup import WAJIB dipisahkan dengan 1 baris kosong (ditegakkan oleh `eslint-plugin-import` / `ruff I`):
1. **Grup 1:** Pustaka bawaan runtime (`node:*` di TS; `from __future__ import annotations`, `typing`, `uuid`, `pathlib` di Python).
2. **Grup 2:** Pustaka pihak ketiga (`react`, `next/*`, `@xyflow/react`, `fastapi`, `pydantic`, `torch`).
3. **Grup 3:** Paket internal monorepo (`@argumind/shared-schemas`, `@argumind/evaluation-metrics`).
4. **Grup 4:** Modul internal aplikasi dengan alias path absolut (`@/components/...`, `apps.api.src...`). JANGAN menggunakan relative path bertingkat lebih dari satu level (`../../`).
5. **Grup 5 (Khusus TS):** Import khusus tipe (`import type { ... }`).

---

## 5. Penanganan Error dan Standar Logging Terstruktur

### A. Penanganan Error
- Semua error bisnis di `C-API` dan `C-NLP` WAJIB mewarisi class dasar `ArgumindDomainError(status_code: int, code: str, detail: str)` yang otomatis diterjemahkan middleware menjadi respons JSON `RFC 9457 Problem Details` (`→ docs/DATA_MODEL.md#5a-konvensi-standar-pagination-filter-sorting-dan-error`).
- Di `C-WEB`, kegagalan fetch/mutasi WAJIB ditangkap oleh `ErrorBoundary` atau `onError` `TanStack Query` untuk menampilkan `Toast` persisten dengan `trace_id`.

### B. Level dan Format Logging (`structlog` / `pino`)
Seluruh log di `staging` dan `prod` WAJIB berformat **JSON satu baris** dengan field wajib: `timestamp`, `level`, `service` (`c-web | c-api | c-nlp`), `trace_id`, `event`, dan `duration_ms`.
- **`DEBUG`:** Detail offset tokenisasi dan distribusi probabilitas NLI (aktif hanya di `dev`).
- **`INFO`:** Siklus hidup request HTTP (`2xx`), transisi tahap `SSE` (`stage_1` $\rightarrow$ `stage_3`), dan pencatatan audit.
- **`WARN`:** *Retry* otomatis saat LLM gagal validasi skema `grounded_refs` (`percobaan 1..2`), atau pemakaian kuota organisasi mencapai `>= 80%`.
- **`ERROR`:** Kegagalan permanen (`HTTP 422 ERR_UNFAITHFUL_SCORE` pasca-retry, `HTTP 504 ERR_LLM_TIMEOUT`).
- **`CRITICAL`:** Kegagalan koneksi `C-DB`/`C-CACHE` atau ketidakcocokan checksum `manifest.sha256`.
- **Aturan Privasi Log:** **JANGAN PERNAH** mencatat isi teks esai (`clean_text`), password, JWT, atau `users.email`/`full_name` ke dalam log; catat hanya `doc_id`, `run_id`, dan `user_id (UUID)`.

---

## 6. Aturan Penulisan Komentar

- **JANGAN** menulis komentar yang mengulang nama fungsi/variabel (mis. `// set selected node id`).
- Komentar (`JSDoc` / Python `Docstring`) **WAJIB** ditulis hanya pada 3 kondisi:
  1. Menjelaskan rumus metrik evaluasi dan rujukan bagian dokumen (mis. `# Rumus QWK sesuai research/METHODOLOGY.md#6B.4`).
  2. Menjelaskan invariant algoritma graf atau batasan indeks karakter `start_char..end_char`.
  3. Menjelaskan alasan keamanan/etik (mis. alasan filter scope `[BLIND]` pada `F-06`).

---

## 7. Daftar Anti-Pattern yang Dilarang Keras

1. **Dilarang menggunakan `any` atau menonaktifkan validasi skema output LLM:**
```ts
// SALAH: Mem-parsing output LLM tanpa validasi kontrak Zod/Pydantic
const data: any = JSON.parse(rawLlmText);
// BENAR: Wajib validasi skema ketat
const data = RubricScoreSchema.parse(JSON.parse(rawLlmText));
```

2. **Dilarang menyimpan token autentikasi di `localStorage` / `sessionStorage` (`→ docs/ROLES_PERMISSIONS.md`):**
```ts
// SALAH: Rentan pencurian via XSS
localStorage.setItem("access_token", jwtString);
// BENAR: Biarkan browser mengirim cookie HttpOnly secara otomatis
fetch("/api/v1/documents", { credentials: "include" });
```

3. **Dilarang membuat query database pada `documents` / `analysis_runs` tanpa filter scope peran:**
```python
# SALAH: Celah IDOR & kebocoran blind annotation (tanpa filter pemilik/organisasi)
stmt = select(Document).where(Document.id == doc_id)
# BENAR: Wajib terapkan filter scope dari policies.py
stmt = apply_read_scope(select(Document).where(Document.id == doc_id), current_user)
```

4. **Dilarang menggunakan nilai warna hex mentah (*hardcoded hex*) di luar `tokens.css` (`→ docs/DESIGN_SYSTEM.md`):**
```tsx
// SALAH: Hardcode hex merusak konsistensi tema Light/Dark
<div style={{ borderColor: "#0284C7", backgroundColor: "#FFFFFF" }} />
// BENAR: Gunakan CSS variable dari DESIGN_SYSTEM.md
<div style={{ borderColor: "var(--node-claim-border)", backgroundColor: "var(--color-surface)" }} />
```

5. **Dilarang memanggil operasi I/O sinkron (blocking) di dalam fungsi `async def` FastAPI:**
```python
# SALAH: Memblokir event loop Uvicorn secara keseluruhan
async def call_llm(): return requests.post(url, json=payload)
# BENAR: Gunakan klien async (httpx.AsyncClient)
async def call_llm(client: httpx.AsyncClient): return await client.post(url, json=payload)
```

6. **Dilarang menelan exception secara diam-diam (`bare except / empty catch`):**
```python
# SALAH: Menyembunyikan kegagalan validasi graf
try: validate_dag_acyclic(edges)
except Exception: pass
```

---

## 8. Pertanyaan Terbuka

1. `TODO(Q-STYLE-01 — Package Manager Monorepo)`: Apakah pengelolaan workspace TypeScript di `argumind-platform/` akan menggunakan `pnpm` (`pnpm-workspace.yaml`) dan Python menggunakan `uv` (`uv.lock`)?
