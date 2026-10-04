# Fase 2 — Data Understanding

**Proyek:** Sistem Rekomendasi Penanganan Kecemasan Siswa SMA Menggunakan Metode *Simple Multi-Attribute Rating Technique* (SMART)
**Metodologi:** CRISP-DM — Fase 2 dari 6

---

## 1. Tujuan Fase

Fase ini bertujuan mengumpulkan data awal dan mengenali karakteristiknya sebelum masuk ke tahap persiapan. Empat aktivitas baku CRISP-DM dijalankan:

| Aktivitas | Sasaran pada proyek ini |
|---|---|
| *Collect Initial Data* | Menghimpun respons kuesioner siswa SMA melalui Google Form |
| *Describe Data* | Menyusun kamus data: jumlah baris/kolom, tipe, skala, dan rentang tiap atribut |
| *Explore Data* | Statistik deskriptif, distribusi, dan korelasi antaratribut untuk menemukan pola awal |
| *Verify Data Quality* | Menilai completeness, consistency, accuracy, serta pola missing data |

**Keluaran fase:** laporan deskripsi data, kamus data, laporan eksplorasi (EDA), dan laporan kualitas data yang menjadi masukan langsung bagi Fase 3.

---

## 2. Pengumpulan Data Awal

| Aspek | Keterangan |
|---|---|
| Sumber | Kuesioner daring (Google Form) yang disebarkan melalui sekolah, media sosial, dan jaringan pertemanan |
| Unit observasi | Satu baris = satu siswa SMA responden |
| Target volume | Minimal 200 responden valid (memadai untuk clustering dan klasifikasi tiga kelas) |
| Periode | Satu gelombang pengumpulan; tanggal pengisian tercatat otomatis (timestamp) |
| Jumlah atribut mentah | ± 45 kolom, terbagi ke dalam 8 domain faktor + 1 domain indikator psikologis + identitas |
| Format | Ekspor CSV/XLSX dari Google Form |
| Persetujuan | Pengantar kuesioner memuat penjelasan tujuan, jaminan anonimitas, dan izin sekolah/orang tua |

Kolom `Sumber Informasi Kuesioner` dan `Nama teman pemberi informasi` bersifat administratif (pelacakan penyebaran), bukan variabel analisis.

---

## 3. Deskripsi Data (Kamus Data)

Atribut dikelompokkan menurut domain agar mudah dirujuk pada fase berikutnya. Kode variabel di bawah ini dipakai konsisten sampai fase Deployment.

### 3.1 Identitas dan Demografi

| Kode | Atribut | Tipe Data | Skala / Rentang |
|---|---|---|---|
| D01 | jenis_kelamin | Kategorikal (nominal) | Laki-laki / Perempuan |
| D02 | tanggal_lahir | Datetime | dd-mm-yyyy → diturunkan menjadi `usia` |
| D03 | nama_sekolah | Teks | Bebas (nominal, kardinalitas tinggi) |
| D04 | sumber_informasi | Kategorikal (nominal) | 4 kategori (administratif) |

### 3.2 F1 — Beban dan Tekanan Akademik

| Kode | Atribut | Tipe Data | Skala |
|---|---|---|---|
| F1.1 | jam_belajar_harian | Numerik (kontinu, dari ordinal) | < 0,5 – 11,5 jam |
| F1.2 | frek_belajar_larut_malam | Kategorikal (ordinal) | 1–4 (tidak pernah → 4–5 kali) |
| F1.3 | waktu_belajar_tidak_cukup | Kategorikal (ordinal) | 1–4 (tidak pernah → sering) |
| F1.4 | jumlah_tugas_terlambat | Kategorikal (ordinal) | 1–4 (tidak pernah → 4–5) |
| F1.5 | beban_tugas_bersamaan | Kategorikal (ordinal) | 1–5 (tidak pernah → sangat sering) |
| F1.6 | tertekan_ujian_nilai | Kategorikal (ordinal) | 1–5 |

### 3.3 F2 — Pola Tidur

| Kode | Atribut | Tipe Data | Skala |
|---|---|---|---|
| F2.1 | durasi_tidur | Numerik (kontinu) | 4 – 12 jam |
| F2.2 | jam_mulai_tidur | Kategorikal (ordinal) | 5 kategori (< 21.00 → ≥ 00.00) |
| F2.3 | frek_kurang_tidur | Kategorikal (ordinal) | 1–5 |
| F2.4 | frek_mengantuk_di_kelas | Kategorikal (ordinal) | 1–5 |

### 3.4 F3 — Penggunaan Media Sosial

| Kode | Atribut | Tipe Data | Skala |
|---|---|---|---|
| F3.1 | durasi_medsos_harian | Kategorikal (ordinal) | 5 kategori (< 1 jam → > 4 jam) |
| F3.2 | medsos_saat_belajar | Kategorikal (ordinal) | 1–5 |
| F3.3 | medsos_sebelum_tidur | Kategorikal (ordinal) | 1–5 |

### 3.5 F4 — Tekanan Keluarga dan Ekspektasi

| Kode | Atribut | Tipe Data | Skala |
|---|---|---|---|
| F4.1 | takut_kecewakan_ortu | Kategorikal (ordinal) | 1–5 |
| F4.2 | tuntutan_nilai_keluarga | Kategorikal (ordinal) | 1–5 |

### 3.6 F5 — Lingkungan Pertemanan

| Kode | Atribut | Tipe Data | Skala | Arah |
|---|---|---|---|---|
| F5.1 | merasa_diterima_teman | Ordinal | 1–5 | Positif (perlu *reverse coding*) |
| F5.2 | punya_teman_dipercaya | Ordinal | 1–5 | Positif |
| F5.3 | dukungan_teman | Ordinal | 1–5 | Positif |
| F5.4 | tekanan_konformitas | Ordinal | 1–5 | Negatif |
| F5.5 | konflik_ganggu_konsentrasi | Ordinal | 1–5 | Negatif |

### 3.7 F6 — Aktivitas Fisik

| Kode | Atribut | Tipe Data | Skala |
|---|---|---|---|
| F6.1 | hari_olahraga_per_minggu | Ordinal | 0 / 1–2 / 3–4 / 5–6 / 7 hari |
| F6.2 | menit_olahraga_per_sesi | Numerik (kontinu) | Isian bebas (menit) |
| F6.3 | aktivitas_fisik_ringan | Ordinal | 1–5 |
| F6.4 | olahraga_untuk_stres | Ordinal | 1–5 |

### 3.8 F7 — Beban Non-Akademik dan Kelelahan

| Kode | Atribut | Tipe Data | Skala | Arah |
|---|---|---|---|---|
| F7.1 | jumlah_ekskul | Numerik (diskrit) | 0–3+ | Netral |
| F7.2 | jam_kegiatan_per_minggu | Numerik (kontinu) | Isian bebas | Netral |
| F7.3 | frek_lomba_setahun | Ordinal | 4 kategori | Netral |
| F7.4 | sulit_bagi_waktu | Ordinal | 1–5 | Negatif |
| F7.5 | kelelahan_kegiatan | Ordinal | 1–5 | Negatif |
| F7.6 | kegiatan_beri_percaya_diri | Ordinal | 1–5 | Positif (*reverse*) |
| F7.7 | kehilangan_minat_belajar | Ordinal | 1–5 | Negatif |

### 3.9 F8 — Pola Makan, Jajan, dan Kafein

| Kode | Atribut | Tipe Data | Skala |
|---|---|---|---|
| F8.1 | uang_saku_cukup | Ordinal | 1–5 |
| F8.2 | beli_makanan_di_sekolah | Ordinal | 1–5 |
| F8.3 | beli_makanan_manis | Ordinal | 1–5 |
| F8.4 | beli_minuman_berkafein | Ordinal | 1–5 |
| F8.5 | makan_saat_tertekan | Ordinal | 1–5 |
| F8.6 | tenang_setelah_makan | Ordinal | 1–5 |
| F8.7 | melewatkan_waktu_makan | Ordinal | 1–5 |

### 3.10 Indikator Hasil dan Indikator Psikologis (Calon Label)

| Kode | Atribut | Tipe Data | Skala | Peran |
|---|---|---|---|---|
| H01 | nilai_rapor_terakhir | Numerik (kontinu) | 0–100 | Variabel dampak |
| H02 | persentase_kehadiran | Ordinal | 5 kategori | Variabel dampak |
| P01 | gugup_cemas_gelisah | Ordinal | 1–5 | Pembentuk label |
| P02 | sulit_kendalikan_khawatir | Ordinal | 1–5 | Pembentuk label |
| P03 | konsentrasi_saat_pelajaran | Ordinal | 1–5 | Pembentuk label (*reverse*) |
| P04 | pikiran_terganggu_masalah | Ordinal | 1–5 | Pembentuk label |
| P05 | sulit_selesaikan_tugas | Ordinal | 1–5 | Pembentuk label |

> **Catatan penting.** P01–P05 **tidak** boleh masuk ke himpunan fitur prediktor karena akan dipakai membentuk label tingkat kecemasan. Menyertakannya menyebabkan *label leakage* dan akurasi model menjadi semu.

### 3.11 Peran Atribut

| Istilah | Definisi pada proyek ini | Contoh |
|---|---|---|
| **Attribute** | Seluruh kolom hasil kuesioner apa adanya | `durasi_tidur`, `nama_sekolah` |
| **Feature** | Atribut yang dipakai sebagai input model, termasuk hasil rekayasa | `indeks_defisit_tidur`, `rasio_belajar_tidur` |
| **Target/Label** | Tingkat indikasi kecemasan (Rendah/Sedang/Tinggi) hasil skor komposit P01–P05 | `level_kecemasan` |

---

## 4. Verifikasi Kualitas Data

### 4.1 Dimensi yang Diperiksa

| Dimensi | Yang diperiksa | Risiko khas pada kuesioner ini |
|---|---|---|
| **Completeness** | Persentase sel terisi per kolom dan per baris | Isian bebas (`menit_olahraga_per_sesi`, `jam_kegiatan_per_minggu`) rawan kosong |
| **Consistency** | Keseragaman format dan penulisan | `nama_sekolah` ditulis beragam ("SMAN 1", "sman 1", "SMA Negeri 1"); format tanggal berbeda |
| **Accuracy** | Kewajaran nilai terhadap rentang logis | `nilai_rapor` > 100 atau < 40; `menit_olahraga` = 600; `jam_belajar` melebihi 24 jam bila digabung dengan tidur |
| **Validitas respons** | Kesungguhan pengisian | *Straight-lining* (semua Likert dijawab sama), durasi pengisian sangat singkat |
| **Missing data** | Pola kehilangan nilai | Perlu diklasifikasikan sebagai MCAR / MAR / MNAR |

### 4.2 Klasifikasi Pola Missing Data

| Jenis | Arti | Contoh yang mungkin terjadi | Implikasi penanganan |
|---|---|---|---|
| **MCAR** | Hilang murni acak | Kegagalan submit pada satu butir | Boleh dihapus bila proporsinya kecil |
| **MAR** | Hilang berkaitan dengan variabel lain yang tercatat | Siswa yang tidak ikut ekskul melewati pertanyaan jam kegiatan | Imputasi bersyarat (median per kelompok) |
| **MNAR** | Hilang berkaitan dengan nilai itu sendiri | Siswa dengan nilai rapor rendah enggan mengisi `nilai_rapor` | Tidak boleh diimputasi begitu saja; ditandai dengan flag `nilai_tidak_diisi` |

### 4.3 Ambang Penerimaan

- Kolom dengan missing > 30% dipertimbangkan untuk dibuang, kecuali secara teoretis krusial.
- Baris dengan missing > 20% pada atribut inti dikeluarkan dari analisis.
- Target akhir: seluruh atribut inti memiliki completeness ≥ 95% sebelum masuk Fase 3.
- Reliabilitas tiap konstruk (F1–F8, P) diuji dengan Cronbach's Alpha, target ≥ 0,70.

---

## 5. Rencana Eksplorasi Data (EDA)

### 5.1 Statistik Deskriptif

| Ukuran | Diterapkan pada | Kegunaan |
|---|---|---|
| Mean, median, modus | `durasi_tidur`, `jam_belajar_harian`, `nilai_rapor`, seluruh butir Likert | Gambaran umum kondisi responden |
| Range, standar deviasi, IQR | Atribut numerik | Melihat keragaman antar-siswa |
| Ringkasan lima angka + boxplot | `nilai_rapor`, `durasi_tidur`, `jam_kegiatan_per_minggu` | Deteksi outlier dengan aturan [Q1 − 1,5×IQR, Q3 + 1,5×IQR] |
| Frekuensi dan proporsi | Seluruh atribut kategorikal | Melihat kelas mayoritas dan kategori langka |

### 5.2 Analisis Distribusi

- **Histogram** untuk `durasi_tidur`, `jam_belajar_harian`, `nilai_rapor`, dan skor komposit kecemasan.
- Bentuk distribusi yang diantisipasi: `jam_kegiatan_per_minggu` cenderung *right-skewed* (mayoritas siswa sedikit kegiatan, sebagian kecil sangat banyak); `nilai_rapor` cenderung *left-skewed*.
- **Bar chart** untuk distribusi respons tiap butir Likert, guna mendeteksi butir dengan variasi jawaban sangat rendah (kandidat dibuang karena tidak informatif).
- **Distribusi label** `level_kecemasan` diperiksa untuk mengukur derajat ketidakseimbangan kelas.

### 5.3 Analisis Hubungan

| Pasangan variabel | Metode | Alasan |
|---|---|---|
| Antar butir Likert / skor domain vs skor kecemasan | Korelasi **Spearman** | Data ordinal, hubungan belum tentu linear |
| Atribut numerik (durasi tidur, nilai rapor, jam belajar) | Korelasi **Pearson** + scatter plot | Data kontinu |
| Kategorikal vs label kecemasan | Uji **Chi-Square** dan *cross-tab* | Menguji keterkaitan kategori dengan tingkat kecemasan |
| Seluruh skor domain | **Heatmap korelasi** | Mendeteksi multikolinearitas antar-indeks domain |

Korelasi kuat antar dua indeks domain (|r| > 0,8) menjadi sinyal agar salah satunya digabung atau dibuang di Fase 3.

### 5.4 Dugaan Awal yang Akan Diuji

Dugaan berikut disusun dari kerangka teoretis pada Fase 1 dan akan dikonfirmasi atau ditolak oleh data:

1. Durasi tidur pendek dan jam tidur larut berasosiasi positif dengan skor kecemasan.
2. Penggunaan media sosial sebelum tidur berkaitan dengan durasi tidur yang lebih pendek — jalur tidak langsung menuju kecemasan.
3. Tekanan ekspektasi keluarga memberikan kontribusi mandiri, terpisah dari beban tugas sekolah.
4. Dukungan pertemanan berperan sebagai penyangga: pada beban akademik yang sama, siswa dengan dukungan tinggi memiliki skor kecemasan lebih rendah.
5. Konsumsi kafein/gula dan kebiasaan melewatkan makan lebih tinggi pada kelompok skor kecemasan tinggi.

> Dugaan ini adalah hipotesis kerja, bukan temuan. Semua pernyataan pada laporan akhir harus disertai angka hasil pengolahan data yang sebenarnya.

---

## 6. Keterbatasan Data yang Sudah Terlihat

| Keterbatasan | Dampak | Mitigasi |
|---|---|---|
| Seluruh data bersifat *self-report* | Rawan *social desirability bias* | Anonimitas ditegaskan; hasil dibaca sebagai indikasi, bukan diagnosis |
| Sampel tidak acak (penyebaran via media sosial dan sekolah) | Generalisasi terbatas | Cakupan sampel dilaporkan apa adanya pada laporan akhir |
| Potensi kelas "indikasi tinggi" berjumlah sedikit | Model bias ke kelas mayoritas | *Resampling* pada data latih dan pelaporan metrik per kelas |
| Kuesioner satu gelombang (*cross-sectional*) | Tidak dapat menyimpulkan sebab-akibat | Semua temuan dinyatakan sebagai hubungan, bukan kausalitas |
| Responden adalah anak di bawah umur | Kewajiban perlindungan data | Anonimisasi sejak ekspor; identitas sekolah dan nama tidak dibawa ke dataset analisis |

---

## 7. Keluaran Fase dan Transisi ke Fase 3

| Dokumen | Isi |
|---|---|
| `laporan_deskripsi_data.md` | Jumlah baris/kolom, kamus data lengkap (bagian 3) |
| `laporan_eksplorasi_data.ipynb` | Statistik deskriptif, histogram, boxplot, heatmap korelasi |
| `laporan_kualitas_data.md` | Tabel missing per kolom, daftar inkonsistensi, daftar outlier dengan keputusannya |
| `daftar_masalah_data.csv` | Antrean pekerjaan yang harus diselesaikan pada Fase 3 |

Temuan kualitas data menentukan langkah pembersihan; temuan korelasi menentukan kandidat fitur dan indeks domain; distribusi label menentukan strategi penyeimbangan kelas. Ketiganya menjadi masukan langsung Fase 3 — Data Preparation.
