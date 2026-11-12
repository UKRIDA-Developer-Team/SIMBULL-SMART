# Fase 1 — Business Understanding

**Proyek:** SPK Rekomendasi Penanganan Kecemasan Siswa dengan Random Forest dan Metode *Simple Multi-Attribute Rating Technique* (SMART)
**Metodologi:** CRISP-DM — Fase 1 dari 6

---

## 1. Latar Belakang Masalah

Kecemasan (*anxiety*) adalah kekhawatiran berlebih yang memengaruhi pikiran, emosi, dan aktivitas sehari-hari. Pada siswa, pemicunya banyak berasal dari tekanan akademik: ujian, tugas yang menumpuk, tuntutan nilai, dan ekspektasi orang tua. Dampaknya berantai: konsentrasi turun, tugas terlambat, motivasi melemah, hingga prestasi dan kesejahteraan mental menurun.

Indikasi kecemasan sering tidak disadari oleh siswa, guru, maupun orang tua. Identifikasi masih bergantung pada observasi guru Bimbingan Konseling (BK). Cara ini punya tiga keterbatasan:

1. **Kapasitas terbatas.** Jumlah guru BK jauh lebih sedikit daripada siswa, sehingga penjaringan menyeluruh sulit dilakukan secara rutin.
2. **Reaktif.** Penanganan biasanya dimulai setelah gejala jelas atau prestasi sudah turun.
3. **Subjektif.** Pilihan bentuk penanganan sering bergantung pada pengalaman pribadi, tanpa dasar multikriteria yang terdokumentasi dan dapat ditelusuri.

Padahal data tentang kebiasaan belajar, tidur, aktivitas fisik, tekanan keluarga, dan kelelahan dapat dikumpulkan dengan kuesioner singkat. Data ini dapat diolah dengan **data mining** untuk memperkirakan tingkat kecemasan, lalu dengan **Sistem Pendukung Keputusan (SPK)** untuk menentukan siapa yang ditangani lebih dulu dan penanganan apa yang paling sesuai.

> **Catatan etis.** Sistem ini adalah alat bantu **skrining dan pendukung keputusan**, bukan alat diagnosis klinis. Keputusan akhir tetap pada guru BK dan/atau tenaga profesional.

## 2. Tujuan Bisnis

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

## 3. Tujuan Data Mining

| Kode | Tujuan | Teknik |
|---|---|---|
| DM-1 | Memprediksi skor kecemasan (0–10) dari faktor gaya hidup dan akademik | Regresi *Random Forest* |
| DM-2 | Mengidentifikasi faktor yang paling berpengaruh terhadap skor kecemasan | *Feature importance* (Gini) dan korelasi |
| DM-3 | Menyediakan input kriteria SPK: prediksi kecemasan menjadi salah satu kriteria SMART | Integrasi RF → SMART |
| DM-4 | Menyesuaikan model dengan populasi sasaran (siswa SMA) | Pelatihan ulang pada data kuesioner riil |

**Titik temu Data Mining dan SPK.** Data mining bekerja pada tahap *diagnosis* (seberapa tinggi indikasi kecemasan dan faktor apa yang dominan). SMART bekerja pada tahap *preskripsi* (siapa lebih dulu dan penanganan apa yang paling tepat).

## 4. Faktor dan Kriteria

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

## 5. Kriteria Keberhasilan

### 5.1 Data Mining

| Kode | Kriteria | Target | Hasil |
|---|---|---|---|
| D1 | Model lebih baik dari baseline rata-rata | MAE < baseline | Tercapai (0,758 vs 1,222 pada 138.509 baris uji Kaggle) |
| D2 | Daya jelaskan model | R² ≥ 0,60 | Tercapai (0,608 pada 138.509 baris uji Kaggle) |
| D3 | Faktor dominan masuk akal secara teori | Faktor stres/kelelahan di peringkat atas | Tercapai (stres 0,75, *burnout* 0,21) |
| D4 | Kinerja pada data riil | MAE lebih rendah dari model Kaggle tanpa latih ulang | Tercapai (MAE 1,113 vs 1,874 pada 59 respons *holdout*) |

### 5.2 SPK

| Kode | Kriteria | Target | Hasil |
|---|---|---|---|
| S1 | Stabilitas terhadap perubahan bobot | ≥ 90% rekomendasi utama tetap saat bobot diubah acak ±10% | Kaggle: profil A 94,3%, profil B 89,1%; data riil: profil A 95,5%, profil B 87,7% |
| S2 | Setiap rekomendasi dapat dijelaskan | 100% hasil disertai kontribusi kriteria dan alasan | Tercapai di aplikasi |
| S3 | Aturan pengaman | Siswa berisiko tinggi selalu mendapat rujukan konseling | Tercapai (10% prediksi tertinggi) |
| S4 | Kebergunaan | Skor rata-rata evaluasi pengguna (Google Form, skala 1–5) ≥ 4 | ⟦ISI setelah uji pengguna⟧ |

## 6. Rencana Proyek

| Fase | Aktivitas | Keluaran |
|---|---|---|
| 1. Business Understanding | Merumuskan masalah, tujuan, kriteria, dan alternatif | Dokumen ini |
| 2. Data Understanding | Memahami dataset Kaggle dan kuesioner riil | Kamus data, statistik deskriptif |
| 3. Data Preparation | Sampling, encoding, pemetaan kuesioner → fitur, pembagian data | Dataset siap model |
| 4. Modeling | Random Forest, pelatihan ulang, SMART | Model + matriks keputusan |
| 5. Evaluation | Metrik regresi, perbandingan algoritma, sensitivitas bobot, keadilan | Laporan evaluasi |
| 6. Deployment | Aplikasi Streamlit bilingual di Streamlit Community Cloud | Aplikasi daring + panduan |
