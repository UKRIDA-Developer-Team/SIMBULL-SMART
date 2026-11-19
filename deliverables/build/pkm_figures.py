"""Diagrams for the PKM-KC proposal (black-and-white friendly, Times New Roman)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "pkm" / "figures"
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams["font.family"] = ["Times New Roman", "DejaVu Serif"]
TEAL, MINT, GREY = "#0F4C5C", "#E3F1EF", "#F4F6F6"


def box(ax, x, y, w, h, text, fill=MINT, size=9, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.05",
                                fc=fill, ec=TEAL, lw=1.1))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size,
            fontweight="bold" if bold else "normal", wrap=True)


def arrow(ax, x0, y0, x1, y1):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=11, color=TEAL, lw=1.1))


def tahapan():
    fig, ax = plt.subplots(figsize=(6.4, 1.95), dpi=220)
    ax.set_xlim(0, 13.1); ax.set_ylim(0, 3.95); ax.axis("off")
    steps = [
        ("1. Pengumpulan\ndata", "Kuesioner\nGoogle Form\nsiswa SMA +\ndata Kaggle"),
        ("2. Persiapan\ndata", "Pembersihan,\nanonimisasi,\n11 fitur +\ntarget"),
        ("3. Pemodelan\nRandom Forest", "Pralatih\nKaggle, latih\nulang dengan\ndata riil"),
        ("4. Keputusan\nSMART", "Utilitas,\nprioritas,\nperingkat 5\nalternatif"),
        ("5. Konstruksi\naplikasi", "Web Streamlit\nbilingual +\npenjelasan\nhasil"),
        ("6. Pengujian", "MAE, CV,\nsensitivitas,\nkeadilan, uji\npengguna BK"),
    ]
    w, h, gap = 1.9, 1.55, 0.26
    for i, (t, d) in enumerate(steps):
        x = 0.1 + i * (w + gap)
        box(ax, x, 2.75, w, 1.0, t, size=7.4, bold=True)
        box(ax, x, 0.9, w, h, d, fill=GREY, size=6.9)
        arrow(ax, x + w / 2, 2.75, x + w / 2, 0.9 + h)
        if i < len(steps) - 1:
            arrow(ax, x + w, 3.25, x + w + gap, 3.25)
    ax.annotate("", xy=(0.1 + 2 * (w + gap), 0.55), xytext=(0.1 + 5 * (w + gap) + w, 0.55),
                arrowprops=dict(arrowstyle="-|>", color="#888888", lw=0.9, linestyle="--"))
    ax.text(6.9, 0.2, "umpan balik hasil uji → perbaikan model dan antarmuka", ha="center", fontsize=7, color="#555555", style="italic")
    fig.tight_layout(pad=0.1)
    fig.savefig(OUT / "gambar_tahapan.png")


def arsitektur():
    fig, ax = plt.subplots(figsize=(6.4, 3.3), dpi=220)
    ax.set_xlim(0, 12.8); ax.set_ylim(0, 6.6); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0.1, 0.2), 3.9, 6.1, boxstyle="round,pad=0.02", fc="white", ec="#999999", ls="--"))
    ax.text(2.05, 6.0, "Pelatihan (offline)", ha="center", fontsize=8.5, style="italic")
    box(ax, 0.4, 4.5, 3.3, 1.0, "Kaggle usia 14–25\n692.545 baris (sekunder)", size=7.8)
    box(ax, 0.4, 3.1, 3.3, 1.0, "Google Form siswa SMA\n(rahasia, tanpa identitas)", size=7.8)
    box(ax, 0.4, 0.8, 3.3, 1.6, "scripts/train.py\n7 strategi latih ulang\n+ validasi silang", fill=GREY, size=7.8)
    arrow(ax, 2.05, 4.5, 2.05, 4.1); arrow(ax, 2.05, 3.1, 2.05, 2.4)
    box(ax, 4.6, 2.6, 2.1, 1.4, "Model RF\n(.joblib)\n+ metadata", fill=GREY, size=7.8)
    arrow(ax, 3.7, 1.6, 4.6, 3.0)
    ax.add_patch(FancyBboxPatch((7.2, 0.2), 5.5, 6.1, boxstyle="round,pad=0.02", fc="white", ec="#999999", ls="--"))
    ax.text(9.95, 6.0, "Aplikasi web (Streamlit Community Cloud)", ha="center", fontsize=8.5, style="italic")
    layers = [("Antarmuka ID/EN: Aplikasi (guru BK)\n+ Laporan teknis (Bab 1–8)", 4.8),
              ("Pemetaan jawaban kuesioner → 11 fitur", 3.75),
              ("Prediksi skor kecemasan (Random Forest)", 2.7),
              ("SMART: prioritas, peringkat, sensitivitas", 1.65),
              ("Penjelasan + aturan pengaman + keadilan", 0.6)]
    for t, y in layers:
        box(ax, 7.5, y, 4.9, 0.8, t, size=7.6)
    for y in (4.8, 3.75, 2.7, 1.65):
        arrow(ax, 9.95, y, 9.95, y - 0.25)
    arrow(ax, 6.7, 3.3, 7.5, 3.1)
    fig.tight_layout(pad=0.1)
    fig.savefig(OUT / "gambar_arsitektur.png")


tahapan()
arsitektur()
print("->", OUT)
