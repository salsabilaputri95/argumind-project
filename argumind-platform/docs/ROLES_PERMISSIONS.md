Tujuan: Menetapkan definisi peran, matriks izin CRUD, batasan scope data, mekanisme autentikasi, lokasi penegakan otorisasi server, perilaku UI, log audit, dan akses data penelitian pada platform Argumind.
Status dan tanggal: Draft v1.0 | 2026-11-18
Sumber kebenaran untuk: Kebijakan RBAC (`author`, `reviewer`, `annotator`, `org_admin`), aturan isolasi *blind annotation* (`F-06`), dan audit keamanan akses.

# Peran & Hak Akses (Roles & Permissions): Argumind Platform

## 1. Definisi Peran Pengguna

Persona pengguna mengacu pada `→ docs/PRD.md#3-persona-pengguna` dan enum `user_role_enum` pada `→ docs/DATA_MODEL.md#12-users-akun-pengguna`.

| Nama Peran (`role`) | Deskripsi Singkat | Cara Diberikan (Provisioning) |
|---|---|---|
| **`author`** | Penulis draf (mahasiswa, peneliti muda, staf analis) yang menganalisis tulisannya sendiri (`F-01`–`F-05`, `F-07`). | Otomatis sebagai *default role* saat registrasi mandiri atau SSO domain mahasiswa. |
| **`reviewer`** | Dosen, editor, atau analis senior yang meninjau draf di organisasinya, memberi `human_override_score` (`F-04`), dan melakukan adjudikasi korpus (`F-06`). | Ditetapkan secara eksplisit oleh `org_admin` melalui panel manajemen anggota atau klaim grup OIDC dosen. |
| **`annotator`** | Anotator terlatih yang menandai komponen, relasi, dan `ImplicitPremise` secara *double-blind* (`F-06`). | Ditetapkan oleh `org_admin` setelah lulus kalibrasi anotasi ($\alpha_{\text{Krip}} \ge 0.75$). |
| **`org_admin`** | Pengelola institusi/laboratorium yang mengatur kuota (`monthly_doc_quota`), peran anggota, dan ekspor korpus riset. | Diberikan saat pembuatan entitas `organizations` awal atau didelegasikan oleh `org_admin` aktif. |

---

## 2. Matriks Izin Resource × Peran (CRUD)

Kode izin: `C` = Create, `R` = Read, `U` = Update, `D` = Delete, `-` = Dilarang (`HTTP 403`). Kode syarat: `[OWN]` = milik sendiri, `[ORG]` = dalam `org_id` yang sama, `[BLIND]` = hanya dokumen yang ditugaskan tanpa melihat anotasi/skor pihak lain.

| Resource (`→ docs/DATA_MODEL.md`) | `author` | `reviewer` | `annotator` | `org_admin` | Syarat Khusus & Kendala Bisnis |
|---|---|---|---|---|---|
| `organizations` | `R [ORG]` | `R [ORG]` | `R [ORG]` | `R, U [ORG]` | Hanya `org_admin` yang boleh mengubah konfigurasi organisasi; kuota tidak bisa diubah oleh `author`. |
| `users` | `R, U [OWN]` | `R [ORG], U [OWN]` | `R, U [OWN]` | `C, R, U, D [ORG]` | Pengguna JANGAN mengubah kolom `role` miliknya sendiri (`privilege escalation` ditolak). |
| `documents` & `document_versions` | `C, R, U, D [OWN]` | `C, R [ORG], U/D [OWN]` | `R [BLIND]` | `R, D [ORG]` | `annotator` hanya boleh membaca `clean_text` yang sudah bebas PII (`raw_s3_key` disembunyikan). |
| `analysis_runs` (`ai_hybrid`) | `C, R [OWN]` | `C, R [ORG]` | `-` | `R [ORG]` | Saat mode anotasi aktif, `annotator` JANGAN melihat output `ai_hybrid` agar tidak bias. |
| `argument_nodes`, `edges`, `gaps` (`ai_hybrid`) | `R, U [OWN]` (`user_feedback`) | `R, U [ORG]` (`user_feedback`) | `-` | `R [ORG]` | `U` terbatas pada kolom `user_feedback` (`ACCEPTED` / `REJECTED`) pada `F-03` dan `F-05`. |
| `rubric_scores` (`F-04`) | `R [OWN]` | `R, U [ORG]` (`override`) | `R, U [BLIND]` (khusus *blind rating*) | `R [ORG]` | Hanya `reviewer` yang boleh mengisi `human_override_score` dan `override_note` pada sesi `ai_hybrid`. |
| `analysis_runs` (`human_annotator` — `F-06`) | `-` | `R [ORG]` (pasca-submit) | `C, R, U [OWN + BLIND]` | `R [ORG]` | `annotator` JANGAN membaca baris `human_annotator` milik `actor_user_id` lain pada dokumen yang sama. |
| `analysis_runs` (`gold_adjudicated` — `F-06`) | `-` | `C, R, U [ORG]` | `R [ORG]` (hanya pasca-adjudikasi) | `R [ORG]` | Hanya `reviewer` atau peneliti senior yang berhak mengunci konsensus *gold standard*. |
| Ekspor Korpus Riset (`/export?corpus=true`) | `-` | `R [ORG]` (`research_opt_in`) | `-` | `R [ORG]` (`research_opt_in`) | WAJIB memfilter `documents.research_opt_in = true` dan menghapus seluruh kolom PII. |

---

## 3. Aturan Scope Data (Data Isolation Rules)

1. **Scope `OWN` (`author`):** Query database WAJIB menyertakan filter `WHERE documents.author_id = :current_user_id`.
2. **Scope `ORG` (`reviewer`, `org_admin`):** Query WAJIB menyertakan filter `WHERE documents.org_id = :current_user_org_id`. Pengguna dari organisasi A JANGAN pernah dapat mengakses UUID milik organisasi B (`IDOR protection`).
3. **Scope `BLIND` (`annotator` pada `F-06`):** Query WAJIB menyertakan filter `WHERE analysis_runs.actor_user_id = :current_user_id AND analysis_runs.run_source = 'human_annotator'`, serta memblokir akses ke `users.full_name` penulis asli dokumen.

---

## 4. Spesifikasi Autentikasi & Manajemen Sesi

| Aspek | Aturan Konkret & Nilai Eksplisit |
|---|---|
| **Metode Autentikasi** | 1. Email + Password (di-hash dengan `Argon2id`: `memory = 64 MB`, `iterations = 3`, `parallelism = 4`).<br>2. SSO Institusi via `OIDC` (`Authorization Code Flow with PKCE`). |
| **Sesi &Kedaluwarsa** | `access_token` JWT (`RS256`) disimpan di cookie `HttpOnly; Secure; SameSite=Lax` dengan `TTL = 15 menit` (`900 detik`). |
| **Refresh & Rotasi** | `refresh_token` disimpan di cookie `HttpOnly` (`Path=/api/v1/auth/refresh`, `TTL = 7 hari`). Setiap pemakaian melakukan *token rotation* di Redis; penggunaan ulang token lama langsung mencabut seluruh sesi pengguna (*reuse detection*). |
| **Logout** | Menghapus cookie sesi dan memasukkan `jti` token ke daftar cabut (*revocation list*) Redis hingga waktu kedaluwarsa aslinya. |
| **Reset Kredensial** | Token reset satu kali pakai (`CSPRNG 32-byte`, di-hash `SHA-256` di DB) dikirim via email dengan `TTL = 15 menit` dan batas *rate limit* `3 permintaan / jam / email`. |
| **MFA (TOTP)** | **WAJIB** aktif (`TOTP RFC 6238`) untuk seluruh akun dengan peran `org_admin` dan peneliti yang mengekspor korpus riset; opsional untuk `author`, `reviewer`, dan `annotator`. |

---

## 5. Lokasi Penegakan Otorisasi & Perilaku UI

1. **Penegakan Wajib di Server (`C-API`):**
   - Seluruh aturan matriks Bagian 2 dan scope Bagian 3 WAJIB ditegakkan di backend melalui dependency FastAPI `apps/api/src/auth/dependencies.py` (`require_role(...)`) dan policy tingkat baris `apps/api/src/auth/policies.py` (`assert_resource_scope(...)`).
   - JANGAN mengandalkan penyembunyian tombol di `C-WEB` sebagai kontrol keamanan.
2. **Perilaku UI Tanpa Izin (`C-WEB`):**
   - **Elemen & Menu Dalam Halaman:** Tombol aksi yang tidak diizinkan (mis. form `human_override_score` bagi `author` atau tombol `"Adjudikasi"` bagi `annotator`) WAJIB disembunyikan (`not rendered`) dari DOM.
   - **Navigasi URL Langsung:** Jika pengguna mengetik URL rute terlarang (mis. `author` membuka `/workspace/annotations/adjudicate`), middleware Next.js (`apps/web/src/middleware.ts`) dan respons `403` dari `C-API` WAJIB menampilkan halaman khusus **`403 Akses Ditolak`** beserta tautan kembali ke dashboard.

---

## 6. Log Audit Keamanan (Audit Log)

Setiap aksi sensitif WAJIB dicatat secara *append-only* (JANGAN menyediakan endpoint `UPDATE`/`DELETE` untuk log audit):
- **Aksi yang Wajib Dicatat:** (1) Login gagal/sukses & pencabutan sesi, (2) Perubahan `users.role` oleh `org_admin`, (3) Pengisian/perubahan `human_override_score` (`F-04`), (4) Penguncian konsensus `gold_adjudicated` (`F-06`), (5) Ekspor korpus riset, dan (6) Seluruh penolakan akses `HTTP 403`.
- **Field Wajib Log Audit:** `event_id (UUID)`, `timestamp (TIMESTAMPTZ)`, `actor_user_id (UUID)`, `actor_role (string)`, `org_id (UUID)`, `action_code (string)`, `target_resource_type (string)`, `target_resource_id (UUID)`, `ip_address (INET)`, `trace_id (string)`, dan `metadata_diff (JSONB)`.
- *Contoh minimal rekaman log:*
  `{"event_id": "01933f10-...", "timestamp": "2026-11-18T02:30:00Z", "actor_user_id": "01933e00-...", "actor_role": "reviewer", "action_code": "SCORE_OVERRIDE_UPDATED", "target_resource_type": "rubric_scores", "target_resource_id": "01933e99-...", "metadata_diff": {"ai_score": 2, "human_override_score": 3}}`

---

## 7. Peran Peneliti dan Akses Data Mentah Penelitian

1. **Akses Korpus Teranonimisasi:** Hanya `reviewer` yang ditunjuk sebagai Peneliti Utama atau `org_admin` dengan MFA aktif yang dapat mengunduh paket korpus (`research_opt_in = true`) yang telah dianonimisasi (`clean_text` + `anon_author_id`).
2. **Larangan Akses Berkas Mentah (`raw_s3_key`):** Tidak ada peran di antarmuka web (`C-WEB`) yang diizinkan mengunduh massal berkas asli pra-redaksi PII (`raw_s3_key`) untuk keperluan eksperimen; seluruh eksperimen `E-01`–`E-03` WAJIB hanya membaca `clean_text` yang telah melewati `pii_redaction`.

---

## 8. Pertanyaan Terbuka

1. `TODO(Q-ROLE-01 — Delegasi Adjudikator)`: Apakah peran adjudikator konsensus *gold standard* pada `F-06` cukup menggunakan peran `reviewer` yang sudah ada, atau memerlukan flag atribut tambahan `is_lead_researcher: boolean` pada tabel `users`?
