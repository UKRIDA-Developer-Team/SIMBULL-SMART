# Fase 5 — Evaluation

**Proyek:** SPK Rekomendasi Penanganan Kecemasan Siswa (Random Forest + SMART)
**Metodologi:** CRISP-DM — Fase 5 dari 6

---

## 1. Kerangka Evaluasi

| Lapis | Pertanyaan | Metode |
|---|---|---|
| Teknis (Data Mining) | Seberapa akurat prediksi skor kecemasan? | MAE, MSE, RMSE, R², perbandingan algoritma, analisis galat |
| Keputusan (SPK) | Apakah rekomendasi stabil dan masuk akal? | Uji sensitivitas bobot, perbandingan profil, contoh kasus |
| Etika | Apakah hasil adil antar kelompok? | MAE dan sebaran rekomendasi per gender |
| Bisnis | Apakah tujuan Fase 1 tercapai? | Kriteria keberhasilan, evaluasi pengguna |

## 2. Metrik Regresi

Masalahnya regresi, jadi metrik yang dipakai:

| Metrik | Rumus | Arti |
|---|---|---|
| MAE | (1/n) Σ \|y − ŷ\| | rata-rata selisih absolut, dalam satuan skor (0–10) |
| MSE | (1/n) Σ (y − ŷ)² | menghukum kesalahan besar |
| RMSE | √MSE | seperti MSE, dalam satuan skor |
| R² | 1 − SS_res / SS_tot | porsi variasi target yang dijelaskan model |

### 2.1 Model dasar (Kaggle), data uji 138.509 baris

| MAE | MSE | RMSE | R² |
|---|---|---|---|
| **0,7583** | 0,8969 | 0,9470 | **0,6077** |

Rata-rata prediksi meleset ±0,76 poin pada skala 0–10, dan model menjelaskan 61% variasi skor kecemasan. Dengan 138.509 baris uji, R² hanya bergeser ±0,002 bila pembagian data diacak ulang, jadi angka ini bukan kebetulan pembagian.

**Dibandingkan notebook.** Notebook melaporkan R² 0,6136 pada 2.000 baris ujinya sendiri. Angka itu tidak sebanding karena diukur pada baris yang berbeda: dengan 40 pembagian acak lain, cara notebook rata-rata hanya mencapai R² 0,599, dan hanya 8% pembagian mencapai 0,6136. Pada 137.365 baris uji yang tidak pernah dilatih oleh kedua model, model notebook mencapai R² 0,598 (MAE 0,769) dan model ini 0,608 (MAE 0,758). Jadi model baru lebih baik pada data yang identik.

### 2.2 Analisis galat

- Grafik aktual vs prediksi (Laporan teknis, Bab 2) menunjukkan titik mengikuti garis diagonal. Prediksi untuk skor ekstrem cenderung **ditarik ke tengah**: rentang prediksi 0,33–7,21, sedangkan rentang aktual 0–9,63. Ini sifat umum Random Forest, yang merata-ratakan pohon.
- Konsekuensinya, siswa dengan kecemasan sangat tinggi dapat terprediksi lebih rendah dari sebenarnya. Karena itu aturan pengaman memakai **persentil** (10% prediksi tertinggi), bukan ambang absolut.

### 2.3 Perbandingan algoritma

Lihat Fase 4 §2.3. RF setara dengan regresi linear dan gradient boosting (selisih R² uji ≤ 0,002), jauh lebih baik dari baseline (MAE 1,222) dan lebih baik dari pohon tunggal (MAE 0,764).

### 2.4 Pelatihan ulang dan pengujian pada data riil

| Uji | Data | Hasil |
|---|---|---|
| Pemilihan strategi | CV 5-fold × 2 pada 233 respons pengembangan | S1 (data riil saja) terbaik: MAE CV 1,251 ± 0,082, R² CV 0,204; S0 (Kaggle): MAE 1,751, R² −0,605 |
| *Holdout* | 59 respons yang tidak dipakai memilih | S1: MAE 1,113, RMSE 1,393, R² 0,441; S0: MAE 1,874, RMSE 2,162, R² −0,346 |

Kriteria D4 (Fase 1) **tercapai**: MAE model terpilih 41% lebih rendah daripada model Kaggle pada *holdout*. Rata-rata prediksi pada 292 respons (5,00) sama dengan rata-rata skor sebenarnya (5,01), sedangkan model Kaggle meremehkan kecemasan siswa SMA.

Per versi formulir (*holdout*): formulir awal MAE 1,000 (39 respons), formulir revisi MAE 1,334 (20 respons). Galat formulir revisi lebih besar, tetapi kelompoknya kecil.

**Perbandingan Kaggle dan data riil.** Pada data Kaggle, model mencapai R² 0,608; pada siswa SMA hanya 0,20 (CV) sampai 0,44 (*holdout*). Data riil jauh lebih sedikit (292 vs 554.036 baris), skor gabungannya kurang konsisten (α tingkat stres 0,32), dan jawaban *self-report* lebih bising. Dengan galat rata-rata ±1,1 poin pada skala 0–10, prediksi cukup untuk **mengurutkan** siswa (skrining), tetapi tidak untuk menetapkan skor pasti.

## 3. Evaluasi Modul Keputusan (SMART)

### 3.1 Sensitivitas bobot

**Per kriteria.** Bobot satu kriteria diubah −20%, −10%, +10%, dan +20% pada semua alternatif. Bobot lain dinormalkan ulang agar Σw = 1. Yang dihitung adalah porsi siswa (dari 20.000) yang rekomendasi utamanya berubah.

| Kriteria (profil A) | −20% | −10% | +10% | +20% |
|---|---|---|---|---|
| Prediksi kecemasan | 1,5% | 0,8% | 0,7% | 1,4% |
| Jam belajar | 2,1% | 1,0% | 0,9% | 1,8% |
| Nilai rapor | 1,8% | 1,0% | 1,0% | 1,9% |
| Jam tidur | 5,5% | 2,5% | 2,2% | 4,1% |
| Aktivitas fisik | 7,0% | 3,2% | 2,9% | 5,2% |
| Tekanan finansial | 2,9% | 1,5% | 1,4% | 2,5% |
| Ekspektasi keluarga | 2,9% | 1,6% | 1,4% | 2,7% |
| *Burnout* | 3,2% | 1,5% | 1,6% | 3,1% |

Perubahan ±10% pada satu bobot mengubah paling banyak 3,2% rekomendasi. Kriteria paling sensitif adalah aktivitas fisik dan jam tidur, karena keduanya menjadi bobot dominan Exercise dan Sleep.

**Acak menyeluruh.** Semua bobot dikalikan faktor acak U(1 − p, 1 + p) sebanyak 100 kali.

| Profil | p | Rekomendasi utama tetap | Tiga besar tetap | Iterasi terburuk |
|---|---|---|---|---|
| A | ±10% | **94,3%** | 95,3% | 90,7% |
| A | ±20% | 89,0% | 90,6% | 82,5% |
| B | ±10% | 89,1% | 82,9% | 78,1% |
| B | ±20% | 78,8% | 68,0% | 62,0% |

Profil A lebih stabil karena bobotnya lebih tegas membedakan alternatif. Profil B hampir seimbang, sehingga lebih banyak siswa berada di dekat batas seri. Kriteria S1 (≥ 90% tetap pada ±10%) terpenuhi oleh profil A. Karena itu **profil A dipilih dan menjadi satu-satunya bobot di aplikasi**.

**Per siswa.** Halaman Rekomendasi menampilkan tabel 8 kriteria × 4 perubahan untuk siswa yang sedang dinilai. Sel yang rekomendasinya berubah diwarnai, sehingga guru BK dapat melihat apakah hasil siswa tersebut kokoh atau berada di batas.

### 3.2 Perbandingan profil

| Alternatif | A | B | C |
|---|---|---|---|
| Sleep | 5.238 | 5.547 | 20.000 |
| Exercise | 7.323 | 4.941 | 0 |
| Study | 1.882 | 1.394 | 0 |
| Counseling | 2.337 | 7.922 | 0 |
| Relaxation | 3.220 | 196 | 0 |

Profil C menunjukkan mengapa bobot khusus per alternatif diperlukan. Tanpa bobot khusus, SMART tidak dapat membedakan alternatif.

### 3.3 Contoh kasus

Contoh STU00006 (Fase 4 §4.3) direkomendasikan **Sleep**. Jam tidurnya 4,2 jam, jauh di bawah rata-rata 6,5 jam (utilitas 0,829). Hasil ini masuk akal secara domain. Relaksasi hanya terpaut 0,020, dan aplikasi menyebutkannya sebagai pilihan yang juga layak. Skor prioritasnya 0,563 (persentil 91), jadi siswa ini termasuk yang perlu ditangani lebih dulu.

### 3.5 Hasil SPK pada siswa SMA (data riil)

Model aktif (S1) dan batas SMART dari 292 respons riil, dihitung untuk setiap responden:

| Alternatif | Profil A | Profil B |
|---|---|---|
| Sleep | 92 | 38 |
| Exercise | 159 | 140 |
| Study | 6 | 5 |
| Counseling | 18 | 30 |
| Relaxation | 17 | 79 |

- Olahraga paling sering direkomendasikan (54% pada profil A): median aktivitas fisik responden hanya 1,5 hari per minggu.
- Strategi belajar jarang muncul (2%), karena jam belajar di luar sekolah rendah (median 1,5 jam) sehingga utilitasnya kecil.
- **Stabilitas** pada data riil (100 kali bobot diacak ±10%): profil A 95,5% rekomendasi utama tetap (iterasi terburuk 91,8%), profil B 87,7%. Kriteria S1 tetap terpenuhi oleh profil A.
- **Aturan pengaman:** batas persentil 90 prediksi riil adalah 6,28; 30 dari 292 responden (10%) mendapat rekomendasi konseling dan rujukan.

## 4. Keadilan (*Fairness*)

| Gender | n (uji) | MAE |
|---|---|---|
| Female | 66.677 | 0,760 |
| Male | 66.303 | 0,756 |
| Other | 5.529 | 0,765 |

Selisih MAE antar gender < 0,01 poin. Sebaran rekomendasi profil A per gender pada 20.000 siswa referensi juga hampir sama: Exercise 35–37%, Sleep 26–27%, Counseling 10–12%. Jadi tidak ditemukan bias gender yang berarti. Pada *holdout* data riil:

| Gender | n (*holdout*) | MAE | Rata-rata prediksi | Rata-rata sebenarnya |
|---|---|---|---|---|
| Female | 29 | 1,262 | 5,33 | 5,10 |
| Male | 30 | 0,969 | 5,02 | 5,10 |

Galat pada siswa perempuan 0,29 poin lebih besar, dan prediksinya sedikit lebih tinggi daripada skor sebenarnya. Kelompoknya kecil (29 dan 30 orang), jadi selisih ini belum pasti, tetapi perlu dipantau saat respons bertambah. Gender hanya menyumbang 2% kepentingan model. Kelompok dengan kurang dari 5 orang tidak ditampilkan demi privasi.

## 5. Evaluasi terhadap Tujuan Bisnis

| Tujuan (Fase 1) | Bukti | Status |
|---|---|---|
| Deteksi dini | prediksi skor dari faktor non-gejala; persentil terhadap populasi | tercapai |
| Prioritas siswa | skor prioritas + unggah banyak siswa + unduh daftar | tercapai |
| Rekomendasi beralasan | tiga teratas, grafik kontribusi, kalimat alasan, uji sensitivitas | tercapai |
| Sesuai populasi SMA | pelatihan ulang dengan 292 respons kuesioner; MAE *holdout* 1,113 vs 1,874 model Kaggle | tercapai, dengan akurasi sedang (R² 0,20–0,44) |
| Diterima pengguna | Google Form evaluasi (pemahaman, kesesuaian, manfaat, stabilitas, tampilan) | ⟦ISI setelah uji pengguna⟧ |

## 6. Keputusan Lanjutan

1. **Lanjut ke deployment** dengan model data riil (S1) sebagai model aktif dan bobot profil A. Model Kaggle tetap tersedia sebagai pembanding (`SPK_MODEL=base`).
2. Kumpulkan respons baru dan uji dengan `scripts/evaluate.py` atau unggah di aplikasi; latih ulang bila respons bertambah banyak.
3. Perbaiki butir tingkat stres dan tekanan ujian (α < 0,4), dan pertimbangkan butir kualitas tidur, konflik teman, dan media sosial saat belajar sebagai fitur (S4 terbaik pada CV).
4. Validasi bobot profil A dengan guru BK atau psikolog, yaitu kesesuaian rekomendasi pertama pada 20–30 kasus.
5. Pengembangan lanjutan (dari rancangan awal): segmentasi siswa (*clustering*), aturan asosiasi kebiasaan, dan bobot yang diturunkan dari *feature importance*.
