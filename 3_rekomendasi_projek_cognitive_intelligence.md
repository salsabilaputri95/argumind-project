# Blueprint Bisnis & Penelitian: 3 Projek Rekomendasi Cognitive Intelligence (Text & Data-Based)

Dokumen ini disusun berdasarkan analisis terhadap 7 ide pada [7_ide_cognitive_intelligence_text_data_based.md](file:///d:/New%20folder%20(2)/7_ide_cognitive_intelligence_text_data_based.md) dengan menggabungkan kerangka **Tech Leadership / Bisnis** (validasi masalah, unit economics, risiko keamanan & privasi, *human-in-the-loop*, dan kriteria *go/no-go*) serta kerangka **Academic Research** (*chain of claims*, desain studi, operasionalisasi metrik, ancaman validitas, dan etika riset).

> [!IMPORTANT]
> **Disiplin Fakta vs Asumsi:** Skor prioritas pada dokumen sumber merupakan estimasi strategis, bukan hasil uji pasar atau survei *willingness-to-pay*. Seluruh angka pasar, regulasi spesifik (seperti kepatuhan UU PDP / aturan sektoral), dan referensi literatur tahun 2025–2026 yang dikutip dari dokumen sumber berstatus **Memerlukan Verifikasi (`This needs verification`)** sebelum dijadikan dasar klaim komersial maupun naskah ilmiah.

---

## Ringkasan Seleksi: Mengapa 3 Projek Ini?

Dari 7 kandidat ide, **EpistemicGate**, **Argumind**, dan **CalibraMind** dipilih karena membentuk portofolio yang saling melengkapi secara teknologi (*shared NLP + Knowledge Graph + Bayesian stack*) namun menyasar tiga risiko/kebutuhan berbeda:

| Peringkat | Projek | Peran Strategis | Keunggulan Bisnis | Keunggulan Penelitian | Risiko Terbesar & Kunci Mitigasi |
|---|---|---|---|---|---|
| **1** | **EpistemicGate** | *Commercial Anchor* (B2B/B2G Trust) | Urgensi tinggi akibat adopsi LLM; *buyer* jelas (Audit, Legal, Risk, Compliance). | Ruang riset kuat di *claim-level NLI*, *provenance*, dan *human-AI reliance calibration*. | Biaya token/latensi & akurasi pada dokumen kompleks → gunakan arsitektur hibrida (IndoBERT/NLI lokal + LLM selektif). |
| **2** | **Argumind** | *Fastest Research-to-Product* (EdTech & Policy) | MVP paling ringan; tidak butuh integrasi sistem inti perusahaan untuk mulai; data teks publik melimpah. | *Novelty* tinggi untuk *Indonesian implicit premise detection* & *explainable argument mining*. | *Willingness-to-pay* sektor pendidikan terbatas → masuk lewat lisensi institusi/kampus + segmen konsultan/legal. |
| **3** | **CalibraMind** | *High-Impact Decision Science* (Risk & Ops) | *Retention* tinggi jika terikat pada metrik proyek/risiko; *switching cost* kuat karena data historis. | Eksperimen kuantitatif bersih (Brier score, kurva kalibrasi, intervensi Bayesian). | Hambatan budaya (*high power distance*: eksekutif enggan "dinilai terlalu percaya diri") → posisikan untuk *estimasi proyek/risiko*, bukan penilaian personal atasan. |

**Mengapa bukan 4 ide lainnya?**
- **MemoryLoop** mudah dijual (L&D/SOP), tetapi *novelty* penelitiannya lebih sempit (*spaced repetition* sudah sangat matang) kecuali digabung dengan evaluasi transfer kasus nyata.
- **FlowCognition** bernilai kontrak besar, tetapi friksi integrasi data (*event log* ERP/sistem internal) dan risiko persepsi pengawasan karyawan (*employee surveillance*) terlalu berat untuk tahap awal.
- **GroupMind** dan **TaskWeave** menarik, tetapi perilaku adopsi rapat/perencanaan sangat sulit diukur *ROI*-nya secara cepat dibanding verifikasi dokumen (EpistemicGate), penilaian tulisan/argumen (Argumind), atau akurasi prediksi numerik (CalibraMind).

---

## Projek 1: EpistemicGate — *AI Evidence Verification & Epistemic Intelligence Platform*

### A. Aspek Bisnis & Tech Leadership

1. **Masalah Bisnis & ICP (Ideal Customer Profile)**
   - **Masalah:** Organisasi makin banyak memakai LLM dan dokumen eksternal untuk membuat laporan, kajian kebijakan, analisis risiko, dan draf legal. Risiko utamanya bukan salah ketik, melainkan *halusinasi yang terdengar meyakinkan* dan kutipan fiktif/tidak relevan.
   - **ICP Awal:** Tim Audit Internal, Compliance, Legal, Risk Management, serta unit Riset/Kebijakan di perusahaan finansial, konsultan, BUMN, atau instansi pemerintah Indonesia.
   - **Buyer vs User:** *Buyer* = Head of Risk/Compliance/Legal atau CTO/CIO; *User* = Auditor, analis, peneliti, dan staf penyusun laporan.

2. **Fakta, Asumsi, & Pertanyaan Validasi**
   - **Fakta (dari konteks dokumen):** Sistem berbasis teks/dokumen tanpa sensor fisik; fokus pada pemecahan dokumen menjadi klaim individual dan pelacakan bukti.
   - **Asumsi:** Perusahaan di Indonesia bersedia membayar untuk alat verifikasi klaim terpisah di luar fitur *built-in* penyedia LLM global.
   - **Pertanyaan Kritis (Customer Discovery):** Seberapa sering tim audit/legal menemukan klaim tanpa bukti pada laporan internal? Apakah mereka bersedia mengunggah dokumen sensitif ke *cloud*, atau wajib *on-premise*?

3. **Alternatif Non-AI & Moat (Diferensiasi)**
   - **Alternatif Non-AI:** *Checklist* audit manual, *peer review* berjenjang, pencarian kata kunci CTRL+F. Kelemahannya: lambat dan tidak skalabel untuk dokumen 50–200 halaman.
   - **Diferensiasi:** Pemetaan granular **per klaim** (bukan skor umum satu dokumen), deteksi klaim yang benar secara umum tetapi **tidak didukung sumber yang dicantumkan**, serta dukungan penuh korpus dan konteks regulasi Bahasa Indonesia dengan opsi *on-premise*.

4. **Model Operasi AI & Data (Human-in-the-Loop)**
   - **Batas Otonomi:** Sistem bertindak sebagai *decision-support* (penanda risiko dan pelacak bukti), **bukan** pemutus otomatis kepatuhan legal.
   - **Alur Kerja:** `Dokumen (PDF/DOCX) -> Ekstraksi Klaim -> Pencarian Bukti (RAG/Internal Repo) -> NLI (Entailment / Contradiction / Neutral) -> Skor Ketidakpastian -> Tinjauan Auditor`.
   - **Efisiensi Biaya:** Gunakan model NLI/encoder kecil (mis. IndoBERT yang di-*fine-tune*) untuk penyaringan awal, dan panggil LLM hanya untuk klaim ambigu guna menekan biaya API.

5. **Risiko Utama & Mitigasi**
   - **Kebocoran Data & Privasi (UU PDP):** Dokumen audit/legal sangat rahasia. *Mitigasi:* Arsitektur *tenant isolation*, enkripsi *at-rest/in-transit*, opsi deployment *on-premise*/VPC privat, tanpa *training* ulang pada data klien (*zero data retention*). *(Kepatuhan spesifik UU PDP memerlukan verifikasi hukum).*
   - **Prompt Injection:** Dokumen yang diunggah dapat berisi teks tersembunyi untuk memanipulasi hasil verifikasi. *Mitigasi:* Sanitasi teks input, pemisahan ketat *system prompt* dan *untrusted document context*, serta verifikasi silang berbasis aturan/NLI non-generatif.
   - **Over-reliance (Ketergantungan Berlebih):** Pengguna percaya 100% pada label "Terverifikasi". *Mitigasi:* Tampilkan potongan bukti asli (*verbatim snippet*) dan skor ketidakpastian, bukan hanya label biner.

6. **MVP, Monetisasi, & Kriteria Go/No-Go**
   - **MVP (8–10 minggu):** Unggah PDF/DOCX + repositori dokumen pembanding, ekstraksi klaim, verifikasi NLI dasar, penyorotan kontradiksi/klaim tanpa bukti, dan ekspor laporan audit.
   - **Monetisasi:** B2B SaaS berbasis kuota dokumen/halaman (*tiered*) + paket *Enterprise On-Premise* (lisensi tahunan + jasa *setup* awal).
   - **Kriteria Go/No-Go (Bulan ke-3):** Lanjutkan ke fase komersial penuh jika ≥ 3 organisasi pilot bersedia menandatangani LOI/uji coba berbayar dan waktu verifikasi dokumen analis berkurang ≥ 30% dengan tingkat kesalahan kritis (*false negative* pada klaim fiktif) di bawah ambang batas yang disepakati pengguna.

### B. Aspek Penelitian & Validasi Empiris

1. **Chain of Claims**
   - **Problem:** Output LLM dan dokumen profesional sering mengandung klaim yang tampak meyakinkan namun tidak memiliki dasar bukti memadai (*epistemic mismatch*).
   - **Literature Gap:** Sebagian besar riset NLI dan *fact-checking* berfokus pada bahasa Inggris dan fakta ensiklopedis (Wikipedia), bukan dokumen operasional/audit berbahasa Indonesia dengan sitasi internal, serta jarang mengukur dampaknya terhadap kalibrasi kepercayaan pengguna.
   - **Research Question (RQ):**
     - *RQ1:* Seberapa akurat model ekstraksi klaim dan NLI berbasis *evidence provenance* dalam mendeteksi klaim tak berdasar pada dokumen Bahasa Indonesia?
     - *RQ2:* Apakah penyajian skor ketidakpastian dan *provenance* meningkatkan kalibrasi kepercayaan (*reliance calibration*) pengguna dibanding antarmuka verifikasi standar?

2. **Desain Penelitian & Inferensi**
   - **Tahap 1 (Komputasional / Evaluasi Model):** Studi komparatif (*benchmarking*) antara *zero-shot LLM*, *RAG standar*, dan arsitektur *Claim-Level NLI + Provenance* pada korpus dokumen beranotasi.
   - **Tahap 2 (Kuasi-Eksperimen / Eksperimen Terkontrol):** *Between-subjects* (Kelompok A: membaca dokumen + skor ringkas; Kelompok B: membaca dokumen + EpistemicGate *claim-level provenance*) untuk mengukur inferensi kausal terhadap kualitas deteksi kesalahan dan kalibrasi kepercayaan manusia.

3. **Data, Pengukuran, & Analisis**
   - **Data:** Korpus publik Bahasa Indonesia (mis. laporan tahunan perusahaan terbuka, kajian kebijakan publik, putusan/dokumen regulasi terbuka) + klaim sintetis yang dimodifikasi (*adversarial/ungrounded claims*).
   - **Metrik Teknis:** Precision/Recall/F1 ekstraksi klaim, Macro-F1 klasifikasi NLI (*Supported, Refuted, Not Enough Evidence*), dan *Citation Faithfulness*.
   - **Metrik Kognitif/Perilaku:** Akurasi deteksi klaim bermasalah oleh manusia, waktu verifikasi, dan *Appropriate Reliance Rate* (kapan pengguna menerima klaim benar dan menolak klaim salah).
   - **Reliabilitas Anotasi:** Minimal 2–3 anotator manusia dengan target *inter-annotator agreement* (Krippendorff's α atau Cohen's κ ≥ 0,75).

4. **Ancaman Validitas & Etika**
   - **Validitas Eksternal:** Dokumen publik mungkin lebih rapi daripada dokumen internal perusahaan yang penuh tabel kompleks. *Mitigasi:* Sertakan variasi format teks-tabel dalam set uji.
   - **Etika Riset:** Anonimisasi data responden eksperimen, *informed consent*, dan tidak menggunakan dokumen rahasia tanpa izin tertulis.
   - **Target Publikasi:** Jurnal/konferensi NLP terapan atau sistem informasi (mis. *Information Processing & Management*, *EMNLP/ACL Industry Track*, atau jurnal terakreditasi SINTA 1/Q1 terkait). *(Status dan cakupan jurnal memerlukan verifikasi saat pengajuan).*

---

## Projek 2: Argumind — *AI Argumentation & Critical Reasoning Intelligence*

### A. Aspek Bisnis & Tech Leadership

1. **Masalah Bisnis & ICP**
   - **Masalah:** Banyak laporan analisis bisnis, kebijakan publik, maupun tugas akademik terlihat rapi secara tata bahasa tetapi rapuh secara logika (melompat ke kesimpulan, menyembunyikan asumsi, mengabaikan penjelasan alternatif, atau mengandung *logical fallacy*).
   - **ICP Awal:**
     1. *Beachhead (Mudah Masuk):* Perguruan tinggi (fakultas hukum, ekonomi, ilmu sosial, pascasarjana) dan lembaga pelatihan/persiapan tes berpikir kritis.
     2. *Ekspansi B2B:* Tim strategi/kebijakan, konsultan, dan analis riset pasar.

2. **Fakta, Asumsi, & Pertanyaan Validasi**
   - **Fakta:** MVP hanya membutuhkan input teks; tersedia dukungan model dasar seperti IndoBERT dan LLM; tanpa ketergantungan perangkat keras khusus.
   - **Asumsi:** Dosen/institusi atau manajer analis mau mengadopsi sistem evaluasi argumen berbasis AI sebagai pendamping penilaian, bukan sekadar memakai *chatbot* umum (ChatGPT/Claude).
   - **Pertanyaan Kritis:** Apakah pengguna lebih membutuhkan *penilaian/rubrik otomatis* atau *peta visual celah argumen & kontraargumen* untuk memperbaiki draf sebelum dikumpulkan?

3. **Alternatif Non-AI & Moat (Diferensiasi)**
   - **Alternatif Non-AI:** Rubrik penilaian manual, *peer review* diskusi kelas.
   - **Diferensiasi vs LLM Umum:** *Chatbot* umum cenderung memberi masukan naratif yang tidak konsisten dan mudah terpengaruh gaya bahasa. Argumind memetakan struktur **Klaim → Premis Eksplisit/Implisit → Bukti → Celah Logika → Kontraargumen** secara terstruktur dan terukur dengan rubrik yang konsisten.

4. **Model Operasi AI & Data**
   - **Batas Otonomi:** Argumind memberi *skor diagnostik dan penjelasan alasan* (*explainable feedback*); keputusan nilai akhir atau persetujuan laporan tetap di tangan manusia.
   - **Arsitektur Ringkas:** `Input Teks -> Segmentasi Klaim & Premis (Argument Mining) -> Deteksi Premis Implisit & Stance -> Evaluasi Kekuatan Bukti -> Pembangkitan Kontraargumen Terarah`.

5. **Risiko Utama & Mitigasi**
   - **Bias Penilaian & Ketidaksetiaan Penjelasan (Unfaithful Explanations):** LLM memberi skor tinggi/rendah tetapi alasannya tidak selaras dengan skor. *Mitigasi:* Pisahkan modul ekstraksi struktur argumen (deterministik/terlatih) dari modul penjelas, dan uji *faithfulness* penjelasan.
   - **Risiko Komersial (Segmen Pendidikan):** Anggaran kampus sering lambat dan terbatas. *Mitigasi:* Gunakan model *freemium* untuk dosen/peneliti individu sebagai corong adopsi, lalu jual lisensi institusi/departemen atau paket *enterprise* untuk tim konsultan/kebijakan.

6. **MVP, Monetisasi, & Kriteria Go/No-Go**
   - **MVP (6–8 minggu):** Antarmuka tempel teks/dokumen, visualisasi graf klaim-premis-bukti, daftar potensi celah penalaran/asumsi tersembunyi, dan generator kontraargumen.
   - **Monetisasi:** Lisensi SaaS per institusi/kursi (*seat*), API integrasi LMS/platform menulis, serta layanan analisis laporan kebijakan.
   - **Kriteria Go/No-Go (Bulan ke-3):** ≥ 50 pengguna aktif mingguan (dosen/analis/mahasiswa pascasarjana) dengan tingkat retensi minggu ke-4 ≥ 25% dan persetujuan pakar terhadap kualitas pemetaan argumen ≥ 75%.

### B. Aspek Penelitian & Validasi Empiris

1. **Chain of Claims**
   - **Problem:** Evaluasi kualitas tulisan analitis dan kebijakan dalam Bahasa Indonesia masih sangat manual dan subjektif, terutama dalam mendeteksi asumsi yang tidak dinyatakan (*implicit premises*).
   - **Literature Gap:** Riset *computational argumentation* didominasi bahasa Inggris (debat daring, esai TOEFL/GRE). Dataset dan metode *implicit premise detection* serta *explainable argument scoring* untuk teks argumentatif Bahasa Indonesia masih sangat terbatas.
   - **Research Question (RQ):**
     - *RQ1:* Bagaimana performa pendekatan hibrida (*Argument Mining + NLI + LLM*) dalam mengekstrak struktur argumen dan premis implisit pada teks berbahasa Indonesia?
     - *RQ2:* Seberapa setia (*faithful*) dan selaras penilaian kualitas argumen otomatis Argumind terhadap rubrik pakar manusia?

2. **Desain Penelitian & Inferensi**
   - **Tahap 1 (Pengembangan Dataset & Model):** Pembuatan korpus argumen Bahasa Indonesia beranotasi (esai mahasiswa/kebijakan/opini) + eksperimen ablasi model (*IndoBERT* vs *LLM prompting* vs *Graph-enhanced model*).
   - **Tahap 2 (Studi Validasi Penilaian):** Korelasi dan kesepakatan antara skor Argumind dengan penilaian *blind* oleh minimal 2–3 pakar/dosen (inferensi deskriptif-asosiasional & validitas konstruk).

3. **Data, Pengukuran, & Analisis**
   - **Metrik Teknis:** F1-score identifikasi komponen argumen (Klaim, Premis), F1 relasi (*Support/Attack*), *Semantic Similarity* / evaluasi manusia untuk ketepatan premis implisit.
   - **Metrik Kualitas Penilaian:** Korelasi Pearson/Spearman dan Quadratic Weighted Kappa (QWK) antara skor sistem dan skor pakar manusia.
   - **Audit Keadilan (Fairness):** Uji apakah panjang teks atau gaya bahasa memengaruhi skor secara tidak semestinya (*length bias check*).

4. **Ancaman Validitas & Etika**
   - **Construct Validity:** "Kualitas argumen" bisa berbeda antara domain hukum, bisnis, dan akademik. *Mitigasi:* Batasi domain awal pada satu/dua genre (mis. esai kebijakan & analisis bisnis) dengan rubrik yang jelas.
   - **Etika:** Jika menggunakan esai mahasiswa, wajib anonimisasi penuh, persetujuan tertulis (*opt-in*), dan larangan menggunakan sistem sebagai penentu tunggal kelulusan.
   - **Target Publikasi:** Konferensi/jurnal *Computational Linguistics*, *Argumentation*, atau *AI in Education* (mis. *Workshop on Argument Mining*, *IJAIED*, *IPM*). *(Cakupan jurnal memerlukan verifikasi).*

---

## Projek 3: CalibraMind — *Human Judgment & Probabilistic Forecasting Intelligence*

### A. Aspek Bisnis & Tech Leadership

1. **Masalah Bisnis & ICP**
   - **Masalah:** Keputusan strategis dan operasional (estimasi waktu proyek IT, proyeksi penjualan, penilaian risiko kredit/kegagalan sistem) sering meleset karena *overconfidence bias* dan tidak adanya umpan balik historis atas akurasi prediksi tim.
   - **ICP Awal (Re-framing Kritis):** Jangan menjual produk ini sebagai "alat mendeteksi manajer yang terlalu percaya diri" (berisiko tinggi ditolak secara politis dalam budaya organisasi hierarkis). Posisikan sebagai **Platform Akurasi Estimasi Proyek, Risiko Operasional, & Forecasting Bisnis** untuk:
     - PMO (Project Management Office) / Engineering Leaders (estimasi jadwal & risiko rilis).
     - Tim Risk Management & Underwriting (asuransi/perbankan/fintech).
     - Konsultan strategi & tim *revenue operations*.

2. **Fakta, Asumsi, & Pertanyaan Validasi**
   - **Fakta:** Menggunakan pendekatan statistik Bayesian, *Brier score / Log score*, dan pelacakan histori prediksi terhadap realisasi tanpa sensor fisik.
   - **Asumsi:** Organisasi memiliki cukup banyak kejadian berulang yang dapat diverifikasi hasilnya dalam 1–3 bulan (agar siklus umpan balik kalibrasi berjalan).
   - **Pertanyaan Kritis:** Jenis keputusan apa di perusahaan target yang hasilnya bisa diketahui dalam 30–90 hari (bukan 5 tahun), sehingga skor kalibrasi bisa terasa manfaatnya dengan cepat?

3. **Alternatif Non-AI & Moat (Diferensiasi)**
   - **Alternatif Non-AI:** Spreadsheet Excel, *post-mortem* rapat proyek. Kelemahan: tidak menghitung kalibrasi probabilistik secara sistematis dan jarang melacak tingkat keyakinan (*confidence level*) awal.
   - **Diferensiasi:** Menggabungkan **LLM untuk memecah masalah kabur menjadi pertanyaan prediktif yang terukur (*resolvable questions*)** dengan **Hierarchical Bayesian Calibration** untuk mengoreksi bias estimasi tim dan menggabungkan prediksi kolektif berdasarkan rekam jejak akurasi.

4. **Model Operasi AI & Data**
   - **Batas Otonomi:** LLM membantu merumuskan pertanyaan prediksi dan memetakan *base rate* historis; model statistik menghitung skor Brier/kalibrasi; keputusan bisnis tetap milik tim.
   - **Privasi & Keamanan:** Data prediksi internal (target penjualan, risiko kegagalan proyek) sangat sensitif. Terapkan agregasi tingkat tim/peran untuk pelaporan manajemen agar individu tidak merasa "dihukum" saat melatih kalibrasi mereka.

5. **Risiko Utama & Mitigasi**
   - **Cold-Start Data:** Di awal pemakaian, belum ada histori prediksi yang selesai (*resolved*). *Mitigasi:* Mulai dengan *onboarding* latihan kalibrasi (*calibration training*) memakai kasus historis/domain publik sebelum masuk ke proyek live, serta fokus pada prediksi jangka pendek (2–8 minggu).
   - **Gaming the System:** Karyawan memberi probabilitas 50% terus-menerus agar terlihat aman. *Mitigasi:* Gunakan *proper scoring rules* (Brier score & Log score) yang secara matematis memberi insentif pada pelaporan keyakinan yang jujur, serta fokuskan KPI pada *perbaikan tim*, bukan hukuman individu.

6. **MVP, Monetisasi, & Kriteria Go/No-Go**
   - **MVP (6–8 minggu):** Pembuat pertanyaan prediksi berbantuan LLM, input probabilitas + alasan singkat, pelacakan tenggat resolusi, perhitungan otomatis Brier Score & kurva kalibrasi, serta dasbor bias (*overconfident* vs *underconfident*).
   - **Monetisasi:** B2B SaaS per tim/organisasi, paket *enterprise risk forecasting*, dan modul pelatihan kalibrasi korporat.
   - **Kriteria Go/No-Go (Bulan ke-3):** Minimal 2–3 tim pilot mencatat ≥ 100 prediksi teresolusi dalam 90 hari dan menunjukkan peningkatan keterlibatan (*weekly active forecasters* ≥ 60%).

### B. Aspek Penelitian & Validasi Empiris

1. **Chain of Claims**
   - **Problem:** Pengambil keputusan organisasi sering menunjukkan ketidaksesuaian antara keyakinan subjektif (*subjective confidence*) dan akurasi objektif (*actual realization*).
   - **Literature Gap:** Studi kalibrasi skala besar umumnya dilakukan pada platform *crowdsourced forecasting* publik (seperti Metaculus/Good Judgment), bukan pada konteks operasional organisasi Indonesia atau menguji intervensi umpan balik Bayesian adaptif secara longitudinal.
   - **Research Question (RQ):**
     - *RQ1:* Bagaimana profil kalibrasi dan kecenderungan bias (*overconfidence/underconfidence*) praktisi/analis pada tugas estimasi organisasi?
     - *RQ2:* Apakah intervensi umpan balik kalibrasi adaptif berbasis model Bayesian menurunkan *Brier Score* dan *Expected Calibration Error (ECE)* pada putaran prediksi berikutnya?

2. **Desain Penelitian & Inferensi**
   - **Desain:** *Longitudinal Randomized Controlled Trial (RCT)* atau kuasi-eksperimen *pre-post with control group* (mis. mahasiswa pascasarjana manajemen/teknik atau analis perusahaan selama 8–12 minggu).
   - **Kelompok Perlakuan:** Mendapat umpan balik kurva kalibrasi historis + koreksi Bayesian adaptif; **Kelompok Kontrol:** Hanya mencatat prediksi dan melihat hasil akhir tanpa analisis kalibrasi.

3. **Data, Pengukuran, & Analisis**
   - **Variabel Utama:** Probabilitas prediksi ($p \in [0,1]$), realisasi biner ($y \in \{0,1\}$), alasan tekstual, dan waktu penyelesaian.
   - **Metrik Evaluasi:** Brier Score (diuraikan menjadi *Reliability, Resolution, Uncertainty*), Log Score, Expected Calibration Error (ECE), serta analisis regresi/model hierarkis Bayesian untuk melihat tren perbaikan antarwaktu.

4. **Ancaman Validitas & Etika**
   - **Attrition / Drop-out:** Peserta berhenti mencatat prediksi sebelum eksperimen selesai. *Mitigasi:* Desain tugas prediksi jangka pendek (mingguan) dengan pengingat ringan.
   - **Etika:** Data performa prediksi individu harus dirahasiakan dari atasan langsung selama masa studi agar tidak menimbulkan tekanan psikologis atau bias kepatuhan.
   - **Target Publikasi:** Jurnal/konferensi *Decision Analysis*, *Judgment and Decision Making*, *Management Science*, atau *Human-Computer Interaction* (CHI/CSCW). *(Cakupan jurnal memerlukan verifikasi).*

---

## Arsitektur Bersama & Roadmap Eksekusi (0–6 Bulan)

Agar pengembangan efisien secara biaya dan tim (prinsip *shared platform engineering*), ketiga produk tidak dibangun dari nol secara terpisah, melainkan memakai **Fondasi Cognitive Intelligence Engine** yang sama:

| Lapisan | Komponen Bersama | Penggunaan Spesifik |
|---|---|---|
| **Core Backend & Data** | Python (FastAPI), PostgreSQL + `pgvector`, Redis/Celery | Manajemen dokumen, antrean pemrosesan asinkron, pencarian semantik. |
| **NLP & Reasoning** | IndoBERT / Sentence-Transformers + LLM Gateway (abstraksi model lokal & API) | *Claim extraction* (EpistemicGate), *Argument mining* (Argumind), *Question decomposition* (CalibraMind). |
| **Knowledge & Probabilistic** | Neo4j (opsional saat skala naik) + Scikit-learn / PyMC / PyTorch | Graf bukti & argumen; model *Bayesian calibration* & Brier score. |
| **Frontend & Observability** | Next.js (TypeScript, Tailwind), Prometheus/Grafana, Audit Log | Antarmuka *human-in-the-loop*, pelacakan latensi, biaya token, dan *audit trail*. |

### Roadmap Paralel (Bisnis + Riset)

- **Bulan 1 (Validasi Masalah & Desain Riset):**
  - *Bisnis:* Lakukan 10–15 wawancara *customer discovery* untuk **EpistemicGate** (Audit/Legal/Risk) dan **Argumind** (Kampus/Kebijakan) guna memvalidasi masalah dan kebutuhan *on-premise*.
  - *Riset:* Finalisasi protokol anotasi, *rubric*, dan pengajuan izin etik (*IRB/ethical clearance*) untuk pengumpulan dataset **Argumind** & **EpistemicGate**.
- **Bulan 2–3 (MVP #1 & Studi Awal):**
  - *Bisnis & Teknis:* Bangun Core Engine + MVP **EpistemicGate** (prioritas komersial) dan prototipe ringan **Argumind** (untuk pengumpulan data riset).
  - *Riset:* Anotasi korpus argumen/klaim Bahasa Indonesia, hitung reliabilitas anotator ($\kappa / \alpha \ge 0{,}75$), jalankan *benchmark* model awal.
- **Bulan 4–5 (Pilot B2B & Eksperimen Empiris):**
  - *Bisnis:* Jalankan pilot **EpistemicGate** di 2–3 tim/organisasi; luncurkan beta **Argumind** di lingkungan kampus/komunitas analis.
  - *Riset:* Jalankan kuasi-eksperimen *reliance calibration* (EpistemicGate) dan uji validasi skor pakar (Argumind). Mulai *pilot study* **CalibraMind** pada estimasi proyek/risiko.
- **Bulan 6 (Evaluasi Go/No-Go & Penulisan Publikasi):**
  - *Bisnis:* Evaluasi metrik konversi pilot ke kontrak berbayar, tinjau ulang unit economics (biaya token per dokumen), dan putuskan skala produk pemenang.
  - *Riset:* Selesaikan analisis statistik dan draf 1–2 manuskrip ilmiah pertama dari data eksperimen yang sudah terkumpul.
