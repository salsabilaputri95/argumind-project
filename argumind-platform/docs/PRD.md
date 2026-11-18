Tujuan: Mendefinisikan kebutuhan produk, metrik keberhasilan, persona pengguna, daftar fitur (`F-01`–`F-07`), kebutuhan non-fungsional, risiko, dan fase rilis untuk platform Argumind.
Status dan tanggal: Draft v1.0 | 2026-11-17
Sumber kebenaran untuk: Ruang lingkup produk, spesifikasi fitur `F-01`–`F-07`, kriteria penerimaan (*acceptance criteria*), dan target kebutuhan non-fungsional.

# Product Requirements Document (PRD): Argumind Platform

## 1. Latar Belakang dan Masalah

Dokumen analisis kebijakan, laporan bisnis, dan esai akademik berbahasa Indonesia sering tampak rapi secara kebahasaan namun rapuh secara logika karena melompat ke kesimpulan, menyembunyikan asumsi (*implicit premise*), dan miskin bukti pendukung. Peninjauan manual oleh dosen, editor, atau analis senior membutuhkan 15–30 menit per dokumen (1.000–2.500 kata) dan menghasilkan penilaian yang subjektif antar-penilai (`→ research/RESEARCH_BRIEF.md#1-masalah-dan-latar-belakang`). Penggunaan *chatbot* AI umum menghasilkan komentar naratif yang tidak terstruktur, mudah bias terhadap panjang teks, dan sering memberikan alasan yang tidak sesuai dengan isi argumen. Organisasi pendidikan tinggi, lembaga riset kebijakan, dan tim konsultan membutuhkan platform evaluasi penalaran kritis yang memetakan struktur argumen secara visual dan konsisten. Argumind menyediakan pemetaan graf klaim-premis-bukti, deteksi premis implisit serta celah logika, penilaian rubrik terjelaskan, dan generator kontraargumen sebagai pendamping keputusan manusia (*human-in-the-loop*).

---

## 2. Tujuan dan Metrik Keberhasilan

| ID Metrik | Metrik Keberhasilan | Target Kuantitatif | Cara Ukur & Periode Evaluasi |
|---|---|---|---|
| **M-01** | Pengguna Aktif Mingguan (*Weekly Active Users* / WAU) | $\ge 50\text{ WAU}$ pada Bulan ke-3 pasca-rilis MVP | Jumlah pengguna unik yang menyelesaikan $\ge 1$ analisis dokumen per minggu pada log analitik produk. |
| **M-02** | Retensi Kohort Minggu ke-4 (*Week-4 Retention*) | $\ge 25\%$ | Persentase pengguna terdaftar di Minggu ke-1 yang kembali menjalankan analisis di Minggu ke-4. |
| **M-03** | Tingkat Persetujuan Pakar (*Expert Graph Acceptance*) | $\ge 75\%$ node/edge dinilai akurat | Rasio komponen dan premis implisit yang disetujui tanpa revisi mayor oleh penilai pakar (`→ research/RESEARCH_BRIEF.md#4-hipotesis`). |
| **M-04** | Keselarasan Skor Rubrik (*Human-AI Agreement*) | `QWK` $\ge 0.70$, Spearman $\rho \ge 0.70$ | Evaluasi *blind scoring* antara sistem dan 3 pakar pada 4 dimensi rubrik (`E-03`). |
| **M-05** | Efisiensi Waktu Tinjauan Argumen | Penurunan waktu $\ge 30\%$ (dari rata-rata 20 menit ke $\le 14$ menit/dokumen) | Perbandingan durasi peninjauan dokumen sebelum dan sesudah menggunakan peta argumen Argumind. |

---

## 3. Persona Pengguna

Detail hak akses per peran dirujuk ke `→ docs/ROLES_PERMISSIONS.md`.

| Peran (`role_id`) | Kebutuhan Utama | Kendala & Titik Friksi |
|---|---|---|
| **Penulis / Mahasiswa (`author`)** | Mendapatkan peta visual celah penalaran, asumsi tersembunyi, dan saran kontraargumen sebelum mengumpulkan draf esai atau kajian kebijakan. | Sulit menyadari lompatan logika pada tulisan sendiri; membutuhkan umpan balik cepat ($\le 15\text{ detik}$) dengan bahasa yang mudah dipahami. |
| **Penilai / Dosen / Analis Senior (`reviewer`)** | Menilai puluhan draf dengan rubrik 4 dimensi yang konsisten, melihat bukti kutipan span teks secara langsung, dan memberi koreksi akhir. | Waktu terbatas (15–30 menit/dokumen); tidak percaya pada skor otomatis jika tidak disertai rujukan kalimat spesifik di dalam teks. |
| **Anotator Riset (`annotator`)** | Menandai batas komponen (`start_char`, `end_char`), relasi `Support`/`Attack`, merumuskan `ImplicitPremise`, dan melakukan adjudikasi korpus riset. | Membutuhkan antarmuka penandaan span yang presisi tanpa tumpang-tindih rusak serta validasi aturan graf otomatis. |
| **Admin Institusi (`org_admin`)** | Mengelola kuota analisis, akun anggota tim/kelas, rubrik standar institusi, serta kepatuhan privasi dokumen. | Anggaran terbatas; mewajibkan dokumen internal tidak dipakai untuk melatih model publik. |

---

## 4. Ruang Lingkup Produk

Definisi domain riset mengacu pada `→ research/RESEARCH_BRIEF.md#6-ruang-lingkup-batasan-dan-asumsi`.

- **In-Scope (Termasuk dalam Produk):**
  1. Unggah dan tempel teks Bahasa Indonesia (`300–2.500` kata) dalam format teks polos, `.md`, `.docx`, dan `.pdf` berbasis teks.
  2. Ekstraksi komponen (`Claim`, `ExplicitPremise`, `Evidence`), relasi (`Support`, `Attack`), rekonstruksi `ImplicitPremise`, dan deteksi 6 tipe `ReasoningGap`.
  3. Kanvas interaktif peta graf argumen yang terhubung dua arah (*bidirectional highlight*) dengan span teks sumber.
  4. Penilaian rubrik 4 dimensi skala `1..5` berbasis bukti graf (`grounded_refs`), generator `Counterargument`, koreksi manual oleh manusia, dan mode anotasi dataset riset.
- **Out-of-Scope (Di Luar Ruang Lingkup Produk):**
  1. Verifikasi kebenaran faktual klaim terhadap sumber eksternal/internet (cakupan proyek `EpistemicGate`).
  2. Pemrosesan gambar pindaian tanpa teks (*OCR scanned PDF*), transkrip audio/video, atau teks di luar rentang `300–2.500` kata.
  3. Penentuan kelulusan akademik otomatis tanpa persetujuan `reviewer`.

---

## 5. Spesifikasi Fitur (`F-01` s.d. `F-07`)

Detail teknis implementasi dirujuk ke `→ docs/ARCHITECTURE.md` dan alur layar ke `→ docs/PAGES_AND_FLOWS.md`.

### `F-01` — Unggah Dokumen & Segmentasi Komponen Argumen
- **Prioritas MoSCoW:** `Must Have` | **Dependensi:** Tidak ada.
- **User Story:** Sebagai `author` atau `reviewer`, saya ingin memasukkan teks atau dokumen (`.txt`, `.md`, `.docx`, `.pdf`) agar sistem secara otomatis menandai batas `Claim`, `ExplicitPremise`, dan `Evidence` pada teks sumber.
- **Acceptance Criteria:**
  1. **Given** pengguna memasukkan teks Bahasa Indonesia sepanjang `300–2.500` kata, **When** pengguna menekan tombol `"Analisis Argumen"`, **Then** sistem menerima dokumen (`HTTP 200/201`) dan mengekstrak daftar `ArgumentNode` dengan indeks `start_char` dan `end_char` yang valid.
  2. **Given** pengguna memasukkan dokumen dengan jumlah kata `< 300` atau `> 2.500`, **When** validasi dijalankan, **Then** sistem menolak permintaan (`HTTP 422`) dan menampilkan pesan batas kata eksplisit.
  3. **Given** dokumen mengandung identitas pribadi (nama penulis/NIM/email pada header), **When** opsi anonimisasi aktif, **Then** sistem menyamarkan teks tersebut menjadi token `[REDACTED_*]` sebelum dianalisis.

### `F-02` — Pemetaan Relasi & Visualisasi Graf Argumen Interaktif
- **Prioritas MoSCoW:** `Must Have` | **Dependensi:** `F-01`.
- **User Story:** Sebagai `author` atau `reviewer`, saya ingin melihat peta visual hubungan `Support` dan `Attack` antar-komponen argumen yang tersinkronisasi dengan teks asli agar struktur penalaran terlihat jelas.
- **Acceptance Criteria:**
  1. **Given** komponen argumen telah diekstrak oleh `F-01`, **When** pemetaan relasi selesai, **Then** sistem menampilkan graf berarah tanpa siklus langsung (*self-loop* `source_id == target_id` WAJIB `0`).
  2. **Given** peta graf dan panel teks tampil berdampingan, **When** pengguna mengklik node `N-01` pada graf, **Then** layar menggulir otomatis ke posisi `start_char..end_char` `N-01` pada teks dalam waktu $\le 100\text{ ms}$.
  3. **Given** sebuah edge memiliki `relation = "Support"` atau `"Attack"`, **When** dirender di kanvas, **Then** sistem membedakan warna, ikon, dan garis (`solid` vs `dashed`) beserta nilai `confidence` (`0.00..1.00`) sesuai `→ docs/DESIGN_SYSTEM.md`.

### `F-03` — Deteksi Premis Implisit & Celah Penalaran (*Reasoning Gap*)
- **Prioritas MoSCoW:** `Must Have` | **Dependensi:** `F-01`, `F-02`.
- **User Story:** Sebagai `author`, saya ingin melihat asumsi tersembunyi (`ImplicitPremise`) dan celah logika (`ReasoningGap`) pada argumen saya agar saya dapat memperbaiki lompatan kesimpulan.
- **Acceptance Criteria:**
  1. **Given** terdapat pasangan `ExplicitPremise → Claim` yang melompat secara logis, **When** modul `F-03` berjalan, **Then** sistem menyisipkan node jembatan bertipe `ImplicitPremise` (`start_char: null`) di antara kedua node tersebut.
  2. **Given** sebuah node atau relasi terdeteksi cacat logis, **When** hasil ditampilkan, **Then** sistem melabelinya dengan salah satu dari 6 kategori: `UnsupportedClaim`, `HastyGeneralization`, `FalseCause`, `CircularReasoning`, `MissingCounterargumentConsideration`, atau `WeakEvidence` beserta tingkat keparahan (`Low`, `Medium`, `High`).
  3. **Given** pengguna meninjau suatu `ImplicitPremise`, **When** pengguna mengklik tombol `"Terima ke Draf"` atau `"Tandai Tidak Valid"`, **Then** sistem menyimpan keputusan umpan balik pengguna untuk evaluasi model.

### `F-04` — Penilaian Rubrik 4 Dimensi Terjelaskan (*Explainable Scoring*)
- **Prioritas MoSCoW:** `Must Have` | **Dependensi:** `F-01`, `F-02`, `F-03`.
- **User Story:** Sebagai `reviewer`, saya ingin melihat skor diagnostik `1..5` pada 4 dimensi rubrik beserta rujukan ID komponen dan celah spesifik agar penilaian dapat dipertanggungjawabkan.
- **Acceptance Criteria:**
  1. **Given** graf argumen dokumen telah terbentuk, **When** modul penilaian selesai, **Then** sistem menampilkan skor integer `1..5` untuk `ClarityOfClaim`, `PremiseSupportAndCoherence`, `EvidenceAdequacy`, dan `CounterargumentAndLimitationAwareness`, serta `overall_score` (`1.00..5.00`).
  2. **Given** setiap skor dimensi ditampilkan, **When** pengguna membuka rincian alasan (*rationale*), **Then** setiap dimensi WAJIB memuat minimal 1 rujukan `grounded_refs` (`node_id` atau `gap_id`) yang dapat diklik; sistem JANGAN menampilkan skor tanpa `grounded_refs`.
  3. **Given** seorang `reviewer` tidak setuju dengan skor sistem, **When** `reviewer` mengubah nilai dimensi dan mengisi catatan revisi, **Then** sistem menyimpan skor manusia (`human_override_score`) secara terpisah tanpa menghapus skor awal sistem.

### `F-05` — Generator Kontraargumen Terarah
- **Prioritas MoSCoW:** `Should Have` | **Dependensi:** `F-01`, `F-03`.
- **User Story:** Sebagai `author`, saya ingin menghasilkan kontraargumen yang menguji klaim atau asumsi implisit utama saya agar tulisan saya lebih tahan terhadap kritik.
- **Acceptance Criteria:**
  1. **Given** pengguna memilih suatu `Claim` atau `ImplicitPremise` pada graf, **When** pengguna memicu generator kontraargumen, **Then** sistem menghasilkan minimal 1 dan maksimal 3 `Counterargument` yang relevan dan terikat pada `target_node_id` tersebut.
  2. **Given** kontraargumen telah ditampilkan, **When** pengguna menambahkan tanggapan/sanggahan di editor teks dan menjalankan analisis ulang, **Then** sistem memperbarui skor dimensi `CounterargumentAndLimitationAwareness`.

### `F-06` — Ruang Kerja Anotasi & Adjudikasi Korpus Riset
- **Prioritas MoSCoW:** `Must Have` (untuk mendukung eksperimen `E-01`–`E-03`) | **Dependensi:** `F-01`, `F-02`.
- **User Story:** Sebagai `annotator`, saya ingin menandai span komponen, menghubungkan relasi, menulis `ImplicitPremise` rujukan, dan menyelesaikan perbedaan anotasi secara *double-blind* agar dataset riset mencapai Krippendorff's $\alpha \ge 0.75$.
- **Acceptance Criteria:**
  1. **Given** `annotator` membuka dokumen tugas anotasi dalam mode *blind*, **When** `annotator` menyorot teks dan memilih tipe komponen, **Then** sistem menyimpan `start_char`, `end_char`, dan `type` tanpa memperlihatkan anotasi milik anotator lain pada dokumen yang sama.
  2. **Given** minimal 2 `annotator` telah menyelesaikan dokumen yang sama, **When** peneliti membuka panel adjudikasi, **Then** sistem menghitung skor kesepakatan ($\alpha_{\text{Krip}}$ / `QWK`) dan menyorot span/relasi yang berbeda untuk diputuskan menjadi *gold standard*.

### `F-07` — Perbandingan Revisi Draf & Ekspor Laporan Diagnostik
- **Prioritas MoSCoW:** `Could Have` | **Dependensi:** `F-02`, `F-04`.
- **User Story:** Sebagai `author` atau `reviewer`, saya ingin membandingkan skor argumen antar-versi revisi dan mengekspor hasil analisis ke format `.pdf` atau `.json` agar progres perbaikan terdokumentasi.
- **Acceptance Criteria:**
  1. **Given** dokumen memiliki $\ge 2$ versi analisis, **When** pengguna membuka tampilan perbandingan versi, **Then** sistem menampilkan selisih (`delta`) jumlah `ReasoningGap` dan perubahan skor 4 dimensi rubrik.
  2. **Given** analisis dokumen telah selesai, **When** pengguna mengklik `"Ekspor Laporan"`, **Then** sistem mengunduh berkas `.json` (skema data penuh untuk riset) atau `.pdf` (ringkasan rubrik dan daftar celah argumen) dalam waktu $\le 3\text{ detik}$.

---

## 6. Kebutuhan Non-Fungsional Terukur

| Kategori | Spesifikasi Eksplisit & Ambang Terukur (`WAJIB` / `JANGAN`) |
|---|---|
| **Performa & Latensi** | 1. Waktu pemrosesan *end-to-end* (`F-01` s.d. `F-04`) untuk dokumen 1.000 kata WAJIB $\le 15.0\text{ detik}$ pada persentil ke-95 (`p95`).<br>2. Interaksi klik/geser pada kanvas graf hingga `100` node WAJIB mempertahankan frame rate $\ge 55\text{ fps}$ dan waktu respons sorotan teks $\le 100\text{ ms}$.<br>3. *First Contentful Paint* (`FCP`) halaman aplikasi WAJIB $\le 1.5\text{ detik}$. |
| **Keamanan & Privasi Data** | 1. Seluruh lalu lintas data WAJIB dienkripsi dengan `TLS 1.3` dan penyimpanan dokumen menggunakan `AES-256` *at-rest*.<br>2. Sistem JANGAN mengirimkan teks dokumen pengguna ke penyedia pihak ketiga dengan kebijakan retensi pelatihan (*zero data retention* wajib aktif).<br>3. Dokumen esai mahasiswa dalam mode riset WAJIB melewati redaksi PII otomatis sebelum disimpan ke tabel korpus (`→ research/ETHICS.md`). |
| **Aksesibilitas (a11y)** | 1. Antarmuka WAJIB memenuhi standar **WCAG 2.1 Level AA** dengan rasio kontras teks normal $\ge 4.5:1$ dan teks besar/komponen graf $\ge 3.0:1$.<br>2. Status komponen (`Claim`, `ExplicitPremise`, `Evidence`) dan relasi (`Support`, `Attack`) JANGAN hanya dibedakan dengan warna; WAJIB disertai label badge teks dan ikon bentuk/pola garis. |
| **SEO & Indeksasi** | 1. Halaman publik (*Landing Page* & dokumentasi publik) WAJIB memiliki skor Lighthouse SEO $\ge 90$.<br>2. Halaman ruang kerja dokumen, graf argumen, dan anotasi riset WAJIB memasang header `X-Robots-Tag: noindex, nofollow` agar dokumen pengguna tidak terindeks mesin pencari. |
| **Dukungan Browser & Perangkat** | 1. WAJIB mendukung penuh Chrome `>= 120`, Edge `>= 120`, Firefox `>= 120`, dan Safari `>= 17` pada resolusi desktop/tablet $\ge 1024\times 768\text{ px}$ (kanvas graf membutuhkan lebar layar $\ge 1024\text{ px}$).<br>2. Pada layar mobile (`< 768 px`), tampilan graf WAJIB otomatis beralih ke mode daftar kartu terstruktur (*structured card list view*). |

---

## 7. Asumsi, Risiko, dan Fase Rilis

### A. Asumsi Produk
- `ASUMSI: P-01` — Pengguna institusi pendidikan dan analis kebijakan terbiasa mengunggah draf dalam format `.docx`, `.pdf` teks, atau menyalin teks langsung ke editor web.
- `ASUMSI: P-02` — Penyediaan mode anotasi internal (`F-06`) di dalam platform yang sama akan memangkas waktu pengumpulan data riset sebesar 40% dibandingkan memakai alat terpisah.

### B. Matriks Risiko Produk

| ID Risiko | Deskripsi Risiko | Kemungkinan | Dampak | Mitigasi Eksplisit |
|---|---|---|---|---|
| **R-01** | Penjelasan LLM tidak selaras dengan skor rubrik (*unfaithful explanation*). | Sedang | Tinggi | Wajibkan skema `grounded_refs` pada `F-04` dan tolak output tanpa rujukan ID node/gap yang valid (`→ research/RESEARCH_BRIEF.md#5-tujuan-dan-kontribusi`). |
| **R-02** | Latensi analisis melebihi `15 detik` saat antrean dokumen padat. | Sedang | Sedang | Tampilkan hasil bertahap (*progressive rendering*: komponen `F-01` & `F-02` tampil dalam $\le 4\text{ detik}$, diikuti `F-03` & `F-04`). |
| **R-03** | Pengguna menganggap skor Argumind sebagai nilai kelulusan mutlak (*over-reliance*). | Tinggi | Tinggi | Pasang banner peringatan tetap bahwa skor bersifat diagnostik dan wajibkan konfirmasi `reviewer` sebelum ekspor penilaian resmi. |
| **R-04** | Anggaran institusi kampus lambat untuk pengadaan lisensi. | Tinggi | Sedang | Sediakan kuota *freemium* untuk dosen/mahasiswa individu dan fokuskan monetisasi institusi pada lisensi laboratorium/konsultan kebijakan. |

### C. Fase Rilis (Roadmap 8 Minggu)
- **Fase 1 — Fondasi & Alat Anotasi Riset (Minggu 1–3):** Rilis `F-01` (input & segmentasi dasar), `F-02` (kanvas graf dasar), dan `F-06` (ruang kerja anotasi & adjudikasi) agar pengumpulan korpus riset dapat langsung berjalan.
- **Fase 2 — Inti Penalaran & Rubrik (Minggu 4–6):** Integrasi penuh `F-03` (deteksi `ImplicitPremise` & `ReasoningGap`), `F-04` (skor rubrik 4 dimensi berbasis graf), dan `F-05` (generator kontraargumen) untuk eksperimen `E-01`–`E-03`.
- **Fase 3 — Pilot & Evaluasi Pakar (Minggu 7–8):** Rilis `F-07` (perbandingan revisi & ekspor laporan), uji coba pilot pengguna (`M-01`–`M-05`), dan evaluasi *go/no-go* Bulan ke-3.

---

## 8. Pertanyaan Terbuka

1. `TODO(Q-PRD-01 — Kuota Freemium)`: Berapa batas jumlah dokumen per bulan untuk akun gratis (`author` individu) sebelum diwajibkan beralih ke lisensi institusi (mis. `5` dokumen/bulan)?
2. `TODO(Q-PRD-02 — Integrasi LMS)`: Apakah ekspor nilai ke LMS kampus (Moodle/Canvas via CSV) diperlukan pada Fase 3 atau ditunda ke rilis v2.0 pasca-pilot?
