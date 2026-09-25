# Fase 2 — Data Understanding

**Proyek:** SPK Rekomendasi Penanganan Kecemasan Siswa (Random Forest + SMART)
**Metodologi:** CRISP-DM — Fase 2 dari 6

---

## 1. Sumber Data

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

## 2. Deskripsi Data Kaggle (20.000 baris)

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

### 2.1 Korelasi dengan skor kecemasan

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
| **Psikologis** | gugup/cemas, sulit mengendalikan khawatir, konsentrasi (dibalik), pikiran terganggu, sulit menyelesaikan tugas | **target skor kecemasan** |
| Pola makan | uang saku cukup, jajan, minuman manis/berkafein, makan saat tertekan, melewatkan makan | tekanan finansial (+ ekstra) |

"Ekstra" berarti butir disimpan untuk analisis korelasi dan satu eksperimen model yang diperluas. Butir ini tidak dipakai model yang dideploy, karena model harus tetap sejajar dengan 11 fitur Kaggle.

### 3.1 Statistik data kuesioner

⟦ISI dari `app/models/real_summary.json` dan `app/reports/private/real_data_report.md` setelah pipeline dijalankan: jumlah respons, jumlah baris bersih, duplikat, *straight-lining*, sebaran gender, statistik tiap fitur, korelasi fitur dan butir ekstra dengan skor kecemasan.⟧

## 4. Kualitas Data

| Dimensi | Kaggle | Kuesioner (pemeriksaan otomatis `spk/gform.py`) |
|---|---|---|
| Kelengkapan | 0 nilai hilang | nilai hilang per fitur dilaporkan; diisi median data latih |
| Duplikat | 0 | baris jawaban identik dibuang |
| Validitas | rentang wajar | nilai di luar rentang (mis. rapor > 100) dikosongkan; jawaban yang tidak dikenali dilaporkan |
| Kesungguhan | – | *straight-lining* (semua Likert sama) dihitung |
| Privasi | tidak ada data pribadi | kolom pribadi dibuang segera setelah usia dihitung |

## 5. Keterbatasan

- Dataset Kaggle kemungkinan besar sintetis dan berasal dari mahasiswa, bukan siswa SMA. Karena itu model dilatih ulang dengan data riil.
- Tingkat stres dan tekanan finansial pada kuesioner adalah **proksi**, sehingga maknanya tidak identik dengan kolom Kaggle.
- Data kuesioner bersifat *self-report* dan *cross-sectional*: rawan bias sosial dan tidak menunjukkan sebab-akibat.
- Sampel kuesioner tidak acak (disebar lewat sekolah, media sosial, dan teman), sehingga generalisasinya terbatas.
