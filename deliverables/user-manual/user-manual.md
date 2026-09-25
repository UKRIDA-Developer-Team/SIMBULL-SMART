[[TOC]]

[[PAGEBREAK]]

# 1. Pendahuluan

## 1.1 Tentang aplikasi

**SPK SMART Kecemasan Siswa** adalah aplikasi web yang membantu guru Bimbingan Konseling (BK) melakukan tiga hal:

1. **Memperkirakan tingkat kecemasan** siswa (skor 0–10) dari 11 faktor gaya hidup dan akademik, memakai model *Random Forest*.
2. **Menyusun prioritas**: siswa mana yang perlu ditangani lebih dulu (skor prioritas SMART).
3. **Merekomendasikan penanganan** dari lima alternatif, yaitu Tidur, Olahraga, Strategi belajar, Konseling, dan Relaksasi, lengkap dengan alasannya.

> **Penting.** Aplikasi ini adalah alat bantu skrining dan pendukung keputusan, **bukan alat diagnosis klinis**. Keputusan akhir tetap pada guru BK atau tenaga profesional.

## 1.2 Siapa penggunanya

| Pengguna | Kebutuhan | Fitur utama |
|---|---|---|
| Guru BK | skrining dini, daftar prioritas, pilihan penanganan | Rekomendasi (satu siswa dan banyak siswa) |
| Wali kelas / pimpinan sekolah | gambaran umum kondisi siswa | Analisis |
| Siswa (dengan pendampingan) | refleksi diri | Rekomendasi → Satu siswa |

## 1.3 Kebutuhan

- Peramban modern (Chrome, Edge, Firefox, atau Safari) dan koneksi internet.
- Tidak perlu akun atau kata sandi.
- Alamat aplikasi: ⟦ISI: URL Streamlit Community Cloud⟧

Saat dibuka pertama kali, server mungkin memerlukan 20–40 detik untuk "bangun". Tunggu hingga halaman Beranda tampil.

# 2. Tampilan Umum

![Gambar 1. Tampilan umum dan halaman Beranda](figures/fig01_home.png)

| No. | Bagian | Fungsi |
|---|---|---|
| 1 | Menu halaman | Berpindah antara **Beranda**, **Rekomendasi**, **Analisis**, dan **Tentang** |
| 2 | Bahasa | **ID** = Bahasa Indonesia, **EN** = English. Seluruh teks, label, dan grafik ikut berganti |
| 3 | Profil bobot SMART | **A** berbasis domain (bawaan, paling stabil), **B** hampir seimbang, **C** sama rata (hanya pembanding). Hasil di semua halaman langsung berubah |
| 4 | Info model aktif | Sumber data model (Kaggle, atau Kaggle → data kuesioner riil) dan jumlah data |
| 5 | Penafian dan privasi | Pengingat bahwa hasil bukan diagnosis, dan data tidak disimpan |
| 6 | Ringkasan | Jumlah kriteria, jumlah alternatif, dan akurasi model (MAE, R²) |
| 7 | Alur kerja | Kuesioner → 11 fitur → Random Forest → SMART → rekomendasi beserta alasan |

Di bawah alur kerja terdapat tautan **Mulai rekomendasi →** yang langsung membuka halaman Rekomendasi.

> Pada layar sempit (ponsel), menu samping tersembunyi. Ketuk tombol **»** di kiri atas untuk membukanya.

[[PAGEBREAK]]

# 3. Menilai Satu Siswa

## 3.1 Membuka formulir

Klik **Rekomendasi** di menu (Gambar 1, no. 1). Tab **Satu siswa** terbuka secara bawaan.

![Gambar 2. Bagian atas formulir satu siswa](figures/fig02_form_top.png)

| No. | Bagian | Keterangan |
|---|---|---|
| 1 | Tab | **Satu siswa** untuk menilai satu orang; **Banyak siswa (unggah berkas)** untuk menilai satu kelas atau sekolah (Bab 4) |
| 2 | Cara input | **Kuesioner (seperti Google Form)**: pertanyaan sama persis dengan Google Form, disarankan. **Lanjutan (11 nilai fitur model)**: isi langsung nilai fitur 0–10 |
| 3 | Coba contoh profil | **Risiko tinggi** dan **Risiko rendah** langsung menampilkan hasil untuk contoh siswa, berguna untuk mengenal aplikasi atau demo |
| 4 | Identitas | Jenis kelamin dan usia. Tidak ada nama atau data pribadi yang diminta, dan data tidak disimpan |
| 5 | Penggeser (*slider*) | Geser ke kiri/kanan untuk memilih jawaban. Label merah di atas penggeser menunjukkan jawaban terpilih |
| 6 | Isian angka | Ketik angka atau pakai tombol **−** / **+** (mis. nilai rapor 0–100) |

## 3.2 Mengisi kuesioner

Isi setiap pertanyaan sesuai kondisi siswa dalam seminggu atau sebulan terakhir.

| Bagian | Pertanyaan | Pilihan jawaban |
|---|---|---|
| Identitas | Jenis kelamin; usia | Laki-laki / Perempuan; 12–30 tahun |
| Kebiasaan belajar | Jam belajar mandiri per hari | Dibawah 30 menit … 11 jam 30 menit |
| | Belajar sampai larut malam (seminggu) | Tidak pernah / 1 kali / 2-3 kali / 4-5 kali |
| | Waktu belajar tidak cukup | Tidak pernah / Jarang / Kadang-kadang / Sering |
| | Tugas terlambat (sebulan) | Tidak pernah / 1 / 2-3 / 4-5 |
| | Nilai rata-rata rapor terakhir | 0–100 |
| Tuntutan dan tekanan | Terlalu banyak tugas bersamaan; tertekan karena ujian; takut mengecewakan orang tua; keluarga menuntut nilai tinggi | Tidak pernah … Sangat sering |
| Tidur, aktivitas fisik, uang saku | Durasi tidur malam | 4 jam … 12 jam |
| | Hari berolahraga ≥ 20–30 menit (seminggu) | 0 / 1-2 / 3-4 / 5-6 / 7 hari |
| | Uang saku cukup | Tidak pernah … Sangat sering |
| Kelelahan | Sulit membagi waktu; kelelahan karena kegiatan; kehilangan minat dan motivasi | Sangat tidak setuju … Sangat setuju |

Aplikasi mengubah jawaban menjadi 11 fitur model dengan rumus yang sama seperti saat model dilatih. Contohnya, "tertekan karena ujian" pada skala 1–5 diubah ke skala 1–10.

## 3.3 Mode lanjutan (opsional)

Pilih **Lanjutan (11 nilai fitur model)** bila nilai fitur sudah diketahui, misalnya dari data lain. Arahkan kursor ke ikon **?** di samping setiap penggeser untuk melihat arti dan rentangnya.

## 3.4 Memproses

![Gambar 3. Tombol proses di bagian bawah formulir](figures/fig03_form_submit.png)

Klik **Proses rekomendasi** (no. 7). Hasil muncul di bawah formulir dalam 1–2 detik. Jawaban hanya dikirim saat tombol ini diklik, jadi mengubah penggeser tidak langsung mengubah hasil.

[[PAGEBREAK]]

## 3.5 Membaca hasil

![Gambar 4. Hasil penilaian satu siswa (contoh "Risiko tinggi")](figures/fig04_result.png)

| No. | Bagian | Cara membaca |
|---|---|---|
| 1 | **Perlu perhatian segera** (kotak merah) | Muncul bila prediksi kecemasan termasuk **10% tertinggi** populasi referensi. Apa pun hasil SMART, sertakan **konseling** dan pertimbangkan rujukan ke psikolog atau layanan kesehatan jiwa |
| 2 | Tiga angka utama | **Prediksi skor kecemasan** (0–10); **Skor prioritas SMART** (0–1, makin tinggi makin perlu didahulukan); **Rekomendasi utama** |
| 3 | Ikon **?** | Arahkan kursor untuk melihat persentil: "lebih tinggi dari …% populasi referensi" |
| 4 | Tiga alternatif teratas | Urutan penanganan dengan skornya. Guru BK tetap bebas memilih di antara ketiganya |
| 5 | Mengapa rekomendasi ini? | Kalimat alasan: alternatif pemenang, **pendorong utama** (kriteria yang paling menyumbang), selisih dengan alternatif kedua, dan posisi skor prioritas |
| 6 | Grafik kontribusi | Setiap batang adalah satu alternatif. Panjang batang = skor SMART, dan setiap warna = sumbangan satu kriteria (bobot × utilitas). Warna yang lebar menunjukkan alasan utama |

**Tips membaca selisih.** Bila selisih skor alternatif pertama dan kedua kecil (< 0,02), aplikasi menandainya. Kedua alternatif sama-sama layak dipertimbangkan.

## 3.6 Rincian nilai dan utilitas

Buka panel **Nilai fitur model & utilitas** di bawah grafik.

![Gambar 5. Nilai tiap kriteria, jenis, dan utilitasnya](figures/fig05_inputs.png)

- **Nilai**: nilai kriteria siswa. Prediksi kecemasan berasal dari model; sisanya dari jawaban.
- **Jenis**: *benefit* = makin tinggi makin butuh perhatian (mis. kelelahan); *cost* = makin rendah makin butuh perhatian (mis. jam tidur).
- **Utilitas** 0–1: posisi siswa dibandingkan populasi referensi. Nilai 1 berarti kondisi paling membutuhkan perhatian.

## 3.7 Uji sensitivitas bobot

Buka panel **Uji sensitivitas bobot (siswa ini)**.

![Gambar 6. Uji sensitivitas untuk siswa yang sedang dinilai](figures/fig06_sensitivity.png)

Setiap baris adalah satu kriteria. Setiap kolom adalah perubahan bobotnya: −20%, −10%, +10%, +20%. Isi sel adalah rekomendasi utama setelah bobot diubah. **Sel berwarna merah** berarti rekomendasi berubah. Kalimat hijau "Stabil" berarti rekomendasi kokoh. Kalimat kuning berarti hasil siswa ini berada di batas, sehingga sebaiknya ditinjau bersama alternatif kedua.

## 3.8 Mengubah profil bobot

Pilih profil **A**, **B**, atau **C** di menu samping (Gambar 1, no. 3). Hasil siswa yang sedang ditampilkan langsung dihitung ulang. Profil **C** memberi bobot sama pada semua alternatif sehingga hasilnya selalu seri, dan aplikasi menampilkan peringatan.

[[PAGEBREAK]]

# 4. Menilai Banyak Siswa

Gunakan tab **Banyak siswa (unggah berkas)** untuk menyusun daftar prioritas satu kelas atau sekolah sekaligus.

## 4.1 Menyiapkan berkas

Ada dua format yang diterima:

1. **Ekspor Google Form.** Di Google Form, buka tab **Respons**, lalu klik **Lihat di Spreadsheet**. Di spreadsheet, pilih **File → Download → CSV** atau **Microsoft Excel (.xlsx)**. Unggah berkas itu tanpa diubah. Aplikasi mengenali kolom pertanyaan secara otomatis.
2. **CSV 11 kolom** dengan nama kolom persis seperti Lampiran A. Kolom `student_id` bersifat opsional.

Ukuran maksimum berkas 50 MB.

## 4.2 Mengunggah dan membaca hasil

![Gambar 7a. Unggah berkas, deteksi otomatis, dan tabel peringkat](figures/fig07_batch_a.png)

| No. | Bagian | Keterangan |
|---|---|---|
| 1 | **Upload** | Klik lalu pilih berkas .csv/.xlsx, atau seret berkas ke kotak ini |
| 2 | Data contoh | Tanpa unggahan, aplikasi memakai **Sampel Kaggle** atau **Ekspor Google Form SINTETIS** (data buatan, bukan siswa nyata) untuk mencoba fitur |
| 3 | Deteksi berkas | Jenis berkas yang terdeteksi, jumlah baris, dan **kolom pribadi yang dibuang** (waktu isi, tanggal lahir, nama sekolah, sumber informasi, nama teman) |
| 4 | Normalisasi | Centang (bawaan) = dibandingkan dengan populasi referensi. Tanpa centang = dibandingkan antarsiswa dalam berkas itu saja |
| 5 | Tampilkan N teratas | Jumlah baris yang ditampilkan di tabel |
| 6 | Tabel peringkat | Diurutkan dari **skor prioritas SMART** tertinggi. Kolom: peringkat, skor prioritas, rekomendasi utama dan skornya, prediksi kecemasan, dan skor kelima alternatif. Klik judul kolom untuk mengurutkan |
| 7 | **Unduh peringkat lengkap** | Mengunduh seluruh hasil sebagai CSV tanpa data pribadi. Setiap siswa diberi ID anonim (R0001, …) sesuai urutan baris berkas |

![Gambar 7b. Grafik sebaran dan evaluasi pada data baru](figures/fig07_batch_b.png)

| No. | Bagian | Keterangan |
|---|---|---|
| 8 | Grafik sebaran | Jumlah siswa per rekomendasi, dan sebaran skor prioritas |
| 9 | Evaluasi model pada data baru | Muncul bila berkas memuat jawaban bagian **Psikologis**. Aplikasi menghitung skor kecemasan sebenarnya dan membandingkannya dengan prediksi (MAE, RMSE, R²) untuk model aktif dan model dasar Kaggle |

## 4.3 Pesan kesalahan yang mungkin muncul

| Pesan | Penyebab | Solusi |
|---|---|---|
| Kolom fitur model hilang | Berkas bukan ekspor Google Form dan tidak memiliki 11 kolom | Unggah ekspor asli dari Google Form, atau lengkapi kolom sesuai Lampiran A |
| Berkas tidak dapat diproses: missing fields / ambiguous fields | Judul pertanyaan di Google Form diubah | Hubungi pengelola aplikasi untuk memperbarui pemetaan kolom (`spk/gform_mapping.json`) |
| … nilai kosong diisi dengan median data latih | Ada jawaban kosong | Tidak perlu tindakan; periksa kembali data bila jumlahnya besar |
| Angka di luar rentang dikosongkan | Mis. nilai rapor > 100 | Perbaiki data sumber lalu unggah ulang |

[[PAGEBREAK]]

# 5. Halaman Analisis

Halaman **Analisis** menampilkan bukti kinerja model dan SPK dalam lima tab (Gambar 8, no. 1). Semua grafik memakai populasi referensi 20.000 siswa dan mengikuti profil bobot yang dipilih.

## 5.1 Tab Data

![Gambar 8. Tab Data: sebaran kriteria pada data referensi](figures/fig08_an_data.png)

Menampilkan jumlah data, rata-rata skor kecemasan, rentang usia, histogram delapan kriteria SMART, dan jumlah per gender. Setelah model dilatih dengan data kuesioner riil, bagian **Data kuesioner riil** juga menampilkan ringkasan agregat: jumlah respons, *box plot* tiap fitur, dan korelasi dengan skor kecemasan. Tidak ada data per siswa yang ditampilkan.

## 5.2 Tab Model (Data Mining)

![Gambar 9a. Metrik, grafik aktual vs prediksi, dan sebaran galat](figures/fig09_an_model_a.png)

![Gambar 9b. Kepentingan fitur dan perbandingan algoritma](figures/fig09_an_model_b.png)

- **MAE / MSE / RMSE / R²**: akurasi prediksi pada data uji. MAE 0,77 berarti rata-rata prediksi meleset ±0,77 poin pada skala 0–10.
- **Aktual vs prediksi**: titik yang dekat garis merah berarti prediksi tepat.
- **Kepentingan fitur**: faktor yang paling memengaruhi prediksi. Tingkat stres dan kelelahan adalah yang terbesar.
- **Perbandingan algoritma**: alasan pemilihan Random Forest dibanding regresi linear, pohon keputusan, gradient boosting, dan baseline.

## 5.3 Tab SMART (SPK)

![Gambar 10a. Kriteria, batas normalisasi, dan bobot per alternatif](figures/fig10_an_smart_a.png)

![Gambar 10b. Sebaran skor prioritas, profil utilitas, dan sebaran rekomendasi](figures/fig10_an_smart_b.png)

![Gambar 10c. Frekuensi rekomendasi, 20 siswa prioritas teratas, dan korelasi](figures/fig10_an_smart_c.png)

Tab ini menjelaskan bagaimana SMART bekerja pada seluruh populasi. Isinya: jenis setiap kriteria, bobot tiap alternatif (peta warna), sebaran skor prioritas, profil utilitas kelompok atas/tengah/bawah, sebaran skor per alternatif, dan skor rekomendasi 20 siswa dengan prioritas tertinggi.

## 5.4 Tab Sensitivitas

![Gambar 11a. Stabilitas global dan peta sensitivitas per kriteria](figures/fig11_an_sens_a.png)

![Gambar 11b. Perbandingan profil bobot A, B, dan C](figures/fig11_an_sens_b.png)

- **Stabilitas global**: persentase siswa yang rekomendasi utamanya tetap saat semua bobot diacak ±10% atau ±20% sebanyak 100 kali. Profil A: 94,6% tetap pada ±10%.
- **Peta sensitivitas**: persentase siswa yang rekomendasinya berubah bila satu kriteria diubah bobotnya. Makin merah makin sensitif.
- **Perbandingan profil**: jumlah siswa per rekomendasi untuk profil A, B, dan C.

## 5.5 Tab Keadilan

![Gambar 12. Pemeriksaan keadilan per gender](figures/fig12_an_fair.png)

Membandingkan kesalahan prediksi (MAE) dan sebaran rekomendasi antar gender. Selisih kecil (< 0,02 poin) menunjukkan model tidak bias terhadap gender tertentu.

[[PAGEBREAK]]

# 6. Halaman Tentang

![Gambar 13a. Tujuan dan arsitektur sistem](figures/fig13_about_a.png)

![Gambar 13b. Data, persiapan data, pemodelan, dan SMART](figures/fig13_about_b.png)

![Gambar 13c. Kriteria, alternatif, model, keterbatasan, etika, dan tim](figures/fig13_about_c.png)

Halaman ini menjelaskan tujuan, arsitektur, sumber data, persiapan data, metode Random Forest dan SMART, evaluasi, keterbatasan, serta prinsip etika dan privasi aplikasi.

# 7. Mengganti Bahasa

![Gambar 14. Tampilan dalam bahasa Inggris](figures/fig14_en.png)

Klik **EN** (no. 1) untuk beralih ke bahasa Inggris, atau **ID** untuk kembali ke Bahasa Indonesia. Pilihan cara input, jawaban yang sudah diproses, dan profil bobot tetap tersimpan selama sesi berjalan. Jawaban formulir yang belum diproses akan kembali ke nilai bawaan.

# 8. Privasi dan Etika

- Aplikasi **tidak menyimpan** data yang diketik atau diunggah. Data hanya diproses di memori selama sesi.
- Kolom pribadi pada ekspor Google Form dibuang otomatis. Hasil unduhan hanya memakai ID anonim.
- Hasil adalah **indikasi**, bukan diagnosis. Jangan memberi label kepada siswa berdasarkan skor.
- Siswa dengan kotak **Perlu perhatian segera** perlu ditindaklanjuti dengan konseling dan, bila perlu, rujukan profesional.
- Bicarakan hasil dengan siswa secara pribadi dan suportif.

# 9. Tanya Jawab

| Pertanyaan | Jawaban |
|---|---|
| Mengapa rekomendasi berbeda saat profil bobot diganti? | Setiap profil menimbang kriteria secara berbeda. Profil A adalah bawaan karena paling stabil (lihat Analisis → Sensitivitas) |
| Apakah skor 6/10 berarti siswa mengalami gangguan kecemasan? | Tidak. Skor adalah perkiraan dari kebiasaan dan tekanan, bukan hasil pemeriksaan klinis |
| Mengapa semua hasil "Tidur" pada profil C? | Profil C memberi bobot sama pada semua alternatif sehingga skornya seri. Profil C hanya pembanding |
| Halaman lama memuat atau kosong? | Muat ulang halaman. Saat pertama dibuka, server mungkin sedang "bangun" |
| Bisakah data siswa disimpan di aplikasi? | Tidak, demi privasi. Unduh hasil peringkat (CSV) bila perlu disimpan oleh sekolah |

[[PAGEBREAK]]

# Lampiran A. Format CSV 11 Kolom

| Kolom | Arti | Rentang |
|---|---|---|
| `age` | usia (tahun) | 12–30 |
| `gender` | jenis kelamin | Male / Female / Other |
| `study_hours_per_day` | jam belajar mandiri per hari | 0–14 |
| `academic_performance` | nilai rata-rata rapor | 0–100 |
| `exam_pressure` | tekanan ujian | 1–10 |
| `stress_level` | tingkat stres akademik | 0–10 |
| `sleep_hours` | jam tidur per malam | 3–12 |
| `physical_activity` | hari berolahraga per minggu | 0–7 |
| `financial_stress` | tekanan finansial | 0–10 |
| `family_expectation` | ekspektasi keluarga | 0–10 |
| `burnout_score` | skor kelelahan | 0–10 |

Kolom opsional: `student_id` (ID sendiri), dan `anxiety_score` (skor kecemasan sebenarnya, untuk evaluasi).

# Lampiran B. Kuesioner Evaluasi Pengguna

Setelah mencoba aplikasi, pengguna diminta mengisi Google Form evaluasi (skala 1 = sangat tidak setuju sampai 5 = sangat setuju):

| No. | Aspek | Pertanyaan |
|---|---|---|
| 1 | Pemahaman fitur | Seberapa mudah Anda memahami informasi dan hasil analisa yang ditampilkan oleh aplikasi ini? |
| 2 | Kesesuaian hasil | Apakah rekomendasi atau keputusan yang diberikan oleh aplikasi masuk akal dan sesuai dengan kondisi nyata? |
| 3 | Manfaat & efisiensi | Apakah aplikasi ini membuat proses pengambilan keputusan menjadi lebih cepat atau lebih mudah dibandingkan cara manual? |
| 4 | Stabilitas sistem | Apakah aplikasi berjalan lancar (tidak loading terlalu lama atau error) saat Anda mencoba menggunakan fitur-fiturnya? |
| 5 | Kenyamanan visual (UI) | Apakah tampilan aplikasi (warna, ukuran tulisan, dan tata letak) nyaman dilihat dan tidak membingungkan? |

Tautan Google Form evaluasi: ⟦ISI⟧
