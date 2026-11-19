# Fase 6 — Deployment

**Proyek:** SPK Rekomendasi Penanganan Kecemasan Siswa (Random Forest + SMART)
**Metodologi:** CRISP-DM — Fase 6 dari 6

---

## 1. Rencana Deployment

| Aktivitas CRISP-DM | Wujud pada proyek |
|---|---|
| *Plan deployment* | Aplikasi web **Streamlit** bilingual (ID/EN), di-*hosting* gratis di **Streamlit Community Cloud** dari repositori GitHub |
| *Plan monitoring & maintenance* | Pipeline pelatihan ulang dengan data kuesioner baru; evaluasi pada data baru |
| *Produce final report* | Laporan teknis ini, panduan pengguna, presentasi |
| *Review project* | Bagian 7 |

**Mengapa Streamlit (bukan Gradio seperti rancangan awal):** antarmuka multi-halaman bawaan, komponen grafik dan tabel yang lengkap, *caching* model, dan *hosting* gratis yang langsung terhubung ke GitHub, sesuai rekomendasi rubrik proyek.

## 2. Arsitektur

```
 Pelatihan offline (laptop / Colab)                    Streamlit Community Cloud
 ─────────────────────────────────                     ─────────────────────────────────────────────
 Kaggle 1M ─► 14–25 80/20 ┐                             streamlit_app.py + ui.py (bilah atas: halaman,
                          ├─► scripts/train.py ─► models/   │  sakelar Aplikasi | Laporan, ID | EN)
 Google Form (rahasia) ───┘   kaggle | real |     *.joblib  ├─ Aplikasi: Beranda, Nilai siswa, Nilai kelas,
                              compare              + meta   │  Bantuan ─► spk/gform.py  (jawaban → fitur)
                                                  (agregat) │             spk/model.py  (prediksi RF)
                                                            │             spk/smart.py  (SMART, sensitivitas)
                                                            │             spk/recommend.py, explain.py, xai.py
                                                            └─ Laporan teknis: Bab 1–8 ─► report.py, spk/plots.py
```

Prinsipnya: **aplikasi tidak pernah melatih model**. Pelatihan berjalan *offline*. Aplikasi hanya memuat model `.joblib` beserta metadata (fitur, pemetaan gender, batas SMART, median imputasi, kuantil referensi) lalu melakukan inferensi. *Preprocessing* saat inferensi memakai kode dan nilai yang sama persis dengan saat pelatihan: `gform.derive`, `GENDER_MAP`, `smart_bounds`, dan `impute_medians`.

## 3. Struktur Kode

| Berkas | Tanggung jawab |
|---|---|
| `app/streamlit_app.py`, `app/ui.py` | titik masuk; daftar halaman kedua bagian; bilah atas (menu, sakelar Aplikasi/Laporan, ID/EN, pilihan model); pemuat model dan data |
| `app/app_pages/home.py`, `help.py` | Beranda dan Bantuan |
| `app/app_pages/recommendation.py` | kuesioner satu siswa (kosong di awal, contoh hanya mengisi formulir) dan hasil ringkas |
| `app/app_pages/batch.py` | unggah satu kelas: daftar rujukan, daftar prioritas, rencana program, evaluasi data baru |
| `app/result_views.py` | potongan hasil yang dipakai kedua bagian: kartu hasil, faktor utama, simulasi "bagaimana jika", kartu xAI |
| `app/report.py`, `app/app_pages/report/*.py` | Laporan teknis Bab 1–8: bab dan subbab bernomor, tabel dan gambar berkapsi, tombol bab sebelumnya/berikutnya |
| `app/spk/*.py` | logika murni tanpa Streamlit, diuji dengan `pytest` |
| `app/scripts/*.py` | pelatihan (`kaggle`, `tune`, `compare`, `real`), inspeksi kuesioner, evaluasi data baru, laporan penggabungan pertanyaan |
| `app/tests/` | 180 uji otomatis (*black-box* dan *white-box*): *parsing* kuesioner, perhitungan SMART, pelatihan ulang, setiap halaman kedua bagian dalam kedua bahasa |

## 4. Fitur Aplikasi

Aplikasi dibagi menjadi dua bagian yang dipilih dengan sakelar **Aplikasi | Laporan** di samping tombol bahasa. Bagian **Aplikasi** ditujukan untuk guru BK dan menampilkan hasil ringkas. Bagian **Laporan teknis** ditujukan untuk dosen dan penguji dan memuat seluruh perhitungan dan evaluasi.

| Bagian · halaman | Fitur | Kaitan rubrik |
|---|---|---|
| Aplikasi · Beranda | rumusan masalah, alur kerja, lima bentuk dukungan, tautan ke laporan teknis | *Problem formulation* |
| Aplikasi · Nilai siswa | kuesioner 18 butir yang kosong di awal dan wajib diisi lengkap; contoh risiko tinggi/rendah yang hanya mengisi formulir; hasil: rekomendasi utama, prediksi + label posisi (dengan rentang dan kelompok pembanding), skor prioritas, urutan lima pilihan, kalimat alasan, faktor utama (Shapley), simulasi "bagaimana jika" untuk beberapa faktor sekaligus, aturan pengaman | *Implementation*, *Explainability* |
| Aplikasi · Nilai kelas | unggah ekspor Google Form (.csv/.xlsx) atau CSV 11 kolom (ada template); data contoh 30 siswa bila diminta; kolom pribadi dibuang otomatis; daftar rujukan segera; daftar prioritas dengan filter; rencana program per bentuk dukungan; unduh CSV; evaluasi MAE/RMSE/R² bila jawaban Psikologis tersedia | *Implementation*, *Evaluation* |
| Laporan · Bab 1–2 | statistik data Kaggle dan agregat data riil; metrik, iterasi model, aktual vs prediksi, galat, *feature importance*, perbandingan algoritma dan strategi | *Data & Criteria*, *Algorithm* |
| Laporan · Bab 3 | perhitungan SMART langkah demi langkah untuk satu siswa: input, prediksi RF, nilai kriteria, utilitas dengan angka yang disubstitusi, matriks bobot, kontribusi w × u, peringkat, prioritas dan aturan pengaman, sensitivitas, dan xAI | *Algorithm*, *Explainability* |
| Laporan · Bab 4–6 | xAI global (Gini vs permutasi, PDP/ICE); hasil SMART pada populasi, stabilitas ±10%/±20%, peta sensitivitas per kriteria; keadilan per gender | *Evaluation & Sensitivity*, *Ethics* |
| Laporan · Bab 7–8 | enam fase CRISP-DM dengan angka langsung dari data, model, dan uji; arsitektur, metode, keterbatasan, etika, tim | *Data Mining process*, *Architecture* |
| Pengaturan | ID/EN; pilihan model (iterasi 1 Kaggle atau iterasi 2 data riil), hasil di semua halaman langsung berubah; perbandingan kedua model untuk satu siswa di Bab 3 | *Evaluation* |

## 5. Langkah Deployment

1. Pastikan `app/models/` berisi model dasar Kaggle (`rf_anxiety_model.joblib`, ±29 MB) dan model aktif data riil (`rf_real_model.joblib`, ±0,4 MB) beserta metadata dan `real_summary.json` (agregat saja). Ekspor kuesioner mentah **tidak** ikut di-*commit*.
2. *Push* ke GitHub (repositori privat `UKRIDA-Developer-Team/SIMBULL-SMART`, cabang `main`).
3. Di share.streamlit.io, pilih *Create app* → repositori → cabang `main` → berkas `app/streamlit_app.py` → Python 3.12. Beri Streamlit akses ke repositori privat.
4. Uji URL publik: setiap halaman dalam ID dan EN, satu penilaian siswa, dan unggah ekspor kuesioner (aplikasi membuang kolom pribadi dan tidak menyimpan apa pun).

Versi pustaka dipatok di `app/requirements.txt` (scikit-learn 1.9.1 sama dengan versi pembuat model) agar berkas `.joblib` dapat dimuat di server.

⟦ISI: URL aplikasi setelah deploy⟧

## 6. Pemantauan, Pemeliharaan, Privasi

| Aspek | Mekanisme |
|---|---|
| Kinerja pada data baru | unggah ekspor baru di tab "Banyak siswa" atau jalankan `scripts/evaluate.py`; bandingkan model aktif dengan model Kaggle |
| Pelatihan ulang | jalankan `scripts/train.py --stage real` saat respons bertambah; strategi terbaik dipilih ulang otomatis |
| Versi model | metadata mencatat sumber data, strategi, jumlah baris, dan waktu pelatihan; ditampilkan di panel pilihan model |
| Privasi | tidak ada penyimpanan data di aplikasi; unggahan diproses di memori; kolom pribadi dibuang; unduhan tanpa identitas; repositori privat; sel agregat < 5 orang disembunyikan; laporan berisi contoh jawaban disimpan di folder yang di-*gitignore* |
| Keamanan penggunaan | penafian "bukan diagnosis" di setiap halaman; aturan pengaman rujukan untuk 10% prediksi tertinggi |

## 7. Peninjauan Proyek

**Yang berhasil:** integrasi RF → SMART berjalan dari satu siswa hingga 20.000 siswa referensi; perhitungan SMART identik dengan notebook. Setiap rekomendasi dapat ditelusuri ke kontribusi kriteria. Pipeline data riil siap pakai begitu ekspor tersedia.

**Yang diperbaiki selama deployment:** bobot Exercise profil A yang berjumlah 1,05; *bug* `criteria_plot` di notebook; normalisasi satu siswa dengan batas referensi; pembersihan usia 14–25; pelatihan pada seluruh data (bukan sampel 8.000 baris) dengan data uji 138.509 baris; *tuning* parameter dengan validasi silang.

**Pengembangan lanjutan:** validasi bobot oleh pakar BK; segmentasi siswa (*clustering*) dan aturan asosiasi dari rancangan awal; bobot SMART yang diturunkan dari *feature importance*; pengumpulan data berkala (longitudinal).
