// Capture the app screens for the User Manual, plus the element boxes annotate.py draws callouts on.
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
      return union(els.map(e => e.getBoundingClientRect()).map(r => [r.left, r.top, r.width, r.height]));
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

(async () => {
  const exe = CHROMES.find(p => p && fs.existsSync(p));
  if (!exe) throw new Error('Google Chrome not found; set CHROME=/path/to/chrome');
  fs.mkdirSync(OUT, { recursive: true });
  for (const f of fs.readdirSync(OUT)) fs.unlinkSync(path.join(OUT, f));
  const browser = await puppeteer.launch({ executablePath: exe, headless: true });
  const page = await browser.newPage();
  await page.setViewport({ width: WIDTH, height: HEIGHT, deviceScaleFactor: DPR });

  // ---- Home
  await open(page, '', '.spk-preview');
  await shot(page, '01_home', {
    nav: { sel: '[data-testid="stTopNavLinkContainer"]', all: true },
    lang: { sel: '.st-key-lang_switch' },
    cta: { sel: '[data-testid="stButton"]', text: 'Mulai penilaian' },
    cta_batch: { sel: '[data-testid="stButton"]', text: 'Nilai satu kelas' },
    preview: { sel: '.spk-preview' },
    steps: { sel: '[class*="st-key-card_step"]', all: true },
    alts: { sel: '[class*="st-key-card_alt_"]', all: true },
    notes: { sel: '.st-key-card_users, .st-key-card_care', all: true },
    footer: { sel: '.spk-footer' },
  });

  // ---- One student: questionnaire, weight profile, result
  await open(page, 'recommendation', '.st-key-card_q5');
  await shot(page, '02_reco_form', {
    title: { sel: '[data-testid="stMainBlockContainer"] h1' },
    view: { sel: '[data-testid="stButtonGroup"]', text: 'Satu siswa' },
    profile: { sel: '[data-testid="stPopover"]' },
    adv: { sel: '[data-testid="stCheckbox"]', text: 'Mode lanjutan' },
    q1: { sel: '.st-key-card_q1' },
    q2: { sel: '.st-key-card_q2' },
    q5: { sel: '.st-key-card_q5' },
    slider: { sel: '.st-key-card_q2 [data-testid="stSlider"]' },
    grade: { sel: '.st-key-card_q2 [data-testid="stNumberInput"]' },
    radio: { sel: '.st-key-card_q2 [data-testid="stRadio"]' },
    tips: { sel: '.st-key-card_tips' },
    examples: { sel: '.st-key-card_examples' },
    submit: { sel: '[data-testid="stFormSubmitButton"]' },
  });

  await page.click('[data-testid="stPopover"] button');
  await settle(page);
  await shot(page, '03_profile', {
    button: { sel: '[data-testid="stPopover"]' },
    body: { sel: '[data-testid="stPopoverBody"]' },
    radio: { sel: '[data-testid="stPopoverBody"] [data-testid="stRadio"]' },
    note: { sel: '[data-testid="stPopoverBody"] p', text: 'Model aktif' },
  }, { full: false });
  await page.keyboard.press('Escape');
  await settle(page);

  await clickText(page, '[data-testid="stButton"] button', 'Contoh risiko tinggi');
  await page.waitForSelector('.st-key-card_hero', { timeout: 60000 });
  await settle(page, 1500);
  await shot(page, '04_result', {
    back: { sel: '[data-testid="stButton"]', text: 'Ubah jawaban' },
    reset: { sel: '[data-testid="stButton"]', text: 'Penilaian baru' },
    safety: { sel: '[data-testid="stAlert"]' },
    hero: { sel: '.st-key-card_hero' },
    best: { sel: '.spk-hero-main' },
    anx: { sel: '.spk-hero-stat', nth: 0 },
    prio: { sel: '.spk-hero-stat', nth: 1 },
    rank: { sel: '.st-key-card_rank' },
    why: { sel: '.st-key-card_why' },
    details: { sel: '[data-testid="stExpander"]' },
  });

  await clickText(page, '[data-testid="stExpander"] summary', 'Rincian perhitungan');
  await shot(page, '05_details_contrib', {
    details: { sel: '[data-testid="stExpander"]' },
    tabs: { sel: '[data-testid="stExpander"] [role="tablist"]' },
    chart: { sel: '[data-testid="stExpander"] [data-testid="stImage"], [data-testid="stExpander"] img' },
  });
  await clickText(page, '[data-testid="stExpander"] [role="tab"]', 'Nilai fitur model');
  await shot(page, '06_details_inputs', {
    details: { sel: '[data-testid="stExpander"]' },
    tabs: { sel: '[data-testid="stExpander"] [role="tablist"]' },
  });
  await clickText(page, '[data-testid="stExpander"] [role="tab"]', 'Uji sensitivitas');
  await shot(page, '07_details_sens', {
    details: { sel: '[data-testid="stExpander"]' },
    tabs: { sel: '[data-testid="stExpander"] [role="tablist"]' },
    verdict: { sel: '[data-testid="stExpander"] [data-testid="stAlert"]' },
  });

  // ---- Whole class, with the synthetic Google Form demo (it carries the answers needed for evaluation)
  await clickText(page, '[data-testid="stButtonGroup"] button', 'Satu kelas');
  await page.waitForSelector('[data-testid="stFileUploader"]', { timeout: 60000 });
  await clickText(page, '.st-key-card_demo label', 'SINTETIS');
  await page.waitForSelector('.st-key-card_eval', { timeout: 60000 });
  await clickText(page, '[data-testid="stExpander"] summary', 'Opsi lanjutan');
  await shot(page, '08_batch', {
    upload: { sel: '[data-testid="stFileUploader"]' },
    demo: { sel: '.st-key-card_demo' },
    detected: { sel: '[data-testid="stAlert"]' },
    metrics: { sel: '[data-testid="stMetric"]', all: true },
    list: [{ sel: '[data-testid="stHeading"]', text: 'Daftar prioritas' }, { sel: '[data-testid="stSelectbox"]' }],
    table: { sel: '[data-testid="stDataFrame"]' },
    download: { sel: '[data-testid="stDownloadButton"]' },
    charts: { sel: '.st-key-card_mix, .st-key-card_hist', all: true },
    options: { sel: '[data-testid="stExpander"]', text: 'Opsi lanjutan' },
    eval: [{ sel: '[data-testid="stHeading"]', text: 'Evaluasi model' }, { sel: '.st-key-card_eval' }],
  });

  // ---- Analysis: one screen per tab
  await open(page, 'analysis', '.st-key-card_hists');
  const frame = { title: { sel: '[data-testid="stMainBlockContainer"] h1' }, footer: { sel: '.spk-footer' } };
  const tabs = { ...frame, tabs: { sel: '[data-testid="stMainBlockContainer"] [role="tablist"]' },
    profile: { sel: '[data-testid="stPopover"]' }, population: { sel: 'p, span', text: 'Populasi analisis' } };
  await shot(page, '09_an_data', tabs);
  for (const [i, [label, name]] of [['Model', 'model'], ['SMART', 'smart'], ['Sensitivitas', 'sens'], ['Keadilan', 'fair']].entries()) {
    await clickText(page, '[data-testid="stMainBlockContainer"] [role="tab"]', label);
    await shot(page, `${10 + i}_an_${name}`, tabs);
  }

  // ---- About
  await open(page, 'about', '.st-key-card_arch');
  await shot(page, '14_about', frame);

  // ---- English: the same Home page after switching the language
  await open(page, '', '.spk-preview');
  await clickText(page, '.st-key-lang_switch button', 'EN');
  await page.waitForFunction(() => document.body.innerText.includes('Start an assessment'), { timeout: 30000 });
  await settle(page, 1200);
  await shot(page, '15_en', { lang: { sel: '.st-key-lang_switch' }, nav: { sel: '[data-testid="stTopNavLinkContainer"]', all: true } },
    { full: false });

  await browser.close();
  console.log('screens ->', OUT);
})().catch(err => { console.error(err); process.exit(1); });
