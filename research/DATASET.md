Tujuan: Mendokumentasikan datasheet korpus riset Argumind (`IndoArg-Analytical-v1`), mencakup sumber, ukuran, kamus field, pembersihan data, partisi train/dev/test, anotasi label, anonimisasi PII, lisensi, dan lokasi penyimpanan.
Status dan tanggal: Draft v1.0 | 2026-11-18
Sumber kebenaran untuk: Struktur berkas korpus `data/`, kamus field dataset eksperimen `E-01`–`E-03`, protokol pembersihan data, dan aturan imutabilitas `data/raw/`.

# Datasheet Dataset: IndoArg-Analytical-v1 (Argumind Research Corpus)

> **Aturan Imutabilitas Data Mentah:** Seluruh berkas di dalam direktori `research/data/raw/` bersifat **READ-ONLY (Imutabel)**. Skrip pra-pemrosesan, anotator, maupun peneliti **JANGAN** mengubah, menimpa, atau menghapus berkas di dalam `research/data/raw/`. Seluruh transformasi dan redaksi PII WAJIB ditulis ke `research/data/interim/` dan `research/data/processed/`.

---

## 1. Sumber, Pengumpul, Periode, dan Cara Pengumpulan

| Atribut Datasheet | Spesifikasi Eksplisit |
|---|---|
| **Nama Dataset & Versi** | `IndoArg-Analytical` — Versi `v1.0.0` |
| **Sumber Data (2 Strata)** | 1. **Strata Akademik (`academic`, 50%):** Esai argumentatif/analitis mahasiswa sarjana tahun akhir dan pascasarjana dari minimal 3 perguruan tinggi di Indonesia yang memberikan persetujuan tertulis (`research_opt_in = true`, `→ docs/DATA_MODEL.md#13-documents-dokumen-induk`).<br>2. **Strata Kebijakan & Bisnis (`policy_business`, 50%):** Naskah kajian kebijakan publik (*policy brief*), analisis regulasi, dan opini analitis terbuka dari minimal 4 lembaga riset/instansi publik di Indonesia (`→ research/METHODOLOGY.md#3-populasi-sampel-ukuran-sampel-dan-teknik-sampling`). |
| **Pengumpul & Kurator** | Tim Peneliti Utama Argumind bersama `3` Anotator Terlatih (`role = annotator`) dan `3` Pakar Domain (`role = reviewer`) (`TODO(isi nama institusi & tim peneliti pada AUTHORS_CONTRIBUTIONS.md)`). |
| **Periode Pengumpulan** | `ASUMSI: Durasi 6 minggu` (`TODO(isi tanggal kalender mulai–selesai pengumpulan data aktual)`). |
| **Cara Pengumpulan & Anotasi** | *Purposive Stratified Quota Sampling* melalui modul ruang kerja anotasi `F-06` (`→ docs/DATA_MODEL.md#5-kontrak-endpoint-rest--sse-c-api`). Setiap dokumen dianotasi secara *double-blind* oleh 2 anotator independen (`run_source = 'human_annotator'`), lalu diadjudikasi menjadi *gold standard* (`run_source = 'gold_adjudicated'`). Skor rubrik 4 dimensi pada *test set* dinilai secara *blind* oleh 3 pakar manusia. |

---

## 2. Ukuran Dataset (Baris, Kolom, dan Berkas)

Angka target di bawah ini mengacu pada desain statistik di `→ research/METHODOLOGY.md#3-populasi-sampel-ukuran-sampel-dan-teknik-sampling`; kolom realisasi aktual ditandai `TODO(...)` hingga pembekuan korpus selesai:

| Nama Berkas (`research/data/processed/v1.0/`) | Unit Baris (Rekaman) | Jumlah Baris Target (`ASUMSI`) | Jumlah Baris Aktual | Jumlah Kolom (Field) | Estimasi Ukuran Berkas |
|---|---|---|---|---|---|
| `documents.jsonl` / `.parquet` | 1 baris = 1 dokumen bersih (`clean_text`) | `400` baris | `TODO(isi pasca-kurasi)` | `10` kolom | $\approx 3.5\text{ MB}$ |
| `nodes.jsonl` / `.parquet` | 1 baris = 1 `ArgumentNode` | `4.000–5.200` baris | `TODO(isi pasca-anotasi)` | `10` kolom | $\approx 2.2\text{ MB}$ |
| `edges.jsonl` / `.parquet` | 1 baris = 1 `ArgumentEdge` | `3.200–4.400` baris | `TODO(isi pasca-anotasi)` | `8` kolom | $\approx 1.1\text{ MB}$ |
| `gaps.jsonl` / `.parquet` | 1 baris = 1 `ReasoningGap` | `800–1.500` baris | `TODO(isi pasca-anotasi)` | `8` kolom | $\approx 0.6\text{ MB}$ |
| `rubric_scores.jsonl` / `.parquet` | 1 baris = 1 skor dimensi per dokumen (`4 x N_doc`) | `1.600` baris (`400 x 4`) | `TODO(isi pasca-anotasi)` | `9` kolom | $\approx 0.8\text{ MB}$ |

---

## 3. Kamus Field (Data Dictionary)

Skema field di bawah ini diturunkan secara konsisten dari `→ docs/DATA_MODEL.md#1-skema-entitas-database-postgresql-16` untuk format rilis korpus riset:

### A. Tabel `documents.jsonl`
| Nama Field | Tipe | Unit | Rentang / Nilai Valid | Missing Value | Deskripsi |
|---|---|---|---|---|---|
| `doc_id` | `string` | ID | `doc_0001`..`doc_0400` | `0%` (Wajib) | ID dokumen riset teranonimisasi. |
| `split` | `string (enum)` | Kategori | `train \| dev \| test` | `0%` (Wajib) | Partisi dataset (`70% / 15% / 15%`). |
| `anon_author_id` | `string` | Hash ID | `^anon_author_[a-f0-9]{12}$` | `0%` (Wajib) | Hash `HMAC-SHA256` penulis untuk *group-stratified split*. |
| `anon_source_org` | `string` | Kode | `org_acad_01`..`org_pol_04` | `0%` (Wajib) | Kode anonim institusi asal untuk kontrol efek domain. |
| `domain_strata` | `string (enum)` | Kategori | `academic \| policy_business` | `0%` (Wajib) | Strata domain dokumen. |
| `length_strata` | `string (enum)` | Kategori | `short \| medium \| long` | `0%` (Wajib) | `short` (`300–800`), `medium` (`801–1500`), `long` (`1501–2500` kata). |
| `word_count` | `integer` | Kata | `300..2500` | `0%` (Wajib) | Jumlah kata pada `clean_text`. |
| `char_length` | `integer` | Karakter | `1500..25000` | `0%` (Wajib) | Panjang karakter UTF-8 `clean_text`. |
| `clean_text` | `string` | Teks UTF-8 | String non-kosong | `0%` (Wajib) | Teks dokumen yang telah melewati normalisasi NFKC & redaksi PII. |
| `paragraph_offsets` | `array<object>` | Indeks karakter | `[{para_id, sent_id, start_char, end_char}]` | `0%` (Wajib) | Peta batas kalimat dan paragraf deterministik. |

### B. Tabel `nodes.jsonl`, `edges.jsonl`, `gaps.jsonl`, dan `rubric_scores.jsonl`
| Berkas | Nama Field | Tipe | Unit | Rentang / Nilai Valid | Missing Value | Deskripsi |
|---|---|---|---|---|---|---|
| `nodes` | `node_id` | `string` | ID | `doc_0001_N-01`, `doc_0001_IP-01` | `0%` (Wajib) | ID unik global komponen argumen. |
| `nodes` | `doc_id` | `string` | FK | Merujuk ke `documents.doc_id` | `0%` (Wajib) | ID dokumen pemilik komponen. |
| `nodes` | `node_type` | `string (enum)` | Label | `Claim \| ExplicitPremise \| ImplicitPremise \| Evidence \| Counterargument` | `0%` (Wajib) | Kategori komponen argumen. |
| `nodes` | `start_char` | `integer \| null` | Indeks char | `0..char_length-1` atau `null` | `null` hanya untuk `ImplicitPremise` & `Counterargument` | Posisi karakter awal span eksplisit. |
| `nodes` | `end_char` | `integer \| null` | Indeks char | `start_char+1..char_length` atau `null` | `null` hanya untuk `ImplicitPremise` & `Counterargument` | Posisi karakter akhir span eksplisit. |
| `nodes` | `text_content` | `string` | Teks UTF-8 | Panjang `10..1000` karakter | `0%` (Wajib) | Span teks asli atau rumusan premis implisit/kontraargumen. |
| `nodes` | `evidence_strength` | `integer \| null` | Skor ordinal | `1..5` atau `null` | Wajib terisi jika `node_type == 'Evidence'`; lainnya `null` | Kekuatan bukti yang disajikan. |
| `nodes` | `target_node_id` | `string \| null` | FK Node | `node_id` valid pada `doc_id` sama | Wajib terisi untuk `ImplicitPremise` & `Counterargument` | Node klaim/premis yang dijembatani atau diserang. |
| `edges` | `edge_id` | `string` | ID | `doc_0001_E-01` | `0%` (Wajib) | ID unik relasi berarah. |
| `edges` | `source_node_id` | `string` | FK Node | `source_node_id != target_node_id` | `0%` (Wajib) | Node pendukung atau penyerang. |
| `edges` | `target_node_id` | `string` | FK Node | `node_id` pada `doc_id` sama | `0%` (Wajib) | Node yang didukung atau diserang. |
| `edges` | `relation_type` | `string (enum)` | Label | `Support \| Attack` | `0%` (Wajib) | Tipe relasi logis. |
| `gaps` | `gap_id` | `string` | ID | `doc_0001_G-01` | `0%` (Wajib) | ID unik celah penalaran. |
| `gaps` | `gap_type` | `string (enum)` | Label (6 kelas) | `UnsupportedClaim \| HastyGeneralization \| FalseCause \| CircularReasoning \| MissingCounterargumentConsideration \| WeakEvidence` | `0%` (Wajib) | Kategori taksonomi celah penalaran (`F-03`). |
| `gaps` | `severity` | `string (enum)` | Tingkat | `Low \| Medium \| High` | `0%` (Wajib) | Keparahan celah penalaran. |
| `gaps` | `target_ref` | `string` | FK Node/Edge | `node_id` atau `edge_id` valid | `0%` (Wajib) | Komponen atau transisi yang mengalami cacat logika. |
| `scores` | `dimension` | `string (enum)` | Dimensi (4) | `ClarityOfClaim \| PremiseSupportAndCoherence \| EvidenceAdequacy \| CounterargumentAndLimitationAwareness` | `0%` (Wajib) | Dimensi rubrik kualitas argumen (`F-04`). |
| `scores` | `gold_score` | `integer` | Skor ordinal | `1..5` | `0%` (Wajib) | Skor konsensus/median pakar manusia (*ground truth*). |
| `scores` | `expert_rater_scores` | `array<int>` | Skor per pakar | `[r1, r2, r3]`, masing-masing `1..5` | Hanya pada `split == 'test'`; `null` pada `train` | Skor *blind* individu dari 3 pakar manusia untuk hitung `QWK`. |
| `scores` | `grounded_refs` | `array<string>` | Array ID | Minimal 1 elemen (`["doc_0001_N-01"]`) | `0%` (Wajib) | Daftar ID node/gap yang menjadi dasar bukti penilaian dimensi. |

---

## 4. Langkah Pembersihan Data Berurutan dan Jumlah Baris Terbuang

Seluruh langkah mengacu pada *pipeline* deterministik di `→ research/METHODOLOGY.md#4-pengumpulan-data-dan-urutan-pra-pemrosesan-preprocessing`:

| Urutan | Nama Langkah (`step_id`) | Aturan Eksekusi & Alasan Pembersihan | Jumlah Dokumen/Baris Terbuang |
|---|---|---|---|
| **1** | Validasi Izin & Lisensi (`consent_filter`) | Membuang dokumen mahasiswa yang tidak memiliki `research_opt_in = true` atau dokumen kebijakan dengan hak cipta tertutup. *Alasan:* Kepatuhan etika riset dan hukum. | `TODO(isi jumlah aktual)` (`ASUMSI: ~5% dari kandidat mentah`) |
| **2** | Ekstraksi & Normalisasi UTF-8 (`encoding_normalization`) | Membuang berkas `.pdf`/`.docx` yang rusak atau merupakan hasil pindaian gambar tanpa lapisan teks (`ERR_CORRUPT_FILE`), lalu menormalisasi Unicode ke `NFKC`. *Alasan:* Mencegah kesalahan indeks karakter `start_char..end_char`. | `TODO(isi jumlah aktual)` (`ASUMSI: ~3% dari kandidat mentah`) |
| **3** | Deduplikasi Dekat (`near_deduplication`) | Menghitung hash `SHA-256` dan kemiripan *MinHash Jaccard* ($\ge 0.85$); membuang draf duplikat dari penulis yang sama. *Alasan:* Mencegah kebocoran data (*data leakage*) antar-split. | `TODO(isi jumlah aktual)` (`ASUMSI: ~2% dari kandidat mentah`) |
| **4** | Penyaringan Panjang & Bahasa (`quality_gate`) | Membuang dokumen dengan `word_count < 300` atau `word_count > 2500`, atau proporsi kalimat berbahasa asing $> 20\%$. *Alasan:* Menjaga ruang lingkup analitis (`→ docs/DATA_MODEL.md#14-document_versions-versi-draf--teks-bersih--f-01-f-07`). | `TODO(isi jumlah aktual)` (`ASUMSI: ~8% dari kandidat mentah`) |
| **5** | Redaksi PII (`pii_redaction`) | Mengganti nama orang, NIM/NIP, email, nomor telepon, dan nama institusi penulis dengan token `[REDACTED_NAME]`, `[REDACTED_ID]`, `[REDACTED_EMAIL]`. Tidak membuang baris, namun wajib diverifikasi manual 100% sebelum masuk anotasi. | `0` baris terbuang (transformasi in-place pada `interim/`) |
| **6** | Audit Konsistensi Anotasi Graf (`graph_integrity_filter`) | Membuang/mengembalikan ke adjudikasi setiap anotasi yang melanggar aturan DAG asiklik, memiliki span di luar batas karakter, atau memiliki $\alpha_{\text{Krip}} < 0.75$ pada batch kalibrasi. | `0` dokumen terbuang di rilis akhir (seluruh konflik WAJIB diselesaikan pada tahap adjudikasi). |

---

## 5. Pembagian Train, Validation (Dev), dan Test

| Partisi (`split`) | Proporsi | Jumlah Dokumen Target ($N=400$) | Komposisi Strata Domain | Komposisi Strata Panjang | Aturan Isolasi Wajib |
|---|---|---|---|---|---|
| **`train`** | `70%` | `280` dokumen | `140` `academic` + `140` `policy_business` | Seimbang per kuartil panjang (`short`, `medium`, `long`) | **Group-Stratified Split:** `anon_author_id` dan klaster topik pada `train` **JANGAN** muncul di `dev` maupun `test`. |
| **`dev` (validation)** | `15%` | `60` dokumen | `30` `academic` + `30` `policy_business` | Seimbang per kuartil panjang | Digunakan khusus untuk *early stopping* dan pemilihan *threshold* NLI. |
| **`test`** | `15%` | `60` dokumen | `30` `academic` + `30` `policy_business` | Seimbang per kuartil panjang | **Dibekukan (*frozen*):** Dinilai oleh 3 pakar *blind*; JANGAN dilihat saat tuning hyperparameter. |

---

## 6. Distribusi Label dan Potensi Bias

1. **Ketidakseimbangan Kelas (*Class Imbalance*):**
   - Pada komponen eksplisit (`nodes`), jumlah `ExplicitPremise` dan `Evidence` secara alami 2–4 kali lebih banyak daripada `Claim`.
   - Pada relasi (`edges`), relasi `Support` diperkirakan mendominasi (`~80–85%`) dibandingkan `Attack` (`~15–20%`). *Mitigasi:* Evaluasi wajib menggunakan **Macro-F1** (bukan Micro-F1/Accuracy) dan pelatihan menggunakan *class-weighted cross-entropy loss*.
2. **Potensi Bias Sumber & Gaya Bahasa:**
   - Esai mahasiswa dari kampus pulau Jawa atau kajian kebijakan kementerian pusat berpotensi mendominasi gaya kosakata formal. *Mitigasi:* Kuota sampling mewajibkan minimal 3 perguruan tinggi dan 4 lembaga berbeda, serta pengujian *length bias* ($|\rho_{YL \cdot H}| \le 0.20$).

---

## 7. Lisensi, Izin Penggunaan, PII, dan Keterbatasan

- **Lisensi Dataset Rilis:** `CC BY-NC-SA 4.0` (*Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International*) untuk keperluan riset akademik non-komersial (`TODO(konfirmasi pilihan lisensi dengan komite etik/institusi)`).
- **Izin Penggunaan:** Dilarang menggunakan korpus untuk melatih ulang model komersial tertutup tanpa izin tertulis atau mencoba melakukan de-anonimisasi penulis esai.
- **Penanganan PII & Anonimisasi:** Mengikuti aturan ketat pada `→ docs/DATA_MODEL.md#6-data-penelitian-dan-aturan-anonimisasi--researchdatasetmd`: penghapusan seluruh atribut tabel `users`, pengacakan `anon_author_id` dengan `HMAC-SHA256`, dan penggantian entitas identitas di dalam teks dengan `[REDACTED_*]`.
- **Keterbatasan Dataset:**
  1. Hanya mencakup teks analitis Bahasa Indonesia sepanjang `300–2.500` kata; tidak mewakili argumen lisan atau media sosial pendek (X/TikTok).
  2. Anotasi `ImplicitPremise` menyediakan 1 rumusan konsensus adjudikasi dan 2 rumusan anotator asli per lompatan logika; karena sifat bahasa alami, rumusan parafrasa lain yang sah secara logis tetap dimungkinkan.

---

## 8. Lokasi, Versi, Checksum, dan Cara Akses

### A. Struktur Direktori Penyimpanan Data
```text
research/data/
├── raw/                        # [READ-ONLY / IMUTABEL] Berkas asli .docx/.pdf/.txt sebelum redaksi PII (DILARANG DIUBAH & DILARANG COMMIT KE GIT PUBLIK)
├── interim/                    # Hasil ekstraksi teks UTF-8, redaksi PII, dan ekspor mentah anotator sebelum adjudikasi
└── processed/
    └── v1.0/                   # Rilis resmi IndoArg-Analytical-v1 (documents, nodes, edges, gaps, rubric_scores + manifest.sha256)
```

### B. Versi dan Checksum Integritas (`SHA-256`)
Setiap rilis di `research/data/processed/v1.0/` WAJIB disertai berkas `manifest.sha256`:
- `documents.jsonl`: `TODO(isi hash SHA-256 64-karakter saat pembekuan v1.0)`
- `nodes.jsonl`: `TODO(isi hash SHA-256 64-karakter saat pembekuan v1.0)`
- `edges.jsonl`: `TODO(isi hash SHA-256 64-karakter saat pembekuan v1.0)`
- `gaps.jsonl`: `TODO(isi hash SHA-256 64-karakter saat pembekuan v1.0)`
- `rubric_scores.jsonl`: `TODO(isi hash SHA-256 64-karakter saat pembekuan v1.0)`

### C. Cara Akses dan Verifikasi
1. `research/data/raw/` hanya dapat diakses oleh Peneliti Utama di penyimpanan terenkripsi (`AES-256`) lokal/institusi dan masuk ke `.gitignore`.
2. `research/data/processed/v1.0/` dimuat melalui skrip pemuat standar dengan memverifikasi checksum terlebih dahulu:
   `sha256sum -c research/data/processed/v1.0/manifest.sha256`

---

## 9. Pertanyaan Terbuka

1. `TODO(Q-DATA-02 — Persetujuan Lisensi Publikasi)`: Apakah komite etik / institusi menyetujui pelepasan `research/data/processed/v1.0/` secara publik di repositori akademik (mis. Zenodo / HuggingFace Datasets) di bawah lisensi `CC BY-NC-SA 4.0`, atau akses dibatasi melalui mekanisme *data request agreement*?
