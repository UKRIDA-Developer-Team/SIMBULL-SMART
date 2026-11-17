# Fase 3 — Data Preparation

**Proyek:** SPK Rekomendasi Penanganan Kecemasan Siswa (Random Forest + SMART)
**Metodologi:** CRISP-DM — Fase 3 dari 6

---

## 1. Ringkasan Langkah

| # | Langkah | Data Kaggle | Data kuesioner | Kode |
|---|---|---|---|---|
| 1 | Pembersihan usia | 1 juta → usia 14–25 (692.545) | usia 14–25 | `data.clean`, `config.AGE_RANGE` |
| 2 | Seleksi atribut | 11 fitur + target; buang variabel hasil | petakan ±50 kolom ke *field* | `config.FEATURES`, `gform_mapping.json` |
| 3 | Pembersihan | tidak ada nilai hilang/duplikat | duplikat, rentang, jawaban tak dikenal, data pribadi | `spk/gform.py` |
| 4 | Encoding | `gender` → kode tetap | teks jawaban → angka | `data.encode_gender`, `gform.encode` |
| 5 | Konstruksi fitur | – | 11 fitur skala Kaggle + target | `gform.derive` |
| 6 | Imputasi | – | median data latih | `gform.impute` |
| 7 | Pembagian data | 80% latih (554.036) / 20% uji (138.509), stratifikasi usia | 80% pengembangan / 20% *holdout* + CV 5-fold ×2 | `data.split_full`, `spk/retrain.py` |

## 2. Data Kaggle

### 2.1 Pembersihan usia

Data Kaggle berasal dari mahasiswa usia 17–29, sedangkan pengguna sasaran adalah pelajar. Agar data yang ditambang mewakili usia pelajar, hanya baris dalam rentang **14–25 tahun** yang dipakai (`config.AGE_RANGE`). Batas 14 mencakup siswa SMA pengisi kuesioner, dan 25 adalah akhir masa kuliah umum. Karena berkas Kaggle mulai dari usia 17, yang tersisa adalah usia 17–25: **692.545 dari 1.000.000 baris** (307.455 baris dibuang). Model dasar karena itu tidak pernah melihat pelajar berusia 14–16; penyesuaian ke siswa SMA dilakukan dengan pelatihan ulang (§4.3).

Seluruh berkas dipakai, bukan sampel. Notebook awal mengambil sampel 2% (20.000 baris) lalu 50% lagi untuk RF, sehingga hanya 8.000 baris yang melatih model dan 2.000 baris yang mengujinya.

### 2.2 Seleksi atribut

- **Target:** `anxiety_score`.
- **Fitur (11):** `age`, `gender`, `study_hours_per_day`, `academic_performance`, `exam_pressure`, `stress_level`, `sleep_hours`, `physical_activity`, `financial_stress`, `family_expectation`, `burnout_score`.
- **Dibuang:** `depression_score`, `mental_health_index`, `risk_level`, `dropout_risk` (variabel hasil → *leakage*); `social_support`, `screen_time`, `internet_usage` (korelasi ≈ 0); `academic_year` (tidak berlaku untuk SMA).

### 2.3 Encoding

`gender` dikodekan dengan pemetaan tetap `Female=0, Male=1, Other=2`. Pemetaan ini sama dengan hasil `LabelEncoder` pada notebook (urutan alfabet). Pemetaan ditulis eksplisit di `config.GENDER_MAP` agar aplikasi tidak bergantung pada objek encoder yang tersimpan.

Random Forest tidak memerlukan normalisasi fitur, sehingga fitur numerik dipakai apa adanya.

### 2.4 Pembagian data

692.545 baris dibagi **80% latih (554.036 baris)** dan **20% uji (138.509 baris)** dengan `test_size=0.2`, `random_state=42`, dan stratifikasi per usia, sehingga setiap usia 17–25 mendapat porsi yang sama (±11,1%) di kedua bagian (`data.split_full`). Rata-rata target pada data latih 2,99 dan pada data uji 2,98.

Dari data uji diambil **20.000 baris** (juga distratifikasi per usia) sebagai **populasi referensi** aplikasi (`app/data/dataset.csv`): batas SMART, persentil, grafik Analisis, dan penjelasan Shapley memakai baris ini. Karena berasal dari data uji, aplikasi tidak pernah menampilkan baris yang dipakai melatih model. Dari data latih disimpan 8.000 baris untuk strategi pelatihan ulang S2 (`kaggle_retrain.csv.gz`).

### 2.5 Pemeriksaan outlier

Selain nilai hilang dan duplikat (tidak ada), diperiksa nilai ekstrem. Tiap kolom memiliki paling banyak 0,6% baris di luar 3 simpangan baku; semuanya nilai yang masih masuk akal (misalnya 14 jam belajar atau nilai rapor 45), bukan kesalahan data. Skor *burnout* bernilai 0 pada 23% baris dan kecemasan 0 pada 2,7% baris; ini batas bawah skala, bukan galat.

Untuk memastikan, baris ekstrem dibuang dari **data latih saja**, lalu model diuji pada 138.509 baris uji yang sama:

| Pembersihan data latih | Baris latih | R² uji (Gradient Boosting) |
|---|---|---|
| Tanpa pembersihan tambahan | 554.036 | **0,6083** |
| Buang baris dengan nilai di luar 3 simpangan baku | 547.004 | 0,6079 |
| Buang baris di luar persentil 1–99 | 483.776 | 0,6058 |
| Buang baris dengan kecemasan 0 atau 10 | 539.326 | 0,6049 |
| Buang 2% outlier (*Isolation Forest*) | 542.955 | 0,6080 |

Tidak ada pembersihan yang menaikkan R², jadi tidak ada baris lain yang dibuang. Data uji tidak boleh ikut dibersihkan: membuang baris uji yang sulit diprediksi menaikkan R² secara semu (0,67 bila galat > 2 simpangan baku dibuang), padahal modelnya sama.

## 3. Data Kuesioner (Google Form)

### 3.1 Pencocokan kolom

Ekspor Google Form memakai judul pertanyaan sebagai nama kolom. Pertanyaan grid tertulis sebagai `Judul grid [teks baris]`. Berkas `spk/gform_mapping.json` mencocokkan setiap *field* dengan potongan teks pertanyaan. Beberapa judul dipakai dua kali di formulir, misalnya "Rata-Rata Jam Belajar Per Hari" dan "Target pengumpulan tugas". Untuk kasus ini, sistem memilih kolom yang jawabannya paling banyak dapat dibaca oleh *parser* field tersebut. Skrip `scripts/inspect_gform.py` menampilkan hasil pencocokan sebelum pelatihan.

**Dua versi formulir.** Formulir direvisi (`context_ori.pdf` → `context_new.pdf`, dikurangi butir yang dihapus). Keduanya adalah Google Form yang sama, jadi satu ekspor berisi baris dari kedua versi. Google mempertahankan kolom saat judul diubah, sehingga header memakai judul terbaru. Pertanyaan tambahan (ditandai `new_form` di `gform_mapping.json`) bersifat opsional: kosong pada baris versi lama dan tidak menggagalkan ekspor lama. Setiap baris diberi label `original` atau `revised`: revisi bila menjawab salah satu pertanyaan tambahan atau memilih opsi "> 5" yang baru ada setelah revisi. Kolom pertanyaan yang sudah dihapus dari formulir diabaikan (masuk daftar kolom tak terpakai). Bila sebuah butir opsional cocok dengan dua kolom setara, butir itu dilewati dan dilaporkan, bukan menghentikan proses.

### 3.2 Pembersihan

- **Data pribadi dibuang:** *timestamp*, tanggal lahir, nama sekolah, sumber informasi, nama teman, email, dan jawaban esai kondisi saat bangun tidur (teks bebas dapat memuat nama). Pembuangan terjadi segera setelah usia dihitung. Setiap baris diberi ID anonim `R0001…`.
- **Duplikat:** baris dengan jawaban identik dibuang.
- **Rentang:** nilai rapor di luar 0–100 dan jam di luar rentang pertanyaan dikosongkan.
- **Jawaban tak dikenal** dihitung dan dicontohkan di laporan privat agar pemetaan dapat diperbaiki.
- ***Straight-lining***: jumlah baris dengan semua jawaban Likert sama dilaporkan.

### 3.3 Encoding jawaban

| Jenis jawaban | Contoh | Menjadi |
|---|---|---|
| Rentang jam | "Dibawah 30 menit", "1 jam 30 menit", "12 jam" | 0,25 · 1,5 · 12 |
| Likert frekuensi | Tidak pernah … Sangat sering (atau … Selalu) | 1 … 5 |
| Likert persetujuan | Sangat tidak setuju … Sangat setuju | 1 … 5 |
| Ordinal 5 tingkat | Tidak pernah / 1 kali / 2-3 kali / 4-5 kali / > 5 kali | 1 … 5 (versi lama tidak punya tingkat 5) |
| Hari olahraga | 0 / 1-2 / 3-4 / 5-6 / 7 hari | 0 · 1,5 · 3,5 · 5,5 · 7 (titik tengah) |
| Jenis kelamin | Laki-laki / Perempuan | Male / Female |

*Parser* juga menerima variasi penulisan: huruf besar/kecil, tanda pisah "–" atau "-", dan nomor urut di depan opsi.

### 3.4 Konstruksi fitur (pemetaan ke skala Kaggle)

Agar model Kaggle dapat dipakai dan dilatih ulang, jawaban kuesioner diubah ke rentang yang sama dengan fitur Kaggle. `unit(x)` berarti skala ordinal 1…n dipetakan ke 0…1.

| Fitur model | Rumus |
|---|---|
| age | ⌊(tanggal acuan − tanggal lahir) / 365,25⌋; tanggal acuan = *timestamp*, atau tanggal pemrosesan bila ekspor tidak memuat *timestamp* (seperti ekspor riil) |
| gender | jenis kelamin |
| study_hours_per_day | jam belajar (jam) |
| academic_performance | nilai rata-rata rapor |
| exam_pressure | 1 + 9 × rata-rata unit(tertekan ujian, nilai di bawah target ᴿ) → 1–10 |
| stress_level | 10 × rata-rata unit(tugas bersamaan, waktu tidak cukup, tugas terlambat, belajar larut malam) |
| sleep_hours | durasi tidur (jam) |
| physical_activity | hari olahraga per minggu |
| financial_stress | 10 × (5 − uang saku cukup) / 4 (dibalik) |
| family_expectation | 10 × rata-rata unit(takut mengecewakan orang tua, tuntutan nilai keluarga) |
| burnout_score | 10 × rata-rata unit(sulit membagi waktu, kelelahan, kehilangan minat) |
| **anxiety_score** (target) | 10 × rata-rata unit(P01, P02, 1 − unit(P03), P04, P05, P06 ᴿ, P07 ᴿ) → 0–10 |
| x_sleep_quality (tambahan) | 10 × rata-rata unit(sulit tertidur, terbangun lalu sulit tidur lagi, mimpi buruk/gelisah) ᴿ |

ᴿ = butir yang hanya ada di formulir revisi. Rata-rata diambil dari butir yang dijawab baris tersebut, sehingga pada baris versi lama rumus kembali ke rumus awal, misalnya anxiety_score = [Σ(P − 1) untuk P01, P02, P04, P05 + (5 − P03)] / 2. Target membutuhkan kelima butir P01–P05; P06–P07 ikut bila dijawab. Opsi "4-5 kali" bernilai tingkat 4 dari 5 (0,75) pada kedua versi, jadi label yang sama selalu bernilai sama.

Butir Psikologis (P01–P07) hanya membentuk target dan **tidak pernah** menjadi fitur, sehingga tidak ada *label leakage*. Rumus diuji otomatis di `tests/test_gform.py`.

### 3.4.1 Pemeriksaan penggabungan dua versi

Laporan kualitas (`inspect_gform.py`, laporan privat pelatihan) memuat:

- **Jumlah baris per versi** (`rows_by_form_version`) dan jumlah jawaban "> 5" (`answers_above_original_max`).
- **Reliabilitas** (*Cronbach's alpha*) setiap skor gabungan, untuk semua butir dan untuk butir versi lama saja. Alpha ≥ 0,6 dianggap cukup. Bila butir tambahan menurunkan alpha suatu skor, keluarkan butir itu dari `COMPOSITES` di `spk/gform.py`.
- **Kesetaraan versi** (`item_set_check`): pada baris revisi, korelasi *r* dan selisih rata-rata (*shift*) antara skor dari butir lama dan skor dari semua butir. *r* tinggi (≥ 0,8) dan *shift* kecil (< 0,5 poin) berarti baris lama dan baru aman digabung.

**Hasil pada data riil** (195 baris formulir awal, 109 baris formulir revisi):

| Skor gabungan | α semua butir | α butir lama | *r* (lama vs semua) | *shift* |
|---|---|---|---|---|
| anxiety_score (target) | 0,78 (7 butir) | 0,69 (5 butir) | 0,958 | −0,05 |
| exam_pressure | 0,38 (2 butir) | – (1 butir) | 0,823 | −0,34 |
| family_expectation (dengan "bisa bercerita") | 0,37 (3 butir) | 0,53 (2 butir, baris yang sama) | 0,898 | −0,16 |
| burnout_score | 0,67 | 0,67 | – | – |
| stress_level | 0,32 | 0,32 | – | – |

- Ketiga skor yang mendapat butir baru lolos uji kesetaraan (*r* ≥ 0,82, |*shift*| ≤ 0,34), jadi kedua versi formulir **digabung**.
- Butir revisi "saya mampu membicarakan kesulitan dengan keluarga" **menurunkan** α ekspektasi keluarga dari 0,53 menjadi 0,37 pada 109 baris yang sama. Sesuai aturan di atas, butir ini **dikeluarkan** dari `family_expectation` dan disimpan sebagai butir ekstra (r = −0,26 dengan kecemasan).
- Tingkat stres (α 0,32) dan tekanan ujian (α 0,38) tetap di bawah 0,6. Butir-butirnya bukan butir revisi, jadi tetap dipakai, tetapi keterbatasan ini dicatat di Fase 2 dan Fase 5.

### 3.5 Imputasi

Fitur yang kosong diisi median data kuesioner. Untuk gender, dipakai modus. Nilai median disimpan di metadata model (`impute_medians`), sehingga unggahan baru di aplikasi diisi dengan nilai yang sama persis. Baris tanpa target dibuang dari pelatihan.

### 3.6 Pembagian data

- **80% pengembangan dan 20% holdout** (`random_state=42`) bila respons ≥ 30, distratifikasi menurut versi formulir agar proporsi baris lama dan baru sama di kedua bagian. Laporan menampilkan galat holdout per versi.
- Butir tambahan (`x_…`) yang kosong pada baris versi lama tidak diimputasi untuk model laporan S4; Random Forest menangani nilai kosong secara langsung, sehingga baris lama tidak tampak "rata-rata".
- Pada data pengembangan dijalankan ***repeated k-fold cross-validation*** (5 lipatan × 2 ulangan) untuk memilih strategi pelatihan ulang (Fase 4).
- Model akhir dilatih ulang pada seluruh respons dengan strategi terpilih.

**Hasil pada data riil:**

| Langkah | Baris |
|---|---|
| Ekspor mentah | 304 |
| Setelah buang duplikat | 304 (0 duplikat) |
| Usia 14–25 (atau usia kosong) | 293 (11 dibuang: 10 berusia 13, 1 berusia 30) |
| Dengan target lengkap | **292** |
| Pengembangan / *holdout* | **233 / 59** (*holdout*: 39 formulir awal, 20 formulir revisi) |

Nilai yang diimputasi: 8 usia (tanggal lahir tidak masuk akal) dan 1 nilai pada tekanan ujian, tingkat stres, aktivitas fisik, tekanan finansial, ekspektasi keluarga, dan *burnout*. Median yang disimpan antara lain usia 15, jam belajar 1,5, nilai rapor 84, jam tidur 6,5, dan *burnout* 5,0.

## 4. Penyiapan Data untuk SMART

Matriks keputusan berisi 8 kriteria untuk setiap siswa: 7 fitur langsung ditambah `rf_anxiety_score` hasil prediksi RF. Normalisasi utilitas membutuhkan min dan maks tiap kriteria. Batas ini dihitung dari populasi referensi saat pelatihan dan disimpan di metadata (`smart_bounds`), agar satu siswa pun dapat dinilai. Batas diambil dari 20.000 baris referensi (bagian data uji Kaggle), atau dari data riil bila respons ≥ 50. Model aktif memakai batas dari 292 respons riil, misalnya prediksi kecemasan 1,95–7,64, jam belajar 0,25–10, dan jam tidur 4–12.

## 5. Keluaran Fase

| Berkas | Isi | Di repositori? |
|---|---|---|
| `app/data/dataset.csv` | 20.000 baris uji Kaggle (populasi referensi) | ya |
| `app/data/kaggle_retrain.csv.gz` | 8.000 baris latih Kaggle untuk strategi S2 | ya |
| `app/data/private/gform_data.csv` | ekspor kuesioner riil (304 respons) | **tidak** (gitignore) |
| `app/reports/question_merge_report.md` | pertanyaan mana digabung menjadi fitur/kriteria (agregat) | ya |
| metadata model | `smart_bounds`, `impute_medians`, `gender_map` | ya |
