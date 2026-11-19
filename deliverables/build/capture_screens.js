// Capture the app screens for the User Manual, plus the element boxes annotate.py draws callouts on.
//
// Covers both zones: the app (Beranda, Nilai siswa, Nilai kelas, Bantuan) and the technical report (Bab 1-8).
//
// Start the app first (cd app && .venv/bin/streamlit run streamlit_app.py), then:
//   node capture_screens.js [app_url]          (default http://localhost:8501)
// Uses the local Google Chrome through puppeteer-core; set CHROME=/path/to/chrome to override.
// Output: deliverables/user-manual/screens/<name>.png + <name>.json (boxes in image pixels).
const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer-core');

const URL = (process.argv[2] || 'http://localhost:8501').replace(/\/$/, '');
const OUT = path.resolve(__dirname, '..', 'user-manual', 'screens');
const WIDTH = 1180, HEIGHT = 860, DPR = 1.5;
const CHROMES = [process.env.CHROME, '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/Applications/Browser/Google Chrome.app/Contents/MacOS/Google Chrome', '/usr/bin/google-chrome', '/usr/bin/chromium'];

const sleep = ms => new Promise(r => setTimeout(r, ms));

// Wait until Streamlit has finished the current run and every image has loaded.
async function settle(page, extra = 800) {
  let calm = 0;
  for (let i = 0; i < 300 && calm < 4; i++) {
    const busy = await page.evaluate(() =>
      !!document.querySelector('[data-testid="stStatusWidget"], [data-testid="stSpinner"], [data-testid="stSkeleton"]') ||
      [...document.images].some(img => !img.complete));
    calm = busy ? 0 : calm + 1;
    await sleep(250);
  }
  await sleep(extra);
}

// A box spec is {sel, text?, nth?, all?} or an array of specs (their union). Returns [x, y, w, h] in CSS px.
async function measure(page, specs) {
  return page.evaluate(specs => {
    const union = rs => {
      if (!rs.length || rs.some(r => !r)) return null;
      const x0 = Math.min(...rs.map(r => r[0])), y0 = Math.min(...rs.map(r => r[1]));
      return [x0, y0, Math.max(...rs.map(r => r[0] + r[2])) - x0, Math.max(...rs.map(r => r[1] + r[3])) - y0];
    };
    const rect = spec => {
      if (Array.isArray(spec)) return union(spec.map(rect));
      let els = [...document.querySelectorAll(spec.sel)];
      if (spec.text) els = els.filter(e => e.textContent.includes(spec.text));
      els = spec.nth != null ? [els[spec.nth]].filter(Boolean) : spec.all ? els : els.slice(0, 1);
      // Hidden elements (e.g. in an inactive tab) report a 0x0 box at the origin: leave them out.
      return union(els.map(e => e.getBoundingClientRect()).filter(r => r.width > 0 && r.height > 0)
        .map(r => [r.left, r.top, r.width, r.height]));
    };
    const out = {};
    for (const [key, spec] of Object.entries(specs)) out[key] = rect(spec);
    // The page's content column (main block minus its side padding), used for horizontal crops.
    const main = document.querySelector('[data-testid="stMainBlockContainer"]');
    const r = main.getBoundingClientRect(), cs = getComputedStyle(main);
    out.content = [r.left + parseFloat(cs.paddingLeft), r.top, r.width - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight), r.height];
    return out;
  }, specs);
}

// Screenshot the whole scrollable page (or just the viewport) and save the boxes next to it.
async function shot(page, name, specs = {}, { full = true } = {}) {
  await page.evaluate(() => document.querySelector('[data-testid="stMain"]').scrollTo(0, 0));
  if (full) {
    for (let i = 0; i < 3; i++) {
      const h = await page.evaluate(() => document.querySelector('[data-testid="stMain"]').scrollHeight);
      await page.setViewport({ width: WIDTH, height: Math.max(HEIGHT, h), deviceScaleFactor: DPR });
      await settle(page, 1200);
      const h2 = await page.evaluate(() => document.querySelector('[data-testid="stMain"]').scrollHeight);
      if (h2 <= Math.max(HEIGHT, h)) break;
    }
  }
  const boxes = await measure(page, specs);
  const missing = Object.keys(boxes).filter(k => !boxes[k]);
  if (missing.length) throw new Error(`${name}: no element for ${missing.join(', ')}`);
  await page.screenshot({ path: path.join(OUT, `${name}.png`) });
  const px = Object.fromEntries(Object.entries(boxes).map(([k, b]) => [k, b.map(v => Math.round(v * DPR))]));
  fs.writeFileSync(path.join(OUT, `${name}.json`), JSON.stringify(px));
  await page.setViewport({ width: WIDTH, height: HEIGHT, deviceScaleFactor: DPR });
  await settle(page, 300);
  console.log('screen', name);
}

async function clickText(page, selector, text) {
  const handles = await page.$$(selector);
  for (const h of handles) {
    if ((await h.evaluate(e => e.textContent)).includes(text)) {
      await h.evaluate(e => e.scrollIntoView({ block: 'center' }));
      await h.click();
      await settle(page);
      return;
    }
  }
  throw new Error(`no ${selector} with text "${text}"`);
}

async function open(page, route, waitFor) {
  await page.goto(`${URL}/${route}`, { waitUntil: 'networkidle2' });
  await page.waitForSelector(waitFor, { timeout: 60000 });
  await settle(page, 1500);
}

// Click the Streamlit element whose label contains text (scrolls it into view first).
async function clickIn(page, scope, text) {
  await clickText(page, scope, text);
}

async function waitText(page, text, timeout = 120000) {
  await page.waitForFunction(t => document.body.innerText.includes(t), { timeout }, text);
  await settle(page, 1200);
}

(async () => {
  const exe = CHROMES.find(p => p && fs.existsSync(p));
  if (!exe) throw new Error('Google Chrome not found; set CHROME=/path/to/chrome');
  fs.mkdirSync(OUT, { recursive: true });
  for (const f of fs.readdirSync(OUT)) fs.unlinkSync(path.join(OUT, f));
  const browser = await puppeteer.launch({ executablePath: exe, headless: true });
  const page = await browser.newPage();
  await page.setViewport({ width: WIDTH, height: HEIGHT, deviceScaleFactor: DPR });

  const bar = {
    brand: { sel: '.spk-brand' }, nav: { sel: '.st-key-topnav' },
    zone: { sel: '[class*="st-key-zone_"]' }, lang: { sel: '.st-key-lang_switch' },
  };
  const frame = { title: { sel: '[data-testid="stMainBlockContainer"] h1' }, footer: { sel: '.spk-footer' } };

  // ================================================================ App zone
  // ---- Home
  await open(page, '', '.spk-preview');
  await shot(page, '01_home', {
    ...bar,
    cta: { sel: '[data-testid="stButton"]', text: 'Mulai penilaian' },
    cta_batch: { sel: '[data-testid="stButton"]', text: 'Nilai satu kelas' },
    preview: { sel: '.spk-preview' },
    steps: { sel: '[class*="st-key-card_step"]', all: true },
    alts: { sel: '[class*="st-key-card_alt_"]', all: true },
    report: { sel: '.st-key-card_report' },
    footer: { sel: '.spk-footer' },
  });

  // ---- One student: the empty questionnaire
  await open(page, 'student', '.st-key-card_q5');
  const form = {
    title: { sel: '[data-testid="stMainBlockContainer"] h1' },
    model: { sel: '[data-testid="stPopover"]' },
    q1: { sel: '.st-key-card_q1' }, q2: { sel: '.st-key-card_q2' }, q5: { sel: '.st-key-card_q5' },
    select: { sel: '.st-key-card_q2 [data-testid="stSelectbox"]' },
    grade: { sel: '.st-key-card_q2 [data-testid="stNumberInput"]' },
    radio: { sel: '.st-key-card_q2 [data-testid="stRadio"]' },
    tips: { sel: '.st-key-card_tips' },
    examples: { sel: '[data-testid="stButton"]', text: 'Contoh risiko', all: true },
    clear: { sel: '.st-key-clear_answers' },
    submit: { sel: '[data-testid="stFormSubmitButton"]' },
  };
  await shot(page, '02_form', form);

  // Submitting an empty form lists the unanswered questions
  await clickIn(page, '[data-testid="stFormSubmitButton"] button', 'Lihat rekomendasi');
  await waitText(page, 'belum dijawab');
  await shot(page, '03_missing', { ...form, missing: { sel: '[data-testid="stAlert"]', text: 'belum dijawab' } });

  // The model setting
  await page.click('[data-testid="stPopover"] button');
  await settle(page);
  await shot(page, '04_model', {
    button: { sel: '[data-testid="stPopover"]' },
    body: { sel: '[data-testid="stPopoverBody"]' },
    radio: { sel: '[data-testid="stPopoverBody"] [data-testid="stRadio"]' },
    note: { sel: '[data-testid="stPopoverBody"] p', text: 'Model aktif' },
  }, { full: false });
  await page.keyboard.press('Escape');
  await settle(page);

  // An example only fills the form
  await clickIn(page, '[data-testid="stButton"] button', 'Contoh risiko tinggi');
  await waitText(page, 'sudah dimuat');
  await shot(page, '05_example', { ...form, loaded: { sel: '[data-testid="stAlert"]', text: 'sudah dimuat' } });

  // ---- Result
  await clickIn(page, '[data-testid="stFormSubmitButton"] button', 'Lihat rekomendasi');
  await page.waitForSelector('.st-key-card_hero', { timeout: 60000 });
  await page.waitForSelector('.st-key-card_whatif_result [data-testid="stSlider"]', { timeout: 120000 });
  await settle(page, 2500);
  const result = {
    back: { sel: '[data-testid="stButton"]', text: 'Ubah jawaban' },
    safety: { sel: '[data-testid="stAlert"]' },
    hero: { sel: '.st-key-card_hero' },
    best: { sel: '.spk-hero-main' },
    anx: { sel: '.spk-hero-stat', nth: 0 },
    prio: { sel: '.spk-hero-stat', nth: 1 },
    rank: { sel: '.st-key-card_rank' },
    why: { sel: '.st-key-card_why' },
    factors: { sel: '.st-key-card_factors_result' },
    whatif: { sel: '.st-key-card_whatif_result' },
    cta: { sel: '.st-key-card_cta' },
    next: { sel: '.st-key-next_student' },
  };
  await shot(page, '06_result', result);

  // What-if with two factors: add sleep hours, lower burnout and raise sleep with the keyboard
  await page.click('.st-key-card_whatif_result [data-testid="stMultiSelect"] .react-aria-ComboBox input');
  await page.waitForSelector('[role="option"]', { timeout: 30000 });
  for (const o of await page.$$('[role="option"]')) {
    if ((await o.evaluate(e => e.textContent)).includes('Jam tidur')) { await o.click(); break; }
  }
  await settle(page);
  await page.keyboard.press('Escape');
  const THUMB = '.st-key-card_whatif_result input[type="range"]';   // Streamlit sliders are range inputs
  await page.waitForFunction(sel => document.querySelectorAll(sel).length === 2, { timeout: 30000 }, THUMB);
  await settle(page);
  const thumbs = await page.$$(THUMB);
  await thumbs[0].focus();
  for (let i = 0; i < 40; i++) await page.keyboard.press('ArrowLeft');
  await settle(page);
  const thumbs2 = await page.$$(THUMB);
  await thumbs2[1].focus();
  for (let i = 0; i < 30; i++) await page.keyboard.press('ArrowRight');
  await page.waitForSelector('.spk-whatif', { timeout: 60000 });
  await settle(page, 1500);
  await shot(page, '07_whatif', {
    whatif: { sel: '.st-key-card_whatif_result' },
    pick: { sel: '.st-key-card_whatif_result [data-testid="stMultiSelect"]' },
    sliders: { sel: '.st-key-card_whatif_result [data-testid="stSlider"]', all: true },
    out: { sel: '.spk-whatif' },
  });

  // ---- The same student's full calculation (report chapter 3), opened from the result
  await clickIn(page, '.st-key-card_cta [data-testid="stButton"] button', 'Buka perhitungan');
  await page.waitForSelector('.spk-toc', { timeout: 60000 });
  await page.waitForSelector('.spk-footer', { timeout: 300000 });
  await settle(page, 2500);
  await shot(page, '08_ch3', {
    ...bar, ...frame,
    eyebrow: { sel: '.spk-eyebrow' }, toc: { sel: '.spk-toc' }, model: { sel: '[data-testid="stPopover"]' },
    source: { sel: '[data-testid="stButtonGroup"]', text: 'Siswa terakhir' },
    s1: { sel: 'h3', text: '3.1' }, s4: { sel: 'h3', text: '3.4' }, s6: { sel: 'h3', text: '3.6' },
    s7: { sel: 'h3', text: '3.7' }, s8: { sel: 'h3', text: '3.8' }, s9: { sel: 'h3', text: '3.9' },
    s10: { sel: 'h3', text: '3.10' }, cap: { sel: '.spk-cap', nth: 0 },
    pager: { sel: '.st-key-ch_pager' },
  });

  // ---- Whole class: empty first, then the 30-student sample
  await open(page, 'class', '.st-key-card_demo');
  const cls = {
    title: { sel: '[data-testid="stMainBlockContainer"] h1' },
    upload: { sel: '[data-testid="stFileUploader"]' },
    demo: { sel: '.st-key-card_demo' },
    toggle: { sel: '.st-key-batch_demo' },
    template: { sel: '[data-testid="stDownloadButton"]', text: 'template' },
  };
  await shot(page, '09_class_empty', { ...cls, empty: { sel: '.st-key-card_class_empty' } });
  await page.click('.st-key-batch_demo label');
  await page.waitForSelector('.st-key-card_one', { timeout: 120000 });
  await settle(page, 2500);
  await clickIn(page, '[data-testid="stExpander"] summary', 'Opsi lanjutan');
  await shot(page, '10_class', {
    ...cls,
    note: { sel: '[data-testid="stAlert"]', text: 'Data contoh' },
    metrics: { sel: '[data-testid="stMetric"]', all: true },
    urgent: [{ sel: '[data-testid="stHeading"]', text: 'Perlu dirujuk segera' }, { sel: '[data-testid="stDataFrame"]', nth: 0 }],
    filters: [{ sel: '[data-testid="stMultiSelect"]' }, { sel: '.st-key-class_detail' }],
    table: { sel: '[data-testid="stDataFrame"]', nth: 1 },
    download: { sel: '[data-testid="stDownloadButton"]', text: 'rencana kelas' },
    programs: { sel: '[class*="st-key-card_prog_"]', all: true },
    one: { sel: '.st-key-card_one' },
    options: { sel: '[data-testid="stExpander"]', text: 'Opsi lanjutan' },
  });

  // ---- Help
  await open(page, 'help', '.st-key-card_help_read');
  await shot(page, '11_help', {
    ...frame, use: { sel: '.st-key-card_help_one, .st-key-card_help_class', all: true },
    read: { sel: '.st-key-card_help_read' }, notes: { sel: '.st-key-card_users, .st-key-card_care', all: true },
  });

  // ================================================================ Report zone
  const chapter = { ...bar, ...frame, eyebrow: { sel: '.spk-eyebrow' }, toc: { sel: '.spk-toc' },
    model: { sel: '[data-testid="stPopover"]' }, h: { sel: 'h3', nth: 0 }, cap: { sel: '.spk-cap', nth: 0 },
    pager: { sel: '.st-key-ch_pager' } };
  for (const [route, name] of [['report-data', '12_ch1'], ['report-model', '13_ch2'], ['report-xai', '14_ch4'],
                               ['report-smart', '15_ch5'], ['report-fairness', '16_ch6'],
                               ['report-architecture', '19_ch8']]) {
    await open(page, route, '.spk-toc');
    await page.waitForSelector('.spk-footer', { timeout: 300000 });
    await settle(page, 2500);
    await shot(page, name, chapter);
  }

  // ---- Chapter 7 (CRISP-DM): the stepper on phase 1, then phase 3 with the question-merge table open
  await open(page, 'report-crispdm', '.st-key-card_dm_hero');
  await page.waitForSelector('.spk-footer', { timeout: 300000 });
  const dm = { ...frame, stepper: { sel: '[data-testid="stButtonGroup"]', text: 'Business Understanding' },
    hero: { sel: '.st-key-card_dm_hero' }, kpis: { sel: '[data-testid="stMetric"]', all: true },
    steps: { sel: '[class*="st-key-card_dm_step"]', all: true }, main: { sel: '.st-key-card_dm_main' },
    side: { sel: '.st-key-card_dm_side' }, next: { sel: '.st-key-dm_next' } };
  await shot(page, '17_ch7', dm);
  await clickIn(page, '[data-testid="stButtonGroup"] button', 'Data Preparation');
  await page.waitForFunction(() => document.body.innerText.includes('FASE 3 DARI 6'), { timeout: 60000 });
  await settle(page, 1500);
  await clickIn(page, '[data-testid="stExpander"] summary', 'digabung');
  await shot(page, '18_ch7_prep', { ...dm, merge: { sel: '[data-testid="stExpander"]', text: 'digabung' } });

  // ---- English: the Home page after switching the language
  await open(page, '', '.spk-preview');
  await clickIn(page, '.st-key-lang_switch button', 'EN');
  await page.waitForFunction(() => document.body.innerText.includes('Start an assessment'), { timeout: 30000 });
  await settle(page, 1200);
  await shot(page, '20_en', bar, { full: false });

  await browser.close();
  console.log('screens ->', OUT);
})().catch(err => { console.error(err); process.exit(1); });
