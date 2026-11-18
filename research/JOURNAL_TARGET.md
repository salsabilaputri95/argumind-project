Tujuan: Menetapkan jurnal target utama dan cadangan (diutamakan bebas biaya publikasi / $0 APC), spesifikasi format naskah, aturan sitasi, kebijakan *peer review*, deklarasi AI, dan checklist pengiriman untuk publikasi riset Argumind.
Status dan tanggal: Draft v1.0 (Diverifikasi terhadap halaman resmi penerbit pada 2026-11-18) | 2026-11-18
Sumber kebenaran untuk: Pemilihan venue publikasi, format template LaTeX/Word, batas halaman/kata, dan syarat *submission* naskah *"Explainable Argument Mining and Implicit Premise Detection for Evaluating Critical Reasoning in Indonesian Analytical Texts"*.

# Target Jurnal & Panduan Pengiriman (Journal Target): Argumind Research

> **Catatan Verifikasi Sumber Resmi:** Seluruh ketentuan di bawah ini diverifikasi terhadap halaman resmi penerbit pada tanggal **`2026-11-18`**. Sesuai instruksi, seluruh kandidat mengutamakan skema **Gratis ($0 APC bagi penulis)** melalui skema *Diamond Open Access* (`TACL`) atau *Hybrid Subscription Option* (`IP&M` dan `IJAIED`).

---

## 1. Perbandingan Jurnal Utama dan Jurnal Cadangan (Prioritas Gratis / $0 APC)

| Atribut | **Target Utama (`J-01`)** | **Target Cadangan 1 (`J-02`)** | **Target Cadangan 2 (`J-03`)** |
|---|---|---|---|
| **Nama Jurnal** | **Transactions of the Association for Computational Linguistics (`TACL`)** | **Information Processing & Management (`IP&M`)** | **International Journal of Artificial Intelligence in Education (`IJAIED`)** |
| **Penerbit** | MIT Press / Association for Computational Linguistics (ACL) | Elsevier Ltd. | Springer Nature (atas nama International AIED Society) |
| **Indeksasi & Kuartil** | Scopus `Q1`, Web of Science (SCIE), ACL Anthology | Scopus `Q1`, Web of Science (SSCI / SCIE) | Scopus `Q1`, Web of Science (ESCI / SSCI) |
| **Biaya Publikasi (APC)** | **GRATIS (`$0 USD` — Diamond Open Access):** Bebas biaya *submission* dan bebas biaya APC; artikel langsung terbuka gratis bagi pembaca. | **GRATIS (`$0 USD` — Opsi Subscription):** Penulis memilih opsi *Subscription* saat diterima (`$0 APC`). *(Opsi Gold OA berbayar tidak dipilih).* | **GRATIS (`$0 USD` — Opsi Subscription):** Penulis memilih publikasi *Subscription / Traditional* (`$0 APC`). *(Opsi Open Choice tidak dipilih).* |
| **Estimasi Waktu Review** | Siklus *rolling bulanan*: keputusan putaran pertama $\approx 6\text{–}8\text{ minggu}$ sejak tenggat bulanan. | *First decision* rata-rata $\approx 6\text{–}10\text{ minggu}$ (berdasarkan halaman statistik jurnal Elsevier). | *First decision* rata-rata $\approx 8\text{–}12\text{ minggu}$ via Editorial Manager. |
| **Kesesuaian Scope dengan Argumind** | Sangat tinggi untuk kontribusi komputasional `RQ1`–`RQ3` (*argument mining*, *implicit premise*, *faithfulness* NLP Bahasa Indonesia). | Sangat tinggi untuk sistem pemrosesan informasi terapan, *decision support*, dan evaluasi kesepakatan manusia-AI. | Sangat tinggi jika menekankan evaluasi esai akademik (`academic` strata) dan umpan balik rubrik diagnostik. |
| **URL Resmi Author Guidelines** | https://transacl.org/index.php/tacl/about/submissions | https://www.sciencedirect.com/journal/information-processing-and-management/publish/guide-for-authors | https://link.springer.com/journal/40593/submission-guidelines |
| **Tanggal Pengecekan** | `2026-11-18` | `2026-11-18` | `2026-11-18` |

---

## 2. Spesifikasi Format dan Teknis Naskah (`J-01: TACL` vs `J-02: IP&M`)

| Komponen Format | Ketentuan Resmi **`J-01: TACL`** (Utama — Diamond OA Gratis) | Ketentuan Resmi **`J-02: IP&M`** (Cadangan 1 — Elsevier Subscription Gratis) |
|---|---|---|
| **Template Resmi** | Wajib LaTeX dua kolom menggunakan paket resmi ACL/TACL (`tacl2021v1.sty` / `acl.sty`, ukuran kertas `A4`, font minimal `11pt`). | Mendukung *Your Paper Your Way* (PDF/Word satu kolom atau LaTeX `elsarticle.cls` saat *initial submission*). |
| **Batas Halaman / Kata** | **Ketat: `7 s.d. 10 halaman`** konten utama (termasuk gambar/tabel, **tidak termasuk** daftar pustaka dan lampiran/appendix). Naskah $< 7$ atau $> 10$ halaman langsung terkena *desk-reject*. | Panjang artikel riset standar **`5.000 s.d. 10.000 kata`** (termasuk teks utama, tabel, dan keterangan gambar). |
| **Struktur Bagian Wajib** | 1. `Introduction` (`RQ1`–`RQ3` & Kontribusi `C-01`–`C-04`)<br>2. `Related Work`<br>3. `Dataset Construction (IndoArg-Analytical-v1)`<br>4. `Methodology (Hybrid Pipeline & Graph-Grounded Scoring)`<br>5. `Experimental Setup` (`E-01`–`E-03b`)<br>6. `Results and Analysis`<br>7. `Conclusion`<br>8. `Limitations` & `Ethical Considerations` (wajib ada; boleh di halaman ke-11 bersama referensi)<br>9. `References` & `Appendix`. | 1. `Title Page` (terpisah untuk review)<br>2. `Highlights` (3–5 bullet, maks `85` karakter termasuk spasi per bullet)<br>3. `Abstract` & `Keywords`<br>4. `1. Introduction`<br>5. `2. Literature Review`<br>6. `3. Methodology & Corpus`<br>7. `4. Experimental Evaluation`<br>8. `5. Discussion & Implications`<br>9. `6. Conclusion`<br>10. `CRediT Statement`, `Declaration of Generative AI`, `Data Availability`, `References`. |
| **Format Abstrak & Kata Kunci** | **Abstrak:** Satu paragraf ringkas (`150–200 kata`), tanpa rumus kompleks dan tanpa sitasi.<br>**Kata Kunci:** Tidak diwajibkan terpisah di template LaTeX TACL (diisi pada metadata portal). | **Abstrak:** Maksimal **`250 kata`** (`150–250 kata`), satu paragraf utuh.<br>**Kata Kunci:** **`4 s.d. 6 kata kunci`** spesifik tepat di bawah abstrak. |
| **Gaya Sitasi & Bibliografi** | **ACL Natbib (`acl_natbib.bst`):** Sistem *Author-Year* dalam teks, mis. `\citet{stab2017parsing}` $\rightarrow$ `Stab and Gurevych (2017)` atau `\citep{koto2020indolem}` $\rightarrow$ `(Koto et al., 2020)`. Wajib mencantumkan URL/DOI ACL Anthology. | **APA Style (7th Edition, `elsarticle-harv.bst`):** Sistem *Author-Date* (`Nama, Tahun`), diurutkan alfabetis berdasarkan nama belakang penulis pertama beserta DOI penuh. |
| **Aturan Gambar dan Tabel** | Gambar wajib berformat vektor (`.pdf` / `.eps`) atau bitmap resolusi $\ge 300\text{ dpi}$; font di dalam grafik minimal setara `9pt`; warna wajib aman bagi buta warna (*colorblind-safe* sesuai `DESIGN_SYSTEM.md`); keterangan tabel di atas tabel, keterangan gambar di bawah gambar. | Gambar resolusi $\ge 300\text{ dpi}$ (kombinasi garis/teks $\ge 500\text{ dpi}$); tabel wajib dalam format teks yang dapat diedit (JANGAN menyisipkan tabel sebagai gambar bitmap); penomoran berurutan (`Table 1`, `Fig. 1`). |
| **Kebijakan *Blind Review*** | **Double-Blind Ketat:** Nama penulis, afiliasi, ucapan terima kasih, dan URL GitHub beridentitas WAJIB dihapus dari PDF naskah. Gunakan repositori anonim (*Anonymous GitHub*) untuk menautkan kode/sampel data saat review. | **Double-Blind:** Naskah utama (*Blinded Manuscript*) tidak boleh memuat nama atau afiliasi penulis; seluruh identitas penulis diunggah pada berkas terpisah `Title Page`. |
| **Data Availability Statement** | Wajib mencantumkan tautan repositori anonim saat review dan repositori permanen (Zenodo DOI + GitHub) saat *camera-ready* (`→ research/REPRODUCIBILITY.md#8-doi-arsip-lisensi-artefak-dan-berkas-citationcff`). | Wajib menyertakan bagian `Data Availability` sebelum daftar pustaka yang menjelaskan cara akses `IndoArg-Analytical-v1` dan lisensi `CC BY-NC-SA 4.0`. |
| **Kebijakan Penggunaan AI Penerbit** | Mengikuti *ACL Policy on Publication Ethics & AI Writing Assistance*: AI tidak boleh menjadi penulis; penggunaan asisten kode/bahasa wajib dideklarasikan secara eksplisit di bagian `Acknowledgments` / `Ethics Statement` (`→ research/AI_USAGE.md`). | Mengikuti *Elsevier Generative AI Policy*: AI dilarang menjadi *co-author*; wajib menyertakan bagian khusus `Declaration of Generative AI and AI-assisted technologies in the writing process` sebelum `References`. |
| **Tenggat Pengiriman (Deadline)** | **Tanggal 1 setiap bulan** (*rolling monthly deadline*, pukul `23:59 UTC-12 / AoE`). | **Sepanjang tahun (*Rolling / Continuous Submission*)** tanpa batas tanggal bulanan. |

---

## 3. Strategi Urutan Pengiriman (*Waterfall Submission Strategy*)

1. **Langkah 1 (Target Utama — `J-01: TACL`):** Kirim pada siklus tanggal 1 bulan terdekat setelah eksperimen `E-01`–`E-03b` selesai (`$0 APC`, *Diamond OA*).
2. **Langkah 2 (Jika `TACL` memberikan keputusan *Reject without Resubmission* atau dianggap terlalu terapan):** Konversi template LaTeX ke format `elsarticle` dan kirim ke **`J-02: Information Processing & Management (IP&M)`** dengan memilih opsi **Subscription (`$0 APC`)**.
3. **Langkah 3 (Jika diarahkan ke domain *AI in Education*):** Kirim ke **`J-03: IJAIED (Springer)`** dengan memilih opsi **Subscription (`$0 APC`)**.

---

## 4. Checklist Kesiapan Sebelum Submit (Pre-Submission Checklist)

Naskah **JANGAN** dikirimkan sebelum seluruh 10 butir di bawah ini berstatus selesai (`[x]`):
- [ ] **1. Judul Terkunci:** Menggunakan judul resmi *"Explainable Argument Mining and Implicit Premise Detection for Evaluating Critical Reasoning in Indonesian Analytical Texts"*.
- [ ] **2. Verifikasi Sitasi & DOI:** Seluruh kunci sitasi di `references.bib` telah memiliki DOI valid dan `0` penanda `[CITATION NEEDED]` tersisa di naskah (`→ research/LITERATURE_REVIEW.md`).
- [ ] **3. Kepatuhan Double-Blind:** Nama penulis, afiliasi, nomor hibah, dan URL GitHub pribadi telah dihapus dari PDF *main manuscript*.
- [ ] **4. Batas Panjang Naskah:** Untuk `TACL`, teks utama berada tepat di rentang `7–10 halaman` (di luar referensi & appendix); untuk `IP&M`, berada di rentang `5.000–10.000 kata` dengan abstrak $\le 250$ kata.
- [ ] **5. Konsistensi Angka Eksperimen:** Seluruh angka pada Tabel 1–4 di naskah cocok 100% dengan `summary_tables.json` dan `→ research/EXPERIMENT_LOG.md`.
- [ ] **6. Pernyataan Etik & UU PDP:** Bagian `Ethical Considerations` mencantumkan status *ethical clearance*, protokol *opt-in*, dan redaksi PII (`→ research/ETHICS.md`).
- [ ] **7. Pernyataan Ketersediaan Data & Kode:** Tautan *Anonymous GitHub* / pratinjau dataset `IndoArg-Analytical-v1` aktif dan dapat dibuka oleh reviewer tanpa login.
- [ ] **8. Deklarasi CRediT & AI Usage:** Teks dari `→ research/AUTHORS_CONTRIBUTIONS.md` dan `→ research/AI_USAGE.md` telah disiapkan sesuai format penerbit.
- [ ] **9. Pilihan Opsi Gratis ($0 APC):** Pada portal pengiriman `IP&M` / `IJAIED`, pastikan memilih **Subscription / Traditional Publishing (`No APC`)**; pada `TACL`, otomatis gratis.
- [ ] **10. Persetujuan Seluruh Penulis:** Semua ko-penulis telah membaca dan menyetujui draf final beserta klaim kontribusi `C-01`–`C-04`.

---

## 5. Pertanyaan Terbuka

1. `TODO(Q-JOUR-01 — Pilihan Pertama TACL vs IP&M)`: Mengingat `TACL` memiliki batas ketat `10 halaman` (format 2 kolom ACL) sedangkan `IP&M` mengizinkan hingga `10.000 kata` (format jurnal panjang Elsevier), apakah peneliti utama ingin menyiapkan draf pertama dalam template LaTeX **`TACL`** atau **`IP&M`**?
