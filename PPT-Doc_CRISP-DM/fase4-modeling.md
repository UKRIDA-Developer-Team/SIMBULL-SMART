# Fase 4 — Modeling

**Proyek:** SPK Rekomendasi Penanganan Kecemasan Siswa (Random Forest + SMART)
**Metodologi:** CRISP-DM — Fase 4 dari 6

---

## 1. Gambaran Umum

| Modul | Teknik | Masukan | Keluaran |
|---|---|---|---|
| M1 — Prediksi (Data Mining) | Random Forest Regressor | 11 fitur siswa | `rf_anxiety_score` (0–10) |
| M2 — Faktor dominan | *Gini feature importance* | model M1 | peringkat faktor |
| M3 — Pelatihan ulang | 7 strategi transfer Kaggle → data riil | model M1 + data kuesioner | model aktif |
| M4 — Keputusan (SPK) | SMART | 7 fitur + `rf_anxiety_score` | skor prioritas, peringkat 5 alternatif |

Alur: **fitur siswa → RF → prediksi kecemasan → SMART → prioritas + rekomendasi**. Prediksi RF menjadi salah satu kriteria SMART. Di titik inilah Data Mining dan SPK terintegrasi.

## 2. M1 — Random Forest Regressor

### 2.1 Alasan pemilihan

Target (`anxiety_score`) kontinu, jadi masalahnya adalah **regresi**. Random Forest dipilih karena:

- Menangkap hubungan non-linear dan interaksi antarfaktor tanpa asumsi bentuk hubungan.
- Tahan terhadap *outlier* dan skala fitur yang berbeda, tanpa normalisasi.
- Menyediakan *feature importance* untuk penjelasan.
- Cocok untuk jawaban kuesioner ordinal dan data berukuran kecil, dengan *bagging* yang mengurangi *overfitting*.

### 2.2 Konfigurasi parameter

| Parameter | Nilai | Alasan |
|---|---|---|
| `n_estimators` | 200 | cukup banyak pohon agar prediksi stabil; waktu latih ±0,3 detik |
| `max_depth` | 10 | membatasi kedalaman agar tidak menghafal data latih |
| `min_samples_split` | 2 | bawaan scikit-learn |
| `min_samples_leaf` | 2 (3 untuk data riil) | daun minimal 2–3 sampel: mengurangi *overfitting* dan hafalan data pribadi |
| `max_features` | `"sqrt"` | tiap pemisahan hanya melihat √11 ≈ 3 fitur, sehingga pohon lebih beragam |
| `random_state` | 42 | hasil dapat direproduksi |
| `n_jobs` | −1 | memakai semua inti CPU |

Model dilatih pada 8.000 baris latih Kaggle (Fase 3) dan disimpan sebagai `app/models/rf_anxiety_model.joblib`, dengan metadata di `rf_anxiety_model_metadata.json`.

### 2.3 Perbandingan dengan algoritma lain

Semua algoritma dilatih pada data latih yang sama dengan validasi silang 5-fold, lalu diuji pada data uji yang sama (`scripts/train.py --stage compare`).

| Algoritma | MAE CV | RMSE CV | R² CV | MAE uji | R² uji |
|---|---|---|---|---|---|
| Baseline rata-rata | 1,2238 | 1,5134 | −0,0010 | 1,2370 | −0,0024 |
| Regresi linear | **0,7684** | **0,9549** | **0,6014** | **0,7548** | **0,6245** |
| Decision Tree (kedalaman 10) | 0,8814 | 1,1127 | 0,4583 | 0,8672 | 0,4955 |
| Gradient Boosting | 0,7728 | 0,9616 | 0,5958 | 0,7667 | 0,6155 |
| **Random Forest (dipakai)** | 0,7790 | 0,9663 | 0,5918 | 0,7668 | 0,6136 |

Pada data Kaggle, regresi linear sedikit lebih akurat. Selisih MAE-nya 0,01 poin pada skala 0–10. Hal ini wajar karena data Kaggle tampak sintetis dengan hubungan yang hampir linear. RF tetap dipakai karena:

1. Kinerjanya setara, jauh lebih baik dari baseline dan dari pohon tunggal.
2. Data kuesioner riil berbentuk ordinal dan tidak dijamin linear.
3. Metode pelatihan ulang dengan *warm start* (M3) memerlukan model *ensemble* pohon.

### 2.4 M2 — Faktor dominan

| Peringkat | Fitur | *Importance* |
|---|---|---|
| 1 | stress_level | 0,4268 |
| 2 | burnout_score | 0,3036 |
| 3 | financial_stress | 0,0630 |
| 4 | exam_pressure | 0,0493 |
| 5 | family_expectation | 0,0386 |
| 6 | study_hours_per_day | 0,0327 |
| 7 | sleep_hours | 0,0273 |
| 8 | physical_activity | 0,0228 |
| 9 | academic_performance | 0,0211 |
| 10 | age | 0,0113 |
| 11 | gender | 0,0035 |

Tingkat stres dan kelelahan menyumbang 73% kepentingan, sejalan dengan korelasi di Fase 2. Gender hampir tidak berpengaruh (0,35%), sehingga risiko bias gender kecil (diperiksa di Fase 5).

## 3. M3 — Pelatihan Ulang dengan Data Riil

Tujuannya adalah menyesuaikan model dari populasi mahasiswa (Kaggle) ke siswa SMA (kuesioner). Tujuh strategi dibandingkan (`spk/retrain.py`):

| Kode | Strategi | Penjelasan |
|---|---|---|
| S0 | Kaggle saja | model M1 tanpa pelatihan ulang (pembanding) |
| S1 | Data riil saja | RF baru hanya dari kuesioner (`min_samples_leaf=3`) |
| S2 (w = 1, 10, 50) | Gabungan berbobot | 8.000 baris Kaggle + data riil; tiap baris riil diberi bobot w |
| S3 (+200, +600) | *Warm start* | 200 pohon Kaggle dipertahankan, lalu ditambah 200 atau 600 pohon baru yang dilatih pada data riil |
| S4 | Data riil diperluas | S1 ditambah butir ekstra kuesioner (media sosial, pertemanan, pola makan, dll.); hanya dilaporkan, tidak dideploy |

Strategi dengan **MAE validasi silang terendah** di antara S0–S3 dipilih, lalu dilatih ulang pada seluruh respons. Hasilnya disimpan sebagai `rf_real_model.joblib`, dan aplikasi otomatis memakainya.

⟦ISI dari `reports/private/real_data_report.md`: tabel MAE/RMSE/R² CV dan holdout untuk S0–S4, strategi terpilih, *feature importance* model aktif.⟧

## 4. M4 — SMART

### 4.1 Langkah

1. **Matriks keputusan.** Setiap siswa memiliki 8 nilai kriteria (Fase 1 §4).
2. **Utilitas** (normalisasi min–maks memakai batas referensi):
   - benefit: `u = (x − min) / (max − min)`
   - cost: `u = (max − x) / (max − min)`
   - Nilai di luar batas dipotong ke rentang 0–1.
3. **Skor prioritas:** `P = Σ wⱼ uⱼ` dengan bobot sama `wⱼ = 1/8`. Siswa diurutkan dengan `rank(method="dense")` dari skor tertinggi.
4. **Skor tiap alternatif:** `Sₐ = Σ wₐⱼ uⱼ`, dengan bobot khusus alternatif a (tabel 4.2).
5. **Rekomendasi:** alternatif dengan Sₐ tertinggi; aplikasi menampilkan tiga teratas.
6. **Aturan pengaman:** bila prediksi kecemasan ≥ persentil 90 populasi referensi, konseling dan rujukan selalu ditampilkan.

### 4.2 Profil bobot

**Profil A — berbasis domain.** Setiap alternatif menekankan kriteria yang paling relevan dengannya. Contohnya, Sleep menekankan jam tidur dan Study menekankan jam belajar serta nilai. Di notebook, bobot Exercise berjumlah **1,05**, padahal SMART mensyaratkan Σw = 1. Aplikasi menormalkannya dengan membagi setiap bobot Exercise dengan 1,05.

| Kriteria | Sleep | Exercise* | Study | Counseling | Relaxation |
|---|---|---|---|---|---|
| Prediksi kecemasan | 0,15 | 0,143 | 0,10 | 0,30 | 0,20 |
| Jam belajar | 0,10 | 0,048 | 0,40 | 0,05 | 0,05 |
| Nilai rapor | 0,10 | 0,048 | 0,30 | 0,05 | 0,05 |
| Jam tidur | 0,40 | 0,048 | 0,00 | 0,05 | 0,20 |
| Aktivitas fisik | 0,05 | 0,429 | 0,00 | 0,05 | 0,10 |
| Tekanan finansial | 0,05 | 0,048 | 0,05 | 0,20 | 0,15 |
| Ekspektasi keluarga | 0,05 | 0,048 | 0,05 | 0,15 | 0,15 |
| *Burnout* | 0,10 | 0,190 | 0,10 | 0,15 | 0,10 |

\*setelah normalisasi (notebook: 0,15 / 0,05 / 0,05 / 0,05 / 0,45 / 0,05 / 0,05 / 0,20).

**Profil B — hampir seimbang.** Kriteria utama tiap alternatif mendapat 0,15–0,20, dan kriteria lain 0,10.

**Profil C — sama rata (kontrol).** Semua bobot 1/8. Karena kelima alternatif memakai bobot yang sama, semua skor seri. `idxmax` lalu selalu memilih alternatif pertama (Sleep). Profil C hanya menjadi pembanding.

### 4.3 Contoh perhitungan (siswa STU00004, profil A)

Siswa laki-laki, 17 tahun. Batas min/maks dari 20.000 siswa referensi.

| Kriteria | Nilai x | Min | Maks | Jenis | Utilitas u |
|---|---|---|---|---|---|
| Prediksi kecemasan | 4,417 | 0,367 | 7,091 | benefit | 0,602 |
| Jam belajar | 5,594 | 0,000 | 13,227 | benefit | 0,423 |
| Nilai rapor | 68,375 | 47,565 | 92,894 | cost | 0,541 |
| Jam tidur | 3,146 | 3,000 | 10,000 | cost | 0,979 |
| Aktivitas fisik | 2,539 | 0,000 | 7,000 | cost | 0,637 |
| Tekanan finansial | 7,278 | 0,000 | 10,000 | benefit | 0,728 |
| Ekspektasi keluarga | 2,577 | 0,000 | 10,000 | benefit | 0,258 |
| *Burnout* | 4,609 | 0,000 | 9,855 | benefit | 0,468 |

Contoh utilitas jam tidur (cost): u = (10,000 − 3,146) / (10,000 − 3,000) = 0,979.

**Skor prioritas** P = (0,602 + 0,423 + 0,541 + 0,979 + 0,637 + 0,728 + 0,258 + 0,468) / 8 = **0,580**, lebih tinggi dari 93% siswa referensi.

**Skor alternatif** (Σ bobot × utilitas):

| Peringkat | Alternatif | Skor | Kontribusi terbesar |
|---|---|---|---|
| 1 | **Sleep** | **0,706** | jam tidur 0,40 × 0,979 = 0,392 |
| 2 | Relaxation | 0,623 | jam tidur 0,196; prediksi kecemasan 0,121 |
| 3 | Exercise | 0,588 | aktivitas fisik 0,273 |
| 4 | Counseling | 0,564 | prediksi kecemasan 0,181; tekanan finansial 0,146 |
| 5 | Study | 0,488 | jam belajar 0,169; nilai rapor 0,162 |

Penjelasan yang dihasilkan aplikasi: *"Tidur mendapat skor tertinggi (0,706). Pendorong utama: jam tidur sedikit (3,1 jam), prediksi kecemasan tinggi (4,4/10), nilai rapor rendah (68). Selisih dengan alternatif kedua (Relaksasi) 0,083."*

### 4.4 Hasil pada populasi referensi (20.000 siswa)

| Alternatif | Profil A (notebook, Σ=1,05) | Profil A (dinormalkan) | Profil B |
|---|---|---|---|
| Sleep | 4.796 | 5.356 | 5.662 |
| Exercise | 8.866 | 6.905 | 4.673 |
| Study | 2.323 | 2.613 | 1.940 |
| Counseling | 1.863 | 2.202 | 7.553 |
| Relaxation | 2.152 | 2.924 | 172 |

Normalisasi menurunkan dominasi Exercise dari 44% menjadi 35%. Profil B lebih banyak merekomendasikan Counseling. Counseling memberi bobot 0,20 pada prediksi kecemasan dan 0,15 pada tekanan finansial serta ekspektasi keluarga. Ekspektasi keluarga rata-rata tinggi pada populasi ini (6,0 dari 10), sehingga skor Counseling ikut terangkat.

## 5. Keluaran Fase

| Berkas | Isi |
|---|---|
| `app/models/rf_anxiety_model.joblib` + metadata | model dasar (Kaggle), metrik, batas SMART |
| `app/models/model_comparison.json` | perbandingan 5 algoritma |
| `app/models/rf_real_model.joblib` + metadata + `real_summary.json` | model aktif setelah data riil (agregat saja) |
| `app/spk/smart.py`, `config.py` | implementasi SMART dan profil bobot |
