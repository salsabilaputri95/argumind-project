Tujuan: Menetapkan kepatuhan etika penelitian, status *ethical clearance*, protokol rekrutmen dan *informed consent*, tata kelola data pribadi (UU PDP), mitigasi risiko partisipan, konflik kepentingan, dan pendanaan untuk proyek Argumind.
Status dan tanggal: Draft v1.0 | 2026-11-18
Sumber kebenaran untuk: Protokol perlindungan subjek manusia, kepatuhan privasi korpus `IndoArg-Analytical-v1`, hak pencabutan persetujuan (*right to erasure*), dan deklarasi etik publikasi.

# Etika Penelitian & Pelindungan Data Pribadi (Research Ethics): Explainable Argument Mining and Implicit Premise Detection for Evaluating Critical Reasoning in Indonesian Analytical Texts

---

## 1. Status *Ethical Clearance* (Kelaikan Etik)

| Atribut Kelaikan Etik | Spesifikasi & Status Saat Ini |
|---|---|
| **Kebutuhan Kelaikan Etik** | **WAJIB** (*Required*). Penelitian ini melibatkan pengumpulan esai akademik mahasiswa (`domain_strata = 'academic'`), penugasan 3 anotator manusia (`role = annotator`), dan evaluasi *blind scoring* oleh 3 pakar domain (`role = reviewer`) (`→ research/METHODOLOGY.md#3-populasi-sampel-ukuran-sampel-dan-teknik-sampling`). |
| **Lembaga Komisi Etik (IRB / KEPK)** | `TODO(isi nama resmi Komisi Etik Penelitian Perguruan Tinggi / BRIN)` |
| **Nomor Surat Keputusan Etik** | `TODO(isi nomor protokol ethical clearance setelah terbit; JANGAN memulai rekrutmen esai mahasiswa sebelum surat terbit)` |
| **Tanggal Persetujuan & Masa Berlaku** | `TODO(isi tanggal persetujuan YYYY-MM-DD s.d. YYYY-MM-DD)` |
| **Pengecualian Strata Publik** | Dokumen pada `domain_strata = 'policy_business'` yang diambil dari naskah kajian kebijakan publik pemerintah/lembaga riset terbuka tidak melibatkan subjek manusia baru, namun tetap WAJIB melewati redaksi PII (`pii_redaction`) sebelum masuk korpus. |

---

## 2. Partisipan Penelitian dan Prosedur Rekrutmen

| Kelompok Partisipan | Kriteria Inklusi Partisipan | Target Jumlah | Cara Rekrutmen & Kompensasi | Aturan Anti-Koersi (`WAJIB` / `JANGAN`) |
|---|---|---|---|---|
| **1. Kontributor Esai (`author`)** | Mahasiswa sarjana tahun akhir (semester $\ge 5$) atau pascasarjana aktif di $\ge 3$ perguruan tinggi Indonesia; berusia $\ge 18$ tahun. | $\approx 150\text{–}200$ kontributor (menghasilkan `200` esai `academic`). | Pengumuman terbuka melalui papan informasi akademik dan saluran resmi program studi. | Dosen pengampu mata kuliah **JANGAN** merekrut langsung mahasiswa di kelas yang sedang dinilai olehnya; partisipasi atau penolakan **JANGAN** memengaruhi nilai akademik mahasiswa. |
| **2. Anotator Korpus (`annotator`)** | Lulusan S1/mahasiswa S2 bidang Linguistik, Ilmu Komputer, Hukum, atau Kebijakan Publik yang lulus uji kalibrasi ($\alpha_{\text{Krip}} \ge 0.75$). | `3` orang anotator. | Seleksi terbuka kontrak asisten peneliti paruh waktu. | Kompensasi dibayarkan berdasarkan jumlah dokumen selesai sesuai standar honorarium riset institusi (`TODO(isi nominal honorarium per dokumen)`), bukan berdasarkan kecocokan dengan hipotesis peneliti. |
| **3. Pakar Penilai (`reviewer`)** | Dosen menulis akademik/logika kritis atau analis kebijakan senior dengan pengalaman $\ge 5$ tahun. | `3` orang pakar domain. | Undangan profesional resmi lintas institusi. | Penilaian dilakukan secara *blind* tanpa mengetahui apakah skor pembanding berasal dari baseline atau model Argumind (`→ research/METHODOLOGY.md#2c-variabel-untuk-rq3`). |

---

## 3. *Informed Consent* (Persetujuan Setelah Penjelasan) dan Lokasi Arsip

1. **Mekanisme Pengumpulan Persetujuan:**
   - **Digital (Via Platform):** Saat `author` mengunggah draf pada halaman `/dashboard` (`P-02`), kotak centang `research_opt_in` secara *default* bernilai **`false` (tidak tercentang)** (`→ docs/DATA_MODEL.md#13-documents-dokumen-induk`). Pengguna yang ingin berkontribusi ke korpus riset WAJIB membuka lembar penjelasan dan mencentang `research_opt_in = true` secara sadar (*explicit opt-in*).
   - **Tertulis (Anotator & Pakar):** Anotator dan pakar menandatangani formulir *Informed Consent* dan Perjanjian Kerahasiaan Data (*Non-Disclosure Agreement* / NDA) sebelum diberi akses peran di sistem.
2. **Isi Wajib Lembar Penjelasan:**
   - Tujuan riset, cara kerja redaksi identitas (`[REDACTED_*]`), penggunaan teks untuk pelatihan model dan rilis dataset akademik (`CC BY-NC-SA 4.0`), serta hak mencabut persetujuan kapan saja sebelum pembekuan rilis dataset.
3. **Lokasi Arsip *Informed Consent*:**
   - Bukti persetujuan digital dicatat di tabel audit database (`timestamp`, `user_id`, versi teks *consent*) dan salinan PDF formulir bertanda tangan disimpan di folder terenkripsi terpisah milik Peneliti Utama (`research/ethics_archive/`, **di luar repositori Git** dan hanya dapat diakses oleh Peneliti Utama serta auditor Komisi Etik).

---

## 4. Tata Kelola Data Pribadi (Kepatuhan UU No. 27 Tahun 2022 — UU PDP)

*(Catatan: Interpretasi operasional di bawah ini merujuk pada prinsip Undang-Undang Nomor 27 Tahun 2022 tentang Pelindungan Data Pribadi di Indonesia; kepatuhan legal formal memerlukan verifikasi pejabat pelindung data institusi).*

| Aspek Tata Kelola PII | Aturan Konkret & Implementasi Teknis (`→ docs/DATA_MODEL.md` & `→ research/DATASET.md`) |
|---|---|
| **Jenis Data Pribadi (PII) yang Terkumpul** | Data Pribadi Umum: `users.full_name`, `users.email`, `users.external_identity_id` (NIM/NIP), afiliasi institusi, serta potensi nama diri yang tertulis di dalam berkas asli (`raw_s3_key`). Penelitian ini **JANGAN** mengumpulkan Data Pribadi Spesifik/Sensitif (kesehatan, biometrik, keuangan pribadi, catatan kejahatan). |
| **Tujuan Pemrosesan** | 1. Manajemen akun dan kuota aplikasi.<br>2. Pembentukan *group-stratified split* (`anon_author_id`) agar dua esai dari penulis yang sama tidak bocor antara partisi `train` dan `test`.<br>3. Audit keabsahan *informed consent*. |
| **Dasar Hukum Pemrosesan** | Persetujuan eksplisit yang sah dari Subjek Data (*Explicit Consent*, Pasal 20 ayat (2) huruf a UU PDP) melalui mekanisme `research_opt_in = true` yang tidak digabungkan secara paksa dengan syarat penggunaan dasar aplikasi. |
| **Prosedur Anonimisasi & Pseudonimisasi** | 1. **Teks Esai (`clean_text`):** Melewati Tahap 2 `pii_redaction` otomatis + verifikasi manual 100% yang mengganti nama, NIM, email, telepon, dan institusi penulis dengan `[REDACTED_NAME]`, `[REDACTED_ID]`, `[REDACTED_EMAIL]`.<br>2. **ID Penulis (`anon_author_id`):** Diganti dengan hash satu arah `HMAC-SHA256(user_id, CORPUS_SALT)` (`^anon_author_[a-f0-9]{12}$`). Kunci `CORPUS_SALT` disimpan terpisah dari dataset rilis. |
| **Batas Retensi Data** | 1. Berkas mentah pra-redaksi (`raw_s3_key` di `EXT-STORAGE` dan `research/data/raw/`) disimpan maksimal hingga verifikasi *ethical audit* publikasi selesai (`ASUMSI: maksimal 12 bulan` sejak pengumpulan, atau `30 hari` untuk pengguna non-riset sesuai `TODO(Q-DATA-01)`), lalu dihapus permanen.<br>2. Korpus teranonimisasi (`research/data/processed/v1.0/`) disimpan permanen untuk reprodusibilitas ilmiah karena sudah tidak memuat PII. |
| **Pembatasan Akses** | Hanya Peneliti Utama dan `org_admin` dengan MFA (`TOTP`) aktif yang memiliki akses ke tabel pemetaan identitas asli (`→ docs/ROLES_PERMISSIONS.md#4-spesifikasi-autentikasi--manajemen-sesi`). `annotator` hanya melihat `clean_text`. |
| **Prosedur Penghapusan (*Right to Erasure*)** | Kontributor berhak meminta penarikan esai melalui tombol `"Cabut Izin Riset"` atau email ke Peneliti Utama. Sistem WAJIB menghapus rekaman dari `documents`, `raw_s3_key`, dan `research/data/interim/` dalam waktu $\le 3 \times 24\text{ jam}$ (72 jam) kerja. |

---

## 5. Risiko bagi Partisipan dan Strategi Mitigasi

| ID Risiko Etik | Deskripsi Risiko bagi Partisipan | Tingkat Risiko | Mitigasi Wajib (`WAJIB` / `JANGAN`) |
|---|---|---|---|
| **RE-01** | **De-anonimisasi tidak sengaja** dari detail kasus spesifik yang ditulis mahasiswa di dalam esai. | Sedang | Selain regex/NER otomatis pada Tahap 2 `pii_redaction`, anotator pada `F-06` WAJIB menandai segmen yang masih mengandung petunjuk identitas pribadi untuk disamarkan sebelum masuk ke `processed/v1.0/`. |
| **RE-02** | **Dampak akademik merugikan (*Automated Grading Harm*)** jika dosen memakai skor diagnostik Argumind sebagai nilai ujian/tugas secara mentah. | Tinggi | 1. Sistem WAJIB menampilkan banner peringatan tetap di `P-03` bahwa skor bersifat diagnostik.<br>2. Selama fase penelitian, skor eksperimen model **JANGAN** diserahkan kepada dosen pengampu sebagai komponen nilai mata kuliah mahasiswa (`→ docs/PRD.md#4-ruang-lingkup-produk`). |
| **RE-03** | **Kebocoran draf belum dipublikasikan** ke penyedia LLM eksternal. | Sedang | Pemanggilan `EXT-LLM` WAJIB menggunakan model *self-hosted* (`vLLM`) atau endpoint dengan kontrak *zero data retention* (`→ docs/ARCHITECTURE.md#1-konteks-sistem-aktor-dan-sistem-eksternal`). |
| **RE-04** | **Kelelahan kognitif (*Cognitive Fatigue*)** pada anotator saat menganotasi teks panjang. | Rendah | Batasi kuota kerja anotator maksimal `8` dokumen (`~10.000` kata) per hari kerja dengan jeda istirahat wajib. |

---

## 6. Deklarasi Konflik Kepentingan dan Sumber Pendanaan

1. **Konflik Kepentingan (*Conflict of Interest*):**
   - Tim peneliti mengembangkan platform `Argumind` baik sebagai artefak penelitian ilmiah maupun sebagai prototipe produk perangkat lunak (`→ 3_rekomendasi_projek_cognitive_intelligence.md`).
   - Untuk mencegah bias evaluasi akibat kepentingan komersial: (a) seluruh penilaian pakar pada `test set` ($n = 60$) dilakukan oleh 3 pakar independen secara *blind*, (b) seluruh percobaan yang gagal atau menghasilkan hasil negatif WAJIB dicatat tanpa sensor di `→ research/EXPERIMENT_LOG.md`, dan (c) hubungan pengembangan produk WAJIB dideklarasikan secara eksplisit pada bagian *Competing Interests* di naskah jurnal.
2. **Sumber Pendanaan (*Funding*):**
   -Sumber pendanaan riset dan komputasi: `TODO(isi nama skema hibah penelitian / pendanaan internal institusi beserta nomor kontrak hibah; jika mandiri, tulis "Penelitian ini didanai secara mandiri oleh tim penulis tanpa hibah eksternal")`.

---

## 7. Pertanyaan Terbuka

1. `TODO(Q-ETH-01 — Nomor Protokol KEPK/IRB)`: Mohon masukkan nama lembaga Komisi Etik dan nomor surat pengajuan/persetujuan kelaikan etik begitu dokumen diajukan.
2. `TODO(Q-ETH-02 — Deklarasi Pendanaan)`: Mohon konfirmasi teks resmi sumber pendanaan (*funding acknowledgment*) yang akan dicantumkan pada naskah publikasi.
