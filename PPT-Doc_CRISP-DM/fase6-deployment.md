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

## 3. Struktur Kode

| Berkas | Tanggung jawab |
|---|---|
| `app/streamlit_app.py` | titik masuk, `st.navigation`, sidebar (bahasa, profil bobot, info model, penafian) |
| `app/app_pages/home.py` | masalah, pengguna, alur kerja, tombol mulai |
| `app/app_pages/recommendation.py` | input satu siswa (kuesioner/lanjutan), hasil + alasan + sensitivitas; unggah banyak siswa + evaluasi data baru |
| `app/app_pages/analysis.py` | data, model, SMART, sensitivitas, keadilan |
| `app/app_pages/about.py` | metode, arsitektur, keterbatasan, etika |
| `app/spk/*.py` | logika murni tanpa Streamlit, diuji dengan `pytest` |
| `app/scripts/*.py` | pelatihan, inspeksi kuesioner, evaluasi, data sintetis |
| `app/tests/` | 38 uji otomatis: *parsing* kuesioner, kesamaan dengan notebook, pelatihan ulang, setiap halaman di kedua bahasa |

## 4. Fitur Aplikasi

| Halaman | Fitur | Kaitan rubrik |
|---|---|---|
| Beranda | rumusan masalah, pengguna, alur, metrik model | *Problem formulation* |
| Rekomendasi — satu siswa | mode kuesioner (pertanyaan Google Form) atau 11 nilai fitur; prediksi + persentil; skor prioritas; tiga alternatif teratas; grafik kontribusi bobot × utilitas; kalimat alasan; uji sensitivitas per siswa; aturan pengaman | *Implementation*, *Explainability* |
| Rekomendasi — banyak siswa | unggah ekspor Google Form (.csv/.xlsx) atau CSV 11 kolom; kolom pribadi dibuang otomatis; peringkat prioritas; unduh hasil; evaluasi MAE/RMSE/R² bila jawaban Psikologis tersedia | *Implementation*, *Evaluation* |
| Analisis | statistik data Kaggle dan agregat data riil; metrik, aktual vs prediksi, galat, *feature importance*, perbandingan algoritma dan strategi; grafik SMART dari notebook; stabilitas ±10%/±20%; peta sensitivitas; keadilan per gender | *Evaluation & Sensitivity*, *Data & Criteria* |
| Tentang | data, *preprocessing*, pemetaan kuesioner, RF, SMART, keterbatasan, etika | *Algorithm*, *Architecture*, *Ethics* |
| Sidebar | ID/EN, profil bobot A/B/C (hasil langsung berubah), versi model | *Sensitivity* |

## 5. Langkah Deployment

1. Pastikan `app/models/` berisi model aktif dan metadata. Setelah data riil dijalankan, tambahkan `rf_real_model.joblib`, metadatanya, dan `real_summary.json`. Data mentah **tidak** ikut di-*commit*.
2. *Push* ke GitHub (repositori privat `UKRIDA-Developer-Team/SIMBULL-SMART`, cabang `main`).
3. Di share.streamlit.io, pilih *Create app* → repositori → cabang `main` → berkas `app/streamlit_app.py` → Python 3.12. Beri Streamlit akses ke repositori privat.
4. Uji URL publik: setiap halaman dalam ID dan EN, satu penilaian siswa, dan unggah `data/sample_gform.csv`.

Versi pustaka dipatok di `app/requirements.txt` (scikit-learn 1.9.1 sama dengan versi pembuat model) agar berkas `.joblib` dapat dimuat di server.

⟦ISI: URL aplikasi setelah deploy⟧

## 6. Pemantauan, Pemeliharaan, Privasi

| Aspek | Mekanisme |
|---|---|
| Kinerja pada data baru | unggah ekspor baru di tab "Banyak siswa" atau jalankan `scripts/evaluate.py`; bandingkan model aktif dengan model Kaggle |
| Pelatihan ulang | jalankan `scripts/train.py --stage real` saat respons bertambah; strategi terbaik dipilih ulang otomatis |
| Versi model | metadata mencatat sumber data, strategi, jumlah baris, dan waktu pelatihan; ditampilkan di sidebar |
| Privasi | tidak ada penyimpanan data di aplikasi; unggahan diproses di memori; kolom pribadi dibuang; unduhan tanpa identitas; repositori privat; sel agregat < 5 orang disembunyikan; laporan berisi contoh jawaban disimpan di folder yang di-*gitignore* |
| Keamanan penggunaan | penafian "bukan diagnosis" di setiap halaman; aturan pengaman rujukan untuk 10% prediksi tertinggi |

## 7. Peninjauan Proyek

**Yang berhasil:** integrasi RF → SMART berjalan dari satu siswa hingga 20.000 siswa, dengan hasil identik dengan notebook. Setiap rekomendasi dapat ditelusuri ke kontribusi kriteria. Pipeline data riil siap pakai begitu ekspor tersedia.

**Yang diperbaiki selama deployment:** bobot Exercise profil A yang berjumlah 1,05; *bug* `criteria_plot` di notebook; normalisasi satu siswa dengan batas referensi.

**Pengembangan lanjutan:** validasi bobot oleh pakar BK; segmentasi siswa (*clustering*) dan aturan asosiasi dari rancangan awal; bobot SMART yang diturunkan dari *feature importance*; pengumpulan data berkala (longitudinal).
