# Fase 2 — Data Understanding

**Proyek:** SPK Rekomendasi Penanganan Kecemasan Siswa (Random Forest + SMART)
**Metodologi:** CRISP-DM — Fase 2 dari 6

---

## 1. Sumber Data

Proyek memakai dua sumber data dengan peran berbeda.

| Aspek | Data pralatih (Kaggle) | Data riil (kuesioner) |
|---|---|---|
| Sumber | Kaggle `sharmajicoder/student-mental-health-and-burnout`, berkas `student_mental_health_burnout_1M.csv` | Google Form yang disebarkan tim ke siswa SMA |
| Ukuran asli | 1.000.000 baris × 20 kolom | **304 respons** × 68 kolom (195 dari formulir awal, 109 dari formulir revisi) |
| Yang dipakai | Rentang usia pelajar 14–25 = **692.545 baris** (berkas hanya berisi usia 17–25), dibagi 80/20 menjadi data latih dan uji | Usia 14–25 dengan jawaban Psikologis lengkap = **292 respons** |
| Populasi | Mahasiswa, usia 17–29 | Siswa SMA/SMP akhir, usia 14–24 (median 15) |
| Peran | Pralatih model; populasi referensi SPK | Pelatihan ulang dan pengujian model |
| Kerahasiaan | Publik | **Rahasia**: tidak masuk repositori |

Alasan dua sumber: data Kaggle besar dan lengkap sehingga cocok untuk membangun model awal, tetapi populasinya bukan siswa SMA. Data kuesioner sesuai populasi sasaran, tetapi jumlahnya kecil. Model dilatih lebih dulu pada Kaggle, lalu disesuaikan dengan data kuesioner.

## 2. Deskripsi Data Kaggle (1.000.000 baris)

Seluruh berkas dipakai. Tidak ada nilai hilang, tidak ada baris duplikat, dan tidak ada nilai mustahil (semua skor 0–10, jam tidur 3–10, nilai 42–97). Usia tersebar merata pada 17–29 tahun, sekitar 77.000 baris per usia.

| Atribut | Tipe | Rata-rata | Std | Min | Median | Maks | Peran |
|---|---|---|---|---|---|---|---|
| age | numerik | 23,00 | 3,74 | 17 | 23 | 29 | fitur (dibersihkan ke 14–25) |
| gender | kategorikal | Female 480.070 · Male 479.643 · Other 40.287 | | | | | fitur |
| academic_year | ordinal | 2,50 | 1,12 | 1 | 3 | 4 | tidak dipakai |
| study_hours_per_day | numerik | 5,00 | 1,99 | 0,00 | 5,00 | 14,00 | fitur + kriteria |
| exam_pressure | numerik | 6,00 | 1,55 | 1,00 | 6,00 | 10,00 | fitur |
| academic_performance | numerik | 71,00 | 5,66 | 42,37 | 71,00 | 97,25 | fitur + kriteria |
| stress_level | numerik | 4,25 | 1,68 | 0,00 | 4,24 | 10,00 | fitur |
| **anxiety_score** | numerik | 2,99 | 1,51 | 0,00 | 2,97 | 10,00 | **target** |
| depression_score | numerik | 1,27 | 1,22 | 0,00 | 1,05 | 8,53 | tidak dipakai (hasil) |
| sleep_hours | numerik | 6,50 | 1,47 | 3,00 | 6,50 | 10,00 | fitur + kriteria |
| physical_activity | numerik | 3,01 | 1,46 | 0,00 | 3,00 | 7,00 | fitur + kriteria |
| social_support | numerik | 5,00 | 1,98 | 0,00 | 5,00 | 10,00 | tidak dipakai |
| screen_time | numerik | 5,02 | 1,96 | 1,00 | 5,00 | 12,00 | tidak dipakai |
| internet_usage | numerik | 5,04 | 2,16 | 1,00 | 5,00 | 14,00 | tidak dipakai |
| financial_stress | numerik | 5,00 | 1,98 | 0,00 | 5,00 | 10,00 | fitur + kriteria |
| family_expectation | numerik | 5,98 | 1,96 | 0,00 | 6,00 | 10,00 | fitur + kriteria |
| burnout_score | numerik | 1,78 | 1,66 | 0,00 | 1,50 | 10,00 | fitur + kriteria |
| mental_health_index | numerik | 7,02 | 1,31 | 1,31 | 7,07 | 10,00 | tidak dipakai (hasil) |
| risk_level | kategorikal | Low 766.645 · Medium 218.275 · High 15.080 | | | | | tidak dipakai (hasil) |
| dropout_risk | numerik | 1,32 | 1,34 | 0,00 | 1,01 | 9,33 | tidak dipakai (hasil) |

### 2.1 Korelasi dengan skor kecemasan

| Atribut | r (Pearson) | Atribut | r (Pearson) |
|---|---|---|---|
| stress_level | 0,761 | study_hours_per_day | 0,269 |
| burnout_score | 0,668 | family_expectation | 0,264 |
| depression_score | 0,476 | academic_performance | 0,045 |
| dropout_risk | 0,462 | physical_activity | −0,132 |
| financial_stress | 0,354 | sleep_hours | −0,200 |
| exam_pressure | 0,350 | mental_health_index | −0,869 |

Korelasi pada 692.545 baris usia 14–25 hampir sama (selisih ≤ 0,002), jadi pembersihan usia tidak mengubah pola data.

Temuan penting:

- `stress_level` dan `burnout_score` paling kuat berhubungan dengan kecemasan.
- `mental_health_index`, `depression_score`, `dropout_risk`, dan `risk_level` adalah **variabel hasil** yang sangat terkait dengan target. `mental_health_index` bahkan dihitung langsung dari target: `10 − 0,4·stres − 0,3·kecemasan − 0,3·depresi` (cocok tepat). Memakainya sebagai fitur menimbulkan *label leakage*, jadi keempatnya dikeluarkan.
- `social_support`, `screen_time`, dan `internet_usage` hampir tidak berkorelasi (|r| < 0,01) sehingga tidak dipakai.
- `academic_year` tidak berlaku untuk siswa SMA dan juga tidak berkorelasi.

## 3. Deskripsi Data Kuesioner

Kuesioner (lampiran `context.pdf`) terdiri atas bagian berikut. Bentuk jawaban: pilihan rentang, skala Likert 5 titik, atau isian angka.

| Bagian | Contoh butir | Dipakai untuk |
|---|---|---|
| Identitas | jenis kelamin, tanggal lahir, nama sekolah, sumber informasi, nama teman | gender dan usia; sisanya **data pribadi yang dibuang** |
| Kebiasaan belajar | jam belajar per hari, belajar larut malam, waktu tidak cukup, tugas terlambat | jam belajar, tingkat stres |
| Tidur | durasi tidur, jam mulai tidur, kurang tidur, mengantuk di kelas | jam tidur (+ ekstra) |
| Akademik | nilai rata-rata rapor, persentase kehadiran | nilai rapor (+ ekstra) |
| Media sosial | durasi harian, saat belajar, sebelum tidur | ekstra |
| Tuntutan dan tekanan | tugas bersamaan, tertekan ujian, takut mengecewakan orang tua, tuntutan nilai keluarga | tekanan ujian, stres, ekspektasi keluarga |
| Aktivitas fisik | hari olahraga per minggu, menit per sesi, aktivitas ringan | aktivitas fisik (+ ekstra) |
| Kegiatan di luar sekolah | jumlah ekskul, jam per minggu, lomba | ekstra |
| Kelelahan | sulit membagi waktu, kelelahan, kehilangan minat, rasa percaya diri | *burnout* |
| Pertemanan | diterima, teman dipercaya, dukungan, tekanan konformitas, konflik | ekstra |
| **Psikologis** | gugup/cemas, sulit mengendalikan khawatir, konsentrasi (dibalik), pikiran terganggu, sulit menyelesaikan tugas; formulir revisi menambah mudah tersinggung dan menghindari kegiatan | **target skor kecemasan** |
| Pola makan | uang saku cukup, jajan, minuman manis/berkafein, makan saat tertekan, melewatkan makan | tekanan finansial (+ ekstra) |

"Ekstra" berarti butir disimpan untuk analisis korelasi dan satu eksperimen model yang diperluas. Butir ini tidak dipakai model yang dideploy, karena model harus tetap sejajar dengan 11 fitur Kaggle.

### 3.1 Statistik data kuesioner

Ekspor berisi **304 respons** dan 68 kolom. Satu formulir Google dipakai dalam dua versi: 195 respons dijawab pada formulir awal dan 109 pada formulir revisi (yang menambah butir seperti "nilai di bawah target", "bisa bercerita ke keluarga", kualitas tidur, dan dua butir Psikologis). Setiap skor gabungan dirata-rata dari butir yang dijawab baris itu, sehingga kedua versi dapat digabung (diperiksa di Fase 3).

- **Usia** dihitung dari tanggal lahir. Ekspor tidak memuat *timestamp*, jadi tanggal acuannya adalah tanggal pemrosesan. 8 tanggal lahir tidak masuk akal (tahun 2026–2027) sehingga usianya dikosongkan. 11 respons di luar rentang 14–25 (10 berusia 13, 1 berusia 30) dibuang. 1 respons tidak lengkap pada butir Psikologis sehingga tidak memiliki target.
- **Dipakai:** 292 respons, laki-laki 160 dan perempuan 132; usia 14 (89), 15 (97), 16 (41), 17 (35), 18 (14), 19–24 (16).
- Tidak ada baris jawaban duplikat; 1 baris menjawab semua butir Likert sama (*straight-lining*) dan tetap dipakai.

| Fitur | Rata-rata | Std | Min | Median | Maks | Rata-rata Kaggle |
|---|---|---|---|---|---|---|
| age | 15,39 | 1,53 | 14 | 15 | 24 | 21,00 |
| study_hours_per_day | 2,12 | 1,99 | 0,25 | 1,50 | 10,00 | 5,01 |
| academic_performance | 81,83 | 8,47 | 40,00 | 84,00 | 100,00 | 71,07 |
| exam_pressure | 5,82 | 2,20 | 1,00 | 5,50 | 10,00 | 6,01 |
| stress_level | 4,39 | 1,48 | 0,00 | 4,58 | 8,75 | 4,24 |
| sleep_hours | 6,73 | 1,35 | 4,00 | 6,50 | 12,00 | 6,52 |
| physical_activity | 2,73 | 1,99 | 0,00 | 1,50 | 7,00 | 3,01 |
| financial_stress | 3,38 | 2,57 | 0,00 | 2,50 | 10,00 | 5,01 |
| family_expectation | 4,72 | 2,46 | 0,00 | 5,00 | 10,00 | 5,97 |
| burnout_score | 4,67 | 1,80 | 0,00 | 5,00 | 10,00 | 1,77 |
| **anxiety_score** | **5,01** | 1,78 | 0,00 | 5,00 | 9,29 | **2,99** |

Perbedaan dengan Kaggle cukup besar: siswa belajar lebih sedikit di luar sekolah (2,1 vs 5,0 jam), nilai rapor lebih tinggi, *burnout* jauh lebih tinggi (4,7 vs 1,8), dan **skor kecemasan rata-rata 5,0 dibanding 3,0**. Karena sebaran target bergeser sejauh ini, model Kaggle tidak dapat dipakai langsung untuk siswa SMA (Fase 5).

**Korelasi dengan skor kecemasan (data riil).**

| Fitur | r | Fitur | r |
|---|---|---|---|
| exam_pressure | 0,498 | financial_stress | 0,001 |
| burnout_score | 0,490 | physical_activity | −0,027 |
| family_expectation | 0,389 | age | −0,060 |
| stress_level | 0,303 | academic_performance | −0,118 |
| study_hours_per_day | 0,029 | sleep_hours | −0,126 |

Pola faktor dominan berbeda dari Kaggle. Pada siswa SMA, tekanan ujian, *burnout*, dan ekspektasi keluarga paling berhubungan dengan kecemasan, sedangkan pada Kaggle tingkat stres jauh mendominasi (r 0,76). Di antara butir ekstra, kualitas tidur (r 0,55), merasa kurang tidur (0,37), mengantuk di kelas (0,37), konflik dengan teman (0,34), dan media sosial saat belajar (0,32) paling berkorelasi.

## 4. Kualitas Data

| Dimensi | Kaggle | Kuesioner (pemeriksaan otomatis `spk/gform.py`) |
|---|---|---|
| Kelengkapan | 0 nilai hilang | 8 usia kosong (tanggal lahir tidak masuk akal), 1 nilai kosong pada 6 fitur, 1 target kosong; fitur kosong diisi median data latih |
| Duplikat | 0 | 0 baris jawaban identik |
| Validitas | rentang wajar | nilai di luar rentang dikosongkan; jawaban isian bebas yang tidak terbaca hanya pada butir ekstra (31 jawaban, mis. jam kegiatan ditulis dalam menit) |
| Kesungguhan | – | 1 baris *straight-lining* |
| Privasi | tidak ada data pribadi | tanggal lahir dan isian bebas dibuang segera setelah usia dihitung; 12 kolom pertanyaan tambahan yang tidak dipetakan tidak dipakai |
| Konsistensi butir | – | Cronbach α: kecemasan 0,78 (7 butir) / 0,69 (5 butir); *burnout* 0,67; tingkat stres 0,32; tekanan ujian 0,38; ekspektasi keluarga 0,37 |

## 5. Keterbatasan

- Dataset Kaggle berasal dari mahasiswa, bukan siswa SMA, dan sebaran skornya berbeda jauh dari data riil. Karena itu model dilatih ulang dengan data riil.
- Skor gabungan tingkat stres, tekanan ujian, dan ekspektasi keluarga memiliki konsistensi butir rendah (α 0,32–0,38), jadi butir-butirnya mengukur hal yang cukup berbeda.
- 292 respons masih kecil untuk model yang stabil; hasil *holdout* 59 respons memiliki ketidakpastian besar.
- Tingkat stres dan tekanan finansial pada kuesioner adalah **proksi**, sehingga maknanya tidak identik dengan kolom Kaggle.
- Data kuesioner bersifat *self-report* dan *cross-sectional*: rawan bias sosial dan tidak menunjukkan sebab-akibat.
- Sampel kuesioner tidak acak (disebar lewat sekolah, media sosial, dan teman), sehingga generalisasinya terbatas.
