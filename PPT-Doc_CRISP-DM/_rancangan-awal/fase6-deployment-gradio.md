# Fase 6 — Deployment (Gradio)

**Proyek:** Sistem Rekomendasi Penanganan Kecemasan Siswa SMA Menggunakan Metode SMART
**Metodologi:** CRISP-DM — Fase 6 dari 6

---

## 1. Tujuan Fase

Membawa model dan modul SMART yang sudah dievaluasi ke dalam bentuk yang benar-benar dapat dipakai guru BK, lalu menyiapkan rencana pemantauan dan pemeliharaannya. Empat aktivitas baku CRISP-DM:

| Aktivitas | Wujud pada proyek ini |
|---|---|
| *Plan Deployment* | Aplikasi web berbasis **Gradio** yang membungkus pipeline preprocessing → klasifikasi → SMART |
| *Plan Monitoring & Maintenance* | Jadwal pemantauan kinerja dan pelatihan ulang model |
| *Produce Final Report* | Laporan akhir proyek dan panduan penggunaan |
| *Review Project* | Refleksi apa yang berhasil dan apa yang perlu diperbaiki |

---

## 2. Mengapa Gradio

| Pertimbangan | Penjelasan |
|---|---|
| Cepat dibangun | Antarmuka dibuat langsung dari Python, tanpa perlu HTML/CSS/JS terpisah |
| Satu bahasa | Pipeline scikit-learn dan antarmuka berada dalam satu berkas proyek — tidak ada risiko perbedaan versi preprocessing antara pelatihan dan penyajian |
| Cocok untuk prototipe | Sesuai lingkup mata kuliah: fokus pada isi model, bukan pada rekayasa web |
| Mudah dibagikan | Dapat dijalankan lokal, dibagikan lewat tautan sementara, atau dihosting gratis di Hugging Face Spaces |
| Komponen siap pakai | Slider, radio, dataframe, dan plot tersedia langsung — pas untuk kuesioner berskala Likert |

Keterbatasannya juga dicatat: Gradio bukan aplikasi multi-pengguna dengan manajemen akun bawaan, sehingga otentikasi sederhana perlu ditambahkan dan penyimpanan data dibuat seminimal mungkin.

---

## 3. Arsitektur Sistem

```
┌──────────────────────────────────────────────────────────────────┐
│                     Antarmuka Gradio (app.py)                    │
│  Tab 1: Skrining Individu   Tab 2: Unggah Batch (CSV)            │
│  Tab 3: Dashboard Sekolah   Tab 4: Tentang & Batasan             │
└───────────────┬──────────────────────────────────────────────────┘
                │
        ┌───────▼────────┐
        │  preprocess.py │  imputer.pkl · scaler.pkl · reverse coding
        └───────┬────────┘   → 8 indeks domain + fitur turunan
                │
    ┌───────────┼────────────┐
    │           │            │
┌───▼────┐ ┌────▼─────┐ ┌────▼──────────┐
│ model_ │ │ model_   │ │ aturan_       │
│ klasi- │ │ cluster  │ │ asosiasi.csv  │
│ fikasi │ │ (KMeans) │ │               │
└───┬────┘ └────┬─────┘ └────┬──────────┘
    │           │            │
    └───────────┼────────────┘
                │  {level, segmen, 3 faktor dominan}
        ┌───────▼────────┐
        │ smart_engine.py│  bobot_kriteria.json · matriks_keputusan.csv
        └───────┬────────┘
                │
     Peringkat 3 penanganan teratas + alasan + skor kriteria
```

Alur ini menegaskan satu hal penting: objek `imputer.pkl` dan `scaler.pkl` yang dipakai aplikasi harus objek yang **sama** dengan yang dihasilkan Fase 3. Menghitung ulang normalisasi dari input tunggal akan menghasilkan angka yang keliru.

---

## 4. Struktur Proyek

```
spk-kecemasan/
├── app.py                     # antarmuka Gradio
├── src/
│   ├── preprocess.py          # reverse coding, indeks domain, transformasi
│   ├── smart_engine.py        # perhitungan SMART
│   └── explain.py             # penyusun kalimat penjelasan
├── models/
│   ├── model_klasifikasi.pkl
│   ├── model_cluster.pkl
│   ├── imputer.pkl
│   └── scaler.pkl
├── config/
│   ├── bobot_kriteria.json
│   ├── matriks_keputusan.csv
│   └── alternatif.json
├── data/
│   └── contoh_batch.csv
├── requirements.txt
└── README.md
```

---

## 5. Rancangan Antarmuka

| Tab | Pengguna | Isi |
|---|---|---|
| **Skrining Individu** | Guru BK / siswa | Form kuesioner ringkas (slider dan radio) → tombol proses → keluaran level indikasi, faktor dominan, dan tiga rekomendasi teratas beserta skor |
| **Unggah Batch** | Guru BK | Unggah CSV hasil ekspor Google Form → tabel hasil seluruh siswa, terurut berdasarkan prioritas → tombol unduh hasil |
| **Dashboard Sekolah** | Wali kelas / pimpinan | Distribusi level indikasi, sebaran segmen, rata-rata indeks per domain — seluruhnya agregat, tanpa identitas |
| **Tentang & Batasan** | Semua | Penjelasan metode, kriteria SMART, dan penyangkalan bahwa sistem bukan alat diagnosis |

Ketentuan tampilan: hasil individual tidak pernah menampilkan nama; kartu hasil selalu memuat kalimat alasan; alternatif A1 dan A10 selalu ikut ditampilkan bila level indikasi "Tinggi".

---

## 6. Implementasi Inti

### 6.1 `src/smart_engine.py`

```python
import json
import pandas as pd

class SmartEngine:
    """Perhitungan SMART: normalisasi utilitas linear + skor terbobot."""

    def __init__(self, path_bobot, path_matriks, path_alternatif):
        with open(path_bobot) as f:
            self.bobot = json.load(f)              # {"C1": 0.25, ...}
        self.matriks = pd.read_csv(path_matriks, index_col="kode")
        with open(path_alternatif) as f:
            self.alternatif = json.load(f)         # {"A1": {"nama": ..., "faktor": [...]}}
        self.cost = {"C5", "C6"}                   # kriteria bersifat cost

    def _utilitas(self, nilai, kriteria, vmin=1, vmax=5):
        if kriteria in self.cost:
            return (vmax - nilai) / (vmax - vmin)
        return (nilai - vmin) / (vmax - vmin)

    def _sesuaikan_konteks(self, matriks, faktor_dominan, level):
        """C1 dan C2 disesuaikan dengan profil siswa hasil data mining."""
        m = matriks.copy()
        skor_level = {"Rendah": 1, "Sedang": 3, "Tinggi": 5}[level]
        for kode in m.index:
            faktor_alt = set(self.alternatif[kode]["faktor"])
            irisan = len(faktor_alt & set(faktor_dominan))
            m.loc[kode, "C1"] = min(5, 1 + 2 * irisan)      # 1, 3, atau 5
            urgensi_alt = self.alternatif[kode]["urgensi"]  # 1-5
            m.loc[kode, "C2"] = 5 - abs(urgensi_alt - skor_level)
        return m

    def peringkat(self, faktor_dominan, level, top_n=3):
        m = self._sesuaikan_konteks(self.matriks, faktor_dominan, level)
        hasil = []
        for kode, baris in m.iterrows():
            skor = sum(
                self.bobot[k] * self._utilitas(baris[k], k) for k in self.bobot
            )
            hasil.append({
                "kode": kode,
                "penanganan": self.alternatif[kode]["nama"],
                "skor": round(skor, 3),
            })
        hasil = sorted(hasil, key=lambda x: x["skor"], reverse=True)

        # aturan pengaman: jalur konseling & rujukan wajib muncul saat level Tinggi
        terpilih = hasil[:top_n]
        if level == "Tinggi":
            kode_terpilih = {h["kode"] for h in terpilih}
            for wajib in ("A1", "A10"):
                if wajib not in kode_terpilih:
                    terpilih.append(next(h for h in hasil if h["kode"] == wajib))
        return terpilih, hasil
```

### 6.2 `app.py` (inti)

```python
import gradio as gr
import joblib
import pandas as pd

from src.preprocess import bangun_fitur, hitung_indeks_domain
from src.smart_engine import SmartEngine
from src.explain import susun_alasan

MODEL = joblib.load("models/model_klasifikasi.pkl")
CLUSTER = joblib.load("models/model_cluster.pkl")
SCALER = joblib.load("models/scaler.pkl")
SMART = SmartEngine("config/bobot_kriteria.json",
                    "config/matriks_keputusan.csv",
                    "config/alternatif.json")

NAMA_DOMAIN = {
    "indeks_tekanan_akademik": "F1",
    "indeks_defisit_tidur": "F2",
    "indeks_beban_digital": "F3",
    "indeks_tekanan_keluarga": "F4",
    "indeks_dukungan_sosial_rendah": "F5",
    "indeks_aktivitas_fisik_rendah": "F6",
    "indeks_beban_kegiatan": "F7",
    "indeks_koping_konsumtif": "F8",
}


def proses_satu_siswa(jawaban: dict):
    indeks = hitung_indeks_domain(jawaban)
    fitur = SCALER.transform(bangun_fitur(jawaban, indeks))

    level = MODEL.predict(fitur)[0]
    segmen = int(CLUSTER.predict(fitur)[0])

    dominan = sorted(indeks, key=indeks.get, reverse=True)[:3]
    kode_dominan = [NAMA_DOMAIN[d] for d in dominan]

    terpilih, semua = SMART.peringkat(kode_dominan, level)
    tabel = pd.DataFrame(terpilih)[["penanganan", "skor"]]
    return level, f"Segmen {segmen}", tabel, susun_alasan(level, dominan, indeks)


with gr.Blocks(title="SPK Penanganan Kecemasan Siswa SMA") as demo:
    gr.Markdown(
        "## Sistem Rekomendasi Penanganan Kecemasan Siswa SMA\n"
        "Metode SMART · Alat bantu skrining — **bukan alat diagnosis klinis**."
    )

    with gr.Tab("Skrining Individu"):
        with gr.Row():
            with gr.Column():
                tidur = gr.Slider(4, 12, value=7, step=0.5,
                                  label="Rata-rata durasi tidur per malam (jam)")
                belajar = gr.Slider(0, 12, value=2, step=0.5,
                                    label="Jam belajar mandiri per hari")
                medsos_tidur = gr.Radio(
                    ["Tidak pernah", "Jarang", "Kadang-kadang", "Sering", "Sangat sering"],
                    value="Kadang-kadang",
                    label="Menggunakan media sosial sebelum tidur")
                beban_tugas = gr.Radio(
                    ["Tidak pernah", "Jarang", "Kadang-kadang", "Sering", "Sangat sering"],
                    value="Sering",
                    label="Merasa tugas menumpuk pada waktu bersamaan")
                tekanan_ortu = gr.Radio(
                    ["Sangat tidak setuju", "Tidak setuju", "Netral", "Setuju", "Sangat setuju"],
                    value="Netral",
                    label="Takut mengecewakan orang tua bila nilai tidak sesuai harapan")
                # ... komponen lain untuk domain F5 - F8
                tombol = gr.Button("Proses", variant="primary")
            with gr.Column():
                out_level = gr.Label(label="Level indikasi")
                out_segmen = gr.Textbox(label="Segmen profil")
                out_tabel = gr.Dataframe(label="Rekomendasi penanganan (terurut)")
                out_alasan = gr.Markdown(label="Dasar rekomendasi")

        tombol.click(
            fn=lambda *a: proses_satu_siswa(dict(zip(
                ["tidur", "belajar", "medsos_tidur", "beban_tugas", "tekanan_ortu"], a))),
            inputs=[tidur, belajar, medsos_tidur, beban_tugas, tekanan_ortu],
            outputs=[out_level, out_segmen, out_tabel, out_alasan],
        )

    with gr.Tab("Unggah Batch"):
        berkas = gr.File(label="CSV hasil ekspor Google Form", file_types=[".csv"])
        tombol_batch = gr.Button("Proses seluruh responden", variant="primary")
        tabel_batch = gr.Dataframe(label="Hasil skrining — terurut berdasarkan prioritas")
        unduh = gr.File(label="Unduh hasil")
        tombol_batch.click(fn=proses_batch, inputs=berkas, outputs=[tabel_batch, unduh])

    with gr.Tab("Dashboard Sekolah"):
        gr.Markdown("Ringkasan agregat — tidak menampilkan data individual.")
        plot_level = gr.BarPlot(label="Distribusi level indikasi")
        plot_domain = gr.BarPlot(label="Rata-rata indeks per domain")

    with gr.Tab("Tentang & Batasan"):
        gr.Markdown(TEKS_BATASAN)

if __name__ == "__main__":
    demo.launch(auth=("bk_sekolah", "ganti_password"), share=False)
```

### 6.3 `requirements.txt`

```
gradio>=4.44
scikit-learn>=1.5
pandas>=2.2
numpy>=1.26
joblib>=1.4
mlxtend>=0.23
matplotlib>=3.9
```

---

## 7. Opsi Penerapan

| Opsi | Cara | Cocok untuk |
|---|---|---|
| **Lokal** | `python app.py` → `http://127.0.0.1:7860` | Demo di kelas, pengujian internal sekolah |
| **Tautan sementara** | `demo.launch(share=True)` — tautan aktif 72 jam | Presentasi jarak jauh, uji coba singkat |
| **Hugging Face Spaces** | Unggah repo, pilih SDK Gradio | Prototipe daring gratis; **hanya dengan data contoh, bukan data siswa asli** |
| **Server sekolah / Docker** | `docker build` + `docker run -p 7860:7860` | Penggunaan nyata dengan data siswa, di jaringan internal |

Untuk data siswa yang sebenarnya, penerapan di lingkungan internal sekolah lebih tepat daripada layanan publik.

---

## 8. Pemantauan dan Pemeliharaan

| Aspek | Mekanisme | Frekuensi |
|---|---|---|
| Kinerja model | Bandingkan prediksi dengan penilaian guru BK pada sampel kasus | Setiap semester |
| *Data drift* | Pantau pergeseran distribusi indeks domain terhadap data pelatihan | Setiap gelombang pengumpulan |
| Umpan balik pengguna | Kolom penilaian "rekomendasi ini sesuai / tidak sesuai" pada antarmuka | Berkelanjutan |
| Pelatihan ulang | Latih ulang bila recall kelas Tinggi turun > 10% atau ada ≥ 100 respons baru | Tahunan atau saat pemicu terpenuhi |
| Peninjauan bobot | Tinjau ulang bobot dan daftar alternatif bersama guru BK | Tahunan |
| Versi model | Catat versi model, tanggal pelatihan, dan metriknya di `README.md` | Setiap pembaruan |

Antarmuka menampilkan versi model dan tanggal pelatihan agar pengguna tahu seberapa mutakhir dasar rekomendasinya.

---

## 9. Privasi, Keamanan, dan Etika Penerapan

| Ketentuan | Penerapan teknis |
|---|---|
| Anonimisasi | Dataset analisis tidak memuat nama, sekolah, atau tanggal lahir lengkap |
| Akses berjenjang | Otentikasi `auth=` pada Gradio; dashboard agregat terpisah dari hasil individual |
| Minimalisasi penyimpanan | Hasil skrining individual tidak disimpan permanen oleh aplikasi kecuali diunduh guru BK |
| Persetujuan | Pengantar kuesioner memuat izin sekolah dan orang tua |
| Penyangkalan | Setiap keluaran memuat pernyataan bahwa sistem adalah alat bantu skrining, bukan diagnosis |
| Jalur rujukan | Kontak guru BK dan layanan profesional selalu ditampilkan pada hasil level "Tinggi" |

---

## 10. Laporan Akhir dan Peninjauan Proyek

### 10.1 Dokumen Akhir

| Berkas | Isi |
|---|---|
| `laporan_akhir.pdf` | Seluruh enam fase CRISP-DM, dari latar belakang sampai penerapan |
| `panduan_pengguna.md` | Cara menjalankan aplikasi, membaca hasil, dan menindaklanjuti |
| `README.md` | Instalasi, struktur proyek, versi model |
| Repositori kode | `app.py`, modul `src/`, model, dan konfigurasi |
| Slide presentasi akhir | Ringkasan proyek untuk sidang / presentasi kelas |

### 10.2 Bahan Refleksi

- Apakah kualitas dan jumlah data mencukupi, dan apa yang perlu diubah pada instrumen kuesioner untuk gelombang berikutnya?
- Butir mana yang reliabilitasnya rendah dan sebaiknya direvisi atau dibuang?
- Apakah delapan indeks domain merupakan pengelompokan terbaik, atau ada domain yang perlu dipecah?
- Bagian mana dari proses yang paling banyak menyita waktu, dan bagaimana mengotomatiskannya?
- Apakah guru BK benar-benar memakai keluaran sistem dalam pengambilan keputusan sehari-hari?

### 10.3 Arah Pengembangan Lanjutan

Deployment bukan akhir siklus. Bila kondisi berubah — kurikulum baru, kebijakan sekolah baru, atau pola perilaku siswa yang bergeser — proyek kembali ke Fase 1 Business Understanding. Arah pengembangan yang paling relevan: pengumpulan data berkala agar analisis menjadi longitudinal, dan penggabungan dengan jalur estimasi indikator berbasis ekspresi wajah sebagai sumber data pelengkap, dengan kajian etika dan persetujuan tersendiri.
