Tujuan: Menetapkan desain penelitian, operasionalisasi variabel per RQ, sampling, prosedur pengumpulan dan pra-pemrosesan data, arsitektur algoritma, rumus metrik evaluasi, serta mitigasi ancaman validitas untuk proyek Argumind.
Status dan tanggal: Draft v1.0 | 2026-11-17
Sumber kebenaran untuk: Metodologi eksperimen `E-01`–`E-03`, parameter model hibrida Argumind, rumus metrik evaluasi, dan pemetaan `RQ1`–`RQ3` ke metode serta metrik.

# Metodologi Penelitian (Methodology): Explainable Argument Mining and Implicit Premise Detection for Evaluating Critical Reasoning in Indonesian Analytical Texts

---

## 1. Desain Penelitian

| Komponen Desain | Spesifikasi Eksplisit | Alasan Pemilihan |
|---|---|---|
| **Jenis Penelitian** | Penelitian eksperimental komputasional (*computational experimental research*) yang dikombinasikan dengan studi validasi psikometrik/kesepakatan pakar (*human-agreement & construct validation study*). | Menjawab kebutuhan evaluasi performa ekstraksi model (`RQ1`, `RQ2`) sekaligus membuktikan keselarasan penilaian sistem terhadap pakar manusia serta kesetiaan penjelasan (`RQ3`). |
| **Pendekatan** | Kuantitatif-komparatif dengan desain *within-dataset repeated measures* (untuk komparasi arsitektur model pada set uji yang sama) dan *blind multi-rater evaluation* (untuk validasi skor rubrik dan premis implisit). | Desain *within-dataset* menghilangkan varians kesulitan dokumen antar-model; evaluasi *blind* mencegah bias konfirmasi pakar saat menilai output model. |
| **Unit Analisis** | 1. Tingkat Dokumen ($D_i$): untuk evaluasi skor rubrik 4 dimensi (`RQ3`).<br>2. Tingkat Komponen/Span ($N_{ij}$): untuk identifikasi batas komponen argumen (`RQ1`).<br>3. Tingkat Pasangan Relasi ($E_{ijk}$): untuk klasifikasi `Support`/`Attack` (`RQ1`) dan rekonstruksi `ImplicitPremise` serta `ReasoningGap` (`RQ2`). | Memungkinkan atribusi kesalahan secara granular dari level token/span hingga level keputusan penilaian dokumen utuh. |

---

## 2. Variabel, Definisi Operasional, dan Skala Ukur per RQ

Definisi dasar komponen mengacu pada `→ research/RESEARCH_BRIEF.md#7-definisi-operasional-istilah-kunci`. Tabel berikut menetapkan variabel eksperimental untuk setiap pertanyaan penelitian:

### A. Variabel untuk `RQ1` (Ekstraksi Komponen & Klasifikasi Relasi)

| Jenis Variabel | Nama Variabel (`field_name`) | Definisi Operasional | Skala Ukur & Nilai Eksplisit | Contoh Minimal |
|---|---|---|---|---|
| **Independen (IV)** | Arsitektur Ekstraksi Struktur (`model_arch_rq1`) | Konfigurasi algoritma pemetaan argumen yang diuji pada `E-01`. | Nominal (3 kategori): `B1_EncoderOnly`, `B2_ZeroShotLLM`, `M1_ArgumindHybrid`. | `model_arch_rq1 = "M1_ArgumindHybrid"` |
| **Dependen (DV-1)** | Akurasi Komponen Argumen (`component_macro_f1`) | Kesesuaian span karakter dan label tipe node (`Claim`, `ExplicitPremise`, `Evidence`) terhadap anotasi *gold standard* pada ambang batas tumpang-tindih token $\ge 0.50$ dan kecocokan eksak. | Rasio: `float (0.0000..1.0000)` | `component_macro_f1 = 0.8125` |
| **Dependen (DV-2)** | Akurasi Relasi Argumen (`relation_macro_f1`) | Ketepatan klasifikasi berarah (`Support`, `Attack`, `NoRelation`) antara pasangan node $(N_a, N_b)$. | Rasio: `float (0.0000..1.0000)` | `relation_macro_f1 = 0.7450` |
| **Kontrol (CV)** | Pembagian Data, Panjang Dokumen, & *Random Seed* (`split_id`, `doc_len_tokens`, `seed`) | Seluruh model WAJIB dilatih dan diuji pada partisi dokumen identik dengan panjang $300 \le \text{kata} \le 2500$ dan `seed` tetap (`42`, `100`, `2026`). | `doc_len_tokens: int`, `seed: int` | `{"split_id": "test_v1", "seed": 42}` |

### B. Variabel untuk `RQ2` (Rekonstruksi Premis Implisit & Deteksi Celah Penalaran)

| Jenis Variabel | Nama Variabel (`field_name`) | Definisi Operasional | Skala Ukur & Nilai Eksplisit | Contoh Minimal |
|---|---|---|---|---|
| **Independen (IV)** | Strategi Pengondisian Konteks (`conditioning_mode_rq2`) | Representasi konteks input yang diberikan ke modul generatif pada `E-02`. | Nominal (3 kategori): `B3_TextOnlyPrompt`, `B4_CoTPrompt`, `M2_GraphNLIConditioned`. | `conditioning_mode_rq2 = "M2_GraphNLIConditioned"` |
| **Dependen (DV-1)** | Kemiripan Semantik Premis Implisit (`implicit_bertscore_f1`) | Skor kemiripan kontekstual antara `ImplicitPremise` hasil rekonstruksi model dan rujukan anotator manusia. | Rasio: `float (0.0000..1.0000)` | `implicit_bertscore_f1 = 0.8040` |
| **Dependen (DV-2)** | Validitas Logis Pakar (`expert_validity_rate`) | Proporsi `ImplicitPremise` yang dinilai "Valid & Jembatan Logis Tepat" (skor $\ge 4$ pada skala Likert 1–5) oleh mayoritas penilai pakar. | Rasio: `float (0.0000..1.0000)` | `expert_validity_rate = 0.7800` |
| **Dependen (DV-3)** | Akurasi Deteksi Celah Logika (`gap_macro_f1`) | Ketepatan klasifikasi 6 label `ReasoningGap` (`→ research/RESEARCH_BRIEF.md#7-definisi-operasional-istilah-kunci`). | Rasio: `float (0.0000..1.0000)` | `gap_macro_f1 = 0.7120` |
| **Kontrol (CV)** | Struktur Sub-Graf Input & Temperatur Decoding (`temperature`, `top_p`) | Evaluasi `E-02` WAJIB menggunakan sub-graf *oracle* (untuk mengisolasi error modul `RQ2`) serta sub-graf prediksi `RQ1` (*end-to-end*), dengan `temperature = 0.0` (greedy/deterministic). | `float`: `temperature = 0.0`, `top_p = 1.0` | `{"graph_source": "oracle", "temperature": 0.0}` |

### C. Variabel untuk `RQ3` (Keselarasan Penilaian & Kesetiaan Penjelasan)

| Jenis Variabel | Nama Variabel (`field_name`) | Definisi Operasional | Skala Ukur & Nilai Eksplisit | Contoh Minimal |
|---|---|---|---|---|
| **Independen (IV)** | Mekanisme Penilaian Rubrik (`scoring_mechanism_rq3`) | Metode pemberian skor 4 dimensi rubrik pada `E-03`. | Nominal (2 kategori): `B5_DirectLLMScoring` vs `M3_GraphGroundedScoring`. | `scoring_mechanism_rq3 = "M3_GraphGroundedScoring"` |
| **Dependen (DV-1)** | Skor Dimensi Rubrik (`rubric_dim_score`) | Nilai kualitas argumen pada 4 dimensi: `ClarityOfClaim`, `PremiseSupportAndCoherence`, `EvidenceAdequacy`, `CounterargumentAndLimitationAwareness`. | Ordinal: `int (1..5)` per dimensi; Rata-rata total: Interval `float (1.00..5.00)` | `{"EvidenceAdequacy": 4, "overall_score": 3.75}` |
| **Dependen (DV-2)** | Kesepakatan Sistem-Pakar (`qwk_score`, `spearman_rho`) | Tingkat kesepakatan antara skor sistem dan median/rata-rata skor 3 pakar manusia. | Rasio/Interval: `float (-1.0000..1.0000)` | `{"qwk_score": 0.7420, "spearman_rho": 0.7610}` |
| **Dependen (DV-3)** | Tingkat Kesetiaan Penjelasan (`faithfulness_rate`) | Proporsi intervensi penghapusan node bukti/premis di mana skor dimensi turun secara monotonik dan `grounded_refs` ikut terbarui secara akurat. | Rasio: `float (0.0000..1.0000)` | `faithfulness_rate = 0.8850` |
| **Dependen (DV-4)** | Bias Panjang Teks (`partial_corr_length`) | Korelasi parsial antara jumlah kata dokumen dan `overall_score` setelah mengontrol skor pakar manusia. | Interval: `float (-1.0000..1.0000)` | `partial_corr_length = 0.1420` |
| **Kontrol (CV)** | Rubrik Penilaian & Anonimitas Penilai (`rubric_version`, `blind_mode`) | Pakar manusia dan sistem WAJIB menggunakan definisi rubrik `v1.0` yang identik; pakar tidak mengetahui skor sistem (`blind_mode = true`). | `boolean`: `blind_mode = true` | `{"rubric_version": "v1.0", "blind_mode": true}` |

---

## 3. Populasi, Sampel, Ukuran Sampel, dan Teknik Sampling

### A. Populasi dan Teknik Sampling
1. **Populasi Target:** Dokumen teks analitis Bahasa Indonesia yang terdiri dari dua strata domain (`→ research/RESEARCH_BRIEF.md#6-ruang-lingkup-batasan-dan-asumsi`):
   - **Strata 1 (Akademik):** Esai argumentatif/analitis mahasiswa sarjana tahun akhir dan pascasarjana di perguruan tinggi Indonesia.
   - **Strata 2 (Kebijakan & Bisnis):** Naskah kajian kebijakan publik (*policy brief*), laporan analisis regulasi/ekonomi, dan opini analitis dari lembaga riset/instansi terbuka di Indonesia.
2. **Teknik Sampling:** *Purposive Stratified Quota Sampling* berdasarkan:
   - Strata domain (`50%` Akademik, `50%` Kebijakan/Bisnis; mengacu pada `ASUMSI: A-01` hingga `TODO(Q-01)` terjawab).
   - Strata panjang dokumen (`300–800` kata, `801–1.500` kata, `1.501–2.500` kata) untuk menguji ketahanan terhadap *length bias*.

### B. Ukuran Sampel dan Dasar Penentuan Statistik (*Power Analysis*)
- **Ukuran Sampel Dokumen ($N_{\text{doc}}$):** `ASUMSI: N_doc = 400 dokumen` (`200` esai akademik + `200` kajian kebijakan), menghasilkan estimasi `4.000–5.200` komponen argumen (`ArgumentNode`) dan `3.200–4.400` pasangan relasi (`ArgumentEdge`).
- **Partisi Dataset:** Pembagian berstrata (*stratified split* berdasarkan domain dan kuartil panjang teks) dengan rasio `70% Train` ($n = 280$), `15% Validation/Dev` ($n = 60$), dan `15% Test` ($n = 60$).
- **Dasar Penentuan Ukuran Uji ($n_{\text{test}} = 60$ dokumen, $\approx 600$ komponen):**
  1. Untuk `RQ3` (korelasi Spearman $\rho$ dan `QWK`): Dengan $\alpha = 0.05$ (dua arah), *statistical power* $(1 - \beta) = 0.90$, untuk mendeteksi korelasi minimum $\rho \ge 0.45$ terhadap hipotesis nol $\rho_0 = 0.00$, ukuran sampel minimum menurut rumus transformasi Fisher-$z$:
     $$n_{\min} = \left( \frac{Z_{1-\alpha/2} + Z_{1-\beta}}{0.5 \ln\frac{1+\rho}{1-\rho}} \right)^2 + 3 = \left( \frac{1.96 + 1.282}{0.4847} \right)^2 + 3 \approx 48 \text{ dokumen}$$
     Dengan $n_{\text{test}} = 60$ dokumen, daya statistik melampaui `0.90`.
  2. Untuk `RQ1` dan `RQ2` (evaluasi tingkat komponen/pasangan relasi pada $n \approx 600$ instance di *test set*): Memberikan *margin of error* proporsi $\le \pm 4.0\%$ pada tingkat kepercayaan `95%` dan daya uji *paired bootstrap* $> 0.95$ untuk mendeteksi selisih F1 $\ge 0.05$.

---

## 4. Pengumpulan Data dan Urutan Pra-Pemrosesan (Preprocessing)

### A. Instrumen, Prosedur, dan Periode Pengumpulan Data
- **Instrumen:**
  1. Pedoman Anotasi Struktur Argumen & Premis Implisit (`→ research/DATASET.md#pedoman-anotasi`).
  2. Antarmuka anotasi berbasis web (Label Studio / modul anotasi internal Argumind) yang memvalidasi skema JSON `ArgumentNode`, `ArgumentEdge`, `ReasoningGap`, dan `RubricScore`.
  3. Lembar persetujuan (*informed consent*) untuk kontributor esai mahasiswa (`→ research/ETHICS.md`).
- **Prosedur:**
  1. Pengumpulan dokumen mentah dan penyaringan kelayakan (panjang `300–2.500` kata, Bahasa Indonesia baku, bebas plagiarisme/teks rusak).
  2. Pelatihan `3` anotator menggunakan `20` dokumen kalibrasi hingga mencapai kesepakatan awal Krippendorff's $\alpha \ge 0.75$.
  3. Anotasi *double-blind* oleh minimal `2` anotator independen per dokumen, diikuti resolusi konflik (*adjudication*) oleh anotator ke-3 / peneliti senior untuk membentuk *gold standard*.
  4. Penilaian skor rubrik 4 dimensi secara *blind* oleh `3` pakar domain pada seluruh dokumen *test set* ($n_{\text{test}} = 60$).
- **Periode Pelaksanaan:** `ASUMSI: Durasi total 6 minggu` (Minggu 1: kurasi korpus & kalibrasi anotator; Minggu 2–5: anotasi paralel & adjudikasi; Minggu 6: audit kualitas dataset & pembekuan *test split*). `TODO(konfirmasi tanggal mulai dan selesai pengumpulan data)`.

### B. Pipeline Pra-Pemrosesan Berurutan (Sequential Preprocessing)
Setiap dokumen mentah WAJIB melewati 6 tahap deterministik berikut secara berurutan sebelum masuk ke anotasi atau model:

1. **Tahap 1 — Ekstraksi & Normalisasi Pengodean (`encoding_normalization`):**
   - Konversi DOCX/PDF berbasis teks ke UTF-8 menggunakan parser deterministik; normalisasi Unicode `NFKC`; ganti karakter kontrol non-cetak (selain `\n`) dengan spasi tunggal. JANGAN mengubah huruf besar/kecil (*case folding* dilarang karena merusak batas kalimat dan entitas).
   - *Contoh:* `"Kebijakan\u00A0fiskal\r\n2026"` $\rightarrow$ `"Kebijakan fiskal\n2026"`.
2. **Tahap 2 — Anonimisasi Identitas Pribadi (`pii_redaction`):**
   - Deteksi dan ganti nama penulis, NIM, email, nomor telepon, dan nama institusi spesifik penulis menggunakan pola regex dan NER dengan token placeholder standar: `[REDACTED_NAME]`, `[REDACTED_ID]`, `[REDACTED_EMAIL]`.
   - *Contoh:* `"Oleh: Budi Santoso (NIM 204511)"` $\rightarrow$ `"Oleh: [REDACTED_NAME] ([REDACTED_ID])"`.
3. **Tahap 3 — Segmentasi Paragraf & Kalimat (`sentence_segmentation`):**
   - Pisahkan paragraf berdasarkan `\n\n`. Pisahkan kalimat menggunakan *sentence splitter* Bahasa Indonesia yang mengenali singkatan baku (`UU No.`, `Rp.`, `Prof.`, `dkk.`, `hlm.`) agar tidak terpotong salah.
   - Setiap kalimat diberi indeks karakter absolut (`start_char`, `end_char`) terhadap string dokumen yang telah dinormalisasi pada Tahap 1–2.
   - *Contoh:* `{"sent_id": "S-01", "para_id": "P-01", "start_char": 0, "end_char": 68, "text": "..."}`.
4. **Tahap 4 — Validasi Kriteria Panjang & Kualitas Teks (`quality_gate`):**
   - Hitung jumlah token kata (`word_count`). Dokumen dengan `word_count < 300` atau `word_count > 2500` atau rasio kata bahasa asing $> 20\%$ WAJIB ditolak dengan kode status `REJECTED_OUT_OF_BOUNDS`.
5. **Tahap 5 — Tokenisasi Sub-Kata & Penyelarasan Offset (`subword_alignment`):**
   - Tokenisasi menggunakan tokenizer model *encoder* (`return_offsets_mapping=True`) dengan batas jendela `max_length = 512` token dan *sliding window stride* `128` token untuk dokumen panjang.
   - Konversi anotasi rentang karakter (`start_char`, `end_char`) ke label sekuens `BIO` (*Beginning, Inside, Outside*): `B-Claim`, `I-Claim`, `B-ExplicitPremise`, `I-ExplicitPremise`, `B-Evidence`, `I-Evidence`, `O`.
6. **Tahap 6 — Konstruksi Kandidat Pasangan Relasi (`pair_candidate_generation`):**
   - Bangkitkan pasangan berarah $(N_a, N_b)$ dengan $a \neq b$ untuk seluruh komponen dalam paragraf yang sama atau antar-klaim utama lintas paragraf (jarak maksimum $\Delta \text{para} \le 3$) guna mencegah ledakan kombinatorial kuadratik.

---

## 5. Arsitektur Metode Argumind dan Analisis Statistik

### A. Spesifikasi Algoritma & Parameter Inti (`M1`–`M3`)
1. **Modul `F-01` Segmentasi Komponen (`M1_ArgumindHybrid` — Tahap 1):**
   - *Arsitektur:* `IndoBERT-large` (atau `DeBERTa-v3-multilingual`) + lapisan *BiLSTM-CRF* untuk penandaan sekuens `BIO`, dikombinasikan dengan *LLM constrained span refinement* hanya ketika entropi prediksi token $> 0.45$.
   - *Hyperparameter Pelatihan:* Optimizer `AdamW`, `learning_rate = 2e-5`, `weight_decay = 0.01`, `batch_size = 16`, `epochs = 10` (dengan *early stopping* `patience = 3` berdasarkan Macro-F1 *dev set*), `warmup_ratio = 0.10`.
2. **Modul `F-02` Pemetaan Relasi & Stance (`M1_ArgumindHybrid` — Tahap 2):**
   - *Arsitektur:* Klasifikasi pasangan komponen $(N_a, N_b)$ menggunakan representasi silang (*cross-encoder* NLI Bahasa Indonesia) ditambah aturan dekode *Minimum Spanning DAG* (algoritma Chu-Liu/Edmonds yang dimodifikasi) yang melarang *self-loop* dan siklus langsung.
   - *Output:* Label relasi $\in \{\text{Support}, \text{Attack}, \text{NoRelation}\}$ beserta distribusi probabilitas NLI $(p_{\text{entail}}, p_{\text{neutral}}, p_{\text{contradict}})$.
3. **Modul `F-03` Rekonstruksi Premis Implisit & Deteksi Celah (`M2_GraphNLIConditioned`):**
   - *Kondisi Pemicu:* Dipanggil untuk setiap pasangan $(N_{\text{premise}}, N_{\text{claim}})$ yang diprediksi berelasi `Support`, tetapi memiliki skor NLI $p_{\text{neutral}} + p_{\text{contradict}} \ge 0.40$ (menandakan adanya lompatan logika atau asumsi tak tertulis).
   - *Inferensi:* Pemanggilan LLM dengan skema JSON terikat (*JSON Schema constrained decoding*, `temperature = 0.0`) yang menerima input tuple `(ExplicitPremise, Claim, NLI_Distribution, Local_Subgraph)` dan menghasilkan objek `ImplicitPremise` serta klasifikasi `ReasoningGap`.
4. **Modul `F-04` Penilaian Rubrik Terjelaskan (`M3_GraphGroundedScoring`):**
   - *Komputasi Skor:* Menggabungkan fitur struktural graf deterministik (rasio klaim yang didukung bukti, kedalaman pohon argumen, jumlah `ReasoningGap` berbobot `severity`, keberadaan kontraargumen) dengan evaluator rubrik berbasis graf.
   - *Kendala Kesetiaan (Faithfulness Constraint):* Sistem WAJIB menolak output skor dimensi apabila `grounded_refs` kosong atau merujuk pada ID node yang tidak ada di graf dokumen (`HTTP 422 / ValidationError`).

### B. Uji Hipotesis dan Tingkat Signifikansi Statistik
- **Tingkat Signifikansi ($\alpha$):** $\alpha = 0.05$ (dua arah) untuk `H1` dan `H2`; $\alpha = 0.01$ untuk `H3a` (`→ research/RESEARCH_BRIEF.md#4-hipotesis`).
- **Uji Komparasi Model (`RQ1`, `RQ2`):**
  1. *Paired Bootstrap Resampling* dengan $B = 10.000$ iterasi pada dokumen *test set* untuk menghitung *p-value* dan interval kepercayaan `95%` selisih Macro-F1 serta BERTScore.
  2. *Wilcoxon Signed-Rank Test* (non-parametrik, berpasangan per dokumen) untuk membandingkan skor validitas pakar pada `RQ2`.
- **Koreksi Multi-Komparasi:** Prosedur *Holm-Bonferroni* WAJIB diterapkan saat menguji lebih dari 2 baseline secara simultan agar *Family-Wise Error Rate* (FWER) tetap $\le 0.05$.

---

## 6. Baseline Pembanding dan Rumus Metrik Evaluasi

### A. Daftar Baseline Pembanding
- **B1 (`B1_EncoderOnly`):** Model `IndoBERT` + linear token classification & pairwise classification tanpa *LLM refinement* maupun dekode graf global.
- **B2 (`B2_ZeroShotLLM`):** *Prompting* LLM secara langsung pada teks dokumen utuh untuk mengekstrak JSON komponen dan relasi tanpa *encoder* lokal.
- **B3 (`B3_TextOnlyPrompt`):** *Prompting* LLM untuk menebak premis implisit dan celah logika langsung dari paragraf mentah tanpa ekstraksi sub-graf argumen dan tanpa sinyal NLI.
- **B4 (`B4_CoTPrompt`):** *Few-shot Chain-of-Thought prompting* (3 contoh *in-context*) tanpa input struktur graf formal.
- **B5 (`B5_DirectLLMScoring`):** Penilaian rubrik 4 dimensi secara langsung oleh LLM dari teks esai mentah beserta penjelasan bebas (*free-text rationale*) tanpa penjangkaran pada graf argumen.

### B. Rumus Matematis Metrik Evaluasi
Seluruh skrip evaluasi pada eksperimen `E-01`–`E-03` WAJIB mengimplementasikan rumus berikut secara eksak:

1. **Macro-F1 Komponen dan Relasi (`RQ1`, `RQ2`):**
   Untuk himpunan kelas $C$ (dengan $|C| = 3$ untuk komponen eksplisit dan $|C| = 2$ untuk relasi aktif `Support`/`Attack`):
   $$\text{Precision}_c = \frac{\text{TP}_c}{\text{TP}_c + \text{FP}_c}, \quad \text{Recall}_c = \frac{\text{TP}_c}{\text{TP}_c + \text{FN}_c}, \quad \text{F1}_c = \frac{2 \cdot \text{Precision}_c \cdot \text{Recall}_c}{\text{Precision}_c + \text{Recall}_c}$$
   $$\text{Macro-F1} = \frac{1}{|C|} \sum_{c \in C} \text{F1}_c$$
   *(Catatan: Pada level komponen, dievaluasi pada dua ambang: Exact Match $\text{IoU} = 1.0$ dan Partial Match $\text{IoU} \ge 0.5$, dengan $\text{IoU}(S_{\text{pred}}, S_{\text{gold}}) = \frac{|S_{\text{pred}} \cap S_{\text{gold}}|}{|S_{\text{pred}} \cup S_{\text{gold}}|}$).*

2. **Krippendorff's Alpha ($\alpha_{\text{Krip}}$) untuk Reliabilitas Anotasi (`Dataset` & `RQ2`):**
   $$\alpha_{\text{Krip}} = 1 - \frac{D_o}{D_e}$$
   di mana $D_o$ adalah ketidaksepakatan yang teramati (*observed disagreement*) dan $D_e$ adalah ketidaksepakatan yang diharapkan secara kebetulan (*expected disagreement*). Target wajib: $\alpha_{\text{Krip}} \ge 0.75$.

3. **BERTScore-F1 untuk Rekonstruksi Premis Implisit (`RQ2`):**
   Diberikan vektor embedding token referensi $x = \langle x_1, \dots, x_k \rangle$ dan kandidat prediksi $\hat{x} = \langle \hat{x}_1, \dots, \hat{x}_m \rangle$:
   $$R_{\text{BERT}} = \frac{1}{|x|} \sum_{x_i \in x} \max_{\hat{x}_j \in \hat{x}} \frac{x_i^\top \hat{x}_j}{\|x_i\| \|\hat{x}_j\|}, \quad P_{\text{BERT}} = \frac{1}{|\hat{x}|} \sum_{\hat{x}_j \in \hat{x}} \max_{x_i \in x} \frac{x_i^\top \hat{x}_j}{\|x_i\| \|\hat{x}_j\|}$$
   $$\text{BERTScore-F1} = \frac{2 \cdot P_{\text{BERT}} \cdot R_{\text{BERT}}}{P_{\text{BERT}} + R_{\text{BERT}}}$$

4. **Quadratic Weighted Kappa (`QWK`) untuk Kesepakatan Skor Rubrik (`RQ3`):**
   Untuk skala rubrik ordinal $1 \dots K$ ($K = 5$), dengan matriks bobot kuadratik $w_{ij}$, matriks observasi ternormalisasi $O_{ij}$, dan matriks ekspektasi $E_{ij}$:
   $$w_{ij} = \frac{(i - j)^2}{(K - 1)^2}, \quad \text{QWK} = 1 - \frac{\sum_{i=1}^{K}\sum_{j=1}^{K} w_{ij} O_{ij}}{\sum_{i=1}^{K}\sum_{j=1}^{K} w_{ij} E_{ij}}$$

5. **Korelasi Peringkat Spearman ($\rho$) dan Korelasi Parsial Panjang Teks (`RQ3`):**
   $$\rho = 1 - \frac{6 \sum_{d=1}^{n} r_d^2}{n(n^2 - 1)}$$
   di mana $r_d$ adalah selisih peringkat skor sistem ($Y$) dan skor rata-rata pakar ($H$) pada dokumen ke-$d$. Korelasi parsial terhadap jumlah kata ($L$) dengan mengontrol skor pakar ($H$) dihitung sebagai:
   $$\rho_{YL \cdot H} = \frac{\rho_{YL} - \rho_{YH}\rho_{LH}}{\sqrt{1 - \rho_{YH}^2}\sqrt{1 - \rho_{LH}^2}}$$
   Target anti-bias panjang teks: $|\rho_{YL \cdot H}| \le 0.20$.

6. **Tingkat Kesetiaan Penjelasan Kontrafaktual (`FaithfulnessRate`, `RQ3`):**
   Untuk himpunan intervensi ablasi $M$ di mana node pendukung/bukti $u \in \text{grounded\_refs}(d, k)$ dihapus dari dokumen $d$ pada dimensi $k$:
   $$\text{FaithfulnessRate} = \frac{1}{|M|} \sum_{m \in M} \mathbb{I}\Big( S_k(G_d \setminus \{u_m\}) < S_k(G_d) \;\land\; u_m \notin \text{grounded\_refs}(G_d \setminus \{u_m\}, k) \Big)$$
   di mana $\mathbb{I}(\cdot)$ adalah fungsi indikator bernilai `1` jika kedua kondisi terpenuhi dan `0` jika sebaliknya.

---

## 7. Ancaman Validitas (Threats to Validity) dan Mitigasi

| Kategori Validitas | Ancaman Spesifik | Strategi Mitigasi Eksplisit (WAJIB Diterapkan) |
|---|---|---|
| **Validitas Internal** | *Error propagation* dari modul ekstraksi komponen (`RQ1`) mengaburkan evaluasi murni modul premis implisit (`RQ2`) dan penilaian rubrik (`RQ3`). | Evaluasi `RQ2` dan `RQ3` WAJIB dijalankan dalam dua mode: (1) **Mode Oracle** (menggunakan graf *gold standard* manusia untuk mengisolasi kemampuan murni modul `F-03`/`F-04`), dan (2) **Mode End-to-End** (menggunakan graf hasil prediksi `F-01`/`F-02`). |
| **Validitas Internal** | Kebocoran data (*data leakage*) jika esai dari penulis atau topik kebijakan yang sama masuk ke *train* dan *test split*. | Pembagian partisi `70/15/15` WAJIB dikelompokkan berdasarkan `author_id` dan klaster topik (*group-stratified split*) sehingga tidak ada penulis yang beririsan antar-split. |
| **Validitas Eksternal** | Model mengalami *overfitting* pada gaya penulisan satu institusi kampus atau satu kementerian/lembaga kebijakan. | Sampel dokumen WAJIB diambil dari minimal `3` perguruan tinggi/program studi berbeda untuk strata akademik dan minimal `4` lembaga/institusi publik berbeda untuk strata kajian kebijakan. |
| **Validitas Konstruk** | Penilaian kualitas argumen sebenarnya hanya mengukur panjang esai atau kemewahan kosakata (*lexical sophistication*), bukan struktur penalaran. | 1. Mengukur dan membatasi $|\rho_{YL \cdot H}| \le 0.20$ terhadap panjang kata.<br>2. Melakukan uji kontrafaktual (`FaithfulnessRate`) dengan menghapus bukti sambil mempertahankan gaya bahasa. |
| **Reliabilitas** | Subjektivitas anotator manusia dalam merumuskan teks `ImplicitPremise` (karena bersifat *open-ended*) dan dalam memberi skor rubrik `1..5`. | 1. Mewajibkan pelatihan kalibrasi dengan ambang $\alpha_{\text{Krip}} \ge 0.75$ sebelum anotasi penuh.<br>2. Untuk `ImplicitPremise`, mengombinasikan evaluasi otomatis (`BERTScore-F1` terhadap 2 referensi anotator) dengan penilaian validitas logis pakar karena rumusan kalimat yang berbeda dapat memiliki arti logis yang ekuivalen. |

---

## 8. Tabel Pemetaan RQ → Metode → Metrik Evaluasi

| ID RQ & Hipotesis | Eksperimen | Metode / Algoritma Utama | Baseline Pembanding | Metrik Evaluasi Utama & Ambang Target | Uji Statistik |
|---|---|---|---|---|---|
| **RQ1** (`H1`)<br>Ekstraksi Komponen & Relasi Argumen | `E-01` | `M1_ArgumindHybrid`: `IndoBERT` + `BiLSTM-CRF` + Cross-Encoder NLI + *Minimum Spanning DAG* + *LLM Constrained Refinement* (`F-01`, `F-02`). | `B1_EncoderOnly`,<br>`B2_ZeroShotLLM` | • `component_macro_f1` (Exact & $\text{IoU} \ge 0.5$): $\Delta \ge +0.05$<br>• `relation_macro_f1`: $\Delta \ge +0.07$ | *Paired Bootstrap Resampling* ($B = 10.000$, $\alpha = 0.05$, koreksi Holm-Bonferroni). |
| **RQ2** (`H2`)<br>Rekonstruksi Premis Implisit & Deteksi Celah | `E-02` | `M2_GraphNLIConditioned`: *Sub-graph & NLI-triggered JSON Constrained LLM Inference* (`F-03`), diuji pada mode *Oracle* dan *End-to-End*. | `B3_TextOnlyPrompt`,<br>`B4_CoTPrompt` | • `implicit_bertscore_f1` $\ge 0.78$<br>• `expert_validity_rate` $\ge 0.75$ ($\Delta \ge +0.15$)<br>• `gap_macro_f1` (6 kelas) | *Paired Bootstrap* ($B = 10.000$) untuk BERTScore & F1; *Wilcoxon Signed-Rank Test* ($\alpha = 0.05$) untuk skor pakar. |
| **RQ3** (`H3a`, `H3b`)<br>Keselarasan Penilaian & Kesetiaan Penjelasan | `E-03` | `M3_GraphGroundedScoring`: *Feature + Graph-Grounded Rubric Evaluator* dengan validasi wajib `grounded_refs` (`F-04`). | `B5_DirectLLMScoring` | • `QWK` $\ge 0.70$, Spearman $\rho \ge 0.70$<br>• `FaithfulnessRate` $\ge 0.85$<br>• Bias panjang $|\rho_{YL \cdot H}| \le 0.20$ | Uji signifikansi korelasi Spearman & `QWK` ($\alpha = 0.01$); uji proporsi McNemar untuk `FaithfulnessRate`. |

---

## 9. Pertanyaan Terbuka

1. `TODO(Q-METH-01 — Konfirmasi Ukuran Sampel Korpus)`: Apakah target sampel $N_{\text{doc}} = 400$ dokumen (`280 train / 60 dev / 60 test`) disetujui sesuai kapasitas anggaran dan waktu tim anotator, atau perlu disesuaikan ke batas minimum statistik ($N_{\text{doc}} = 300$, dengan $n_{\text{test}} = 50$)?
2. `TODO(Q-METH-02 — Pemilihan Model Encoder & LLM Spesifik)`: Untuk menjaga reprodusibilitas `E-01`–`E-03`, mohon kunci nama *checkpoint* HuggingFace untuk *encoder* (mis. `indobenchmark/indobert-large-p2` vs `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7`) serta *checkpoint* LLM utama (`→ research/RESEARCH_BRIEF.md#8-pertanyaan-terbuka` `Q-02`).
