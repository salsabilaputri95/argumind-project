Tujuan: Melacak langkah berikutnya, progres tahapan penelitian, milestone, hambatan (*blockers*), dan status per bagian naskah untuk proyek riset Argumind.
Status dan tanggal: Aktif | 2026-11-18
Sumber kebenaran untuk: Status kesiapan riset, jadwal eksekusi `E-01`–`E-03b`, dan progres penulisan naskah publikasi (`TACL` / `IP&M`).

# Pelacak Progres Penelitian (RESEARCH_PROGRESS.md): Argumind Research

- **Judul Naskah Terkunci:** *Explainable Argument Mining and Implicit Premise Detection for Evaluating Critical Reasoning in Indonesian Analytical Texts*
- **Target Jurnal Utama:** `J-01: TACL` (MIT Press/ACL, Diamond OA `$0 APC`) | **Cadangan:** `J-02: IP&M` (Elsevier, Subscription `$0 APC`)

### Langkah Berikutnya (Maks 3 — Prioritas Sesi Berikutnya)
1. **Jalankan Pelatihan Model di Google Colab:** Hubungkan repo `salsabilaputri95/argumind-project` dan jalankan `research/notebooks/Argumind_Colab_Training.ipynb` untuk melatih `IndoBERT` BIO (`F-01`) dan `Cross-Encoder NLI` (`F-02`).
2. **Pengajuan *Ethical Clearance* & Kalibrasi Anotator:** Ajukan protokol etik ke Komisi Etik (KEPK/IRB) (`→ research/ETHICS.md`) dan gunakan modul `F-06` yang telah siap untuk uji kalibrasi 3 anotator hingga $\alpha_{\text{Krip}} \ge 0.75$.
3. **Ekstraksi Angka PDF Literatur:** Isi nilai metrik eksak (`TODO(ekstrak ...)`) pada tabel `research/LITERATURE_REVIEW.md` dari 10 PDF ACL Anthology terverifikasi.

---

## 1. Checklist Tahapan Penelitian

| Tahap Penelitian | Deskripsi Tugas Utama | Penanggung Jawab | Tenggat Target (`ASUMSI`) | Status (`todo \| doing \| done \| blocked`) |
|---|---|---|---|---|
| **1. Pustaka (*Literature*)** | Strategi pencarian `2020–2026`, 10 studi terverifikasi + tautan ACL Anthology, sintesis 3 tema, & `references.bib` | Peneliti Utama | Minggu ke-1 | `done` (`references.bib` & DOI terverifikasi; metrik rinci PDF opsional) |
| **2. Desain (*Design*)** | Rumusan `RQ1`–`RQ3`, `H1`–`H3b`, metodologi `M1`–`M3`, datasheet `DATASET.md`, & rencana `E-01`–`E-03b` | Peneliti Utama | Minggu ke-1 | `done` (Menunggu pengisian `AUTHORS_CONTRIBUTIONS.md`) |
| **3. Data (*Corpus*)** | Pengumpulan $N=400$ dokumen (`200 academic`, `200 policy`), redaksi PII, anotasi *double-blind*, & adjudikasi ($\alpha_{\text{Krip}} \ge 0.75$) | Ko-Penulis Data & 3 Anotator | Minggu ke-2 s.d. ke-6 | `doing` (Korpus benih `v1.0` & UI `F-06` siap; butuh `BLK-R01` untuk esai mahasiswa) |
| **4. Eksperimen (*Experiments*)** | Eksekusi multi-seed `[42, 100, 2026]` untuk `E-01`, `E-02a`, `E-02b`, `E-03a`, dan `E-03b` + pencatatan di `EXPERIMENT_LOG.md` | Ko-Penulis Komputasi | Minggu ke-7 s.d. ke-8 | `doing` (Runner, paket metrik 97% cov, smoke run `[LOG-20261118-01]`, & Colab notebook siap) |
| **5. Analisis (*Analysis*)** | Uji *Paired Bootstrap* ($B=10.000$), *Wilcoxon*, *Holm-Bonferroni*, analisis error kualitatif, & penghapusan label `«dugaan»` | Peneliti Utama & Komputasi | Minggu ke-9 | `todo` |
| **6. Penulisan (*Writing*)** | Penyusunan naskah lengkap sesuai template `TACL` (`7–10 halaman`) / `IP&M` beserta tabel LaTeX dari `summary_tables.json` | Seluruh Penulis | Minggu ke-10 s.d. ke-11 | `todo` |
| **7. Revisi Internal** | Audit *double-blind*, cek ulang angka naskah vs `metrics_raw.json`, dan uji reprodusibilitas di container bersih | Seluruh Penulis | Minggu ke-12 | `todo` |
| **8. Submit (*Submission*)** | Pengiriman naskah + repositori anonim + deklarasi AI & etik ke portal jurnal (`TACL` / `IP&M`) | Peneliti Korespondensi | Minggu ke-12 (Tgl 1) | `todo` |
| **9. Revisi Reviewer** | Eksperimen tambahan (*rebuttal*), penyusunan *response letter*, dan penyiapan berkas *camera-ready* + DOI Zenodo | Seluruh Penulis | Pasca-Keputusan Review | `todo` |

---

## 2. Milestone Utama

- **M1 (Minggu 1):** Seluruh dokumen desain riset, `references.bib`, paket `evaluation-metrics`, runner eksperimen, & notebook Google Colab terkunci — **`TERCAPAI (2026-11-18)`**.
- **M2 (Minggu 3):** Surat *Ethical Clearance* terbit & kalibrasi anotator mencapai $\alpha_{\text{Krip}} \ge 0.75$ pada 20 dokumen awal.
- **M3 (Minggu 6):** Rilis beku `IndoArg-Analytical-v1` ($N=400$: `280 train / 60 dev / 60 test`) beserta `manifest.sha256`.
- **M4 (Minggu 9):** Seluruh eksperimen `E-01`–`E-03b` selesai dijalankan dan tercatat lengkap di `EXPERIMENT_LOG.md`.
- **M5 (Minggu 12):** Naskah lulus checklist 10 butir `JOURNAL_TARGET.md` dan dikirimkan (*submitted*).

---

## 3. Tabel Blocker Riset Aktif

| ID Blocker | Masalah yang Memblokir | Dampak | Solusi / Butuh Dari Siapa |
|---|---|---|---|
| **BLK-R01** | Nomor persetujuan *Ethical Clearance* (KEPK/IRB) belum terbit (`TODO(Q-ETH-01)`). | Memblokir pengumpulan esai mahasiswa (`academic` strata); pengumpulan dokumen kebijakan publik tetap bisa jalan. | Peneliti Utama & Komisi Etik Institusi |
| **BLK-R03** | Dokumen `research/AUTHORS_CONTRIBUTIONS.md` sengaja ditunda. | Memblokir kelengkapan deklarasi CRediT penulis sebelum *submission*. | Instruksi Peneliti Utama |

---

## 4. Status per Bagian Naskah Ilmiah

| Bagian Naskah (`→ research/JOURNAL_TARGET.md`) | Sumber Materi di Repositori | Status Saat Ini (`belum mulai \| draf \| revisi \| final`) |
|---|---|---|
| **Title & Abstract** | `RESEARCH_BRIEF.md` (Judul Opsi A telah final) | `draf` |
| **1. Introduction (`RQ1`–`RQ3`, `C-01`–`C-04`)** | `RESEARCH_BRIEF.md` | `draf` |
| **2. Related Work / Literature Review** | `LITERATURE_REVIEW.md`, `references.bib` (10 studi 2020–2025) | `draf` |
| **3. Corpus Construction (`IndoArg-Analytical-v1`)** | `DATASET.md`, `ETHICS.md` | `draf` (Menunggu statistik aktual pasca-anotasi) |
| **4. Proposed Methodology (`M1`–`M3`)** | `METHODOLOGY.md`, `DECISIONS.md` (`ADR-05`, `ADR-06`) | `draf` |
| **5. Experimental Setup (`E-01`–`E-03b`)** | `EXPERIMENT_PLAN.md`, `REPRODUCIBILITY.md` | `draf` |
| **6. Results, Ablation, & Discussion** | `EXPERIMENT_LOG.md`, `outputs/summary_tables.json` | `belum mulai` (Menunggu hasil eksperimen penuh) |
| **7. Conclusion, Limitations, & Ethics Statement** | `RESEARCH_BRIEF.md`, `ETHICS.md`, `AI_USAGE.md` | `draf` |
