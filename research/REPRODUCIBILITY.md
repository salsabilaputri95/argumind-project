Tujuan: Menetapkan spesifikasi lingkungan perangkat keras/lunak, penguncian dependensi, verifikasi checksum dataset, prosedur eksekusi dari nol, kontrol determinisme seed, batas toleransi variasi hasil, estimasi sumber daya, serta metadata `CITATION.cff` untuk proyek Argumind.
Status dan tanggal: Draft v1.0 (Pra-Verifikasi Mesin Bersih) | 2026-11-18
Sumber kebenaran untuk: Protokol reprodusibilitas eksperimen `E-01`–`E-03b`, pengaturan determinisme PyTorch/CUDA, dan paket artefak publikasi ilmiah.

# Panduan Reprodusibilitas (Reproducibility Guide): Explainable Argument Mining and Implicit Premise Detection for Evaluating Critical Reasoning in Indonesian Analytical Texts

> **Peringatan Status Uji Mesin Bersih (*Clean-Machine Verification*):** Sesuai aturan penulisan, dokumen ini **JANGAN** mengklaim bahwa barisan perintah di bawah telah lulus uji mesin bersih sebelum skrip `research/runners/` selesai diimplementasikan. Seluruh langkah di Bagian 4 berstatus **`[PENDING CLEAN-CONTAINER VERIFICATION]`** (`TODO(jalankan dan verifikasi di container Ubuntu 22.04 bersih sebelum pengiriman naskah jurnal)`).

---

## 1. Spesifikasi Lingkungan Komputasi (Hardware & Software)

| Komponen Lingkungan | Spesifikasi Minimum (Reproduksi Evaluasi) | Spesifikasi Referensi (Pelatihan & Eksperimen Penuh) |
|---|---|---|
| **Sistem Operasi (OS)** | Linux `Ubuntu 22.04.5 LTS` (Kernel `>= 5.15`, `x86_64`) atau Windows 11 via `WSL2 Ubuntu 22.04` | `Ubuntu 22.04.5 LTS` di dalam Docker Container (`nvidia/cuda:12.4.1-cudnn-devel-ubuntu22.04`) |
| **Bahasa & Runtime** | `Python 3.12.7` (`CPython`), `Node.js 22.11.0 LTS` (hanya jika menjalankan UI anotasi `F-06`) | `Python 3.12.7` (`CPython`) |
| **GPU & Akselerator** | `1x NVIDIA T4 (16 GB VRAM)` atau `RTX 3090/4090 (24 GB VRAM)`, Driver `>= 550.54`, `CUDA 12.4` | `1x NVIDIA L4 (24 GB VRAM)` atau `1x NVIDIA A100 (40/80 GB VRAM)` jika menjalankan `EXT-LLM` lokal via `vLLM` |
| **CPU & Memori (RAM)** | `8 vCPU`, `32 GB RAM` | `16 vCPU`, `64 GB RAM` |
| **Ruang Penyimpanan Disk** | `50 GB SSD` bebas (korpus + cache *checkpoint* `IndoBERT` & NLI) | `120 GB NVMe SSD` bebas (termasuk bobot model LLM *open-weights* + artefak `research/outputs/`) |

---

## 2. Penguncian Dependensi (Lockfiles)

Untuk mencegah pergeseran versi library (*dependency drift*), lingkungan eksperimen WAJIB diinstal dari berkas pengunci deterministik:
1. **Python Lockfile:** `research/requirements.lock` (dihasilkan melalui `uv pip compile pyproject.toml --generate-hashes -o research/requirements.lock` atau `poetry.lock`).
2. **Versi Library Inti Wajib (`ASUMSI: dikunci saat inisialisasi repo`):**
   - `torch==2.5.1+cu124`
   - `transformers==4.46.2`
   - `datasets==3.1.0`
   - `accelerate==1.1.1`
   - `bert-score==0.3.13`
   - `scikit-learn==1.5.2`
   - `scipy==1.14.1`
   - `krippendorff==0.6.1`
   - `networkx==3.4.2`
   - `pydantic==2.10.1`
3. **Aturan Instalasi:** JANGAN menjalankan `pip install <paket>` tanpa flag `--require-hashes -r research/requirements.lock` pada mesin eksperimen.

---

## 3. Lokasi Data, Checksum, dan Cara Unduh

Mengacu pada spesifikasi di `→ research/DATASET.md#8-lokasi-versi-checksum-dan-cara-akses`:
- **Lokasi Lokal:** `research/data/processed/v1.0/` (`documents.jsonl`, `nodes.jsonl`, `edges.jsonl`, `gaps.jsonl`, `rubric_scores.jsonl`).
- **Repositori Arsip Eksternal:** `TODO(isi URL Zenodo / HuggingFace Datasets setelah dataset v1.0 dibekukan)`.
- **Berkas Checksum:** `research/data/processed/v1.0/manifest.sha256`.
- **Aturan Wajib:** Skrip unduh dan pra-cek WAJIB memverifikasi seluruh hash `SHA-256` 64-karakter. JANGAN menyertakan atau memodifikasi isi `research/data/raw/` (`→ research/DATASET.md`).

---

## 4. Prosedur Eksekusi dari Nol (Urutan Perintah)

> **Status Verifikasi:** `TODO(Uji urutan perintah ini pada mesin/container bersih tanpa cache lokal dan catat commit hash hasil ujinya di EXPERIMENT_LOG.md)`.

```bash
# Langkah 1: Kloning repositori dan pindah ke commit rilis eksperimen
git clone <TODO_REPO_URL> argumind
cd argumind
git checkout <TODO_RELEASE_TAG_OR_COMMIT_HASH>

# Langkah 2: Buat virtual environment terisolasi dan instal dependensi terkunci
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip==24.3.1
pip install --no-cache-dir -r research/requirements.lock

# Langkah 3: Unduh korpus IndoArg-Analytical-v1 dan verifikasi integritas SHA-256
python -m research.scripts.download_corpus --version v1.0 --target-dir research/data/processed/v1.0
sha256sum -c research/data/processed/v1.0/manifest.sha256

# Langkah 4: Jalankan Eksperimen E-01 (RQ1 - Ekstraksi Komponen & Relasi, 3 Seed)
for SEED in 42 100 2026; do
  python -m research.runners.run_experiment \
    --exp-id E-01 --arch B1_EncoderOnly \
    --data-dir research/data/processed/v1.0 --split test --seed $SEED \
    --output-dir research/outputs/E-01/B1_seed${SEED}

  python -m research.runners.run_experiment \
    --exp-id E-01 --arch M1_ArgumindHybrid \
    --data-dir research/data/processed/v1.0 --split test --seed $SEED \
    --output-dir research/outputs/E-01/M1_seed${SEED}
done

# Langkah 5: Jalankan Eksperimen E-02a (Oracle) & E-02b (End-to-End) untuk RQ2
for SEED in 42 100 2026; do
  python -m research.runners.run_experiment \
    --exp-id E-02a --arch M2_GraphNLIConditioned --graph-source oracle \
    --data-dir research/data/processed/v1.0 --split test --seed $SEED \
    --output-dir research/outputs/E-02a/M2_oracle_seed${SEED}

  python -m research.runners.run_experiment \
    --exp-id E-02b --arch M2_GraphNLIConditioned --graph-source predicted \
    --pred-graph-dir research/outputs/E-01/M1_seed${SEED} \
    --data-dir research/data/processed/v1.0 --split test --seed $SEED \
    --output-dir research/outputs/E-02b/M2_e2e_seed${SEED}
done

# Langkah 6: Jalankan Eksperimen E-03a (Keselarasan Rubrik) & E-03b (Faithfulness Ablation)
for SEED in 42 100 2026; do
  python -m research.runners.run_experiment \
    --exp-id E-03a --arch M3_GraphGroundedScoring \
    --pred-graph-dir research/outputs/E-02b/M2_e2e_seed${SEED} \
    --data-dir research/data/processed/v1.0 --split test --seed $SEED \
    --output-dir research/outputs/E-03a/M3_seed${SEED}
done

python -m research.runners.run_experiment \
  --exp-id E-03b --arch M3_GraphGroundedScoring \
  --data-dir research/data/processed/v1.0 --split test --seed 42 \
  --output-dir research/outputs/E-03b/M3_counterfactual_seed42

# Langkah 7: Agregasi tabel statistik (Paired Bootstrap B=10000 & Holm-Bonferroni)
python -m research.runners.aggregate_results \
  --outputs-root research/outputs \
  --bootstrap-samples 10000 \
  --seed 42 \
  --export-tables research/outputs/summary_tables.json
```

---

## 5. Kontrol Determinisme dan Random Seed

Seluruh skrip pada `research/runners/` WAJIB memanggil fungsi pengunci seed global dengan daftar seed resmi **`[42, 100, 2026]`** (`→ research/EXPERIMENT_PLAN.md#2-tabel-skenario-eksperimen-e-01-sd-e-03b`):
- Variabel lingkungan wajib sebelum impor PyTorch:
  - `PYTHONHASHSEED=<SEED>`
  - `CUBLAS_WORKSPACE_CONFIG=:4096:8`
- Pengaturan API di dalam Python:
  - `random.seed(seed)`, `np.random.seed(seed)`, `torch.manual_seed(seed)`, `torch.cuda.manual_seed_all(seed)`
  - `torch.use_deterministic_algorithms(True)`
  - `torch.backends.cudnn.deterministic = True` dan `torch.backends.cudnn.benchmark = False`
- Parameter inferensi LLM utama WAJIB menggunakan `temperature = 0.0`, `top_p = 1.0`, dan parameter `seed = <SEED>`.

---

## 6. Tabel Pemetaan Hasil → Perintah → File Output → Toleransi Variasi

| Klaim / Tabel Hasil (`→ research/RESEARCH_BRIEF.md`) | Skenario & Perintah | Lokasi File Output Utama | Toleransi Variasi Lintas Mesin ($\pm\epsilon$) |
|---|---|---|---|
| **Tabel 1 (`RQ1` — `H1`):** `component_macro_f1`, `relation_macro_f1`, & `cycle_rate` | Langkah 4 (`--exp-id E-01`, rata-rata 3 seed) | `research/outputs/E-01/*/metrics_raw.json` & `summary_tables.json` | $\pm 0.0000$ pada GPU & CUDA identik; $\le \pm 0.0030$ (`0.3%` F1) lintas arsitektur GPU berbeda; `cycle_rate` WAJIB eksak `0.0000`. |
| **Tabel 2 (`RQ2` — `H2` Oracle & E2E):** `implicit_bertscore_f1` & `gap_macro_f1` | Langkah 5 (`--exp-id E-02a` dan `E-02b`) | `research/outputs/E-02a/*/metrics_raw.json` & `research/outputs/E-02b/*/metrics_raw.json` | $\le \pm 0.0020$ pada `BERTScore-F1` dengan model *self-hosted* `vLLM` deterministik (`temp=0.0`); $\le \pm 0.0080$ jika menggunakan endpoint API komersial. |
| **Tabel 3 (`RQ3` — `H3a`):** Kesepakatan Skor Rubrik (`qwk_score`, `spearman_rho`) | Langkah 6 (`--exp-id E-03a`) | `research/outputs/E-03a/*/metrics_raw.json` | $\le \pm 0.0050$ pada `QWK` dan Spearman $\rho$; perhitungan `QWK` antar-pakar manusia bersifat deterministik eksak ($\pm 0.0000$). |
| **Tabel 4 (`RQ3` — `H3b`):** `faithfulness_rate` & Bias Panjang ($\rho_{YL \cdot H}$) | Langkah 6 (`--exp-id E-03b`) | `research/outputs/E-03b/M3_counterfactual_seed42/metrics_raw.json` | $\le \pm 0.0050$ pada `faithfulness_rate` dan $|\rho_{YL \cdot H}|$. |

---

## 7. Estimasi Waktu Eksekusi dan Sumber Daya Komputasi

*Seluruh angka durasi di bawah menggunakan `ASUMSI: estimasi pada 1x GPU NVIDIA L4 24GB untuk N_doc = 400` dan WAJIB diperbarui dengan angka aktual dari `EXPERIMENT_LOG.md`:*

| Tahap Eksperimen | Estimasi Waktu per Seed (`ASUMSI`) | Total Waktu (3 Seed) | Kebutuhan VRAM Puncak | Penggunaan Disk Output |
|---|---|---|---|---|
| Verifikasi & Pra-pemrosesan Korpus (`Langkah 3`) | `~5 menit` (sekali jalan) | `~5 menit` | `< 2 GB` (CPU + NER) | `~25 MB` |
| Pelatihan & Evaluasi `E-01` (`B1`, `M1`, dan Ablasi) | `~45 menit / seed` | `~2 jam 15 menit` | `~14.5 GB VRAM` | `~4.5 GB` (*checkpoints*) |
| Inferensi `E-02a` & `E-02b` ($n_{\text{test}} = 60$ dok) | `~20 menit / seed` | `~1 jam 00 menit` | `~16.0 GB VRAM` (jika lokal) | `~120 MB` |
| Evaluasi `E-03a` & Ablasi Kontrafaktual `E-03b` ($M \approx 180$) | `~35 menit` | `~1 jam 15 menit` | `~16.0 GB VRAM` | `~150 MB` |
| Bootstrap Resampling ($B = 10.000$, `Langkah 7`) | `~3 menit` (CPU) | `~3 menit` | `0 GB` (CPU `8 threads`) | `~10 MB` |
| **Total Keseluruhan Reproduksi Dari Nol** | — | **`~4 jam 38 menit`** | **Maks `16.0 GB VRAM`** | **`~5.0 GB`** |

---

## 8. DOI Arsip, Lisensi Artefak, dan Berkas `CITATION.cff`

- **DOI Arsip Kode & Dataset (Zenodo):** `TODO(daftarkan dan isi DOI Zenodo permanen, mis. 10.5281/zenodo.XXXXXXX saat pembekuan rilis v1.0.0)`.
- **Lisensi Kode Sumber Eksperimen:** `Apache License 2.0` (`LICENSE-CODE`).
- **Lisensi Dataset `IndoArg-Analytical-v1`:** `CC BY-NC-SA 4.0` (`LICENSE-DATA`, `→ research/DATASET.md#7-lisensi-izin-penggunaan-pii-dan-keterbatasan`).

### Isi Berkas `CITATION.cff` (Simpan di Root Repositori)

```yaml
cff-version: 1.2.0
message: "Jika Anda menggunakan kode, model, atau korpus IndoArg-Analytical dari repositori ini, mohon sitasi menggunakan metadata berikut."
title: "Explainable Argument Mining and Implicit Premise Detection for Evaluating Critical Reasoning in Indonesian Analytical Texts"
version: "1.0.0"
date-released: "2026-11-18"
license: "Apache-2.0"
repository-code: "https://github.com/TODO-ORG/argumind"
doi: "10.5281/zenodo.TODO"
authors:
  - family-names: "TODO(Nama Belakang Penulis 1)"
    given-names: "TODO(Nama Depan Penulis 1)"
    orcid: "https://orcid.org/0000-0000-0000-0000"
    affiliation: "TODO(Afiliasi Institusi)"
keywords:
  - "argument mining"
  - "implicit premise detection"
  - "explainable AI"
  - "critical reasoning"
  - "Indonesian NLP"
```

---

## 9. Pertanyaan Terbuka

1. `TODO(Q-REPRO-01 — Kontainerisasi Docker vs Conda/uv)`: Apakah artefak reprodusibilitas yang akan disertakan untuk reviewer jurnal berupa `Dockerfile` lengkap beserta *docker-compose* atau paket skrip `uv` / `requirements.lock`?
