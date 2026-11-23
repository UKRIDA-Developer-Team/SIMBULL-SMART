// Laporan Teknis Data Mining (UAS) = cover + daftar isi + CRISP-DM fase 1-6 + lampiran.
// Sources: PPT-Doc_CRISP-DM/fase*.md. Output: deliverables/laporan-dm/Laporan-Teknis-Data-Mining.docx
// The report has since been edited directly; rebuild it with `node build_laporan.js --from-md`.
const fs = require('fs');
const path = require('path');
const { buildWithToc, coverPage } = require('./md2docx');

const ROOT = path.resolve(__dirname, '..', '..');
const SRC = path.join(ROOT, 'PPT-Doc_CRISP-DM');
const OUT_DIR = path.join(ROOT, 'deliverables', 'laporan-dm');
const MEMBERS = [['Steven Feryanta', '412025028'], ['Steven Iwan', '412024008'], ['Triemas Putra', '412024018'], ['Davidson Rafael', '412024030']];

const phases = [
  'fase1-business-understanding.md', 'fase2-data-understanding.md', 'fase3-data-preparation.md',
  'fase4-modeling.md', 'fase5-evaluation.md', 'fase6-deployment.md',
];

function chapter(file, n) {
  let md = fs.readFileSync(path.join(SRC, file), 'utf8');
  md = md.replace(/^\*\*(Proyek|Metodologi):\*\*.*$/gm, '');          // per-file header lines
  md = md.replace(/^# Fase \d+ — (.+)$/m, `# ${n}. $1`);             // "Fase 1 — X" -> "1. X"
  md = md.replace(/^## (\d+)\. /gm, `## ${n}.$1 `);                  // "## 2. X" -> "## 1.2 X"
  md = md.replace(/^### (\d+)\.(\d+) /gm, `### ${n}.$1.$2 `);         // "### 2.1 X" -> "### 1.2.1 X"
  return md;
}

const intro = `[[TOC]]

[[PAGEBREAK]]

# Pendahuluan

Laporan ini mendokumentasikan teknik Data Mining pada proyek akhir **Sistem Pendukung Keputusan Rekomendasi Penanganan Kecemasan Siswa**. Laporan ini bukan proyek baru. Fokusnya adalah validasi teknis *pipeline* Data Mining dengan metodologi **CRISP-DM** (*Cross-Industry Standard Process for Data Mining*): pemahaman masalah, pemahaman dan persiapan data, pemodelan Random Forest, evaluasi, dan integrasi model ke aplikasi web **SI SMART** berbasis Streamlit. Aplikasi tersebut menggabungkan prediksi Data Mining dengan metode SPK SMART.

Laporan memakai dua sumber data: dataset publik Kaggle (1 juta baris) untuk pralatih, dan **304 respons kuesioner riil** siswa SMA yang bersifat rahasia untuk pelatihan ulang dan pengujian. Semua angka data riil adalah agregat yang dihasilkan otomatis oleh \`scripts/train.py --stage real\`; tidak ada baris individu yang ditampilkan. Bagian bertanda ⟦ISI …⟧ yang tersisa hanya hasil uji pengguna.

[[PAGEBREAK]]
`;

const lampiran = `[[PAGEBREAK]]

# Lampiran Teknis

## A. Repositori dan Aplikasi

| Item | Tautan / lokasi |
|---|---|
| Repositori GitHub | https://github.com/UKRIDA-Developer-Team/SIMBULL-SMART (privat; akses diberikan kepada penilai) |
| Cabang pengembangan | \`future\` (digabung ke \`main\` untuk deployment) |
| Aplikasi daring | https://si-smart.streamlit.app/ |
| Notebook Colab | \`code/Copy of EskulSPK2026_SMART_Final.ipynb\` |
| Kode aplikasi | \`app/\` (lihat \`app/README.md\`) |

## B. Menjalankan Ulang Pipeline

\`\`\`
cd app
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-train.txt
python scripts/train.py --stage kaggle                            # model dasar (berkas Kaggle 1 juta baris; R² 0,6077)
python scripts/train.py --stage tune                              # random search parameter (CV 5-fold)
python scripts/train.py --stage compare                           # perbandingan algoritma
python scripts/inspect_gform.py data/private/gform_data.csv       # cek pemetaan kuesioner
python scripts/train.py --stage real --gform data/private/gform_data.csv   # model aktif (S1)
python scripts/merge_report.py data/private/gform_data.csv        # pertanyaan mana digabung
python scripts/evaluate.py --gform data/private/<respons_baru>.csv   # uji respons baru
pytest                                                            # uji otomatis
streamlit run streamlit_app.py
\`\`\`

## C. Versi Pustaka

| Pustaka | Versi |
|---|---|
| Python | 3.12+ |
| scikit-learn | 1.9.1 |
| pandas | 3.0.6 |
| numpy | 2.5.3 |
| streamlit | 1.64.0 |
| matplotlib / seaborn | 3.11.2 / 0.13.2 |
`;

// --from-md builds the .docx from the edited laporan-teknis-dm.md as it is, without re-reading the
// phase files (the report has diverged from PPT-Doc_CRISP-DM, which stays unchanged).
const MD_FILE = path.join(OUT_DIR, 'laporan-teknis-dm.md');
let md;
if (process.argv.includes('--from-md')) {
  md = fs.readFileSync(MD_FILE, 'utf8');
} else {
  md = intro + phases.map((f, i) => chapter(f, i + 1)).join('\n\n[[PAGEBREAK]]\n\n') + '\n\n' + lampiran;
  fs.mkdirSync(OUT_DIR, { recursive: true });
  fs.writeFileSync(MD_FILE, md);
}

const cover = coverPage({
  kicker: 'LAPORAN TEKNIS DATA MINING (UAS)',
  title: 'Prediksi Kecemasan Siswa dengan Random Forest dan Rekomendasi Penanganan dengan Metode SMART',
  subtitle: 'Dokumentasi pipeline Data Mining dengan metodologi CRISP-DM',
  members: MEMBERS,
  footer: ['Universitas Kristen Krida Wacana', '2026'],
});

buildWithToc({ markdown: md, baseDir: SRC, out: path.join(OUT_DIR, 'Laporan-Teknis-Data-Mining.docx'),
  title: 'Laporan Teknis Data Mining — Kelompok 1', cover })
  .then(f => console.log('->', f));
