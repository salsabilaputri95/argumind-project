Tujuan: Menetapkan batas tugas yang diizinkan dan dilarang bagi agen AI, matriks verifikasi manusia, buku log audit penggunaan AI, serta templat deklarasi resmi sesuai kebijakan penerbit jurnal (`TACL` dan `IP&M`).
Status dan tanggal: Draft v1.0 | 2026-11-18
Sumber kebenaran untuk: Tata kelola penggunaan *Generative AI / Coding Agent* selama siklus penelitian dan penulisan naskah Argumind.

# Tata Kelola & Log Penggunaan AI (AI Usage Policy & Log): Argumind Research

---

## 1. Tabel Tugas yang Boleh Dikerjakan Agen AI (Permitted Tasks)

Penggunaan agen AI diizinkan **HANYA** sebagai asisten pendamping di bawah pengawasan peneliti manusia untuk 5 kategori tugas berikut:

| Kategori Tugas | Cakupan yang Diizinkan (`WAJIB` Mengikuti Syarat) | Syarat & Kendala Operasional | Contoh Konkret |
|---|---|---|---|
| **1. Ringkas Paper (*Literature Summarization*)** | Meringkas PDF/abstrak artikel ilmiah yang **sudah diunggah atau diverifikasi DOI-nya** oleh peneliti manusia ke dalam tabel perbandingan (`→ research/LITERATURE_REVIEW.md`). | Agen WAJIB menyalin DOI dan angka metrik hanya dari teks sumber; jika informasi tidak tersedia di teks, agen WAJIB menulis `TODO(...)`. | Mengekstrak kolom metode dan keterbatasan dari PDF `[stab2017parsing]`. |
| **2. Penyusunan Draf Kerangka (*Drafting*)** | Menyusun draf awal spesifikasi (`docs/*.md`, `research/*.md`) dan kerangka bagian metodologi/eksperimen berdasarkan poin-poin arahan peneliti. | Seluruh klaim kontribusi (`C-01`–`C-04`) dan interpretasi hasil WAJIB ditandai sebagai kandidat/«dugaan» hingga disahkan peneliti manusia. | Menyusun draf struktur `research/METHODOLOGY.md` dan `research/EXPERIMENT_PLAN.md`. |
| **3. Penulisan Kode & Skrip (*Code Generation*)** | Menulis kode aplikasi (`apps/`), paket metrik (`packages/evaluation-metrics`), skrip runner eksperimen (`research/runners/`), dan unit/E2E test (`→ docs/GIT_WORKFLOW.md#5-aturan-perubahan-oleh-agen-ai-ai-agent-governance`). | Wajib bekerja di branch `ai/<tipe>/...`, lulus seluruh DoD 8 langkah (`→ docs/TESTING.md`), dan menyertakan label `ai-assisted`. | Mengimplementasikan dekode Chu-Liu/Edmonds DAG dan unit test `QWK`. |
| **4. Perbaikan Bahasa (*Language Editing*)** | Memperbaiki tata bahasa, kejelasan kalimat akademik bahasa Inggris/Indonesia, dan keringkasan paragraf pada draf yang sudah ditulis manusia. | JANGAN mengubah makna substantif, nilai p-value, atau menggeser arah hipotesis `H1`–`H3b`. | Memoles tata bahasa Inggris pada bagian `Introduction` agar sesuai gaya `TACL`. |
| **5. Pemformatan Teknis (*Formatting*)** | Mengonversi tabel hasil dari `summary_tables.json` ke tabel LaTeX (`booktabs`), merapikan format BibTeX di `references.bib`, dan memeriksa kepatuhan template (`tacl2021v1.sty` / `elsarticle.cls`). | Angka di dalam tabel LaTeX WAJIB identik karakter-demi-karakter dengan output skrip agregasi. | Mengonversi JSON hasil `E-01` menjadi blok `\begin{table}...\end{table}`. |

---

## 2. Daftar Larangan Keras bagi Agen AI (Strictly Prohibited Actions)

Agen AI **DILARANG KERAS (`JANGAN PERNAH`)** melakukan 4 tindakan berikut dalam kondisi apa pun:

1. **Dilarang Mengarang Data, Hasil Eksperimen, atau Sitasi (*No Fabrication/Hallucination*):**
   - **JANGAN** membuat data esai sintetis yang diklaim sebagai esai manusia asli, **JANGAN** mengarang atau membulatkan angka di `EXPERIMENT_LOG.md`, dan **JANGAN** menulis referensi/DOI dari ingatan model tanpa verifikasi sumber resmi (`→ research/LITERATURE_REVIEW.md`).
2. **Dilarang Menulis Kesimpulan Akhir atau Klaim Ilmiah Tanpa Persetujuan Manusia:**
   - **JANGAN** menyatakan hipotesis `H1`–`H3b` terbukti atau menulis kesimpulan ilmiah final tanpa pemeriksaan statistik dan persetujuan tertulis dari Peneliti Utama. Setiap simpulan awal dari agen WAJIB diberi label **`«dugaan»`** (`→ research/EXPERIMENT_LOG.md`).
3. **Dilarang Mengubah atau Menghapus Isi `research/data/raw/`:**
   - **JANGAN** membaca untuk memodifikasi, menimpa, mengganti nama, atau menghapus berkas apa pun di dalam direktori `research/data/raw/` (`→ research/DATASET.md`).
4. **Dilarang Mengunggah Data Sensitif / PII atau Naskah Peer-Review ke Layanan Luar:**
   - **JANGAN** mengirimkan esai mahasiswa pra-redaksi PII (`raw_s3_key` / `data/raw/`), kredensial `.env`, atau dokumen rahasia ke API LLM publik/pihak ketiga yang menyimpan data pelatihan (`→ research/ETHICS.md#5-risiko-bagi-partisipan-dan-strategi-mitigasi`).

---

## 3. Matriks Verifikasi Manusia (Siapa Memverifikasi Apa)

Agen AI tidak dapat menjadi penulis (*co-author*) dan tidak memikul tanggung jawab hukum/ilmiah. Setiap keluaran agen WAJIB diverifikasi oleh peneliti manusia sesuai pembagian berikut:

| Keluaran / Artefak yang Dibantu AI | Peran Verifikator Manusia | Metode Verifikasi Wajib Sebelum Disetujui |
|---|---|---|
| **Sitasi, DOI, & Tabel Studi (`LITERATURE_REVIEW.md`, `references.bib`)** | Peneliti Utama / Ko-Penulis Literatur | Memeriksa silang (*cross-check*) setiap DOI pada halaman resmi penerbit dan mencocokkan angka hasil dengan PDF asli artikel. |
| **Rumus Metrik & Skrip Eksperimen (`METHODOLOGY.md`, `packages/evaluation-metrics`)** | Ko-Penulis Metodologi & Komputasi | Menjalankan unit test deterministik (`pytest --cov-fail-under=95`) dan mencocokkan hasil dengan hitungan manual pada *toy dataset*. |
| **Hasil Eksperimen & Tabel Naskah (`EXPERIMENT_LOG.md`, `summary_tables.json`)** | Peneliti Utama & Ko-Penulis Komputasi | Memeriksa kecocokan `commit_hash`, `manifest.sha256`, dan `metrics_raw.json` sebelum menghapus label `«dugaan»`. |
| **Kode Platform (`apps/web`, `apps/api`, `apps/nlp-worker`)** | Tech Lead / Reviewer PR Manusia | Code review pada Pull Request berlabel `ai-assisted` dan verifikasi kelulusan CI Gate (`→ docs/GIT_WORKFLOW.md`). |
| **Kepatuhan Privasi, Redaksi PII, & Etika (`ETHICS.md`, `data/processed/`)** | Peneliti Utama / Penanggung Jawab Etik | Audit sampel manual 100% atas hasil redaksi `[REDACTED_*]` sebelum pembekuan `IndoArg-Analytical-v1`. |

---

## 4. Log Penggunaan AI (Append-Only Audit Trail)

Seluruh penggunaan alat AI generatif selama proyek ini WAJIB dicatat secara *append-only* pada tabel di bawah ini:

| Tanggal | Tool dan Model AI | Tugas yang Dikerjakan | Bagian / Berkas Terdampak | Diverifikasi Oleh (Status) |
|---|---|---|---|---|
| `2026-11-17` | Antigravity Agent (`Gemini 4 Argon Medium`) | Penyusunan draf awal *Research Brief* (`RQ1`–`RQ3`, `H1`–`H3b`, definisi operasional) dan *Literature Review* dengan penanda `TODO`/`[CITATION NEEDED]`. | `research/RESEARCH_BRIEF.md`, `research/LITERATURE_REVIEW.md` | Peneliti Utama (Judul Opsi A telah disetujui; menunggu pengesahan `TODO(Q-04)`) |
| `2026-11-17` | Antigravity Agent (`Gemini 4 Argon Medium`) | Penyusunan draf metodologi penelitian (`METHODOLOGY.md`) dan spesifikasi kebutuhan produk (`PRD.md`). | `research/METHODOLOGY.md`, `argumind-platform/docs/PRD.md` | Peneliti Utama (`Pending Review`) |
| `2026-11-18` | Antigravity Agent (`Gemini 4 Argon Medium`) | Penyusunan spesifikasi arsitektur, model data, datasheet korpus, RBAC, rencana/log eksperimen, alur halaman, sistem desain (+ preview HTML), etika riset, ADR, reprodusibilitas, standar kode, pengujian, alur Git, target jurnal (dengan verifikasi web resmi penerbit), dan kebijakan penggunaan AI. | `argumind-platform/docs/*.md`, `research/DATASET.md`, `EXPERIMENT_PLAN.md`, `EXPERIMENT_LOG.md`, `ETHICS.md`, `REPRODUCIBILITY.md`, `JOURNAL_TARGET.md`, `AI_USAGE.md` | Peneliti Utama (`Pending Review`) |

---

## 5. Templat Pernyataan Pengungkapan Penggunaan AI (Untuk Naskah Jurnal)

Sesuai kebijakan penerbit pada `→ research/JOURNAL_TARGET.md#2-spesifikasi-format-dan-teknis-naskah-j-01-tacl-vs-j-02-ipm`, salin salah satu templat resmi berikut ke dalam naskah sebelum pengiriman:

### A. Templat untuk Target Utama `J-01: TACL / ACL` (Bagian *Acknowledgments* atau *Ethical Considerations*)
> **Disclosure of AI Assistance:** During the preparation of this work, the authors used Antigravity (`Gemini 4 Argon`) to assist with drafting documentation structures, scaffolding experimental runner code, and polishing English grammar. No generative AI tools were used to fabricate research data, generate unverified citations, or draw autonomous scientific conclusions. All code, mathematical formulations, experimental logs, and manuscript claims were independently verified and approved by the human authors, who take full responsibility for the content of this publication. *(Note: The LLMs evaluated as part of the proposed hybrid architecture in Experiments E-01–E-03b are objects of scientific study and are fully detailed in the Methodology section).*

### B. Templat untuk Target Cadangan `J-02: Information Processing & Management (Elsevier)`
Letakkan bagian ini tepat sebelum `References` dengan judul khusus sesuai pedoman wajib Elsevier:
> **Declaration of generative AI and AI-assisted technologies in the writing process**
> During the preparation of this work the author(s) used Antigravity (`Gemini 4 Argon`) in order to assist in code scaffolding, documentation structuring, and language editing of the manuscript draft. After using this tool/service, the author(s) reviewed and edited the content as needed and take(s) full responsibility for the content of the published article.

---

## 6. Pertanyaan Terbuka

1. `TODO(Q-AI-01 — Nama Verifikator pada Log)`: Mohon konfirmasi inisial atau nama lengkap Peneliti Utama yang akan dicantumkan pada kolom `"Diverifikasi Oleh"` setelah meninjau draf dokumen spesifikasi ini.
