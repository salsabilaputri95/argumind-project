Tujuan: Mendefinisikan masalah penelitian, kesenjangan literatur, pertanyaan penelitian (RQ), hipotesis, kontribusi, ruang lingkup, dan definisi operasional untuk proyek Argumind.
Status dan tanggal: Draft v1.0 | 2026-11-17
Sumber kebenaran untuk: Rumusan `RQ1`–`RQ3`, hipotesis `H1`–`H3`, batasan ruang lingkup riset, dan definisi operasional konstruk argumentasi Bahasa Indonesia.

# Research Brief: Explainable Argument Mining and Implicit Premise Detection for Evaluating Critical Reasoning in Indonesian Analytical Texts

## 1. Masalah dan Latar Belakang

Dokumen analisis kebijakan, kajian bisnis, dan esai akademik berbahasa Indonesia sering memiliki tata bahasa yang rapi tetapi mengandung kelemahan penalaran struktural seperti lompatan kesimpulan, asumsi tersembunyi (*implicit premise*), dan ketiadaan bukti pendukung. Evaluasi manual terhadap struktur argumen oleh dosen atau analis memerlukan waktu 15–30 menit per dokumen (1.000–2.500 kata) dan rentan terhadap ketidaksepakatan antar-penilai (*inter-rater disagreement*) [CITATION NEEDED]. Penggunaan *Large Language Model* (LLM) generatif secara langsung (*zero-shot prompting*) menghasilkan umpan balik naratif yang tidak konsisten, rentan terhadap bias panjang teks (*length bias*), dan sering memberikan alasan yang tidak setia (*unfaithful explanation*) terhadap skor yang dihasilkan [CITATION NEEDED]. Oleh karena itu, diperlukan arsitektur komputasional hibrida yang memisahkan ekstraksi graf struktur argumen secara terukur dari pembangkitan umpan balik diagnostik pada teks Bahasa Indonesia. Sistem `Argumind` dirancang sebagai *decision-support* evaluasi penalaran kritis dengan memetakan komponen klaim, premis eksplisit, premis implisit, kekuatan bukti, celah logika, serta kontraargumen secara terstruktur.

---

## 2. Research Gap

Penelitian *computational argumentation* dan *argument mining* terkini (2020–2025) didominasi oleh korpus bahasa Inggris pada esai terstandar dan debat daring, seperti evaluasi kemampuan LLM lintas tugas argumentasi `[chen2024exploring]`, *fine-tuning* LLM *open-weight* untuk ekstraksi komponen-relasi `[cabessa2025argument]`, serta klasifikasi relasi *support/attack* berbasis *prompting* `[gorur2025can]`. Pada subtugas penalaran tak tertulis dan umpan balik pendidikan, studi pembangkitan premis implisit dengan pengetahuan *commonsense* sadar-wacana `[chakrabarty2021implicit]`, pembuatan korpus deteksi-rekonstruksi *enthymeme* `[stahl2023mind]`, penilaian esai multi-tugas `[ding2023score]`, serta *prompting* skor dan umpan balik gabungan `[stahl2024exploring]` juga masih terfokus pada bahasa Inggris dan belum menguji kesetiaan penjelasan (*explanation faithfulness*) melalui ablasi graf kontrafaktual. Sementara itu, di ekosistem NLP Bahasa Indonesia, tolok ukur dan model seperti `IndoLEM`/`IndoBERT` `[koto2020indolem]`, `IndoNLU` `[wilie2020indonlu]`, dan inisiatif multi-dataset `NusaCrowd` `[cahyawijaya2023nusacrowd]` telah menyediakan sumber daya untuk tugas NLU umum dan NLI pasangan kalimat, namun belum menyediakan korpus beranotasi maupun arsitektur hibrida teruji untuk ekstraksi graf argumen multi-komponen, rekonstruksi premis implisit, dan penilaian kualitas penalaran terjelaskan pada teks analitis dan kebijakan berbahasa Indonesia.

---

## 3. Pertanyaan Penelitian (Research Questions)

- **RQ1 (Ekstraksi Struktur & Relasi Argumen):** Seberapa akurat arsitektur hibrida (`encoder` lokal yang di-*fine-tune* + pemetaan relasi NLI + *LLM constrained decoding*) dalam mengidentifikasi batas komponen argumen (`Claim`, `ExplicitPremise`, `Evidence`) dan mengklasifikasikan relasi (`Support`, `Attack`) pada teks analitis Bahasa Indonesia dibandingkan dengan pendekatan *encoder-only* dan *zero-shot LLM*? Sistem WAJIB dievaluasi menggunakan metrik Macro-F1 komponen dan Macro-F1 relasi pada set uji beranotasi pakar (`→ research/METHODOLOGY.md#evaluasi`).
- **RQ2 (Rekonstruksi Premis Implisit & Celah Penalaran):** Sejauh mana modul inferensi graf-ke-teks pada Argumind mampu merekonstruksi premis implisit (`ImplicitPremise`) yang hilang dan mendeteksi celah logika (`ReasoningGap`) pada pasangan `ExplicitPremise → Claim` berbahasa Indonesia dibandingkan dengan *prompting* LLM standar? Evaluasi WAJIB mengukur kesamaan semantik (BERTScore) terhadap anotasi rujukan dan tingkat penerimaan validitas logis oleh anotator pakar.
- **RQ3 (Keselarasan Penilaian & Kesetiaan Penjelasan):** Seberapa tinggi kesepakatan (*agreement*) antara skor rubrik diagnostik Argumind dengan penilaian *blind* pakar manusia, serta apakah mekanisme *graph-grounded scoring* menurunkan tingkat ketidaksetiaan penjelasan (*unfaithful explanation*) dan bias panjang teks dibandingkan penilaian *direct LLM scoring*? Evaluasi WAJIB diukur dengan *Quadratic Weighted Kappa* (`QWK`), korelasi Spearman ($\rho$), dan uji intervensi penghapusan node graf.

---

## 4. Hipotesis

| ID | Terkait | Rumusan Hipotesis | Arah & Ambang Kuantitatif yang Diharapkan | Eksperimen Terkait |
|---|---|---|---|---|
| **H1** | `RQ1` | Arsitektur hibrida Argumind menghasilkan performa ekstraksi komponen argumen dan klasifikasi relasi yang lebih tinggi secara signifikan daripada baseline *encoder-only* (IndoBERT) dan *zero-shot LLM* pada teks analitis Bahasa Indonesia. | Peningkatan Macro-F1 komponen $\ge +0.05$ dan Macro-F1 relasi $\ge +0.07$ ($p < 0.05$, uji *paired bootstrap resampling*). `ASUMSI: selisih minimal 0.05 dianggap bermakna secara praktis.` | `E-01` (`→ research/EXPERIMENT_PLAN.md#E-01`) |
| **H2** | `RQ2` | Pengondisian LLM menggunakan sub-graf argumen lokal (`ExplicitPremise`, `Claim`, dan label NLI) menghasilkan rekonstruksi `ImplicitPremise` dan deteksi `ReasoningGap` yang lebih relevan dan valid secara logis dibandingkan *zero-shot/few-shot LLM* tanpa struktur graf. | BERTScore-F1 $\ge 0.78$ dan proporsi premis implisit yang dinilai valid oleh pakar $\ge 75\%$ (naik $\ge +15$ poin persentase dibanding baseline). `ASUMSI: target 75% mengacu pada ambang Go/No-Go dokumen produk.` | `E-02` (`→ research/EXPERIMENT_PLAN.md#E-02`) |
| **H3a** | `RQ3` | Skor kualitas argumen berbasis graf (`graph-grounded rubric scoring`) memiliki kesepakatan tinggi dengan skor rata-rata pakar manusia. | `QWK` $\ge 0.70$ dan korelasi Spearman $\rho \ge 0.70$ ($p < 0.01$) pada seluruh dimensi rubrik. | `E-03` (`→ research/EXPERIMENT_PLAN.md#E-03`) |
| **H3b** | `RQ3` | *Graph-grounded rubric scoring* menghasilkan tingkat kesetiaan penjelasan (*faithfulness*) yang lebih tinggi dan korelasi parsial terhadap panjang kata (*length bias*) yang lebih rendah dibandingkan *direct LLM scoring*. | Konsistensi penurunan skor saat node bukti dihapus (*counterfactual ablation consistency*) $\ge 85\%$; korelasi parsial panjang teks terhadap skor $|\rho_{\text{length}}| \le 0.20$. | `E-03` (`→ research/EXPERIMENT_PLAN.md#E-03`) |

---

## 5. Tujuan dan Kontribusi

> **Catatan Persetujuan:** Seluruh klaim kontribusi di bawah ini berstatus kandidat desain riset dan **WAJIB disetujui serta divalidasi oleh peneliti manusia** setelah hasil eksperimen `E-01` s.d. `E-03` tersedia. JANGAN menyajikan klaim kandidat sebagai temuan yang sudah terbukti sebelum verifikasi empiris selesai.

### A. Tujuan Penelitian
1. Membangun skema anotasi dan korpus teks argumentatif Bahasa Indonesia pada domain analisis kebijakan dan esai akademik yang mencakup komponen eksplisit, premis implisit, dan skor kualitas penalaran.
2. Merancang dan mengevaluasi *pipeline* hibrida (`F-01` Segmentasi Komponen, `F-02` Pemetaan Relasi, `F-03` Deteksi Premis Implisit & Celah Logika, `F-04` Penilaian Rubrik Terjelaskan, `F-05` Generator Kontraargumen).
3. Mengukur keselarasan penilaian sistem terhadap pakar manusia serta mengaudit *explanation faithfulness* dan *length bias*.

### B. Matriks Status Kontribusi (Terbukti vs Klaim Kandidat)

| ID | Butir Kontribusi | Kategori | Status Saat Ini | Bukti / Syarat Validasi |
|---|---|---|---|---|
| **C-01** | Spesifikasi konseptual taksonomi graf argumen (`Claim → ExplicitPremise / ImplicitPremise → Evidence → ReasoningGap → Counterargument`) untuk sistem Argumind. | Desain & Arsitektur | **Telah Ditetapkan** (Blueprint Konseptual) | Tercantum pada blueprint proyek (`3_rekomendasi_projek_cognitive_intelligence.md`). |
| **C-02** | Dataset beranotasi struktur argumen dan premis implisit Bahasa Indonesia dengan reliabilitas antar-anotator Krippendorff's $\alpha \ge 0.75$. | Dataset / Resource | **Klaim Kandidat (Belum Terbukti)** | WAJIB dibuktikan melalui proses anotasi multi-anotator (`→ research/DATASET.md`) dan disetujui peneliti manusia. |
| **C-03** | Metode hibrida *Graph-Conditioned Implicit Premise & Gap Detection* untuk teks Bahasa Indonesia yang mengungguli *zero-shot LLM*. | Metodologi / Model | **Klaim Kandidat (Belum Terbukti)** | WAJIB dibuktikan melalui eksperimen ablasi `E-01` dan `E-02` dengan uji signifikansi statistik. |
| **C-04** | Kerangka evaluasi *Graph-Grounded Explainable Argument Scoring* yang tahan terhadap *length bias* dan menjamin kesetiaan penjelasan terhadap komponen graf. | Evaluasi & Kualitas | **Klaim Kandidat (Belum Terbukti)** | WAJIB dibuktikan melalui eksperimen `E-03` bersama minimal 3 penilai pakar manusia. |

---

## 6. Ruang Lingkup, Batasan, dan Asumsi

### A. Ruang Lingkup (*In-Scope* vs *Out-of-Scope*)

| Dimensi | In-Scope (Termasuk dalam Riset) | Out-of-Scope (Di Luar Ruang Lingkup Riset) |
|---|---|---|
| **Bahasa & Format** | Teks Bahasa Indonesia baku/semi-formal dengan panjang 300–2.500 kata per dokumen dalam format teks polos, Markdown, DOCX, atau PDF berbasis teks. | Teks bahasa daerah, transkrip percakapan lisan tidak terstruktur, dokumen pindaian gambar tanpa OCR (*scanned image*), serta analisis tabel keuangan/rumus matematika kompleks. |
| **Domain Teks** | Esai akademik mahasiswa/pascasarjana, naskah kajian kebijakan publik (*policy brief*), dan laporan analisis bisnis/opini terstruktur. | Naskah sastra/fiksi, kode program, atau kontrak hukum klausul per klausul (domain verifikasi klaim dokumen kepatuhan masuk ke proyek `EpistemicGate`). |
| **Tugas Komputasional** | Ekstraksi batas komponen (`Claim`, `ExplicitPremise`, `Evidence`), klasifikasi relasi (`Support`, `Attack`), rekonstruksi `ImplicitPremise`, deteksi `ReasoningGap`, penilaian rubrik 4 dimensi, dan pembangkitan `Counterargument`. | Verifikasi fakta eksternal *real-time* terhadap internet/database rahasia (`out-of-scope`; Argumind menilai koherensi internal, kecukupan bukti yang disajikan di dalam teks, dan struktur logika). |
| **Otonomi Sistem** | *Human-in-the-loop decision support*: menghasilkan skor diagnostik dan peta visual untuk ditinjau penulis/penilai manusia. | Penentuan kelulusan akademik otomatis tanpa tinjauan dosen atau persetujuan kebijakan otomatis. JANGAN gunakan skor Argumind sebagai penentu tunggal nilai akhir. |

### B. Batasan (*Limitations*)
1. **Validitas Konstruk Lintas Domain:** Kriteria argumen yang kuat pada kajian kebijakan publik berbeda dengan argumen dogmatik hukum; model awal dibatasi pada genre esai analitis dan kajian kebijakan.
2. **Ketergantungan Kualitas Anotasi:** Rekonstruksi `ImplicitPremise` bersifat semi-terbuka (*open-ended text generation*), sehingga satu lompatan logika dapat memiliki lebih dari satu rumusan premis implisit yang valid.
3. **Verifikasi Kebenaran Faktual:** Tanpa modul RAG eksternal (`EpistemicGate`), sistem hanya menilai apakah suatu `Evidence` relevan dan mendukung `Claim` secara logis, bukan apakah angka di dalam `Evidence` tersebut faktual di dunia nyata.

### C. Asumsi Eksplisit
- `ASUMSI: A-01` — Korpus publik kajian kebijakan Indonesia dan esai mahasiswa (dengan *informed consent* dan anonimisasi penuh) sejumlah minimal 300–500 dokumen (sekitar 3.000–5.000 komponen argumen) dapat dikumpulkan dan dianotasi dalam waktu 4–6 minggu (`TODO(konfirmasi target jumlah dokumen korpus awal dengan peneliti utama)`).
- `ASUMSI: A-02` — Minimal 3 anotator terlatih dan 3 pakar domain (dosen/analis senior) tersedia untuk proses anotasi *gold standard* dan evaluasi *blind scoring* (`TODO(konfirmasi daftar dan kualifikasi anotator/pakar)`).
- `ASUMSI: A-03` — Kombinasi model lokal sekelas `IndoBERT` / `multilingual-e5` / `DeBERTa-v3-multilingual` dan pemanggilan LLM selektif memenuhi batas latensi inferensi $\le 15\text{ detik}$ per dokumen 1.000 kata.

---

## 7. Definisi Operasional Istilah Kunci

Setiap konstruk WAJIB mengacu pada definisi, tipe data/skala, dan contoh minimal berikut di seluruh dokumen `research/` dan `argumind-platform/docs/`:

| Istilah Kunci (`ID Tipe`) | Definisi Operasional & Aturan Pengukuran | Tipe Data / Skala | Contoh Minimal (Pola Konkret) |
|---|---|---|---|
| **Argument Component (`ArgumentNode`)** | Rentang teks berurutan (*contiguous span*) pada dokumen sumber yang memiliki fungsi argumentatif tunggal. WAJIB memiliki indeks karakter awal dan akhir (`start_char: int`, `end_char: int`) untuk komponen eksplisit. | `enum: Claim \| ExplicitPremise \| ImplicitPremise \| Evidence \| Counterargument` | `{"node_id": "N-01", "type": "Claim", "start_char": 0, "end_char": 68, "text": "Pemerintah daerah wajib mengalihkan subsidi BBM ke transportasi umum."}` |
| **Claim (`Claim`)** | Pernyataan utama atau kesimpulan yang ingin dibuktikan oleh penulis dan membutuhkan dukungan premis. Satu paragraf analitis WAJIB memiliki minimal 0 atau 1 `MainClaim` atau `SubClaim`. | `string` (span teks eksplisit di dokumen) | `"Penerapan kerja jarak jauh menurunkan biaya operasional perusahaan jasa."` |
| **Explicit Premise (`ExplicitPremise`)** | Alasan atau proposisi pendukung/penentang yang tertulis secara eksplisit di dalam teks untuk menopang atau menyerang suatu `Claim`. | `string` (span teks eksplisit di dokumen) | `"Perusahaan tidak perlu menyewa ruang kantor fisik dengan kapasitas penuh setiap hari."` |
| **Implicit Premise (`ImplicitPremise`)** | Asumsi penghubung (*warrant*) yang tidak tertulis di dalam teks tetapi WAJIB bernilai benar agar transisi logis dari `ExplicitPremise` menuju `Claim` menjadi valid. | `string` (teks hasil rekonstruksi model/anotator; `start_char: null`) | Jika `ExplicitPremise` = `"Mayoritas responden survei berasal dari Jakarta"` dan `Claim` = `"Kebijakan ini disetujui masyarakat Indonesia"`, maka `ImplicitPremise` = `"Preferensi responden di Jakarta mewakili populasi masyarakat Indonesia secara keseluruhan."` |
| **Evidence (`Evidence`)** | Data empiris, kutipan regulasi, statistik, hasil riset, atau contoh kasus konkret yang disajikan penulis di dalam teks untuk memvalidasi `ExplicitPremise` atau `Claim`. | `string` (span teks eksplisit) + `evidence_strength: int (1..5)` | `"Berdasarkan laporan BPS 2025, biaya komuter menyerap 28% pendapatan pekerja perkotaan."` |
| **Argument Relation (`ArgumentEdge`)** | Hubungan logis berarah dari node sumber (`source_id`) ke node target (`target_id`). JANGAN membuat edge siklus langsung (*self-loop* `source_id == target_id`). | `enum: Support \| Attack` + `confidence: float (0.00..1.00)` | `{"edge_id": "E-01", "source_id": "N-02", "target_id": "N-01", "relation": "Support", "confidence": 0.91}` |
| **Reasoning Gap (`ReasoningGap`)** | Celah penalaran atau *logical fallacy* terstruktur yang terdeteksi pada node atau edge, diklasifikasikan ke dalam taksonomi tetap: `UnsupportedClaim`, `HastyGeneralization`, `FalseCause`, `CircularReasoning`, `MissingCounterargumentConsideration`, atau `WeakEvidence`. | `enum` taksonomi + `severity: enum(Low \| Medium \| High)` | `{"gap_id": "G-01", "target_ref": "E-01", "gap_type": "HastyGeneralization", "severity": "High", "explanation": "Sampel satu kota digeneralisasi menjadi populasi nasional tanpa bukti keterwakilan."}` |
| **Counterargument (`Counterargument`)** | Pernyataan tandingan yang menyerang `Claim`, `ExplicitPremise`, atau `ImplicitPremise` utama untuk menguji ketahanan argumen penulis. | `string` + `target_node_id: string` | `{"counter_id": "CA-01", "target_node_id": "N-01", "text": "Pengalihan subsidi secara mendadak tanpa kesiapan armada transportasi umum justru meningkatkan beban biaya logistik rumah tangga."}` |
| **Argument Quality Score (`RubricScore`)** | Skor kualitas argumen pada 4 dimensi rubrik: (1) `ClarityOfClaim`, (2) `PremiseSupportAndCoherence`, (3) `EvidenceAdequacy`, (4) `CounterargumentAndLimitationAwareness`. Setiap dimensi dinilai pada skala ordinal `1` s.d. `5` dan WAJIB menyertakan referensi `node_id`/`gap_id` sebagai bukti alasan. | `int (1..5)` per dimensi; `overall_score: float (1.00..5.00)` | `{"dimension": "EvidenceAdequacy", "score": 2, "grounded_refs": ["N-01", "G-01"], "rationale": "Klaim N-01 tidak didukung bukti statistik dan memiliki celah G-01."}` |
| **Explanation Faithfulness (`FaithfulnessRate`)** | Proporsi kasus di mana perubahan/penghapusan komponen graf yang dirujuk oleh penjelasan sistem (`grounded_refs`) secara konsisten mengubah skor dimensi rubrik sesuai arah logisnya (mis. penghapusan node `Evidence` menurunkan skor `EvidenceAdequacy`). | `float (0.00..1.00)` (target $\ge 0.85$) | Ketika node `Evidence` `N-04` dihapus dari input, skor `EvidenceAdequacy` turun dari `4` menjadi `2` dan penjelasan tidak lagi merujuk `N-04` (`faithful = 1`). |

---

## 8. Pertanyaan Terbuka

1. `TODO(Q-01 — Memblokir Dataset & Eksperimen)`: Apakah korpus utama untuk eksperimen `E-01`–`E-03` akan memprioritaskan **(a) esai argumentatif mahasiswa/pascasarjana**, **(b) naskah kajian kebijakan publik (*policy brief*) terbuka**, atau **(c) gabungan keduanya secara berimbang (50:50)**?
2. `TODO(Q-02 — Memblokir Metodologi Model)`: Model LLM apa yang diizinkan sebagai *backbone* eksperimen dan produksi (mis. model *open-weights* lokal seperti `Qwen2.5-14B/32B-Instruct` / `Llama-3.1-8B/70B` untuk privasi data institusi, atau API komersial)?
3. `TODO(Q-03 — Non-Blokir, Literatur)`: Mohon konfirmasi daftar referensi spesifik tahun 2024–2026 yang ingin dimasukkan ke `research/LITERATURE_REVIEW.md` untuk menggantikan penanda `[CITATION NEEDED]` pada Bagian 1 dan Bagian 2.
4. `TODO(Q-04 — Persetujuan Peneliti)`: Apakah rumusan `RQ1`–`RQ3`, ambang kuantitatif hipotesis `H1`–`H3b`, dan daftar klaim kontribusi `C-01`–`C-04` disetujui oleh peneliti utama?
