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

---

## 3. Pertanyaan Terbuka

1. `TODO(Q-LOG-01 — Pelacak Eksperimen Otomatis)`: Apakah skrip `research.runners.run_experiment` juga akan diintegrasikan dengan pelacak lokal seperti `MLflow` / `Weights & Biases (offline mode)` selain menulis otomatis ke `EXPERIMENT_LOG.md`?
