### Keterbatasan

- Data Kaggle berasal dari mahasiswa. Data dibersihkan ke rentang usia pelajar 14-25, tetapi berkasnya hanya berisi usia 17-25, sehingga model dasar tidak pernah melihat pelajar berusia 14-16. Pengguna sasaran adalah siswa SMA (sekitar 15-18 tahun); karena itu model dilatih ulang dengan data kuesioner riil.
- **Data riil.** Pada 292 respons siswa (usia 14-25 setelah pembersihan), model Kaggle gagal: R² *holdout* −0,35, MAE 1,87, karena siswa ini jauh lebih cemas (rata-rata 5,0 vs 3,0) dan faktor dominannya berbeda (*burnout*, tekanan ujian, ekspektasi keluarga). Model yang dipakai dilatih hanya dengan jawaban riil: MAE *holdout* 1,11, R² 0,44 pada 59 siswa, dan R² validasi silang 0,20. Galat sekitar ±1,1 poin cukup untuk mengurutkan siswa, bukan untuk skor pasti.
- Beberapa fitur kuesioner adalah **proksi** (mis. tingkat stres dan tekanan finansial) sehingga maknanya tidak identik dengan fitur Kaggle.
- Data *self-report* dan *cross-sectional*: rawan bias sosial dan tidak menunjukkan sebab-akibat.
- Pada data Kaggle, regresi linear dan gradient boosting sama akuratnya dengan Random Forest (R² uji 0,606 dan 0,608 vs 0,608; MAE CV 0,760, 0,761, dan 0,761); RF dipertahankan karena hasil notebook, ketahanan terhadap hubungan non-linear, dan *feature importance*.
- **R² berhenti di sekitar 0,61 pada data Kaggle.** Sekitar 40% variasi skor kecemasan adalah derau acak yang tidak dibawa kolom masukan mana pun: regresi linear, gradient boosting, dan Random Forest yang dituning sama-sama mencapai 0,606-0,608 pada 138.509 baris uji. Membuang outlier atau baris ekstrem tidak menaikkannya. Hanya `mental_health_index` yang dapat menaikkannya (ke sekitar 0,80), tetapi kolom itu dihitung dari skor kecemasan itu sendiri (`10 - 0,4 stres - 0,3 kecemasan - 0,3 depresi`). Memakainya berarti *label leakage*, dan kuesioner tidak memiliki butir tersebut.
- Random Forest hampir hanya mengandalkan tingkat stres dan burnout (96% *feature importance*), karena dua kolom itu membawa hampir seluruh sinyal pada data Kaggle. Faktor lain tetap diperhitungkan SMART sebagai kriteria tersendiri.
- Bobot profil A/B ditetapkan berdasarkan pertimbangan domain, belum divalidasi pakar; profil C selalu seri dan hanya menjadi pembanding.

### Etika, keadilan, dan privasi

- **Bukan alat diagnosis.** Hasil adalah indikasi untuk membantu guru BK, bukan label klinis.
- **Aturan pengaman.** Siswa dengan prediksi kecemasan di 10% teratas selalu mendapat rekomendasi konseling dan rujukan, apa pun peringkat SMART.
- **Privasi.** Tidak ada data yang disimpan; unggahan diproses di memori; kolom pribadi dibuang; hasil unduhan tanpa identitas; repositori privat dan data mentah tidak di-commit; sel agregat dengan kurang dari 5 orang disembunyikan.
- **Keadilan.** Kesalahan prediksi dan sebaran rekomendasi dibandingkan antar gender pada halaman Analisis.
