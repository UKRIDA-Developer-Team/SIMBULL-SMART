# Fase 5 — Evaluation

**Proyek:** Sistem Rekomendasi Penanganan Kecemasan Siswa SMA Menggunakan Metode SMART
**Metodologi:** CRISP-DM — Fase 5 dari 6

---

## 1. Tujuan Fase

Menilai apakah hasil Fase 4 benar-benar menjawab tujuan bisnis yang dirumuskan pada Fase 1 — bukan sekadar mencapai metrik teknis yang bagus. Fase ini menutup dengan keputusan: lanjut ke Deployment, kembali ke fase sebelumnya, atau menghentikan proyek.

Evaluasi dilakukan dalam tiga lapis:

| Lapis | Pertanyaan yang dijawab |
|---|---|
| **Teknis** | Seberapa baik model dan modul SMART bekerja secara kuantitatif? |
| **Keputusan** | Apakah peringkat rekomendasi masuk akal dan stabil? |
| **Bisnis** | Apakah kriteria sukses Fase 1 tercapai, dan apakah sistem layak dipakai sekolah? |

---

## 2. Lapis 1 — Evaluasi Teknis

### 2.1 Evaluasi Model Klasifikasi

Metrik yang dilaporkan untuk setiap model kandidat:

| Metrik | Rumus / arti | Peran |
|---|---|---|
| Akurasi | Proporsi prediksi benar | Gambaran umum, **bukan** metrik utama |
| Precision (per kelas) | TP / (TP + FP) | Seberapa tepat penandaan sebuah kelas |
| **Recall kelas "Tinggi"** | TP / (TP + FN) | **Metrik utama** — mengukur siswa berisiko yang tidak terlewat |
| F1-score makro | Rata-rata harmonik precision-recall antar kelas | Ringkasan adil pada kelas timpang |
| ROC-AUC (One-vs-Rest) | Kemampuan membedakan kelas | Pembanding antar model |

**Contoh format *confusion matrix*** (angka ilustratif, diisi dengan hasil sebenarnya):

| Aktual \ Prediksi | Rendah | Sedang | Tinggi |
|---|---|---|---|
| **Rendah** | 34 | 5 | 1 |
| **Sedang** | 6 | 41 | 5 |
| **Tinggi** | 1 | 4 | 25 |

Dari matriks di atas: recall kelas Tinggi = 25 / (1 + 4 + 25) = 0,833. Angka ini yang menentukan apakah ambang keberhasilan D4 (≥ 0,85) tercapai; bila belum, ambang probabilitas kelas Tinggi diturunkan atau strategi penyeimbangan kelas ditinjau ulang.

Sel yang paling perlu diperhatikan adalah **baris Tinggi kolom Rendah** — siswa berisiko yang diprediksi aman. Satu kasus pun pada sel ini wajib ditelusuri karakteristiknya.

### 2.2 Evaluasi Model Clustering

| Metrik | Ambang | Keterangan |
|---|---|---|
| Silhouette Score | ≥ 0,50 | Kepaduan dan keterpisahan cluster |
| Davies-Bouldin Index | Semakin kecil semakin baik | Pembanding antar nilai *k* |
| Ukuran cluster | Tidak ada cluster < 5% total responden | Cluster terlalu kecil sulit dijadikan dasar program |
| Kebermaknaan profil | Penilaian guru BK | Cluster harus dikenali sebagai tipe siswa yang nyata |

### 2.3 Evaluasi Aturan Asosiasi

Aturan dinilai dari support, confidence, dan lift, lalu disaring lagi secara manual: aturan yang secara logika hanya menyatakan ulang definisi (redundan) atau tidak dapat ditindaklanjuti dibuang meskipun metriknya tinggi. Target minimal: 10 aturan bermakna dengan lift > 1.

---

## 3. Lapis 2 — Evaluasi Modul Keputusan (SMART)

### 3.1 Uji Sensitivitas Bobot

Setiap bobot kriteria diubah ±10% dan ±20% secara bergantian (bobot lain dinormalisasi ulang), lalu diperiksa apakah peringkat berubah.

| Skenario | Yang diamati | Ambang lolos |
|---|---|---|
| Bobot C1 naik/turun 10% | Perubahan alternatif peringkat 1 | Tidak berubah pada ≥ 90% kasus uji |
| Seluruh bobot diacak ±10% (100 iterasi) | Stabilitas tiga besar | Komposisi tiga besar tetap pada ≥ 80% iterasi |
| Bobot disamakan rata (w = 1/7) | Arah peringkat | Alternatif peringkat 1 masih masuk tiga besar |

Sistem yang peringkatnya berubah drastis oleh perubahan bobot kecil tidak layak dipakai untuk keputusan yang menyangkut siswa.

### 3.2 Kesesuaian dengan Penilaian Pakar

Sejumlah kasus uji (disarankan 20–30 profil siswa yang mewakili seluruh segmen dan level) diberikan kepada guru BK atau psikolog sekolah untuk diperingkat secara manual, lalu dibandingkan dengan keluaran sistem.

| Ukuran | Cara hitung | Target |
|---|---|---|
| Kesesuaian peringkat pertama | Proporsi kasus dengan alternatif teratas sama | ≥ 80% |
| Kesesuaian tiga besar | Proporsi irisan tiga besar sistem dan pakar | ≥ 70% |
| Korelasi peringkat | Spearman's rho antara urutan sistem dan pakar | ≥ 0,70 |
| Kesepakatan kategoris | Cohen's Kappa untuk level indikasi | ≥ 0,60 (kesepakatan substansial) |

Ketidaksesuaian tidak otomatis berarti sistem salah. Setiap perbedaan ditelusuri: bila pakar mempertimbangkan informasi yang tidak ada di kuesioner, temuan itu menjadi masukan untuk revisi instrumen, bukan revisi bobot.

### 3.3 Uji Aturan Pengaman

Diperiksa secara khusus bahwa untuk setiap kasus uji dengan level "Tinggi", alternatif A1 (konseling BK) dan A10 (rujukan profesional) selalu muncul sebagai rekomendasi pendamping, apa pun hasil skor SMART.

---

## 4. Lapis 3 — Evaluasi Bisnis

Setiap kriteria sukses bisnis dari Fase 1 diperiksa satu per satu.

| Kode | Kriteria sukses (Fase 1) | Cara verifikasi | Status |
|---|---|---|---|
| B1 | ≥ 90% siswa terskrining dalam satu periode | Rasio responden valid terhadap populasi sasaran | … |
| B2 | ≤ 1 hari kerja dari data terkumpul ke rekomendasi | Pengukuran waktu proses ujung-ke-ujung | … |
| B3 | ≥ 80% rekomendasi dinilai sesuai oleh guru BK | Kuesioner penilaian pada kasus uji | … |
| B4 | ≥ 75% siswa bersedia menjalankan rekomendasi teratas | Survei kecil pada uji coba terbatas | … |
| B5 | 100% rekomendasi disertai penjelasan | Pemeriksaan keluaran sistem | … |

Kolom status diisi Tercapai / Tercapai sebagian / Belum tercapai, disertai bukti angka.

### 4.1 Evaluasi terhadap Tujuan Bisnis

| Tujuan bisnis Fase 1 | Terpenuhi bila | Catatan evaluasi |
|---|---|---|
| Preventif, bukan reaktif | Sistem mampu menandai siswa berisiko sebelum penurunan prestasi terjadi | Perlu data periode berikutnya untuk pembuktian penuh |
| Objektif dan konsisten | Profil siswa yang sama selalu menghasilkan rekomendasi yang sama | Diuji dengan input berulang |
| Cepat dan berkelanjutan | Proses skrining otomatis berjalan tanpa intervensi manual | Diukur pada B2 |
| Dapat dijelaskan | Setiap keluaran memuat faktor dominan dan skor kriteria | Diuji pada B5 |
| Efisien secara sumber daya | Daftar prioritas siswa dapat dipakai menyusun jadwal konseling | Dinilai bersama guru BK |

---

## 5. Peninjauan Proses (*Review Process*)

Seluruh rantai pekerjaan ditinjau ulang untuk memastikan tidak ada langkah kritis yang terlewat.

| Fase | Butir pemeriksaan | Risiko bila terlewat |
|---|---|---|
| Business Understanding | Alternatif dan kriteria sudah divalidasi guru BK | Sistem menjawab masalah yang salah |
| Data Understanding | Pola missing sudah diklasifikasikan (MCAR/MAR/MNAR) | Imputasi keliru menciptakan bias |
| Data Preparation | *Reverse coding* diterapkan pada seluruh butir positif | Indeks domain tidak bermakna |
| Data Preparation | P01–P05 tidak ikut sebagai prediktor | *Label leakage*, akurasi semu |
| Data Preparation | Normalisasi dan SMOTE hanya dari/di data latih | Kebocoran data uji, metrik terlalu optimistis |
| Modeling | Parameter dan *random state* tercatat | Hasil tidak dapat direproduksi |
| Modeling | Bobot SMART punya dasar empiris | Rekomendasi kembali subjektif |
| Evaluation | Metrik dilaporkan per kelas, bukan hanya rata-rata | Kelemahan pada kelas minoritas tersembunyi |

---

## 6. Keputusan Lanjutan (*Determine Next Steps*)

| Kondisi | Keputusan |
|---|---|
| Seluruh kriteria D dan S terpenuhi, kriteria B utama (B3, B5) terpenuhi | **Lanjut ke Fase 6 — Deployment** |
| Recall kelas Tinggi < 0,85 | Kembali ke Fase 4: setel ulang ambang, ubah strategi penyeimbangan, atau tambah data |
| Silhouette < 0,50 atau cluster tidak bermakna | Kembali ke Fase 3: tinjau ulang komposisi indeks domain |
| Kesesuaian dengan pakar < 80% | Kembali ke Fase 1/4: tinjau ulang daftar alternatif, nilai kriteria, atau bobot |
| Jumlah responden jauh di bawah target | Perpanjang pengumpulan data sebelum melanjutkan |

Untuk keperluan mata kuliah, sistem tetap dapat di-*deploy* sebagai prototipe meskipun sebagian ambang belum tercapai — asalkan keterbatasan tersebut dinyatakan terbuka pada laporan dan pada antarmuka aplikasi.

---

## 7. Risiko dan Catatan Etis

| Risiko | Dampak | Mitigasi |
|---|---|---|
| *False negative* pada siswa berisiko | Siswa yang butuh bantuan tidak terjangkau | Recall diprioritaskan; jalur pelaporan mandiri tetap tersedia di samping sistem |
| Pelabelan dan stigma | Siswa merasa dicap "bermasalah" | Istilah yang dipakai adalah "indikasi" dan "prioritas tindak lanjut"; hasil individual hanya dapat diakses guru BK |
| Ketergantungan berlebih pada sistem | Guru BK berhenti melakukan observasi langsung | Antarmuka menegaskan status sistem sebagai alat bantu; keputusan akhir tetap pada manusia |
| Kebocoran data siswa | Pelanggaran privasi anak di bawah umur | Anonimisasi, akses berjenjang, tanpa penyimpanan nama pada dataset analisis |
| Perubahan kondisi siswa seiring waktu | Model menjadi usang | Pemantauan berkala dan pelatihan ulang (dibahas di Fase 6) |
| Salah tafsir sebagai diagnosis | Penanganan keliru | Penyangkalan eksplisit di setiap keluaran: bukan alat diagnosis klinis |

---

## 8. Keluaran Fase

| Berkas | Isi |
|---|---|
| `laporan_evaluasi_model.md` | Tabel metrik, confusion matrix, kurva ROC, perbandingan model |
| `laporan_uji_sensitivitas.md` | Hasil variasi bobot dan stabilitas peringkat |
| `laporan_validasi_pakar.md` | Perbandingan peringkat sistem vs guru BK dan analisis perbedaannya |
| `checklist_kriteria_sukses.md` | Status B1–B5, D1–D6, S1–S5 |
| `keputusan_fase5.md` | Keputusan lanjut/ulang beserta alasannya |

Bila keputusan yang diambil adalah lanjut, seluruh berkas model dan bobot dibekukan versinya sebelum masuk Fase 6 — Deployment.
