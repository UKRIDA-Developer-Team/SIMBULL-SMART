# Fase 3 — Data Preparation

**Proyek:** SPK Rekomendasi Penanganan Kecemasan Siswa (Random Forest + SMART)
**Metodologi:** CRISP-DM — Fase 3 dari 6

---

## 1. Ringkasan Langkah

| # | Langkah | Data Kaggle | Data kuesioner | Kode |
|---|---|---|---|---|
| 1 | Sampling | 1 juta → 20.000 (2%), lalu 10.000 (50%) untuk RF | seluruh respons | `spk/data.py`, `spk/model.py::split` |
| 2 | Seleksi atribut | 11 fitur + target; buang variabel hasil | petakan ±50 kolom ke *field* | `config.FEATURES`, `gform_mapping.json` |
| 3 | Pembersihan | tidak ada nilai hilang/duplikat | duplikat, rentang, jawaban tak dikenal, data pribadi | `spk/gform.py` |
| 4 | Encoding | `gender` → kode tetap | teks jawaban → angka | `data.encode_gender`, `gform.encode` |
| 5 | Konstruksi fitur | – | 11 fitur skala Kaggle + target | `gform.derive` |
| 6 | Imputasi | – | median data latih | `gform.impute` |
| 7 | Pembagian data | 80% latih / 20% uji | 80% pengembangan / 20% *holdout* + CV 5-fold ×2 | `model.split`, `spk/retrain.py` |

## 2. Data Kaggle

### 2.1 Sampling

Berkas 1 juta baris terlalu besar untuk Google Colab dan deployment, jadi diambil sampel acak **2% (20.000 baris)** dengan `random_state=42`. Sampel ini disimpan sebagai `app/data/dataset.csv`. Untuk melatih RF, diambil lagi **50% (10.000 baris)**.

### 2.2 Seleksi atribut

- **Target:** `anxiety_score`.
- **Fitur (11):** `age`, `gender`, `study_hours_per_day`, `academic_performance`, `exam_pressure`, `stress_level`, `sleep_hours`, `physical_activity`, `financial_stress`, `family_expectation`, `burnout_score`.
- **Dibuang:** `depression_score`, `mental_health_index`, `risk_level`, `dropout_risk` (variabel hasil → *leakage*); `social_support`, `screen_time`, `internet_usage` (korelasi ≈ 0); `academic_year` (tidak berlaku untuk SMA).

### 2.3 Encoding

`gender` dikodekan dengan pemetaan tetap `Female=0, Male=1, Other=2`. Pemetaan ini sama dengan hasil `LabelEncoder` pada notebook (urutan alfabet). Pemetaan ditulis eksplisit di `config.GENDER_MAP` agar aplikasi tidak bergantung pada objek encoder yang tersimpan.

Random Forest tidak memerlukan normalisasi fitur, sehingga fitur numerik dipakai apa adanya.

### 2.4 Pembagian data

Dari 10.000 baris: **8.000 latih** dan **2.000 uji** (`test_size=0.2`, `random_state=42`). Rata-rata target pada data latih 3,00 dan pada data uji 3,07, jadi sebaran keduanya seimbang.

## 3. Data Kuesioner (Google Form)

### 3.1 Pencocokan kolom

Ekspor Google Form memakai judul pertanyaan sebagai nama kolom. Pertanyaan grid tertulis sebagai `Judul grid [teks baris]`. Berkas `spk/gform_mapping.json` mencocokkan setiap *field* dengan potongan teks pertanyaan. Beberapa judul dipakai dua kali di formulir, misalnya "Rata-Rata Jam Belajar Per Hari" dan "Target pengumpulan tugas". Untuk kasus ini, sistem memilih kolom yang jawabannya paling banyak dapat dibaca oleh *parser* field tersebut. Skrip `scripts/inspect_gform.py` menampilkan hasil pencocokan sebelum pelatihan.

### 3.2 Pembersihan

- **Data pribadi dibuang:** *timestamp*, tanggal lahir, nama sekolah, sumber informasi, nama teman, dan email. Pembuangan terjadi segera setelah usia dihitung. Setiap baris diberi ID anonim `R0001…`.
- **Duplikat:** baris dengan jawaban identik dibuang.
- **Rentang:** nilai rapor di luar 0–100 dan jam di luar rentang pertanyaan dikosongkan.
- **Jawaban tak dikenal** dihitung dan dicontohkan di laporan privat agar pemetaan dapat diperbaiki.
- ***Straight-lining***: jumlah baris dengan semua jawaban Likert sama dilaporkan.

### 3.3 Encoding jawaban

| Jenis jawaban | Contoh | Menjadi |
|---|---|---|
| Rentang jam | "Dibawah 30 menit", "1 jam 30 menit", "12 jam" | 0,25 · 1,5 · 12 |
| Likert frekuensi | Tidak pernah … Sangat sering | 1 … 5 |
| Likert persetujuan | Sangat tidak setuju … Sangat setuju | 1 … 5 |
| Ordinal 4 tingkat | Tidak pernah / 1 kali / 2-3 kali / 4-5 kali | 1 … 4 |
| Hari olahraga | 0 / 1-2 / 3-4 / 5-6 / 7 hari | 0 · 1,5 · 3,5 · 5,5 · 7 (titik tengah) |
| Jenis kelamin | Laki-laki / Perempuan | Male / Female |

*Parser* juga menerima variasi penulisan: huruf besar/kecil, tanda pisah "–" atau "-", dan nomor urut di depan opsi.

### 3.4 Konstruksi fitur (pemetaan ke skala Kaggle)

Agar model Kaggle dapat dipakai dan dilatih ulang, jawaban kuesioner diubah ke rentang yang sama dengan fitur Kaggle. `unit(x)` berarti skala ordinal 1…n dipetakan ke 0…1.

| Fitur model | Rumus |
|---|---|
| age | ⌊(timestamp − tanggal lahir) / 365,25⌋ |
| gender | jenis kelamin |
| study_hours_per_day | jam belajar (jam) |
| academic_performance | nilai rata-rata rapor |
| exam_pressure | 1 + (tertekan ujian − 1) × 9/4 → 1–10 |
| stress_level | 10 × rata-rata unit(tugas bersamaan, waktu tidak cukup, tugas terlambat, belajar larut malam) |
| sleep_hours | durasi tidur (jam) |
| physical_activity | hari olahraga per minggu |
| financial_stress | 10 × (5 − uang saku cukup) / 4 (dibalik) |
| family_expectation | 10 × rata-rata unit(takut mengecewakan orang tua, tuntutan nilai keluarga) |
| burnout_score | 10 × rata-rata unit(sulit membagi waktu, kelelahan, kehilangan minat) |
| **anxiety_score** (target) | [Σ(P − 1) untuk P01, P02, P04, P05 + (5 − P03)] / 2 → 0–10 |

Lima butir Psikologis (P01–P05) hanya membentuk target dan **tidak pernah** menjadi fitur, sehingga tidak ada *label leakage*. Rumus diuji otomatis di `tests/test_gform.py`.

### 3.5 Imputasi

Fitur yang kosong diisi median data kuesioner. Untuk gender, dipakai modus. Nilai median disimpan di metadata model (`impute_medians`), sehingga unggahan baru di aplikasi diisi dengan nilai yang sama persis. Baris tanpa target dibuang dari pelatihan.

### 3.6 Pembagian data

- **80% pengembangan dan 20% holdout** (`random_state=42`) bila respons ≥ 30.
- Pada data pengembangan dijalankan ***repeated k-fold cross-validation*** (5 lipatan × 2 ulangan) untuk memilih strategi pelatihan ulang (Fase 4).
- Model akhir dilatih ulang pada seluruh respons dengan strategi terpilih.

⟦ISI dari laporan data riil: jumlah baris mentah → bersih, jumlah pengembangan/holdout, jumlah nilai yang diimputasi.⟧

## 4. Penyiapan Data untuk SMART

Matriks keputusan berisi 8 kriteria untuk setiap siswa: 7 fitur langsung ditambah `rf_anxiety_score` hasil prediksi RF. Normalisasi utilitas membutuhkan min dan maks tiap kriteria. Batas ini dihitung dari populasi referensi saat pelatihan dan disimpan di metadata (`smart_bounds`), agar satu siswa pun dapat dinilai. Batas diambil dari data Kaggle 20.000 baris, atau dari data riil bila respons ≥ 50.

## 5. Keluaran Fase

| Berkas | Isi | Di repositori? |
|---|---|---|
| `app/data/dataset.csv` | 20.000 baris sampel Kaggle | ya |
| `app/data/private/gform_raw.csv` | ekspor kuesioner mentah | **tidak** (gitignore) |
| `app/data/sample_gform.csv` | 250 baris ekspor **sintetis** untuk uji dan demo | ya |
| metadata model | `smart_bounds`, `impute_medians`, `gender_map` | ya |
