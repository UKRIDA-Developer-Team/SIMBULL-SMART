// Minimal Markdown -> DOCX converter for the project deliverables (docx-js).
//
// Supports: # / ## / ### / #### headings, paragraphs, **bold**, *italic*, `code`,
// ⟦placeholder⟧ (yellow highlight), pipe tables, bullet and numbered lists (2 levels),
// ``` code blocks, > blockquotes, ![caption](image.png), and three markers:
//   [[WIDTHS 8,10,12 size=16]]  column widths (% of text width) and font size for the next table
//   [[TOC]]        table of contents field (Word/ONLYOFFICE fill it on open)
//   [[PAGEBREAK]]  page break
//
// Usage from another script:
//   const { build } = require('./md2docx');
//   await build({ markdown, baseDir, out, title, cover: [...paragraphs] });
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell, WidthType,
  BorderStyle, ShadingType, AlignmentType, LevelFormat, ImageRun, TableOfContents, PageBreak,
  Footer, Header, PageNumber, TabStopType,
} = require('docx');

const PAGE_W = 11906, PAGE_H = 16838, MARGIN = 1440;           // A4, 1" margins (DXA)
// Mutable style so other builders (e.g. the PKM proposal) can reuse the parser with their own format.
const ST = {
  font: 'Calibri', size: 22, tableSize: 19, contentW: PAGE_W - 2 * MARGIN, maxImgHpx: Math.round(8.3 * 96),
  para: { spacing: { after: 120 } }, tableHead: 'DCE6F2', tableBorder: 'BFBFBF', captionColor: '555555',
};
function configure(opts) { Object.assign(ST, opts); }
const CONTENT_PX = Math.round((ST.contentW / 1440) * 96);          // ~602 px (default layout)

function pngSize(file) {
  const b = fs.readFileSync(file);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20), data: b };
}

// ---------- inline ----------
const ESC_STAR = '\uE000';
function inline(text, base = {}) {
  text = text.replace(/\\\*/g, ESC_STAR);                         // markdown escape \* -> literal *
  const runs = [];
  const re = /(\*\*\*[^*]+\*\*\*|\*\*[^*]+\*\*|⟦[^⟧]*⟧|`[^`]+`|\*[^*\s][^*]*\*)/g;
  let last = 0, m;
  const push = (t, opts = {}) => { if (t) runs.push(new TextRun({ text: t.replace(/\uE000/g, '*'), font: ST.font, ...base, ...opts })); };
  while ((m = re.exec(text))) {
    push(text.slice(last, m.index));
    const tok = m[0];
    if (tok.startsWith('***')) push(tok.slice(3, -3), { bold: true, italics: true });
    else if (tok.startsWith('**')) runs.push(...inline(tok.slice(2, -2), { ...base, bold: true }));
    else if (tok.startsWith('⟦')) push(tok.replace(/[`*]/g, ''), { highlight: 'yellow', bold: true });
    else if (tok.startsWith('`')) push(tok.slice(1, -1), { font: ST.codeFont || 'Courier New', size: (base.size || ST.size) - (ST.codeFont ? 0 : 2) });
    else runs.push(...inline(tok.slice(1, -1), { ...base, italics: true }));
    last = m.index + tok.length;
  }
  push(text.slice(last));
  return runs;
}

// ---------- blocks ----------
function splitRow(line) {
  return line.trim().replace(/^\|/, '').replace(/\|$/, '')
    .split(/(?<!\\)\|/).map(c => c.trim().replace(/\\\|/g, '|'));
}

function table(rows, layout) {
  const header = splitRow(rows[0]);
  const body = rows.slice(2).map(splitRow);
  const n = header.length;
  const size = (layout && layout.size) || ST.tableSize;
  const lens = header.map((h, i) => Math.max(h.length, ...body.map(r => (r[i] || '').length), 3));
  const capped = lens.map(l => Math.min(l, 60));
  const total = capped.reduce((a, b) => a + b, 0);
  let widths = layout && layout.pct
    ? layout.pct.map(p => Math.round((p / 100) * ST.contentW))
    : capped.map(l => Math.max(700, Math.round((l / total) * ST.contentW)));
  const scale = ST.contentW / widths.reduce((a, b) => a + b, 0);
  widths = widths.map(w => Math.floor(w * scale));
  widths[n - 1] += ST.contentW - widths.reduce((a, b) => a + b, 0);
  const border = { style: BorderStyle.SINGLE, size: 4, color: ST.tableBorder };
  const borders = { top: border, bottom: border, left: border, right: border };
  const cell = (text, i, head) => new TableCell({
    width: { size: widths[i], type: WidthType.DXA },
    borders,
    shading: head && ST.tableHead ? { fill: ST.tableHead, type: ShadingType.CLEAR, color: 'auto' } : undefined,
    margins: { top: 50, bottom: 50, left: 90, right: 90 },
    children: [new Paragraph({ spacing: { before: 0, after: 0 }, alignment: ST.tableAlign && !head ? ST.tableAlign(i) : undefined, children: inline(text || '', { size, bold: head || undefined }) })],
  });
  return new Table({
    width: { size: ST.contentW, type: WidthType.DXA },
    columnWidths: widths,
    rows: [
      new TableRow({ tableHeader: true, children: header.map((h, i) => cell(h, i, true)) }),
      ...body.map(r => new TableRow({ children: header.map((_, i) => cell(r[i], i, false)) })),
    ],
  });
}

function image(src, caption, baseDir) {
  const file = path.resolve(baseDir, src);
  const { w, h, data } = pngSize(file);
  const maxW = Math.round((ST.contentW / 1440) * 96 * (ST.imgScale || 1));
  let width = maxW, height = Math.round((h / w) * width);
  if (height > ST.maxImgHpx) { height = ST.maxImgHpx; width = Math.round((w / h) * height); }
  const out = [new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { before: 120, after: 60 }, keepNext: !!caption,
    children: [new ImageRun({ type: 'png', data, transformation: { width, height },
      altText: { title: caption || src, description: caption || src, name: path.basename(src) } })],
  })];
  if (caption) out.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 },
    children: inline(caption, ST.captionRun || { italics: true, size: 18, color: ST.captionColor }) }));
  return out;
}

function parse(markdown, baseDir, opts = {}) {
  const lines = markdown.replace(/\r/g, '').split('\n');
  const out = [];
  let i = 0, para = [], listInstance = 0, inList = false, inHanging = false, layout = null;
  const flush = () => {
    if (para.length) {
      const text = para.join(' ');
      const hang = opts.hanging && inHanging;
      out.push(new Paragraph({ ...ST.para, alignment: AlignmentType.JUSTIFIED,
        keepNext: ST.keepNextPattern ? ST.keepNextPattern.test(text) : undefined,
        indent: hang ? { left: 720, hanging: 720 } : undefined, children: inline(text) }));
      para = [];
    }
  };
  const headings = { 1: HeadingLevel.HEADING_1, 2: HeadingLevel.HEADING_2, 3: HeadingLevel.HEADING_3, 4: HeadingLevel.HEADING_4 };
  while (i < lines.length) {
    const line = lines[i];
    const t = line.trim();
    if (t === '[[TOC]]') {
      flush();
      out.push(new Paragraph({ spacing: { before: 120, after: 240 },
        children: [new TextRun({ text: opts.tocTitle || 'Daftar Isi', font: ST.font, size: 32, bold: true, color: '1F3864' })] }));
      out.push(new TableOfContents(opts.tocTitle || 'Daftar Isi', { hyperlink: false, headingStyleRange: '1-2',
        cachedEntries: (opts.toc || []).map(e => ({ title: e.title, level: e.level, page: e.page })) }));
      i++; continue;
    }
    const wm = t.match(/^\[\[WIDTHS ([\d.,]+)(?: size=(\d+))?\]\]$/);
    if (wm) { flush(); layout = { pct: wm[1].split(',').map(Number), size: wm[2] ? Number(wm[2]) : undefined }; i++; continue; }
    if (t === '[[PAGEBREAK]]') { flush(); out.push(new Paragraph({ children: [new PageBreak()] })); i++; continue; }
    if (/^#{1,4} /.test(t)) {
      flush();
      const level = t.match(/^#+/)[0].length;
      if (level === 1) inHanging = !!(opts.hanging && opts.hanging.test(t));
      out.push(new Paragraph({ heading: headings[level], children: inline(t.replace(/^#+ /, '')) }));
      i++; continue;
    }
    if (t === '---' || t === '') { flush(); i++; continue; }
    if (t.startsWith('```')) {
      flush(); i++;
      const code = [];
      while (i < lines.length && !lines[i].trim().startsWith('```')) code.push(lines[i++]);
      i++;
      code.forEach(c => out.push(new Paragraph({ spacing: { before: 0, after: 0 },
        shading: { fill: 'F2F2F2', type: ShadingType.CLEAR, color: 'auto' },
        children: [new TextRun({ text: c || ' ', font: 'Courier New', size: 16 })] })));
      out.push(new Paragraph({ spacing: { after: 120 }, children: [] }));
      continue;
    }
    if (t.startsWith('|')) {
      flush();
      const rows = [];
      while (i < lines.length && lines[i].trim().startsWith('|')) rows.push(lines[i++]);
      out.push(table(rows, layout));
      layout = null;
      out.push(new Paragraph({ spacing: { after: 120 }, children: [] }));
      continue;
    }
    const img = t.match(/^!\[(.*)\]\((.+)\)$/);
    if (img) { flush(); out.push(...image(img[2], img[1], baseDir)); i++; continue; }
    if (t.startsWith('>')) {
      flush();
      const q = [];
      while (i < lines.length && lines[i].trim().startsWith('>')) q.push(lines[i++].trim().replace(/^>\s?/, ''));
      out.push(new Paragraph({ spacing: { after: 160 }, indent: { left: 400 },
        border: { left: { style: BorderStyle.SINGLE, size: 12, color: '4C72B0', space: 8 } },
        children: inline(q.join(' '), { italics: false, color: '333333' }) }));
      continue;
    }
    const li = line.match(/^(\s*)([-*]|\d+\.)\s+(.*)$/);
    if (!li && t !== '') inList = false;
    if (li) {
      flush();
      if (!inList) { listInstance += 1; inList = true; }
      const level = li[1].length >= 2 ? 1 : 0;
      const numbered = /\d+\./.test(li[2]);
      let text = li[3];
      i++;
      // continuation lines (indented, not a new item)
      while (i < lines.length && /^\s{2,}\S/.test(lines[i]) && !/^\s*([-*]|\d+\.)\s+/.test(lines[i])) text += ' ' + lines[i++].trim();
      out.push(new Paragraph({ numbering: { reference: numbered ? 'numbers' : 'bullets', level, instance: listInstance },
        spacing: ST.listSpacing || { after: 60 }, children: inline(text) }));
      continue;
    }
    para.push(t); i++;
  }
  flush();
  return out;
}

// toc: [{title, level, page}] pre-filled entries (a real TOC field, so Word can update it later).
async function build({ markdown, baseDir, out, title, cover = [], toc = [], tocTitle = 'Daftar Isi' }) {
  const doc = new Document({
    creator: 'Kelompok 1', title,
    features: { updateFields: true },
    styles: {
      default: { document: { run: { font: ST.font, size: 22 } } },
      paragraphStyles: [
        { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
          run: { size: 32, bold: true, font: ST.font, color: '1F3864' }, paragraph: { spacing: { before: 360, after: 180 }, outlineLevel: 0, keepNext: true, keepLines: true } },
        { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
          run: { size: 26, bold: true, font: ST.font, color: '2E74B5' }, paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1, keepNext: true, keepLines: true } },
        { id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal', quickFormat: true,
          run: { size: 23, bold: true, font: ST.font, color: '404040' }, paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 2, keepNext: true, keepLines: true } },
        { id: 'TOC1', name: 'toc 1', basedOn: 'Normal', next: 'Normal', run: { bold: true, size: 22, font: ST.font },
          paragraph: { spacing: { before: 100, after: 20 } } },
        { id: 'TOC2', name: 'toc 2', basedOn: 'Normal', next: 'Normal', run: { size: 21, font: ST.font },
          paragraph: { indent: { left: 360 }, spacing: { before: 0, after: 20 } } },
        { id: 'Heading4', name: 'Heading 4', basedOn: 'Normal', next: 'Normal', quickFormat: true,
          run: { size: 22, bold: true, italics: true, font: ST.font }, paragraph: { spacing: { before: 160, after: 80 }, outlineLevel: 3, keepNext: true, keepLines: true } },
      ],
    },
    numbering: { config: [
      { reference: 'bullets', levels: [
        { level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
        { level: 1, format: LevelFormat.BULLET, text: '◦', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 1440, hanging: 360 } } } } ] },
      { reference: 'numbers', levels: [
        { level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
        { level: 1, format: LevelFormat.LOWER_LETTER, text: '%2)', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 1440, hanging: 360 } } } } ] },
    ] },
    sections: [
      ...(cover.length ? [{ properties: { page: { size: { width: PAGE_W, height: PAGE_H }, margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN } } }, children: cover }] : []),
      {
        properties: { page: { size: { width: PAGE_W, height: PAGE_H }, margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN }, pageNumbers: { start: 1 } } },
        headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT,
          children: [new TextRun({ text: title, font: ST.font, size: 16, color: '888888' })] })] }) },
        footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
          children: [new TextRun({ children: [PageNumber.CURRENT], font: ST.font, size: 18 })] })] }) },
        children: parse(markdown, baseDir, { toc, tocTitle }),
      },
    ],
  });
  fs.writeFileSync(out, await Packer.toBuffer(doc));
  return out;
}

function coverPage({ kicker, title, subtitle, members, footer, logo }) {
  const P = (children, opts = {}) => new Paragraph({ alignment: AlignmentType.CENTER, ...opts, children });
  const T = (text, o = {}) => new TextRun({ text, font: ST.font, ...o });
  const out = [
    P([T(kicker, { size: 26, bold: true, color: '2E74B5' })], { spacing: { before: 1800, after: 240 } }),
    P([T(title, { size: 40, bold: true, color: '1F3864' })], { spacing: { after: 240 } }),
    P([T(subtitle, { size: 24, italics: true, color: '404040' })], { spacing: { after: 1400 } }),
  ];
  if (logo) out.push(...image(logo.src, '', logo.baseDir));
  out.push(P([T('Disusun oleh: Kelompok 1', { size: 24, bold: true })], { spacing: { before: 400, after: 200 } }));
  members.forEach(([name, nim]) => out.push(P([T(`${name}`, { size: 22 }), T(`  —  ${nim}`, { size: 22, color: '555555' })], { spacing: { after: 60 } })));
  footer.forEach((f, k) => out.push(P([T(f, { size: 22, bold: k === 0 })], { spacing: { before: k === 0 ? 1400 : 0, after: 60 } })));
  return out;   // the next section starts on a new page
}

// ---------- two-pass build: fill the TOC with real page numbers ----------
const { execFileSync } = require('child_process');
const os = require('os');
const PY = path.resolve(__dirname, '..', '..', 'app', '.venv', 'bin', 'python');

function plain(t) { return t.replace(/\*\*\*|\*\*|\*|`|⟦|⟧/g, ''); }
function squash(t) { return t.replace(/\s+/g, ''); }

function headingsOf(markdown, maxLevel = 2) {
  let inCode = false;
  return markdown.split('\n').flatMap(line => {
    if (line.trim().startsWith('```')) inCode = !inCode;
    const m = !inCode && line.match(/^(#{1,4}) (.+)$/);
    return m && m[1].length <= maxLevel ? [{ title: plain(m[2].trim()), level: m[1].length }] : [];
  });
}

// firstNumberedPage: PDF page index that shows page number 1 (cover pages are unnumbered).
async function buildWithToc(args, { maxLevel = 2, firstNumberedPage = 2 } = {}) {
  const entries = headingsOf(args.markdown, maxLevel);
  await build({ ...args, toc: entries.map(e => ({ ...e, page: '00' })) });
  const pdf = path.join(os.tmpdir(), `toc-${process.pid}.pdf`);
  execFileSync(path.join(__dirname, 'render.sh'), [args.out, pdf], { stdio: 'ignore' });
  const pages = execFileSync(PY, [path.join(__dirname, 'pdf_pages.py'), pdf], { maxBuffer: 1 << 26 })
    .toString().trim().split('\n').map(l => squash(l.split('\t').slice(1).join('\t')));
  // skip the pages holding the TOC itself: start searching after the last page that lists every title
  let from = 0;
  let cursor = from;
  const toc = entries.map(e => {
    const key = squash(e.title);
    let idx = -1;
    for (let k = cursor; k < pages.length; k++) {
      const tocPage = entries.filter(x => pages[k].includes(squash(x.title))).length > entries.length * 0.5;
      if (!tocPage && pages[k].includes(key)) { idx = k; break; }
    }
    if (idx >= 0) cursor = idx;
    return { ...e, page: idx >= 0 ? String(idx + 1 - (firstNumberedPage - 1)) : '' };
  });
  await build({ ...args, toc });
  const missing = toc.filter(e => !e.page).map(e => e.title);
  if (missing.length) console.warn('TOC: page not found for', missing);
  return args.out;
}

module.exports = { build, buildWithToc, coverPage, image, parse, inline, configure, ST, headingsOf, squash, CONTENT_PX };
