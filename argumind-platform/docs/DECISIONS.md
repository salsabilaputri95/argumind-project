Tujuan: Mencatat seluruh Keputusan Arsitektur dan Metodologi Penelitian (*Architecture & Research Decision Records* / ADR) secara *append-only* untuk proyek Argumind.
Status dan tanggal: Draft v1.0 | 2026-11-18
Sumber kebenaran untuk: Rasional pemilihan tumpukan teknologi (`ADR-01`–`ADR-04`) dan keputusan metodologi riset (`ADR-05`–`ADR-06`).

# Catatan Keputusan Arsitektur & Metodologi (Decisions / ADR): Argumind

> **Aturan Append-Only:** Dokumen ini bersifat **append-only**. **JANGAN** menghapus atau menimpa ADR lama; jika sebuah keputusan berubah, ubah status ADR lama menjadi `Digantikan oleh ADR-xx` dan tambahkan entri `ADR-xx` baru di bagian bawah.

## 1. Indeks Keputusan (ADR Index)

| ID ADR | Judul Keputusan | Kategori | Tanggal | Status Saat Ini |
|---|---|---|---|---|
| **`ADR-01`** | Pemisahan Monorepo Next.js 15 (`C-WEB`) dan Python FastAPI + PyTorch (`C-API` / `C-NLP`) | Arsitektur Stack | 2026-11-18 | `Diusulkan` (Menunggu Pengesahan) |
| **`ADR-02`** | Autentikasi JWT (`RS256`) di Cookie `HttpOnly` + Rotasi Refresh Token di Redis | Keamanan & Auth | 2026-11-18 | `Diusulkan` (Menunggu Pengesahan) |
| **`ADR-03`** | Kombinasi `TanStack Query` + `Zustand` + `@xyflow/react` (`elkjs`) untuk Kanvas Graf | State & UI Graf | 2026-11-18 | `Diusulkan` (Menunggu Pengesahan) |
| **`ADR-04`** | Komunikasi Progres Analisis 3 Tahap Menggunakan *Server-Sent Events* (`SSE`) | Alur Data & Latensi | 2026-11-18 | `Diusulkan` (Menunggu Pengesahan) |
| **`ADR-05`** | Pipeline Hibrida (`IndoBERT` + *Minimum Spanning DAG* + *JSON-Constrained LLM*) | Metodologi Riset (`RQ1`, `RQ2`) | 2026-11-18 | `Diterima` (`→ research/METHODOLOGY.md`) |
| **`ADR-06`** | Penjangkaran Wajib `grounded_refs` dan Pemisahan Evaluasi *Oracle* vs *End-to-End* | Metodologi Riset (`RQ2`, `RQ3`) | 2026-11-18 | `Diterima` (`→ research/METHODOLOGY.md`) |

---

## 2. Rincian Keputusan (Maks $\le 15$ Baris per ADR)

### `ADR-01` — Pemisahan Monorepo Next.js 15 (`C-WEB`) dan Python FastAPI + PyTorch (`C-API` / `C-NLP`)
- **Tanggal & Status:** `2026-11-18` | Status: `Diusulkan` (`→ docs/ARCHITECTURE.md#2-komponen-sistem-dan-diagram-komponen`)
- **Konteks:** Platform membutuhkan antarmuka web interaktif untuk visualisasi graf dan anotasi (`F-02`, `F-06`) sekaligus mengeksekusi model `IndoBERT`, `NetworkX` DAG, dan evaluasi metrik riset Python (`F-01`–`F-05`).
| Opsi | Kelebihan | Kekurangan |
|---|---|---|
| **A. Next.js 15 (TS) + FastAPI/PyTorch (Python) dalam Monorepo** | Ekosistem UI React terbaik + akses langsung ke `PyTorch`/`Transformers`/`NetworkX` tanpa jembatan bahasa yang rapuh. | Membutuhkan sinkronisasi skema tipe antara TypeScript dan Python (`packages/shared-schemas`). |
| **B. Fullstack Next.js (Node.js Backend) saja** | Satu bahasa pemrograman (`TypeScript`). | Tidak dapat menjalankan pelatihan/inferensi `IndoBERT` + `BiLSTM-CRF` dan skrip metrik riset secara native. |
| **C. Monolitik Python (Django/Jinja + HTMX)** | Deployment backend tunggal. | Sulit membangun kanvas graf interaktif $\ge 55\text{ fps}$ dan sorotan span dua arah $\le 100\text{ ms}$. |
- **Keputusan:** Memilih **Opsi A** dengan menempatkan `C-WEB` (Next.js 15) dan `C-API`/`C-NLP` (FastAPI + PyTorch) dalam satu monorepo dengan kontrak OpenAPI/JSON Schema bersama.
- **Konsekuensi:** Tim wajib menjaga konsistensi skema antara `zod` dan `pydantic` melalui pipeline CI; layanan `C-NLP` dapat diskalakan terpisah pada node GPU.

### `ADR-02` — Autentikasi JWT (`RS256`) di Cookie `HttpOnly` + Rotasi Refresh Token di Redis
- **Tanggal & Status:** `2026-11-18` | Status: `Diusulkan` (`→ docs/ROLES_PERMISSIONS.md#4-spesifikasi-autentikasi--manajemen-sesi`)
- **Konteks:** Sistem menangani esai akademik ber-PII dan sesi anotasi *double-blind* lintas peran (`author`, `reviewer`, `annotator`, `org_admin`) yang rentan jika token dicuri lewat XSS.
| Opsi | Kelebihan | Kekurangan |
|---|---|---|
| **A. JWT `RS256` di Cookie `HttpOnly; Secure; SameSite=Lax` + Redis Refresh Rotation** | Kebal terhadap pembacaan token via XSS JavaScript; pencabutan sesi instan saat terdeteksi pemakaian ulang token. | Memerlukan validasi header `X-CSRF-Token` pada setiap endpoint mutasi. |
| **B. Penyimpanan Bearer JWT di `localStorage`** | Implementasi header klien sederhana tanpa CSRF token. | Rentan terhadap pencurian token penuh jika terjadi celah XSS pada dependensi UI. |
- **Keputusan:** Memilih **Opsi A** dengan `access_token` berumur `15 menit`, `refresh_token` `7 hari` terotasi di Redis, dan kewajiban MFA `TOTP` bagi `org_admin`.
- **Konsekuensi:** `C-API` dan `C-WEB` wajib menerapkan middleware CSRF dan *reuse detection* pada endpoint `/api/v1/auth/refresh`.

### `ADR-03` — Kombinasi `TanStack Query` + `Zustand` + `@xyflow/react` (`elkjs`) untuk Kanvas Graf
- **Tanggal & Status:** `2026-11-18` | Status: `Diusulkan` (`→ docs/ARCHITECTURE.md#4-daftar-library-utama-dan-alternatif-yang-ditolak`)
- **Konteks:** Halaman `P-03` harus merender hingga `100` node komponen argumen dengan kartu HTML interaktif dan menyinkronkan klik node ke posisi scroll teks dalam $\le 100\text{ ms}$ (`INP <= 100ms`).
| Opsi | Kelebihan | Kekurangan |
|---|---|---|
| **A. `@xyflow/react` + `elkjs` + `TanStack Query` (Server) + `Zustand` (UI)** | Node berupa komponen React utuh; tata letak pohon hierarkis deterministik; sorotan span teks tidak memicu *re-render* global. | Ukuran bundle `@xyflow/react` cukup besar sehingga wajib dimuat dengan `dynamic import`. |
| **B. `Cytoscape.js` / `D3-force` + `React Context`** | Ringan untuk ribuan titik sederhana. | Sulit menanamkan tombol aksi/badge aksesibel di dalam node; `React Context` menyebabkan *lag* saat *pan/zoom*. |
- **Keputusan:** Memilih **Opsi A** untuk memisahkan *server cache* (`TanStack Query`) dari *high-frequency UI state* (`Zustand`) di atas kanvas `@xyflow/react`.
- **Konsekuensi:** Komponen kanvas wajib di-lazy-load ($\le 120\text{ KB}$ gzipped) dan otomatis beralih ke tampilan kartu vertikal pada layar `< 768px`.

### `ADR-04` — Komunikasi Progres Analisis 3 Tahap Menggunakan *Server-Sent Events* (`SSE`)
- **Tanggal & Status:** `2026-11-18` | Status: `Diusulkan` (`→ docs/ARCHITECTURE.md#5b-jalur-mutasi--analisis-bertahap-progressive-pipeline-f-01f-04`)
- **Konteks:** Analisis penuh `F-01` s.d. `F-04` membutuhkan waktu hingga `15.0 detik` (`p95`), tetapi pengguna membutuhkan umpan balik visual struktur awal dalam $\le 4.0\text{ detik}$ (`→ docs/PRD.md#7b-matriks-risiko-produk`).
| Opsi | Kelebihan | Kekurangan |
|---|---|---|
| **A. *Server-Sent Events* (`SSE`) Satu Arah dari `C-API` via Redis Pub/Sub** | Berjalan di atas HTTP standar, otomatis *reconnect*, dan mengirimkan hasil Tahap 1 ($\le 4\text{s}$), Tahap 2 ($\le 10\text{s}$), dan Tahap 3 ($\le 15\text{s}$) secara real-time. | Komunikasi satu arah (server ke klien); pemicu awal tetap memakai `POST`. |
| **B. Short Polling (`GET` setiap 2 detik)** | Sangat sederhana di sisi server. | Menambah latensi rata-rata `1–2 detik` per tahap dan membebani `C-API` dengan request berulang. |
| **C. WebSockets Dua Arah Penuh** | Mendukung komunikasi dua arah penuh. | Berlebihan (*overkill*) untuk streaming status pipeline satu arah dan rumit pada *load balancer*. |
- **Keputusan:** Memilih **Opsi A (`SSE`)** untuk menyiarkan 3 tahap hasil analisis secara progresif dari `C-NLP` ke `C-WEB`.
- **Konsekuensi:** Jika Tahap 2/3 mengalami timeout LLM (`504`), hasil Tahap 1 (`F-01` & `F-02` lokal) sudah tampil di layar dan tersimpan aman di database.

### `ADR-05` — Pipeline Hibrida (`IndoBERT` + *Minimum Spanning DAG* + *JSON-Constrained LLM*)
- **Tanggal & Status:** `2026-11-18` | Status: `Diterima` (`→ research/METHODOLOGY.md#5-arsitektur-metode-argumind-dan-analisis-statistik`)
- **Konteks:** Penggunaan *zero-shot LLM* murni mahal, lambat, sering melanggar batas indeks karakter `start_char..end_char`, dan dapat menghasilkan relasi siklus pada graf argumen Bahasa Indonesia.
| Opsi | Kelebihan | Kekurangan |
|---|---|---|
| **A. Hibrida: `IndoBERT + BiLSTM-CRF` + Cross-Encoder NLI + Chu-Liu/Edmonds DAG + Selektif LLM** | Presisi batas span karakter tinggi, bebas siklus (`cycle_rate == 0`), hemat biaya token karena LLM hanya dipanggil saat $p_{\text{neutral}} + p_{\text{contradict}} \ge 0.40$. | Arsitektur *pipeline* lebih kompleks dibandingkan pemanggilan API tunggal. |
| **B. *Zero-Shot / Few-Shot LLM* End-to-End (`B2`)** | Tanpa pelatihan model lokal. | Biaya dan latensi tinggi; batas karakter sering meleset; alasan skor tidak terikat graf. |
- **Keputusan:** Memilih **Opsi A** sebagai arsitektur inti `M1_ArgumindHybrid` dan `M2_GraphNLIConditioned` untuk menjawab `RQ1` dan `RQ2`.
- **Konsekuensi:** Eksperimen `E-01` wajib menguji ablasi tanpa dekode DAG (`M1_NoDAG`) dan tanpa *LLM refinement* (`M1_NoLLMRefine`) untuk membuktikan kontribusi tiap komponen.

### `ADR-06` — Penjangkaran Wajib `grounded_refs` dan Pemisahan Evaluasi *Oracle* vs *End-to-End*
- **Tanggal & Status:** `2026-11-18` | Status: `Diterima` (`→ research/METHODOLOGY.md#7-ancaman-validitas-threats-to-validity-dan-mitigasi`)
- **Konteks:** Penilaian kualitas argumen dengan LLM rentan terhadap *unfaithful explanation* (alasan tidak sesuai isi argumen) dan *error propagation* dari tahap ekstraksi komponen.
| Opsi | Kelebihan | Kekurangan |
|---|---|---|
| **A. Validasi Skema Wajib `grounded_refs` (`>= 1` ID) + Evaluasi Ganda (*Oracle* & *End-to-End*)** | Menjamin setiap skor dimensi menunjuk ke `node_key`/`gap_key` nyata (`HTTP 422` jika kosong) dan memisahkan error ekstraksi (`RQ1`) dari error penalaran (`RQ2`/`RQ3`). | Membutuhkan eksekusi eksperimen ganda (`E-02a` & `E-02b`, `E-03a` & `E-03b`). |
| **B. Penjelasan Teks Bebas (*Free-Text Rationale*) pada Mode *End-to-End* Saja** | Lebih sedikit skenario eksperimen. | Tidak dapat menguji *counterfactual faithfulness* (`FaithfulnessRate`) dan reviewer jurnal akan mengkritik *confounding error*. |
- **Keputusan:** Memilih **Opsi A** untuk seluruh penilaian rubrik `F-04` dan desain eksperimen `E-02`–`E-03`.
- **Konsekuensi:** Database menetapkan constraint `CHECK (jsonb_array_length(grounded_refs) >= 1)` pada tabel `rubric_scores`.

---

## 3. Pertanyaan Terbuka

1. `TODO(Q-ADR-01 — Konfirmasi Alasan & Pengesahan ADR-01 s.d. ADR-04)`: Apakah alasan pemilihan pada `ADR-01` (Next.js + FastAPI), `ADR-02` (JWT Cookie HttpOnly), `ADR-03` (React Flow + Zustand), dan `ADR-04` (SSE 3 tahap) sudah sesuai dengan preferensi tim teknis Anda untuk diubah statusnya dari `Diusulkan` menjadi `Diterima`?
