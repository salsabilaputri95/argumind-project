Tujuan: Mencatat seluruh riwayat eksekusi eksperimen (`E-01`–`E-03b`) secara *append-only*, mencakup parameter, seed, lingkungan, perintah, angka mentah tanpa pembulatan, lokasi berkas output, anomali, dan kesimpulan sementara.
Status dan tanggal: Draft v1.0 | 2026-11-18
Sumber kebenaran untuk: Jejak audit empiris seluruh percobaan yang berhasil maupun gagal pada proyek riset Argumind.

# Log Eksperimen (Experiment Log — Append-Only): Argumind Research

> **ATURAN WAJIB LOG EKSPERIMEN:**
> 1. **Append-Only:** Tambahkan entri baru **HANYA** di bagian paling bawah dokumen ini. **JANGAN** mengedit, menimpa, atau menghapus entri lama yang sudah tercatat. Jika ada koreksi terhadap run lama, buat entri run baru yang merujuk ke ID run lama tersebut.
> 2. **Larangan Membulatkan atau Mengarang Angka:** Salin angka metrik secara verbatim (presisi penuh, minimal 4–6 angka di belakang koma sesuai `metrics_raw.json`) dan cantumkan path berkas output-nya. **JANGAN** mengarang angka sebelum eksperimen dijalankan.
> 3. **Wajib Mencatat Percobaan Gagal:** Setiap percobaan yang gagal (`OOM`, `timeout`, bug skrip, atau metrik di bawah target hipotesis) **WAJIB** tetap dicatat dengan status `FAILED` atau `NEGATIVE_RESULT`. **JANGAN** menyembunyikan percobaan yang gagal.
> 4. **Label Kesimpulan Sementara:** Seluruh interpretasi pada tiap entri wajib diawali dengan label **`«dugaan»`** hingga seluruh rangkaian multi-seed dan uji signifikansi statistik disahkan oleh peneliti utama.

---

## 1. Template Baku Entri Log (Salin Blok Ini untuk Setiap Run Baru)

```markdown
### [LOG-YYYYMMDD-XX] — <ID Skenario: E-01 | E-02a | E-02b | E-03a | E-03b>
- **ID Run & Status:** `run_YYYYMMDD_seedXX_v1` | Status: `COMPLETED | FAILED | ABORTED | NEGATIVE_RESULT`
- **Tanggal & Waktu (UTC+8):** `YYYY-MM-DDTHH:MM:SS+08:00`
- **Git Commit Hash:** `<40-char-sha1-commit-hash>` (Status working tree: `clean`)
- **Konfigurasi & Parameter:**
  - `arch / mode`: `<mis. M1_ArgumindHybrid>`
  - `encoder_checkpoint`: `<nama_model_hf>`
  - `llm_checkpoint`: `<nama_model_llm>`
  - `hyperparameters`: `{"lr": 2e-5, "batch_size": 16, "epochs": 10, "temperature": 0.0}`
  - `dataset_version & split`: `IndoArg-Analytical-v1 (manifest sha256: <hash_awal_8_char>) | split: <dev|test>`
- **Random Seed:** `<42 | 100 | 2026>`
- **Lingkungan Eksekusi (Environment):**
  - `OS & Kernel`: `<mis. Ubuntu 22.04 LTS / Windows 11 WSL2>`
  - `CPU & RAM`: `<mis. AMD EPYC 16vCPU, 64GB RAM>`
  - `GPU & VRAM`: `<mis. 1x NVIDIA L4 24GB, CUDA 12.4>`
  - `Python & PyTorch`: `Python 3.12.x | torch 2.5.x+cu124 | transformers 4.46.x`
- **Perintah Eksekusi (Command):**
  `python -m research.runners.run_experiment --exp-id <E-XX> --arch <ARCH> --data-dir research/data/processed/v1.0 --split <SPLIT> --seed <SEED> --output-dir research/outputs/<E-XX>/<RUN_ID>`
- **Hasil Mentah (Tanpa Pembulatan) & Lokasi File Output:**
  - **File Output:**
    - Config: `research/outputs/<E-XX>/<RUN_ID>/config_locked.json`
    - Prediksi: `research/outputs/<E-XX>/<RUN_ID>/predictions.jsonl`
    - Metrik Mentah: `research/outputs/<E-XX>/<RUN_ID>/metrics_raw.json`
    - Log Proses: `research/outputs/<E-XX>/<RUN_ID>/run.log`
  - **Angka Asli (`metrics_raw.json`):**
    - `<nama_metrik_1>`: `<salin_angka_asli_tanpa_pembulatan>`
    - `<nama_metrik_2>`: `<salin_angka_asli_tanpa_pembulatan>`
    - `latency_p95_ms`: `<salin_angka_asli>`
- **Anomali / Error yang Ditemukan:**
  - `<Tulis "Tidak ada" atau rincikan error, mis. 2 dokumen mengalami timeout LLM pada tahap F-03, lihat baris 142 di run.log>`
- **Kesimpulan Sementara:**
  - «dugaan» `<Tulis interpretasi awal berdasarkan angka di atas tanpa klaim kausal final>`
```

---

## 2. Daftar Rekaman Eksekusi (Append-Only)

### [LOG-20261118-00] — Inisialisasi Buku Log (Belum Ada Eksperimen Dijalankan)
- **ID Run & Status:** `INIT_LOG` | Status: `PENDING_DATASET_FREEZE`
- **Tanggal & Waktu (UTC+8):** `2026-11-18T10:39:00+08:00`
- **Git Commit Hash:** `TODO(isi commit hash saat repositori git diinisialisasi)`
- **Konfigurasi & Parameter:** Belum ada model yang dijalankan; menunggu penyelesaian anotasi `IndoArg-Analytical-v1` (`→ research/DATASET.md#2-ukuran-dataset-baris-kolom-dan-berkas`).
- **Random Seed:** `N/A`
- **Lingkungan Eksekusi (Environment):** `N/A`
- **Perintah Eksekusi (Command):** `N/A`
- **Hasil Mentah (Tanpa Pembulatan) & Lokasi File Output:** Belum ada berkas di `research/outputs/` (sesuai aturan: dilarang mengarang hasil eksperimen).
- **Anomali / Error yang Ditemukan:** Tidak ada.
- **Kesimpulan Sementara:**
  - «dugaan» Eksekusi perdana akan dimulai dari verifikasi pipeline pra-pemrosesan dan baseline `B1_EncoderOnly` pada skenario `E-01` begitu partisi `train` dan `dev` tersedia.

### [LOG-20261118-01] — E-01 (Smoke Run Korpus Benih v1.0 / Fallback Heuristik Lokal)
- **ID Run & Status:** `run_20261118_seed42` | Status: `COMPLETED` (Smoke Test Pra-Fine-Tuning Colab)
- **Tanggal & Waktu (UTC+8):** `2026-11-18T14:38:08+08:00`
- **Git Commit Hash:** `74dae63081d42e1bf6b871caead445047ab45f7b` (Working tree: `uncommitted Fase 1 changes`)
- **Konfigurasi & Parameter:**
  - `arch / mode`: `M1_ArgumindHybrid` (mode fallback heuristik lokal tanpa checkpoint GPU IndoBERT)
  - `dataset_version & split`: `IndoArg-Analytical-v1` seed sample (`manifest sha256 documents.jsonl: 4dd851d9`) | `split: test` (`n_docs = 2`)
- **Random Seed:** `42`
- **Lingkungan Eksekusi (Environment):**
  - `OS`: `Windows` (`D:\argumind`)
  - `Python`: `Python 3.13.5` (`.venv`)
- **Perintah Eksekusi (Command):**
  `.venv\Scripts\python.exe -m research.runners.run_experiment --exp-id E-01 --arch M1_ArgumindHybrid --data-dir research/data/processed/v1.0 --split test --seed 42 --output-dir research/outputs/E-01/run_20261118_seed42`
- **Hasil Mentah (Tanpa Pembulatan) & Lokasi File Output:**
  - **File Output:**
    - Config: `research/outputs/E-01/run_20261118_seed42/config_locked.json`
    - Prediksi: `research/outputs/E-01/run_20261118_seed42/predictions.jsonl`
    - Metrik Mentah: `research/outputs/E-01/run_20261118_seed42/metrics_raw.json`
    - Log Proses: `research/outputs/E-01/run_20261118_seed42/run.log`
  - **Angka Asli (`metrics_raw.json`):**
    - `component_macro_f1_exact`: `0.5735735735735735`
    - `component_macro_f1_iou50`: `0.5735735735735735`
    - `relation_macro_f1`: `0.0`
    - `cycle_rate`: `0.0`
    - `n_docs`: `2`
    - `latency_total_ms`: `1941.54`
- **Anomali / Error yang Ditemukan:**
  - `relation_macro_f1` bernilai `0.0` pada smoke test ini karena runner memakai ID lokal (`N-01`) sementara `edges.jsonl` pada korpus benih memakai ID berprefiks dokumen (`doc_0011_N-01`) serta model NLI belum di-fine-tune di GPU Colab.
- **Kesimpulan Sementara:**
  - «dugaan» Pipeline runner, verifikasi checksum `manifest.sha256`, pencatatan artefak keluaran, dan jaminan graf bebas siklus (`cycle_rate = 0.0`) berfungsi; evaluasi akurasi sesungguhnya wajib menunggu fine-tuning `IndoBERT` + `Cross-Encoder NLI` di Google Colab pada korpus penuh.

### [LOG-20261119-02] — E-01 (Fine-Tuning IndoBERT BIO + Cross-Encoder NLI di Google Colab T4 GPU — Korpus Benih v1.0)
- **ID Run & Status:** `colab_seed42` | Status: `NEGATIVE_RESULT` (Pipeline GPU End-to-End Lulus pada Korpus Benih 12 Dokumen; Butuh Korpus Penuh $N=400$ untuk Konvergensi BIO)
- **Tanggal & Waktu (UTC):** `2026-11-19T02:52:23.937039+00:00`
- **Git Commit Hash:** `1f8662b` (`main` di `/content/argumind-project`)
- **Konfigurasi & Parameter:**
  - `arch / mode`: `M1_ArgumindHybrid`
  - `encoder_checkpoint`: `indobenchmark/indobert-base-p2` (BIO Sequence Labeler & Cross-Encoder NLI)
  - `hyperparameters`: `{"bio_epochs": 10, "nli_epochs": 8, "lr": 2e-5, "batch_size": 16}`
  - `dataset_version & split`: `IndoArg-Analytical-v1` seed sample (`manifest sha256 documents.jsonl: c403494e`) | `split: test` (`n_docs = 2`)
- **Random Seed:** `42`
- **Lingkungan Eksekusi (Environment):**
  - `OS`: `Linux (Google Colab VM)`
  - `GPU & VRAM`: `1x NVIDIA Tesla T4 15360MiB, Driver 580.82.07, CUDA 13.0`
  - `Python & PyTorch`: `Python 3.13 | torch 2.14.1+cu130`
- **Perintah Eksekusi (Command):**
  `run_experiment(exp_id="E-01", arch="M1_ArgumindHybrid", data_dir=Path("research/data/processed/v1.0"), split="test", seed=42, output_dir=Path("research/outputs/E-01/colab_seed42"), bio_model_dir=Path("research/outputs/colab_indobert_bio_seed42/best_model"), nli_model_dir=Path("research/outputs/colab_nli_rel_seed42/best_nli_model"))`
- **Hasil Mentah (Tanpa Pembulatan) & Lokasi File Output:**
  - **File Output:**
    - Evaluasi BIO (`F-01`): `research/outputs/colab_indobert_bio_seed42/eval_bio.json` (+ bobot lokal `best_model/model.safetensors`)
    - Evaluasi NLI (`F-02`): `research/outputs/colab_nli_rel_seed42/eval_nli.json` (+ bobot lokal `best_nli_model/model.safetensors`)
    - Config: `research/outputs/E-01/colab_seed42/config_locked.json`
    - Prediksi: `research/outputs/E-01/colab_seed42/predictions.jsonl`
    - Metrik Mentah: `research/outputs/E-01/colab_seed42/metrics_raw.json`
    - Log Proses: `research/outputs/E-01/colab_seed42/run.log`
  - **Angka Asli (`eval_bio.json`, `eval_nli.json`, & `metrics_raw.json`):**
    - `nli_dev_best_relation_macro_f1`: `0.5`
    - `nli_test_relation_support_f1`: `1.0`
    - `nli_test_relation_attack_f1`: `0.0`
    - `nli_test_relation_macro_f1`: `0.5`
    - `bio_dev_best_macro_f1_iou50`: `0.0`
    - `component_macro_f1_exact`: `0.0`
    - `component_macro_f1_iou50`: `0.0`
    - `relation_macro_f1`: `0.0`
    - `cycle_rate`: `0.0`
    - `n_docs`: `2`
    - `latency_total_ms`: `2334.9`
- **Anomali / Error yang Ditemukan:**
  - Pada evaluasi terisolasi pasangan *gold* (`eval_nli.json`), Cross-Encoder NLI + Chu-Liu/Edmonds DAG mencapai `Support F1 = 1.0` dan `macro_f1 = 0.5`. Namun pada evaluasi *end-to-end* (`E-01`), karena partisi `train` korpus benih hanya berisi 8 dokumen (`1` batch per epoch = total `10` langkah gradien), lapisan klasifikasi token `IndoBERT BIO` belum konvergen (`bio_dev_best_macro_f1_iou50 = 0.0`) sehingga batas karakter span belum cocok dengan offset *gold*.
- **Kesimpulan Sementara:**
  - «dugaan» Seluruh pipeline pelatihan GPU di Google Colab, penyimpanan bobot `.safetensors`, dekode DAG Chu-Liu/Edmonds (`cycle_rate = 0.0`), dan inferensi ter-batch (`latency_total_ms = 2334.9` untuk 2 dokumen) telah terverifikasi berfungsi; konvergensi model BIO membutuhkan penambahan ukuran partisi `train` menuju target korpus penuh ($n_{\text{train}} = 280$).

### [LOG-20261119-03] — E-03b (Evaluasi Graph-Grounded Scoring, Faithfulness, & Length Bias di Google Colab T4 GPU)
- **ID Run & Status:** `colab_seed42` | Status: `COMPLETED`
- **Tanggal & Waktu (UTC):** `2026-11-19T02:52:24.400329+00:00`
- **Git Commit Hash:** `1f8662b` (`main` di `/content/argumind-project`)
- **Konfigurasi & Parameter:**
  - `arch / mode`: `M3_GraphGroundedScoring`
  - `dataset_version & split`: `IndoArg-Analytical-v1` seed sample (`manifest sha256 documents.jsonl: c403494e`) | `split: test` (`n_docs = 2`, `n_interventions = 2`)
- **Random Seed:** `42`
- **Lingkungan Eksekusi (Environment):**
  - `OS`: `Linux (Google Colab VM)`
  - `GPU & VRAM`: `1x NVIDIA Tesla T4 15360MiB, CUDA 13.0`
  - `Python & PyTorch`: `Python 3.13 | torch 2.14.1+cu130`
- **Perintah Eksekusi (Command):**
  `run_experiment(exp_id="E-03b", arch="M3_GraphGroundedScoring", data_dir=Path("research/data/processed/v1.0"), split="test", seed=42, output_dir=Path("research/outputs/E-03b/colab_seed42"))`
- **Hasil Mentah (Tanpa Pembulatan) & Lokasi File Output:**
  - **File Output:**
    - Config: `research/outputs/E-03b/colab_seed42/config_locked.json`
    - Prediksi: `research/outputs/E-03b/colab_seed42/predictions.jsonl`
    - Metrik Mentah: `research/outputs/E-03b/colab_seed42/metrics_raw.json`
    - Log Proses: `research/outputs/E-03b/colab_seed42/run.log`
  - **Angka Asli (`metrics_raw.json`):**
    - `qwk_score`: `0.5`
    - `spearman_rho`: `0.0`
    - `partial_corr_length`: `0.0`
    - `faithfulness_rate`: `1.0`
    - `n_interventions`: `2`
    - `latency_total_ms`: `462.37`
- **Anomali / Error yang Ditemukan:**
  - Tidak ada error eksekusi. `spearman_rho = 0.0` terjadi karena kedua dokumen pada partisi `test` korpus benih memiliki rata-rata skor prediksi yang bernilai konstan (*tied ranks* pada $n=2$).
- **Kesimpulan Sementara:**
  - «dugaan» Mekanisme *counterfactual ablation* pada `M3_GraphGroundedScoring` berhasil menurunkan skor dimensi secara konsisten dan memperbarui `grounded_refs` saat node bukti dihapus (`faithfulness_rate = 1.0`, `partial_corr_length = 0.0`).

---

## 3. Pertanyaan Terbuka

1. `TODO(Q-LOG-01 — Pelacak Eksperimen Otomatis)`: Apakah skrip `research.runners.run_experiment` juga akan diintegrasikan dengan pelacak lokal seperti `MLflow` / `Weights & Biases (offline mode)` selain menulis otomatis ke `EXPERIMENT_LOG.md`?
