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
| `n_estimators` | 300 | cukup banyak pohon agar prediksi stabil pada data besar |
| `max_depth` | 12 | cukup dalam untuk 554.036 baris tanpa menghafal data latih |
| `min_samples_split` | 2 | bawaan scikit-learn |
| `min_samples_leaf` | 50 (3 untuk data riil) | setiap daun mewakili minimal 50 siswa: prediksi lebih halus dan tidak menghafal |
| `max_features` | 0,75 | tiap pemisahan melihat 75% fitur (8 dari 11) |
| `max_samples` | 0,6 | tiap pohon dilatih pada 60% baris latih, sehingga pohon lebih beragam |
| `random_state` | 42 | hasil dapat direproduksi |
| `n_jobs` | −1 | memakai semua inti CPU saat pelatihan |

Nilai ini dipilih dengan ***random search*** (`scripts/train.py --stage tune`, hasil di `models/rf_tuning.json`): 25 kombinasi parameter, masing-masing dinilai dengan **validasi silang 5-fold** pada 50.000 baris latih. Kombinasi terbaik mencapai R² CV 0,5996; pengaturan notebook (200 pohon, kedalaman 10, `max_features="sqrt"`) mencapai 0,5966 dan berada di peringkat 11. Data uji tidak dipakai selama pencarian. Pengaturan notebook tetap dipakai untuk data kuesioner yang kecil.

Model dilatih pada seluruh 554.036 baris latih (Fase 3) dan disimpan sebagai `app/models/rf_anxiety_model.joblib` (±29 MB), dengan metadata di `rf_anxiety_model_metadata.json`.

### 2.3 Perbandingan dengan algoritma lain

Validasi silang 5-fold memakai 50.000 baris latih yang sama untuk semua algoritma. Skor uji didapat dari model yang dilatih pada seluruh 554.036 baris latih dan diuji pada 138.509 baris uji (`scripts/train.py --stage compare`).

| Algoritma | MAE CV | RMSE CV | R² CV | MAE uji | R² uji |
|---|---|---|---|---|---|
| Baseline rata-rata | 1,2128 | 1,5040 | −0,0001 | 1,2217 | 0,0000 |
| Regresi linear | **0,7604** | **0,9499** | **0,6011** | 0,7602 | 0,6064 |
| Decision Tree (kedalaman 10) | 0,7989 | 1,0047 | 0,5537 | 0,7644 | 0,6010 |
| Gradient Boosting | 0,7606 | 0,9505 | 0,6006 | **0,7579** | **0,6083** |
| **Random Forest (dipakai)** | 0,7610 | 0,9515 | 0,5998 | 0,7583 | 0,6077 |

Pada data uji, Random Forest, Gradient Boosting, dan regresi linear praktis setara: selisih R² paling besar 0,002. Semua jauh lebih baik dari baseline. Pohon tunggal mendekati karena data latih sangat besar, tetapi tetap paling lemah di antara model yang dilatih. RF tetap dipakai karena:

1. Kinerjanya setara dengan algoritma terbaik.
2. Data kuesioner riil berbentuk ordinal dan tidak dijamin linear.
3. Metode pelatihan ulang dengan *warm start* (M3) memerlukan model *ensemble* pohon.

**Batas R².** Semua jenis model berhenti di R² ≈ 0,61. Hutan acak yang dilatih pada sisa galat regresi linear hanya mencapai R² −0,01, artinya sekitar 40% variasi skor kecemasan adalah derau yang tidak dibawa 11 fitur. Hanya `mental_health_index` yang dapat menaikkannya (ke ±0,80), tetapi kolom itu dihitung dari target dan termasuk *leakage*.

### 2.4 M2 — Faktor dominan

| Peringkat | Fitur | *Importance* |
|---|---|---|
| 1 | stress_level | 0,7512 |
| 2 | burnout_score | 0,2080 |
| 3 | financial_stress | 0,0128 |
| 4 | sleep_hours | 0,0072 |
| 5 | exam_pressure | 0,0070 |
| 6 | family_expectation | 0,0032 |
| 7 | study_hours_per_day | 0,0032 |
| 8 | physical_activity | 0,0030 |
| 9 | academic_performance | 0,0029 |
| 10 | age | 0,0011 |
| 11 | gender | 0,0004 |

Tingkat stres dan kelelahan menyumbang 96% kepentingan, sejalan dengan korelasi di Fase 2. Dengan daun minimal 50 siswa, model hampir hanya memisahkan pada dua fitur terkuat; fitur lain tetap berperan dalam SMART sebagai kriteria tersendiri. Gender hampir tidak berpengaruh (0,04%), sehingga risiko bias gender kecil (diperiksa di Fase 5).

## 3. M3 — Pelatihan Ulang dengan Data Riil

Tujuannya adalah menyesuaikan model dari populasi mahasiswa (Kaggle) ke siswa SMA (kuesioner). Tujuh strategi dibandingkan (`spk/retrain.py`):

| Kode | Strategi | Penjelasan |
|---|---|---|
| S0 | Kaggle saja | model M1 tanpa pelatihan ulang (pembanding) |
| S1 | Data riil saja | RF baru hanya dari kuesioner (`min_samples_leaf=3`) |
| S2 (w = 1, 10, 50) | Gabungan berbobot | 8.000 baris Kaggle + data riil; tiap baris riil diberi bobot w |
| S3 (+200, +600) | *Warm start* | 300 pohon Kaggle dipertahankan, lalu ditambah 200 atau 600 pohon baru yang dilatih pada data riil |
| S4 | Data riil diperluas | S1 ditambah butir ekstra kuesioner (media sosial, pertemanan, pola makan, dll.); hanya dilaporkan, tidak dideploy |

Strategi dengan **MAE validasi silang terendah** di antara S0–S3 dipilih, lalu dilatih ulang pada seluruh respons. Hasilnya disimpan sebagai `rf_real_model.joblib`, dan aplikasi otomatis memakainya.

### 3.1 Hasil pada data riil

Validasi silang 5-fold × 2 pada 233 respons pengembangan; *holdout* 59 respons yang tidak dipakai memilih strategi.

| Strategi | MAE CV (± sd) | R² CV | MAE *holdout* | R² *holdout* |
|---|---|---|---|---|
| S0 Kaggle saja | 1,751 ± 0,204 | −0,605 | 1,874 | −0,346 |
| **S1 Data riil saja (dipilih)** | **1,251 ± 0,082** | **0,204** | **1,113** | **0,441** |
| S2 gabungan, w = 1 | 1,287 ± 0,085 | 0,162 | 1,185 | 0,389 |
| S2 gabungan, w = 10 | 1,263 ± 0,076 | 0,189 | 1,155 | 0,443 |
| S2 gabungan, w = 50 | 1,252 ± 0,072 | 0,200 | 1,158 | 0,422 |
| S3 *warm start* +200 | 1,444 ± 0,140 | −0,070 | 1,445 | 0,179 |
| S3 *warm start* +600 | 1,309 ± 0,097 | 0,132 | 1,239 | 0,383 |
| S4 riil + butir ekstra (tidak dideploy) | 1,203 ± 0,093 | 0,280 | – | – |

Temuan:

- **Model Kaggle tidak berlaku untuk siswa SMA.** S0 memiliki R² negatif: lebih buruk daripada menebak rata-rata. Penyebabnya pergeseran sebaran (rata-rata kecemasan riil 5,0 vs 3,0 di Kaggle) dan pola faktor yang berbeda (Fase 2).
- **S1 dipilih**, dengan S2 w = 50 hampir sama (selisih MAE CV 0,001). Menambahkan data Kaggle tidak membantu. *Warm start* paling buruk di antara strategi latih ulang, karena 300 pohon Kaggle tetap ikut memberi suara.
- **S4** (dengan butir ekstra seperti kualitas tidur, media sosial, dan konflik teman) paling akurat pada CV (MAE 1,203). Butir ini tidak ada di dataset Kaggle maupun di formulir aplikasi, sehingga hanya dilaporkan sebagai arah pengembangan.
- R² *holdout* (0,44) lebih tinggi daripada R² CV (0,20). Dengan hanya 59 respons, angka *holdout* memiliki ketidakpastian besar; R² CV memberi gambaran yang lebih hati-hati.

Model aktif: 200 pohon, kedalaman 10, `max_features="sqrt"`, `min_samples_leaf=3` (pengaturan notebook dengan daun lebih besar untuk data kecil), dilatih pada 292 respons.

| Peringkat | Fitur | *Importance* (model aktif) |
|---|---|---|
| 1 | burnout_score | 0,222 |
| 2 | exam_pressure | 0,196 |
| 3 | family_expectation | 0,139 |
| 4 | stress_level | 0,125 |
| 5 | academic_performance | 0,083 |
| 6 | sleep_hours | 0,061 |
| 7 | study_hours_per_day | 0,049 |
| 8 | age | 0,038 |
| 9 | physical_activity | 0,033 |
| 10 | financial_stress | 0,033 |
| 11 | gender | 0,020 |

Berbeda dengan model Kaggle (stres 75%), model riil membagi kepentingan lebih merata: *burnout*, tekanan ujian, dan ekspektasi keluarga paling berpengaruh, sesuai korelasi pada data riil.

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
6. **Aturan pengaman:** bila prediksi kecemasan ≥ persentil 90 kelompok pembanding (292 responden riil untuk model aktif, ambang 6,28), konseling dan rujukan selalu ditampilkan.

### 4.2 Bobot alternatif

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

Dua susunan bobot lain diuji sebagai pembanding, tetapi tidak dipakai aplikasi akhir:

**Profil B — hampir seimbang.** Kriteria utama tiap alternatif mendapat 0,15–0,20, dan kriteria lain 0,10.

**Profil C — sama rata (kontrol).** Semua bobot 1/8. Karena kelima alternatif memakai bobot yang sama, semua skor seri. `idxmax` lalu selalu memilih alternatif pertama (Sleep). Profil C hanya menjadi pembanding.

Aplikasi akhir hanya memakai **profil A** (lihat Fase 5, stabilitas bobot); pengguna tidak lagi dapat memilih profil.

### 4.3 Contoh perhitungan (siswa STU00006, profil A)

Siswa laki-laki, 19 tahun, dari populasi referensi. Batas min/maks dari 20.000 siswa referensi.

| Kriteria | Nilai x | Min | Maks | Jenis | Utilitas u |
|---|---|---|---|---|---|
| Prediksi kecemasan | 3,800 | 0,333 | 7,161 | benefit | 0,508 |
| Jam belajar | 5,360 | 0,000 | 14,000 | benefit | 0,383 |
| Nilai rapor | 69,234 | 45,172 | 92,627 | cost | 0,493 |
| Jam tidur | 4,194 | 3,000 | 10,000 | cost | 0,829 |
| Aktivitas fisik | 1,674 | 0,000 | 7,000 | cost | 0,761 |
| Tekanan finansial | 6,869 | 0,000 | 10,000 | benefit | 0,687 |
| Ekspektasi keluarga | 5,802 | 0,000 | 10,000 | benefit | 0,580 |
| *Burnout* | 2,587 | 0,000 | 9,855 | benefit | 0,263 |

Contoh utilitas jam tidur (cost): u = (10,000 − 4,194) / (10,000 − 3,000) = 0,829.

**Skor prioritas** P = (0,508 + 0,383 + 0,493 + 0,829 + 0,761 + 0,687 + 0,580 + 0,263) / 8 = **0,563**, lebih tinggi dari 91% siswa referensi.

**Skor alternatif** (Σ bobot × utilitas):

| Peringkat | Alternatif | Skor | Kontribusi terbesar |
|---|---|---|---|
| 1 | **Sleep** | **0,623** | jam tidur 0,40 × 0,829 = 0,332 |
| 2 | Relaxation | 0,604 | jam tidur 0,166; tekanan finansial 0,103 |
| 3 | Exercise | 0,590 | aktivitas fisik 0,326 |
| 4 | Counseling | 0,539 | prediksi kecemasan 0,152; tekanan finansial 0,137 |
| 5 | Study | 0,441 | jam belajar 0,153; nilai rapor 0,148 |

Penjelasan yang dihasilkan aplikasi: *"Tidur mendapat skor tertinggi (0,623). Pendorong utama: jam tidur sedikit (4,2 jam), prediksi kecemasan tinggi (3,8/10), nilai rapor 69,2. Selisih dengan alternatif kedua (Relaksasi) 0,020. Selisihnya kecil, jadi Relaksasi juga layak dipertimbangkan."*

### 4.4 Hasil pada populasi referensi (20.000 siswa)

| Alternatif | Profil A (notebook, Σ=1,05) | Profil A (dinormalkan) | Profil B |
|---|---|---|---|
| Sleep | 4.648 | 5.238 | 5.547 |
| Exercise | 9.338 | 7.323 | 4.941 |
| Study | 1.637 | 1.882 | 1.394 |
| Counseling | 1.956 | 2.337 | 7.922 |
| Relaxation | 2.421 | 3.220 | 196 |

Normalisasi menurunkan dominasi Exercise dari 47% menjadi 37%. Profil B lebih banyak merekomendasikan Counseling. Counseling memberi bobot 0,20 pada prediksi kecemasan dan 0,15 pada tekanan finansial serta ekspektasi keluarga. Ekspektasi keluarga rata-rata tinggi pada populasi ini (6,0 dari 10), sehingga skor Counseling ikut terangkat.

## 5. Keluaran Fase

| Berkas | Isi |
|---|---|
| `app/models/rf_anxiety_model.joblib` + metadata | model dasar (Kaggle), metrik, batas SMART |
| `app/models/model_comparison.json` | perbandingan 5 algoritma |
| `app/models/rf_tuning.json` | hasil *random search* 25 pengaturan RF |
| `app/models/rf_real_model.joblib` + metadata + `real_summary.json` | model aktif setelah data riil (agregat saja) |
| `app/spk/smart.py`, `config.py` | implementasi SMART dan bobot alternatif |
