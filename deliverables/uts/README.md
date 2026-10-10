# SPK SMART Kecemasan Siswa

**Sistem Pendukung Keputusan Prioritas dan Rekomendasi Penanganan Kecemasan Siswa SMA Berbasis Random Forest dan Metode SMART**

Keluaran UTS mata kuliah Sistem Pendukung Keputusan, UKRIDA 2026. Folder ini berisi tiga berkas:

| Berkas | Isi |
|---|---|
| `Laporan-UTS-SPK-SMART-Kecemasan.docx` | Laporan UTS (Bab 1 Intelligence, Bab 2 Perancangan, Bab 3 Bukti Perhitungan, Bab 4 Logbook dan Jadwal, Daftar Pustaka) |
| `Perhitungan-SMART-SPK-Kecemasan.xlsx` | Perhitungan SMART lengkap dengan rumus Excel yang dapat ditelusuri |
| `README.md` | Berkas ini |

## Identitas Kelompok (Kelompok 1)

| Nama | NIM |
|---|---|
| Steven Feryanta | 412025028 |
| Steven Iwan | 412024008 |
| Triemas Putra | 412024018 |
| Davidson Rafael | 412024030 |

## Metode yang Dipilih

**SMART (*Simple Multi-Attribute Rating Technique*)**, digabung dengan model data mining **Random Forest Regressor**.

- Random Forest memprediksi skor kecemasan siswa (0–10) dari 11 faktor gaya hidup dan akademik. Prediksi ini menjadi kriteria C1.
- SMART mengubah delapan kriteria (C1–C8) menjadi utilitas 0–1, lalu membuat dua keputusan:
  1. **Siapa ditangani lebih dulu:** skor prioritas siswa.
  2. **Penanganan apa yang paling sesuai:** peringkat lima alternatif (A1–A5) untuk tiap siswa.

## Alasan Pemilihan Metode

1. **Transparan.** Skor adalah jumlah bobot × utilitas, sehingga kontribusi setiap kriteria dapat ditunjukkan kepada guru BK, siswa, dan orang tua. Ini penting untuk masalah kesehatan mental.
2. **Dapat menilai satu siswa.** Normalisasi memakai batas min–maks referensi dari 20.000 siswa. Skor seorang siswa tidak berubah ketika siswa lain ditambahkan. Pada TOPSIS, skor bergantung pada kelompok yang dinilai bersama.
3. **Mendukung kriteria benefit dan cost** secara langsung.
4. **Tidak membutuhkan panel ahli** untuk perbandingan berpasangan seperti AHP. Bobot ditetapkan langsung, lalu diuji dengan analisis sensitivitas.
5. **Ringan dan stabil.** Pada 20.000 siswa, perubahan acak ±10% pada semua bobot profil A mempertahankan 94,6% rekomendasi utama.

## Rumus Utama

Notasi: i = siswa, j = kriteria (1..8), k = alternatif (1..5), x_ij = nilai siswa i pada kriteria j, min_j dan maks_j = batas referensi.

| Langkah | Rumus |
|---|---|
| Utilitas kriteria benefit | u_ij = (x_ij − min_j) / (maks_j − min_j) |
| Utilitas kriteria cost | u_ij = (maks_j − x_ij) / (maks_j − min_j) |
| Pemotongan | u_ij = min(1, maks(0, u_ij)); jika maks_j = min_j maka u_ij = 1 |
| Normalisasi bobot | w_kj = w'_kj / Σ_j w'_kj (bobot tiap alternatif berjumlah 1) |
| Skor prioritas siswa | P_i = Σ_j (1/8) · u_ij |
| Skor alternatif | S_ik = Σ_j w_kj · u_ij |
| Rekomendasi | k* = argmaks_k S_ik |
| Aturan pengaman | jika persentil prediksi kecemasan ≥ 90, rekomendasi akhir = Konseling + rujukan profesional |
| Sensitivitas bobot | S'_ik = (S_ik + w_kc · d · u_ic) / (1 + w_kc · d), untuk perubahan bobot kriteria c sebesar d |

## Tahapan Algoritma

1. **Input profil siswa:** 11 fitur (usia, gender, jam belajar, nilai rapor, tekanan ujian, tingkat stres, jam tidur, hari olahraga, tekanan finansial, ekspektasi keluarga, *burnout*).
2. **Prediksi:** Random Forest menghasilkan skor kecemasan 0–10 (kriteria C1).
3. **Matriks keputusan:** susun x_ij untuk C1–C8 (C1 dari prediksi, C2–C8 langsung dari input).
4. **Normalisasi:** hitung utilitas u_ij dengan rumus benefit atau cost dan batas referensi.
5. **Bobot:** normalisasi bobot tiap alternatif agar berjumlah 1 (profil A, B, atau C).
6. **Skor prioritas:** P_i = rata-rata utilitas; urutkan siswa dari P_i terbesar.
7. **Skor alternatif:** S_ik = Σ w_kj · u_ij untuk lima alternatif; urutkan dari terbesar.
8. **Aturan pengaman:** siswa dengan persentil prediksi ≥ 90 selalu mendapat Konseling + rujukan.
9. **Penjelasan dan validasi:** tampilkan kontribusi w_kj · u_ij, alternatif ke-2, dan uji sensitivitas ±10%/±20%.

## Arti Setiap Kriteria

**Benefit** berarti nilai tinggi menaikkan utilitas (siswa lebih membutuhkan perhatian). **Cost** berarti nilai rendah yang menaikkan utilitas.

| Kode | Kriteria | Jenis | Arti | Min–maks referensi |
|---|---|---|---|---|
| C1 | Prediksi skor kecemasan (Random Forest) | benefit | Makin tinggi prediksi kecemasan, makin perlu ditangani | 0,367–7,091 |
| C2 | Jam belajar per hari | benefit | Beban belajar panjang menambah tekanan | 0–13,227 |
| C3 | Nilai rata-rata rapor | cost | Nilai rendah menandakan kesulitan akademik | 47,565–92,894 |
| C4 | Jam tidur per malam | cost | Tidur pendek memperburuk kondisi | 3–10 |
| C5 | Hari olahraga per minggu | cost | Jarang olahraga berarti kurang penyaluran stres | 0–7 |
| C6 | Tekanan finansial (0–10) | benefit | Tekanan ekonomi menambah beban | 0–10 |
| C7 | Ekspektasi keluarga (0–10) | benefit | Tuntutan keluarga tinggi menambah tekanan | 0–10 |
| C8 | Skor *burnout* (0–10) | benefit | Kelelahan tinggi butuh pemulihan | 0–9,855 |

Alternatif penanganan:

| Kode | Alternatif | Kriteria berbobot terbesar (profil A) |
|---|---|---|
| A1 | Tidur (*Sleep*): perbaikan pola tidur | C4 jam tidur 0,40 |
| A2 | Olahraga (*Exercise*): aktivitas fisik terjadwal | C5 olahraga 0,43; C8 *burnout* 0,19 |
| A3 | Strategi belajar (*Study*): manajemen waktu | C2 jam belajar 0,40; C3 nilai rapor 0,30 |
| A4 | Konseling (*Counseling*): konseling BK, rujukan | C1 prediksi kecemasan 0,30; C6 finansial 0,20 |
| A5 | Relaksasi (*Relaxation*): pernapasan, *mindfulness* | C1 0,20; C4 0,20; C6 dan C7 0,15 |

## Interpretasi Hasil SPK

Spreadsheet menghitung 10 siswa: S01–S02 adalah contoh profil di aplikasi, S03–S10 adalah data uji Kaggle. Hasil dengan profil bobot A:

| Prioritas | Siswa | Skor P_i | Rekomendasi SMART | Rekomendasi akhir |
|---|---|---|---|---|
| 1 | S01 | 0,8259 | Olahraga | **Konseling + rujukan** (persentil prediksi 99,7 ≥ 90) |
| 2 | S06 | 0,5235 | Tidur | Tidur |
| 3 | S08 | 0,4841 | Tidur | Tidur |
| 4 | S10 | 0,4400 | Strategi belajar | Strategi belajar |
| 5 | S05 | 0,4188 | Relaksasi | Relaksasi |
| 6 | S03 | 0,4151 | Strategi belajar | Strategi belajar |
| 7 | S07 | 0,3788 | Olahraga | Olahraga |
| 8 | S09 | 0,3782 | Konseling | Konseling |
| 9 | S04 | 0,3625 | Olahraga | Olahraga |
| 10 | S02 | 0,2310 | Relaksasi | Relaksasi |

Cara membaca:

- **Skor prioritas** (0–1) menentukan urutan pemanggilan siswa oleh guru BK. Makin tinggi, makin banyak kriteria yang menunjukkan kebutuhan perhatian.
- **Rekomendasi SMART** adalah alternatif dengan skor tertinggi. Contoh: S01 hanya berolahraga 0,5 hari per minggu (utilitas C5 = 0,93), sehingga Olahraga mendapat skor 0,8730.
- **Aturan pengaman** mengganti rekomendasi menjadi Konseling + rujukan bila prediksi kecemasan berada di 10% teratas. Program dari SMART tetap dijalankan sesudahnya.
- Bila selisih skor dengan alternatif kedua kecil (< 0,02, misalnya S03, S05, S07), guru BK sebaiknya mempertimbangkan kedua program.
- Sistem ini adalah alat bantu skrining, **bukan diagnosis klinis**. Keputusan akhir tetap pada guru BK dan tenaga profesional.

## Konsistensi dengan Aplikasi

Sheet **Validasi** membandingkan setiap skor spreadsheet dengan keluaran fungsi `spk.recommend.assess()` di aplikasi. Hasilnya **10 dari 10 siswa cocok** untuk profil bobot A, B, dan C, dengan selisih maksimum 3,3E−16 (pembulatan bilangan titik mengambang). Uji sensitivitas di sheet StudiKasus juga sama dengan tabel di aplikasi (S01: 32 dari 32 skenario stabil; S03: 23 dari 32).

## Cara Memakai Spreadsheet

| Sheet | Isi |
|---|---|
| Petunjuk | Legenda warna, rumus, alur sheet |
| Kriteria, Alternatif | C1–C8 (jenis, batas referensi) dan A1–A5 |
| Bobot | Profil A mentah dan ternormalisasi, B, C, bobot aktif, bobot prioritas |
| Data | 11 fitur siswa, prediksi RF, persentil |
| MatriksKeputusan, Normalisasi | x_ij dan u_ij |
| SkorPrioritas, SkorAlternatif | P_i dan peringkat siswa; S_ik dan rekomendasi |
| StudiKasus | Matriks alternatif × kriteria satu siswa dan uji sensitivitas |
| Rekomendasi | Aturan pengaman, rekomendasi akhir, interpretasi |
| Validasi | Perbandingan dengan keluaran aplikasi |

- Teks biru = input, hitam = rumus, hijau = rumus antar-sheet. Sel kuning boleh diubah: **Bobot!C3** (profil A/B/C), **StudiKasus!C3** (ID siswa), **Rekomendasi!C3** (ambang pengaman).
- Prediksi Random Forest (Data!N) disalin dari aplikasi, karena model tidak dapat dijalankan di Excel. Semua langkah SMART lainnya memakai rumus.
- Buka dengan Microsoft Excel, Google Sheets, atau ONLYOFFICE. Rumus dihitung saat berkas dibuka.

## Membuat Ulang Berkas

```bash
cd app && .venv/bin/python ../deliverables/build/uts_data.py         # data siswa + keluaran aplikasi -> uts_data.json
.venv/bin/python ../deliverables/build/build_uts_xlsx.py               # spreadsheet
.venv/bin/python ../deliverables/build/uts_figures.py                  # gambar laporan
cd ../deliverables/build && node build_uts.js                         # laporan .docx
```

Repositori: https://github.com/UKRIDA-Developer-Team/SIMBULL-SMART (privat).
