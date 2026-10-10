"""UTS SPK spreadsheet: the full SMART calculation as traceable Excel formulas.

Input: deliverables/uts/uts_data.json (from uts_data.py). Output: deliverables/uts/Perhitungan-SMART-SPK-Kecemasan.xlsx
Only the student inputs, the RF prediction (the data-mining step cannot run in Excel), the
criterion bounds, the weights, and the app's own results (for the check) are typed values.
Everything else is a formula.
"""
import json
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "deliverables" / "uts"
D = json.loads((OUT_DIR / "uts_data.json").read_text())
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else OUT_DIR / "Perhitungan-SMART-SPK-Kecemasan.xlsx"

CRIT = D["criteria"]
ALTS = D["alternatives"]
STU = D["students"]
NC, NA, NS = len(CRIT), len(ALTS), len(STU)
CODES = [f"C{i + 1}" for i in range(NC)]
ACODES = [f"A{i + 1}" for i in range(NA)]

CRIT_INFO = {
    "rf_anxiety_score": ("Prediksi skor kecemasan (Random Forest)", "Makin tinggi prediksi kecemasan, makin perlu ditangani.",
                         "Keluaran model data mining; inti masalah yang ingin ditangani."),
    "study_hours_per_day": ("Jam belajar per hari", "Beban belajar panjang menambah tekanan.",
                            "Korelasi positif dengan kecemasan (r = 0,272)."),
    "academic_performance": ("Nilai rata-rata rapor", "Nilai rendah menandakan kesulitan akademik.",
                             "Kesulitan akademik adalah pemicu kecemasan siswa."),
    "sleep_hours": ("Jam tidur per malam", "Tidur pendek memperburuk kondisi.",
                    "Korelasi negatif dengan kecemasan (r = -0,205)."),
    "physical_activity": ("Hari olahraga per minggu", "Jarang olahraga berarti kurang penyaluran stres.",
                          "Korelasi negatif dengan kecemasan (r = -0,122)."),
    "financial_stress": ("Tekanan finansial (0-10)", "Tekanan ekonomi menambah beban.",
                         "Korelasi positif dengan kecemasan (r = 0,360)."),
    "family_expectation": ("Ekspektasi keluarga (0-10)", "Tuntutan keluarga tinggi menambah tekanan.",
                           "Korelasi positif dengan kecemasan (r = 0,260)."),
    "burnout_score": ("Skor kelelahan / burnout (0-10)", "Kelelahan tinggi butuh pemulihan.",
                      "Korelasi kuat dengan kecemasan (r = 0,674)."),
}
ALT_INFO = {
    "Sleep": ("Tidur", "Program perbaikan pola tidur (sleep hygiene) dan jadwal malam."),
    "Exercise": ("Olahraga", "Program aktivitas fisik terjadwal untuk menurunkan ketegangan."),
    "Study": ("Strategi belajar", "Pelatihan manajemen waktu dan strategi belajar."),
    "Counseling": ("Konseling", "Konseling individual dengan guru BK; rujukan profesional bila perlu."),
    "Relaxation": ("Relaksasi", "Latihan pernapasan, mindfulness, dan manajemen stres."),
}
FEATURES = ["age", "gender", "study_hours_per_day", "academic_performance", "exam_pressure", "stress_level",
            "sleep_hours", "physical_activity", "financial_stress", "family_expectation", "burnout_score"]
FEAT_LABEL = {
    "age": "Usia", "gender": "Gender", "study_hours_per_day": "Jam belajar/hari", "academic_performance": "Nilai rapor",
    "exam_pressure": "Tekanan ujian", "stress_level": "Tingkat stres", "sleep_hours": "Jam tidur",
    "physical_activity": "Olahraga (hari/minggu)", "financial_stress": "Tekanan finansial",
    "family_expectation": "Ekspektasi keluarga", "burnout_score": "Burnout",
}

# ---------- styles ----------
FONT = "Arial"
BLUE, GREEN, BLACK = "0000FF", "008000", "000000"
HEAD_FILL = PatternFill("solid", fgColor="1F3864")
SUB_FILL = PatternFill("solid", fgColor="DCE6F2")
INPUT_FILL = PatternFill("solid", fgColor="FFFF00")
OK_FILL = PatternFill("solid", fgColor="C6EFCE")
BAD_FILL = PatternFill("solid", fgColor="FFC7CE")
BEST_FILL = PatternFill("solid", fgColor="FFE699")
thin = Side(style="thin", color="A6A6A6")
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
NUM4 = "0.0000"


def put(ws, ref, value, color=BLACK, bold=False, fmt=None, fill=None, wrap=False, align=None, size=10, italic=False):
    c = ws[ref]
    c.value = value
    c.font = Font(name=FONT, size=size, color=color, bold=bold, italic=italic)
    if fmt:
        c.number_format = fmt
    if fill:
        c.fill = fill
    if wrap or align:
        c.alignment = Alignment(wrap_text=wrap, horizontal=align, vertical="top" if wrap else None)
    return c


def header(ws, row, col, labels, fill=SUB_FILL, color=BLACK):
    for k, text in enumerate(labels):
        c = put(ws, f"{L(col + k)}{row}", text, color=color, bold=True, fill=fill, wrap=True, align="center")
        c.border = BOX


def title(ws, text, sub=None):
    put(ws, "A1", text, bold=True, size=14, color="1F3864")
    if sub:
        put(ws, "A2", sub, italic=True, color="595959")


def boxed(ws, r0, r1, c0, c1):
    for r in range(r0, r1 + 1):
        for c in range(c0, c1 + 1):
            ws.cell(r, c).border = BOX


def note(ws, ref, text):
    ws[ref].comment = Comment(text, "Kelompok 1")


def widths(ws, spec):
    for col, w in spec.items():
        ws.column_dimensions[col].width = w


wb = Workbook()

# ======================= Petunjuk =======================
ws = wb.active
ws.title = "Petunjuk"
title(ws, "Perhitungan Metode SMART - SPK Rekomendasi Penanganan Kecemasan Siswa",
      "Kelompok 1 - Sistem Pendukung Keputusan, UKRIDA 2026. Spreadsheet ini mereplikasi perhitungan SMART di aplikasi (app/spk/smart.py).")
rows = [
    ("Anggota", "Steven Feryanta (412025028), Steven Iwan (412024008), Triemas Putra (412024018), Davidson Rafael (412024030)"),
    ("Metode", "SMART (Simple Multi-Attribute Rating Technique) dengan utilitas min-max dan bobot ternormalisasi."),
    ("Dua keputusan", "(1) Siapa ditangani lebih dulu: skor prioritas = rata-rata utilitas 8 kriteria (bobot sama 1/8)."),
    ("", "(2) Penanganan apa: skor alternatif A_k = jumlah w_kj x u_j, dengan vektor bobot khusus untuk tiap alternatif."),
    ("Alur sheet", "Kriteria -> Alternatif -> Bobot -> Data -> MatriksKeputusan -> Normalisasi -> SkorPrioritas -> SkorAlternatif -> StudiKasus -> Rekomendasi -> Validasi"),
    ("", ""),
    ("Legenda warna", ""),
    ("Teks biru", "Nilai yang diketik (input): data siswa, prediksi RF dari aplikasi, batas min/maks, bobot, hasil aplikasi untuk pembanding."),
    ("Teks hitam", "Rumus perhitungan di sheet yang sama."),
    ("Teks hijau", "Rumus yang mengambil nilai dari sheet lain."),
    ("Sel kuning", "Pilihan yang boleh diubah: profil bobot (Bobot!C3), siswa studi kasus (StudiKasus!C3), ambang aturan pengaman (Rekomendasi!C3)."),
    ("", ""),
    ("Rumus utama", ""),
    ("Utilitas benefit", "u_ij = (x_ij - min_j) / (maks_j - min_j)   (dipotong ke rentang 0..1)"),
    ("Utilitas cost", "u_ij = (maks_j - x_ij) / (maks_j - min_j)   (dipotong ke rentang 0..1)"),
    ("Normalisasi bobot", "w_kj = w'_kj / jumlah_j w'_kj, sehingga bobot tiap alternatif berjumlah 1"),
    ("Skor prioritas siswa i", "P_i = jumlah_j (1/8) x u_ij"),
    ("Skor alternatif k siswa i", "S_ik = jumlah_j w_kj x u_ij;  rekomendasi = alternatif dengan S_ik terbesar"),
    ("Aturan pengaman", "Jika persentil prediksi kecemasan >= 90, rekomendasi akhir = Konseling + rujukan profesional."),
    ("", ""),
    ("Catatan", "Prediksi RF (kriteria C1) dihitung oleh model Random Forest di aplikasi, lalu disalin sebagai input (Data!N). Model RF tidak dapat dijalankan di Excel."),
    ("", "Batas min/maks memakai batas referensi yang disimpan aplikasi saat pelatihan (rf_anxiety_model_metadata.json), bukan min/maks 10 siswa ini, agar hasil sama dengan aplikasi."),
    ("", "Sheet Validasi membandingkan setiap skor dengan keluaran aplikasi untuk profil bobot yang dipilih."),
]
for i, (k, v) in enumerate(rows):
    r = 4 + i
    put(ws, f"A{r}", k, bold=bool(k) and not v or k in ("Legenda warna", "Rumus utama"))
    if k in ("Teks biru",):
        put(ws, f"B{r}", v, color=BLUE)
    elif k == "Teks hijau":
        put(ws, f"B{r}", v, color=GREEN)
    elif k == "Sel kuning":
        put(ws, f"B{r}", v, fill=INPUT_FILL)
    else:
        put(ws, f"B{r}", v)
    ws[f"A{r}"].font = Font(name=FONT, size=10, bold=True)
widths(ws, {"A": 26, "B": 130})

# ======================= Kriteria =======================
ws = wb.create_sheet("Kriteria")
title(ws, "Kriteria SMART (C1-C8)", "Jenis: benefit = nilai tinggi menaikkan utilitas (lebih butuh perhatian); cost = nilai rendah menaikkan utilitas.")
header(ws, 4, 1, ["Kode", "Kolom data", "Nama kriteria", "Jenis", "Min referensi", "Maks referensi", "Arti (kebutuhan perhatian)", "Dasar pemilihan"])
for i, c in enumerate(CRIT):
    r = 5 + i
    name, meaning, basis = CRIT_INFO[c]
    put(ws, f"A{r}", CODES[i], bold=True)
    put(ws, f"B{r}", c)
    put(ws, f"C{r}", name)
    put(ws, f"D{r}", D["criteria_type"][c], color=BLUE, align="center")
    put(ws, f"E{r}", D["bounds"][c]["min"], color=BLUE, fmt=NUM4)
    put(ws, f"F{r}", D["bounds"][c]["max"], color=BLUE, fmt=NUM4)
    put(ws, f"G{r}", meaning, wrap=True)
    put(ws, f"H{r}", basis, wrap=True)
boxed(ws, 4, 4 + NC, 1, 8)
note(ws, "E4", "Sumber: app/models/rf_anxiety_model_metadata.json -> smart_bounds. Min/maks tiap kriteria pada 20.000 baris data referensi Kaggle (C1 = min/maks prediksi RF). Dipakai aplikasi untuk menormalisasi satu siswa.")
note(ws, "D4", "Sumber: app/spk/config.py -> CRITERIA_TYPE.")
put(ws, "A15", "Jumlah kriteria", bold=True)
put(ws, "C15", f"=COUNTA(A5:A{4 + NC})", fmt="0")
widths(ws, {"A": 7, "B": 22, "C": 36, "D": 10, "E": 14, "F": 14, "G": 44, "H": 44})

# ======================= Alternatif =======================
ws = wb.create_sheet("Alternatif")
title(ws, "Alternatif tindakan (A1-A5)", "Lima bentuk penanganan yang dibandingkan untuk setiap siswa.")
header(ws, 4, 1, ["Kode", "Alternatif (aplikasi)", "Nama Indonesia", "Uraian tindakan"])
for i, a in enumerate(ALTS):
    r = 5 + i
    put(ws, f"A{r}", ACODES[i], bold=True)
    put(ws, f"B{r}", a, color=BLUE)
    put(ws, f"C{r}", ALT_INFO[a][0])
    put(ws, f"D{r}", ALT_INFO[a][1], wrap=True)
boxed(ws, 4, 4 + NA, 1, 4)
widths(ws, {"A": 7, "B": 20, "C": 20, "D": 70})

# ======================= Bobot =======================
ws = wb.create_sheet("Bobot")
title(ws, "Bobot kriteria per alternatif", "Baris = alternatif, kolom = kriteria. Setiap baris harus berjumlah 1 (syarat SMART).")
put(ws, "A3", "Profil bobot aktif:", bold=True)
put(ws, "C3", "A", color=BLUE, bold=True, fill=INPUT_FILL, align="center")
put(ws, "D3", "Ketik A, B, atau C. A = berbasis domain (default aplikasi), B = hampir seimbang, C = sama rata (kontrol).", italic=True)
dv = DataValidation(type="list", formula1='"A,B,C"', allow_blank=False)
ws.add_data_validation(dv)
dv.add("C3")

CC = 3  # first criterion column (C)
LASTC = L(CC + NC - 1)       # J
SUMC = L(CC + NC)            # K


def weight_block(r0, label, values=None, formula=None, color=BLUE, explain=None):
    """r0 = label row; header at r0+1; alternatives at r0+2.. ; returns first data row."""
    put(ws, f"A{r0}", label, bold=True, color="1F3864")
    if explain:
        put(ws, f"D{r0}", explain, italic=True, color="595959")
    header(ws, r0 + 1, 1, ["Kode", "Alternatif"] + CODES + ["Jumlah"])
    first = r0 + 2
    for i, a in enumerate(ALTS):
        r = first + i
        put(ws, f"A{r}", ACODES[i], bold=True)
        put(ws, f"B{r}", f"=Alternatif!B{5 + i}", color=GREEN)
        for j, c in enumerate(CRIT):
            ref = f"{L(CC + j)}{r}"
            if values is not None:
                put(ws, ref, values[a][c], color=color, fmt="0.00")
            else:
                put(ws, ref, formula(r, j), color=color, fmt=NUM4)
        put(ws, f"{SUMC}{r}", f"=SUM({L(CC)}{r}:{LASTC}{r})", fmt=NUM4, bold=True)
    boxed(ws, r0 + 1, first + NA - 1, 1, CC + NC)
    return first


RAW_A = weight_block(5, "Profil A mentah (notebook, sel 68)", values=D["weights_A_raw"],
                     explain="Bobot asli notebook. Baris Exercise berjumlah 1,05 sehingga perlu dinormalisasi.")
NORM_A = weight_block(13, "Profil A ternormalisasi (dipakai aplikasi)",
                      formula=lambda r, j: f"={L(CC + j)}{RAW_A + (r - (13 + 2))}/${SUMC}{RAW_A + (r - (13 + 2))}",
                      color=BLACK, explain="w_kj = w'_kj / jumlah baris. Rumus = config.normalize(WEIGHTS_A_NOTEBOOK).")
B_FIRST = weight_block(21, "Profil B hampir seimbang", values=D["weights_B"],
                       explain="Bobot kriteria utama tiap alternatif 0,20; lainnya 0,10-0,15.")
C_FIRST = weight_block(29, "Profil C sama rata (kontrol)",
                       formula=lambda r, j: "=1/Kriteria!$C$15", color=GREEN,
                       explain="Semua bobot 1/8. Semua skor alternatif seri, jadi hasil selalu alternatif pertama (Tidur).")
ACT = weight_block(37, "Bobot aktif (dipakai semua sheet berikutnya)",
                   formula=lambda r, j: (f'=IF($C$3="A",{L(CC + j)}{NORM_A + r - 39},'
                                         f'IF($C$3="B",{L(CC + j)}{B_FIRST + r - 39},{L(CC + j)}{C_FIRST + r - 39}))'),
                   color=BLACK, explain="Diambil dari profil yang dipilih di sel C3.")
assert ACT == 39
put(ws, "A45", "Bobot prioritas (keputusan siapa lebih dulu)", bold=True, color="1F3864")
put(ws, "D45", "Bobot sama untuk 8 kriteria: w_j = 1/8 (config.PRIORITY_WEIGHTS).", italic=True, color="595959")
header(ws, 46, 1, ["", "Bobot"] + CODES + ["Jumlah"])
put(ws, "B47", "w_j prioritas", bold=True)
for j in range(NC):
    put(ws, f"{L(CC + j)}47", "=1/Kriteria!$C$15", color=GREEN, fmt=NUM4)
put(ws, f"{SUMC}47", f"=SUM({L(CC)}47:{LASTC}47)", fmt=NUM4, bold=True)
boxed(ws, 46, 47, 1, CC + NC)

put(ws, "A50", "Dasar penentuan bobot profil A", bold=True, color="1F3864")
basis = [
    "Setiap alternatif memberi bobot terbesar pada kriteria yang langsung ditangani alternatif itu:",
    "Tidur -> C4 jam tidur (0,40); Olahraga -> C5 hari olahraga (0,45) dan C8 burnout (0,20); Strategi belajar -> C2 jam belajar (0,40) dan C3 nilai rapor (0,30);",
    "Konseling -> C1 prediksi kecemasan (0,30) dan C6 tekanan finansial (0,20); Relaksasi -> C1 prediksi kecemasan (0,20), C4 jam tidur (0,20), C6 dan C7 tekanan (0,15).",
    "Kriteria lain diberi bobot kecil (0,05-0,15) agar kondisi umum siswa tetap ikut dihitung. Bobot diuji dengan analisis sensitivitas (sheet StudiKasus dan halaman Analisis aplikasi).",
]
for i, t in enumerate(basis):
    put(ws, f"A{51 + i}", t)
widths(ws, {"A": 7, "B": 14, **{L(CC + j): 9 for j in range(NC)}, SUMC: 9})
ws.column_dimensions["D"].width = 9

# ======================= Data =======================
ws = wb.create_sheet("Data")
title(ws, "Data siswa (alternatif keputusan prioritas)",
      "S01-S02 = contoh profil di aplikasi; S03-S10 = baris data uji Kaggle. Kolom N = prediksi RF dari aplikasi.")
hdr = ["ID", "Sumber"] + [FEAT_LABEL[f] for f in FEATURES] + ["Prediksi RF (C1)", "Persentil prediksi RF", "Skor kecemasan aktual"]
header(ws, 4, 1, hdr)
for i, s in enumerate(STU):
    r = 5 + i
    put(ws, f"A{r}", s["id"], bold=True)
    put(ws, f"B{r}", s["source"], color=BLUE)
    for k, f in enumerate(FEATURES):
        v = s["features"][f]
        put(ws, f"{L(3 + k)}{r}", v, color=BLUE, fmt=None if f in ("age", "gender") else "0.00")
    put(ws, f"N{r}", s["rf_score"], color=BLUE, fmt=NUM4)
    put(ws, f"O{r}", s["rf_percentile"], color=BLUE, fmt="0.0")
    put(ws, f"P{r}", s["actual_anxiety"] if s["actual_anxiety"] is not None else "-", color=BLUE,
        fmt="0.00", align="right")
boxed(ws, 4, 4 + NS, 1, 16)
note(ws, "N4", "Keluaran RandomForestRegressor aplikasi (models/rf_anxiety_model.joblib) untuk 11 fitur di kiri. Dihasilkan oleh deliverables/build/uts_data.py.")
note(ws, "O4", "Persentase populasi referensi (20.000 baris) yang prediksinya lebih rendah. Dipakai untuk aturan pengaman.")
note(ws, "P4", "Label asli dataset Kaggle (untuk melihat kualitas prediksi). Contoh profil S01-S02 tidak punya label.")
put(ws, f"A{6 + NS}", "Kesalahan absolut rata-rata prediksi RF pada S03-S10 (MAE):", bold=True)
put(ws, f"N{6 + NS}", f"=SUMPRODUCT(ABS(N7:N{4 + NS}-P7:P{4 + NS}))/COUNT(P7:P{4 + NS})", fmt=NUM4)
widths(ws, {"A": 6, "B": 30, **{L(3 + k): 11 for k in range(11)}, "N": 12, "O": 12, "P": 12})

# ======================= MatriksKeputusan =======================
FIRST = 11  # first student row in MatriksKeputusan / Normalisasi / SkorPrioritas / SkorAlternatif
LASTR = FIRST + NS - 1
CRIT_SRC = {c: L(3 + FEATURES.index(c)) for c in CRIT if c in FEATURES}
CRIT_SRC["rf_anxiety_score"] = "N"


def crit_header(ws, with_bounds=True):
    put(ws, "A4", "Kode", bold=True, fill=SUB_FILL)
    put(ws, "A5", "Kriteria", bold=True, fill=SUB_FILL)
    put(ws, "A6", "Jenis", bold=True, fill=SUB_FILL)
    put(ws, "A7", "Min", bold=True, fill=SUB_FILL)
    put(ws, "A8", "Maks", bold=True, fill=SUB_FILL)
    for j in range(NC):
        col = L(2 + j)
        put(ws, f"{col}4", f"=Kriteria!A{5 + j}", color=GREEN, bold=True, align="center", fill=SUB_FILL)
        put(ws, f"{col}5", f"=Kriteria!C{5 + j}", color=GREEN, wrap=True, fill=SUB_FILL)
        put(ws, f"{col}6", f"=Kriteria!D{5 + j}", color=GREEN, align="center")
        put(ws, f"{col}7", f"=Kriteria!E{5 + j}", color=GREEN, fmt=NUM4)
        put(ws, f"{col}8", f"=Kriteria!F{5 + j}", color=GREEN, fmt=NUM4)
    boxed(ws, 4, 8, 1, 1 + NC)
    ws.row_dimensions[5].height = 42


ws = wb.create_sheet("MatriksKeputusan")
title(ws, "Matriks keputusan X (siswa x kriteria)", "x_ij = nilai siswa i pada kriteria j, diambil dari sheet Data.")
crit_header(ws)
header(ws, FIRST - 1, 1, ["ID siswa"] + [f"x_i,{c}" for c in CODES])
for i in range(NS):
    r = FIRST + i
    put(ws, f"A{r}", f"=Data!A{5 + i}", color=GREEN, bold=True)
    for j, c in enumerate(CRIT):
        put(ws, f"{L(2 + j)}{r}", f"=Data!{CRIT_SRC[c]}{5 + i}", color=GREEN, fmt=NUM4)
boxed(ws, FIRST - 1, LASTR, 1, 1 + NC)
widths(ws, {"A": 10, **{L(2 + j): 15 for j in range(NC)}})

# ======================= Normalisasi =======================
ws = wb.create_sheet("Normalisasi")
title(ws, "Normalisasi: nilai utilitas u_ij (0-1)",
      "benefit: (x - min)/(maks - min); cost: (maks - x)/(maks - min); dipotong ke 0..1. Jika maks = min, u = 1.")
crit_header(ws)
header(ws, FIRST - 1, 1, ["ID siswa"] + [f"u_i,{c}" for c in CODES])
for i in range(NS):
    r = FIRST + i
    put(ws, f"A{r}", f"=MatriksKeputusan!A{r}", color=GREEN, bold=True)
    for j in range(NC):
        col = L(2 + j)
        x = f"MatriksKeputusan!{col}{r}"
        lo, hi, typ = f"{col}$7", f"{col}$8", f"{col}$6"
        put(ws, f"{col}{r}",
            f'=IF({hi}={lo},1,MAX(0,MIN(1,IF({typ}="benefit",({x}-{lo})/({hi}-{lo}),({hi}-{x})/({hi}-{lo})))))',
            color=GREEN, fmt=NUM4)
boxed(ws, FIRST - 1, LASTR, 1, 1 + NC)
widths(ws, {"A": 10, **{L(2 + j): 15 for j in range(NC)}})

# ======================= SkorPrioritas =======================
ws = wb.create_sheet("SkorPrioritas")
title(ws, "Keputusan 1 - Skor prioritas siswa (siapa ditangani lebih dulu)",
      "P_i = jumlah_j w_j x u_ij dengan w_j = 1/8. Kolom B-I = kontribusi tiap kriteria (w_j x u_ij).")
crit_header(ws)
put(ws, "A9", "Bobot w_j", bold=True, fill=SUB_FILL)
for j in range(NC):
    put(ws, f"{L(2 + j)}9", f"=Bobot!{L(CC + j)}47", color=GREEN, fmt=NUM4)
header(ws, FIRST - 1, 1, ["ID siswa"] + [f"w x u ({c})" for c in CODES] + ["Skor prioritas P_i", "Peringkat"])
PCOL, RCOL = L(2 + NC), L(3 + NC)   # J, K
for i in range(NS):
    r = FIRST + i
    put(ws, f"A{r}", f"=Normalisasi!A{r}", color=GREEN, bold=True)
    for j in range(NC):
        col = L(2 + j)
        put(ws, f"{col}{r}", f"={col}$9*Normalisasi!{col}{r}", color=GREEN, fmt=NUM4)
    put(ws, f"{PCOL}{r}", f"=SUMPRODUCT(Normalisasi!B{r}:{L(1 + NC)}{r},$B$9:${L(1 + NC)}$9)", color=GREEN, fmt=NUM4, bold=True)
    put(ws, f"{RCOL}{r}", f"=RANK({PCOL}{r},${PCOL}${FIRST}:${PCOL}${LASTR},0)", fmt="0", align="center")
boxed(ws, FIRST - 1, LASTR, 1, 3 + NC)
S0 = LASTR + 3
put(ws, f"A{S0}", "Urutan prioritas penanganan (diurutkan dengan rumus LARGE + MATCH)", bold=True, color="1F3864")
header(ws, S0 + 1, 1, ["Peringkat", "ID siswa", "Skor P_i"])
for k in range(NS):
    r = S0 + 2 + k
    put(ws, f"A{r}", k + 1, align="center")
    put(ws, f"C{r}", f"=LARGE(${PCOL}${FIRST}:${PCOL}${LASTR},A{r})", fmt=NUM4)
    put(ws, f"B{r}", f"=INDEX($A${FIRST}:$A${LASTR},MATCH(C{r},${PCOL}${FIRST}:${PCOL}${LASTR},0))", bold=True)
boxed(ws, S0 + 1, S0 + 1 + NS, 1, 3)
widths(ws, {"A": 10, **{L(2 + j): 14 for j in range(NC)}, PCOL: 14, RCOL: 10})

# ======================= SkorAlternatif =======================
ws = wb.create_sheet("SkorAlternatif")
title(ws, "Keputusan 2 - Skor alternatif penanganan per siswa",
      "S_ik = jumlah_j w_kj x u_ij (SUMPRODUCT baris utilitas siswa dengan baris bobot aktif alternatif k).")
put(ws, "A3", "Profil bobot aktif:", bold=True)
put(ws, "C3", "=Bobot!C3", color=GREEN, bold=True, align="center")
header(ws, FIRST - 1, 1, ["ID siswa"] + [f"=Alternatif!B{5 + k}" for k in range(NA)]
       + ["Rekomendasi (skor tertinggi)", "Skor tertinggi", "Peringkat 2", "Selisih #1 - #2"])
for k in range(NA):
    ws[f"{L(2 + k)}{FIRST - 1}"].font = Font(name=FONT, size=10, bold=True, color=GREEN)
for k in range(NA):
    put(ws, f"{L(2 + k)}{FIRST - 2}", ACODES[k], bold=True, align="center")
BCOL, MCOL, SCOL, GCOL = L(2 + NA), L(3 + NA), L(4 + NA), L(5 + NA)  # G H I J
AR = f"$B{{r}}:${L(1 + NA)}{{r}}"
for i in range(NS):
    r = FIRST + i
    rng = f"$B{r}:${L(1 + NA)}{r}"
    put(ws, f"A{r}", f"=Normalisasi!A{r}", color=GREEN, bold=True)
    for k in range(NA):
        put(ws, f"{L(2 + k)}{r}",
            f"=SUMPRODUCT(Normalisasi!$B{r}:${L(1 + NC)}{r},Bobot!${L(CC)}${ACT + k}:${LASTC}${ACT + k})",
            color=GREEN, fmt=NUM4)
    put(ws, f"{BCOL}{r}", f"=INDEX($B${FIRST - 1}:${L(1 + NA)}${FIRST - 1},MATCH(MAX({rng}),{rng},0))", bold=True)
    put(ws, f"{MCOL}{r}", f"=MAX({rng})", fmt=NUM4)
    put(ws, f"{SCOL}{r}", f"=INDEX($B${FIRST - 1}:${L(1 + NA)}${FIRST - 1},MATCH(LARGE({rng},2),{rng},0))")
    put(ws, f"{GCOL}{r}", f"=LARGE({rng},1)-LARGE({rng},2)", fmt=NUM4)
boxed(ws, FIRST - 1, LASTR, 1, 5 + NA)
ws.conditional_formatting.add(f"B{FIRST}:{L(1 + NA)}{LASTR}",
                              FormulaRule(formula=[f"B{FIRST}=MAX($B{FIRST}:${L(1 + NA)}{FIRST})"], fill=BEST_FILL))
R0 = LASTR + 3
put(ws, f"A{R0}", "Peringkat alternatif per siswa (1 = paling sesuai)", bold=True, color="1F3864")
header(ws, R0 + 1, 1, ["ID siswa"] + [f"=Alternatif!B{5 + k}" for k in range(NA)])
for i in range(NS):
    r = R0 + 2 + i
    src = FIRST + i
    put(ws, f"A{r}", f"=A{src}", bold=True)
    for k in range(NA):
        col = L(2 + k)
        put(ws, f"{col}{r}", f"=RANK({col}{src},$B{src}:${L(1 + NA)}{src},0)", fmt="0", align="center")
boxed(ws, R0 + 1, R0 + 1 + NS, 1, 1 + NA)
put(ws, f"A{R0 + 3 + NS}", "Catatan: pada profil C semua skor seri; MATCH memilih alternatif pertama (Tidur), sama seperti idxmax di aplikasi.", italic=True)
widths(ws, {"A": 10, **{L(2 + k): 13 for k in range(NA)}, BCOL: 22, MCOL: 12, SCOL: 14, GCOL: 13})

# ======================= StudiKasus =======================
ws = wb.create_sheet("StudiKasus")
title(ws, "Studi kasus satu siswa: matriks keputusan alternatif x kriteria",
      "Pilih ID siswa di C3. Sel matriks kontribusi = w_kj x u_j; jumlah baris = skor alternatif S_k.")
put(ws, "A3", "ID siswa:", bold=True)
put(ws, "C3", "S01", color=BLUE, bold=True, fill=INPUT_FILL, align="center")
dv2 = DataValidation(type="list", formula1=f"=Data!$A$5:$A${4 + NS}")
ws.add_data_validation(dv2)
dv2.add("C3")
put(ws, "D3", "Baris di tabel:", bold=True)
put(ws, "F3", f"=MATCH(C3,Normalisasi!$A${FIRST}:$A${LASTR},0)", fmt="0")
put(ws, "G3", "Profil bobot:", bold=True)
put(ws, "I3", "=Bobot!C3", color=GREEN, bold=True)
# criteria rows
header(ws, 5, 1, ["", "Kriteria"] + CODES)
put(ws, "B6", "Nilai x_j", bold=True)
put(ws, "B7", "Jenis", bold=True)
put(ws, "B8", "Utilitas u_j", bold=True)
for j in range(NC):
    col = L(3 + j)
    put(ws, f"{col}6", f"=INDEX(MatriksKeputusan!{L(2 + j)}${FIRST}:{L(2 + j)}${LASTR},$F$3)", color=GREEN, fmt=NUM4)
    put(ws, f"{col}7", f"=Kriteria!D{5 + j}", color=GREEN, align="center")
    put(ws, f"{col}8", f"=INDEX(Normalisasi!{L(2 + j)}${FIRST}:{L(2 + j)}${LASTR},$F$3)", color=GREEN, fmt=NUM4, bold=True)
boxed(ws, 5, 8, 1, 2 + NC)
# weight matrix
put(ws, "A10", "Bobot aktif w_kj", bold=True, color="1F3864")
header(ws, 11, 1, ["Kode", "Alternatif"] + CODES + ["Jumlah"])
for k in range(NA):
    r = 12 + k
    put(ws, f"A{r}", ACODES[k], bold=True)
    put(ws, f"B{r}", f"=Alternatif!B{5 + k}", color=GREEN)
    for j in range(NC):
        put(ws, f"{L(3 + j)}{r}", f"=Bobot!{L(CC + j)}{ACT + k}", color=GREEN, fmt=NUM4)
    put(ws, f"{L(3 + NC)}{r}", f"=SUM(C{r}:{L(2 + NC)}{r})", fmt=NUM4)
boxed(ws, 11, 11 + NA, 1, 3 + NC)
# contribution matrix
put(ws, "A18", "Matriks kontribusi w_kj x u_j dan skor akhir", bold=True, color="1F3864")
header(ws, 19, 1, ["Kode", "Alternatif"] + CODES + ["Skor S_k", "Peringkat", "Cek vs SkorAlternatif"])
SK, RK, CK = L(3 + NC), L(4 + NC), L(5 + NC)   # K L M
for k in range(NA):
    r = 20 + k
    put(ws, f"A{r}", ACODES[k], bold=True)
    put(ws, f"B{r}", f"=B{12 + k}")
    for j in range(NC):
        col = L(3 + j)
        put(ws, f"{col}{r}", f"={col}{12 + k}*{col}$8", fmt=NUM4)
    put(ws, f"{SK}{r}", f"=SUM(C{r}:{L(2 + NC)}{r})", fmt=NUM4, bold=True)
    put(ws, f"{RK}{r}", f"=RANK({SK}{r},${SK}$20:${SK}${19 + NA},0)", fmt="0", align="center")
    put(ws, f"{CK}{r}", f'=IF(ABS({SK}{r}-INDEX(SkorAlternatif!{L(2 + k)}${FIRST}:{L(2 + k)}${LASTR},$F$3))<1E-12,"sama","beda")', color=GREEN, align="center")
boxed(ws, 19, 19 + NA, 1, 5 + NC)
ws.conditional_formatting.add(f"{RK}20:{RK}{19 + NA}", CellIsRule(operator="equal", formula=["1"], fill=BEST_FILL))
put(ws, "A26", "Rekomendasi utama:", bold=True)
put(ws, "D26", f"=INDEX(B20:B{19 + NA},MATCH(1,{RK}20:{RK}{19 + NA},0))", bold=True, fill=BEST_FILL)
put(ws, "F26", "Skor:", bold=True)
put(ws, "G26", f"=MAX({SK}20:{SK}{19 + NA})", fmt=NUM4, bold=True)
put(ws, "A27", "Kriteria penyumbang terbesar:", bold=True)
put(ws, "D27", f"=INDEX($C$5:${L(2 + NC)}$5,MATCH(LARGE(INDEX($C$20:${L(2 + NC)}${19 + NA},MATCH(1,${RK}$20:${RK}${19 + NA},0),0),1),"
               f"INDEX($C$20:${L(2 + NC)}${19 + NA},MATCH(1,${RK}$20:${RK}${19 + NA},0),0),0))", bold=True)
put(ws, "F27", "(kontribusi w x u terbesar pada baris rekomendasi utama)", italic=True)

# sensitivity (closed form of smart.perturb + renormalize)
T0 = 30
put(ws, f"A{T0}", "Uji sensitivitas bobot siswa ini (sama dengan tabel sensitivitas di aplikasi)", bold=True, color="1F3864")
put(ws, f"A{T0 + 1}", "Bobot kriteria c diubah (1 + d) pada semua alternatif lalu dinormalisasi ulang: S'_k = (S_k + w_kc x d x u_c) / (1 + w_kc x d).", italic=True)
header(ws, T0 + 2, 1, ["No", "Kriteria", "Perubahan d"] + [f"=B{12 + k}" for k in range(NA)] + ["Terbaik", "Berubah?"])
for k in range(NA):
    ws[f"{L(4 + k)}{T0 + 2}"].font = Font(name=FONT, size=10, bold=True)
row = T0 + 3
deltas = [-0.2, -0.1, 0.1, 0.2]
first_s = row
for j in range(NC):
    for d in deltas:
        put(ws, f"A{row}", j + 1, align="center")
        put(ws, f"B{row}", f"=INDEX($C$5:${L(2 + NC)}$5,A{row})")
        put(ws, f"C{row}", d, color=BLUE, fmt="+0%;-0%")
        for k in range(NA):
            w = f"INDEX($C${12 + k}:${L(2 + NC)}${12 + k},$A{row})"
            u = f"INDEX($C$8:${L(2 + NC)}$8,$A{row})"
            put(ws, f"{L(4 + k)}{row}", f"=(${SK}${20 + k}+{w}*$C{row}*{u})/(1+{w}*$C{row})", fmt=NUM4)
        rng = f"D{row}:{L(3 + NA)}{row}"
        put(ws, f"{L(4 + NA)}{row}", f"=INDEX($D${T0 + 2}:${L(3 + NA)}${T0 + 2},MATCH(MAX({rng}),{rng},0))")
        put(ws, f"{L(5 + NA)}{row}", f'=IF({L(4 + NA)}{row}=$D$26,"tidak","YA")', align="center")
        row += 1
last_s = row - 1
boxed(ws, T0 + 2, last_s, 1, 5 + NA)
ws.conditional_formatting.add(f"{L(5 + NA)}{first_s}:{L(5 + NA)}{last_s}", CellIsRule(operator="equal", formula=['"YA"'], fill=BAD_FILL))
put(ws, f"A{row + 1}", "Skenario stabil:", bold=True)
put(ws, f"D{row + 1}", f'=COUNTIF({L(5 + NA)}{first_s}:{L(5 + NA)}{last_s},"tidak")&" dari "&COUNTA({L(5 + NA)}{first_s}:{L(5 + NA)}{last_s})&" skenario"', bold=True)
widths(ws, {"A": 6, "B": 14, "C": 11, **{L(3 + j): 11 for j in range(1, NC)}, SK: 11, RK: 10, CK: 12})
ws.column_dimensions["C"].width = 12

# ======================= Rekomendasi =======================
ws = wb.create_sheet("Rekomendasi")
title(ws, "Hasil akhir dan interpretasi SPK", "Menggabungkan keputusan 1 (prioritas) dan keputusan 2 (alternatif terbaik) dengan aturan pengaman.")
put(ws, "A3", "Ambang aturan pengaman (persentil):", bold=True)
put(ws, "C3", D["safety_percentile"], color=BLUE, bold=True, fill=INPUT_FILL, align="center")
note(ws, "C3", "config.SAFETY_PERCENTILE = 90: siswa dengan prediksi kecemasan di 10% teratas populasi referensi selalu mendapat Konseling + rujukan.")
header(ws, 5, 1, ["ID siswa", "Skor prioritas", "Peringkat prioritas", "Prediksi RF", "Persentil RF",
                  "Aturan pengaman?", "Rekomendasi SMART", "Alternatif ke-2", "Rekomendasi akhir", "Interpretasi"])
for i in range(NS):
    r = 6 + i
    src = FIRST + i
    put(ws, f"A{r}", f"=SkorPrioritas!A{src}", color=GREEN, bold=True)
    put(ws, f"B{r}", f"=SkorPrioritas!{PCOL}{src}", color=GREEN, fmt=NUM4)
    put(ws, f"C{r}", f"=SkorPrioritas!{RCOL}{src}", color=GREEN, fmt="0", align="center")
    put(ws, f"D{r}", f"=Data!N{5 + i}", color=GREEN, fmt="0.00")
    put(ws, f"E{r}", f"=Data!O{5 + i}", color=GREEN, fmt="0.0")
    put(ws, f"F{r}", f'=IF(E{r}>=$C$3,"YA","tidak")', align="center")
    put(ws, f"G{r}", f"=SkorAlternatif!{BCOL}{src}", color=GREEN)
    put(ws, f"H{r}", f"=SkorAlternatif!{SCOL}{src}", color=GREEN)
    put(ws, f"I{r}", f'=IF(F{r}="YA","Counseling + rujukan profesional",G{r})', bold=True)
    put(ws, f"J{r}",
        f'="Prioritas ke-"&C{r}&" dari "&COUNT($B$6:$B${5 + NS})&" siswa. "&IF(F{r}="YA",'
        f'"Prediksi kecemasan di atas persentil "&$C$3&": segera konseling dan rujuk; program "&G{r}&" menyusul.",'
        f'"Program utama "&G{r}&" (selisih "&TEXT(SkorAlternatif!{GCOL}{src},"0.000")&" dari "&H{r}&").")',
        wrap=True)
boxed(ws, 5, 5 + NS, 1, 10)
ws.conditional_formatting.add(f"F6:F{5 + NS}", CellIsRule(operator="equal", formula=['"YA"'], fill=BAD_FILL))
put(ws, f"A{8 + NS}", "Rekapitulasi rekomendasi akhir", bold=True, color="1F3864")
header(ws, 9 + NS, 1, ["Rekomendasi", "Jumlah siswa"])
labels = ALTS + ["Counseling + rujukan profesional"]
for k, a in enumerate(labels):
    r = 10 + NS + k
    put(ws, f"A{r}", a)
    put(ws, f"B{r}", f'=COUNTIF($I$6:$I${5 + NS},A{r})', fmt="0", align="center")
put(ws, f"A{10 + NS + len(labels)}", "Total", bold=True)
put(ws, f"B{10 + NS + len(labels)}", f"=SUM(B{10 + NS}:B{9 + NS + len(labels)})", fmt="0", bold=True, align="center")
boxed(ws, 9 + NS, 10 + NS + len(labels), 1, 2)
put(ws, f"A{13 + NS + len(labels)}", "Cara membaca: guru BK menangani siswa berurutan menurut peringkat prioritas, memberi program sesuai kolom Rekomendasi akhir, "
                                       "dan memakai alternatif ke-2 bila selisih skor kecil (< 0,02) atau program pertama tidak tersedia.", italic=True)
widths(ws, {"A": 34, "B": 13, "C": 12, "D": 11, "E": 11, "F": 12, "G": 18, "H": 16, "I": 30, "J": 70})
for i in range(NS):
    ws.row_dimensions[6 + i].height = 30

# ======================= Validasi =======================
ws = wb.create_sheet("Validasi")
title(ws, "Validasi: spreadsheet vs keluaran aplikasi",
      "Tabel kanan (biru) = hasil spk.recommend.assess() di aplikasi untuk 3 profil. Tabel kiri membandingkan dengan profil aktif.")
put(ws, "A3", "Profil bobot aktif:", bold=True)
put(ws, "C3", "=Bobot!C3", color=GREEN, bold=True, align="center")
# app table at column P onwards
AP = 16  # P
app_hdr = ["Kunci", "Profil", "ID", "Prioritas"] + ALTS + ["Terbaik"]
header(ws, 5, AP, app_hdr)
ar = 6
for p in ("A", "B", "C"):
    for s in STU:
        a = s["app"][p]
        put(ws, f"{L(AP)}{ar}", f"={L(AP + 1)}{ar}&{L(AP + 2)}{ar}")
        put(ws, f"{L(AP + 1)}{ar}", p, color=BLUE, align="center")
        put(ws, f"{L(AP + 2)}{ar}", s["id"], color=BLUE)
        put(ws, f"{L(AP + 3)}{ar}", a["priority"], color=BLUE, fmt="0.000000")
        for k, alt in enumerate(ALTS):
            put(ws, f"{L(AP + 4 + k)}{ar}", a["scores"][alt], color=BLUE, fmt="0.000000")
        put(ws, f"{L(AP + 4 + NA)}{ar}", a["best"], color=BLUE)
        ar += 1
APP_LAST = ar - 1
boxed(ws, 5, APP_LAST, AP, AP + 4 + NA)
KEYS = f"${L(AP)}$6:${L(AP)}${APP_LAST}"


def app_val(col_offset, key):
    c = L(AP + col_offset)
    return f"INDEX(${c}$6:${c}${APP_LAST},MATCH({key},{KEYS},0))"


header(ws, 5, 1, ["ID siswa", "Prioritas (sheet)", "Prioritas (aplikasi)", "Selisih prioritas"]
       + [f"Selisih {a}" for a in ALTS] + ["Terbaik (sheet)", "Terbaik (aplikasi)", "Status"])
for i in range(NS):
    r = 6 + i
    src = FIRST + i
    key = f"$C$3&A{r}"
    put(ws, f"A{r}", f"=SkorPrioritas!A{src}", color=GREEN, bold=True)
    put(ws, f"B{r}", f"=SkorPrioritas!{PCOL}{src}", color=GREEN, fmt="0.000000")
    put(ws, f"C{r}", "=" + app_val(3, key), fmt="0.000000")
    put(ws, f"D{r}", f"=ABS(B{r}-C{r})", fmt="0.0E+00")
    for k in range(NA):
        put(ws, f"{L(5 + k)}{r}", f"=ABS(SkorAlternatif!{L(2 + k)}{src}-{app_val(4 + k, key)})", color=GREEN, fmt="0.0E+00")
    put(ws, f"{L(5 + NA)}{r}", f"=SkorAlternatif!{BCOL}{src}", color=GREEN)
    put(ws, f"{L(6 + NA)}{r}", "=" + app_val(4 + NA, key))
    put(ws, f"{L(7 + NA)}{r}", f'=IF(AND(MAX(D{r}:{L(4 + NA)}{r})<1E-9,{L(5 + NA)}{r}={L(6 + NA)}{r}),"COCOK","BEDA")', bold=True, align="center")
boxed(ws, 5, 5 + NS, 1, 7 + NA)
STC = L(7 + NA)
ws.conditional_formatting.add(f"{STC}6:{STC}{5 + NS}", CellIsRule(operator="equal", formula=['"COCOK"'], fill=OK_FILL))
ws.conditional_formatting.add(f"{STC}6:{STC}{5 + NS}", CellIsRule(operator="equal", formula=['"BEDA"'], fill=BAD_FILL))
put(ws, f"A{7 + NS}", "Kesimpulan:", bold=True)
put(ws, f"C{7 + NS}", f'=COUNTIF({STC}6:{STC}{5 + NS},"COCOK")&" dari "&COUNTA(A6:A{5 + NS})&" siswa cocok dengan aplikasi (toleransi 1E-9)."', bold=True)
put(ws, f"A{8 + NS}", "Selisih maksimum seluruh skor:", bold=True)
put(ws, f"C{8 + NS}", f"=MAX(D6:{L(4 + NA)}{5 + NS})", fmt="0.0E+00", bold=True)
widths(ws, {"A": 10, "B": 14, "C": 14, "D": 12, **{L(5 + k): 12 for k in range(NA)}, L(5 + NA): 14, L(6 + NA): 14, STC: 10,
            L(AP): 8, L(AP + 1): 7, L(AP + 2): 6, L(AP + 3): 11, **{L(AP + 4 + k): 11 for k in range(NA)}, L(AP + 4 + NA): 12})

for s in wb.worksheets:
    s.sheet_view.showGridLines = s.title not in ("Petunjuk",)
    s.freeze_panes = None
wb.calculation.fullCalcOnLoad = True
wb.save(OUT)
print("->", OUT)
