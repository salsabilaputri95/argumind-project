Tujuan: Menetapkan struktur rute (sitemap), pola state layar standar, spesifikasi tiap halaman, tata letak responsif, alur kerja utama pengguna, serta pola navigasi pada platform Argumind.
Status dan tanggal: Draft v1.0 | 2026-11-18
Sumber kebenaran untuk: Rute aplikasi Next.js (`apps/web/src/app/`), hierarki section per halaman, pemetaan layar ke endpoint `DATA_MODEL.md`, dan alur interaksi `F-01`–`F-07`.

# Halaman & Alur Pengguna (Pages & Flows): Argumind Platform

---

## 1. Sitemap & Matriks Rute Aplikasi

Detail otorisasi server mengacu pada `→ docs/ROLES_PERMISSIONS.md#2-matriks-izin-resource--peran-crud`.

| ID Halaman | Route Path | Nama Halaman | Peran Akses | Tujuan Utama & Rujukan Fitur |
|---|---|---|---|---|
| **`P-01`** | `/login` | Masuk & SSO Institusi | Publik (Tamu) | Autentikasi email/password atau OIDC kampus serta verifikasi MFA `TOTP`. |
| **`P-02`** | `/dashboard` | Daftar Dokumen & Unggah Baru | `author`, `reviewer`, `annotator`, `org_admin` | Mengunggah draf baru (`F-01`), melihat daftar dokumen sesuai scope, dan memfilter status analisis. |
| **`P-03`** | `/documents/[docId]/versions/[ver]/workspace` | Ruang Kerja Peta Argumen & Rubrik | `author`, `reviewer`, `org_admin` | Visualisasi graf interaktif (`F-02`), premis implisit & celah (`F-03`), skor rubrik (`F-04`), dan kontraargumen (`F-05`). |
| **`P-04`** | `/documents/[docId]/compare` | Perbandingan Revisi & Ekspor | `author`, `reviewer`, `org_admin` | Membandingkan delta skor/celah antar-versi draf dan mengekspor laporan `.pdf`/`.json` (`F-07`). |
| **`P-05`** | `/annotations/[docVerId]` | Ruang Kerja Anotasi *Double-Blind* | `annotator` | Menandai span `ArgumentNode`, `ArgumentEdge`, `ImplicitPremise`, dan skor *blind* (`F-06`). |
| **`P-06`** | `/annotations/[docVerId]/adjudicate` | Konsol Adjudikasi *Gold Standard* | `reviewer`, `org_admin` | Membandingkan anotasi 2+ `annotator`, melihat skor $\alpha_{\text{Krip}}$, dan mengunci *gold standard* (`F-06`). |
| **`P-07`** | `/admin/organization` | Manajemen Institusi & Ekspor Korpus | `org_admin` | Mengelola anggota, kuota dokumen bulanan, dan mengunduh korpus riset (`research_opt_in = true`). |

---

## 2. Pola State Layar Standar (Berlaku untuk Semua Halaman)

Aturan ini ditulis satu kali dan WAJIB diterapkan di seluruh halaman (`P-01`–`P-07`) kecuali dinyatakan lain pada bagian pengecualian halaman:

| State Layar | Kondisi Pemicu | Tampilan & Perilaku Wajib (`WAJIB` / `JANGAN`) |
|---|---|---|
| **Loading (Memuat)** | Fetch data awal sedang berlangsung (`isPending == true`). | WAJIB menampilkan *skeleton loader* dengan dimensi tetap (`CLS <= 0.05`) dalam $\le 100\text{ ms}$; JANGAN menampilkan layar putih kosong atau *spinner* layar penuh yang memblokir navigasi. |
| **Kosong (Empty State)** | Respons sukses (`HTTP 200`) dengan `data.length == 0`. | WAJIB menampilkan ilustrasi ikon minimal, teks penjelasan singkat (maks 2 kalimat), dan 1 tombol aksi primer (*Call-to-Action*, mis. `"+ Unggah Dokumen Pertama"`). |
| **Error (Gagal)** | Respons `HTTP 4xx/5xx` (format `RFC 9457` `→ docs/DATA_MODEL.md#5a-konvensi-standar-pagination-filter-sorting-dan-error`). | WAJIB menampilkan banner/toast berisi `detail`, `code`, `trace_id` yang bisa disalin, dan tombol `"Coba Lagi"`. JANGAN menampilkan *stack trace* mentah ke pengguna. |
| **Tanpa Izin (`403`)** | Peran tidak memenuhi syarat rute atau `HTTP 403 ERR_ROLE_FORBIDDEN`. | Elemen aksi tanpa izin WAJIB tidak dirender di DOM; akses URL langsung WAJIB merender tampilan `403 Akses Ditolak` dengan tombol `"Kembali ke Dashboard"`. |

---

## 3. Spesifikasi per Halaman (Maks $\le 30$ Baris per Halaman)

### `P-01` — Masuk & SSO Institusi (`/login`)
- **Wireframe Teks:** `[Header Logo Argumind]` $\rightarrow$ `[Card Tengah: Tab Login Email | Tombol SSO OIDC Kampus]` $\rightarrow$ `[Step Kondisional: Input 6-Digit MFA TOTP]` $\rightarrow$ `[Footer Kebijakan Privasi & Zero-Retention]`.
- **Komponen:** `AuthForm`, `OidcProviderButton`, `TotpInputModal`.
- **Data & Endpoint:** `POST /api/v1/auth/login`, `GET /api/v1/auth/oidc/authorize`, `POST /api/v1/auth/mfa/verify`.
- **Aksi Pengguna:** Submit email/password atau klik SSO; masukkan kode TOTP 6 digit (wajib bagi `org_admin`); klik `"Lupa Kata Sandi"`.
- **Pengecualian State:** Jika pengguna sudah memiliki cookie JWT aktif, langsung *redirect* (`HTTP 307`) ke `/dashboard`.

### `P-02` — Daftar Dokumen & Unggah Baru (`/dashboard`)
- **Rujukan Fitur:** `F-01` | **Wireframe Teks:** `[TopNav + Kuota Organisasi Bar]` $\rightarrow$ `[Header Action: Tombol "+ Dokumen Baru" + Filter Strata & Status + Search]` $\rightarrow$ `[Tabel/Grid Dokumen + Pagination]` $\rightarrow$ `[Modal Unggah: Dropzone .txt/.md/.docx/.pdf | Editor Tempel Teks + Hitung Kata Real-time 300..2500 + Checkbox research_opt_in]`.
- **Komponen:** `QuotaProgressBar`, `DocumentFilterBar`, `DocumentTable`, `UploadDocumentModal`, `LiveWordCounter`.
- **Data & Endpoint:** `GET /api/v1/documents?limit=20&offset=0&domain_strata&status&sort=-created_at`, `POST /api/v1/documents`.
- **Aksi Pengguna:** Memilih berkas/menempel teks; mencentang persetujuan riset (`research_opt_in`); menekan `"Analisis Argumen"`; membuka dokumen yang ada.
- **Pengecualian State:** Tombol submit pada `UploadDocumentModal` WAJIB `disabled` selama `word_count < 300` atau `word_count > 2500` dengan indikator angka merah eksplisit.

### `P-03` — Ruang Kerja Peta Argumen & Rubrik (`/documents/[docId]/versions/[ver]/workspace`)
- **Rujukan Fitur:** `F-01`, `F-02`, `F-03`, `F-04`, `F-05` | **Wireframe Teks:** `[Header: Breadcrumb + Selector Versi + Status Progres SSE + Tombol Bandingkan/Ekspor]` $\rightarrow$ `[Split Pane 3 Kolom: (Kiri 32%) Panel Teks Bersih & Sorotan Span | (Tengah 43%) Kanvas DAG React Flow + Kontrol Filter/Zoom | (Kanan 25%) Tab Skor Rubrik 4 Dimensi, Celah Logika G-xx, & Generator Kontraargumen CA-xx]`.
- **Komponen:** `AnnotatedTextPane`, `ArgumentGraphCanvas`, `NodeInspectorPopover`, `RubricScoreAccordion`, `OverrideScoreForm` (khusus `reviewer`), `CounterargumentDrawer`.
- **Data & Endpoint:** `POST .../analyze`, `GET /api/v1/jobs/{job_id}/stream` (SSE), `GET /api/v1/runs/{run_id}?include=nodes,edges,gaps,scores`, `PATCH .../nodes/{node_key}/feedback`, `PATCH .../scores/{dimension}`.
- **Aksi Pengguna:** Klik node `N-xx` pada graf untuk menggulir teks ($\le 100\text{ ms}$) dan sebaliknya; terima/tolak `ImplicitPremise` (`IP-xx`); picu `Counterargument` (`F-05`); simpan `human_override_score` beserta `override_note` (`reviewer`).
- **Pengecualian State:** Saat analisis berjalan, halaman JANGAN memblokir layar penuh; WAJIB merender progres bertahap via SSE: `stage_1_structure` ($\le 4\text{s}$), `stage_2_implicit_gaps` ($\le 10\text{s}$), dan `stage_3_scoring_complete` ($\le 15\text{s}$). Banner tetap di atas skor menegaskan: *"Skor bersifat diagnostik; keputusan akhir di tangan manusia"*.

### `P-04` — Perbandingan Revisi & Ekspor (`/documents/[docId]/compare`)
- **Rujukan Fitur:** `F-07` | **Wireframe Teks:** `[Header Breadcrumb + Pemilih Versi A vs Versi B + Tombol Unduh .PDF / .JSON]` $\rightarrow$ `[Bar Kartu Delta: Perubahan Overall Score & Selisih Jumlah ReasoningGap]` $\rightarrow$ `[Tabel Perbandingan 4 Dimensi Rubrik (Skor vA vs vB)]` $\rightarrow$ `[Daftar Celah yang Terselesaikan (Resolved) vs Celah Baru]`.
- **Komponen:** `VersionSelectorPair`, `ScoreDeltaSummary`, `DimensionComparisonTable`, `GapDiffList`, `ExportActionButton`.
- **Data & Endpoint:** `GET /api/v1/runs/{run_id_A}`, `GET /api/v1/runs/{run_id_B}`, `GET /api/v1/runs/{run_id_B}/export?format=pdf|json`.
- **Aksi Pengguna:** Memilih dua nomor versi (`v1` vs `v2`); meninjau celah logika yang berhasil diperbaiki; mengunduh berkas laporan `.pdf` atau `.json` ($\le 3\text{ detik}$).
- **Pengecualian State:** Jika dokumen baru memiliki `1` versi (`version_number == 1`), tampilkan state informasi yang mengarahkan pengguna untuk mengunggah revisi `v2` terlebih dahulu.

### `P-05` — Ruang Kerja Anotasi *Double-Blind* (`/annotations/[docVerId]`)
- **Rujukan Fitur:** `F-06` | **Wireframe Teks:** `[Header Mode Blind (Tanpa Nama Penulis) + Indikator Validasi DAG + Tombol Simpan Draf & Submit Final]` $\rightarrow$ `[Split Pane: (Kiri 45%) Teks clean_text dengan Penyeleksi Span Karakter | (Kanan 55%) Kanvas Rakitan Graf Manual + Form Tambah ImplicitPremise, ReasoningGap, & Skor Rubrik Blind]`.
- **Komponen:** `SpanSelectorToolbar`, `ManualGraphBuilder`, `ImplicitPremiseModal`, `DagValidationBanner`, `BlindRubricForm`.
- **Data & Endpoint:** `GET /api/v1/runs/{my_annotator_run_id}`, `PUT /api/v1/annotations/{doc_ver_id}`.
- **Aksi Pengguna:** Menyorot teks untuk membuat `Claim`/`ExplicitPremise`/`Evidence`; menarik garis `Support`/`Attack`; menulis `ImplicitPremise` jembatan; mengisi 4 skor dimensi; menekan `"Submit Anotasi"`.
- **Pengecualian State:** Tombol `"Submit Anotasi"` WAJIB terkunci (`disabled`) jika `DagValidationBanner` mendeteksi siklus pada edge `Support` atau ada dimensi skor tanpa `grounded_refs`.

### `P-06` — Konsol Adjudikasi *Gold Standard* (`/annotations/[docVerId]/adjudicate`)
- **Rujukan Fitur:** `F-06` | **Wireframe Teks:** `[Header Skor Kesepakatan: Krippendorff Alpha & QWK + Tombol Kunci Gold Standard]` $\rightarrow$ `[3-Way Diff View: (Kiri) Anotator 1 | (Tengah) Anotator 2 | (Kanan) Graf Konsensus Gold Standard]`.
- **Komponen:** `AgreementMetricsHeader`, `SpanConflictHighlighter`, `SideBySideGraphDiff`, `AcceptGoldButton`.
- **Data & Endpoint:** `GET /api/v1/runs?doc_version_id={id}&run_source=human_annotator`, `POST /api/v1/annotations/{doc_ver_id}/adjudicate`.
- **Aksi Pengguna:** Meninjau span/edge yang disorot kuning (konflik antar-anotator); memilih anotasi A1, A2, atau menggabungkannya; mengunci hasil sebagai `gold_adjudicated`.
- **Pengecualian State:** Jika jumlah anotator yang selesai pada dokumen tersebut `< 2`, halaman menolak adjudikasi dan menampilkan status `"Menunggu Anotator Ke-2 Selesai"`.

### `P-07` — Manajemen Institusi & Ekspor Korpus (`/admin/organization`)
- **Rujukan Fitur:** Pendukung `F-01`, `F-06` | **Wireframe Teks:** `[Header Organisasi]` $\rightarrow$ `[Tab 1: Anggota & Penetapan Role | Tab 2: Penggunaan Kuota Bulanan | Tab 3: Ekspor Korpus Riset Teranonimisasi]`.
- **Komponen:** `MemberRoleTable`, `QuotaUsageChart`, `CorpusExportPanel` (dilindungi konfirmasi MFA).
- **Data & Endpoint:** `GET /api/v1/users`, `PATCH /api/v1/users/{id}`, `GET /api/v1/runs/export?corpus=true`.
- **Aksi Pengguna:** Mengubah peran anggota (`author` $\leftrightarrow$ `reviewer` / `annotator`); memantau sisa `monthly_doc_quota`; mengunduh paket JSONL korpus riset (`research_opt_in == true`).

---

## 4. Perilaku Responsif Lintas Perangkat

Sesuai kebutuhan non-fungsional pada `→ docs/PRD.md#6-kebutuhan-non-fungsional-terukur`:

| Breakpoint Layar | Perubahan Tata Letak & Komponen Eksplisit |
|---|---|
| **Desktop (`>= 1024px`)** | Tampilan penuh: `P-03`, `P-05`, dan `P-06` menampilkan *Split Pane* multi-kolom dengan kanvas graf interaktif `@xyflow/react` aktif berdampingan dengan panel teks. |
| **Tablet (`768px – 1023px`)** | Pada `P-03`, panel kanan (Skor Rubrik & Celah) berubah menjadi *collapsible bottom/side drawer*; panel Teks (`45%`) dan Kanvas Graf (`55%`) tetap berdampingan. |
| **Mobile (`< 768px`)** | Kanvas graf bebas (`@xyflow/react`) **DINONAKTIFKAN** dan WAJIB otomatis diganti dengan **Mode Daftar Kartu Terstruktur (*Structured Card List View*)** yang menampilkan hierarki `Claim -> Premise -> Evidence` secara vertikal beserta tab pindah layar (`[Tab Teks] | [Tab Struktur] | [Tab Skor]`). Ruang anotasi `P-05` dan adjudikasi `P-06` menampilkan banner wajib layar $\ge 1024\text{ px}$. |

---

## 5. Alur Utama Pengguna (End-to-End Flows)

### Alur 1: Analisis Dokumen, Eksplorasi Graf, & Revisi Penulis (`F-01` s.d. `F-05`, `F-07`)
1. **Aktor:** `author` | **Aksi:** Di `/dashboard` (`P-02`), klik `"+ Dokumen Baru"`, unggah berkas `.docx` (`1.200` kata), dan klik `"Analisis Argumen"`.
2. **Hasil Sistem:** `POST /api/v1/documents` mengembalikan `201 Created`; memicu `POST .../analyze` (`202 Accepted`) dan mengarahkan pengguna ke `/documents/{id}/versions/1/workspace` (`P-03`).
3. **Hasil Bertahap (SSE):** Dalam $\le 4\text{s}$, kanvas merender `Claim`, `ExplicitPremise`, `Evidence`, dan relasi (`stage_1`). Dalam $\le 10\text{s}$, muncul node kuning `ImplicitPremise` (`IP-01`) dan badge merah `ReasoningGap` (`G-01`, `stage_2`). Dalam $\le 15\text{s}$, panel kanan menampilkan skor 4 dimensi beserta `grounded_refs` (`stage_3`).
4. **Aksi lanjutan:** `author` mengklik `G-01` (`HastyGeneralization`); panel teks otomatis menggulir ke kalimat terkait. `author` menekan `"Buat Kontraargumen"` (`F-05`), membaca sanggahan `CA-01`, lalu mengunggah draf perbaikan `v2` dan membuka `P-04` untuk melihat kenaikan skor.
5. **Jalur Gagal (Failure Path):**
   - *Gagal Validasi Kata:* Jika dokumen `210` kata, `POST /api/v1/documents` ditolak (`422 ERR_WORD_COUNT_BOUNDS`); modal tetap terbuka dengan sorotan batas kata.
   - *Timeout LLM (`504 ERR_LLM_TIMEOUT`):* Hasil `stage_1` (IndoBERT + NLI lokal) tetap tersimpan dan tampil di kanvas; panel kanan menampilkan tombol `"Ulangi Analisis Premis Implisit & Skor"` tanpa perlu mengunggah ulang dokumen.

### Alur 2: Tinjauan Pakar & Override Skor Rubrik (`F-04`)
1. **Aktor:** `reviewer` | **Aksi:** Membuka dokumen mahasiswa di `P-03`, mengklik `grounded_refs` `["N-01", "G-01"]` pada dimensi `EvidenceAdequacy` (skor AI = `2`).
2. **Aksi Override:** `reviewer` menilai bukti pada paragraf ke-4 sudah memadai, memilih `human_override_score = 3`, mengetik `override_note` (`45` karakter), dan menekan `"Simpan Penilaian Pakar"`.
3. **Hasil Sistem:** `PATCH .../scores/EvidenceAdequacy` mengembalikan `200 OK`, mencatat aksi ke log audit, dan menampilkan badge `"Diverifikasi Pakar (Skor: 3 | Skor Awal AI: 2)"`.
4. **Jalur Gagal:** Jika `override_note < 10` karakter, validasi form menolak pengiriman (`422`) dan meminta alasan eksplisit.

### Alur 3: Anotasi *Double-Blind* & Adjudikasi Korpus Riset (`F-06`)
1. **Aktor:** Dua `annotator` (`A1` dan `A2`) | **Aksi:** Masing-masing membuka `P-05` (`/annotations/{docVerId}`) secara terpisah, menandai span komponen, merumuskan `ImplicitPremise`, dan menekan `"Submit Anotasi"`.
2. **Aktor:** `reviewer` (Adjudikator) | **Aksi:** Membuka `P-06` (`/annotations/{docVerId}/adjudicate`), meninjau skor $\alpha_{\text{Krip}}$ otomatis, menyelesaikan span yang berbeda di panel tengah, dan menekan `"Kunci Gold Standard"`.
3. **Hasil Sistem:** `POST .../adjudicate` menyimpan rekaman `run_source = 'gold_adjudicated'` (`201 Created`) yang siap diekspor ke dataset riset.
4. **Jalur Gagal:** Jika `A1` mencoba membuka URL milik `A2` atau membuka `P-06`, server menolak dengan `403 ERR_ROLE_FORBIDDEN` dan merender layar `403`.

---

## 6. Pola Navigasi dan Breadcrumb

- **Bilah Navigasi Atas (Top Navigation Bar):** Menampilkan `[Logo Argumind]` | Menu sesuai peran: `Dokumen` (semua peran), `Tugas Anotasi` (khusus `annotator`/`reviewer`), `Admin Organisasi` (khusus `org_admin`) | `[Indikator Kuota Dokumen]` | `[Menu Profil & Logout]`.
- **Format Breadcrumb Wajib (Tampil di `P-03`, `P-04`, `P-05`, `P-06`):**
  - Pada `P-03`: `Dashboard` `/documents` `>` `<Judul Dokumen Terpotong maks 40 char>` `>` `Versi v{ver} (Ruang Kerja)`
  - Pada `P-04`: `Dashboard` `>` `<Judul Dokumen>` `>` `Perbandingan Versi (vA vs vB)`
  - Pada `P-06`: `Tugas Anotasi` `>` `Dokumen #{docVerId_short}` `>` `Adjudikasi Gold Standard`

---

## 7. Pertanyaan Terbuka

1. `TODO(Q-FLOW-01 — Mode Edit Teks In-Place)`: Pada `P-03`, apakah ketika penulis ingin memperbaiki draf menjadi `v2` mereka dapat langsung mengedit teks di panel kiri (`in-place editor`) lalu klik `"Simpan sebagai v2 & Analisis Ulang"`, atau wajib melalui modal unggah versi baru?
