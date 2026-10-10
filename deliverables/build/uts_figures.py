"""Figures for the Laporan UTS SPK: decision flow, activity schedule (bar chart), case-study contributions."""
import json
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Patch  # noqa: E402

DIR = Path(__file__).resolve().parents[1] / "uts"
OUT = DIR / "figures"
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams["font.family"] = ["Times New Roman", "DejaVu Serif"]
TEAL, MINT, GREY, AMBER = "#0F4C5C", "#E3F1EF", "#F4F6F6", "#FFF2CC"


def box(ax, x, y, w, h, text, fill=MINT, size=8.5, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06", fc=fill, ec=TEAL, lw=1.1))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size, fontweight="bold" if bold else "normal")


def arrow(ax, x0, y0, x1, y1, color=TEAL):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=11, color=color, lw=1.1))


def flow():
    """input -> model -> output -> recommendation (top to bottom)."""
    fig, ax = plt.subplots(figsize=(6.4, 5.0), dpi=220)
    ax.set_xlim(0, 12.8); ax.set_ylim(-0.1, 9.8); ax.axis("off")
    box(ax, 0.4, 8.2, 5.2, 1.4, "INPUT\nProfil siswa: 11 fitur (kuesioner,\nisian nilai, atau berkas CSV)", size=7.8)
    box(ax, 7.0, 8.2, 5.4, 1.4, "PARAMETER KEPUTUSAN\nBobot profil A/B/C, batas min-maks\nreferensi, ambang pengaman P90", fill=AMBER, size=7.8)
    box(ax, 0.4, 6.0, 5.2, 1.4, "MODEL DATA MINING\nRandom Forest Regressor -> prediksi\nskor kecemasan 0-10 (kriteria C1)", fill=GREY, size=7.8)
    box(ax, 0.4, 3.8, 12.0, 1.4, "MODEL SPK - SMART\nMatriks keputusan X: C1 (prediksi RF) + C2-C8 (dari input)"
        "  ->  utilitas u_ij min-maks (benefit / cost)", size=7.8)
    box(ax, 0.4, 1.9, 5.6, 1.3, "Keputusan 1: skor prioritas\nP_i = jumlah (1/8) x u_ij", fill=GREY, size=7.8)
    box(ax, 6.8, 1.9, 5.6, 1.3, "Keputusan 2: skor alternatif\nS_ik = jumlah w_kj x u_ij  (A1-A5)", fill=GREY, size=7.8)
    box(ax, 0.4, 0.0, 5.6, 1.3, "OUTPUT\nPeringkat siswa: siapa\nditangani lebih dulu", size=7.8)
    box(ax, 6.8, 0.0, 5.6, 1.3, "REKOMENDASI\nAlternatif terbaik + 3 teratas + kontribusi;\npersentil >= 90 -> Konseling + rujukan", fill=AMBER, size=7.6)
    arrow(ax, 3.0, 8.2, 3.0, 7.4)
    arrow(ax, 3.0, 6.0, 3.0, 5.2)
    ax.plot([5.6, 6.3, 6.3], [8.9, 8.9, 5.3], color=TEAL, lw=1.1)
    arrow(ax, 6.3, 5.4, 6.3, 5.2)
    ax.text(6.45, 6.7, "C2-C8\nlangsung", fontsize=7, color=TEAL, va="center")
    arrow(ax, 9.7, 8.2, 9.7, 5.2)
    arrow(ax, 3.2, 3.8, 3.2, 3.2)
    arrow(ax, 9.6, 3.8, 9.6, 3.2)
    arrow(ax, 3.2, 1.9, 3.2, 1.3)
    arrow(ax, 9.6, 1.9, 9.6, 1.3)
    fig.tight_layout(pad=0.1)
    fig.savefig(OUT / "gambar_alur.png")
    plt.close(fig)


def gantt():
    tasks = [
        ("Identifikasi masalah & studi literatur", "2026-09-01", "2026-09-09", True),
        ("Business understanding (kriteria, alternatif)", "2026-09-05", "2026-09-10", True),
        ("Pengumpulan data (Kaggle + Google Form)", "2026-09-08", "2026-09-20", True),
        ("Pemahaman & persiapan data", "2026-09-12", "2026-09-22", True),
        ("Pemodelan RF + SMART (notebook Colab)", "2026-09-16", "2026-09-24", True),
        ("Pengembangan aplikasi Streamlit", "2026-09-24", "2026-09-26", True),
        ("Pengujian & validasi (pytest, sensitivitas)", "2026-09-25", "2026-09-27", True),
        ("Dokumentasi (laporan DM, manual, PPT, PKM)", "2026-09-25", "2026-09-29", True),
        ("Simulasi pembersihan data & rekayasa fitur", "2026-09-30", "2026-10-10", True),
        ("Laporan UTS, spreadsheet, README", "2026-10-10", "2026-10-11", True),
        ("Latih ulang data riil, deployment, uji pengguna", "2026-10-12", "2026-11-06", False),
    ]
    fig, ax = plt.subplots(figsize=(6.4, 3.6), dpi=220)
    for i, (name, s, e, done) in enumerate(tasks):
        s, e = date.fromisoformat(s), date.fromisoformat(e)
        ax.barh(i, (e - s).days + 1, left=mdates.date2num(s), height=0.6,
                color=TEAL if done else "white", edgecolor=TEAL, hatch=None if done else "///", lw=1)
    ax.set_yticks(range(len(tasks)), [t[0] for t in tasks], fontsize=7)
    ax.invert_yaxis()
    ax.xaxis_date()
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
    ax.tick_params(axis="x", labelsize=7)
    ax.grid(axis="x", color="#DDDDDD", lw=0.6)
    ax.set_axisbelow(True)
    ax.axvline(mdates.date2num(date(2026, 10, 10)), color="#B8860B", lw=1, ls="--")
    ax.text(mdates.date2num(date(2026, 10, 10)) - 0.4, -0.55, "pengumpulan UTS", ha="right", fontsize=6.5, color="#B8860B")
    ax.legend(handles=[Patch(fc=TEAL, ec=TEAL, label="selesai"), Patch(fc="white", ec=TEAL, hatch="///", label="rencana")],
              fontsize=7, loc="lower left", frameon=False)
    ax.set_xlabel("Tanggal (2026)", fontsize=7.5)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout(pad=0.2)
    fig.savefig(OUT / "gambar_jadwal.png")
    plt.close(fig)


def contrib():
    d = json.loads((DIR / "uts_data.json").read_text())
    s = d["students"][0]
    raw = d["weights_A_raw"]
    names = {"Sleep": "Tidur", "Exercise": "Olahraga", "Study": "Strategi belajar", "Counseling": "Konseling", "Relaxation": "Relaksasi"}
    alts = d["alternatives"]
    crit = d["criteria"]
    colors = ["#0F4C5C", "#2E86AB", "#7FB7BE", "#D3D5D4", "#F2C14E", "#F78154", "#B5525C", "#5D576B"]
    fig, ax = plt.subplots(figsize=(6.4, 2.7), dpi=220)
    order = sorted(alts, key=lambda a: s["app"]["A"]["scores"][a])
    for i, a in enumerate(order):
        tot = sum(raw[a].values())
        left = 0
        for j, c in enumerate(crit):
            v = raw[a][c] / tot * s["utility"][c]
            ax.barh(i, v, left=left, color=colors[j], edgecolor="white", lw=0.5, label=f"C{j + 1}" if i == 0 else None)
            left += v
        ax.text(left + 0.01, i, f"{left:.4f}", va="center", fontsize=7)
    ax.set_yticks(range(len(order)), [names[a] for a in order], fontsize=7.5)
    ax.set_xlim(0, 1.0)
    ax.set_xlabel("Skor SMART = jumlah (bobot x utilitas)", fontsize=7.5)
    ax.tick_params(axis="x", labelsize=7)
    ax.legend(ncol=8, fontsize=6.5, loc="upper center", bbox_to_anchor=(0.5, 1.2), frameon=False)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    fig.tight_layout(pad=0.2)
    fig.savefig(OUT / "gambar_kontribusi_s01.png")
    plt.close(fig)


flow()
gantt()
contrib()
print("->", OUT)
