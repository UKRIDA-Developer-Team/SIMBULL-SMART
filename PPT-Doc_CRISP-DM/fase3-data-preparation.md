# Fase 3 — Data Preparation

**Proyek:** Sistem Rekomendasi Penanganan Kecemasan Siswa SMA Menggunakan Metode SMART
**Metodologi:** CRISP-DM — Fase 3 dari 6

---

## 1. Tujuan Fase

Menghasilkan dataset final yang siap dimasukkan ke modul pemodelan. Fase ini umumnya menyerap porsi waktu terbesar dalam proyek data mining, dan kualitas keluarannya menentukan kualitas model pada Fase 4.

Enam langkah yang dijalankan:

| # | Langkah | Keluaran |
|---|---|---|
| 1 | Seleksi data | Daftar atribut yang dipakai dan yang dibuang beserta alasannya |
| 2 | Pembersihan data | Dataset bebas duplikat, missing tertangani, outlier terputuskan |
| 3 | Encoding dan pembalikan skala | Seluruh atribut dalam bentuk numerik yang searah |
| 4 | Konstruksi fitur | Indeks per domain, label kecemasan, fitur turunan |
| 5 | Normalisasi dan seleksi fitur | Skala seragam, atribut redundan dibuang |
| 6 | Pembagian dan penyeimbangan data | Data latih/uji dan matriks keputusan SMART |

---

## 2. Langkah 1 — Seleksi Data

### 2.1 Atribut yang Dibuang

| Atribut | Alasan |
|---|---|
| `nama_sekolah` | Kardinalitas tinggi, berisiko mengidentifikasi responden, tidak relevan sebagai prediktor |
| `sumber_informasi`, `nama_teman_pemberi_informasi` | Data administratif penyebaran kuesioner; berisi nama orang lain |
| `tanggal_lahir` | Diganti oleh atribut turunan `usia`; tanggal penuh adalah data pengenal |
| `timestamp` pengisian | Dipakai hanya untuk deteksi duplikat dan pengisian terlalu cepat, lalu dibuang |
| Butir dengan variasi jawaban < 5% | Tidak informatif bagi model |

### 2.2 Atribut yang Dipertahankan

Seluruh atribut domain F1–F8, indikator hasil (H01, H02), demografi `jenis_kelamin` dan `usia`, serta P01–P05 yang **dipisahkan ke tabel terpisah** sebagai bahan pembentuk label.

### 2.3 Pemisahan Anti-*Leakage*

Dataset dipecah menjadi dua berkas sejak awal:

```
dataset_fitur.csv   → D01, usia, F1.*, F2.*, ..., F8.*, H01, H02
dataset_label.csv   → P01 ... P05  → level_kecemasan
```

Penggabungan hanya dilakukan lewat `id_responden` anonim saat pelatihan model, dan P01–P05 tidak pernah ikut sebagai kolom prediktor.

---

## 3. Langkah 2 — Pembersihan Data

### 3.1 Duplikat

Duplikat dideteksi dari kombinasi `timestamp` + `jenis_kelamin` + `tanggal_lahir` + `nama_sekolah` sebelum kolom tersebut dibuang. Baris ganda dari submit berulang disisakan satu (entri terakhir).

### 3.2 Penanganan Missing Value

| Jenis atribut | Strategi | Alasan |
|---|---|---|
| Ordinal Likert (missing < 5%) | Imputasi **modus** per butir | Menjaga bentuk distribusi ordinal |
| Numerik (`durasi_tidur`, `nilai_rapor`, `menit_olahraga`) | Imputasi **median**, dikelompokkan per jenis kelamin dan tingkat kelas bila memungkinkan | Median tahan terhadap outlier; imputasi bersyarat cocok untuk pola MAR |
| `jam_kegiatan_per_minggu` kosong saat `jumlah_ekskul = 0` | Diisi **0** (bukan imputasi statistik) | Kosong di sini berarti "tidak ada kegiatan", bukan data hilang |
| `nilai_rapor` kosong (dugaan MNAR) | Diimputasi median **dan** ditambahkan kolom penanda `nilai_rapor_tidak_diisi` (0/1) | Ketidaklengkapan itu sendiri berpotensi informatif |
| Kolom dengan missing > 30% | Dibuang | Imputasi terlalu banyak menciptakan data buatan |

### 3.3 Outlier dan Nilai Tidak Wajar

| Pemeriksaan | Aturan | Tindakan |
|---|---|---|
| `nilai_rapor` di luar 0–100 | Batas logis | Dikoreksi bila jelas salah ketik (mis. 850 → 85), selain itu dibuang |
| `menit_olahraga_per_sesi` > 240 | Aturan IQR + batas logis | Ditinjau; nilai ekstrem dari atlet sekolah dipertahankan dan ditandai |
| `jam_belajar` + `durasi_tidur` + jam sekolah > 24 jam | Konsistensi antar-atribut | Baris ditandai tidak konsisten dan dikeluarkan |
| Outlier numerik lain | [Q1 − 1,5×IQR, Q3 + 1,5×IQR] | Tidak otomatis dihapus — diperiksa dulu apakah wajar secara domain |

Prinsipnya: outlier yang **wajar secara domain** dipertahankan, outlier yang merupakan **kesalahan input** dikoreksi atau dibuang.

### 3.4 Validitas Respons

| Pemeriksaan | Ambang | Tindakan |
|---|---|---|
| *Straight-lining* | Seluruh butir Likert dijawab nilai yang sama pada ≥ 3 domain | Baris dibuang |
| Durasi pengisian | Jauh di bawah waktu minimum wajar | Baris dibuang |
| Inkonsistensi butir berlawanan arah | Jawaban ekstrem yang saling bertentangan | Ditandai untuk ditinjau manual |

### 3.5 Konsistensi Format

Standardisasi teks (kapitalisasi awal), penyeragaman format tanggal, dan penyeragaman penamaan kategori sebelum encoding.

---

## 4. Langkah 3 — Encoding dan Pembalikan Skala

### 4.1 Pengkodean Skala Likert

| Label respons | Kode |
|---|---|
| Tidak pernah / Sangat tidak setuju | 0 |
| Jarang / Tidak setuju | 1 |
| Kadang-kadang / Netral | 2 |
| Sering / Setuju | 3 |
| Sangat sering / Sangat setuju | 4 |

Butir dengan empat opsi (F1.2–F1.4) dikodekan 0–3 lalu diskalakan ke 0–4 agar setara antar butir.

### 4.2 Pembalikan Arah (*Reverse Coding*)

Butir yang arah maknanya positif dibalik agar seluruh butir searah — nilai lebih besar berarti kondisi lebih berisiko:

```
nilai_baru = 4 - nilai_lama
```

Diterapkan pada: `merasa_diterima_teman`, `punya_teman_dipercaya`, `dukungan_teman`, `kegiatan_beri_percaya_diri`, `konsentrasi_saat_pelajaran` (P03), `uang_saku_cukup`, `aktivitas_fisik_ringan`, `olahraga_untuk_stres`, `hari_olahraga_per_minggu`.

Tanpa langkah ini, penjumlahan skor domain akan saling meniadakan dan indeks menjadi tidak bermakna.

### 4.3 Konversi Rentang Menjadi Angka

Kategori rentang diubah ke titik tengahnya agar bisa diperlakukan sebagai numerik:

| Atribut | Kategori | Nilai numerik |
|---|---|---|
| `durasi_medsos_harian` | < 1 jam / 1–2 / 2–3 / 3–4 / > 4 jam | 0,5 / 1,5 / 2,5 / 3,5 / 4,5 |
| `persentase_kehadiran` | < 80 / 80–84 / 85–89 / 90–94 / 95–100 | 78 / 82 / 87 / 92 / 97,5 |
| `hari_olahraga_per_minggu` | 0 / 1–2 / 3–4 / 5–6 / 7 | 0 / 1,5 / 3,5 / 5,5 / 7 |
| `jam_mulai_tidur` | < 21.00 → ≥ 00.00 | 20,5 / 21,5 / 22,5 / 23,5 / 24,5 |

### 4.4 Atribut Nominal

`jenis_kelamin` dikodekan biner. Tidak ada atribut nominal berkategori banyak yang tersisa setelah seleksi, sehingga *one-hot encoding* hampir tidak diperlukan — ini menghindari ledakan dimensi pada dataset yang jumlah barisnya terbatas.

---

## 5. Langkah 4 — Konstruksi Fitur

### 5.1 Indeks Skor per Domain

Setiap domain diringkas menjadi satu indeks 0–100 agar mudah ditafsirkan dan mengurangi dimensi:

```
indeks_domain = (jumlah skor butir domain / skor maksimum domain) × 100
```

| Fitur | Dibentuk dari |
|---|---|
| `indeks_tekanan_akademik` | F1.2 – F1.6 |
| `indeks_defisit_tidur` | F2.1 (dibalik), F2.2, F2.3, F2.4 |
| `indeks_beban_digital` | F3.1, F3.2, F3.3 |
| `indeks_tekanan_keluarga` | F4.1, F4.2 |
| `indeks_dukungan_sosial_rendah` | F5.1–F5.5 (setelah reverse coding) |
| `indeks_aktivitas_fisik_rendah` | F6.1–F6.4 (setelah reverse coding) |
| `indeks_beban_kegiatan` | F7.4, F7.5, F7.6, F7.7 |
| `indeks_koping_konsumtif` | F8.3, F8.4, F8.5, F8.6, F8.7 |

Delapan indeks inilah yang menjadi masukan utama clustering dan penentu faktor dominan untuk SMART.

### 5.2 Fitur Turunan Tambahan

| Fitur | Rumus | Alasan |
|---|---|---|
| `usia` | Tahun pengisian − tahun lahir | Menggantikan tanggal lahir |
| `rasio_belajar_tidur` | `jam_belajar_harian` / `durasi_tidur` | Menangkap ketidakseimbangan waktu |
| `beban_total_mingguan` | `jam_belajar_harian` × 7 + `jam_kegiatan_per_minggu` | Beban waktu total di luar jam sekolah |
| `medsos_malam_x_tidur_pendek` | `medsos_sebelum_tidur` × (1 jika `durasi_tidur` < 7) | Interaksi antara F3 dan F2 |
| `nilai_rapor_tidak_diisi` | Penanda 0/1 | Menyimpan informasi pola MNAR |

### 5.3 Pembentukan Label Tingkat Kecemasan

```
skor_kecemasan = P01 + P02 + P03_reversed + P04 + P05        (rentang 0 – 20)
```

| Level | Rentang skor | Interpretasi kerja |
|---|---|---|
| Rendah | 0 – 6 | Indikasi minimal |
| Sedang | 7 – 12 | Indikasi perlu perhatian |
| Tinggi | 13 – 20 | Indikasi kuat, prioritas tindak lanjut |

Batas ini adalah **ambang kerja**, bukan ambang klinis. Ambang final ditetapkan setelah melihat distribusi skor yang sebenarnya (mempertimbangkan pembagian tersil) dan ditinjau bersama guru BK. Setiap penyesuaian ambang wajib didokumentasikan.

---

## 6. Langkah 5 — Normalisasi dan Seleksi Fitur

### 6.1 Normalisasi

Min-Max ke rentang 0–1 diterapkan pada seluruh fitur numerik:

```
x' = (x − x_min) / (x_max − x_min)
```

Alasan: K-Means dan k-NN bekerja berbasis jarak, sehingga atribut berskala besar (`nilai_rapor` 0–100) akan mendominasi atribut berskala kecil bila tidak diseragamkan. Parameter `x_min` dan `x_max` **dihitung hanya dari data latih**, lalu diterapkan ke data uji — bukan dihitung ulang dari seluruh data.

Decision Tree dan Random Forest tidak memerlukan normalisasi, tetapi dataset yang sama tetap dipakai agar perbandingan antar model adil.

### 6.2 Seleksi Fitur

| Metode | Fungsi |
|---|---|
| Matriks korelasi antar-indeks | Membuang salah satu dari pasangan dengan |r| > 0,8 |
| Information Gain / Chi-Square | Memeringkat relevansi fitur terhadap label |
| *Feature importance* Random Forest | Konfirmasi silang peringkat relevansi |

Hasil peringkat ini punya dua kegunaan: menyaring fitur untuk model, dan menjadi dasar empiris penentuan bobot kriteria SMART pada Fase 4.

---

## 7. Langkah 6 — Pembagian dan Penyeimbangan Data

| Aspek | Keputusan |
|---|---|
| Rasio pembagian | 80% latih, 20% uji, **stratified** berdasarkan `level_kecemasan` |
| Validasi | *Stratified 5-fold cross validation* pada data latih |
| Ketidakseimbangan kelas | SMOTE atau *random oversampling* **hanya di dalam lipatan latih** |
| *Random state* | Ditetapkan tetap agar hasil dapat direproduksi |

Menerapkan SMOTE sebelum pembagian data adalah kesalahan umum: data sintetis akan bocor ke data uji dan membuat metrik terlihat jauh lebih baik daripada kenyataannya.

---

## 8. Penyiapan Data untuk Modul SMART

Selain dataset pemodelan, fase ini juga menyiapkan **matriks keputusan** SMART berukuran 10 alternatif × 7 kriteria:

| Sumber nilai | Kriteria yang diisi |
|---|---|
| Keluaran data mining | C1 (kesesuaian faktor dominan), C2 (kesesuaian tingkat urgensi) |
| Penilaian guru BK / literatur | C3 (efektivitas), C7 (aksesibilitas dan penerimaan) |
| Data profil sekolah | C4 (ketersediaan sumber daya), C5 (biaya) |
| Estimasi program | C6 (waktu dan beban bagi siswa) |

Seluruh nilai dinyatakan pada skala 1–5 agar dapat dinormalisasi seragam pada Fase 4.

---

## 9. Keluaran Fase

| Berkas | Isi |
|---|---|
| `dataset_bersih.csv` | Data setelah pembersihan, sebelum rekayasa fitur |
| `dataset_model.csv` | Fitur final (8 indeks + fitur turunan + demografi) dan label |
| `scaler.pkl`, `imputer.pkl` | Objek transformasi yang dipakai ulang saat deployment |
| `matriks_keputusan_smart.csv` | Nilai 10 alternatif × 7 kriteria |
| `log_preparation.md` | Catatan setiap keputusan pembersihan dan jumlah baris yang terpengaruh |

Berkas `scaler.pkl` dan `imputer.pkl` bersifat kritis: aplikasi Gradio pada Fase 6 harus memakai objek transformasi yang **sama persis** dengan yang dipakai saat pelatihan, bukan menghitung ulang dari data baru.
