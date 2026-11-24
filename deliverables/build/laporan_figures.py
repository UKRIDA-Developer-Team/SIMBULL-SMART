"""Figures for the technical report (Laporan Teknis Data Mining).

Run with the app's virtual environment:  app/.venv/bin/python deliverables/build/laporan_figures.py
Output: deliverables/laporan-dm/figures/
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "laporan-dm" / "figures"
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams["font.family"] = ["Calibri", "Carlito", "DejaVu Sans"]
INK, TEAL, MINT, GREY, LINE = "#1F3864", "#0F4C5C", "#E3F1EF", "#F4F6F6", "#9A9A9A"


def box(ax, x, y, w, h, title, body="", fill=MINT):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=fill, ec=TEAL, lw=1.0))
    if body:
        ax.text(x + w / 2, y + h - 0.2, title, ha="center", va="top", fontsize=8.2, fontweight="bold", color=INK)
        ax.text(x + w / 2, y + h - 0.52, body, ha="center", va="top", fontsize=7.3, color="#333333",
                linespacing=1.35)
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center", fontsize=8.2, fontweight="bold", color=INK)


def arrow(ax, x0, y0, x1, y1):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=10, color=TEAL, lw=1.0))


def zone(ax, x, y, w, h, label):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.1",
                                fc="white", ec=LINE, lw=0.9, ls="--"))
    ax.text(x + 0.2, y + h - 0.25, label, ha="left", va="top", fontsize=8.6, style="italic", color="#444444")


def arsitektur():
    fig, ax = plt.subplots(figsize=(7.2, 4.0), dpi=220)
    ax.set_xlim(0, 14.4); ax.set_ylim(0, 8.0); ax.axis("off")

    # Offline training
    zone(ax, 0.1, 0.1, 5.4, 7.8, "Pelatihan offline (laptop)")
    box(ax, 0.4, 5.75, 2.35, 1.5, "Kaggle", "1 juta baris\nusia 14–25\nsplit 80/20")
    box(ax, 2.95, 5.75, 2.35, 1.5, "Google Form", "304 respons\nsiswa SMA\n(rahasia)")
    box(ax, 0.4, 3.3, 4.9, 1.75, "scripts/train.py",
        "pralatih RF, random search,\nperbandingan algoritma,\n7 strategi latih ulang")
    box(ax, 0.4, 0.4, 4.9, 2.2, "app/models/",
        "model Kaggle dan model aktif (.joblib)\nmetadata: fitur, batas SMART,\nmedian imputasi, kuantil referensi\nringkasan data riil (agregat)", fill=GREY)
    arrow(ax, 1.575, 5.75, 2.2, 5.05); arrow(ax, 4.125, 5.75, 3.5, 5.05)
    arrow(ax, 2.85, 3.3, 2.85, 2.6)

    # Streamlit app
    zone(ax, 6.0, 0.1, 8.3, 7.8, "Aplikasi web: Streamlit Community Cloud")
    box(ax, 6.3, 5.75, 7.7, 1.5, "streamlit_app.py + ui.py",
        "bilah atas: menu halaman, sakelar Aplikasi | Laporan,\nbahasa ID | EN, pilihan model")
    box(ax, 6.3, 3.3, 3.75, 1.75, "Aplikasi (guru BK)", "Beranda, Nilai siswa,\nNilai kelas, Bantuan")
    box(ax, 10.25, 3.3, 3.75, 1.75, "Laporan teknis", "Bab 1–8\nreport.py, spk/plots.py")
    box(ax, 6.3, 0.4, 7.7, 2.2, "spk/ (logika tanpa Streamlit)",
        "gform.py: jawaban kuesioner menjadi 11 fitur\nmodel.py: prediksi Random Forest\nsmart.py: utilitas, prioritas, peringkat, sensitivitas\n"
        "recommend.py, explain.py, xai.py: rekomendasi dan penjelasan", fill=GREY)
    arrow(ax, 8.175, 5.75, 8.175, 5.05); arrow(ax, 12.125, 5.75, 12.125, 5.05)
    arrow(ax, 8.175, 3.3, 8.175, 2.6); arrow(ax, 12.125, 3.3, 12.125, 2.6)

    # Models are loaded by the app, never trained there
    arrow(ax, 5.3, 1.5, 6.3, 1.5)
    ax.text(5.8, 1.65, "dimuat", ha="center", va="bottom", fontsize=7, color="#555555", style="italic")

    fig.tight_layout(pad=0.1)
    fig.savefig(OUT / "gambar_arsitektur.png")
    plt.close(fig)


arsitektur()
print("->", OUT)
