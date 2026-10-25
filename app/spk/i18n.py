"""UI strings in Bahasa Indonesia (id) and English (en). Long page text lives in content/{id,en}/."""
from __future__ import annotations

LANGS = {"id": "Bahasa Indonesia", "en": "English"}
DEFAULT = "id"

S: dict[str, dict[str, str]] = {
    # ---- shell ----
    "app_title": {"id": "SPK SMART Kecemasan Siswa", "en": "Student Anxiety SMART DSS"},
    "nav_home": {"id": "Beranda", "en": "Home"},
    "nav_reco": {"id": "Rekomendasi", "en": "Recommendation"},
    "nav_analysis": {"id": "Analisis", "en": "Analysis"},
    "nav_about": {"id": "Tentang", "en": "About"},
    "lang": {"id": "Bahasa", "en": "Language"},
    "profile": {"id": "Profil bobot SMART", "en": "SMART weight profile"},
    "profile_button": {"id": "Profil bobot {p}", "en": "Weight profile {p}"},
    "profile_intro": {
        "id": "Profil bobot menentukan seberapa besar pengaruh tiap kriteria pada pilihan dukungan. Hasil langsung diperbarui.",
        "en": "The weight profile sets how much each criterion counts toward each kind of support. Results update at once."},
    "profile_help": {
        "id": "A menekankan kriteria yang paling relevan untuk tiap alternatif. B hampir seimbang. C sama rata (kontrol).",
        "en": "A stresses the criteria most relevant to each alternative. B is nearly balanced. C is equal (control)."},
    "profile_A": {"id": "A - Berbasis domain", "en": "A - Domain-weighted"},
    "profile_B": {"id": "B - Hampir seimbang", "en": "B - Nearly balanced"},
    "profile_C": {"id": "C - Sama rata (kontrol)", "en": "C - Equal (control)"},
    "profile_A_desc": {"id": "Disarankan. Tiap dukungan menekankan kriteria yang paling relevan.",
                       "en": "Recommended. Each kind of support stresses its most relevant criteria."},
    "profile_B_desc": {"id": "Bobot hampir sama untuk semua kriteria.", "en": "Nearly the same weight for every criterion."},
    "profile_C_desc": {"id": "Semua bobot sama. Hanya untuk pembanding.", "en": "All weights equal. For comparison only."},
    "profile_c_warning": {
        "id": "Profil C memberi bobot sama untuk semua alternatif, sehingga semua skor seri dan hasilnya selalu 'Tidur'. Gunakan hanya sebagai pembanding.",
        "en": "Profile C gives every alternative the same weights, so all scores tie and the result is always 'Sleep'. Use it only as a baseline."},
    "disclaimer": {
        "id": "Alat bantu skrining dan pendukung keputusan, **bukan alat diagnosis klinis**. Keputusan akhir tetap pada guru BK atau tenaga profesional.",
        "en": "A screening and decision-support aid, **not a clinical diagnosis tool**. The final decision stays with the school counselor or a professional."},
    "disclaimer_plain": {
        "id": "Alat bantu skrining dan pendukung keputusan, bukan alat diagnosis klinis. Keputusan akhir tetap pada guru BK atau tenaga profesional.",
        "en": "A screening and decision-support aid, not a clinical diagnosis tool. The final decision stays with the school counselor or a professional."},
    "privacy_note": {
        "id": "Data yang Anda isi atau unggah hanya diproses selama sesi ini dan tidak disimpan.",
        "en": "Data you enter or upload is processed for this session only and is not stored."},
    "footer_team": {"id": "Kelompok 1 · Data Mining & Sistem Pendukung Keputusan",
                    "en": "Group 1 · Data Mining & Decision Support Systems"},
    "model_badge": {"id": "Model aktif: {source} · {n} baris data{strategy}",
                    "en": "Active model: {source} · {n} data rows{strategy}"},
    "src_kaggle": {"id": "Kaggle (pralatih)", "en": "Kaggle (pretrained)"},
    "src_real": {"id": "Kaggle → data kuesioner riil", "en": "Kaggle → real questionnaire data"},
    "src_gform": {"id": "Data kuesioner riil", "en": "Real questionnaire data"},
    "missing_artifacts": {"id": "Model atau dataset tidak ditemukan. Jalankan `python scripts/train.py` terlebih dahulu.",
                          "en": "Model or dataset missing. Run `python scripts/train.py` first."},

    # ---- home page ----
    "home_eyebrow": {"id": "Skrining dini kecemasan siswa", "en": "Early screening for student anxiety"},
    "home_title": {"id": "Kenali lebih awal siswa yang butuh dukungan.", "en": "Spot students who need support, early."},
    "home_lead": {
        "id": "Jawab beberapa pertanyaan tentang keseharian siswa. Sistem memperkirakan tingkat kecemasannya, menentukan prioritas, dan menyarankan bentuk dukungan yang paling sesuai, lengkap dengan alasannya.",
        "en": "Answer a few questions about a student's daily life. The system estimates their anxiety level, sets a priority, and suggests the most suitable kind of support, with the reasons behind it."},
    "home_cta": {"id": "Mulai penilaian", "en": "Start an assessment"},
    "home_cta_batch": {"id": "Nilai satu kelas sekaligus", "en": "Assess a whole class"},
    "home_facts": {"id": "Dilatih dengan {n} data · {k} kriteria · 5 bentuk dukungan",
                   "en": "Trained on {n} records · {k} criteria · 5 kinds of support"},
    "home_preview": {"id": "Contoh hasil", "en": "Sample result"},
    "home_preview_anx": {"id": "Kecemasan", "en": "Anxiety"},
    "home_preview_prio": {"id": "Prioritas", "en": "Priority"},
    "home_how": {"id": "Cara kerjanya", "en": "How it works"},
    "home_step1_t": {"id": "Isi kuesioner", "en": "Answer the questionnaire"},
    "home_step1_d": {"id": "17 pertanyaan singkat tentang belajar, tidur, tekanan, dan kelelahan. Sama dengan Google Form, sekitar 3 menit.",
                     "en": "17 short questions on study, sleep, pressure and fatigue. Same as the Google Form, about 3 minutes."},
    "home_step2_t": {"id": "Sistem menghitung", "en": "The system does the math"},
    "home_step2_d": {"id": "Random Forest memperkirakan skor kecemasan 0-10. Metode SMART lalu menimbang 8 kriteria.",
                     "en": "A Random Forest estimates an anxiety score from 0 to 10. SMART then weighs 8 criteria."},
    "home_step3_t": {"id": "Baca rekomendasinya", "en": "Read the recommendation"},
    "home_step3_d": {"id": "Lima bentuk dukungan diurutkan dari yang paling cocok, beserta alasan dan tingkat prioritasnya.",
                     "en": "Five kinds of support, ranked from best fit, with the reasons and a priority level."},
    "home_alts": {"id": "Lima bentuk dukungan", "en": "Five kinds of support"},
    "home_alts_lead": {"id": "Sistem memilih di antara lima program yang umum dijalankan guru BK.",
                       "en": "The system chooses among five programs that school counselors commonly run."},
    "home_users_t": {"id": "Untuk siapa?", "en": "Who is it for?"},
    "home_users_d": {
        "id": "Guru BK dan wali kelas, untuk skrining dini dan perencanaan program. Siswa juga dapat memakainya untuk refleksi diri dengan pendampingan.",
        "en": "School counselors and homeroom teachers, for early screening and program planning. Students can also use it for guided self-reflection."},
    "home_care_t": {"id": "Perlu diingat", "en": "Keep in mind"},
    "home_care_1": {"id": "Hasil adalah bahan pertimbangan, bukan diagnosis.", "en": "Results support a decision; they are not a diagnosis."},
    "home_care_2": {"id": "Siswa di 10% kecemasan tertinggi selalu diarahkan ke konseling.",
                    "en": "Students in the top 10% for anxiety are always pointed to counseling."},
    "home_care_3": {"id": "Tidak ada data yang disimpan.", "en": "Nothing you enter is stored."},

    # ---- recommendation page ----
    "reco_title": {"id": "Rekomendasi penanganan", "en": "Support recommendation"},
    "reco_intro": {
        "id": "Isi profil satu siswa atau unggah data satu kelas. Sistem memperkirakan tingkat kecemasan, lalu metode SMART mengurutkan lima bentuk dukungan.",
        "en": "Fill in one student's profile or upload a whole class. The system estimates the anxiety level, then SMART ranks five kinds of support."},
    "view_single": {"id": "Satu siswa", "en": "One student"},
    "view_batch": {"id": "Satu kelas (unggah berkas)", "en": "A whole class (upload)"},
    "mode_adv": {"id": "Mode lanjutan: isi 11 nilai fitur model", "en": "Advanced mode: enter the 11 model features"},
    "mode_help": {
        "id": "Mode kuesioner memakai pertanyaan yang sama dengan Google Form, lalu mengubah jawaban menjadi fitur model dengan rumus yang sama seperti saat pelatihan.",
        "en": "Questionnaire mode uses the Google Form questions and converts answers to model features with the same formulas used in training."},
    "examples": {"id": "Ingin mencoba dulu?", "en": "Just exploring?"},
    "example_high": {"id": "Contoh risiko tinggi", "en": "High-risk example"},
    "example_low": {"id": "Contoh risiko rendah", "en": "Low-risk example"},
    "submit": {"id": "Lihat rekomendasi", "en": "See recommendation"},
    "sec_q_identity": {"id": "Tentang siswa", "en": "About the student"},
    "sec_q_identity_hint": {"id": "Tidak disimpan.", "en": "Not stored."},
    "sec_q_study": {"id": "Belajar & nilai", "en": "Study & grades"},
    "sec_q_study_hint": {"id": "Kebiasaan belajar seminggu dan sebulan terakhir.", "en": "Study habits over the last week and month."},
    "sec_q_pressure": {"id": "Tuntutan & tekanan", "en": "Demands & pressure"},
    "sec_q_pressure_hint": {"id": "Seberapa sering siswa merasakannya.", "en": "How often the student feels this."},
    "sec_q_life": {"id": "Tidur, olahraga & uang saku", "en": "Sleep, exercise & pocket money"},
    "sec_q_life_hint": {"id": "Rata-rata dalam seminggu terakhir.", "en": "On average over the last week."},
    "sec_q_burnout": {"id": "Kelelahan", "en": "Fatigue"},
    "sec_q_burnout_hint": {"id": "Seberapa setuju siswa dengan pernyataan berikut.", "en": "How much the student agrees with each statement."},
    "sec_adv_profile": {"id": "Profil siswa", "en": "Student profile"},
    "sec_adv_values": {"id": "Nilai fitur model", "en": "Model feature values"},
    "age_q": {"id": "Usia (tahun)", "en": "Age (years)"},
    "tips_title": {"id": "Sebelum mengisi", "en": "Before you start"},
    "tips_1": {"id": "Jawab sesuai kondisi siswa akhir-akhir ini, bukan kondisi idealnya.",
               "en": "Answer for how things have been lately, not how they should be."},
    "tips_2": {"id": "Tidak ada jawaban benar atau salah.", "en": "There are no right or wrong answers."},
    "tips_3": {"id": "Jawaban hanya diproses di sesi ini dan tidak disimpan.", "en": "Answers are processed in this session only and never stored."},
    "tips_4": {"id": "Hasilnya bahan pertimbangan, bukan diagnosis.", "en": "The result supports a decision; it is not a diagnosis."},
    "back_edit": {"id": "Ubah jawaban", "en": "Edit answers"},
    "new_assessment": {"id": "Penilaian baru", "en": "New assessment"},
    "res_best": {"id": "Rekomendasi utama", "en": "Top recommendation"},
    "res_fit": {"id": "Skor kecocokan {s:.3f} dari 1", "en": "Fit score {s:.3f} out of 1"},
    "res_pred": {"id": "Perkiraan tingkat kecemasan", "en": "Estimated anxiety level"},
    "res_pred_note": {"id": "Lebih tinggi dari {p:.0f}% siswa pembanding.", "en": "Higher than {p:.0f}% of reference students."},
    "res_priority": {"id": "Prioritas penanganan", "en": "Support priority"},
    "res_priority_note": {"id": "Lebih tinggi dari {p:.0f}% siswa pembanding. Menentukan siapa yang dibantu lebih dulu.",
                          "en": "Higher than {p:.0f}% of reference students. Decides who is helped first."},
    "band_low": {"id": "Di bawah rata-rata", "en": "Below average"},
    "band_mid": {"id": "Sekitar rata-rata", "en": "Around average"},
    "band_high": {"id": "Di atas rata-rata", "en": "Above average"},
    "band_top": {"id": "Jauh di atas rata-rata", "en": "Well above average"},
    "prio_low": {"id": "Rendah", "en": "Low"},
    "prio_mid": {"id": "Sedang", "en": "Medium"},
    "prio_high": {"id": "Tinggi", "en": "High"},
    "prio_top": {"id": "Sangat tinggi", "en": "Very high"},
    "res_rank": {"id": "Urutan lima pilihan", "en": "All five options, ranked"},
    "res_rank_help": {"id": "Makin panjang batang, makin cocok untuk siswa ini.", "en": "The longer the bar, the better the fit for this student."},
    "res_why": {"id": "Mengapa {alt}?", "en": "Why {alt}?"},
    "res_details": {"id": "Rincian perhitungan", "en": "Calculation details"},
    "res_contrib": {"id": "Kontribusi tiap kriteria (bobot × utilitas)", "en": "Contribution of each criterion (weight × utility)"},
    "res_contrib_help": {
        "id": "Panjang batang = skor SMART alternatif. Setiap warna = sumbangan satu kriteria. Kriteria dengan utilitas tinggi berarti kondisi siswa pada kriteria itu membutuhkan perhatian.",
        "en": "Bar length = the alternative's SMART score. Each colour = one criterion's share. High utility on a criterion means the student's condition there needs attention."},
    "res_inputs": {"id": "Nilai fitur model & utilitas", "en": "Model feature values & utilities"},
    "res_sens": {"id": "Uji sensitivitas bobot", "en": "Weight sensitivity test"},
    "res_sens_help": {
        "id": "Setiap bobot kriteria diubah ±10% dan ±20% (bobot lain dinormalisasi ulang). Sel berwarna = rekomendasi utama berubah.",
        "en": "Each criterion weight is changed by ±10% and ±20% (others renormalized). Coloured cell = top recommendation changes."},
    "res_sens_stable": {"id": "Stabil: rekomendasi utama tidak berubah pada {k} dari {n} skenario.",
                        "en": "Stable: the top recommendation holds in {k} of {n} scenarios."},
    "res_sens_changes": {"id": "Rekomendasi berubah pada {k} dari {n} skenario, terutama saat bobot {crit} diubah.",
                         "en": "The recommendation changes in {k} of {n} scenarios, mostly when the {crit} weight moves."},
    "safety_title": {"id": "Perlu perhatian segera", "en": "Needs prompt attention"},
    "safety_body": {
        "id": "Prediksi kecemasan siswa ini berada di {pct}% teratas populasi referensi. Apa pun hasil SMART, **konseling** perlu disertakan dan siswa sebaiknya dirujuk ke: {contact}.",
        "en": "This student's predicted anxiety is in the top {pct}% of the reference population. Whatever SMART ranks first, **counseling** should be included and the student should be referred to: {contact}."},
    "narr_best": {"id": "**{alt}** mendapat skor tertinggi ({score:.3f}) dengan profil bobot {profile}.",
                  "en": "**{alt}** has the highest score ({score:.3f}) under weight profile {profile}."},
    "narr_drivers": {"id": "Pendorong utama: {drivers}.", "en": "Main drivers: {drivers}."},
    "narr_gap": {"id": "Selisih dengan alternatif kedua ({alt2}) {gap:.3f}.",
                 "en": "Gap to the second alternative ({alt2}): {gap:.3f}."},
    "narr_gap_small": {"id": "Selisihnya kecil, jadi {alt2} juga layak dipertimbangkan.",
                       "en": "The gap is small, so {alt2} is also worth considering."},
    "narr_priority": {"id": "Skor prioritas {score:.3f} lebih tinggi dari {p:.0f}% siswa referensi.",
                      "en": "Priority score {score:.3f} is higher than {p:.0f}% of reference students."},

    # ---- recommendation page: whole class ----
    "batch_upload": {"id": "Berkas data siswa", "en": "Student data file"},
    "batch_upload_help": {"id": "Ekspor Google Form (.csv/.xlsx) atau CSV berisi 11 kolom fitur model.",
                          "en": "A Google Form export (.csv/.xlsx) or a CSV with the 11 model-feature columns."},
    "batch_demo_title": {"id": "Belum punya berkas?", "en": "No file yet?"},
    "batch_demo_lead": {"id": "Pakai data contoh untuk mencoba. Unggahan Anda selalu dipakai lebih dulu.",
                        "en": "Try it with demo data. An uploaded file always takes precedence."},
    "batch_default": {"id": "Data contoh", "en": "Demo data"},
    "batch_demo_kaggle": {"id": "Sampel Kaggle (20.000 baris)", "en": "Kaggle sample (20,000 rows)"},
    "batch_demo_gform": {"id": "Ekspor Google Form SINTETIS (250 baris, bukan data riil)",
                         "en": "SYNTHETIC Google Form export (250 rows, not real data)"},
    "batch_detected_gform": {"id": "Terdeteksi ekspor Google Form: {n} baris, {k} kolom pribadi dibuang ({cols}).",
                             "en": "Detected a Google Form export: {n} rows, {k} personal columns dropped ({cols})."},
    "batch_detected_csv": {"id": "Terdeteksi CSV fitur model: {n} baris.", "en": "Detected a model-feature CSV: {n} rows."},
    "batch_bad": {"id": "Berkas tidak dapat diproses: {err}", "en": "The file could not be processed: {err}"},
    "batch_missing_cols": {"id": "Kolom fitur model hilang: {cols}. Unggah ekspor Google Form atau CSV dengan 11 kolom: {need}.",
                           "en": "Missing model feature columns: {cols}. Upload a Google Form export or a CSV with the 11 columns: {need}."},
    "batch_imputed": {"id": "{n} nilai kosong diisi dengan median data latih.", "en": "{n} empty values were filled with training medians."},
    "batch_options": {"id": "Opsi lanjutan", "en": "Advanced options"},
    "batch_bounds": {"id": "Normalisasi dengan batas referensi (mati = min/max batch ini, seperti notebook)",
                     "en": "Normalize with reference bounds (off = min/max of this batch, as in the notebook)"},
    "batch_n": {"id": "Jumlah siswa", "en": "Students"},
    "batch_urgent": {"id": "Perlu perhatian segera", "en": "Need prompt attention"},
    "batch_urgent_help": {"id": "Prediksi kecemasan di 10% teratas populasi referensi.",
                          "en": "Predicted anxiety in the top 10% of the reference population."},
    "batch_top_alt": {"id": "Paling sering disarankan", "en": "Most often suggested"},
    "batch_mean_anx": {"id": "Rata-rata prediksi kecemasan", "en": "Mean predicted anxiety"},
    "batch_list": {"id": "Daftar prioritas", "en": "Priority list"},
    "batch_list_help": {"id": "Diurutkan dari skor prioritas tertinggi. Unduhan memuat semua siswa, tanpa data pribadi.",
                        "en": "Sorted by priority score, highest first. The download has every student and no personal data."},
    "batch_topn": {"id": "Tampilkan", "en": "Show"},
    "batch_download": {"id": "Unduh peringkat lengkap (CSV)", "en": "Download full ranking (CSV)"},
    "batch_eval": {"id": "Evaluasi model pada data baru", "en": "Model evaluation on new data"},
    "batch_eval_help": {
        "id": "Berkas memuat jawaban Psikologis (P01-P05), jadi skor kecemasan sebenarnya dapat dihitung dan dibandingkan dengan prediksi.",
        "en": "The file has the Psikologis answers (P01-P05), so the actual anxiety score can be computed and compared with the prediction."},
    "batch_dist": {"id": "Sebaran rekomendasi", "en": "Recommendation mix"},
    "student_id": {"id": "ID siswa", "en": "Student ID"},

    # ---- analysis page ----
    "an_title": {"id": "Analisis data, model & keputusan", "en": "Data, model & decision analysis"},
    "an_lead": {
        "id": "Ringkasan teknis untuk guru BK, dosen, dan penguji: seberapa akurat model, bagaimana SMART memilih, dan seberapa stabil hasilnya.",
        "en": "A technical summary for counselors, lecturers and reviewers: how accurate the model is, how SMART decides, and how stable the results are."},
    "an_tab_data": {"id": "Data", "en": "Data"},
    "an_tab_model": {"id": "Model", "en": "Model"},
    "an_tab_smart": {"id": "SMART", "en": "SMART"},
    "an_tab_sens": {"id": "Sensitivitas", "en": "Sensitivity"},
    "an_tab_fair": {"id": "Keadilan", "en": "Fairness"},
    "an_population": {"id": "Populasi analisis: sampel Kaggle ({n} baris), dinilai dengan model aktif.",
                      "en": "Analysis population: Kaggle sample ({n} rows), scored with the active model."},
    "an_data_intro": {"id": "Data yang melatih model dan menjadi pembanding setiap siswa.",
                      "en": "The data that trains the model and serves as the reference for every student."},
    "an_model_intro": {"id": "Seberapa dekat prediksi Random Forest dengan skor kecemasan sebenarnya.",
                       "en": "How close the Random Forest's predictions are to the actual anxiety scores."},
    "an_smart_intro": {"id": "Bagaimana SMART menimbang delapan kriteria untuk setiap bentuk dukungan.",
                       "en": "How SMART weighs the eight criteria for each kind of support."},
    "an_sens_intro": {"id": "Apakah rekomendasi berubah bila bobot sedikit digeser.",
                      "en": "Whether the recommendation changes when the weights shift slightly."},
    "an_distributions": {"id": "Sebaran kriteria", "en": "Criteria distributions"},
    "an_gender": {"id": "Komposisi gender", "en": "Gender mix"},
    "an_criteria": {"id": "Kriteria & batas normalisasi", "en": "Criteria & normalization bounds"},
    "an_results": {"id": "Hasil pada populasi referensi", "en": "Results on the reference population"},
    "an_real_none": {"id": "Belum ada ringkasan data riil. Jalankan `scripts/train.py --stage real` untuk menambahkannya.",
                     "en": "No real-data summary yet. Run `scripts/train.py --stage real` to add it."},
    "an_real_title": {"id": "Data kuesioner riil (agregat, tanpa baris individu)", "en": "Real questionnaire data (aggregates, no individual rows)"},
    "an_kaggle_title": {"id": "Data pralatih: Kaggle Student Mental Health & Burnout", "en": "Pretraining data: Kaggle Student Mental Health & Burnout"},
    "an_metrics": {"id": "Metrik pada data uji", "en": "Test-set metrics"},
    "an_metrics_real": {"id": "Model aktif dilatih ulang dengan strategi {s} pada {n} respons riil. Metrik: {note}.",
                        "en": "Active model retrained with strategy {s} on {n} real responses. Metrics: {note}."},
    "an_compare": {"id": "Perbandingan algoritma", "en": "Algorithm comparison"},
    "an_compare_note": {
        "id": "Random Forest setara dengan regresi linear dan gradient boosting pada data Kaggle, lebih baik dari pohon keputusan tunggal, dan jauh lebih baik dari baseline rata-rata. RF dipilih karena menangkap hubungan non-linear pada data kuesioner ordinal, tahan outlier, dan memberi feature importance untuk penjelasan.",
        "en": "Random Forest is on par with linear regression and gradient boosting on the Kaggle data, better than a single decision tree, and far better than the mean baseline. RF was kept because it captures non-linear effects in ordinal questionnaire data, is robust to outliers, and gives feature importance for explanations."},
    "an_strategies": {"id": "Strategi pelatihan ulang (Kaggle → data riil)", "en": "Retraining strategies (Kaggle → real data)"},
    "an_sens_global": {"id": "Seluruh bobot diacak ±{pct}% sebanyak {n} kali",
                       "en": "All weights jittered by ±{pct}%, {n} times"},
    "an_sens_pop": {"id": "Per kriteria", "en": "Per criterion"},
    "an_top1": {"id": "Rekomendasi utama tetap", "en": "Top-1 unchanged"},
    "an_top3": {"id": "Tiga besar tetap", "en": "Top-3 unchanged"},
    "an_fair_intro": {
        "id": "Memeriksa apakah kesalahan prediksi dan sebaran rekomendasi berbeda antar gender. Gender adalah fitur model (importance kecil); selisih besar menandakan bias.",
        "en": "Checks whether prediction error and the recommendation mix differ by gender. Gender is a model feature (small importance); a large gap signals bias."},
    "an_top1_min": {"id": "Iterasi terburuk (top-1)", "en": "Worst iteration (top-1)"},
    "an_base_test": {"id": "Grafik aktual vs prediksi memakai model dasar Kaggle pada data uji Kaggle (2.000 baris).",
                     "en": "Actual-vs-predicted uses the Kaggle base model on the Kaggle test set (2,000 rows)."},
    "an_weights_note": {
        "id": "Bobot profil A pada notebook untuk Olahraga berjumlah 1,05; aplikasi menormalkannya menjadi 1 agar sesuai syarat SMART.",
        "en": "In the notebook, profile A's Exercise weights sum to 1.05; the app normalizes them to 1 as SMART requires."},
    "an_profiles": {"id": "Perbandingan profil bobot", "en": "Weight profile comparison"},
    "an_metadata": {"id": "Hyperparameter & metadata", "en": "Hyperparameters & metadata"},

    # ---- about page ----
    "about_title": {"id": "Tentang aplikasi", "en": "About this app"},
    "about_arch": {"id": "Arsitektur sistem", "en": "System architecture"},
    "about_criteria": {"id": "Kriteria & jenis", "en": "Criteria & types"},
    "about_alts": {"id": "Bentuk dukungan", "en": "Kinds of support"},
    "about_model": {"id": "Model aktif", "en": "Active model"},
    "about_team": {"id": "Tim", "en": "Team"},

    # ---- common words ----
    "alternative": {"id": "Alternatif", "en": "Alternative"},
    "score": {"id": "Skor", "en": "Score"},
    "rank": {"id": "Peringkat", "en": "Rank"},
    "criterion": {"id": "Kriteria", "en": "Criterion"},
    "value": {"id": "Nilai", "en": "Value"},
    "utility": {"id": "Utilitas", "en": "Utility"},
    "type": {"id": "Jenis", "en": "Type"},
    "benefit": {"id": "benefit (makin tinggi makin butuh)", "en": "benefit (higher = more need)"},
    "cost": {"id": "cost (makin rendah makin butuh)", "en": "cost (lower = more need)"},
    "count": {"id": "Jumlah", "en": "Count"},
    "students": {"id": "Siswa", "en": "Students"},
}

FEATURES = {
    "age": {"id": "Usia", "en": "Age"},
    "gender": {"id": "Jenis kelamin", "en": "Gender"},
    "study_hours_per_day": {"id": "Jam belajar per hari", "en": "Study hours per day"},
    "academic_performance": {"id": "Nilai rata-rata rapor", "en": "Academic performance"},
    "exam_pressure": {"id": "Tekanan ujian", "en": "Exam pressure"},
    "stress_level": {"id": "Tingkat stres akademik", "en": "Academic stress level"},
    "sleep_hours": {"id": "Jam tidur", "en": "Sleep hours"},
    "physical_activity": {"id": "Hari olahraga per minggu", "en": "Exercise days per week"},
    "financial_stress": {"id": "Tekanan finansial", "en": "Financial stress"},
    "family_expectation": {"id": "Ekspektasi keluarga", "en": "Family expectation"},
    "burnout_score": {"id": "Skor kelelahan (burnout)", "en": "Burnout score"},
    "rf_anxiety_score": {"id": "Prediksi kecemasan (RF)", "en": "Predicted anxiety (RF)"},
    "anxiety_score": {"id": "Skor kecemasan", "en": "Anxiety score"},
    "smart_score": {"id": "Skor prioritas SMART", "en": "SMART priority score"},
}

FEATURE_HELP = {
    "study_hours_per_day": {"id": "Jam belajar mandiri di luar sekolah (0-14).", "en": "Self-study hours outside school (0-14)."},
    "academic_performance": {"id": "Nilai rata-rata rapor terakhir (0-100).", "en": "Latest report-card average (0-100)."},
    "exam_pressure": {"id": "1 = tidak pernah tertekan, 10 = sangat sering.", "en": "1 = never pressured, 10 = very often."},
    "stress_level": {"id": "0-10, gabungan beban tugas, tugas terlambat, belajar larut malam.", "en": "0-10, combines task load, late tasks, late-night study."},
    "sleep_hours": {"id": "Rata-rata jam tidur malam.", "en": "Average hours of sleep per night."},
    "physical_activity": {"id": "Hari berolahraga ≥20-30 menit dalam seminggu (0-7).", "en": "Days with ≥20-30 min exercise per week (0-7)."},
    "financial_stress": {"id": "0 = uang saku selalu cukup, 10 = tidak pernah cukup.", "en": "0 = pocket money always enough, 10 = never enough."},
    "family_expectation": {"id": "0-10, takut mengecewakan orang tua & tuntutan nilai.", "en": "0-10, fear of disappointing parents & grade demands."},
    "burnout_score": {"id": "0-10, sulit membagi waktu, kelelahan, kehilangan minat.", "en": "0-10, time-splitting trouble, exhaustion, lost interest."},
}

ALTERNATIVES = {
    "Sleep": {"id": "Tidur", "en": "Sleep"},
    "Exercise": {"id": "Olahraga", "en": "Exercise"},
    "Study": {"id": "Strategi belajar", "en": "Study strategy"},
    "Counseling": {"id": "Konseling", "en": "Counseling"},
    "Relaxation": {"id": "Relaksasi", "en": "Relaxation"},
}

ALT_DESC = {
    "Sleep": {"id": "Program perbaikan pola tidur (sleep hygiene) dan jadwal malam.",
              "en": "Sleep-hygiene program and an evening schedule."},
    "Exercise": {"id": "Program aktivitas fisik terjadwal untuk menurunkan ketegangan.",
                 "en": "Scheduled physical activity to lower tension."},
    "Study": {"id": "Pelatihan manajemen waktu dan strategi belajar.",
              "en": "Time-management and study-strategy coaching."},
    "Counseling": {"id": "Konseling individual dengan guru BK; rujukan profesional bila perlu.",
                   "en": "One-to-one counseling with the school counselor; professional referral if needed."},
    "Relaxation": {"id": "Latihan relaksasi: pernapasan, mindfulness, manajemen stres.",
                   "en": "Relaxation practice: breathing, mindfulness, stress management."},
}

# How a high-utility criterion reads in a sentence ({v} = the raw value).
DRIVERS = {
    "rf_anxiety_score": {"id": "prediksi kecemasan tinggi ({v:.1f}/10)", "en": "high predicted anxiety ({v:.1f}/10)"},
    "study_hours_per_day": {"id": "jam belajar panjang ({v:.1f} jam/hari)", "en": "long study hours ({v:.1f} h/day)"},
    "academic_performance": {"id": "nilai rapor rendah ({v:.0f})", "en": "low report grades ({v:.0f})"},
    "sleep_hours": {"id": "jam tidur sedikit ({v:.1f} jam)", "en": "short sleep ({v:.1f} h)"},
    "physical_activity": {"id": "jarang olahraga ({v:.1f} hari/minggu)", "en": "little exercise ({v:.1f} days/week)"},
    "financial_stress": {"id": "tekanan finansial tinggi ({v:.1f}/10)", "en": "high financial stress ({v:.1f}/10)"},
    "family_expectation": {"id": "ekspektasi keluarga tinggi ({v:.1f}/10)", "en": "high family expectation ({v:.1f}/10)"},
    "burnout_score": {"id": "kelelahan tinggi ({v:.1f}/10)", "en": "high burnout ({v:.1f}/10)"},
}

# English labels for the questionnaire's answer options (Indonesian = the option text itself).
OPTIONS_EN = {
    "freq5": ["Never", "Rarely", "Sometimes", "Often", "Very often"],
    "agree5": ["Strongly disagree", "Disagree", "Neutral", "Agree", "Strongly agree"],
    "jajan5": ["Never", "Once in a while", "Neutral", "Often", "Very often"],
    "late_night4": ["Never", "Once", "2-3 times", "4-5 times"],
    "insufficient4": ["Never", "Rarely", "Sometimes", "Often"],
    "late_tasks4": ["None", "1", "2-3", "4-5"],
    "gender": ["Male", "Female"],
    "exercise_days": ["0 days", "1-2 days", "3-4 days", "5-6 days", "7 days"],
}

# Questionnaire items shown in the app (field -> question), same wording as the Google Form.
QUESTIONS = {
    "gender": {"id": "Jenis kelamin", "en": "Gender"},
    "study_hours": {"id": "Rata-rata jam belajar mandiri per hari di luar jam sekolah",
                    "en": "Average self-study hours per day outside school"},
    "late_night": {"id": "Dalam seminggu terakhir, berapa kali Anda belajar sampai larut malam karena tugas/ujian?",
                   "en": "In the last week, how many times did you study late at night for tasks/exams?"},
    "time_insufficient": {"id": "Seberapa sering waktu belajar Anda tidak cukup untuk menyelesaikan seluruh tugas?",
                          "en": "How often is your study time not enough to finish all tasks?"},
    "late_tasks": {"id": "Dalam sebulan terakhir, berapa tugas yang terlambat dikumpulkan?",
                   "en": "In the last month, how many tasks were handed in late?"},
    "report_grade": {"id": "Nilai rata-rata rapor terakhir (0-100)", "en": "Latest report-card average (0-100)"},
    "many_tasks": {"id": "Seberapa sering Anda merasa memiliki terlalu banyak tugas pada waktu yang bersamaan?",
                   "en": "How often do you have too many school tasks at the same time?"},
    "exam_stress": {"id": "Seberapa sering Anda merasa tertekan karena ujian, nilai, atau tuntutan akademik?",
                    "en": "How often do you feel pressured by exams, grades, or academic demands?"},
    "fear_parents": {"id": "Saya takut mengecewakan orang tua jika prestasi saya tidak sesuai harapan mereka",
                     "en": "I am afraid of disappointing my parents if my results miss their expectations"},
    "family_demand": {"id": "Keluarga saya menuntut nilai akademik yang sangat tinggi",
                      "en": "My family demands very high grades"},
    "sleep_duration": {"id": "Rata-rata durasi tidur malam", "en": "Average night sleep duration"},
    "exercise_days": {"id": "Dalam seminggu terakhir, berapa hari Anda berolahraga minimal 20-30 menit?",
                      "en": "In the last week, on how many days did you exercise for at least 20-30 minutes?"},
    "pocket_money": {"id": "Saya memiliki uang saku yang cukup untuk kebutuhan harian di sekolah",
                     "en": "I have enough pocket money for my daily needs at school"},
    "time_split": {"id": "Saya kesulitan membagi waktu antara kegiatan sekolah dan belajar",
                   "en": "I struggle to split my time between school activities and study"},
    "exhausted": {"id": "Saya merasa kelelahan karena banyaknya kegiatan sekolah",
                  "en": "I feel exhausted by the number of school activities"},
    "lost_interest": {"id": "Saya kehilangan minat dan motivasi terhadap belajar maupun sekolah",
                      "en": "I have lost interest and motivation for study and school"},
}


def _pick(table: dict, key: str, lang: str) -> str:
    entry = table.get(key)
    if entry is None:
        return key
    return entry.get(lang) or entry.get(DEFAULT) or key


def t(key: str, lang: str = DEFAULT, **fmt) -> str:
    text = _pick(S, key, lang)
    return text.format(**fmt) if fmt else text


def feature(name: str, lang: str = DEFAULT) -> str:
    return _pick(FEATURES, name, lang)


def feature_help(name: str, lang: str = DEFAULT) -> str | None:
    return FEATURE_HELP.get(name, {}).get(lang)


def alt(name: str, lang: str = DEFAULT) -> str:
    return _pick(ALTERNATIVES, name, lang)


def alt_desc(name: str, lang: str = DEFAULT) -> str:
    return _pick(ALT_DESC, name, lang)


def driver(criterion: str, value: float, lang: str = DEFAULT) -> str:
    return _pick(DRIVERS, criterion, lang).format(v=value)


def question(field: str, lang: str = DEFAULT) -> str:
    return _pick(QUESTIONS, field, lang)


def option_label(scale: str, index: int, option: str, lang: str = DEFAULT) -> str:
    if lang == "en" and scale in OPTIONS_EN and index < len(OPTIONS_EN[scale]):
        return OPTIONS_EN[scale][index]
    return option


def hours_label(hours: float, lang: str = DEFAULT) -> str:
    if hours < 0.5:
        return "Dibawah 30 menit" if lang == "id" else "Under 30 min"
    whole, half = int(hours), (hours - int(hours)) >= 0.5
    if lang == "en":
        return f"{whole} h 30 min" if (whole and half) else (f"{whole} h" if whole else "30 min")
    if whole == 0:
        return "30 menit"
    return f"{whole} jam 30 menit" if half else f"{whole} jam"
