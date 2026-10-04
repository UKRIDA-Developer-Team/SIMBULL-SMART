# Fase 4 — Modeling

**Proyek:** Sistem Rekomendasi Penanganan Kecemasan Siswa SMA Menggunakan Metode SMART
**Metodologi:** CRISP-DM — Fase 4 dari 6

---

## 1. Tujuan Fase

Menerapkan teknik data mining pada dataset hasil Fase 3, lalu menyambungkan keluarannya ke modul pengambilan keputusan SMART. Fase ini terdiri atas empat modul pemodelan dan satu modul keputusan.

| Modul | Teknik | Keluaran |
|---|---|---|
| M1 — Segmentasi | K-Means (pembanding: K-Medoids, Agglomerative) | Profil cluster siswa |
| M2 — Klasifikasi | Naïve Bayes, Decision Tree (C4.5), Random Forest, k-NN | Model prediksi level kecemasan |
| M3 — Pola asosiatif | FP-Growth / Apriori | Aturan kombinasi kebiasaan |
| M4 — Kepentingan fitur | Information Gain, *Gini importance* | Peringkat faktor → bobot kriteria |
| M5 — Keputusan | SMART | Peringkat alternatif penanganan |

---

## 2. Modul M1 — Segmentasi Siswa (Clustering)

### 2.1 Rancangan

| Aspek | Keputusan |
|---|---|
| Algoritma utama | K-Means (cepat, mudah ditafsirkan, cocok untuk fitur numerik hasil normalisasi) |
| Pembanding | K-Medoids (lebih tahan outlier), Agglomerative Hierarchical (untuk memeriksa struktur alami) |
| Fitur masukan | 8 indeks domain hasil Fase 3, seluruhnya berskala 0–1 |
| Penentuan *k* | Elbow Method (WCSS) dan Silhouette Score untuk *k* = 2 sampai 6 |
| Inisialisasi | `k-means++`, `n_init = 20`, `random_state` tetap |
| Validasi | Silhouette Score, Davies-Bouldin Index, dan kebermaknaan profil menurut guru BK |

### 2.2 Cara Membaca Hasil

Setiap cluster dideskripsikan dengan rata-rata kedelapan indeksnya, lalu diberi nama kerja yang menggambarkan karakter dominannya — misalnya *segmen beban akademik tinggi*, *segmen defisit tidur dan digital*, *segmen tekanan ekspektasi keluarga*, dan *segmen relatif stabil*.

Sebuah cluster dianggap layak dipakai bila memenuhi tiga syarat: Silhouette ≥ 0,50, memiliki setidaknya satu indeks yang jelas menonjol dibanding cluster lain, dan dapat dikenali oleh guru BK sebagai tipe siswa yang nyata. Cluster dengan anggota sangat sedikit digabung atau dilaporkan sebagai kasus khusus.

### 2.3 Peran Hasil bagi SPK

Nama cluster menjadi konteks penyesuaian bobot: pada segmen *defisit tidur dan digital*, bobot kriteria kesesuaian faktor dominan (C1) mengarahkan skor tertinggi ke alternatif A4 dan A6; pada segmen *tekanan keluarga*, ke A8.

---

## 3. Modul M2 — Klasifikasi Tingkat Indikasi

### 3.1 Kandidat Algoritma

| Algoritma | Alasan dicoba | Catatan |
|---|---|---|
| **Naïve Bayes** | Ringan, bekerja baik pada data kecil | Asumsi independensi antar-fitur tidak sepenuhnya terpenuhi |
| **Decision Tree (C4.5/CART)** | Aturannya dapat dibaca langsung — cocok untuk domain yang menuntut penjelasan | Rawan *overfitting*; kedalaman dibatasi |
| **Random Forest** | Biasanya paling akurat pada data tabular; menyediakan *feature importance* | Kurang transparan; dijelaskan lewat kepentingan fitur |
| **k-NN** | Pembanding sederhana berbasis kemiripan | Sensitif terhadap skala dan jumlah data |

### 3.2 Skema Pengujian

| Aspek | Nilai |
|---|---|
| Pembagian data | 80/20 stratified (sudah disiapkan di Fase 3) |
| Validasi silang | Stratified 5-fold pada data latih |
| Penyetelan parameter | *Grid search* terbatas: kedalaman pohon, jumlah estimator, nilai *k*, kriteria split |
| Penanganan kelas timpang | SMOTE di dalam lipatan latih; `class_weight='balanced'` sebagai pembanding |
| Metrik pemilihan model | **Recall kelas "Tinggi"** sebagai metrik utama, F1-score makro sebagai metrik pendamping |

### 3.3 Alasan Recall Diutamakan

Kesalahan melewatkan siswa yang benar-benar berisiko (*false negative*) jauh lebih merugikan daripada menandai siswa yang sebenarnya baik-baik saja (*false positive*). Biaya *false positive* hanyalah satu sesi konseling tambahan; biaya *false negative* adalah siswa yang membutuhkan bantuan tidak terjangkau sama sekali. Karena itu model dengan akurasi lebih rendah tetapi recall kelas "Tinggi" lebih baik akan dipilih.

Bila diperlukan, ambang probabilitas digeser dari 0,5 ke nilai yang lebih rendah untuk kelas "Tinggi" guna menaikkan recall — dengan konsekuensi presisi menurun, yang dilaporkan secara terbuka.

### 3.4 Format Pelaporan Hasil

| Model | Akurasi | Precision (Tinggi) | Recall (Tinggi) | F1 makro | Catatan |
|---|---|---|---|---|---|
| Naïve Bayes | … | … | … | … | |
| Decision Tree | … | … | … | … | |
| Random Forest | … | … | … | … | |
| k-NN | … | … | … | … | |

Tabel diisi dengan hasil eksperimen yang sebenarnya, disertai *confusion matrix* tiap model.

---

## 4. Modul M3 — Aturan Asosiasi

| Aspek | Keputusan |
|---|---|
| Algoritma | FP-Growth (lebih efisien dari Apriori pada jumlah item sedang) |
| Persiapan data | Indeks domain didiskretisasi menjadi Rendah / Sedang / Tinggi, lalu diubah ke bentuk transaksi |
| Ambang | Support ≥ 10%, Confidence ≥ 70%, Lift > 1 |
| Fokus | Aturan yang bagian konsekuennya adalah `level_kecemasan = Tinggi` |

Bentuk aturan yang dicari, misalnya: *defisit tidur tinggi* ∧ *beban digital tinggi* ∧ *tekanan akademik tinggi* → *indikasi kecemasan tinggi*. Aturan semacam ini berguna sebagai kalimat penjelas pada keluaran SPK, karena lebih mudah dipahami guru BK daripada bobot model.

Aturan dengan lift mendekati 1 dibuang meskipun confidence-nya tinggi, karena itu hanya mencerminkan kelas mayoritas.

---

## 5. Modul M4 — Kepentingan Fitur dan Penentuan Bobot

### 5.1 Sumber Peringkat

Tiga metode dipakai bersama, dan hanya faktor yang konsisten muncul di peringkat atas pada ketiganya yang dipakai:

1. *Information Gain* terhadap label.
2. *Gini importance* dari Random Forest.
3. Korelasi Spearman antara indeks domain dan skor kecemasan.

### 5.2 Konversi ke Bobot Kriteria SMART

Bobot mentah ditetapkan pada skala 0–100 dengan kriteria terpenting diberi nilai 100, lalu dinormalisasi sehingga totalnya 1:

| Kode | Kriteria | Sifat | Bobot mentah | Bobot ternormalisasi |
|---|---|---|---|---|
| C1 | Kesesuaian dengan faktor dominan siswa | Benefit | 100 | **0,25** |
| C2 | Kesesuaian dengan tingkat urgensi | Benefit | 80 | **0,20** |
| C3 | Efektivitas menurut pakar dan literatur | Benefit | 60 | **0,15** |
| C4 | Ketersediaan sumber daya sekolah | Benefit | 48 | **0,12** |
| C5 | Biaya implementasi | Cost | 40 | **0,10** |
| C6 | Waktu dan beban tambahan bagi siswa | Cost | 32 | **0,08** |
| C7 | Aksesibilitas dan penerimaan siswa | Benefit | 40 | **0,10** |
| | **Total** | | **400** | **1,00** |

Nilai C1 tiap alternatif diturunkan dari kecocokannya dengan tiga faktor dominan siswa hasil M4; nilai C2 diturunkan dari level indikasi hasil M2. Dua kriteria inilah yang membuat peringkat berbeda antar siswa, sedangkan C3–C7 relatif tetap untuk satu sekolah.

---

## 6. Modul M5 — Perhitungan SMART

### 6.1 Langkah Baku

1. Menentukan kriteria (C1–C7) dan alternatif (A1–A10).
2. Menetapkan bobot mentah dan menormalisasinya sehingga Σw = 1.
3. Menyusun matriks keputusan berisi nilai tiap alternatif pada tiap kriteria (skala 1–5).
4. Menghitung nilai utilitas:
   - Kriteria **benefit**: `u = (Cᵢ − Cₘᵢₙ) / (Cₘₐₓ − Cₘᵢₙ)`
   - Kriteria **cost**: `u = (Cₘₐₓ − Cᵢ) / (Cₘₐₓ − Cₘᵢₙ)`
   Dengan skala 1–5, keduanya menjadi `u = (x − 1)/4` dan `u = (5 − x)/4`.
5. Menghitung skor akhir: `U(aᵢ) = Σⱼ wⱼ · uᵢⱼ`
6. Mengurutkan alternatif dari skor tertinggi.

### 6.2 Contoh Perhitungan

**Profil siswa uji coba:** level indikasi **Tinggi**; segmen *defisit tidur dan digital*; tiga faktor dominan: F2 (pola tidur), F3 (media sosial), F1 (beban akademik).

**Matriks keputusan** (nilai 1–5, lima alternatif teratas ditampilkan):

| Alternatif | C1 | C2 | C3 | C4 | C5 (cost) | C6 (cost) | C7 |
|---|---|---|---|---|---|---|---|
| A4 — Program higiene tidur | 5 | 4 | 4 | 5 | 1 | 2 | 5 |
| A6 — Digital wellbeing | 5 | 3 | 3 | 5 | 1 | 2 | 5 |
| A3 — Manajemen waktu & strategi belajar | 4 | 4 | 4 | 4 | 2 | 3 | 4 |
| A1 — Konseling individual BK | 3 | 5 | 5 | 3 | 3 | 4 | 3 |
| A10 — Rujukan tenaga profesional | 2 | 5 | 5 | 2 | 5 | 5 | 2 |

**Nilai utilitas** setelah normalisasi:

| Alternatif | C1 | C2 | C3 | C4 | C5 | C6 | C7 |
|---|---|---|---|---|---|---|---|
| A4 | 1,00 | 0,75 | 0,75 | 1,00 | 1,00 | 0,75 | 1,00 |
| A6 | 1,00 | 0,50 | 0,50 | 1,00 | 1,00 | 0,75 | 1,00 |
| A3 | 0,75 | 0,75 | 0,75 | 0,75 | 0,75 | 0,50 | 0,75 |
| A1 | 0,50 | 1,00 | 1,00 | 0,50 | 0,50 | 0,25 | 0,50 |
| A10 | 0,25 | 1,00 | 1,00 | 0,25 | 0,00 | 0,00 | 0,25 |

**Skor akhir** dengan bobot (0,25 / 0,20 / 0,15 / 0,12 / 0,10 / 0,08 / 0,10):

| Peringkat | Alternatif | Skor akhir |
|---|---|---|
| 1 | **A4 — Program higiene tidur** | **0,893** |
| 2 | A6 — Digital wellbeing | 0,805 |
| 3 | A3 — Manajemen waktu & strategi belajar | 0,730 |
| 4 | A1 — Konseling individual BK | 0,655 |
| 5 | A10 — Rujukan tenaga profesional | 0,468 |

Contoh rincian A4:
```
U(A4) = 0,25(1,00) + 0,20(0,75) + 0,15(0,75) + 0,12(1,00)
      + 0,10(1,00) + 0,08(0,75) + 0,10(1,00)
      = 0,250 + 0,150 + 0,1125 + 0,120 + 0,100 + 0,060 + 0,100
      = 0,893
```

### 6.3 Cara Membaca Hasil

Peringkat teratas mengarah ke A4 dan A6 karena keduanya paling sesuai dengan faktor dominan siswa (C1 tinggi) sekaligus murah dan mudah dijalankan sekolah. A10 berada di peringkat bawah bukan karena tidak efektif — nilai C3-nya justru tertinggi — melainkan karena biayanya besar dan relevansinya terhadap faktor dominan siswa ini rendah.

Untuk siswa dengan skor kecemasan sangat tinggi disertai gangguan fungsi sehari-hari, sistem menerapkan **aturan pengaman**: A1 dan A10 selalu dimunculkan sebagai rekomendasi pendamping berapa pun skor SMART-nya. Perhitungan multikriteria tidak boleh menutup jalur rujukan profesional.

### 6.4 Aturan Penyajian Rekomendasi

- Sistem menampilkan **tiga alternatif teratas**, bukan hanya satu, agar guru BK tetap memiliki ruang memilih.
- Setiap rekomendasi disertai alasan berbasis faktor dominan dan aturan asosiasi yang relevan.
- Skor SMART ditampilkan apa adanya agar dapat ditelusuri.

---

## 7. Keluaran Fase

| Berkas | Isi |
|---|---|
| `model_klasifikasi.pkl` | Model terpilih beserta parameternya |
| `model_cluster.pkl` | Model K-Means dan pusat cluster |
| `profil_cluster.csv` | Rata-rata indeks per cluster dan nama segmen |
| `aturan_asosiasi.csv` | Daftar aturan dengan support, confidence, lift |
| `bobot_kriteria.json` | Bobot C1–C7 hasil turunan kepentingan fitur |
| `smart_engine.py` | Implementasi perhitungan SMART |
| `laporan_modeling.md` | Perbandingan model, parameter, dan alasan pemilihan |

Seluruh keluaran ini diuji ulang terhadap tujuan bisnis pada Fase 5 — Evaluation.
