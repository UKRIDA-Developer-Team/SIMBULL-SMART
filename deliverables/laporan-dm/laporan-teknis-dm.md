[[TOC]]

[[PAGEBREAK]]

# Pendahuluan

Laporan ini mendokumentasikan teknik Data Mining pada proyek akhir **Sistem Pendukung Keputusan Rekomendasi Penanganan Kecemasan Siswa**. Laporan ini bukan proyek baru. Fokusnya adalah validasi teknis *pipeline* Data Mining dengan metodologi **CRISP-DM** (*Cross-Industry Standard Process for Data Mining*): pemahaman masalah, pemahaman dan persiapan data, pemodelan Random Forest, evaluasi, dan integrasi model ke aplikasi web berbasis Streamlit. Aplikasi tersebut menggabungkan prediksi Data Mining dengan metode SPK SMART.

Bagian bertanda ⟦ISI …⟧ diisi setelah *pipeline* dijalankan pada data kuesioner riil yang bersifat rahasia. Angka agregatnya dihasilkan otomatis oleh `scripts/train.py --stage real`.

[[PAGEBREAK]]
# 1. Business Understanding




---

## 1.1 Latar Belakang Masalah

Kecemasan (*anxiety*) adalah kekhawatiran berlebih yang memengaruhi pikiran, emosi, dan aktivitas sehari-hari. Pada siswa, pemicunya banyak berasal dari tekanan akademik: ujian, tugas yang menumpuk, tuntutan nilai, dan ekspektasi orang tua. Dampaknya berantai: konsentrasi turun, tugas terlambat, motivasi melemah, hingga prestasi dan kesejahteraan mental menurun.

Indikasi kecemasan sering tidak disadari oleh siswa, guru, maupun orang tua. Identifikasi masih bergantung pada observasi guru Bimbingan Konseling (BK). Cara ini punya tiga keterbatasan:

1. **Kapasitas terbatas.** Jumlah guru BK jauh lebih sedikit daripada siswa, sehingga penjaringan menyeluruh sulit dilakukan secara rutin.
2. **Reaktif.** Penanganan biasanya dimulai setelah gejala jelas atau prestasi sudah turun.
3. **Subjektif.** Pilihan bentuk penanganan sering bergantung pada pengalaman pribadi, tanpa dasar multikriteria yang terdokumentasi dan dapat ditelusuri.

Padahal data tentang kebiasaan belajar, tidur, aktivitas fisik, tekanan keluarga, dan kelelahan dapat dikumpulkan dengan kuesioner singkat. Data ini dapat diolah dengan **data mining** untuk memperkirakan tingkat kecemasan, lalu dengan **Sistem Pendukung Keputusan (SPK)** untuk menentukan siapa yang ditangani lebih dulu dan penanganan apa yang paling sesuai.

> **Catatan etis.** Sistem ini adalah alat bantu **skrining dan pendukung keputusan**, bukan alat diagnosis klinis. Keputusan akhir tetap pada guru BK dan/atau tenaga profesional.

## 1.2 Tujuan Bisnis

Membangun aplikasi web yang membantu guru BK:

1. **Mendeteksi dini** siswa dengan indikasi kecemasan tinggi dari data kuesioner, tanpa menanyakan gejala secara langsung.
2. **Menyusun prioritas** siswa yang perlu ditangani lebih dulu, sehingga waktu BK yang terbatas dipakai secara adil dan terukur.
3. **Merekomendasikan bentuk penanganan** dari lima alternatif, lengkap dengan alasan yang dapat dijelaskan kepada siswa dan orang tua.

| Kode | Alternatif penanganan | Keterangan |
|---|---|---|
| A1 | Sleep (Tidur) | Program perbaikan pola tidur (*sleep hygiene*) dan jadwal malam |
| A2 | Exercise (Olahraga) | Program aktivitas fisik terjadwal |
| A3 | Study (Strategi belajar) | Pelatihan manajemen waktu dan strategi belajar |
| A4 | Counseling (Konseling) | Konseling individual dengan guru BK; rujukan profesional bila perlu |
| A5 | Relaxation (Relaksasi) | Latihan pernapasan, *mindfulness*, manajemen stres |

## 1.3 Tujuan Data Mining

| Kode | Tujuan | Teknik |
|---|---|---|
| DM-1 | Memprediksi skor kecemasan (0–10) dari faktor gaya hidup dan akademik | Regresi *Random Forest* |
| DM-2 | Mengidentifikasi faktor yang paling berpengaruh terhadap skor kecemasan | *Feature importance* (Gini) dan korelasi |
| DM-3 | Menyediakan input kriteria SPK: prediksi kecemasan menjadi salah satu kriteria SMART | Integrasi RF → SMART |
| DM-4 | Menyesuaikan model dengan populasi sasaran (siswa SMA) | Pelatihan ulang pada data kuesioner riil |

**Titik temu Data Mining dan SPK.** Data mining bekerja pada tahap *diagnosis* (seberapa tinggi indikasi kecemasan dan faktor apa yang dominan). SMART bekerja pada tahap *preskripsi* (siapa lebih dulu dan penanganan apa yang paling tepat).

## 1.4 Faktor dan Kriteria

Delapan kriteria SMART diturunkan dari faktor penyebab kecemasan:

| Kriteria | Jenis | Makna "membutuhkan perhatian" |
|---|---|---|
| Prediksi kecemasan (RF) | benefit | makin tinggi makin butuh |
| Jam belajar per hari | benefit | beban belajar panjang |
| Nilai rata-rata rapor | cost | makin rendah makin butuh |
| Jam tidur | cost | makin sedikit makin butuh |
| Hari olahraga per minggu | cost | makin jarang makin butuh |
| Tekanan finansial | benefit | makin tinggi makin butuh |
| Ekspektasi keluarga | benefit | makin tinggi makin butuh |
| Skor kelelahan (*burnout*) | benefit | makin tinggi makin butuh |

Dalam proyek ini, **benefit** berarti nilai tinggi menaikkan utilitas, sehingga siswa lebih diprioritaskan. **Cost** berarti nilai rendah yang menaikkan utilitas.

## 1.5 Kriteria Keberhasilan

### 1.5.1 Data Mining

| Kode | Kriteria | Target | Hasil |
|---|---|---|---|
| D1 | Model lebih baik dari baseline rata-rata | MAE < baseline | Tercapai (0,767 vs 1,237 pada data uji Kaggle) |
| D2 | Daya jelaskan model | R² ≥ 0,60 | Tercapai (0,614 pada data uji Kaggle) |
| D3 | Faktor dominan masuk akal secara teori | Faktor stres/kelelahan di peringkat atas | Tercapai (stres 0,43, *burnout* 0,30) |
| D4 | Kinerja pada data riil | MAE lebih rendah dari model Kaggle tanpa latih ulang | ⟦ISI dari laporan data riil⟧ |

### 1.5.2 SPK

| Kode | Kriteria | Target | Hasil |
|---|---|---|---|
| S1 | Stabilitas terhadap perubahan bobot | ≥ 90% rekomendasi utama tetap saat bobot diubah acak ±10% | Profil A: 94,6%; profil B: 88,8% |
| S2 | Setiap rekomendasi dapat dijelaskan | 100% hasil disertai kontribusi kriteria dan alasan | Tercapai di aplikasi |
| S3 | Aturan pengaman | Siswa berisiko tinggi selalu mendapat rujukan konseling | Tercapai (10% prediksi tertinggi) |
| S4 | Kebergunaan | Skor rata-rata evaluasi pengguna (Google Form, skala 1–5) ≥ 4 | ⟦ISI setelah uji pengguna⟧ |

## 1.6 Rencana Proyek

| Fase | Aktivitas | Keluaran |
|---|---|---|
| 1. Business Understanding | Merumuskan masalah, tujuan, kriteria, dan alternatif | Dokumen ini |
| 2. Data Understanding | Memahami dataset Kaggle dan kuesioner riil | Kamus data, statistik deskriptif |
| 3. Data Preparation | Sampling, encoding, pemetaan kuesioner → fitur, pembagian data | Dataset siap model |
| 4. Modeling | Random Forest, pelatihan ulang, SMART | Model + matriks keputusan |
| 5. Evaluation | Metrik regresi, perbandingan algoritma, sensitivitas bobot, keadilan | Laporan evaluasi |
| 6. Deployment | Aplikasi Streamlit bilingual di Streamlit Community Cloud | Aplikasi daring + panduan |


[[PAGEBREAK]]

# 2. Data Understanding




---

## 2.1 Sumber Data

Proyek memakai dua sumber data dengan peran berbeda.

| Aspek | Data pralatih (Kaggle) | Data riil (kuesioner) |
|---|---|---|
| Sumber | Kaggle `sharmajicoder/student-mental-health-and-burnout`, berkas `student_mental_health_burnout_1M.csv` | Google Form yang disebarkan tim ke siswa SMA |
| Ukuran asli | 1.000.000 baris × 20 kolom | ⟦ISI: jumlah respons⟧ baris × ±50 kolom |
| Yang dipakai | Sampel acak 2% = **20.000 baris** (`random_state=42`) | Seluruh respons valid setelah pembersihan |
| Populasi | Mahasiswa, usia 17–29 | Siswa SMA, usia ±15–18 |
| Peran | Pralatih model; populasi referensi SPK | Pelatihan ulang dan pengujian model |
| Kerahasiaan | Publik | **Rahasia**: tidak masuk repositori |

Alasan dua sumber: data Kaggle besar dan lengkap sehingga cocok untuk membangun model awal, tetapi populasinya bukan siswa SMA. Data kuesioner sesuai populasi sasaran, tetapi jumlahnya kecil. Model dilatih lebih dulu pada Kaggle, lalu disesuaikan dengan data kuesioner.

## 2.2 Deskripsi Data Kaggle (20.000 baris)

Tidak ada nilai hilang dan tidak ada baris duplikat pada sampel.

| Atribut | Tipe | Rata-rata | Std | Min | Median | Maks | Peran |
|---|---|---|---|---|---|---|---|
| age | numerik | 23,01 | 3,75 | 17 | 23 | 29 | fitur |
| gender | kategorikal | Female 9.632 · Male 9.561 · Other 807 | | | | | fitur |
| academic_year | ordinal | 2,51 | 1,12 | 1 | 3 | 4 | tidak dipakai |
| study_hours_per_day | numerik | 5,03 | 1,97 | 0,00 | 5,01 | 13,23 | fitur + kriteria |
| exam_pressure | numerik | 6,01 | 1,55 | 1,00 | 6,02 | 10,00 | fitur |
| academic_performance | numerik | 71,10 | 5,66 | 47,56 | 71,10 | 92,89 | fitur + kriteria |
| stress_level | numerik | 4,27 | 1,67 | 0,00 | 4,27 | 10,00 | fitur |
| **anxiety_score** | numerik | 3,01 | 1,52 | 0,00 | 2,98 | 9,11 | **target** |
| depression_score | numerik | 1,28 | 1,22 | 0,00 | 1,05 | 7,86 | tidak dipakai (hasil) |
| sleep_hours | numerik | 6,50 | 1,49 | 3,00 | 6,50 | 10,00 | fitur + kriteria |
| physical_activity | numerik | 3,02 | 1,47 | 0,00 | 3,00 | 7,00 | fitur + kriteria |
| social_support | numerik | 5,01 | 1,98 | 0,00 | 5,00 | 10,00 | tidak dipakai |
| screen_time | numerik | 5,04 | 1,95 | 1,00 | 5,02 | 12,00 | tidak dipakai |
| internet_usage | numerik | 5,06 | 2,14 | 1,00 | 5,04 | 13,70 | tidak dipakai |
| financial_stress | numerik | 5,00 | 1,99 | 0,00 | 4,99 | 10,00 | fitur + kriteria |
| family_expectation | numerik | 6,00 | 1,94 | 0,00 | 6,02 | 10,00 | fitur + kriteria |
| burnout_score | numerik | 1,79 | 1,67 | 0,00 | 1,51 | 9,85 | fitur + kriteria |
| mental_health_index | numerik | 7,01 | 1,31 | 2,02 | 7,06 | 10,00 | tidak dipakai (hasil) |
| risk_level | kategorikal | Low 15.321 · Medium 4.376 · High 303 | | | | | tidak dipakai (hasil) |
| dropout_risk | numerik | 1,33 | 1,35 | 0,00 | 1,00 | 8,56 | tidak dipakai (hasil) |

### 2.2.1 Korelasi dengan skor kecemasan

| Atribut | r (Pearson) | Atribut | r (Pearson) |
|---|---|---|---|
| stress_level | 0,761 | study_hours_per_day | 0,272 |
| burnout_score | 0,674 | family_expectation | 0,260 |
| depression_score | 0,474 | academic_performance | 0,056 |
| dropout_risk | 0,470 | physical_activity | −0,122 |
| financial_stress | 0,360 | sleep_hours | −0,205 |
| exam_pressure | 0,351 | mental_health_index | −0,869 |

Temuan penting:

- `stress_level` dan `burnout_score` paling kuat berhubungan dengan kecemasan.
- `mental_health_index`, `depression_score`, `dropout_risk`, dan `risk_level` adalah **variabel hasil** yang sangat terkait dengan target. Memakainya sebagai fitur menimbulkan *label leakage*, jadi keempatnya dikeluarkan.
- `social_support`, `screen_time`, dan `internet_usage` hampir tidak berkorelasi (|r| < 0,01) sehingga tidak dipakai.
- `academic_year` tidak berlaku untuk siswa SMA dan juga tidak berkorelasi.

## 2.3 Deskripsi Data Kuesioner

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
| **Psikologis** | gugup/cemas, sulit mengendalikan khawatir, konsentrasi (dibalik), pikiran terganggu, sulit menyelesaikan tugas | **target skor kecemasan** |
| Pola makan | uang saku cukup, jajan, minuman manis/berkafein, makan saat tertekan, melewatkan makan | tekanan finansial (+ ekstra) |

"Ekstra" berarti butir disimpan untuk analisis korelasi dan satu eksperimen model yang diperluas. Butir ini tidak dipakai model yang dideploy, karena model harus tetap sejajar dengan 11 fitur Kaggle.

### 2.3.1 Statistik data kuesioner

⟦ISI dari `app/models/real_summary.json` dan `app/reports/private/real_data_report.md` setelah pipeline dijalankan: jumlah respons, jumlah baris bersih, duplikat, *straight-lining*, sebaran gender, statistik tiap fitur, korelasi fitur dan butir ekstra dengan skor kecemasan.⟧

## 2.4 Kualitas Data

| Dimensi | Kaggle | Kuesioner (pemeriksaan otomatis `spk/gform.py`) |
|---|---|---|
| Kelengkapan | 0 nilai hilang | nilai hilang per fitur dilaporkan; diisi median data latih |
| Duplikat | 0 | baris jawaban identik dibuang |
| Validitas | rentang wajar | nilai di luar rentang (mis. rapor > 100) dikosongkan; jawaban yang tidak dikenali dilaporkan |
| Kesungguhan | – | *straight-lining* (semua Likert sama) dihitung |
| Privasi | tidak ada data pribadi | kolom pribadi dibuang segera setelah usia dihitung |

## 2.5 Keterbatasan

- Dataset Kaggle kemungkinan besar sintetis dan berasal dari mahasiswa, bukan siswa SMA. Karena itu model dilatih ulang dengan data riil.
- Tingkat stres dan tekanan finansial pada kuesioner adalah **proksi**, sehingga maknanya tidak identik dengan kolom Kaggle.
- Data kuesioner bersifat *self-report* dan *cross-sectional*: rawan bias sosial dan tidak menunjukkan sebab-akibat.
- Sampel kuesioner tidak acak (disebar lewat sekolah, media sosial, dan teman), sehingga generalisasinya terbatas.


[[PAGEBREAK]]

# 3. Data Preparation




---

## 3.1 Ringkasan Langkah

| # | Langkah | Data Kaggle | Data kuesioner | Kode |
|---|---|---|---|---|
| 1 | Sampling | 1 juta → 20.000 (2%), lalu 10.000 (50%) untuk RF | seluruh respons | `spk/data.py`, `spk/model.py::split` |
| 2 | Seleksi atribut | 11 fitur + target; buang variabel hasil | petakan ±50 kolom ke *field* | `config.FEATURES`, `gform_mapping.json` |
| 3 | Pembersihan | tidak ada nilai hilang/duplikat | duplikat, rentang, jawaban tak dikenal, data pribadi | `spk/gform.py` |
| 4 | Encoding | `gender` → kode tetap | teks jawaban → angka | `data.encode_gender`, `gform.encode` |
| 5 | Konstruksi fitur | – | 11 fitur skala Kaggle + target | `gform.derive` |
| 6 | Imputasi | – | median data latih | `gform.impute` |
| 7 | Pembagian data | 80% latih / 20% uji | 80% pengembangan / 20% *holdout* + CV 5-fold ×2 | `model.split`, `spk/retrain.py` |

## 3.2 Data Kaggle

### 3.2.1 Sampling

Berkas 1 juta baris terlalu besar untuk Google Colab dan deployment, jadi diambil sampel acak **2% (20.000 baris)** dengan `random_state=42`. Sampel ini disimpan sebagai `app/data/dataset.csv`. Untuk melatih RF, diambil lagi **50% (10.000 baris)**.

### 3.2.2 Seleksi atribut

- **Target:** `anxiety_score`.
- **Fitur (11):** `age`, `gender`, `study_hours_per_day`, `academic_performance`, `exam_pressure`, `stress_level`, `sleep_hours`, `physical_activity`, `financial_stress`, `family_expectation`, `burnout_score`.
- **Dibuang:** `depression_score`, `mental_health_index`, `risk_level`, `dropout_risk` (variabel hasil → *leakage*); `social_support`, `screen_time`, `internet_usage` (korelasi ≈ 0); `academic_year` (tidak berlaku untuk SMA).

### 3.2.3 Encoding

`gender` dikodekan dengan pemetaan tetap `Female=0, Male=1, Other=2`. Pemetaan ini sama dengan hasil `LabelEncoder` pada notebook (urutan alfabet). Pemetaan ditulis eksplisit di `config.GENDER_MAP` agar aplikasi tidak bergantung pada objek encoder yang tersimpan.

Random Forest tidak memerlukan normalisasi fitur, sehingga fitur numerik dipakai apa adanya.

### 3.2.4 Pembagian data

Dari 10.000 baris: **8.000 latih** dan **2.000 uji** (`test_size=0.2`, `random_state=42`). Rata-rata target pada data latih 3,00 dan pada data uji 3,07, jadi sebaran keduanya seimbang.

## 3.3 Data Kuesioner (Google Form)

### 3.3.1 Pencocokan kolom

Ekspor Google Form memakai judul pertanyaan sebagai nama kolom. Pertanyaan grid tertulis sebagai `Judul grid [teks baris]`. Berkas `spk/gform_mapping.json` mencocokkan setiap *field* dengan potongan teks pertanyaan. Beberapa judul dipakai dua kali di formulir, misalnya "Rata-Rata Jam Belajar Per Hari" dan "Target pengumpulan tugas". Untuk kasus ini, sistem memilih kolom yang jawabannya paling banyak dapat dibaca oleh *parser* field tersebut. Skrip `scripts/inspect_gform.py` menampilkan hasil pencocokan sebelum pelatihan.

### 3.3.2 Pembersihan

- **Data pribadi dibuang:** *timestamp*, tanggal lahir, nama sekolah, sumber informasi, nama teman, dan email. Pembuangan terjadi segera setelah usia dihitung. Setiap baris diberi ID anonim `R0001…`.
- **Duplikat:** baris dengan jawaban identik dibuang.
- **Rentang:** nilai rapor di luar 0–100 dan jam di luar rentang pertanyaan dikosongkan.
- **Jawaban tak dikenal** dihitung dan dicontohkan di laporan privat agar pemetaan dapat diperbaiki.
- ***Straight-lining***: jumlah baris dengan semua jawaban Likert sama dilaporkan.

### 3.3.3 Encoding jawaban

| Jenis jawaban | Contoh | Menjadi |
|---|---|---|
| Rentang jam | "Dibawah 30 menit", "1 jam 30 menit", "12 jam" | 0,25 · 1,5 · 12 |
| Likert frekuensi | Tidak pernah … Sangat sering | 1 … 5 |
| Likert persetujuan | Sangat tidak setuju … Sangat setuju | 1 … 5 |
| Ordinal 4 tingkat | Tidak pernah / 1 kali / 2-3 kali / 4-5 kali | 1 … 4 |
| Hari olahraga | 0 / 1-2 / 3-4 / 5-6 / 7 hari | 0 · 1,5 · 3,5 · 5,5 · 7 (titik tengah) |
| Jenis kelamin | Laki-laki / Perempuan | Male / Female |

*Parser* juga menerima variasi penulisan: huruf besar/kecil, tanda pisah "–" atau "-", dan nomor urut di depan opsi.

### 3.3.4 Konstruksi fitur (pemetaan ke skala Kaggle)

Agar model Kaggle dapat dipakai dan dilatih ulang, jawaban kuesioner diubah ke rentang yang sama dengan fitur Kaggle. `unit(x)` berarti skala ordinal 1…n dipetakan ke 0…1.

| Fitur model | Rumus |
|---|---|
| age | ⌊(timestamp − tanggal lahir) / 365,25⌋ |
| gender | jenis kelamin |
| study_hours_per_day | jam belajar (jam) |
| academic_performance | nilai rata-rata rapor |
| exam_pressure | 1 + (tertekan ujian − 1) × 9/4 → 1–10 |
| stress_level | 10 × rata-rata unit(tugas bersamaan, waktu tidak cukup, tugas terlambat, belajar larut malam) |
| sleep_hours | durasi tidur (jam) |
| physical_activity | hari olahraga per minggu |
| financial_stress | 10 × (5 − uang saku cukup) / 4 (dibalik) |
| family_expectation | 10 × rata-rata unit(takut mengecewakan orang tua, tuntutan nilai keluarga) |
| burnout_score | 10 × rata-rata unit(sulit membagi waktu, kelelahan, kehilangan minat) |
| **anxiety_score** (target) | [Σ(P − 1) untuk P01, P02, P04, P05 + (5 − P03)] / 2 → 0–10 |

Lima butir Psikologis (P01–P05) hanya membentuk target dan **tidak pernah** menjadi fitur, sehingga tidak ada *label leakage*. Rumus diuji otomatis di `tests/test_gform.py`.

### 3.3.5 Imputasi

Fitur yang kosong diisi median data kuesioner. Untuk gender, dipakai modus. Nilai median disimpan di metadata model (`impute_medians`), sehingga unggahan baru di aplikasi diisi dengan nilai yang sama persis. Baris tanpa target dibuang dari pelatihan.

### 3.3.6 Pembagian data

- **80% pengembangan dan 20% holdout** (`random_state=42`) bila respons ≥ 30.
- Pada data pengembangan dijalankan ***repeated k-fold cross-validation*** (5 lipatan × 2 ulangan) untuk memilih strategi pelatihan ulang (Fase 4).
- Model akhir dilatih ulang pada seluruh respons dengan strategi terpilih.

⟦ISI dari laporan data riil: jumlah baris mentah → bersih, jumlah pengembangan/holdout, jumlah nilai yang diimputasi.⟧

## 3.4 Penyiapan Data untuk SMART

Matriks keputusan berisi 8 kriteria untuk setiap siswa: 7 fitur langsung ditambah `rf_anxiety_score` hasil prediksi RF. Normalisasi utilitas membutuhkan min dan maks tiap kriteria. Batas ini dihitung dari populasi referensi saat pelatihan dan disimpan di metadata (`smart_bounds`), agar satu siswa pun dapat dinilai. Batas diambil dari data Kaggle 20.000 baris, atau dari data riil bila respons ≥ 50.

## 3.5 Keluaran Fase

| Berkas | Isi | Di repositori? |
|---|---|---|
| `app/data/dataset.csv` | 20.000 baris sampel Kaggle | ya |
| `app/data/private/gform_raw.csv` | ekspor kuesioner mentah | **tidak** (gitignore) |
| `app/data/sample_gform.csv` | 250 baris ekspor **sintetis** untuk uji dan demo | ya |
| metadata model | `smart_bounds`, `impute_medians`, `gender_map` | ya |


[[PAGEBREAK]]

# 4. Modeling




---

## 4.1 Gambaran Umum

| Modul | Teknik | Masukan | Keluaran |
|---|---|---|---|
| M1 — Prediksi (Data Mining) | Random Forest Regressor | 11 fitur siswa | `rf_anxiety_score` (0–10) |
| M2 — Faktor dominan | *Gini feature importance* | model M1 | peringkat faktor |
| M3 — Pelatihan ulang | 7 strategi transfer Kaggle → data riil | model M1 + data kuesioner | model aktif |
| M4 — Keputusan (SPK) | SMART | 7 fitur + `rf_anxiety_score` | skor prioritas, peringkat 5 alternatif |

Alur: **fitur siswa → RF → prediksi kecemasan → SMART → prioritas + rekomendasi**. Prediksi RF menjadi salah satu kriteria SMART. Di titik inilah Data Mining dan SPK terintegrasi.

## 4.2 M1 — Random Forest Regressor

### 4.2.1 Alasan pemilihan

Target (`anxiety_score`) kontinu, jadi masalahnya adalah **regresi**. Random Forest dipilih karena:

- Menangkap hubungan non-linear dan interaksi antarfaktor tanpa asumsi bentuk hubungan.
- Tahan terhadap *outlier* dan skala fitur yang berbeda, tanpa normalisasi.
- Menyediakan *feature importance* untuk penjelasan.
- Cocok untuk jawaban kuesioner ordinal dan data berukuran kecil, dengan *bagging* yang mengurangi *overfitting*.

### 4.2.2 Konfigurasi parameter

| Parameter | Nilai | Alasan |
|---|---|---|
| `n_estimators` | 200 | cukup banyak pohon agar prediksi stabil; waktu latih ±0,3 detik |
| `max_depth` | 10 | membatasi kedalaman agar tidak menghafal data latih |
| `min_samples_split` | 2 | bawaan scikit-learn |
| `min_samples_leaf` | 2 (3 untuk data riil) | daun minimal 2–3 sampel: mengurangi *overfitting* dan hafalan data pribadi |
| `max_features` | `"sqrt"` | tiap pemisahan hanya melihat √11 ≈ 3 fitur, sehingga pohon lebih beragam |
| `random_state` | 42 | hasil dapat direproduksi |
| `n_jobs` | −1 | memakai semua inti CPU |

Model dilatih pada 8.000 baris latih Kaggle (Fase 3) dan disimpan sebagai `app/models/rf_anxiety_model.joblib`, dengan metadata di `rf_anxiety_model_metadata.json`.

### 4.2.3 Perbandingan dengan algoritma lain

Semua algoritma dilatih pada data latih yang sama dengan validasi silang 5-fold, lalu diuji pada data uji yang sama (`scripts/train.py --stage compare`).

| Algoritma | MAE CV | RMSE CV | R² CV | MAE uji | R² uji |
|---|---|---|---|---|---|
| Baseline rata-rata | 1,2238 | 1,5134 | −0,0010 | 1,2370 | −0,0024 |
| Regresi linear | **0,7684** | **0,9549** | **0,6014** | **0,7548** | **0,6245** |
| Decision Tree (kedalaman 10) | 0,8814 | 1,1127 | 0,4583 | 0,8672 | 0,4955 |
| Gradient Boosting | 0,7728 | 0,9616 | 0,5958 | 0,7667 | 0,6155 |
| **Random Forest (dipakai)** | 0,7790 | 0,9663 | 0,5918 | 0,7668 | 0,6136 |

Pada data Kaggle, regresi linear sedikit lebih akurat. Selisih MAE-nya 0,01 poin pada skala 0–10. Hal ini wajar karena data Kaggle tampak sintetis dengan hubungan yang hampir linear. RF tetap dipakai karena:

1. Kinerjanya setara, jauh lebih baik dari baseline dan dari pohon tunggal.
2. Data kuesioner riil berbentuk ordinal dan tidak dijamin linear.
3. Metode pelatihan ulang dengan *warm start* (M3) memerlukan model *ensemble* pohon.

### 4.2.4 M2 — Faktor dominan

| Peringkat | Fitur | *Importance* |
|---|---|---|
| 1 | stress_level | 0,4268 |
| 2 | burnout_score | 0,3036 |
| 3 | financial_stress | 0,0630 |
| 4 | exam_pressure | 0,0493 |
| 5 | family_expectation | 0,0386 |
| 6 | study_hours_per_day | 0,0327 |
| 7 | sleep_hours | 0,0273 |
| 8 | physical_activity | 0,0228 |
| 9 | academic_performance | 0,0211 |
| 10 | age | 0,0113 |
| 11 | gender | 0,0035 |

Tingkat stres dan kelelahan menyumbang 73% kepentingan, sejalan dengan korelasi di Fase 2. Gender hampir tidak berpengaruh (0,35%), sehingga risiko bias gender kecil (diperiksa di Fase 5).

## 4.3 M3 — Pelatihan Ulang dengan Data Riil

Tujuannya adalah menyesuaikan model dari populasi mahasiswa (Kaggle) ke siswa SMA (kuesioner). Tujuh strategi dibandingkan (`spk/retrain.py`):

| Kode | Strategi | Penjelasan |
|---|---|---|
| S0 | Kaggle saja | model M1 tanpa pelatihan ulang (pembanding) |
| S1 | Data riil saja | RF baru hanya dari kuesioner (`min_samples_leaf=3`) |
| S2 (w = 1, 10, 50) | Gabungan berbobot | 8.000 baris Kaggle + data riil; tiap baris riil diberi bobot w |
| S3 (+200, +600) | *Warm start* | 200 pohon Kaggle dipertahankan, lalu ditambah 200 atau 600 pohon baru yang dilatih pada data riil |
| S4 | Data riil diperluas | S1 ditambah butir ekstra kuesioner (media sosial, pertemanan, pola makan, dll.); hanya dilaporkan, tidak dideploy |

Strategi dengan **MAE validasi silang terendah** di antara S0–S3 dipilih, lalu dilatih ulang pada seluruh respons. Hasilnya disimpan sebagai `rf_real_model.joblib`, dan aplikasi otomatis memakainya.

⟦ISI dari `reports/private/real_data_report.md`: tabel MAE/RMSE/R² CV dan holdout untuk S0–S4, strategi terpilih, *feature importance* model aktif.⟧

## 4.4 M4 — SMART

### 4.4.1 Langkah

1. **Matriks keputusan.** Setiap siswa memiliki 8 nilai kriteria (Fase 1 §4).
2. **Utilitas** (normalisasi min–maks memakai batas referensi):
   - benefit: `u = (x − min) / (max − min)`
   - cost: `u = (max − x) / (max − min)`
   - Nilai di luar batas dipotong ke rentang 0–1.
3. **Skor prioritas:** `P = Σ wⱼ uⱼ` dengan bobot sama `wⱼ = 1/8`. Siswa diurutkan dengan `rank(method="dense")` dari skor tertinggi.
4. **Skor tiap alternatif:** `Sₐ = Σ wₐⱼ uⱼ`, dengan bobot khusus alternatif a (tabel 4.2).
5. **Rekomendasi:** alternatif dengan Sₐ tertinggi; aplikasi menampilkan tiga teratas.
6. **Aturan pengaman:** bila prediksi kecemasan ≥ persentil 90 populasi referensi, konseling dan rujukan selalu ditampilkan.

### 4.4.2 Profil bobot

**Profil A — berbasis domain.** Setiap alternatif menekankan kriteria yang paling relevan dengannya. Contohnya, Sleep menekankan jam tidur dan Study menekankan jam belajar serta nilai. Di notebook, bobot Exercise berjumlah **1,05**, padahal SMART mensyaratkan Σw = 1. Aplikasi menormalkannya dengan membagi setiap bobot Exercise dengan 1,05.

| Kriteria | Sleep | Exercise* | Study | Counseling | Relaxation |
|---|---|---|---|---|---|
| Prediksi kecemasan | 0,15 | 0,143 | 0,10 | 0,30 | 0,20 |
| Jam belajar | 0,10 | 0,048 | 0,40 | 0,05 | 0,05 |
| Nilai rapor | 0,10 | 0,048 | 0,30 | 0,05 | 0,05 |
| Jam tidur | 0,40 | 0,048 | 0,00 | 0,05 | 0,20 |
| Aktivitas fisik | 0,05 | 0,429 | 0,00 | 0,05 | 0,10 |
| Tekanan finansial | 0,05 | 0,048 | 0,05 | 0,20 | 0,15 |
| Ekspektasi keluarga | 0,05 | 0,048 | 0,05 | 0,15 | 0,15 |
| *Burnout* | 0,10 | 0,190 | 0,10 | 0,15 | 0,10 |

\*setelah normalisasi (notebook: 0,15 / 0,05 / 0,05 / 0,05 / 0,45 / 0,05 / 0,05 / 0,20).

**Profil B — hampir seimbang.** Kriteria utama tiap alternatif mendapat 0,15–0,20, dan kriteria lain 0,10.

**Profil C — sama rata (kontrol).** Semua bobot 1/8. Karena kelima alternatif memakai bobot yang sama, semua skor seri. `idxmax` lalu selalu memilih alternatif pertama (Sleep). Profil C hanya menjadi pembanding.

### 4.4.3 Contoh perhitungan (siswa STU00004, profil A)

Siswa laki-laki, 17 tahun. Batas min/maks dari 20.000 siswa referensi.

| Kriteria | Nilai x | Min | Maks | Jenis | Utilitas u |
|---|---|---|---|---|---|
| Prediksi kecemasan | 4,417 | 0,367 | 7,091 | benefit | 0,602 |
| Jam belajar | 5,594 | 0,000 | 13,227 | benefit | 0,423 |
| Nilai rapor | 68,375 | 47,565 | 92,894 | cost | 0,541 |
| Jam tidur | 3,146 | 3,000 | 10,000 | cost | 0,979 |
| Aktivitas fisik | 2,539 | 0,000 | 7,000 | cost | 0,637 |
| Tekanan finansial | 7,278 | 0,000 | 10,000 | benefit | 0,728 |
| Ekspektasi keluarga | 2,577 | 0,000 | 10,000 | benefit | 0,258 |
| *Burnout* | 4,609 | 0,000 | 9,855 | benefit | 0,468 |

Contoh utilitas jam tidur (cost): u = (10,000 − 3,146) / (10,000 − 3,000) = 0,979.

**Skor prioritas** P = (0,602 + 0,423 + 0,541 + 0,979 + 0,637 + 0,728 + 0,258 + 0,468) / 8 = **0,580**, lebih tinggi dari 93% siswa referensi.

**Skor alternatif** (Σ bobot × utilitas):

| Peringkat | Alternatif | Skor | Kontribusi terbesar |
|---|---|---|---|
| 1 | **Sleep** | **0,706** | jam tidur 0,40 × 0,979 = 0,392 |
| 2 | Relaxation | 0,623 | jam tidur 0,196; prediksi kecemasan 0,121 |
| 3 | Exercise | 0,588 | aktivitas fisik 0,273 |
| 4 | Counseling | 0,564 | prediksi kecemasan 0,181; tekanan finansial 0,146 |
| 5 | Study | 0,488 | jam belajar 0,169; nilai rapor 0,162 |

Penjelasan yang dihasilkan aplikasi: *"Tidur mendapat skor tertinggi (0,706). Pendorong utama: jam tidur sedikit (3,1 jam), prediksi kecemasan tinggi (4,4/10), nilai rapor rendah (68). Selisih dengan alternatif kedua (Relaksasi) 0,083."*

### 4.4.4 Hasil pada populasi referensi (20.000 siswa)

| Alternatif | Profil A (notebook, Σ=1,05) | Profil A (dinormalkan) | Profil B |
|---|---|---|---|
| Sleep | 4.796 | 5.356 | 5.662 |
| Exercise | 8.866 | 6.905 | 4.673 |
| Study | 2.323 | 2.613 | 1.940 |
| Counseling | 1.863 | 2.202 | 7.553 |
| Relaxation | 2.152 | 2.924 | 172 |

Normalisasi menurunkan dominasi Exercise dari 44% menjadi 35%. Profil B lebih banyak merekomendasikan Counseling. Counseling memberi bobot 0,20 pada prediksi kecemasan dan 0,15 pada tekanan finansial serta ekspektasi keluarga. Ekspektasi keluarga rata-rata tinggi pada populasi ini (6,0 dari 10), sehingga skor Counseling ikut terangkat.

## 4.5 Keluaran Fase

| Berkas | Isi |
|---|---|
| `app/models/rf_anxiety_model.joblib` + metadata | model dasar (Kaggle), metrik, batas SMART |
| `app/models/model_comparison.json` | perbandingan 5 algoritma |
| `app/models/rf_real_model.joblib` + metadata + `real_summary.json` | model aktif setelah data riil (agregat saja) |
| `app/spk/smart.py`, `config.py` | implementasi SMART dan profil bobot |


[[PAGEBREAK]]

# 5. Evaluation




---

## 5.1 Kerangka Evaluasi

| Lapis | Pertanyaan | Metode |
|---|---|---|
| Teknis (Data Mining) | Seberapa akurat prediksi skor kecemasan? | MAE, MSE, RMSE, R², perbandingan algoritma, analisis galat |
| Keputusan (SPK) | Apakah rekomendasi stabil dan masuk akal? | Uji sensitivitas bobot, perbandingan profil, contoh kasus |
| Etika | Apakah hasil adil antar kelompok? | MAE dan sebaran rekomendasi per gender |
| Bisnis | Apakah tujuan Fase 1 tercapai? | Kriteria keberhasilan, evaluasi pengguna |

## 5.2 Metrik Regresi

Masalahnya regresi, jadi metrik yang dipakai:

| Metrik | Rumus | Arti |
|---|---|---|
| MAE | (1/n) Σ \|y − ŷ\| | rata-rata selisih absolut, dalam satuan skor (0–10) |
| MSE | (1/n) Σ (y − ŷ)² | menghukum kesalahan besar |
| RMSE | √MSE | seperti MSE, dalam satuan skor |
| R² | 1 − SS_res / SS_tot | porsi variasi target yang dijelaskan model |

### 5.2.1 Model dasar (Kaggle), data uji 2.000 baris

| MAE | MSE | RMSE | R² |
|---|---|---|---|
| **0,7668** | 0,9112 | 0,9546 | **0,6136** |

Rata-rata prediksi meleset ±0,77 poin pada skala 0–10, dan model menjelaskan 61% variasi skor kecemasan. Hasil ini sama persis dengan notebook Colab, yang diverifikasi otomatis di `tests/test_smart.py`.

### 5.2.2 Analisis galat

- Grafik aktual vs prediksi (halaman Analisis) menunjukkan titik mengikuti garis diagonal. Prediksi untuk skor ekstrem cenderung **ditarik ke tengah**: rentang prediksi 0,37–7,09, sedangkan rentang aktual 0–9,11. Ini sifat umum Random Forest, yang merata-ratakan pohon.
- Konsekuensinya, siswa dengan kecemasan sangat tinggi dapat terprediksi lebih rendah dari sebenarnya. Karena itu aturan pengaman memakai **persentil** (10% prediksi tertinggi), bukan ambang absolut.

### 5.2.3 Perbandingan algoritma

Lihat Fase 4 §2.3. RF setara dengan regresi linear dan gradient boosting (selisih MAE ≤ 0,012), jauh lebih baik dari baseline (MAE 1,237) dan pohon tunggal (MAE 0,867).

### 5.2.4 Pelatihan ulang dan pengujian pada data riil

| Uji | Data | Hasil |
|---|---|---|
| Pemilihan strategi | CV 5-fold × 2 pada 80% data kuesioner | ⟦ISI: MAE CV per strategi⟧ |
| *Holdout* | 20% data kuesioner yang tidak dipakai memilih | ⟦ISI: MAE/RMSE/R² model terpilih vs model Kaggle (S0)⟧ |
| Data baru | respons yang masuk setelah pelatihan (`scripts/evaluate.py` atau unggah di aplikasi) | ⟦ISI⟧ |

Kriteria D4 (Fase 1) tercapai bila MAE model terpilih lebih rendah dari S0 pada *holdout*.

## 5.3 Evaluasi Modul Keputusan (SMART)

### 5.3.1 Sensitivitas bobot

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

### 5.3.2 Perbandingan profil

| Alternatif | A (dinormalkan) | B | C |
|---|---|---|---|
| Sleep | 5.356 | 5.662 | 20.000 |
| Exercise | 6.905 | 4.673 | 0 |
| Study | 2.613 | 1.940 | 0 |
| Counseling | 2.202 | 7.553 | 0 |
| Relaxation | 2.924 | 172 | 0 |

Profil C menunjukkan mengapa bobot khusus per alternatif diperlukan. Tanpa bobot khusus, SMART tidak dapat membedakan alternatif.

### 5.3.3 Temuan: bobot notebook tidak ternormalisasi

Pada notebook, bobot Exercise profil A berjumlah 1,05. Akibatnya skor Exercise naik 5%, dan Exercise direkomendasikan untuk 8.866 siswa (44%). Setelah dinormalkan, angkanya 6.905 siswa (35%). Aplikasi memakai versi yang dinormalkan. Uji otomatis memastikan setiap profil berjumlah 1 dan tetap dapat mereproduksi angka notebook dengan bobot aslinya.

### 5.3.4 Contoh kasus

Contoh STU00004 (Fase 4 §4.3) direkomendasikan **Sleep**. Jam tidurnya 3,1 jam, termasuk yang terendah pada populasi (utilitas 0,979). Hasil ini masuk akal secara domain. Skor prioritasnya 0,580 (persentil 93), jadi siswa ini termasuk yang perlu ditangani lebih dulu.

## 5.4 Keadilan (*Fairness*)

| Gender | n (uji) | MAE |
|---|---|---|
| Female | 964 | 0,768 |
| Male | 948 | 0,767 |
| Other | 88 | 0,751 |

Selisih MAE antar gender < 0,02 poin. Sebaran rekomendasi profil A per gender juga hampir sama: Exercise 34–35%, Sleep 25–27%, Counseling 11–13%. Jadi tidak ditemukan bias gender yang berarti. Untuk data riil, pemeriksaan yang sama dijalankan pada *holdout* ⟦ISI⟧. Kelompok dengan kurang dari 5 orang tidak ditampilkan demi privasi.

## 5.5 Evaluasi terhadap Tujuan Bisnis

| Tujuan (Fase 1) | Bukti | Status |
|---|---|---|
| Deteksi dini | prediksi skor dari faktor non-gejala; persentil terhadap populasi | tercapai |
| Prioritas siswa | skor prioritas + unggah banyak siswa + unduh daftar | tercapai |
| Rekomendasi beralasan | tiga teratas, grafik kontribusi, kalimat alasan, uji sensitivitas | tercapai |
| Sesuai populasi SMA | pelatihan ulang dengan kuesioner | ⟦ISI setelah data riil⟧ |
| Diterima pengguna | Google Form evaluasi (pemahaman, kesesuaian, manfaat, stabilitas, tampilan) | ⟦ISI setelah uji pengguna⟧ |

## 5.6 Keputusan Lanjutan

1. **Lanjut ke deployment** dengan model Kaggle sebagai model awal dan profil A sebagai bawaan.
2. Jalankan pipeline data riil begitu ekspor kuesioner tersedia, lalu perbarui metrik di laporan ini.
3. Validasi bobot profil A dengan guru BK atau psikolog, yaitu kesesuaian rekomendasi pertama pada 20–30 kasus.
4. Pengembangan lanjutan (dari rancangan awal): segmentasi siswa (*clustering*), aturan asosiasi kebiasaan, dan bobot yang diturunkan dari *feature importance*.


[[PAGEBREAK]]

# 6. Deployment




---

## 6.1 Rencana Deployment

| Aktivitas CRISP-DM | Wujud pada proyek |
|---|---|
| *Plan deployment* | Aplikasi web **Streamlit** bilingual (ID/EN), di-*hosting* gratis di **Streamlit Community Cloud** dari repositori GitHub |
| *Plan monitoring & maintenance* | Pipeline pelatihan ulang dengan data kuesioner baru; evaluasi pada data baru |
| *Produce final report* | Laporan teknis ini, panduan pengguna, presentasi |
| *Review project* | Bagian 7 |

**Mengapa Streamlit (bukan Gradio seperti rancangan awal):** antarmuka multi-halaman bawaan, komponen grafik dan tabel yang lengkap, *caching* model, dan *hosting* gratis yang langsung terhubung ke GitHub, sesuai rekomendasi rubrik proyek.

## 6.2 Arsitektur

```
 Pelatihan offline (laptop / Colab)                    Streamlit Community Cloud
 ─────────────────────────────────                     ─────────────────────────────────────────────
 Kaggle 1M ─► 20k sampel ─┐                             streamlit_app.py (navigasi, bahasa, profil bobot)
                          ├─► scripts/train.py ─► models/   │
 Google Form (rahasia) ───┘   kaggle | real |     *.joblib  ├─ Beranda
                              compare              + meta   ├─ Rekomendasi ─► spk/gform.py  (jawaban → fitur)
                                                  (agregat) │                 spk/model.py  (prediksi RF)
                                                            │                 spk/smart.py  (SMART, sensitivitas)
                                                            │                 spk/recommend.py, explain.py
                                                            ├─ Analisis    ─► spk/plots.py
                                                            └─ Tentang
```

Prinsipnya: **aplikasi tidak pernah melatih model**. Pelatihan berjalan *offline*. Aplikasi hanya memuat model `.joblib` beserta metadata (fitur, pemetaan gender, batas SMART, median imputasi, kuantil referensi) lalu melakukan inferensi. *Preprocessing* saat inferensi memakai kode dan nilai yang sama persis dengan saat pelatihan: `gform.derive`, `GENDER_MAP`, `smart_bounds`, dan `impute_medians`.

## 6.3 Struktur Kode

| Berkas | Tanggung jawab |
|---|---|
| `app/streamlit_app.py` | titik masuk, `st.navigation`, sidebar (bahasa, profil bobot, info model, penafian) |
| `app/app_pages/home.py` | masalah, pengguna, alur kerja, tombol mulai |
| `app/app_pages/recommendation.py` | input satu siswa (kuesioner/lanjutan), hasil + alasan + sensitivitas; unggah banyak siswa + evaluasi data baru |
| `app/app_pages/analysis.py` | data, model, SMART, sensitivitas, keadilan |
| `app/app_pages/about.py` | metode, arsitektur, keterbatasan, etika |
| `app/spk/*.py` | logika murni tanpa Streamlit, diuji dengan `pytest` |
| `app/scripts/*.py` | pelatihan, inspeksi kuesioner, evaluasi, data sintetis |
| `app/tests/` | 39 uji otomatis: *parsing* kuesioner, kesamaan dengan notebook, pelatihan ulang, setiap halaman di kedua bahasa |

## 6.4 Fitur Aplikasi

| Halaman | Fitur | Kaitan rubrik |
|---|---|---|
| Beranda | rumusan masalah, pengguna, alur, metrik model | *Problem formulation* |
| Rekomendasi — satu siswa | mode kuesioner (pertanyaan Google Form) atau 11 nilai fitur; prediksi + persentil; skor prioritas; tiga alternatif teratas; grafik kontribusi bobot × utilitas; kalimat alasan; uji sensitivitas per siswa; aturan pengaman | *Implementation*, *Explainability* |
| Rekomendasi — banyak siswa | unggah ekspor Google Form (.csv/.xlsx) atau CSV 11 kolom; kolom pribadi dibuang otomatis; peringkat prioritas; unduh hasil; evaluasi MAE/RMSE/R² bila jawaban Psikologis tersedia | *Implementation*, *Evaluation* |
| Analisis | statistik data Kaggle dan agregat data riil; metrik, aktual vs prediksi, galat, *feature importance*, perbandingan algoritma dan strategi; grafik SMART dari notebook; stabilitas ±10%/±20%; peta sensitivitas; keadilan per gender | *Evaluation & Sensitivity*, *Data & Criteria* |
| Tentang | data, *preprocessing*, pemetaan kuesioner, RF, SMART, keterbatasan, etika | *Algorithm*, *Architecture*, *Ethics* |
| Sidebar | ID/EN, profil bobot A/B/C (hasil langsung berubah), versi model | *Sensitivity* |

## 6.5 Langkah Deployment

1. Pastikan `app/models/` berisi model aktif dan metadata. Setelah data riil dijalankan, tambahkan `rf_real_model.joblib`, metadatanya, dan `real_summary.json`. Data mentah **tidak** ikut di-*commit*.
2. *Push* ke GitHub (repositori privat `UKRIDA-Developer-Team/SIMBULL-SMART`, cabang `main`).
3. Di share.streamlit.io, pilih *Create app* → repositori → cabang `main` → berkas `app/streamlit_app.py` → Python 3.12. Beri Streamlit akses ke repositori privat.
4. Uji URL publik: setiap halaman dalam ID dan EN, satu penilaian siswa, dan unggah `data/sample_gform.csv`.

Versi pustaka dipatok di `app/requirements.txt` (scikit-learn 1.9.1 sama dengan versi pembuat model) agar berkas `.joblib` dapat dimuat di server.

⟦ISI: URL aplikasi setelah deploy⟧

## 6.6 Pemantauan, Pemeliharaan, Privasi

| Aspek | Mekanisme |
|---|---|
| Kinerja pada data baru | unggah ekspor baru di tab "Banyak siswa" atau jalankan `scripts/evaluate.py`; bandingkan model aktif dengan model Kaggle |
| Pelatihan ulang | jalankan `scripts/train.py --stage real` saat respons bertambah; strategi terbaik dipilih ulang otomatis |
| Versi model | metadata mencatat sumber data, strategi, jumlah baris, dan waktu pelatihan; ditampilkan di sidebar |
| Privasi | tidak ada penyimpanan data di aplikasi; unggahan diproses di memori; kolom pribadi dibuang; unduhan tanpa identitas; repositori privat; sel agregat < 5 orang disembunyikan; laporan berisi contoh jawaban disimpan di folder yang di-*gitignore* |
| Keamanan penggunaan | penafian "bukan diagnosis" di setiap halaman; aturan pengaman rujukan untuk 10% prediksi tertinggi |

## 6.7 Peninjauan Proyek

**Yang berhasil:** integrasi RF → SMART berjalan dari satu siswa hingga 20.000 siswa, dengan hasil identik dengan notebook. Setiap rekomendasi dapat ditelusuri ke kontribusi kriteria. Pipeline data riil siap pakai begitu ekspor tersedia.

**Yang diperbaiki selama deployment:** bobot Exercise profil A yang berjumlah 1,05; *bug* `criteria_plot` di notebook; normalisasi satu siswa dengan batas referensi.

**Pengembangan lanjutan:** validasi bobot oleh pakar BK; segmentasi siswa (*clustering*) dan aturan asosiasi dari rancangan awal; bobot SMART yang diturunkan dari *feature importance*; pengumpulan data berkala (longitudinal).


[[PAGEBREAK]]

# Lampiran Teknis

## A. Repositori dan Aplikasi

| Item | Tautan / lokasi |
|---|---|
| Repositori GitHub | https://github.com/UKRIDA-Developer-Team/SIMBULL-SMART (privat; akses diberikan kepada penilai) |
| Cabang pengembangan | `future` (digabung ke `main` untuk deployment) |
| Aplikasi daring | ⟦ISI: URL Streamlit Community Cloud⟧ |
| Notebook Colab | `code/Copy of EskulSPK2026_SMART_Final.ipynb` |
| Kode aplikasi | `app/` (lihat `app/README.md`) |

## B. Menjalankan Ulang Pipeline

```
cd app
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-train.txt
python scripts/train.py --stage kaggle --csv data/dataset.csv     # model dasar (MAE 0,7668)
python scripts/train.py --stage compare                           # perbandingan algoritma
python scripts/inspect_gform.py data/private/gform_raw.csv        # cek pemetaan kuesioner
python scripts/train.py --stage real --gform data/private/gform_raw.csv
python scripts/evaluate.py --gform data/private/gform_new.csv     # uji data baru
pytest                                                            # uji otomatis
streamlit run streamlit_app.py
```

## C. Versi Pustaka

| Pustaka | Versi |
|---|---|
| Python | 3.12+ |
| scikit-learn | 1.9.1 |
| pandas | 3.0.6 |
| numpy | 2.5.3 |
| streamlit | 1.64.0 |
| matplotlib / seaborn | 3.11.2 / 0.13.2 |
