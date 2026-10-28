// Final presentation (<= 15 minutes) -> deliverables/ppt/Presentasi-SPK-SMART-Kecemasan.pptx
const path = require('path');
const fs = require('fs');
const pptxgen = require('pptxgenjs');

const ROOT = path.resolve(__dirname, '..');
const SCREENS = path.join(ROOT, 'user-manual', 'screens');
const FIGS = path.join(ROOT, 'user-manual', 'figures');
const OUT = path.join(ROOT, 'ppt', 'Presentasi-SPK-SMART-Kecemasan.pptx');

const C = { deep: '0F4C5C', teal: '1B7A8C', mint: 'D8EFEC', ice: 'F2F8F7', coral: 'E36414', ink: '1E2A30', mute: '5F6F75', white: 'FFFFFF', line: 'C9DAD7' };
const H = 'Cambria', B = 'Calibri';

const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE';   // 13.33 x 7.5
pres.author = 'Kelompok 1';
pres.title = 'SPK SMART Kecemasan Siswa';

const W = 13.33;
function title(slide, text, sub) {
  slide.addText(text, { x: 0.6, y: 0.35, w: W - 1.2, h: 0.8, fontFace: H, fontSize: 34, bold: true, color: C.deep, margin: 0, isTextBox: true });
  if (sub) slide.addText(sub, { x: 0.6, y: 1.12, w: W - 1.2, h: 0.45, fontFace: B, fontSize: 16, color: C.mute, margin: 0, isTextBox: true });
}
function badge(slide, n, x, y, d = 0.55, fill = C.teal) {
  slide.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill } });
  slide.addText(String(n), { x, y, w: d, h: d, fontFace: B, fontSize: 18, bold: true, color: C.white, align: 'center', valign: 'middle', margin: 0, isTextBox: true });
}
function card(slide, x, y, w, h, fill = C.ice) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.12, fill: { color: fill }, line: { color: C.line, width: 0.75 } });
}
function text(slide, t, o) { slide.addText(t, { fontFace: B, fontSize: 15, color: C.ink, margin: 0, isTextBox: true, valign: 'top', ...o }); }
function bullets(slide, items, o) {
  slide.addText(items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1 } })),
    { fontFace: B, fontSize: 15, color: C.ink, paraSpaceAfter: 6, valign: 'top', isTextBox: true, ...o });
}
function img(slide, file, x, y, w, maxH) {
  const buf = fs.readFileSync(file);
  const pw = buf.readUInt32BE(16), ph = buf.readUInt32BE(20);
  let h = w * ph / pw;
  if (maxH && h > maxH) { h = maxH; w = h * pw / ph; }
  slide.addImage({ path: file, x, y, w, h, altText: path.basename(file) });
  return { w, h };
}
function footer(slide, n) {
  slide.addText(`Kelompok 1 · SPK SMART Kecemasan Siswa`, { x: 0.6, y: 7.05, w: 6, h: 0.3, fontFace: B, fontSize: 10, color: C.mute, margin: 0, isTextBox: true });
  slide.addText(String(n), { x: W - 1.1, y: 7.05, w: 0.5, h: 0.3, fontFace: B, fontSize: 10, color: C.mute, align: 'right', margin: 0, isTextBox: true });
}

// 1 ── Title ───────────────────────────────────────────────
let s = pres.addSlide(); s.background = { color: C.deep };
s.addShape(pres.shapes.OVAL, { x: 9.6, y: -1.2, w: 5.2, h: 5.2, fill: { color: C.teal, transparency: 55 }, line: { color: C.teal, transparency: 100 } });
s.addShape(pres.shapes.OVAL, { x: 10.9, y: 3.9, w: 3.2, h: 3.2, fill: { color: C.mint, transparency: 80 }, line: { color: C.mint, transparency: 100 } });
text(s, 'PROYEK AKHIR · DATA MINING & SISTEM PENDUKUNG KEPUTUSAN', { x: 0.8, y: 1.3, w: 9, h: 0.4, fontSize: 14, color: C.mint, bold: true, charSpacing: 2 });
s.addText('SPK SMART Kecemasan Siswa', { x: 0.8, y: 1.9, w: 9.5, h: 1.2, fontFace: H, fontSize: 48, bold: true, color: C.white, margin: 0, isTextBox: true });
text(s, 'Prediksi tingkat kecemasan dengan Random Forest dan rekomendasi penanganan dengan metode SMART', { x: 0.8, y: 3.15, w: 8.8, h: 0.9, fontSize: 20, color: C.mint });
text(s, 'Kelompok 1 — Steven Feryanta · Steven Iwan · Triemas Putra · Davidson Rafael', { x: 0.8, y: 5.4, w: 10, h: 0.4, fontSize: 15, color: C.white });
text(s, 'Universitas Kristen Krida Wacana · 2026', { x: 0.8, y: 5.85, w: 10, h: 0.4, fontSize: 13, color: C.mint });
s.addNotes('Pembukaan (±30 detik). Perkenalkan tim dan judul: aplikasi yang menggabungkan Data Mining (Random Forest) untuk memprediksi tingkat kecemasan siswa dengan SPK SMART untuk menentukan prioritas dan bentuk penanganan.');

// 2 ── Problem ─────────────────────────────────────────────
s = pres.addSlide(); s.background = { color: C.white };
title(s, 'Masalah: kecemasan siswa sering terlambat ditangani', 'Penjaringan masih bergantung pada observasi guru BK');
const probs = [
  ['Kapasitas terbatas', 'Jumlah guru BK jauh lebih sedikit dari jumlah siswa, sehingga penjaringan menyeluruh sulit dilakukan rutin.'],
  ['Reaktif', 'Penanganan baru dimulai setelah gejala jelas atau prestasi sudah turun.'],
  ['Subjektif', 'Bentuk penanganan dipilih berdasarkan pengalaman pribadi, tanpa dasar multikriteria yang dapat ditelusuri.'],
];
probs.forEach(([h, d], i) => {
  const x = 0.6 + i * 4.1;
  card(s, x, 2.0, 3.8, 3.6);
  badge(s, i + 1, x + 0.35, 2.35, 0.7, C.coral);
  text(s, h, { x: x + 0.35, y: 3.25, w: 3.2, h: 0.5, fontFace: H, fontSize: 22, bold: true, color: C.deep });
  text(s, d, { x: x + 0.35, y: 3.85, w: 3.1, h: 1.6, fontSize: 15, color: C.ink });
});
text(s, 'Padahal data kebiasaan belajar, tidur, aktivitas fisik, tekanan keluarga, dan kelelahan dapat dikumpulkan lewat kuesioner singkat.',
  { x: 0.6, y: 6.0, w: 12, h: 0.6, fontSize: 16, italic: true, color: C.teal });
footer(s, 2);
s.addNotes('Latar belakang (±1 menit). Tiga keterbatasan cara lama: kapasitas, reaktif, subjektif. Peluangnya: data kebiasaan siswa bisa dikumpulkan dengan kuesioner, lalu diolah.');

// 3 ── Solution ────────────────────────────────────────────
s = pres.addSlide(); s.background = { color: C.white };
title(s, 'Solusi: Data Mining + SPK dalam satu aplikasi web', 'Dari jawaban kuesioner menjadi prioritas dan rekomendasi yang dapat dijelaskan');
const flow = [['Kuesioner', '11 faktor gaya hidup & akademik'], ['Random Forest', 'prediksi skor kecemasan 0–10'], ['SMART', 'skor prioritas + 5 alternatif'], ['Rekomendasi', 'tiga teratas + alasan']];
flow.forEach(([h, d], i) => {
  const x = 0.6 + i * 3.15;
  card(s, x, 2.1, 2.7, 2.0, i === 1 || i === 2 ? C.mint : C.ice);
  text(s, h, { x: x + 0.2, y: 2.35, w: 2.3, h: 0.5, fontFace: H, fontSize: 21, bold: true, color: C.deep, align: 'center' });
  text(s, d, { x: x + 0.2, y: 3.0, w: 2.3, h: 0.9, fontSize: 14, align: 'center', color: C.ink });
  if (i < 3) s.addShape(pres.shapes.RIGHT_ARROW, { x: x + 2.75, y: 2.85, w: 0.35, h: 0.45, fill: { color: C.teal }, line: { color: C.teal } });
});
const alts = [['Tidur', 'sleep hygiene & jadwal malam'], ['Olahraga', 'aktivitas fisik terjadwal'], ['Strategi belajar', 'manajemen waktu'], ['Konseling', 'dengan guru BK / rujukan'], ['Relaksasi', 'pernapasan, mindfulness']];
text(s, 'Lima alternatif penanganan', { x: 0.6, y: 4.55, w: 6, h: 0.45, fontFace: H, fontSize: 20, bold: true, color: C.deep });
alts.forEach(([h, d], i) => {
  const x = 0.6 + i * 2.5;
  card(s, x, 5.1, 2.3, 1.45);
  text(s, h, { x: x + 0.15, y: 5.25, w: 2.0, h: 0.45, fontSize: 17, bold: true, color: C.teal });
  text(s, d, { x: x + 0.15, y: 5.75, w: 2.0, h: 0.7, fontSize: 13, color: C.mute });
});
footer(s, 3);
s.addNotes('Solusi (±1 menit). Alur empat langkah. Data Mining bekerja di tahap diagnosis (seberapa tinggi indikasi kecemasan), SMART di tahap preskripsi (siapa lebih dulu, penanganan apa). Pengguna utama: guru BK.');

// 4 ── Data ────────────────────────────────────────────────
s = pres.addSlide(); s.background = { color: C.white };
title(s, 'Data: pralatih publik, disesuaikan dengan data riil', 'Dua sumber dengan peran berbeda (CRISP-DM: Data Understanding)');
card(s, 0.6, 1.9, 5.9, 4.6);
text(s, 'Kaggle — Student Mental Health & Burnout', { x: 0.9, y: 2.1, w: 5.4, h: 0.5, fontFace: H, fontSize: 19, bold: true, color: C.deep });
s.addText('20.000', { x: 0.9, y: 2.7, w: 3, h: 0.9, fontFace: H, fontSize: 48, bold: true, color: C.teal, margin: 0, isTextBox: true });
text(s, 'baris (sampel 2% dari 1 juta), 20 kolom, tanpa nilai hilang', { x: 0.9, y: 3.6, w: 5.3, h: 0.5, fontSize: 14, color: C.mute });
bullets(s, ['11 fitur + target anxiety_score', 'Variabel hasil (mental_health_index, depression, dropout, risk_level) dibuang untuk mencegah label leakage', 'Peran: pralatih model & populasi referensi SPK'], { x: 0.9, y: 4.2, w: 5.4, h: 2.2, fontSize: 14 });
card(s, 6.85, 1.9, 5.9, 4.6, C.mint);
text(s, 'Kuesioner Google Form — siswa SMA', { x: 7.15, y: 2.1, w: 5.4, h: 0.5, fontFace: H, fontSize: 19, bold: true, color: C.deep });
s.addText('±50', { x: 7.15, y: 2.7, w: 3, h: 0.9, fontFace: H, fontSize: 48, bold: true, color: C.teal, margin: 0, isTextBox: true });
text(s, 'pertanyaan: akademik, tidur, media sosial, keluarga, aktivitas fisik, kelelahan, pertemanan, psikologis, pola makan', { x: 7.15, y: 3.6, w: 5.3, h: 0.7, fontSize: 14, color: C.mute });
bullets(s, ['Data riil yang dikumpulkan tim · bersifat rahasia', '5 butir Psikologis membentuk target; tidak pernah menjadi fitur', 'Data pribadi (nama sekolah, tanggal lahir, dll.) dibuang otomatis', 'Jumlah respons: ⟦ISI⟧'], { x: 7.15, y: 4.35, w: 5.4, h: 2.1, fontSize: 14 });
footer(s, 4);
s.addNotes('Data (±1 menit). Kaggle besar dan lengkap untuk pralatih, tetapi populasinya mahasiswa. Kuesioner sesuai populasi SMA tetapi lebih kecil. Karena itu model dipralatih di Kaggle lalu dilatih ulang dengan data kuesioner. Sebutkan jumlah respons riil.');

// 5 ── CRISP-DM + preparation ───────────────────────────────
s = pres.addSlide(); s.background = { color: C.white };
title(s, 'Persiapan data: jawaban kuesioner → 11 fitur model', 'Rumus yang sama dipakai saat pelatihan dan di aplikasi');
const rows = [
  ['Jawaban kuesioner', 'Fitur model'],
  ['"1 jam 30 menit"', 'jam belajar / jam tidur = 1,5'],
  ['Tertekan ujian (Likert 1–5)', 'exam_pressure 1–10'],
  ['Tugas bersamaan, waktu kurang, tugas terlambat, belajar larut', 'stress_level 0–10'],
  ['Uang saku cukup (dibalik)', 'financial_stress 0–10'],
  ['Takut kecewakan ortu, tuntutan nilai', 'family_expectation 0–10'],
  ['Sulit bagi waktu, kelelahan, hilang minat', 'burnout_score 0–10'],
  ['5 butir Psikologis (konsentrasi dibalik)', 'TARGET anxiety_score 0–10'],
];
s.addTable(rows.map((r, i) => r.map(c => ({ text: c, options: { bold: i === 0, color: i === 0 ? C.white : C.ink, fill: { color: i === 0 ? C.deep : (i % 2 ? C.ice : C.white) } } }))),
  { x: 0.6, y: 1.85, w: 7.6, colW: [4.3, 3.3], fontFace: B, fontSize: 13, border: { type: 'solid', pt: 0.5, color: C.line }, rowH: 0.52 });
const steps = ['Sampling 20.000 → 10.000 → 80/20 latih-uji', 'Pencocokan kolom otomatis (judul ganda pun dikenali)', 'Buang duplikat & data pribadi, validasi rentang', 'Imputasi median; CV 5-fold × 2 untuk data riil'];
steps.forEach((t, i) => { badge(s, i + 1, 8.7, 1.95 + i * 1.2, 0.55); text(s, t, { x: 9.45, y: 1.97 + i * 1.2, w: 3.3, h: 0.9, fontSize: 15 }); });
footer(s, 5);
s.addNotes('Data Preparation (±1 menit). Tekankan anti-leakage: butir Psikologis hanya membentuk target. Pipeline kuesioner otomatis: cukup taruh ekspor Google Form lalu jalankan skrip.');

// 6 ── Modeling ────────────────────────────────────────────
s = pres.addSlide(); s.background = { color: C.white };
title(s, 'Modeling: Random Forest Regressor', 'Target kontinu → regresi · 200 pohon, kedalaman 10, max_features √n');
const imp = [['Tingkat stres', 0.4268], ['Burnout', 0.3036], ['Tekanan finansial', 0.0630], ['Tekanan ujian', 0.0493], ['Ekspektasi keluarga', 0.0386], ['Jam belajar', 0.0327], ['Jam tidur', 0.0273], ['Aktivitas fisik', 0.0228], ['Nilai rapor', 0.0211], ['Usia', 0.0113], ['Gender', 0.0035]].reverse();
s.addChart(pres.charts.BAR, [{ name: 'Importance', labels: imp.map(x => x[0]), values: imp.map(x => x[1]) }], {
  x: 0.5, y: 1.75, w: 7.2, h: 5.1, barDir: 'bar', chartColors: [C.teal], showValue: true, dataLabelFormatCode: '0.000', dataLabelFontSize: 10,
  showTitle: true, title: 'Kepentingan fitur (Gini)', titleFontSize: 14, titleColor: C.deep, showLegend: false,
  catAxisLabelFontSize: 12, valAxisHidden: true, valGridLine: { style: 'none' }, catGridLine: { style: 'none' }, catAxisLabelColor: C.ink });
card(s, 8.1, 1.9, 4.65, 4.85);
text(s, 'Mengapa Random Forest?', { x: 8.4, y: 2.1, w: 4.1, h: 0.5, fontFace: H, fontSize: 19, bold: true, color: C.deep });
bullets(s, ['Menangkap hubungan non-linear antarfaktor', 'Tahan outlier, tanpa normalisasi fitur', 'Feature importance untuk penjelasan', 'Mendukung warm start: pralatih Kaggle + pohon baru dari data riil', 'Stres & burnout = 73% kepentingan; gender hanya 0,35%'], { x: 8.4, y: 2.7, w: 4.1, h: 3.9, fontSize: 15 });
footer(s, 6);
s.addNotes('Modeling (±1,5 menit). Jelaskan parameter dan alasannya. Faktor dominan sejalan dengan korelasi. Gender hampir tidak berpengaruh, jadi risiko bias kecil.');

// 7 ── Evaluation ──────────────────────────────────────────
s = pres.addSlide(); s.background = { color: C.white };
title(s, 'Evaluasi model', 'Data uji 2.000 baris · validasi silang 5-fold');
const stats = [['0,767', 'MAE — rata-rata meleset ±0,77 poin (skala 0–10)'], ['0,614', 'R² — 61% variasi skor dijelaskan'], ['1,237', 'MAE baseline rata-rata (pembanding)']];
stats.forEach(([v, l], i) => {
  s.addText(v, { x: 0.6, y: 1.9 + i * 1.6, w: 3.2, h: 0.9, fontFace: H, fontSize: 48, bold: true, color: i === 2 ? C.mute : C.teal, margin: 0, isTextBox: true });
  text(s, l, { x: 0.6, y: 2.8 + i * 1.6, w: 3.8, h: 0.6, fontSize: 14, color: C.mute });
});
const algo = [['Baseline rata-rata', 1.2238], ['Decision Tree', 0.8814], ['Random Forest', 0.7790], ['Gradient Boosting', 0.7728], ['Regresi linear', 0.7684]];
s.addChart(pres.charts.BAR, [{ name: 'MAE CV', labels: algo.map(a => a[0]), values: algo.map(a => a[1]) }], {
  x: 4.6, y: 1.75, w: 8.1, h: 3.8, barDir: 'bar', chartColors: [C.teal], showValue: true, dataLabelFormatCode: '0.000', dataLabelFontSize: 11,
  showTitle: true, title: 'MAE validasi silang (lebih rendah lebih baik)', titleFontSize: 14, titleColor: C.deep, showLegend: false,
  valAxisHidden: true, valGridLine: { style: 'none' }, catGridLine: { style: 'none' }, catAxisLabelFontSize: 12 });
card(s, 4.6, 5.7, 8.1, 1.15, C.mint);
text(s, 'RF setara regresi linear & gradient boosting (selisih ≤ 0,012) dan jauh lebih baik dari pohon tunggal & baseline. Pada data kuesioner riil: MAE ⟦ISI⟧ (strategi terpilih ⟦ISI⟧).', { x: 4.85, y: 5.82, w: 7.7, h: 0.95, fontSize: 14 });
footer(s, 7);
s.addNotes('Evaluasi (±1,5 menit). Jujur: regresi linear sedikit lebih akurat di Kaggle, karena data Kaggle cenderung linear. RF dipilih untuk data kuesioner yang ordinal dan untuk warm start. Sebutkan hasil tujuh strategi pelatihan ulang pada data riil.');

// 8 ── SMART ───────────────────────────────────────────────
s = pres.addSlide(); s.background = { color: C.white };
title(s, 'SPK: metode SMART', '8 kriteria · utilitas min–maks · bobot khusus per alternatif');
card(s, 0.6, 1.85, 5.6, 4.95);
text(s, 'Langkah', { x: 0.9, y: 2.0, w: 5, h: 0.45, fontFace: H, fontSize: 19, bold: true, color: C.deep });
const smartSteps = ['Kriteria: prediksi kecemasan RF + 7 faktor', 'Utilitas benefit (x−min)/(max−min); cost (max−x)/(max−min)', 'Skor prioritas = rata-rata utilitas → urutan siswa', 'Skor alternatif = Σ bobot × utilitas', 'Rekomendasi = skor tertinggi; tampil 3 teratas', 'Pengaman: 10% prediksi tertinggi → konseling + rujukan'];
smartSteps.forEach((t, i) => { badge(s, i + 1, 0.9, 2.55 + i * 0.7, 0.45); text(s, t, { x: 1.5, y: 2.58 + i * 0.7, w: 4.55, h: 0.6, fontSize: 14 }); });
const ex = [['Strategi belajar', 0.488], ['Konseling', 0.564], ['Olahraga', 0.588], ['Relaksasi', 0.623], ['Tidur', 0.706]];
s.addChart(pres.charts.BAR, [{ name: 'Skor', labels: ex.map(e => e[0]), values: ex.map(e => e[1]) }], {
  x: 6.5, y: 1.75, w: 6.2, h: 3.5, barDir: 'bar', chartColors: [C.teal], showValue: true, dataLabelFormatCode: '0.000', dataLabelFontSize: 11,
  showTitle: true, title: 'Contoh siswa STU00004 (profil A)', titleFontSize: 14, titleColor: C.deep, showLegend: false,
  valAxisHidden: true, valGridLine: { style: 'none' }, catGridLine: { style: 'none' }, catAxisLabelFontSize: 12 });
card(s, 6.5, 5.4, 6.2, 1.4, C.mint);
text(s, 'Tidur 0,706: jam tidur 3,1 jam → utilitas 0,979 × bobot 0,40 = 0,392 (penyumbang terbesar). Skor prioritas 0,580 — lebih tinggi dari 93% siswa.', { x: 6.75, y: 5.52, w: 5.8, h: 1.2, fontSize: 14 });
footer(s, 8);
s.addNotes('SMART (±1,5 menit). Tunjukkan rumus utilitas dan contoh nyata. Benefit di sini berarti makin tinggi makin butuh perhatian. Temuan: bobot Olahraga di notebook berjumlah 1,05; aplikasi menormalkannya menjadi 1.');

// 9 ── Sensitivity & fairness ──────────────────────────────
s = pres.addSlide(); s.background = { color: C.white };
title(s, 'Uji sensitivitas & keadilan', 'Apakah rekomendasi stabil dan adil?');
const sens = [['94,6%', 'rekomendasi tetap saat semua bobot diacak ±10% (100×)'], ['89,4%', 'tetap pada ±20%'], ['≤ 3%', 'berubah bila satu bobot digeser ±10%']];
sens.forEach(([v, l], i) => {
  card(s, 0.6 + i * 2.75, 1.85, 2.55, 2.1, i === 0 ? C.mint : C.ice);
  s.addText(v, { x: 0.75 + i * 2.75, y: 2.0, w: 2.3, h: 0.8, fontFace: H, fontSize: 36, bold: true, color: C.teal, align: 'center', margin: 0, isTextBox: true });
  text(s, l, { x: 0.8 + i * 2.75, y: 2.85, w: 2.2, h: 1.0, fontSize: 13, align: 'center', color: C.mute });
});
s.addChart(pres.charts.BAR, [
  { name: 'Profil A', labels: ['Tidur', 'Olahraga', 'Str. belajar', 'Konseling', 'Relaksasi'], values: [5356, 6905, 2613, 2202, 2924] },
  { name: 'Profil B', labels: ['Tidur', 'Olahraga', 'Str. belajar', 'Konseling', 'Relaksasi'], values: [5662, 4673, 1940, 7553, 172] },
], { x: 0.5, y: 4.1, w: 8.2, h: 2.85, barDir: 'col', barGrouping: 'clustered', chartColors: [C.teal, C.coral], showLegend: true, legendPos: 'r',
  showTitle: true, title: 'Rekomendasi pada 20.000 siswa per profil bobot', titleFontSize: 13, titleColor: C.deep,
  valGridLine: { color: 'E5E5E5', size: 0.5 }, catGridLine: { style: 'none' }, catAxisLabelFontSize: 11, valAxisLabelFontSize: 10 });
card(s, 9.0, 1.85, 3.75, 5.0);
text(s, 'Keadilan gender', { x: 9.3, y: 2.0, w: 3.2, h: 0.5, fontFace: H, fontSize: 19, bold: true, color: C.deep });
[['Female', '0,768'], ['Male', '0,767'], ['Other', '0,751']].forEach(([g, m], i) => {
  text(s, g, { x: 9.3, y: 2.7 + i * 0.75, w: 1.6, h: 0.5, fontSize: 16 });
  text(s, `MAE ${m}`, { x: 10.9, y: 2.7 + i * 0.75, w: 1.7, h: 0.5, fontSize: 16, bold: true, color: C.teal });
});
text(s, 'Selisih < 0,02 poin; sebaran rekomendasi per gender hampir sama. Profil A dipilih sebagai bawaan karena paling stabil.', { x: 9.3, y: 5.0, w: 3.25, h: 1.7, fontSize: 13, color: C.mute });
footer(s, 9);
s.addNotes('Sensitivitas & keadilan (±1 menit). Profil A paling stabil (94,6% tetap). Profil B lebih sering memilih Konseling. Tidak ada bias gender yang berarti.');

// 10 ── App demo ───────────────────────────────────────────
s = pres.addSlide(); s.background = { color: C.white };
title(s, 'Aplikasi: hasil yang dapat dijelaskan', 'Streamlit · bilingual ID/EN · 4 halaman');
const top = img(s, path.join(FIGS, 'ppt_result_top.png'), 0.6, 1.75, 6.4);
img(s, path.join(FIGS, 'ppt_contrib.png'), 0.6, 1.95 + top.h, 6.4, 6.9 - (1.95 + top.h));
const feats = [['Satu siswa', 'Kuesioner seperti Google Form atau 11 nilai fitur; contoh profil siap pakai'], ['Alasan', 'Tiga teratas, grafik kontribusi bobot × utilitas, kalimat alasan'], ['Sensitivitas', 'Tabel ±10/±20% per siswa'], ['Banyak siswa', 'Unggah ekspor Google Form → peringkat prioritas, unduh CSV, evaluasi data baru'], ['Analisis', 'Data, model, SMART, sensitivitas, keadilan']];
feats.forEach(([h, d], i) => {
  badge(s, i + 1, 7.3, 1.8 + i * 1.03, 0.5);
  text(s, h, { x: 7.95, y: 1.78 + i * 1.03, w: 4.8, h: 0.4, fontSize: 16, bold: true, color: C.deep });
  text(s, d, { x: 7.95, y: 2.15 + i * 1.03, w: 4.8, h: 0.6, fontSize: 13, color: C.mute });
});
footer(s, 10);
s.addNotes('Demo (±3 menit, langsung di aplikasi). 1) Beranda. 2) Rekomendasi → Risiko tinggi: tunjukkan kotak pengaman, tiga teratas, alasan, grafik kontribusi, tabel sensitivitas. 3) Ganti profil bobot. 4) Banyak siswa → unggah ekspor Google Form. 5) Analisis singkat. 6) Ganti bahasa.');

// 11 ── Architecture & retraining ──────────────────────────
s = pres.addSlide(); s.background = { color: C.white };
title(s, 'Arsitektur & pelatihan ulang dengan data riil', 'Pelatihan offline, aplikasi hanya melakukan inferensi');
const boxes = [
  [0.6, 2.0, 'Kaggle 20k', C.ice], [0.6, 3.5, 'Google Form (rahasia)', C.mint],
  [3.6, 2.75, 'scripts/train.py\nkaggle · real · compare', C.ice], [6.6, 2.75, 'models/\nRF .joblib + metadata', C.mint],
  [9.6, 2.0, 'Streamlit Cloud\nBeranda · Rekomendasi', C.ice], [9.6, 3.5, 'Analisis · Tentang\n(ID/EN)', C.ice],
];
boxes.forEach(([x, y, t, f]) => { card(s, x, y, 2.6, 1.1, f); text(s, t, { x: x + 0.1, y: y + 0.15, w: 2.4, h: 0.85, fontSize: 14, bold: true, align: 'center', valign: 'middle', color: C.deep }); });
[[3.25, 2.45], [3.25, 3.75], [6.25, 3.2], [9.25, 3.2]].forEach(([x, y]) => s.addShape(pres.shapes.RIGHT_ARROW, { x, y, w: 0.3, h: 0.3, fill: { color: C.teal }, line: { color: C.teal } }));
card(s, 0.6, 5.0, 12.15, 1.8);
text(s, 'Tujuh strategi pelatihan ulang dibandingkan otomatis (CV 5-fold × 2): model Kaggle apa adanya · data riil saja · gabungan berbobot 1/10/50 · warm start +200/+600 pohon. MAE terendah dipakai; data mentah tidak pernah di-commit, aplikasi hanya memuat agregat.', { x: 0.9, y: 5.15, w: 11.6, h: 1.0, fontSize: 15 });
text(s, 'Strategi terpilih: ⟦ISI⟧ · 39 uji otomatis (pytest) memastikan hasil identik dengan notebook', { x: 0.9, y: 6.2, w: 11.6, h: 0.45, fontSize: 14, color: C.teal, bold: true });
footer(s, 11);
s.addNotes('Arsitektur (±1 menit). Pemisahan pelatihan dan inferensi. Pipeline data riil: drop file ekspor, jalankan inspect_gform lalu train --stage real. Uji otomatis menjaga hasil tetap sama dengan notebook.');

// 12 ── Ethics ─────────────────────────────────────────────
s = pres.addSlide(); s.background = { color: C.white };
title(s, 'Etika, keadilan, dan privasi', 'Bidang sensitif: kesehatan mental siswa');
const eth = [['Bukan diagnosis', 'Penafian di setiap halaman; hasil adalah indikasi untuk guru BK'], ['Aturan pengaman', '10% prediksi tertinggi selalu mendapat konseling + rujukan'], ['Privasi', 'Tidak ada penyimpanan; kolom pribadi dibuang; unduhan beridentitas anonim; repositori privat'], ['Keadilan', 'MAE & sebaran rekomendasi dibandingkan per gender; kelompok < 5 orang disembunyikan']];
eth.forEach(([h, d], i) => {
  const x = 0.6 + (i % 2) * 6.15, y = 1.9 + Math.floor(i / 2) * 2.45;
  card(s, x, y, 5.95, 2.2, i === 1 ? C.mint : C.ice);
  badge(s, i + 1, x + 0.3, y + 0.3, 0.6, i === 1 ? C.coral : C.teal);
  text(s, h, { x: x + 1.15, y: y + 0.32, w: 4.5, h: 0.5, fontFace: H, fontSize: 20, bold: true, color: C.deep });
  text(s, d, { x: x + 1.15, y: y + 0.9, w: 4.55, h: 1.2, fontSize: 15 });
});
footer(s, 12);
s.addNotes('Etika (±45 detik). Tekankan bahwa sistem membantu, bukan menggantikan guru BK atau psikolog. Privasi dirancang sejak awal: data mentah tidak pernah masuk repositori.');

// 13 ── Conclusion ─────────────────────────────────────────
s = pres.addSlide(); s.background = { color: C.deep };
s.addText('Kesimpulan', { x: 0.8, y: 0.6, w: 11, h: 0.9, fontFace: H, fontSize: 40, bold: true, color: C.white, margin: 0, isTextBox: true });
const concl = ['Random Forest memprediksi kecemasan dengan MAE 0,77 dan R² 0,61; faktor dominan: stres & burnout', 'SMART mengubah prediksi menjadi prioritas dan rekomendasi yang stabil (94,6%) dan dapat dijelaskan', 'Aplikasi siap pakai, bilingual, dan siap dilatih ulang dengan data kuesioner riil'];
concl.forEach((t, i) => { badge(s, i + 1, 0.8, 1.8 + i * 1.05, 0.6, C.teal); text(s, t, { x: 1.65, y: 1.85 + i * 1.05, w: 10.8, h: 0.8, fontSize: 18, color: C.white }); });
text(s, 'Pengembangan lanjutan', { x: 0.8, y: 5.1, w: 6, h: 0.5, fontFace: H, fontSize: 20, bold: true, color: C.mint });
text(s, 'Validasi bobot oleh guru BK/psikolog · segmentasi siswa (clustering) · aturan asosiasi kebiasaan · pengumpulan data berkala', { x: 0.8, y: 5.6, w: 11.5, h: 0.8, fontSize: 16, color: C.mint });
text(s, 'Terima kasih · ⟦ISI: URL aplikasi⟧', { x: 0.8, y: 6.6, w: 11, h: 0.5, fontSize: 16, bold: true, color: C.white });
s.addNotes('Penutup (±45 detik). Ringkas tiga poin utama, sebutkan pengembangan lanjutan, tampilkan URL aplikasi, buka sesi tanya jawab.');

fs.mkdirSync(path.dirname(OUT), { recursive: true });
pres.writeFile({ fileName: OUT }).then(f => console.log('->', f));
