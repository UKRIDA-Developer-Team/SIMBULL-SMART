// User Manual (Panduan Pengguna) .docx from deliverables/user-manual/user-manual.md + figures/.
const fs = require('fs');
const path = require('path');
const { buildWithToc, coverPage } = require('./md2docx');

const DIR = path.resolve(__dirname, '..', 'user-manual');
const MEMBERS = [['Steven Feryanta', '412025028'], ['Steven Iwan', '412024008'], ['Triemas Putra', '412024018'], ['Davidson Rafael', '412024030']];
const md = fs.readFileSync(path.join(DIR, 'user-manual.md'), 'utf8');
const cover = coverPage({
  kicker: 'DOKUMEN USER MANUAL (PANDUAN PENGGUNAAN)',
  title: 'SPK SMART Kecemasan Siswa',
  subtitle: 'Panduan langkah demi langkah memakai aplikasi rekomendasi penanganan kecemasan siswa',
  members: MEMBERS,
  footer: ['Universitas Kristen Krida Wacana', '2026'],
});
buildWithToc({ markdown: md, baseDir: DIR, out: path.join(DIR, 'User-Manual-SPK-SMART-Kecemasan.docx'),
  title: 'User Manual — SPK SMART Kecemasan Siswa', cover }).then(f => console.log('->', f));
