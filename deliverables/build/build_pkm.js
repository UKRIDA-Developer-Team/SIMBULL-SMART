// Proposal PKM-KC 2026 -> deliverables/pkm/Proposal-PKM-KC.docx
// Format (Format Proposal PKM-KC 2026): no cover/abstract; Daftar Isi etc. with roman page numbers
// bottom-right; Bab 1 .. Lampiran with arabic numbers top-right starting at 1; Times New Roman 12,
// line spacing 1.15, justified, A4, margins left 4 cm, right/top/bottom 3 cm.
const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync } = require('child_process');
const {
  Document, Packer, Paragraph, TextRun, AlignmentType, LevelFormat, Header, Footer, PageNumber,
  NumberFormat, TabStopType, PageBreak,
} = require('docx');
const md = require('./md2docx');

const DIR = path.resolve(__dirname, '..', 'pkm');
const OUT = path.join(DIR, 'Proposal-PKM-KC.docx');
const PY = path.resolve(__dirname, '..', '..', 'app', '.venv', 'bin', 'python');
const cm = c => Math.round(c * 567);
const PAGE_W = 11906, PAGE_H = 16838;
const MARGIN = { left: cm(4), right: cm(3), top: cm(3), bottom: cm(3), header: cm(1.5), footer: cm(1.5) };
const FONT = 'Times New Roman', SIZE = 24, LINE = 276;   // 12 pt, 1.15 spacing

md.configure({
  font: FONT, size: SIZE, tableSize: 20, contentW: PAGE_W - MARGIN.left - MARGIN.right,
  maxImgHpx: Math.round(8.0 * 96), para: { spacing: { line: LINE, after: 100 } },
  listSpacing: { line: LINE, after: 40 }, tableHead: 'E7E6E6', tableBorder: '000000',
  captionRun: { size: 22 }, imgScale: 1, codeFont: FONT, keepNextPattern: /^Tabel \d+\./,
});

const core = fs.readFileSync(path.join(DIR, 'proposal-inti.md'), 'utf8');
const lampiran = fs.readFileSync(path.join(DIR, 'proposal-lampiran.md'), 'utf8');
const T = (text, o = {}) => new TextRun({ text, font: FONT, size: SIZE, ...o });

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
  const heads = md.headingsOf(core + '\n' + lampiran, 2);
  const lines = (core + '\n' + lampiran).split('\n');
  const figs = lines.map(l => l.match(/^!\[(Gambar \d+\..*)\]/)).filter(Boolean).map(m => ({ title: m[1], level: 3 }));
  const tabs = lines.map(l => l.match(/^(Tabel \d+\..*)$/)).filter(Boolean).map(m => ({ title: m[1], level: 3 }));
  const lamp = heads.filter(h => /^Lampiran \d/.test(h.title)).map(h => ({ ...h, level: 3 }));
  const toc = heads.filter(h => !/^Lampiran \d/.test(h.title));
  return { toc, figs, tabs, lamp };
}

async function write(pages) {
  const { toc, figs, tabs, lamp } = collect();
  const pg = e => (pages ? (pages[e.title] || '') : '00');
  const front = [
    ...frontList('DAFTAR ISI', [
      { title: 'DAFTAR ISI', level: 1, page: 'i' }, { title: 'DAFTAR GAMBAR', level: 1, page: 'ii' },
      { title: 'DAFTAR TABEL', level: 1, page: 'ii' }, { title: 'DAFTAR LAMPIRAN', level: 1, page: 'ii' },
      ...toc.map(e => ({ ...e, page: pg(e) })),
    ], true),
    new Paragraph({ children: [new PageBreak()] }),
    ...frontList('DAFTAR GAMBAR', figs.map(e => ({ ...e, page: pg(e) })), true),
    ...frontList('DAFTAR TABEL', tabs.map(e => ({ ...e, page: pg(e) })), false),
    ...frontList('DAFTAR LAMPIRAN', lamp.map(e => ({ ...e, page: pg(e) })), false),
  ];
  const body = [
    ...md.parse(core, DIR, { hanging: /DAFTAR PUSTAKA/ }),
    new Paragraph({ children: [new PageBreak()] }),
    ...md.parse(lampiran, DIR),
  ];
  const heading = (id, name, lvl, extra = {}) => ({ id, name, basedOn: 'Normal', next: 'Normal', quickFormat: true,
    run: { font: FONT, size: SIZE, bold: true, color: '000000', ...extra.run },
    paragraph: { spacing: { line: LINE, before: extra.before ?? 200, after: 100 }, outlineLevel: lvl, keepNext: true, keepLines: true, ...extra.paragraph } });
  const doc = new Document({
    creator: 'Kelompok 1', title: 'Proposal PKM-KC',
    styles: {
      default: { document: { run: { font: FONT, size: SIZE }, paragraph: { spacing: { line: LINE } } } },
      paragraphStyles: [
        heading('Heading1', 'Heading 1', 0, { before: 0, paragraph: { pageBreakBefore: false } }),
        heading('Heading2', 'Heading 2', 1),
        heading('Heading3', 'Heading 3', 2, { run: { italics: true } }),
      ],
    },
    numbering: { config: [
      { reference: 'bullets', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 360 } } } },
        { level: 1, format: LevelFormat.BULLET, text: '–', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: 'numbers', levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '(%1)', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 420, hanging: 420 } } } },
        { level: 1, format: LevelFormat.LOWER_LETTER, text: '%2)', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 840, hanging: 420 } } } }] },
    ] },
    sections: [
      { properties: { page: { size: { width: PAGE_W, height: PAGE_H }, margin: MARGIN,
          pageNumbers: { start: 1, formatType: NumberFormat.LOWER_ROMAN } } },
        footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: SIZE })] })] }) },
        children: front },
      { properties: { page: { size: { width: PAGE_W, height: PAGE_H }, margin: MARGIN,
          pageNumbers: { start: 1, formatType: NumberFormat.DECIMAL } } },
        headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: SIZE })] })] }) },
        footers: { default: new Footer({ children: [new Paragraph({ children: [] })] }) },
        children: body },
    ],
  });
  fs.writeFileSync(OUT, await Packer.toBuffer(doc));
}

function pageTexts() {
  const pdf = path.join(os.tmpdir(), `pkm-${process.pid}.pdf`);
  execFileSync(path.join(__dirname, 'render.sh'), [OUT, pdf], { stdio: 'ignore' });
  return execFileSync(PY, [path.join(__dirname, 'pdf_pages.py'), pdf], { maxBuffer: 1 << 26 })
    .toString().trim().split('\n').map(l => md.squash(l.split('\t').slice(1).join('\t')));
}

(async () => {
  await write(null);
  const texts = pageTexts();
  const start = texts.findIndex((t, i) => i > 0 && t.includes('BAB1.PENDAHULUAN') && !t.includes('DAFTARISI'));
  const { toc, figs, tabs, lamp } = collect();
  const pages = {};
  let cursor = start;
  for (const e of [...toc, ...lamp].sort((a, b) => 0)) {
    for (let k = cursor; k < texts.length; k++) if (texts[k].includes(md.squash(e.title))) { pages[e.title] = String(k - start + 1); cursor = k; break; }
  }
  for (const e of [...figs, ...tabs]) {
    const key = md.squash(e.title.split('.')[0] + '.');
    const k = texts.findIndex((t, i) => i >= start && t.includes(key));
    if (k >= 0) pages[e.title] = String(k - start + 1);
  }
  await write(pages);
  const lampStart = texts.findIndex((t, i) => i >= start && t.startsWith(md.squash('1LAMPIRAN')) || (i >= start && t.includes('LAMPIRANLampiran1.Biodata') && !t.includes('DAFTARLAMPIRAN')));
  console.log(`front matter: ${start} pages; core (Bab 1 – Daftar Pustaka): ${lampStart - start} pages; total ${texts.length}`);
  const missing = [...toc, ...lamp, ...figs, ...tabs].filter(e => !pages[e.title]).map(e => e.title);
  if (missing.length) console.warn('page not found:', missing);
  console.log('->', OUT);
})();
