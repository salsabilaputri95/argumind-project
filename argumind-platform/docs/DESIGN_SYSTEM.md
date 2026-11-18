Tujuan: Menetapkan token desain eksplisit (warna, tipografi, spasi, radius, bayangan, gerak), variabel CSS tunggal, spesifikasi 10 komponen inti, aturan visualisasi chart/graf, dan standar aksesibilitas WCAG 2.1 AA untuk platform Argumind.
Status dan tanggal: Draft v1.0 | 2026-11-18
Sumber kebenaran untuk: Variabel CSS (`apps/web/src/styles/tokens.css`), palet warna komponen dan graf argumen (`F-02`–`F-05`), serta spesifikasi UI seluruh halaman (`P-01`–`P-07`).

# Sistem Desain (Design System): Argumind Platform

---

## 1. Tabel Design Tokens

### A. Token Warna (Mode Terang & Mode Gelap) + Semantik Graf Argumen
Seluruh pasangan warna latar dan teks di bawah ini WAJIB memenuhi rasio kontras minimum WCAG 2.1 AA ($\ge 4.5:1$ untuk teks normal, $\ge 3.0:1$ untuk teks besar dan batas node graf):

| Nama Token | Nilai Mode Terang (`Light`) | Nilai Mode Gelap (`Dark`) | Penggunaan Eksplisit |
|---|---|---|---|
| `--color-primary` | `#1E40AF` (Blue 800) | `#60A5FA` (Blue 400) | Tombol aksi primer (`Analisis Argumen`), tautan aktif, border node terpilih. |
| `--color-primary-hover` | `#1E3A8A` (Blue 900) | `#93C5FD` (Blue 300) | State `:hover` pada tombol primer dan elemen interaktif utama. |
| `--color-secondary` | `#0F766E` (Teal 700) | `#2DD4BF` (Teal 400) | Aksi sekunder (`Bandingkan Versi`, `Buat Kontraargumen`), aksen filter. |
| `--color-bg-canvas` | `#F8FAFC` (Slate 50) | `#090D16` (Slate 950) | Latar belakang utama halaman dan kanvas graf `@xyflow/react` (`P-03`, `P-05`). |
| `--color-surface` | `#FFFFFF` | `#111827` (Gray 900) | Latar kartu (`Card`), panel teks esai, baris tabel, dan node graf standar. |
| `--color-surface-elevated` | `#F1F5F9` (Slate 100) | `#1F2937` (Gray 800) | Header tabel, *dropdown*, *modal*, *popover* inspektor node. |
| `--color-border` | `#CBD5E1` (Slate 300) | `#374151` (Gray 700) | Garis pemisah *split-pane* `1px solid`, border input normal, dan grid tabel. |
| `--color-text-primary` | `#0F172A` (Slate 900) | `#F8FAFC` (Slate 50) | Teks utama dokumen (`clean_text`), judul halaman, isi node graf (Kontras $> 14:1$). |
| `--color-text-secondary` | `#475569` (Slate 600) | `#94A3B8` (Slate 400) | Label metadata, *breadcrumb*, *timestamp*, dan sub-judul (Kontras $\ge 5.7:1$). |
| `--color-text-muted` | `#64748B` (Slate 500) | `#64748B` (Slate 500) | Teks *disabled* dan *placeholder* input. |
| `--color-success` / `bg` | `#15803D` / `#DCFCE7` | `#4ADE80` / `#052E16` | Status `COMPLETED`, relasi `Support`, skor dimensi tinggi (`4..5`), badge `ACCEPTED`. |
| `--color-warning` / `bg` | `#B45309` / `#FEF3C7` | `#FBBF24` / `#451A03` | Node `ImplicitPremise` (`IP-xx`), `severity = Medium`, konflik adjudikasi (`P-06`). |
| `--color-error` / `bg` | `#B91C1C` / `#FEE2E2` | `#F87171` / `#450A0A` | Relasi `Attack`, `ReasoningGap` (`severity = High`), validasi form gagal (`HTTP 422`). |
| `--color-info` / `bg` | `#0369A1` / `#E0F2FE` | `#38BDF8` / `#082F49` | Node `Claim` utama, banner progres `SSE`, petunjuk kalibrasi anotasi. |
| `--node-claim-border` | `#0284C7` (`2px solid`) | `#38BDF8` (`2px solid`) | Border & sorotan span untuk `node_type = 'Claim'` (Ikon wajib: `[C] Target`). |
| `--node-premise-border` | `#4F46E5` (`2px solid`) | `#818CF8` (`2px solid`) | Border & sorotan span untuk `node_type = 'ExplicitPremise'` (Ikon wajib: `[P]Layers`). |
| `--node-implicit-border` | `#D97706` (`2px dashed`) | `#FBBF24` (`2px dashed`) | Border garis putus-putus untuk `node_type = 'ImplicitPremise'` (Ikon wajib: `[IP] Sparkles`). |
| `--node-evidence-border` | `#059669` (`2px solid`) | `#34D399` (`2px solid`) | Border & sorotan span untuk `node_type = 'Evidence'` (Ikon wajib: `[E] FileCheck`). |
| `--node-counter-border` | `#E11D48` (`2px dotted`) | `#FB7185` (`2px dotted`) | Border titik-titik untuk `node_type = 'Counterargument'` (Ikon wajib: `[CA] ShieldAlert`). |

### B. Token Tipografi
- **Font Family:**
  - `--font-sans`: `'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif` (UI, label, tabel, node graf).
  - `--font-serif-essay`: `'Source Serif 4', Georgia, Cambria, serif` (khusus panel bacaan teks dokumen `clean_text` di `P-03`/`P-05` agar nyaman dibaca hingga 2.500 kata).
  - `--font-mono`: `'JetBrains Mono', 'Fira Code', Consolas, monospace` (ID node `N-01`, `trace_id`, indeks karakter `start_char..end_char`, angka metrik).

| Peran Tipografi (`Token`) | Ukuran (`px` / `rem`) | Bobot (`font-weight`) | `line-height` | `letter-spacing` | Penggunaan |
|---|---|---|---|---|---|
| `--text-display` | `30px` / `1.875rem` | `700` (Bold) | `36px` (`1.20`) | `-0.02em` | Skor utama `overall_score` pada laporan & header halaman publik. |
| `--text-h1` | `24px` / `1.500rem` | `700` (Bold) | `32px` (`1.33`) | `-0.015em` | Judul halaman utama (`/dashboard`, judul dokumen di `P-03`). |
| `--text-h2` | `18px` / `1.125rem` | `600` (SemiBold) | `26px` (`1.44`) | `-0.01em` | Judul panel *split-pane*, judul modal, dan nama dimensi rubrik. |
| `--text-h3` | `15px` / `0.9375rem` | `600` (SemiBold) | `22px` (`1.46`) | `0em` | Header kartu node graf dan sub-bagian inspektor. |
| `--text-body` | `14px` / `0.875rem` | `400` (Regular) | `20px` (`1.43`) | `0em` | Teks standar aplikasi, tabel, form input, dan alasan rubrik (`rationale`). |
| `--text-prose-essay` | `16px` / `1.000rem` | `400` (Regular) | `28px` (`1.75`) | `0.005em` | Teks esai/kebijakan pada `AnnotatedTextPane` (`lebar baris maks 68ch`). |
| `--text-caption` | `12px` / `0.750rem` | `500` (Medium) | `16px` (`1.33`) | `0.01em` | Badge tipe komponen, label sumbu chart, *timestamp*, dan *helper text*. |

### C. Token Spacing, Radius, Shadow, Breakpoint, Z-Index, dan Motion

| Kategori | Nama Token | Nilai Eksplisit | Penggunaan |
|---|---|---|---|
| **Spacing (Grid `4px`)** | `--space-1` s.d. `--space-8` | `4px`, `8px`, `12px`, `16px`, `20px`, `24px`, `32px`, `48px` | Padding dalam badge (`4px 8px`), padding kartu/node (`12px 16px`), jarak antar-panel (`16px`). |
| **Border Radius** | `--radius-sm`, `--radius-md`, `--radius-lg`, `--radius-full` | `4px`, `8px`, `12px`, `9999px` | Sorotan span teks (`4px`), input & tombol (`8px`), kartu node graf & modal (`12px`), badge pil (`9999px`). |
| **Elevation / Shadow** | `--shadow-sm`<br>`--shadow-md`<br>`--shadow-lg` | `0 1px 2px 0 rgba(15,23,42,0.06)`<br>`0 4px 6px -1px rgba(15,23,42,0.10)`<br>`0 10px 15px -3px rgba(15,23,42,0.15)` | Kartu statis & baris tabel (`sm`), node graf aktif/di-hover & dropdown (`md`), modal & drawer (`lg`). |
| **Breakpoints** | `--bp-sm`, `--bp-md`, `--bp-lg`, `--bp-xl` | `640px`, `768px`, `1024px`, `1440px` | Mobile (`<768px`), Tablet (`768px–1023px`), Desktop kanvas graf (`>=1024px`), Layar lebar (`>=1440px`). |
| **Z-Index** | `--z-canvas`, `--z-sticky`, `--z-drawer`, `--z-modal`, `--z-toast` | `1`, `20`, `30`, `40`, `50` | Mencegah tumpang-tindih antara kontrol kanvas React Flow (`1`), navbar (`20`), drawer (`30`), modal (`40`), dan toast (`50`). |
| **Motion** | `--duration-fast`, `--duration-normal`, `--ease-out` | `120ms`, `200ms`, `cubic-bezier(0.16, 1, 0.3, 1)` | Transisi hover/sorotan teks (`120ms`), buka/tutup akordeon & modal (`200ms`). Wajib `0ms` jika `prefers-reduced-motion: reduce`. |

---

## 2. Sumber Tunggal Variabel CSS (`apps/web/src/styles/tokens.css`)

```css
:root {
  --color-primary: #1E40AF;
  --color-primary-hover: #1E3A8A;
  --color-secondary: #0F766E;
  --color-bg-canvas: #F8FAFC;
  --color-surface: #FFFFFF;
  --color-surface-elevated: #F1F5F9;
  --color-border: #CBD5E1;
  --color-text-primary: #0F172A;
  --color-text-secondary: #475569;
  --color-text-muted: #64748B;
  --color-success: #15803D;
  --color-success-bg: #DCFCE7;
  --color-warning: #B45309;
  --color-warning-bg: #FEF3C7;
  --color-error: #B91C1C;
  --color-error-bg: #FEE2E2;
  --color-info: #0369A1;
  --color-info-bg: #E0F2FE;
  --node-claim-border: #0284C7;
  --node-premise-border: #4F46E5;
  --node-implicit-border: #D97706;
  --node-evidence-border: #059669;
  --node-counter-border: #E11D48;
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-serif-essay: 'Source Serif 4', Georgia, Cambria, serif;
  --font-mono: 'JetBrains Mono', Consolas, monospace;
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-full: 9999px;
  --shadow-sm: 0 1px 2px 0 rgba(15, 23, 42, 0.06);
  --shadow-md: 0 4px 6px -1px rgba(15, 23, 42, 0.10);
  --shadow-lg: 0 10px 15px -3px rgba(15, 23, 42, 0.15);
  --focus-ring: 0 0 0 2px #FFFFFF, 0 0 0 4px #1E40AF;
  --duration-fast: 120ms;
  --duration-normal: 200ms;
}

.dark {
  --color-primary: #60A5FA;
  --color-primary-hover: #93C5FD;
  --color-secondary: #2DD4BF;
  --color-bg-canvas: #090D16;
  --color-surface: #111827;
  --color-surface-elevated: #1F2937;
  --color-border: #374151;
  --color-text-primary: #F8FAFC;
  --color-text-secondary: #94A3B8;
  --color-success: #4ADE80;
  --color-success-bg: #052E16;
  --color-warning: #FBBF24;
  --color-warning-bg: #451A03;
  --color-error: #F87171;
  --color-error-bg: #450A0A;
  --color-info: #38BDF8;
  --color-info-bg: #082F49;
  --focus-ring: 0 0 0 2px #090D16, 0 0 0 4px #60A5FA;
}
```

---

## 3. Spesifikasi 10 Komponen Inti

| Komponen | Varian | Ukuran Eksplisit | Spesifikasi State (`default`, `hover`, `focus`, `active`, `disabled`, `error`, `loading`) | Token yang Dipakai |
|---|---|---|---|---|
| **1. Button** | `primary`, `secondary`, `outline`, `ghost`, `danger` | `sm`: tinggi `32px`, pad `0 12px`, font `12px`<br>`md`: tinggi `40px`, pad `0 16px`, font `14px`<br>`lg`: tinggi `44px`, pad `0 20px`, font `15px` | • `default`: bg `--color-primary`, teks `#FFFFFF`<br>• `hover`: bg `--color-primary-hover`<br>• `focus`: `box-shadow: var(--focus-ring)`<br>• `active`: `transform: scale(0.98)`<br>• `disabled`: `opacity: 0.50`, `cursor: not-allowed`<br>• `loading`: ikon spinner `16px` berputar, teks tetap tampil, klik dikunci. | `--color-primary`, `--radius-md`, `--focus-ring`, `--duration-fast` |
| **2. Input (Text / Textarea)** | `default`, `search`, `essay-paste` | Tinggi `40px` (`input`), tinggi min `240px` (`essay-paste`), pad `8px 12px`, border `1px solid` | • `default`: border `--color-border`, bg `--color-surface`<br>• `hover`: border `#94A3B8`<br>• `focus`: border `--color-primary`, `box-shadow: var(--focus-ring)`<br>• `disabled`: bg `--color-surface-elevated`, teks `--color-text-muted`<br>• `error`: border `2px solid var(--color-error)`, bg `--color-error-bg` (`aria-invalid="true"`). | `--color-surface`, `--color-border`, `--color-error`, `--radius-md` |
| **3. Select** | `single`, `version-picker` (`P-03`/`P-04`) | Tinggi `40px`, lebar min `160px`, pad `8px 32px 8px 12px` | • `default`/`hover`/`focus`/`disabled`/`error`: identik dengan `Input`<br>• `active (open)`: menu *dropdown* memiliki `max-height: 280px`, `z-index: var(--z-drawer)`, opsi terpilih memakai bg `--color-info-bg` dan ikon centang `16px`. | `--color-surface-elevated`, `--shadow-md`, `--radius-md` |
| **4. Table** | `document-list` (`P-02`), `rubric-diff` (`P-04`), `member-list` (`P-07`) | Tinggi header `40px`, tinggi baris `48px`, pad sel `12px 16px` | • `default`: border bawah `1px solid var(--color-border)`<br>• `hover`: baris berubah ke `--color-surface-elevated`<br>• `focus`: baris yang dapat diklik menampilkan `--focus-ring`<br>• `loading`: 5 baris *skeleton* tinggi `48px`<br>• `empty`: rentang `colSpan` penuh menampilkan komponen Empty State. | `--color-surface`, `--color-surface-elevated`, `--color-border`, `--text-body` |
| **5. Card & Argument Node** | `surface-card`, `graph-node` (`Claim`, `Premise`, `Implicit`, `Evidence`, `Counter`) | `graph-node`: lebar tetap `260px`, tinggi min `84px`, pad `12px`, radius `12px` | • `default`: bg `--color-surface`, border kiri `4px` + keliling `2px` sesuai `--node-*-border`<br>• `hover`: `--shadow-md`<br>• `active/selected`: ring luar `3px solid var(--color-primary)` dan sorot span teks terkait<br>• `error (has gap)`: badge merah `G-xx` di sudut kanan atas. | `--node-*-border`, `--color-surface`, `--radius-lg`, `--shadow-sm`, `--shadow-md` |
| **6. Modal** | `form-modal` (`Unggah`), `confirm-danger` | `md`: lebar maks `560px`<br>`lg`: lebar maks `760px`<br>Pad `24px`, backdrop `rgba(15,23,42,0.60)` | • `open`: animasi `opacity 0->1` & `scale 0.96->1` dalam `200ms`; fokus dikunci di dalam modal (*focus trap*)<br>• `Escape` menutup modal kecuali saat `loading` pengiriman form aktif. | `--color-surface`, `--radius-lg`, `--shadow-lg`, `--z-modal`, `--duration-normal` |
| **7. Chart & Graph Canvas** | `dag-canvas` (`F-02`), `rubric-radar/bar` (`F-04`), `quota-bar` (`P-07`) | Kanvas: `100%` tinggi viewport dikurangi `56px` navbar; Bar rubrik: tinggi `200px` | • `default`: latar titik-titik (*dot grid* jarak `16px`, warna `--color-border`)<br>• `loading`: *skeleton* pohon 3 node statis<br>• `error`: banner fallback dengan tombol muat ulang. | `--color-bg-canvas`, `--color-border`, `--z-canvas` |
| **8. Badge** | `node-type` (`C`, `P`, `IP`, `E`, `CA`), `severity` (`Low`, `Med`, `High`), `status` | Tinggi `22px`, pad `2px 8px`, font `12px` (`--text-caption`), radius `9999px` | WAJIB menggabungkan **Ikon `12px` + Kode Teks (`N-01` / `G-01`) + Warna Semantik** agar tidak bergantung pada warna saja. | `--radius-full`, `--text-caption`, `--color-success/warning/error/info-bg` |
| **9. Toast** | `info`, `success`, `warning`, `error` | Lebar `360px`, pad `12px 16px`, posisi kanan-bawah (`jarak 24px`) | Tampil otomatis selama `5000ms` untuk `success`/`info`; **WAJIB bertahan (*persistent*) hingga ditutup manual** untuk `error` (`HTTP 4xx/5xx`) agar pengguna sempat menyalin `trace_id`. | `--z-toast`, `--shadow-lg`, `--radius-md` |
| **10. Navigasi** | `top-navbar`, `breadcrumb`, `split-pane-tabs` (Mobile) | Tinggi `top-navbar`: `56px`; Tinggi tab mobile: `44px` | Item rute aktif memiliki indikator garis bawah `2px solid var(--color-primary)` dan atribut `aria-current="page"`. | `--color-surface`, `--color-primary`, `--z-sticky` |

---

## 4. Aturan Visualisasi Chart dan Graf Argumen (`F-02`, `F-04`, `F-07`)

1. **Palet Seri & Ketebalan Garis Relasi (`ArgumentEdge`):**
   - Relasi `Support`: Garis utuh (`stroke-dasharray: none`), warna `#15803D` (`Light`) / `#4ADE80` (`Dark`), panah tertutup di ujung `target_node_id`, label badge tengah `[+ Support | 0.91]`.
   - Relasi `Attack`: Garis putus-putus (`stroke-dasharray: 6 4`), warna `#B91C1C` (`Light`) / `#F87171` (`Dark`), ujung panah berlian/silang, label badge tengah `[x Attack | 0.85]`.
   - Ketebalan garis (`stroke-width`) diskalakan secara linier dari `1.5px` (`confidence = 0.50`) hingga `3.0px` (`confidence = 1.00`).
2. **Palet Seri Grafik Skor Rubrik 4 Dimensi (`P-03`, `P-04`):**
   - Seri 1 (Skor AI / Versi A): `#64748B` (Slate 500, pola arsir diagonal).
   - Seri 2 (Skor Override Pakar / Versi B): `#1E40AF` (Blue 800, isian solid).
3. **Aturan Label & Tooltip:**
   - Sumbu nilai skor rubrik WAJIB menggunakan bilangan bulat `1, 2, 3, 4, 5` (JANGAN menampilkan sumbu desimal seperti `2.5` pada label grid).
   - *Tooltip* saat kursor berada di atas bar dimensi atau edge graf WAJIB muncul dalam `100ms`, berlatar `--color-surface-elevated`, menampilkan nilai eksak (mis. `Skor: 3/5 | Bukti: N-01, G-01`), dan tidak menutupi node yang sedang ditunjuk.
4. **Empty State Chart/Graf:** Jika belum ada komponen yang diekstrak, kanvas menampilkan kotak tengah berukuran `320x160px` dengan border `--color-border` bertuliskan `"Belum ada struktur argumen. Jalankan analisis untuk merender peta klaim-premis."`

---

## 5. Standar Aksesibilitas (WCAG 2.1 Level AA)

1. **Rasio Kontras Terukur:**
   - Teks utama (`--color-text-primary` di atas `--color-surface`): `15.8:1` (`Light`) dan `16.1:1` (`Dark`) — melampaui syarat minimum `4.5:1`.
   - Teks sekunder (`--color-text-secondary` di atas `--color-surface`): `7.2:1` (`Light`) dan `6.4:1` (`Dark`) — melampaui syarat minimum `4.5:1`.
   - Border node graf dan garis relasi terhadap `--color-bg-canvas`: seluruhnya $\ge 3.2:1$ — melampaui syarat minimum `3.0:1` untuk komponen non-teks.
2. **Indikator Fokus Keyboard (`Focus Ring`):**
   - Setiap elemen interaktif (termasuk setiap node dan edge di kanvas `@xyflow/react`) WAJIB menampilkan `box-shadow: var(--focus-ring)` (`2px` offset putih/gelap + `2px` cincin `#1E40AF`/`#60A5FA`) saat menerima `:focus-visible`. JANGAN menulis `outline: none` tanpa pengganti `--focus-ring`.
   - Navigasi antar-node di kanvas graf WAJIB dapat dilakukan dengan tombol `Tab` dan tombol panah (`ArrowUp/Down/Left/Right`).
3. **Ukuran Target Sentuh & Klik Minimal:**
   - Pada viewport Mobile/Tablet (`< 1024px`), seluruh tombol, tab, dan kontrol pilihan WAJIB memiliki area target sentuh minimal **`44x44px`**.
   - Pada viewport Desktop (`>= 1024px`), kontrol ikon rapat pada toolbar kanvas dan anotasi WAJIB memiliki area klik minimal **`32x32px`** dengan jarak antar-target minimal `4px`.

---

## 6. Pertanyaan Terbuka

1. `TODO(Q-DS-01 — Tema Default Aplikasi)`: Apakah aplikasi web Argumind saat pertama kali dibuka akan menggunakan **Mode Terang (`Light`)** sebagai *default* (karena menyerupai kertas dokumen akademik) atau mengikuti preferensi sistem operasi (`prefers-color-scheme`)?
