# Sistem Rekomendasi Penanganan Kecemasan Siswa SMA Menggunakan Metode *Simple Multi-Attribute Rating Technique* (SMART)

**Fase Business Understanding — CRISP-DM (Cross-Industry Standard Process for Data Mining)**

---

## 0. Penentuan Task Data Mining pada Kuesioner

Kuesioner yang tersedia berisi data self-report siswa SMA yang mencakup kebiasaan belajar, pola tidur, penggunaan media sosial, kehadiran, tuntutan akademik dan keluarga, aktivitas fisik, kegiatan organisasi, lingkungan pertemanan, kondisi psikologis, serta kebiasaan makan/jajan. Karena kuesioner **tidak memuat label diagnosis klinis**, task data mining dipilih dengan kombinasi berikut:

| Prioritas | Task Data Mining | Teknik | Peran terhadap SPK |
|---|---|---|---|
| Utama | **Clustering (segmentasi)** | K-Means / K-Medoids, validasi Silhouette & Davies-Bouldin, Elbow Method | Menghasilkan segmen profil siswa (misal: *beban akademik tinggi*, *defisit tidur & digital*, *tekanan keluarga & ekspektasi*, *kondisi stabil*) yang menjadi konteks penyesuaian bobot kriteria SMART |
| Utama | **Klasifikasi tingkat indikasi kecemasan** | Naïve Bayes, Decision Tree (C4.5), Random Forest, k-NN | Menetapkan level indikasi (Rendah / Sedang / Tinggi) yang menentukan tingkat urgensi dan kandidat alternatif penanganan |
| Pendukung | **Association Rule Mining** | Apriori / FP-Growth (support, confidence, lift) | Menemukan pola kebiasaan yang sering muncul bersamaan dengan indikasi kecemasan tinggi sebagai dasar justifikasi rekomendasi |
| Pendukung | **Analisis korelasi & feature importance** | Spearman/Chi-Square, Information Gain, Gini importance | **Menjadi dasar objektif penentuan bobot kriteria SMART**, menggantikan bobot yang semata-mata subjektif |
| Opsional | **Outlier / anomaly detection** | LOF, Isolation Forest | Mendeteksi siswa dengan profil ekstrem yang perlu prioritas rujukan langsung ke tenaga profesional |

**Pembentukan label (target variable).** Lima butir pada bagian *Psikologis* dijadikan skor komposit indikasi kecemasan (skala Likert 5 titik dikodekan 0–4, total 0–20), kemudian dikategorikan menjadi tiga level menggunakan pendekatan *cut-off* (misal terciles atau adaptasi ambang GAD-2/GAD-7). **Butir pembentuk label wajib dikeluarkan dari himpunan fitur prediktor** untuk menghindari *label leakage*; prediktor hanya berasal dari faktor gaya hidup, akademik, sosial, dan keluarga.

**Titik temu Data Mining dan SPK.** Data mining bekerja pada tahap *diagnosis* (siapa berisiko dan mengapa), sedangkan SMART bekerja pada tahap *preskripsi* (penanganan apa yang paling tepat, dengan urutan prioritas). Output data mining berupa **level indikasi + faktor dominan** menjadi input yang mengatur bobot kriteria SMART secara dinamis per siswa/segmen.

---

## 1. Latar Belakang Masalah

Kecemasan (*anxiety*) merupakan kondisi kekhawatiran berlebih yang memengaruhi pikiran, emosi, dan aktivitas sehari-hari. Pada siswa SMA, kondisi ini banyak dipicu oleh tekanan akademik seperti ujian, penumpukan tugas, tuntutan nilai, serta ekspektasi orang tua. Dampaknya bersifat berantai: menurunnya konsentrasi saat belajar, keterlambatan pengumpulan tugas, penurunan motivasi, hingga menurunnya prestasi dan kesejahteraan mental siswa.

Persoalannya, indikasi kecemasan sering tidak disadari, baik oleh siswa itu sendiri, guru, maupun lingkungan sekitarnya. Identifikasi umumnya masih bergantung pada observasi guru Bimbingan Konseling (BK) dan konsultasi tatap muka. Pendekatan ini memiliki tiga keterbatasan utama:

1. **Keterbatasan kapasitas.** Rasio guru BK terhadap jumlah siswa yang timpang membuat penjaringan menyeluruh sulit dilakukan secara rutin dan berkelanjutan.
2. **Sifat reaktif.** Penanganan umumnya baru dilakukan setelah gejala terlihat jelas atau setelah prestasi siswa menurun, bukan pada tahap dini.
3. **Subjektivitas keputusan penanganan.** Bahkan ketika siswa berisiko berhasil teridentifikasi, penentuan bentuk penanganan sering bergantung pada pengalaman personal guru, tanpa dasar penilaian multikriteria yang terdokumentasi, konsisten, dan dapat ditelusuri.

Di sisi lain, sekolah sebenarnya telah mengumpulkan data yang kaya melalui kuesioner siswa — mencakup jam belajar, durasi dan jam tidur, penggunaan media sosial, beban tugas, tekanan keluarga, aktivitas fisik, keterlibatan organisasi, kualitas relasi pertemanan, serta pola konsumsi kafein dan makanan. Data ini umumnya hanya berhenti sebagai laporan deskriptif dan **belum diolah menjadi pengetahuan yang dapat menuntun pengambilan keputusan**.

Kesenjangan tersebut membuka dua kebutuhan yang saling melengkapi. Pertama, kebutuhan akan proses *data mining* untuk menemukan pola dan faktor dominan penyebab kecemasan dari data kuesioner. Kedua, kebutuhan akan Sistem Pendukung Keputusan (SPK) yang mampu mengubah temuan tersebut menjadi rekomendasi bentuk penanganan yang terurut berdasarkan prioritas. Metode SMART dipilih karena karakteristiknya sesuai dengan konteks ini: perhitungannya sederhana dan transparan, mendukung banyak kriteria dengan satuan berbeda melalui normalisasi utilitas linear, serta menghasilkan skor akhir yang mudah dijelaskan kepada guru BK, siswa, dan orang tua — aspek yang krusial pada domain sensitif seperti kesehatan mental.

> **Catatan etis.** Sistem ini diposisikan sebagai alat bantu **skrining dan pendukung keputusan**, bukan alat diagnosis klinis. Keputusan akhir tetap berada pada guru BK dan/atau tenaga profesional.

---

## 2. Tujuan Bisnis (Business Objectives)

**Tujuan umum.** Membangun sistem pendukung keputusan berbasis SMART yang mampu merekomendasikan bentuk penanganan kecemasan yang paling sesuai bagi setiap siswa SMA, berdasarkan profil faktor risiko yang dihasilkan dari proses data mining terhadap data kuesioner.

**SPK ini merekomendasikan:**

**(a) Alternatif bentuk penanganan (rekomendasi utama)** — SPK menghasilkan *ranking* alternatif penanganan untuk tiap siswa/segmen:

| Kode | Alternatif Penanganan |
|---|---|
| A1 | Konseling individual bersama guru BK |
| A2 | Konseling kelompok / *peer support group* |
| A3 | Pelatihan manajemen waktu dan strategi belajar |
| A4 | Program perbaikan higiene tidur (*sleep hygiene*) dan pengaturan jadwal malam |
| A5 | Program aktivitas fisik terjadwal dan relaksasi (pernapasan, mindfulness) |
| A6 | Program *digital wellbeing* — pembatasan media sosial, khususnya menjelang tidur |
| A7 | Mediasi akademik: penyesuaian beban tugas/deadline bersama wali kelas |
| A8 | Sesi komunikasi dengan orang tua (*parenting session*) untuk kasus tekanan ekspektasi keluarga |
| A9 | Edukasi gizi dan pengaturan konsumsi kafein/gula |
| A10 | Rujukan ke psikolog/tenaga profesional untuk kasus indikasi berat |

**(b) Prioritas penanganan antar siswa (rekomendasi sekunder)** — SPK juga dapat menyusun urutan siswa yang paling membutuhkan intervensi lebih dahulu, sehingga sumber daya BK yang terbatas dapat dialokasikan secara adil dan terukur.

**Tujuan bisnis spesifik:**

1. Mengubah pola penanganan sekolah dari **reaktif** menjadi **preventif** melalui deteksi dini indikasi kecemasan.
2. Meningkatkan **objektivitas dan konsistensi** keputusan penanganan dengan dasar perhitungan multikriteria yang transparan.
3. Mempersingkat **waktu penjaringan** dari observasi manual berbulan-bulan menjadi proses otomatis berbasis data kuesioner.
4. Menyediakan **bukti dan alasan** di balik setiap rekomendasi, sehingga dapat dikomunikasikan kepada siswa dan orang tua tanpa memberi kesan menghakimi.
5. Mengoptimalkan **alokasi sumber daya sekolah** (jam guru BK, ruang konseling, anggaran program).

---

## 3. Tujuan Data Mining (Data Mining Goals)

Tujuan bisnis di atas diterjemahkan ke dalam tujuan data mining yang terukur:

1. **DM-1 — Segmentasi.** Menghasilkan sejumlah *cluster* profil siswa berdasarkan kesamaan pola gaya hidup, beban akademik, dan lingkungan sosial, lengkap dengan karakteristik pembeda tiap segmen.
2. **DM-2 — Klasifikasi.** Membangun model yang mengklasifikasikan siswa ke dalam tiga level indikasi kecemasan (Rendah, Sedang, Tinggi) dari atribut non-psikologis, sehingga skrining dapat dilakukan secara otomatis.
3. **DM-3 — Identifikasi faktor dominan.** Menentukan variabel yang paling berpengaruh terhadap tingkat indikasi kecemasan melalui *feature importance* dan uji korelasi, sebagai landasan empiris penentuan bobot kriteria SMART.
4. **DM-4 — Penemuan pola asosiatif.** Menghasilkan aturan asosiasi yang menggambarkan kombinasi kebiasaan yang sering menyertai indikasi kecemasan tinggi (contoh bentuk aturan: *durasi tidur rendah* ∧ *penggunaan media sosial sebelum tidur tinggi* ∧ *beban tugas bersamaan tinggi* → *indikasi kecemasan tinggi*).
5. **DM-5 — Penyediaan input SPK.** Menghasilkan keluaran terstruktur berupa `{level indikasi, cluster, tiga faktor dominan}` per siswa yang langsung dikonsumsi oleh modul SMART.

---

## 4. Faktor Penyebab dan Korelasinya terhadap Rekomendasi SPK

Kuesioner memetakan delapan kelompok faktor. Setiap kelompok berperan ganda: sebagai **variabel prediktor** dalam data mining, dan sebagai **penentu relevansi alternatif** dalam perhitungan SMART.

| Kelompok Faktor | Variabel Kuesioner Terkait | Mekanisme Pengaruh | Alternatif Penanganan yang Dikuatkan |
|---|---|---|---|
| **F1. Beban & tekanan akademik** | Frekuensi merasa tugas terlalu banyak bersamaan; tertekan karena ujian/nilai; waktu belajar dirasa tidak cukup; jumlah tugas terlambat; frekuensi belajar hingga larut malam | Tuntutan melebihi kapasitas waktu → khawatir berkepanjangan, tekanan tenggat | A3, A7, A1 |
| **F2. Pola tidur** | Durasi tidur malam; jam mulai tidur; frekuensi merasa kurang tidur; frekuensi mengantuk saat pelajaran | Defisit tidur menurunkan regulasi emosi dan konsentrasi; membentuk lingkaran cemas–sulit tidur | A4, A6, A5 |
| **F3. Penggunaan media sosial** | Durasi harian; penggunaan saat seharusnya belajar; penggunaan sebelum tidur | Menunda waktu tidur, memecah fokus belajar, memicu perbandingan sosial | A6, A3, A4 |
| **F4. Tekanan keluarga & ekspektasi** | Takut mengecewakan orang tua; tuntutan keluarga akan nilai sangat tinggi | Tekanan eksternal berkelanjutan yang tidak dapat diatasi siswa sendiri | A8, A1, A10 |
| **F5. Dukungan sosial & pertemanan** | Merasa diterima; punya teman untuk bercerita; dukungan saat bermasalah; tekanan konformitas; konflik teman | Dukungan sosial berperan sebagai penyangga (*buffer*); ketiadaannya memperkuat dampak stresor lain | A2, A1 |
| **F6. Aktivitas fisik** | Jumlah hari olahraga/minggu; durasi per sesi; aktivitas ringan-sedang; olahraga untuk meredakan stres | Aktivitas fisik menurunkan ketegangan fisiologis dan memperbaiki kualitas tidur | A5, A4 |
| **F7. Beban non-akademik & kelelahan** | Jumlah organisasi/ekskul; jam per minggu; frekuensi lomba; kesulitan membagi waktu; kelelahan; kehilangan minat/motivasi | Akumulasi beban tanpa pemulihan → indikasi kelelahan (*burnout*) | A7, A3, A1 |
| **F8. Pola makan, jajan & kafein** | Frekuensi membeli minuman manis dan berkafein; pemilihan makanan saat tertekan; merasa lebih tenang setelah makan; melewatkan waktu makan | Kafein berlebih memperberat gejala fisiologis kecemasan; *emotional eating* dan melewatkan makan menandakan koping maladaptif | A9, A1, A5 |
| **Indikator hasil** | Nilai rata-rata rapor; persentase kehadiran | Berfungsi sebagai variabel dampak/validasi, bukan prediktor utama | — |

### 4.1 Alur Korelasi Faktor → Kriteria → Rekomendasi

Hasil data mining tidak digunakan sekadar sebagai laporan, melainkan mengalir langsung ke dalam perhitungan SMART melalui dua jalur:

**Jalur 1 — Faktor dominan menentukan nilai kriteria relevansi.** Alternatif yang menyasar faktor dominan siswa memperoleh nilai tinggi pada kriteria kesesuaian. Siswa dengan faktor dominan F2 dan F3 akan mendapat nilai relevansi tinggi untuk A4 dan A6, sedangkan siswa dengan faktor dominan F4 akan mendapat nilai relevansi tinggi untuk A8.

**Jalur 2 — Feature importance menentukan bobot kriteria.** Besar pengaruh tiap faktor terhadap level indikasi kecemasan (hasil DM-3) dinormalisasi menjadi bobot pada kriteria relevansi, sehingga bobot SMART berbasis data, bukan semata penilaian subjektif.

### 4.2 Kriteria SMART yang Diusulkan

| Kode | Kriteria | Sifat | Sumber Nilai |
|---|---|---|---|
| C1 | Kesesuaian dengan faktor dominan siswa | Benefit | Output data mining (DM-3, DM-5) |
| C2 | Kesesuaian dengan tingkat urgensi/level indikasi | Benefit | Output klasifikasi (DM-2) |
| C3 | Efektivitas berdasarkan penilaian pakar & literatur | Benefit | Penilaian guru BK/psikolog |
| C4 | Ketersediaan sumber daya sekolah (SDM, fasilitas) | Benefit | Data profil sekolah |
| C5 | Biaya implementasi | Cost | Data profil sekolah |
| C6 | Waktu dan beban tambahan bagi siswa | Cost | Estimasi program |
| C7 | Aksesibilitas dan tingkat penerimaan siswa (stigma/privasi) | Benefit | Penilaian pakar & survei siswa |

**Langkah perhitungan SMART:** (1) menetapkan kriteria; (2) memberi bobot mentah dan menormalisasinya sehingga Σw = 1; (3) menghitung nilai utilitas tiap alternatif dengan normalisasi linear — untuk kriteria *benefit* digunakan `u = (Cᵢ − Cₘᵢₙ) / (Cₘₐₓ − Cₘᵢₙ)` dan untuk kriteria *cost* digunakan bentuk terbaliknya `u = (Cₘₐₓ − Cᵢ) / (Cₘₐₓ − Cₘᵢₙ)`; (4) menghitung skor akhir `U(aᵢ) = Σⱼ wⱼ · uᵢⱼ`; (5) menyusun peringkat alternatif dari skor tertinggi.

---

## 5. Hasil dan Dampak yang Diharapkan

**Bagi siswa.** Indikasi kecemasan terdeteksi lebih dini, sebelum berdampak pada prestasi dan kehadiran. Siswa menerima bentuk bantuan yang sesuai dengan penyebab spesifiknya, bukan penanganan seragam yang berpeluang tidak relevan.

**Bagi guru BK dan sekolah.** Tersedia daftar prioritas siswa dan rekomendasi program yang terdokumentasi, sehingga waktu konseling terpakai untuk penanganan, bukan untuk penjaringan awal. Perencanaan program tahunan dapat disusun berdasarkan profil segmen yang dominan di sekolah tersebut.

**Bagi pengambil kebijakan sekolah.** Tersedia bukti kuantitatif mengenai faktor yang paling berkontribusi terhadap tekanan siswa — misalnya beban tugas yang bertumpuk pada periode tertentu atau pola tidur yang terganggu — yang dapat menjadi dasar penyesuaian kebijakan akademik.

**Bagi pengembangan keilmuan.** Diperoleh model integrasi antara data mining (CRISP-DM) dan pengambilan keputusan multikriteria (SMART) pada domain kesehatan mental pendidikan, di mana bobot kriteria diturunkan dari data empiris dan hasilnya tetap dapat dijelaskan.

---

## 6. Rencana Awal Proyek (CRISP-DM)

| Fase | Aktivitas Utama | Keluaran | Estimasi |
|---|---|---|---|
| **1. Business Understanding** | Menetapkan masalah, tujuan bisnis, tujuan data mining, kriteria sukses, daftar alternatif dan kriteria SMART; validasi awal bersama guru BK | Dokumen ini; daftar alternatif & kriteria terverifikasi | Minggu 1–2 |
| **2. Data Understanding** | Pengumpulan respons kuesioner; statistik deskriptif; pemeriksaan distribusi, nilai hilang, dan outlier; uji reliabilitas (Cronbach's Alpha) tiap konstruk; matriks korelasi antarvariabel | Laporan eksplorasi data & kamus data | Minggu 3–4 |
| **3. Data Preparation** | Pembersihan data; encoding ordinal untuk skala Likert; konversi rentang jam ke nilai numerik (titik tengah); normalisasi Min-Max; penanganan *missing value*; pembentukan skor komposit indikasi kecemasan dan pelabelan tiga level; pemisahan fitur prediktor dari butir pembentuk label; seleksi fitur; penanganan ketidakseimbangan kelas (SMOTE) | *Dataset* siap model | Minggu 4–5 |
| **4. Modeling** | Clustering (K-Means, penentuan k optimal); klasifikasi (Naïve Bayes, C4.5, Random Forest, k-NN) dengan *k-fold cross validation*; *association rule mining*; ekstraksi *feature importance*; implementasi perhitungan SMART dan pemetaan output DM ke bobot/nilai kriteria | Model terlatih; profil cluster; aturan asosiasi; matriks keputusan SMART | Minggu 6–8 |
| **5. Evaluation** | Evaluasi model (akurasi, presisi, recall, F1, confusion matrix, Silhouette); uji sensitivitas bobot SMART; validasi peringkat rekomendasi terhadap penilaian pakar; pemeriksaan kesesuaian dengan tujuan bisnis | Laporan evaluasi & keputusan lanjut/perbaikan | Minggu 9–10 |
| **6. Deployment** | Pembangunan prototipe SPK berbasis web (input kuesioner → level indikasi & faktor dominan → peringkat penanganan beserta alasannya); *dashboard* rekapitulasi untuk guru BK; uji coba terbatas; penyusunan dokumentasi, panduan penggunaan, dan protokol privasi data | Prototipe SPK, dokumentasi, laporan akhir | Minggu 11–12 |

**Kebutuhan sumber daya:** data kuesioner siswa SMA (target ≥ 200 responden valid), Python (Pandas, Scikit-learn, Mlxtend, Matplotlib) atau RapidMiner untuk tahap data mining, serta Laravel/Flask + MySQL untuk prototipe SPK.

**Asumsi dan risiko:** data bersifat *self-report* sehingga rentan *social desirability bias* — dimitigasi dengan penjaminan anonimitas; jumlah responden pada kelas indikasi tinggi berpotensi sedikit — dimitigasi dengan *resampling* dan pelaporan metrik per kelas; responden adalah anak di bawah umur — memerlukan persetujuan sekolah dan orang tua serta penyimpanan data yang teranonimisasi.

---

## 7. Kriteria Sukses

### 7.1 Kriteria Sukses Bisnis

| Kode | Kriteria | Target |
|---|---|---|
| B1 | Cakupan penjaringan siswa dalam satu periode | ≥ 90% siswa terskrining, dari sebelumnya bergantung pada pelaporan sukarela |
| B2 | Waktu penjaringan hingga rekomendasi tersedia | Dari observasi manual berminggu-minggu menjadi ≤ 1 hari kerja setelah data terkumpul |
| B3 | Relevansi rekomendasi menurut guru BK | ≥ 80% kasus dinilai "sesuai" atau "sangat sesuai" |
| B4 | Penerimaan siswa terhadap rekomendasi | ≥ 75% siswa menyatakan bersedia menjalankan rekomendasi teratas |
| B5 | Keterlacakan keputusan | 100% rekomendasi disertai penjelasan faktor dominan dan skor kriteria |

### 7.2 Kriteria Sukses Data Mining (Teknis)

| Kode | Kriteria | Target |
|---|---|---|
| D1 | Kualitas data siap model | *Missing value* < 5%; Cronbach's Alpha tiap konstruk ≥ 0,70 |
| D2 | Kualitas clustering | Silhouette Score ≥ 0,50; tiap cluster memiliki karakteristik pembeda yang dapat diinterpretasikan |
| D3 | Kinerja klasifikasi | Akurasi ≥ 80%; F1-score makro ≥ 0,75 |
| D4 | Sensitivitas pada kelas kritis | **Recall kelas "indikasi tinggi" ≥ 0,85** — kesalahan melewatkan siswa berisiko jauh lebih merugikan daripada kesalahan positif |
| D5 | Kualitas aturan asosiasi | Minimal 10 aturan dengan support ≥ 10%, confidence ≥ 70%, dan lift > 1 |
| D6 | Kebermaknaan faktor | Faktor dominan hasil model konsisten dengan uji korelasi dan dapat diterima secara teoretis oleh pakar |

### 7.3 Kriteria Sukses SPK

| Kode | Kriteria | Target |
|---|---|---|
| S1 | Kesesuaian peringkat SMART dengan penilaian pakar | Tingkat kesesuaian alternatif peringkat pertama ≥ 80% pada kasus uji |
| S2 | Stabilitas model keputusan | Perubahan bobot ±10% tidak mengubah tiga alternatif teratas pada mayoritas kasus (uji sensitivitas) |
| S3 | Kelengkapan fungsional prototipe | Sistem dapat memproses input, menampilkan level indikasi, faktor dominan, peringkat penanganan, dan riwayat |
| S4 | Kebergunaan antarmuka | Skor System Usability Scale (SUS) ≥ 68 |
| S5 | Kepatuhan privasi | Data teranonimisasi, akses berjenjang, dan tersedia protokol rujukan untuk kasus indikasi berat |

---

*Dokumen ini mencakup Fase 1 CRISP-DM (Business Understanding) beserta kerangka awal fase 2–6. Sistem yang dibangun berfungsi sebagai alat bantu skrining dan pendukung keputusan, bukan pengganti diagnosis dan penanganan oleh tenaga profesional.*
