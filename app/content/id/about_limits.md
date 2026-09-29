### Keterbatasan

- Data Kaggle berasal dari mahasiswa (usia 17-29), sedangkan pengguna sasaran adalah siswa SMA; karena itu model dilatih ulang dengan data kuesioner riil.
- Beberapa fitur kuesioner adalah **proksi** (mis. tingkat stres dan tekanan finansial) sehingga maknanya tidak identik dengan fitur Kaggle.
- Data *self-report* dan *cross-sectional*: rawan bias sosial dan tidak menunjukkan sebab-akibat.
- Pada data Kaggle, regresi linear sedikit lebih akurat daripada Random Forest (MAE CV 0,768 vs 0,779); RF dipertahankan karena hasil notebook, ketahanan terhadap hubungan non-linear, dan *feature importance*.
- Bobot profil A/B ditetapkan berdasarkan pertimbangan domain, belum divalidasi pakar; profil C selalu seri dan hanya menjadi pembanding.

### Etika, keadilan, dan privasi

- **Bukan alat diagnosis.** Hasil adalah indikasi untuk membantu guru BK, bukan label klinis.
- **Aturan pengaman.** Siswa dengan prediksi kecemasan di 10% teratas selalu mendapat rekomendasi konseling dan rujukan, apa pun peringkat SMART.
- **Privasi.** Tidak ada data yang disimpan; unggahan diproses di memori; kolom pribadi dibuang; hasil unduhan tanpa identitas; repositori privat dan data mentah tidak di-commit; sel agregat dengan kurang dari 5 orang disembunyikan.
- **Keadilan.** Kesalahan prediksi dan sebaran rekomendasi dibandingkan antar gender pada halaman Analisis.
