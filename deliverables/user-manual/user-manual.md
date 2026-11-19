[[TOC]]

[[PAGEBREAK]]

# 1. Pendahuluan

## 1.1 Tentang aplikasi

**SI SMART Kecemasan Siswa** adalah aplikasi web yang membantu guru Bimbingan Konseling (BK) melakukan tiga hal:

1. **Memperkirakan tingkat kecemasan** siswa (skor 0–10) dari 11 faktor gaya hidup dan akademik, memakai model *Random Forest* yang dilatih dengan jawaban kuesioner 292 siswa SMA.
2. **Menyusun prioritas**: siswa mana yang perlu ditangani lebih dulu (skor prioritas SMART).
3. **Merekomendasikan penanganan** dari lima bentuk dukungan, yaitu Tidur, Olahraga, Strategi belajar, Konseling, dan Relaksasi, lengkap dengan alasannya.

> **Penting.** Aplikasi ini adalah alat bantu skrining dan pendukung keputusan, **bukan alat diagnosis klinis**. Keputusan akhir tetap pada guru BK atau tenaga profesional.

## 1.2 Dua bagian aplikasi

Aplikasi memiliki dua bagian. Sakelar **Aplikasi | Laporan** di kanan atas memindahkan Anda dari satu bagian ke bagian lain.

| Bagian | Untuk siapa | Halaman |
|---|---|---|
| **Aplikasi** | guru BK, wali kelas, siswa dengan pendampingan | Beranda, Nilai siswa, Nilai kelas, Bantuan (Bab 3–6) |
| **Laporan** (laporan teknis) | dosen, penguji, pengelola aplikasi | Bab 1 Data sampai Bab 8 Arsitektur (Bab 7) |

Bagian Aplikasi menampilkan hasil yang ringkas dan langsung dapat dipakai. Bagian Laporan memuat seluruh perhitungan dan evaluasi, termasuk perhitungan SMART langkah demi langkah untuk siswa yang baru dinilai.

## 1.3 Kebutuhan

- Peramban modern (Chrome, Edge, Firefox, atau Safari) dan koneksi internet.
- Tidak perlu akun atau kata sandi.
- Alamat aplikasi: ⟦ISI: URL Streamlit Community Cloud⟧

Saat dibuka pertama kali, server mungkin memerlukan 20–40 detik untuk "bangun". Tunggu hingga halaman Beranda tampil.

# 2. Tampilan Umum dan Beranda

![Gambar 1. Bilah atas dan halaman Beranda](figures/fig01_home.png)

| No. | Bagian | Fungsi |
|---|---|---|
| 1 | Menu halaman | Di samping logo **SI SMART**. Pada bagian Aplikasi berisi **Beranda**, **Nilai siswa**, **Nilai kelas**, dan **Bantuan**; pada bagian Laporan berisi **1 Data** sampai **8 Arsitektur**. Halaman yang sedang dibuka diberi latar hijau muda |
| 2 | Sakelar **Aplikasi \| Laporan** | Berpindah antara bagian Aplikasi dan Laporan teknis. Sakelar selalu menunjukkan bagian halaman yang sedang dibuka |
| 3 | Bahasa | **ID** = Bahasa Indonesia, **EN** = English. Seluruh teks, label, dan grafik ikut berganti (Bab 8) |
| 4 | **Mulai penilaian** | Membuka halaman **Nilai siswa** (Bab 3) |
| 5 | **Nilai satu kelas sekaligus** | Membuka halaman **Nilai kelas** (Bab 4) |
| 6 | Contoh hasil | Gambaran bentuk hasil: rekomendasi utama, tingkat kecemasan, dan prioritas. Kartu ini hanya contoh, bukan hasil siswa mana pun |
| 7 | Cara kerjanya | Tiga langkah: isi kuesioner, sistem menghitung (Random Forest lalu SMART), baca rekomendasinya |
| 8 | Lima bentuk dukungan | Penjelasan singkat setiap alternatif penanganan yang dapat direkomendasikan |
| 9 | **Untuk dosen dan penguji** | Tombol **Buka laporan teknis** membuka bagian Laporan, Bab 1 (Bab 7) |
| 10 | Catatan kaki | Penafian (bukan alat diagnosis klinis) dan pernyataan privasi. Catatan ini tampil di bagian bawah setiap halaman |

> Pada layar sempit (ponsel), menu halaman dapat digeser ke kiri dan ke kanan, dan sakelar bagian serta bahasa pindah ke baris kedua.

[[PAGEBREAK]]

# 3. Menilai Satu Siswa

## 3.1 Membuka formulir

Klik **Mulai penilaian** di Beranda (Gambar 1, no. 4), atau klik **Nilai siswa** di menu atas.

![Gambar 2. Bagian atas formulir satu siswa](figures/fig02_form_top.png)

| No. | Bagian | Keterangan |
|---|---|---|
| 1 | Pilihan model | Tombol di kanan atas, mis. **Model riil**. Membuka pengaturan model prediksi (subbab 3.8) |
| 2 | Kartu bagian bernomor | Pertanyaan dikelompokkan dalam lima kartu: **1 Tentang siswa**, **2 Belajar & nilai**, **3 Tuntutan & tekanan**, **4 Tidur, olahraga & uang saku**, dan **5 Kelelahan**. Tidak ada nama atau data pribadi yang diminta |
| 3 | Daftar pilihan | Untuk jam belajar dan durasi tidur. Klik lalu pilih jawaban (mis. "2 jam") |
| 4 | Isian angka | Untuk usia dan nilai rapor. Ketik angka atau pakai tombol **−** / **+** |
| 5 | Pilihan jawaban | Klik salah satu bulatan (mis. Tidak pernah / 1 kali / 2–3 kali). Hanya satu jawaban yang dapat dipilih |
| 6 | **Sebelum mengisi** | Empat tips: jawab sesuai kondisi akhir-akhir ini, tidak ada jawaban benar atau salah, jawaban tidak disimpan, dan hasil bukan diagnosis |
| 7 | **Contoh risiko tinggi / rendah** | Mengisi formulir dengan jawaban contoh (subbab 3.3) |
| 8 | **Kosongkan jawaban** | Menghapus semua jawaban di formulir |

## 3.2 Mengisi kuesioner

Formulir dibuka **kosong**: tidak ada jawaban yang diisikan otomatis. Jawab ke-18 pertanyaan sesuai kondisi siswa dalam seminggu atau sebulan terakhir.

| Kartu | Pertanyaan | Pilihan jawaban |
|---|---|---|
| 1 Tentang siswa | Jenis kelamin; usia | Laki-laki / Perempuan; 12–30 tahun |
| 2 Belajar & nilai | Jam belajar mandiri per hari | Dibawah 30 menit … 11 jam 30 menit |
| | Nilai rata-rata rapor terakhir | 0–100 |
| | Belajar sampai larut malam (seminggu) | Tidak pernah / 1 kali / 2–3 kali / 4–5 kali / > 5 kali |
| | Waktu belajar tidak cukup | Tidak pernah / Jarang / Kadang-kadang / Sering |
| | Tugas terlambat (sebulan) | Tidak pernah / 1 / 2–3 / 4–5 / > 5 |
| | Nilai di bawah target | Tidak pernah / Jarang / Kadang-kadang / Sering / Selalu |
| 3 Tuntutan & tekanan | Terlalu banyak tugas bersamaan; tertekan karena ujian; takut mengecewakan orang tua; keluarga menuntut nilai tinggi | Tidak pernah / Jarang / Kadang-kadang / Sering / Sangat sering |
| 4 Tidur, olahraga & uang saku | Durasi tidur malam | 4 jam … 12 jam |
| | Hari berolahraga minimal 20–30 menit (seminggu) | 0 hari / 1–2 hari / 3–4 hari / 5–6 hari / 7 hari |
| | Uang saku cukup | Tidak pernah / Pernah / Netral / Sering / Sangat sering |
| 5 Kelelahan | Sulit membagi waktu; kelelahan karena kegiatan sekolah; kehilangan minat dan motivasi | Sangat tidak setuju / Tidak setuju / Netral / Setuju / Sangat setuju |

Aplikasi mengubah jawaban menjadi 11 fitur model dengan rumus yang sama seperti saat model dilatih. Contohnya, "tertekan karena ujian" pada skala 1–5 diubah ke skala 1–10.

## 3.3 Mencoba dengan jawaban contoh

Klik **Contoh risiko tinggi** atau **Contoh risiko rendah** (Gambar 2, no. 7). Formulir terisi jawaban contoh, tetapi **hasil belum ditampilkan**. Kotak biru di atas formulir memberi tahu bahwa jawaban contoh sudah dimuat. Periksa atau ubah jawabannya, lalu klik **Lihat rekomendasi**. Klik **Kosongkan jawaban** untuk kembali ke formulir kosong.

![Gambar 3. Formulir setelah jawaban contoh risiko tinggi dimuat](figures/fig05_example.png)

## 3.4 Memproses

![Gambar 4. Tombol proses di bagian bawah formulir](figures/fig03_form_submit.png)

Klik **Lihat rekomendasi** (no. 9) di bawah kartu terakhir. Jawaban hanya dikirim saat tombol ini diklik.

Bila masih ada pertanyaan yang belum dijawab, hasil tidak ditampilkan. Kotak merah di bawah tombol menyebut jumlah dan daftar pertanyaan yang belum dijawab (Gambar 5). Lengkapi jawabannya, lalu klik **Lihat rekomendasi** lagi.

![Gambar 5. Pesan pertanyaan yang belum dijawab](figures/fig03b_missing.png)

Bila semua pertanyaan terjawab, formulir berganti menjadi layar hasil dalam beberapa detik dan halaman kembali ke atas.

[[PAGEBREAK]]

## 3.5 Membaca hasil

![Gambar 6. Layar hasil satu siswa (contoh risiko tinggi)](figures/fig06_result.png)

| No. | Bagian | Cara membaca |
|---|---|---|
| 1 | **Ubah jawaban** | Kembali ke formulir. Jawaban sebelumnya tetap terisi, jadi cukup ubah yang perlu lalu klik **Lihat rekomendasi** lagi |
| 2 | **Perlu perhatian segera** (kotak merah) | Muncul bila prediksi kecemasan termasuk **10% tertinggi** di antara 292 siswa SMA responden kuesioner (≥ 6,28). Apa pun hasil SMART, sertakan **konseling** dan pertimbangkan rujukan ke guru BK, psikolog, atau layanan kesehatan jiwa |
| 3 | **Rekomendasi utama** | Bentuk dukungan dengan skor SMART tertinggi, penjelasan singkatnya, dan **skor kecocokan** (0–1) |
| 4 | **Perkiraan tingkat kecemasan** | Prediksi Random Forest (0–10) dan label posisinya (lihat tabel di bawah). Kalimat di bawahnya menyebut persentil, mis. "Lebih tinggi dari 100% di antara 292 siswa SMA responden kuesioner" |
| 5 | **Prioritas penanganan** | Skor prioritas SMART (0–1). Makin tinggi, makin perlu didahulukan. Labelnya: *Rendah*, *Sedang*, *Tinggi*, atau *Sangat tinggi* |
| 6 | **Urutan lima pilihan** | Kelima bentuk dukungan diurutkan dari skor tertinggi. Makin panjang batang, makin cocok untuk siswa ini |
| 7 | **Mengapa …?** | Kalimat alasan: alternatif pemenang, **pendorong utama** (kriteria yang paling menyumbang), selisih dengan alternatif kedua, dan posisi skor prioritas |
| 8 | **Faktor utama** | Faktor yang paling menaikkan (merah) atau menurunkan (hijau) prediksi kecemasan siswa ini (subbab 3.6) |
| 9 | **Bagaimana jika?** | Simulasi perubahan satu atau beberapa faktor sekaligus (subbab 3.6) |
| 10 | **Perhitungan lengkap** | Tombol **Buka perhitungan** membuka Laporan, Bab 3, untuk siswa yang sama (subbab 3.7) |
| 11 | **Nilai siswa lain** | Mengosongkan formulir untuk siswa berikutnya |

**Arti label kecemasan dan prioritas.** Label tidak dihitung dari rata-rata, tetapi dari posisi siswa di antara 292 siswa SMA responden kuesioner (bila model Kaggle dipilih, pembandingnya 20.000 siswa data uji Kaggle). Arahkan kursor ke tanda **?** di samping label untuk melihat rentang tepatnya:

| Label kecemasan | Posisi | Prediksi (model riil) |
|---|---|---|
| Di bawah rata-rata | 40% terbawah | di bawah 4,66 |
| Sekitar rata-rata | 40–60% | 4,66–5,34 |
| Di atas rata-rata | 60–90% | 5,34–6,28 |
| Jauh di atas rata-rata | 10% teratas | 6,28 ke atas (selalu dirujuk) |

Label prioritas (*Rendah*, *Sedang*, *Tinggi*, *Sangat tinggi*) memakai batas posisi yang sama (40%, 60%, 90%) pada skor prioritas.

**Tips membaca selisih.** Bila selisih skor alternatif pertama dan kedua kecil (< 0,02), kotak **Mengapa …?** menambahkan kalimat "Selisihnya kecil, jadi … juga layak dipertimbangkan".

## 3.6 Faktor utama dan "Bagaimana jika?"

**Faktor utama** (Gambar 6, no. 8) membandingkan siswa dengan rata-rata 100 siswa sampel Kaggle. Angka merah (+) menunjukkan berapa poin sebuah faktor menaikkan perkiraan kecemasan; angka hijau (−) menurunkannya. Nilai di tengah adalah nilai siswa untuk faktor itu.

![Gambar 7. "Bagaimana jika?" dengan dua faktor diubah sekaligus](figures/fig07_whatif.png)

**Bagaimana jika?** menghitung ulang prediksi, prioritas, dan rekomendasi bila satu atau beberapa faktor diubah:

1. Kotak **Faktor yang diubah** (no. 1) sudah berisi faktor yang paling menaikkan prediksi siswa ini. Klik kotak itu untuk menambah faktor lain, atau klik **×** untuk menghapusnya.
2. Setiap faktor terpilih mendapat penggeser (no. 2) yang dimulai dari nilai siswa sekarang. Arahkan kursor ke tanda **?** untuk melihat nilai siswa sekarang.
3. Geser satu atau beberapa nilai. Hasil gabungannya (no. 3) menampilkan prediksi kecemasan, skor prioritas, dan rekomendasi utama baru beserta selisihnya. Tulisan "(berubah)" berarti rekomendasi utama berganti.

Ini simulasi model, bukan bukti sebab-akibat; gunakan sebagai bahan diskusi dengan siswa.

## 3.7 Perhitungan lengkap

Klik **Buka perhitungan** (Gambar 6, no. 10). Aplikasi berpindah ke bagian Laporan, **Bab 3 Perhitungan SMART (contoh kerja)**, dan memakai siswa yang baru dinilai. Isinya dijelaskan di subbab 7.3.

## 3.8 Mengganti model prediksi

![Gambar 8. Pengaturan model prediksi](figures/fig04_model.png)

1. Klik tombol model (no. 1) di kanan atas halaman Nilai siswa, Nilai kelas, atau setiap bab Laporan.
2. Pilih **model prediksi** (no. 2):
   - **Iterasi 2 · Data kuesioner riil (bawaan)**: dilatih ulang dengan 292 respons siswa SMA. Disarankan untuk siswa sungguhan; rata-rata meleset ±1,1 poin pada siswa riil.
   - **Iterasi 1 · Kaggle (model dasar)**: dilatih dengan data mahasiswa. Akurat pada data Kaggle, tetapi meleset ±1,9 poin pada siswa SMA. Pilih untuk membandingkan atau menunjukkan perkembangan model.
3. Klik di luar panel untuk menutupnya. Hasil di semua halaman langsung dihitung ulang.

Baris paling bawah panel (no. 3) menunjukkan **model aktif**: sumber data model dan jumlah data. Pilihan model tetap berlaku saat berpindah halaman selama sesi berjalan. Bobot SMART tetap sama untuk kedua model.

[[PAGEBREAK]]

# 4. Menilai Satu Kelas

Klik **Nilai satu kelas sekaligus** di Beranda (Gambar 1, no. 5), atau klik **Nilai kelas** di menu atas.

## 4.1 Menyiapkan berkas

![Gambar 9. Halaman Nilai kelas sebelum ada data](figures/fig09_class_empty.png)

Halaman dibuka kosong. Tidak ada data yang dinilai sampai Anda mengunggah berkas atau menyalakan data contoh.

| No. | Bagian | Keterangan |
|---|---|---|
| 1 | **Berkas data siswa** | Klik **Upload** lalu pilih berkas .csv/.xlsx, atau seret berkas ke kotak ini. Ukuran maksimum 50 MB |
| 2 | **Coba dengan data contoh (30 siswa)** | Sakelar untuk mencoba halaman tanpa berkas (subbab 4.2) |
| 3 | **Unduh template CSV** | Berkas CSV berisi 11 kolom model dan dua baris contoh, untuk sekolah yang tidak memakai Google Form |
| 4 | Langkah memulai | Tiga langkah singkat: ekspor Google Form, unggah, atau pakai template / data contoh |

Ada dua format yang diterima:

1. **Ekspor Google Form.** Di Google Form, buka tab **Respons**, lalu klik **Lihat di Spreadsheet**. Di spreadsheet, pilih **File → Download → CSV** atau **Microsoft Excel (.xlsx)**. Unggah berkas itu tanpa diubah. Aplikasi mengenali kolom pertanyaan secara otomatis.
2. **CSV 11 kolom** dengan nama kolom persis seperti Lampiran A (atau isi template no. 3). Kolom `student_id` bersifat opsional.

Setelah berkas diunggah, kotak biru menyebut jenis berkas yang terdeteksi, jumlah baris, dan **kolom pribadi yang dibuang** (waktu isi, tanggal lahir, nama sekolah, sumber informasi, nama teman).

## 4.2 Data contoh

Nyalakan **Coba dengan data contoh (30 siswa)** bila belum punya berkas. Data contoh berisi 30 siswa acak dari data uji Kaggle (mahasiswa, bukan siswa sungguhan sekolah Anda); lima di antaranya sengaja dipilih dari kecemasan sangat tinggi agar daftar rujukan tidak kosong. Bila berkas diunggah, berkas selalu dipakai dan sakelar dinonaktifkan. Gambar 10 memakai data contoh.

## 4.3 Membaca hasil kelas

![Gambar 10a. Ringkasan kelas, daftar rujukan, dan daftar prioritas](figures/fig10_class_a.png)

| No. | Bagian | Keterangan |
|---|---|---|
| 1 | Keterangan data | Sumber data yang sedang dinilai (data contoh atau berkas unggahan) |
| 2 | Ringkasan kelas | **Jumlah siswa**; **Perlu dirujuk segera**; **Prioritas tinggi** (skor prioritas di 40% teratas); **Paling sering disarankan**. Arahkan kursor ke tanda **?** untuk batas angkanya |
| 3 | **Perlu dirujuk segera** | Siswa dengan prediksi kecemasan di 10% teratas di antara 292 responden riil (≥ 6,28), beserta rekomendasi SMART-nya dan alamat rujukan. Sertakan konseling untuk siswa ini, apa pun rekomendasinya |
| 4 | Filter | **Rekomendasi**: tampilkan hanya siswa dengan rekomendasi tertentu (kosong = semua). **Hanya yang perlu dirujuk**: saring siswa rujukan. **Tampilkan skor tiap dukungan**: menambah kolom skor kelima alternatif |
| 5 | **Daftar prioritas** | Diurutkan dari **skor prioritas SMART** tertinggi. Kolom: ID siswa, peringkat, skor prioritas, prediksi kecemasan, rekomendasi utama, dan tanda **Rujuk**. Klik judul kolom untuk mengurutkan |
| 6 | **Unduh rencana kelas (CSV)** | Mengunduh semua siswa (tanpa data pribadi) dengan peringkat, skor, program, tanda rujukan, dan skor kelima alternatif. Pada ekspor Google Form, setiap siswa diberi ID anonim (R0001, …) sesuai urutan baris berkas |

![Gambar 10b. Rencana program, detail satu siswa, dan opsi lanjutan](figures/fig10_class_b.png)

| No. | Bagian | Keterangan |
|---|---|---|
| 7 | **Rencana program** | Satu kartu per bentuk dukungan: jumlah siswa dan ID-nya, dari prioritas tertinggi. Kartu Konseling juga menyebut jumlah siswa rujukan dari kelompok lain. Dipakai untuk merencanakan sesi kelompok |
| 8 | **Detail satu siswa** | Pilih satu ID siswa untuk melihat urutan kelima pilihannya. Tombol **Lihat perhitungan siswa ini** membuka Laporan, Bab 3, untuk siswa tersebut |
| 9 | **Opsi lanjutan** | Kotak **Normalisasi dengan batas referensi** dicentang secara bawaan: siswa dibandingkan dengan batas data latih. Tanpa centang: siswa dibandingkan antarsiswa dalam berkas itu saja, seperti di notebook |

**Evaluasi model pada data baru.** Bila ekspor Google Form memuat jawaban bagian **Psikologis** (P01–P05), muncul bagian **Evaluasi model**: aplikasi menghitung skor kecemasan sebenarnya dan membandingkannya dengan prediksi (MAE, RMSE, R²) untuk model aktif dan model dasar Kaggle, lengkap dengan grafik aktual vs prediksi. Gunakan hanya respons yang **baru**, yang belum dipakai melatih model.

## 4.4 Pesan kesalahan yang mungkin muncul

| Pesan | Penyebab | Solusi |
|---|---|---|
| Kolom fitur model hilang | Berkas bukan ekspor Google Form dan tidak memiliki 11 kolom | Unggah ekspor asli dari Google Form, atau pakai template CSV (Lampiran A) |
| Berkas tidak dapat diproses: missing fields / ambiguous fields | Judul pertanyaan di Google Form diubah | Hubungi pengelola aplikasi untuk memperbarui pemetaan kolom (`spk/gform_mapping.json`) |
| … nilai kosong diisi dengan median data latih | Ada jawaban kosong | Tidak perlu tindakan; periksa kembali data bila jumlahnya besar |
| Angka di luar rentang dikosongkan | Mis. nilai rapor > 100 | Perbaiki data sumber lalu unggah ulang |

[[PAGEBREAK]]

# 5. Halaman Bantuan

![Gambar 11. Halaman Bantuan](figures/fig11_help.png)

Halaman **Bantuan** merangkum cara memakai aplikasi: langkah menilai satu siswa dan satu kelas beserta tautannya (no. 1), arti keempat bagian hasil (no. 2), serta sasaran pengguna dan hal yang perlu diingat (no. 3). Baris paling bawah menyebut alamat rujukan.

# 6. Perhitungan untuk Siswa yang Sedang Dinilai

Bagian Aplikasi sengaja menampilkan hasil ringkas. Untuk menelusuri angka di balik satu hasil, pakai salah satu jalan berikut:

- Dari hasil satu siswa: tombol **Buka perhitungan** (Gambar 6, no. 10).
- Dari hasil satu kelas: tombol **Lihat perhitungan siswa ini** (Gambar 10b, no. 8).
- Dari bagian Laporan: **3 Perhitungan**, lalu pilih **Siswa terakhir dinilai**.

Ketiganya membuka Laporan, Bab 3 (subbab 7.3).

[[PAGEBREAK]]

# 7. Laporan Teknis

Klik **Laporan** pada sakelar di kanan atas, atau **Buka laporan teknis** di Beranda. Laporan teknis ditujukan untuk dosen dan penguji: isinya bukti kinerja model dan SPK, disusun seperti laporan dengan bab, subbab, tabel, dan gambar bernomor.

## 7.1 Navigasi laporan

![Gambar 12. Bagian atas sebuah bab laporan](figures/fig12_report_frame.png)

| No. | Bagian | Keterangan |
|---|---|---|
| 1 | Sakelar **Aplikasi \| Laporan** | Menunjukkan bahwa Anda berada di bagian Laporan. Klik **Aplikasi** untuk kembali ke Beranda |
| 2 | Menu bab | **1 Data**, **2 Model**, **3 Perhitungan**, **4 xAI**, **5 SMART**, **6 Keadilan**, **7 CRISP-DM**, **8 Arsitektur** |
| 3 | Nomor bab | "Laporan teknis · Bab n" |
| 4 | **Isi** | Daftar subbab. Klik salah satu untuk langsung menuju subbab itu |
| 5 | Pilihan model | Sama seperti subbab 3.8. Semua angka di laporan mengikuti model yang dipilih |
| 6 | Judul subbab | Bernomor, mis. "1.1" |
| 7 | Keterangan tabel/gambar | "Tabel n.m" di atas tabel dan "Gambar n.m" di bawah gambar |

![Gambar 13. Tombol bab sebelumnya dan berikutnya](figures/fig12b_pager.png)

Di bagian bawah setiap bab ada tautan ke bab sebelumnya dan bab berikutnya (no. 8).

## 7.2 Bab 1 Data

![Gambar 14a. Bab 1 Data (1/3)](figures/fig13_ch1_a.png)

![Gambar 14b. Bab 1 Data (2/3)](figures/fig13_ch1_b.png)

![Gambar 14c. Bab 1 Data (3/3)](figures/fig13_ch1_c.png)

Bab 1 menampilkan dua sumber data. **Data pralatih Kaggle**: jumlah baris, rata-rata skor kecemasan, rentang usia, jumlah fitur, komposisi gender, dan histogram delapan kriteria SMART. **Data kuesioner riil**: ringkasan agregat 292 respons siswa (jumlah respons, duplikat, *straight-lining*, komposisi gender, *box plot* setiap fitur, dan korelasi setiap butir dengan skor kecemasan). Tidak ada data per siswa yang ditampilkan.

## 7.3 Bab 3 Perhitungan SMART (contoh kerja)

Bab 3 menguraikan seluruh langkah dari jawaban siswa sampai rekomendasi, dengan angka siswa yang dipilih.

![Gambar 15. Bab 3: daftar isi, pilihan siswa, dan input](figures/fig14_ch3_top.png)

Pilih siswa (no. 2): **Siswa terakhir dinilai** (muncul bila sudah ada siswa yang dinilai), **Contoh risiko tinggi**, atau **Contoh risiko rendah**. Subbab Bab 3 (no. 1):

| Subbab | Isi |
|---|---|
| 3.1 Input siswa | Nilai 11 fitur model (Tabel 3.1, no. 3) |
| 3.2 Prediksi Random Forest | Rumus rata-rata pohon, prediksi, persentil, jumlah pohon, dan perbandingan dua model untuk siswa ini |
| 3.3 Nilai kriteria | Delapan kriteria SMART, jenis (*benefit*/*cost*), dan batas min/maks |
| 3.4 Normalisasi utilitas | Rumus utilitas *benefit* dan *cost*, lalu substitusi angka siswa untuk setiap kriteria |
| 3.5 Bobot | Matriks bobot kriteria × alternatif; setiap kolom berjumlah 1 |
| 3.6 Skor tiap alternatif | Kontribusi bobot × utilitas per kriteria, skor S tiap alternatif, dan penjabaran skor alternatif teratas |
| 3.7 Peringkat | Urutan alternatif dan selisihnya dengan yang teratas; sama dengan halaman hasil |
| 3.8 Prioritas & aturan pengaman | Skor prioritas (bobot 1/8), persentilnya, batas pengaman P90, dan apakah aturan pengaman aktif |
| 3.9 Sensitivitas bobot | Rekomendasi utama bila bobot satu kriteria diubah ±10% dan ±20% |
| 3.10 Penjelasan AI | Tiga tab: nilai Shapley, dari prediksi ke rekomendasi, dan "Bagaimana jika?" |

![Gambar 16. Bab 3.4–3.5: normalisasi utilitas dan bobot](figures/fig15_ch3_utility.png)

![Gambar 17. Bab 3.6–3.7: skor tiap alternatif dan peringkat](figures/fig16_ch3_scores.png)

![Gambar 18. Bab 3.8–3.9: prioritas, aturan pengaman, dan sensitivitas](figures/fig17_ch3_priority.png)

![Gambar 19. Bab 3.10: penjelasan AI untuk siswa ini](figures/fig18_ch3_xai.png)

**Membaca uji sensitivitas (3.9).** Setiap baris adalah satu kriteria dan setiap kolom perubahan bobotnya. Isi sel adalah rekomendasi utama setelah bobot diubah. **Sel berwarna oranye muda** berarti rekomendasi berubah. Kotak hijau berarti rekomendasi kokoh; kotak biru menyebut berapa skenario yang mengubah rekomendasi.

**Membaca penjelasan AI (3.10).** Tab **Prediksi kecemasan** menampilkan grafik air terjun nilai Shapley: batang oranye menaikkan prediksi dan batang biru menurunkannya, dibanding rata-rata 100 siswa sampel Kaggle. Tab **Dari prediksi ke rekomendasi** menunjukkan bagian skor rekomendasi yang berasal dari prediksi kecemasan dan sumbangan setiap kriteria. Tab **Bagaimana jika?** memuat tabel skenario (setiap faktor dipindahkan ke tingkat siswa tipikal) dan alat yang sama seperti subbab 3.6.

## 7.4 Bab 2 Model, Bab 4 xAI, Bab 5 SMART, dan Bab 6 Keadilan

![Gambar 20a. Bab 2 Model Random Forest (1/3)](figures/fig19_ch2_a.png)

![Gambar 20b. Bab 2 Model Random Forest (2/3)](figures/fig19_ch2_b.png)

![Gambar 20c. Bab 2 Model Random Forest (3/3)](figures/fig19_ch2_c.png)

**Bab 2** memuat metrik model aktif (MAE, MSE, RMSE, R² pada *holdout* 59 siswa riil; MAE 1,11), iterasi model Kaggle → data riil, grafik aktual vs prediksi dan sebaran residual, kepentingan fitur, perbandingan algoritma, strategi pelatihan ulang, dan metadata model.

![Gambar 21a. Bab 4 Explainable AI (1/2)](figures/fig20_ch4_a.png)

![Gambar 21b. Bab 4 Explainable AI (2/2)](figures/fig20_ch4_b.png)

**Bab 4** menampilkan penjelasan global: kepentingan fitur Gini vs permutasi, dan *partial dependence* (PDP). Pilih faktor yang ditampilkan di kotak pilihan faktor. Bagian bawah menjelaskan metode xAI.

![Gambar 22a. Bab 5 Hasil dan sensitivitas SMART (1/3)](figures/fig21_ch5_a.png)

![Gambar 22b. Bab 5 Hasil dan sensitivitas SMART (2/3)](figures/fig21_ch5_b.png)

![Gambar 22c. Bab 5 Hasil dan sensitivitas SMART (3/3)](figures/fig21_ch5_c.png)

**Bab 5** menjelaskan SMART pada seluruh populasi referensi: kriteria dan batas normalisasi, bobot per alternatif, sebaran skor prioritas, profil utilitas, jumlah siswa per rekomendasi, stabilitas global (persentase siswa yang rekomendasinya tetap saat semua bobot diacak ±10% dan ±20% sebanyak 100 kali), dan sensitivitas per kriteria.

![Gambar 23. Bab 6 Keadilan](figures/fig22_ch6.png)

**Bab 6** membandingkan kesalahan prediksi (MAE) dan sebaran rekomendasi antar gender. Pada data uji Kaggle selisihnya di bawah 0,01 poin. Pada *holdout* kuesioner riil, galat siswa perempuan 0,29 poin lebih besar (29 dan 30 siswa), sehingga perlu dipantau saat data bertambah.

## 7.5 Bab 7 CRISP-DM

![Gambar 24. Bab 7 CRISP-DM, fase 1](figures/fig23_ch7.png)

| No. | Bagian | Keterangan |
|---|---|---|
| 1 | Pilihan fase | Enam fase CRISP-DM: Business Understanding, Data Understanding, Data Preparation, Modeling, Evaluation, Deployment. Klik untuk berpindah |
| 2 | Judul fase | Nomor fase dan pertanyaan yang dijawab fase itu |
| 3 | Angka kunci | Empat angka langsung dari data atau model, mis. jumlah baris, R², stabilitas |
| 4 | **Yang dikerjakan** | Empat langkah utama fase tersebut |
| 5 | Bukti | Tabel atau grafik pendukung, mis. korelasi kolom, alur penyiapan data, perbandingan algoritma, atau status kriteria keberhasilan |
| 6 | Keputusan, keluaran, kode | Keputusan penting, berkas yang dihasilkan, dan letak kodenya |
| 7 | **Berikutnya / Sebelumnya** | Tombol untuk berpindah ke fase berikutnya atau sebelumnya |

![Gambar 25a. Fase Data Preparation dengan panel penggabungan pertanyaan (1/2)](figures/fig24_ch7_prep_a.png)

![Gambar 25b. Fase Data Preparation dengan panel penggabungan pertanyaan (2/2)](figures/fig24_ch7_prep_b.png)

Fase **Data Preparation** menampilkan jumlah baris tiap langkah (no. 1): berkas Kaggle, baris usia 14–25, data latih, dan data uji. Panel **Pertanyaan mana digabung menjadi apa** (no. 2, dibuka) menunjukkan butir kuesioner yang digabung menjadi setiap fitur dan kriteria SMART, beserta aturan dan perannya.

## 7.6 Bab 8 Arsitektur dan batasan

![Gambar 26a. Bab 8 Arsitektur dan batasan (1/4)](figures/fig25_ch8_a.png)

![Gambar 26b. Bab 8 Arsitektur dan batasan (2/4)](figures/fig25_ch8_b.png)

![Gambar 26c. Bab 8 Arsitektur dan batasan (3/4)](figures/fig25_ch8_c.png)

![Gambar 26d. Bab 8 Arsitektur dan batasan (4/4)](figures/fig25_ch8_d.png)

Bab 8 menjelaskan arsitektur sistem, ringkasan metode, kriteria dan contoh bobot, bentuk dukungan, pengaturan model aktif, keterbatasan dan etika, serta tim pengembang.

[[PAGEBREAK]]

# 8. Mengganti Bahasa

![Gambar 27. Tampilan dalam bahasa Inggris](figures/fig26_en.png)

Klik **EN** (no. 2) di pojok kanan atas untuk beralih ke bahasa Inggris, atau **ID** untuk kembali ke Bahasa Indonesia. Sakelar bagian (no. 1) dan menu halaman (no. 3) ikut berganti. Bahasa tetap berlaku saat berpindah halaman atau bagian. Hasil yang sudah diproses dan pilihan model tetap tersimpan selama sesi berjalan; jawaban formulir yang belum diproses perlu diisi ulang.

# 9. Privasi dan Etika

- Aplikasi **tidak menyimpan** data yang diketik atau diunggah. Data hanya diproses di memori selama sesi.
- Kolom pribadi pada ekspor Google Form dibuang otomatis. Hasil unduhan hanya memakai ID anonim.
- Hasil adalah **indikasi**, bukan diagnosis. Jangan memberi label kepada siswa berdasarkan skor.
- Siswa dengan kotak **Perlu perhatian segera**, atau yang masuk daftar **Perlu dirujuk segera**, perlu ditindaklanjuti dengan konseling dan, bila perlu, rujukan profesional.
- Bicarakan hasil dengan siswa secara pribadi dan suportif.

# 10. Tanya Jawab

| Pertanyaan | Jawaban |
|---|---|
| Di mana perhitungan lengkapnya? | Klik **Buka perhitungan** di hasil, atau buka **Laporan → 3 Perhitungan** (subbab 7.3) |
| Mengapa ada dua model? | Untuk menunjukkan iterasi: model Kaggle (dasar) dan model yang dilatih ulang dengan data siswa SMA. Gunakan model riil (bawaan) untuk siswa sungguhan |
| "Lebih tinggi dari …%" dibandingkan dengan siapa? | Dengan 292 siswa SMA responden kuesioner (model riil), atau 20.000 siswa data uji Kaggle (model Kaggle). Tanda **?** di samping label menyebut rentangnya (subbab 3.5) |
| Apakah skor 6/10 berarti siswa mengalami gangguan kecemasan? | Tidak. Skor adalah perkiraan dari kebiasaan dan tekanan, bukan hasil pemeriksaan klinis |
| Mengapa tombol contoh tidak langsung menampilkan hasil? | Agar jawaban contoh dapat diperiksa dan diubah dulu. Klik **Lihat rekomendasi** setelah memeriksanya |
| Bagaimana kembali ke formulir setelah hasil tampil? | Klik **Ubah jawaban** untuk memperbaiki jawaban, atau **Nilai siswa lain** untuk siswa berikutnya |
| Mengapa halaman Nilai kelas kosong? | Halaman menunggu berkas. Unggah ekspor Google Form, atau nyalakan **Coba dengan data contoh** |
| Halaman lama memuat atau kosong? | Muat ulang halaman. Saat pertama dibuka, server mungkin sedang "bangun" |
| Bisakah data siswa disimpan di aplikasi? | Tidak, demi privasi. Unduh rencana kelas (CSV) bila perlu disimpan oleh sekolah |
| Seberapa akurat perkiraan kecemasannya? | Pada siswa yang tidak dipakai melatih, rata-rata meleset ±1,1 poin dari skala 0–10. Cukup untuk mengurutkan siswa, bukan untuk skor pasti |

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

Kolom opsional: `student_id` (ID sendiri), dan `anxiety_score` (skor kecemasan sebenarnya, untuk evaluasi). Template berisi kolom-kolom ini dapat diunduh dari halaman Nilai kelas (**Unduh template CSV**).

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
