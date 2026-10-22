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

### 2.1 Model dasar (Kaggle), data uji 2.000 baris

| MAE | MSE | RMSE | R² |
|---|---|---|---|
| **0,7668** | 0,9112 | 0,9546 | **0,6136** |

Rata-rata prediksi meleset ±0,77 poin pada skala 0–10, dan model menjelaskan 61% variasi skor kecemasan. Hasil ini sama persis dengan notebook Colab, yang diverifikasi otomatis di `tests/test_smart.py`.

### 2.2 Analisis galat

- Grafik aktual vs prediksi (halaman Analisis) menunjukkan titik mengikuti garis diagonal. Prediksi untuk skor ekstrem cenderung **ditarik ke tengah**: rentang prediksi 0,37–7,09, sedangkan rentang aktual 0–9,11. Ini sifat umum Random Forest, yang merata-ratakan pohon.
- Konsekuensinya, siswa dengan kecemasan sangat tinggi dapat terprediksi lebih rendah dari sebenarnya. Karena itu aturan pengaman memakai **persentil** (10% prediksi tertinggi), bukan ambang absolut.

### 2.3 Perbandingan algoritma

Lihat Fase 4 §2.3. RF setara dengan regresi linear dan gradient boosting (selisih MAE ≤ 0,012), jauh lebih baik dari baseline (MAE 1,237) dan pohon tunggal (MAE 0,867).

### 2.4 Pelatihan ulang dan pengujian pada data riil

| Uji | Data | Hasil |
|---|---|---|
| Pemilihan strategi | CV 5-fold × 2 pada 80% data kuesioner | ⟦ISI: MAE CV per strategi⟧ |
| *Holdout* | 20% data kuesioner yang tidak dipakai memilih | ⟦ISI: MAE/RMSE/R² model terpilih vs model Kaggle (S0)⟧ |
| Data baru | respons yang masuk setelah pelatihan (`scripts/evaluate.py` atau unggah di aplikasi) | ⟦ISI⟧ |

Kriteria D4 (Fase 1) tercapai bila MAE model terpilih lebih rendah dari S0 pada *holdout*.

## 3. Evaluasi Modul Keputusan (SMART)

### 3.1 Sensitivitas bobot

**Per kriteria.** Bobot satu kriteria diubah −20%, −10%, +10%, dan +20% pada semua alternatif. Bobot lain dinormalkan ulang agar Σw = 1. Yang dihitung adalah porsi siswa (dari 20.000) yang rekomendasi utamanya berubah.

| Kriteria (profil A) | −20% | −10% | +10% | +20% |
|---|---|---|---|---|
| Prediksi kecemasan | 1,5% | 0,6% | 0,7% | 1,3% |
| Jam belajar | 2,3% | 1,1% | 1,0% | 2,0% |
| Nilai rapor | 2,2% | 1,1% | 1,0% | 2,1% |
| Jam tidur | 5,0% | 2,4% | 2,1% | 3,9% |
| Aktivitas fisik | 6,5% | 3,0% | 2,8% | 5,0% |
| Tekanan finansial | 2,6% | 1,3% | 1,3% | 2,5% |
| Ekspektasi keluarga | 2,8% | 1,5% | 1,3% | 2,5% |
| *Burnout* | 3,1% | 1,5% | 1,4% | 2,8% |

Perubahan ±10% pada satu bobot mengubah paling banyak 3% rekomendasi. Kriteria paling sensitif adalah aktivitas fisik dan jam tidur, karena keduanya menjadi bobot dominan Exercise dan Sleep.

**Acak menyeluruh.** Semua bobot dikalikan faktor acak U(1 − p, 1 + p) sebanyak 100 kali.

| Profil | p | Rekomendasi utama tetap | Tiga besar tetap | Iterasi terburuk |
|---|---|---|---|---|
| A | ±10% | **94,6%** | 94,9% | 90,9% |
| A | ±20% | 89,4% | 90,1% | 82,2% |
| B | ±10% | 88,8% | 83,4% | 78,4% |
| B | ±20% | 78,5% | 68,7% | 62,5% |

Profil A lebih stabil karena bobotnya lebih tegas membedakan alternatif. Profil B hampir seimbang, sehingga lebih banyak siswa berada di dekat batas seri. Kriteria S1 (≥ 90% tetap pada ±10%) terpenuhi oleh profil A. Karena itu **profil A menjadi bawaan aplikasi**.

**Per siswa.** Halaman Rekomendasi menampilkan tabel 8 kriteria × 4 perubahan untuk siswa yang sedang dinilai. Sel yang rekomendasinya berubah diwarnai, sehingga guru BK dapat melihat apakah hasil siswa tersebut kokoh atau berada di batas.

### 3.2 Perbandingan profil

| Alternatif | A (dinormalkan) | B | C |
|---|---|---|---|
| Sleep | 5.356 | 5.662 | 20.000 |
| Exercise | 6.905 | 4.673 | 0 |
| Study | 2.613 | 1.940 | 0 |
| Counseling | 2.202 | 7.553 | 0 |
| Relaxation | 2.924 | 172 | 0 |

Profil C menunjukkan mengapa bobot khusus per alternatif diperlukan. Tanpa bobot khusus, SMART tidak dapat membedakan alternatif.

### 3.3 Temuan: bobot notebook tidak ternormalisasi

Pada notebook, bobot Exercise profil A berjumlah 1,05. Akibatnya skor Exercise naik 5%, dan Exercise direkomendasikan untuk 8.866 siswa (44%). Setelah dinormalkan, angkanya 6.905 siswa (35%). Aplikasi memakai versi yang dinormalkan. Uji otomatis memastikan setiap profil berjumlah 1 dan tetap dapat mereproduksi angka notebook dengan bobot aslinya.

### 3.4 Contoh kasus

Contoh STU00004 (Fase 4 §4.3) direkomendasikan **Sleep**. Jam tidurnya 3,1 jam, termasuk yang terendah pada populasi (utilitas 0,979). Hasil ini masuk akal secara domain. Skor prioritasnya 0,580 (persentil 93), jadi siswa ini termasuk yang perlu ditangani lebih dulu.

## 4. Keadilan (*Fairness*)

| Gender | n (uji) | MAE |
|---|---|---|
| Female | 964 | 0,768 |
| Male | 948 | 0,767 |
| Other | 88 | 0,751 |

Selisih MAE antar gender < 0,02 poin. Sebaran rekomendasi profil A per gender juga hampir sama: Exercise 34–35%, Sleep 25–27%, Counseling 11–13%. Jadi tidak ditemukan bias gender yang berarti. Untuk data riil, pemeriksaan yang sama dijalankan pada *holdout* ⟦ISI⟧. Kelompok dengan kurang dari 5 orang tidak ditampilkan demi privasi.

## 5. Evaluasi terhadap Tujuan Bisnis

| Tujuan (Fase 1) | Bukti | Status |
|---|---|---|
| Deteksi dini | prediksi skor dari faktor non-gejala; persentil terhadap populasi | tercapai |
| Prioritas siswa | skor prioritas + unggah banyak siswa + unduh daftar | tercapai |
| Rekomendasi beralasan | tiga teratas, grafik kontribusi, kalimat alasan, uji sensitivitas | tercapai |
| Sesuai populasi SMA | pelatihan ulang dengan kuesioner | ⟦ISI setelah data riil⟧ |
| Diterima pengguna | Google Form evaluasi (pemahaman, kesesuaian, manfaat, stabilitas, tampilan) | ⟦ISI setelah uji pengguna⟧ |

## 6. Keputusan Lanjutan

1. **Lanjut ke deployment** dengan model Kaggle sebagai model awal dan profil A sebagai bawaan.
2. Jalankan pipeline data riil begitu ekspor kuesioner tersedia, lalu perbarui metrik di laporan ini.
3. Validasi bobot profil A dengan guru BK atau psikolog, yaitu kesesuaian rekomendasi pertama pada 20–30 kasus.
4. Pengembangan lanjutan (dari rancangan awal): segmentasi siswa (*clustering*), aturan asosiasi kebiasaan, dan bobot yang diturunkan dari *feature importance*.
