// Laporan UTS SPK -> deliverables/uts/Laporan-UTS-SPK-SMART-Kecemasan.docx
// Format (RubrikPenilaianUTSSPKUkrida20261): docx, Times New Roman 12 (page numbers too), line spacing 1.15,
// justified, A4, one column, margins left 4 cm and right/top/bottom 3 cm. Harvard references with hanging indent.
// Source: deliverables/uts/laporan-uts.md; {{TAB_*}} tables are filled from deliverables/uts/uts_data.json.
const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync } = require('child_process');
const {
  Document, Packer, Paragraph, TextRun, AlignmentType, LevelFormat, Footer, PageNumber,
  NumberFormat, TabStopType, PageBreak,
} = require('docx');
const md = require('./md2docx');

const DIR = path.resolve(__dirname, '..', 'uts');
const OUT = path.join(DIR, 'Laporan-UTS-SPK-SMART-Kecemasan.docx');
const PY = path.resolve(__dirname, '..', '..', 'app', '.venv', 'bin', 'python');
const cm = c => Math.round(c * 567);
const PAGE_W = 11906, PAGE_H = 16838;
const MARGIN = { left: cm(4), right: cm(3), top: cm(3), bottom: cm(3), header: cm(1.5), footer: cm(1.5) };
const FONT = 'Times New Roman', SIZE = 24, LINE = 276;   // 12 pt, 1.15 spacing

const TITLE = 'SPK SMART Kecemasan Siswa';
const SUBTITLE = 'Sistem Pendukung Keputusan Prioritas dan Rekomendasi Penanganan Kecemasan Siswa SMA Berbasis Random Forest dan Metode SMART';
const MEMBERS = [['Steven Feryanta', '412025028'], ['Steven Iwan', '412024008'], ['Triemas Putra', '412024018'], ['Davidson Rafael', '412024030']];

md.configure({
  font: FONT, size: SIZE, tableSize: 18, contentW: PAGE_W - MARGIN.left - MARGIN.right,
  maxImgHpx: Math.round(8.0 * 96), para: { spacing: { line: LINE, after: 100 } },
  listSpacing: { line: LINE, after: 40 }, tableHead: 'E7E6E6', tableBorder: '000000',
  captionRun: { size: 22 }, imgScale: 1, codeFont: FONT, keepNextPattern: /^Tabel \d+\./,
});

// ---------- data tables ----------
const D = JSON.parse(fs.readFileSync(path.join(DIR, 'uts_data.json'), 'utf8'));
const CRIT = D.criteria, ALTS = D.alternatives, STU = D.students;
const CODES = CRIT.map((_, j) => `C${j + 1}`);
const ALT_ID = { Sleep: 'Tidur', Exercise: 'Olahraga', Study: 'Strategi belajar', Counseling: 'Konseling', Relaxation: 'Relaksasi' };
const CRIT_ID = ['Prediksi kecemasan', 'Jam belajar', 'Nilai rapor', 'Jam tidur', 'Aktivitas fisik', 'Tekanan finansial', 'Ekspektasi keluarga', 'Burnout'];
const f = (x, d = 4) => x.toFixed(d).replace('.', ',').replace(/^-/, '−');
const row = cells => `| ${cells.join(' | ')} |`;
const tbl = (head, rows) => [row(head), row(head.map(() => '---')), ...rows.map(row)].join('\n');
const xval = (s, c) => (c === 'rf_anxiety_score' ? s.rf_score : s.features[c]);
const normA = Object.fromEntries(ALTS.map(a => {
  const tot = CRIT.reduce((t, c) => t + D.weights_A_raw[a][c], 0);
  return [a, Object.fromEntries(CRIT.map(c => [c, D.weights_A_raw[a][c] / tot]))];
}));
const A = s => s.app.A;
const sortedAlts = s => [...ALTS].sort((p, q) => A(s).scores[q] - A(s).scores[p]);
const safetyLabel = 'Konseling + rujukan profesional';

const TABLES = {
  TAB_WA: tbl(['Kode', 'Alternatif', ...CODES, 'Jumlah'], ALTS.map((a, k) => [
    `A${k + 1}`, ALT_ID[a], ...CRIT.map(c => f(normA[a][c])), f(CRIT.reduce((t, c) => t + normA[a][c], 0), 2)])),
  TAB_X: tbl(['ID', ...CODES], STU.map(s => [s.id, ...CRIT.map(c => f(xval(s, c)))])),
  TAB_BOUNDS: tbl(['Kode', 'Kriteria', 'Jenis', 'Min referensi', 'Maks referensi'], CRIT.map((c, j) => [
    CODES[j], CRIT_ID[j], D.criteria_type[c], f(D.bounds[c].min), f(D.bounds[c].max)])),
  TAB_U: tbl(['ID', ...CODES], STU.map(s => [s.id, ...CRIT.map(c => f(s.utility[c]))])),
  TAB_P: (() => {
    const order = [...STU].sort((p, q) => A(q).priority - A(p).priority);
    return tbl(['Peringkat', 'ID', 'Skor prioritas P_i', 'Prediksi RF (C1)', 'Persentil RF'],
      order.map((s, r) => [String(r + 1), s.id, f(A(s).priority), f(s.rf_score, 2), f(s.rf_percentile, 1)]));
  })(),
  TAB_S: tbl(['ID', ...ALTS.map(a => ALT_ID[a]), 'Rekomendasi', 'Selisih #1−#2'], STU.map(s => {
    const o = sortedAlts(s), sc = A(s).scores;
    return [s.id, ...ALTS.map(a => (a === o[0] ? `**${f(sc[a])}**` : f(sc[a]))), ALT_ID[o[0]], f(sc[o[0]] - sc[o[1]])];
  })),
  TAB_S01: (() => {
    const s = STU[0], o = sortedAlts(s);
    return tbl(['Kode', 'Alternatif', ...CODES, 'S_k', 'Peringkat'], ALTS.map((a, k) => [
      `A${k + 1}`, ALT_ID[a], ...CRIT.map(c => f(normA[a][c] * s.utility[c])),
      a === o[0] ? `**${f(A(s).scores[a])}**` : f(A(s).scores[a]), String(o.indexOf(a) + 1)]));
  })(),
  TAB_FINAL: (() => {
    const order = [...STU].sort((p, q) => A(q).priority - A(p).priority);
    return tbl(['Prioritas', 'ID', 'Rekomendasi SMART', 'Alternatif ke-2', 'Aturan pengaman', 'Rekomendasi akhir'],
      order.map((s, r) => {
        const o = sortedAlts(s), safe = s.rf_percentile >= D.safety_percentile;
        return [String(r + 1), s.id, ALT_ID[o[0]], ALT_ID[o[1]], safe ? 'YA' : 'tidak', safe ? `**${safetyLabel}**` : ALT_ID[o[0]]];
      }));
  })(),
};
// sanity: the safety rule must agree with the app's flag
STU.forEach(s => { if ((s.rf_percentile >= D.safety_percentile) !== s.safety) throw new Error(`safety mismatch ${s.id}`); });

let core = fs.readFileSync(path.join(DIR, 'laporan-uts.md'), 'utf8');
core = core.replace(/\{\{(TAB_\w+)\}\}/g, (_, k) => { if (!TABLES[k]) throw new Error(`no table ${k}`); return TABLES[k]; });
fs.writeFileSync(path.join(DIR, 'laporan-uts.compiled.md'), core);

// ---------- front matter ----------
const T = (text, o = {}) => new TextRun({ text, font: FONT, size: SIZE, ...o });
const P = (children, o = {}) => new Paragraph({ alignment: AlignmentType.CENTER, ...o, children });

function cover() {
  return [
    P([T('LAPORAN UJIAN TENGAH SEMESTER', { bold: true, size: 28 })], { spacing: { before: 600, after: 120 } }),
    P([T('SISTEM PENDUKUNG KEPUTUSAN', { bold: true, size: 28 })], { spacing: { after: 900 } }),
    P([T(TITLE, { bold: true, size: 36 })], { spacing: { after: 240 } }),
    P([T(SUBTITLE, { size: 26 })], { spacing: { line: LINE, after: 1400 } }),
    P([T('Disusun oleh: Kelompok 1', { bold: true })], { spacing: { after: 200 } }),
    ...MEMBERS.map(([n, nim]) => P([T(`${n}  (${nim})`)], { spacing: { after: 60 } })),
    P([T('UNIVERSITAS KRISTEN KRIDA WACANA', { bold: true })], { spacing: { before: 1800, after: 60 } }),
    P([T('JAKARTA', { bold: true })], { spacing: { after: 60 } }),
    P([T('2026', { bold: true })]),
  ];
}

function frontList(title, entries, first) {
  const out = [new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: first ? 0 : 360, after: 240 },
    children: [T(title, { bold: true })] })];
  entries.forEach(e => out.push(new Paragraph({
    spacing: { line: LINE, after: 40 }, indent: { left: e.level === 2 ? 360 : 0 },
    tabStops: [{ type: TabStopType.RIGHT, position: md.ST.contentW, leader: 'dot' }],
    children: [T(e.title, { bold: e.level === 1 }), T(`\t${e.page}`)],
  })));
  return out;
}

function collect() {
  const toc = md.headingsOf(core, 2);
  const lines = core.split('\n');
  const figs = lines.map(l => l.match(/^!\[(Gambar \d+\..*)\]/)).filter(Boolean).map(m => ({ title: m[1], level: 3 }));
  const tabs = lines.map(l => l.match(/^(Tabel \d+\..*)$/)).filter(Boolean).map(m => ({ title: m[1], level: 3 }));
  return { toc, figs, tabs };
}

async function write(pages) {
  const { toc, figs, tabs } = collect();
  const pg = e => (pages ? (pages[e.title] || '') : '00');
  const front = [
    ...frontList('DAFTAR ISI', [
      { title: 'DAFTAR ISI', level: 1, page: 'i' }, { title: 'DAFTAR GAMBAR', level: 1, page: 'ii' },
      { title: 'DAFTAR TABEL', level: 1, page: 'ii' },
      ...toc.map(e => ({ ...e, page: pg(e) })),
    ], true),
    new Paragraph({ children: [new PageBreak()] }),
    ...frontList('DAFTAR GAMBAR', figs.map(e => ({ ...e, page: pg(e) })), true),
    ...frontList('DAFTAR TABEL', tabs.map(e => ({ ...e, page: pg(e) })), false),
  ];
  const heading = (id, name, lvl, extra = {}) => ({ id, name, basedOn: 'Normal', next: 'Normal', quickFormat: true,
    run: { font: FONT, size: SIZE, bold: true, color: '000000', ...extra.run },
    paragraph: { spacing: { line: LINE, before: extra.before ?? 200, after: 100 }, outlineLevel: lvl, keepNext: true, keepLines: true, ...extra.paragraph } });
  const pageNo = new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
    children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: SIZE })] })] });
  const doc = new Document({
    creator: 'Kelompok 1', title: `Laporan UTS SPK - ${TITLE}`,
    styles: {
      default: { document: { run: { font: FONT, size: SIZE }, paragraph: { spacing: { line: LINE } } } },
      paragraphStyles: [
        heading('Heading1', 'Heading 1', 0, { before: 0, paragraph: { alignment: AlignmentType.CENTER } }),
        heading('Heading2', 'Heading 2', 1),
        heading('Heading3', 'Heading 3', 2, { run: { italics: true } }),
      ],
    },
    numbering: { config: [
      { reference: 'bullets', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 360 } } } },
        { level: 1, format: LevelFormat.BULLET, text: '–', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: 'numbers', levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 360 } } } },
        { level: 1, format: LevelFormat.LOWER_LETTER, text: '%2)', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ] },
    sections: [
      { properties: { page: { size: { width: PAGE_W, height: PAGE_H }, margin: MARGIN } }, children: cover() },
      { properties: { page: { size: { width: PAGE_W, height: PAGE_H }, margin: MARGIN,
          pageNumbers: { start: 1, formatType: NumberFormat.LOWER_ROMAN } } },
        footers: { default: pageNo }, children: front },
      { properties: { page: { size: { width: PAGE_W, height: PAGE_H }, margin: MARGIN,
          pageNumbers: { start: 1, formatType: NumberFormat.DECIMAL } } },
        footers: { default: pageNo }, children: md.parse(core, DIR, { hanging: /DAFTAR PUSTAKA/ }) },
    ],
  });
  fs.writeFileSync(OUT, await Packer.toBuffer(doc));
}

function pageTexts() {
  const pdf = path.join(os.tmpdir(), `uts-${process.pid}.pdf`);
  execFileSync(path.join(__dirname, 'render.sh'), [OUT, pdf], { stdio: 'ignore' });
  return execFileSync(PY, [path.join(__dirname, 'pdf_pages.py'), pdf], { maxBuffer: 1 << 26 })
    .toString().trim().split('\n').map(l => md.squash(l.split('\t').slice(1).join('\t')));
}

(async () => {
  await write(null);
  const texts = pageTexts();
  const start = texts.findIndex(t => t.includes('BAB1.PENDAHULUAN') && !t.includes('DAFTARISI'));
  const { toc, figs, tabs } = collect();
  const pages = {};
  let cursor = start;
  for (const e of toc) {
    for (let k = cursor; k < texts.length; k++) if (texts[k].includes(md.squash(e.title))) { pages[e.title] = String(k - start + 1); cursor = k; break; }
  }
  for (const e of [...figs, ...tabs]) {
    const key = md.squash(e.title.split('.')[0] + '.');
    const k = texts.findIndex((t, i) => i >= start && t.includes(key));
    if (k >= 0) pages[e.title] = String(k - start + 1);
  }
  await write(pages);
  console.log(`cover + front matter: ${start} pages; body: ${texts.length - start} pages`);
  const missing = [...toc, ...figs, ...tabs].filter(e => !pages[e.title]).map(e => e.title);
  if (missing.length) console.warn('page not found:', missing);
  console.log('->', OUT);
})();
