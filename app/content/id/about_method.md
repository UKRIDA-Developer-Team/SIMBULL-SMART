### Data

| Sumber | Isi | Peran |
|---|---|---|
| Kaggle *Student Mental Health & Burnout* (1 juta baris) | Sampel acak 2% = 20.000 baris, 20 kolom | Pralatih model; populasi referensi untuk analisis |
| Kuesioner Google Form siswa SMA | ±50 pertanyaan (akademik, tidur, media sosial, keluarga, aktivitas fisik, kelelahan, pertemanan, psikologis, pola makan) | Pelatihan ulang model dengan data riil; pengujian pada data baru |

Data kuesioner bersifat **rahasia**: berkas mentah tidak pernah masuk repositori, kolom pribadi (waktu isi, tanggal lahir, nama sekolah, nama teman) dibuang segera setelah usia dihitung, dan aplikasi hanya memuat ringkasan agregat.

### Persiapan data

- **Kaggle**: tanpa nilai hilang; `gender` dikodekan tetap (`Female=0, Male=1, Other=2`, sama dengan LabelEncoder di notebook); 50% sampel (10.000 baris) dibagi 80/20 menjadi data latih/uji (`random_state=42`).
- **Google Form → 11 fitur model** (`spk/gform.py`): jawaban teks diubah ke angka, lalu diskalakan ke rentang fitur Kaggle:
  - jam belajar & jam tidur: teks rentang ("1 jam 30 menit") → jam;
  - tekanan ujian: Likert 1-5 → 1-10;
  - tingkat stres: rata-rata ternormalisasi dari tugas bersamaan, waktu tidak cukup, tugas terlambat, belajar larut malam × 10;
  - tekanan finansial: kebalikan dari "uang saku cukup" × 10;
  - ekspektasi keluarga & burnout: rata-rata butir terkait × 10;
  - **target** skor kecemasan: jumlah 5 butir *Psikologis* (butir konsentrasi dibalik), 0-20 → 0-10.
  Butir pembentuk target **tidak pernah** dipakai sebagai fitur (mencegah *label leakage*).

### Pemodelan (Data Mining)

**Random Forest Regressor** (200 pohon, kedalaman maksimum 10, `min_samples_leaf=2`, `max_features="sqrt"`) memprediksi `anxiety_score`. Dengan data riil, tujuh strategi dibandingkan lewat *repeated 5-fold cross-validation*: model Kaggle apa adanya, RF hanya data riil, gabungan Kaggle + riil dengan bobot 1/10/50, dan *warm start* (menambah 200/600 pohon yang dilatih pada data riil). Strategi dengan MAE terendah dipakai.

### Keputusan (SPK - SMART)

1. Delapan kriteria: prediksi kecemasan RF, jam belajar, nilai rapor, jam tidur, aktivitas fisik, tekanan finansial, ekspektasi keluarga, burnout.
2. Utilitas: *benefit* `u = (x - min)/(max - min)`, *cost* `u = (max - x)/(max - min)`; di sini "benefit" berarti **makin tinggi makin membutuhkan perhatian**. Batas min/max diambil dari populasi referensi agar satu siswa pun dapat dinilai.
3. **Skor prioritas** = rata-rata utilitas (bobot sama) → peringkat siswa.
4. **Skor alternatif** = Σ bobot × utilitas, dengan bobot khusus tiap alternatif (profil A/B/C) → alternatif dengan skor tertinggi direkomendasikan.

### Evaluasi

MAE, RMSE, R² pada data uji; perbandingan dengan regresi linear, pohon keputusan, gradient boosting, dan baseline rata-rata; uji sensitivitas bobot ±10%/±20% per siswa dan populasi; stabilitas 100 iterasi acak; perbandingan profil bobot; pemeriksaan keadilan per gender; evaluasi pada respons baru lewat unggahan berkas.
