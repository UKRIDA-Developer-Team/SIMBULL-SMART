### Data

| Sumber | Isi | Peran |
|---|---|---|
| Kaggle *Student Mental Health & Burnout* (1 juta baris) | Hanya rentang usia pelajar 14-25 = 692.545 baris (berkas berisi usia 17-25), dibagi 80/20: 554.036 baris latih, 138.509 baris uji | Pralatih model; 20.000 baris uji menjadi populasi referensi untuk analisis |
| Kuesioner Google Form siswa SMA | ±50 pertanyaan (akademik, tidur, media sosial, keluarga, aktivitas fisik, kelelahan, pertemanan, psikologis, pola makan) | Pelatihan ulang model dengan data riil; pengujian pada data baru |

Data kuesioner bersifat **rahasia**: berkas mentah tidak pernah masuk repositori, kolom pribadi (waktu isi, tanggal lahir, nama sekolah, nama teman) dibuang segera setelah usia dihitung, dan aplikasi hanya memuat ringkasan agregat.

### Persiapan data

- **Kaggle**: tanpa nilai hilang, tanpa baris duplikat, tanpa nilai mustahil; `gender` dikodekan tetap (`Female=0, Male=1, Other=2`, sama dengan LabelEncoder di notebook). Alur: berkas lengkap 1 juta baris → hanya baris dalam rentang usia pelajar 14-25 (berkas mencakup 17-29, sehingga tersisa usia 17-25) → pembagian latih/uji 80/20, distratifikasi per usia (`random_state=42`). Model dilatih dengan seluruh 554.036 baris latih dan diuji pada seluruh 138.509 baris uji. 20.000 baris uji (`dataset.csv`) menjadi populasi referensi aplikasi, sehingga grafik dan persentil tidak pernah memakai baris latih.
- **Google Form → 11 fitur model** (`spk/gform.py`): jawaban teks diubah ke angka, lalu diskalakan ke rentang fitur Kaggle. Setiap butir dipetakan dulu ke 0-1 (tingkat 1 → 0, tingkat teratas → 1):
  - jam belajar & jam tidur: teks rentang ("1 jam 30 menit") → jam;
  - tekanan ujian: rata-rata "tertekan karena ujian" dan "nilai di bawah target" → 1-10;
  - tingkat stres: rata-rata tugas bersamaan, waktu tidak cukup, tugas terlambat, belajar larut malam × 10 (tugas terlambat dan belajar larut malam punya 5 tingkat, sampai "> 5");
  - tekanan finansial: kebalikan dari "uang saku cukup" × 10;
  - ekspektasi keluarga: rata-rata takut mengecewakan orang tua dan tuntutan keluarga × 10 ("mampu membicarakan kesulitan dengan keluarga" dikeluarkan karena pada data riil menurunkan reliabilitas skor);
  - burnout: rata-rata 3 butirnya × 10;
  - **target** skor kecemasan: rata-rata 7 butir *Psikologis* (butir konsentrasi dibalik) × 10, 0-10.
  Butir pembentuk target **tidak pernah** dipakai sebagai fitur (mencegah *label leakage*).
- **Dua versi formulir dalam satu ekspor**: formulir direvisi, dan baris yang diisi sebelum revisi tidak punya pertanyaan tambahan. Setiap skor merata-ratakan butir yang dimiliki baris tersebut, sehingga baris lama tetap memakai rumus lama (mis. kecemasan = 5 butir) dan baris baru memakai semua butir. Laporan kualitas memeriksa penggabungan ini: *Cronbach's alpha* per skor, serta pada baris baru korelasi dan selisih rata-rata antara versi butir lama dan versi semua butir.

### Pemodelan (Data Mining)

**Random Forest Regressor** (300 pohon, kedalaman maksimum 12, `min_samples_leaf=50`, `max_features=0.75`, `max_samples=0.6`) memprediksi `anxiety_score`. Pengaturan ini adalah yang terbaik dari 25 pengaturan pada *random search* dengan *cross-validation* 5-fold pada 50.000 baris latih; pengaturan notebook (kedalaman 10, `max_features="sqrt"`) tetap dipakai untuk data kuesioner yang kecil. Dengan data riil, tujuh strategi dibandingkan lewat *repeated 5-fold cross-validation*: model Kaggle apa adanya, RF hanya data riil, gabungan Kaggle + riil dengan bobot 1/10/50, dan *warm start* (menambah 200/600 pohon yang dilatih pada data riil). Strategi dengan MAE terendah dipakai.

### Keputusan (SPK - SMART)

1. Delapan kriteria: prediksi kecemasan RF, jam belajar, nilai rapor, jam tidur, aktivitas fisik, tekanan finansial, ekspektasi keluarga, burnout.
2. Utilitas: *benefit* `u = (x - min)/(max - min)`, *cost* `u = (max - x)/(max - min)`; di sini "benefit" berarti **makin tinggi makin membutuhkan perhatian**. Batas min/max diambil dari populasi referensi agar satu siswa pun dapat dinilai.
3. **Skor prioritas** = rata-rata utilitas (bobot sama) → peringkat siswa.
4. **Skor alternatif** = Σ bobot × utilitas, dengan bobot khusus tiap alternatif → alternatif dengan skor tertinggi direkomendasikan.

### Evaluasi

MAE, RMSE, R² pada data uji; perbandingan dengan regresi linear, pohon keputusan, gradient boosting, dan baseline rata-rata; uji sensitivitas bobot ±10%/±20% per siswa dan populasi; stabilitas 100 iterasi acak; pemeriksaan keadilan per gender; evaluasi pada respons baru lewat unggahan berkas.
