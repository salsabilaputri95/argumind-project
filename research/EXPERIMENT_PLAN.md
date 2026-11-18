Tujuan: Menetapkan rencana skenario eksperimen (`E-01`–`E-03b`), konfigurasi variabel, partisi dataset, metrik, kriteria keberhasilan, jumlah ulangan, dan seed untuk proyek Argumind.
Status dan tanggal: Draft v1.0 | 2026-11-18
Sumber kebenaran untuk: Matriks eksekusi eksperimen `E-01` s.d. `E-03b`, parameter faktor ablasi, dan protokol pengulangan multi-seed.

# Rencana Eksperimen (Experiment Plan): Explainable Argument Mining and Implicit Premise Detection for Evaluating Critical Reasoning in Indonesian Analytical Texts

---

## 1. Aturan Eksekusi Eksperimen

1. **Isolasi Partisi Data:** Seluruh pelatihan model dan *hyperparameter tuning* WAJIB hanya menggunakan partisi `train` ($n = 280$) dan `dev` ($n = 60$) dari `IndoArg-Analytical-v1` (`→ research/DATASET.md#5-pembagian-train-validation-dev-dan-test`). Partisi `test` ($n = 60$) WAJIB dibekukan dan hanya dievaluasi satu kali per konfigurasi final yang terkunci.
2. **Pencatatan Log Wajib:** Setiap eksekusi skrip eksperimen (termasuk yang gagal, *timeout*, atau tidak mencapai target hipotesis) WAJIB langsung dicatat secara *append-only* ke dalam `→ research/EXPERIMENT_LOG.md` tanpa pembulatan angka.
3. **Verifikasi Integritas Sebelum Run:** Sebelum memulai `E-01`–`E-03b`, skrip runner WAJIB memverifikasi checksum `research/data/processed/v1.0/manifest.sha256` (`→ research/DATASET.md#8-lokasi-versi-checksum-dan-cara-akses`). JANGAN menjalankan eksperimen jika verifikasi checksum gagal.

---

## 2. Tabel Skenario Eksperimen (`E-01` s.d. `E-03b`)

Definisi variabel, baseline (`B1`–`B5`), model (`M1`–`M3`), dan rumus metrik mengacu pada `→ research/METHODOLOGY.md#2-variabel-definisi-operasional-dan-skala-ukur-per-rq` dan `→ research/METHODOLOGY.md#6-baseline-pembanding-dan-rumus-metrik-evaluasi`.

| ID | RQ | Hipotesis | Variabel yang Diubah (IV) | Konfigurasi & Parameter Eksplisit | Dataset dan Split | Metrik Evaluasi | Kriteria Keberhasilan | Jumlah Ulangan | Seed |
|---|---|---|---|---|---|---|---|---|---|
| **`E-01`** | `RQ1` | `H1` | `model_arch_rq1`:<br>1. `B1_EncoderOnly`<br>2. `B2_ZeroShotLLM`<br>3. `M1_NoDAG` (Ablasi tanpa Chu-Liu/Edmonds)<br>4. `M1_NoLLMRefine` (Ablasi tanpa refinement)<br>5. `M1_ArgumindHybrid` (Penuh) | • Encoder: `AdamW`, `lr = 2e-5`, `batch_size = 16`, `max_len = 512`, `stride = 128`, `epochs = 10` (`patience = 3`).<br>• Refinement threshold: entropi token $> 0.45$.<br>• Decoding LLM (`B2` & `M1`): `temperature = 0.0`, `top_p = 1.0`. | `IndoArg-Analytical-v1` (`documents.jsonl`, `nodes.jsonl`, `edges.jsonl`); Latih di `train` ($280$), tuning di `dev` ($60$), uji akhir di `test` ($60$). | • `component_macro_f1` (Exact $\text{IoU}=1.0$ & Partial $\text{IoU}\ge 0.5$)<br>• `relation_macro_f1` (`Support`/`Attack`)<br>• Tingkat pelanggaran DAG (`cycle_rate`) | `M1_ArgumindHybrid` mengungguli `B1` dan `B2` dengan $\Delta\text{Macro-F1}_{\text{comp}} \ge +0.0500$ dan $\Delta\text{Macro-F1}_{\text{rel}} \ge +0.0700$ ($p < 0.05$, *paired bootstrap* $B=10.000$); `cycle_rate == 0.0000`. | `3x` ulangan penuh untuk pelantikan *encoder* (`B1`, `M1`); `1x` deterministik (`temp=0.0`) untuk `B2`. | `[42, 100, 2026]` |
| **`E-02a`**<br>*(Mode Oracle)* | `RQ2` | `H2` | `conditioning_mode_rq2`:<br>1. `B3_TextOnlyPrompt`<br>2. `B4_CoTPrompt` (3-shot)<br>3. `M2_NoNLI` (Ablasi sub-graf tanpa skor NLI)<br>4. `M2_GraphNLIConditioned` (Penuh) | • Input struktur menggunakan graf *gold standard* (`oracle`) untuk mengisolasi kemampuan murni modul `F-03`.<br>• Pemicu NLI: pasangan `Support` dengan $p_{\text{neutral}} + p_{\text{contradict}} \ge 0.40$.<br>• LLM: JSON Schema terikat, `temperature = 0.0`. | `IndoArg-Analytical-v1` (`nodes.jsonl`, `edges.jsonl`, `gaps.jsonl`); Evaluasi pada partisi `test` ($n = 60$ dokumen) + penilaian *blind* 3 pakar. | • `implicit_bertscore_f1`<br>• `expert_validity_rate` (proporsi skor pakar $\ge 4$)<br>• `gap_macro_f1` (6 kelas `ReasoningGap`) | `implicit_bertscore_f1` $\ge 0.7800$; `expert_validity_rate` $\ge 0.7500$ dan naik $\ge +0.1500$ dibanding `B3`/`B4` ($p < 0.05$, *Wilcoxon signed-rank*). | `3x` sampling untuk uji stabilitas (`temp=0.2` pada uji sensitivitas) + `1x` utama (`temp=0.0`). | `[42, 100, 2026]` |
| **`E-02b`**<br>*(Mode End-to-End)* | `RQ2` | `H2` | Sama dengan `E-02a`, namun input graf berasal dari prediksi terbaik `M1_ArgumindHybrid` pada `E-01` (`graph_source = "predicted"`). | Mengukur dampak propagasi error (*error propagation*) dari `F-01`/`F-02` terhadap kualitas `ImplicitPremise` dan `ReasoningGap` (`→ research/METHODOLOGY.md#7-ancaman-validitas-threats-to-validity-dan-mitigasi`). | Partisi `test` ($n = 60$ dokumen) dengan input node/edge hasil keluaran `E-01`. | • `implicit_bertscore_f1`<br>• `gap_macro_f1`<br>• Penurunan relatif ($\Delta_{\text{drop}}$) terhadap `E-02a`. | `M2_GraphNLIConditioned` tetap unggul signifikan ($p < 0.05$) atas `B3` dan `B4`; penurunan $\Delta_{\text{drop}}$ BERTScore dibanding `E-02a` $\le 0.0400$. | `3x` (mengikuti 3 *checkpoint* seed `E-01`). | `[42, 100, 2026]` |
| **`E-03a`**<br>*(Keselarasan Pakar)* | `RQ3` | `H3a` | `scoring_mechanism_rq3`:<br>1. `B5_DirectLLMScoring`<br>2. `M3_OracleGraphScoring`<br>3. `M3_GraphGroundedScoring` (End-to-End) | • Penilaian 4 dimensi rubrik skala `1..5` (`ClarityOfClaim`, `PremiseSupportAndCoherence`, `EvidenceAdequacy`, `CounterargumentAndLimitationAwareness`).<br>• Validasi wajib `jsonb_array_length(grounded_refs) >= 1`. | `IndoArg-Analytical-v1` (`rubric_scores.jsonl`), partisi `test` ($n = 60$ dokumen $\times 4$ dimensi = $240$ skor dimensi) yang dinilai *blind* oleh 3 pakar. | • `qwk_score` per dimensi & gabungan<br>• `spearman_rho` ($\rho$) terhadap rata-rata 3 pakar<br>• MAE (*Mean Absolute Error*) | `qwk_score` $\ge 0.7000$ dan `spearman_rho` $\ge 0.7000$ ($p < 0.01$) pada keempat dimensi rubrik. | `3x` (mengikuti 3 seed graf `E-01`/`E-02b`). | `[42, 100, 2026]` |
| **`E-03b`**<br>*(Faithfulness & Length Bias)* | `RQ3` | `H3b` | `intervention_type`:<br>1. Penghapusan kontrafaktual node `Evidence` / `ExplicitPremise` yang ada di `grounded_refs`<br>2. Evaluasi korelasi parsial lintas strata panjang (`short`, `medium`, `long`). | • Untuk setiap dokumen `test`, hapus 1 per 1 node `Evidence` dari graf & teks, lalu jalankan ulang `B5` dan `M3`.<br>• Hitung korelasi parsial panjang kata $L$ terhadap skor sistem $Y$ dengan mengontrol skor pakar $H$. | Partisi `test` ($n = 60$ dokumen asli + $M \approx 180$ dokumen kontrafaktual terablasi). | • `faithfulness_rate`<br>• `partial_corr_length` ($\rho_{YL \cdot H}$)<br>• Tingkat penolakan skema (`unfaithful_schema_reject_rate`) | `faithfulness_rate` $\ge 0.8500$ (unggul signifikan atas `B5` via uji McNemar, $p < 0.01$); $|\rho_{YL \cdot H}| \le 0.2000$. | `1x` deterministik pada seluruh instance ablasi $M$ (`temp = 0.0`). | `42` |

---

## 3. Pola Perintah Eksekusi dan Lokasi Artefak Keluaran

Setiap skenario WAJIB dijalankan melalui CLI terstandar yang menyimpan konfigurasi dan hasil mentah ke `research/outputs/{exp_id}/{run_id}/`:

```bash
# Contoh minimal eksekusi E-01 dengan seed 42:
python -m research.runners.run_experiment \
  --exp-id E-01 \
  --arch M1_ArgumindHybrid \
  --data-dir research/data/processed/v1.0 \
  --split test \
  --seed 42 \
  --output-dir research/outputs/E-01/run_20261118_seed42
```

Setiap direktori `research/outputs/{exp_id}/{run_id}/` WAJIB menghasilkan 4 berkas berikut:
1. `config_locked.json` — Salinan parameter lengkap, versi library, dan hash SHA-256 dataset.
2. `predictions.jsonl` — Prediksi level dokumen/node/edge/skor sebelum agregasi.
3. `metrics_raw.json` — Angka metrik penuh tanpa pembulatan beserta interval kepercayaan *bootstrap* 95%.
4. `run.log` — Log standar eksekusi, latensi, dan tangkapan error/anomali.

---

## 4. Pertanyaan Terbuka

1. `TODO(Q-EXP-01 — Kuota Token Eksperimen)`: Apakah anggaran pemanggilan LLM untuk pengulangan `3x` seed pada `E-02a`, `E-02b`, dan `E-03b` ($M \approx 180$ ablasi kontrafaktual) sudah disetujui, atau uji sensitivitas `temp=0.2` pada `E-02a` cukup dijalankan pada subset `30` dokumen?
