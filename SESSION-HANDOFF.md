# Session handoff: SPK SMART Kecemasan Siswa

Last updated 2026-09-25. This is a recap for the next working session: what was decided, what was built, where the files are, and what is still open.

## 1. Project in one paragraph

Final project for Data Mining + SPK (Kelompok 1, UKRIDA). A Random Forest regressor predicts a student's `anxiety_score` (0–10) from 11 lifestyle and academic features. SMART then turns the prediction and seven other criteria into:

- a priority score (who needs help first), and
- a ranking of 5 interventions: Sleep, Exercise, Study, Counseling, Relaxation.

The app is Streamlit in `app/`. The original Colab notebook is `code/Copy of EskulSPK2026_SMART_Final.ipynb`.

Note: the "EkskulSPK" Streamlit plan the user pasted was a generic template. In this project, "recommended extracurricular" means "recommended intervention".

## 2. Decisions made with the user

| Topic | Decision |
|---|---|
| Real data | Real Google Form data exists, is **confidential**, and is not in the repo. Build a drop-in pipeline: Kaggle pretrain → retrain on real data → deploy → test on new data |
| Docs vs app mismatch | Rewrite the CRISP-DM docs to match the built app. The unbuilt ideas (clustering, classification, association rules, 10 alternatives, Gradio) move to "future work" |
| Scope | App refactor + deploy, Laporan Teknis DM, User Manual + final PPT, PKM draft |
| UI language | Bilingual toggle (ID/EN) |
| Repo visibility | `UKRIDA-Developer-Team/SIMBULL-SMART` is **private**. Raw form data is never committed anyway |
| PKM scheme | "Decide later" |
| Tool installs | Only npm `docx` + `pptxgenjs` approved. **Not** approved: Playwright/Chromium, LibreOffice, pandoc, pip extras. ONLYOFFICE is installed and is used for rendering |
| Git | User approved commit, push, and a PR from `future` into `main` |

## 3. Rubric audit (excluding video, TikTok/IG, and the Kejujuran & Logbook doc)

Rubric sources: `rubricGuide/Rubrik Penilaian Proyek Data Mining dan SPK (1).pdf` and `rubricGuide/DATMIN LAPORAN (UAS).pdf`.

| Output | Status now |
|---|---|
| Final app (Technical 40%: problem formulation, data/criteria, algorithm, architecture, implementation, evaluation & sensitivity, explainability, ethics) | Built and tested locally. **Not deployed yet** |
| Laporan Teknis DM (UAS: cover+TOC, BU 10, DU 15, DP 20, Modeling 25, Eval 15, Deployment 10, GitHub link) | Built, `.docx`, 26 pages. Real-data numbers are placeholders |
| User Manual `.docx` (annotated screenshots) | Built, 28 pages |
| Final PPT `.pptx` (≤15 min) | Built, 13 slides with speaker notes |
| Proposal PKM `.docx` | **Not started** (see §8) |
| User-evaluation GForm (5 rubric questions) | Questions listed in User Manual Appendix B. The form itself is not created |

## 4. What was built

### 4.1 App (`app/`)

- **Entry point and pages:**
  - `streamlit_app.py` uses `st.navigation`.
  - Pages are in `app_pages/`: `home.py`, `recommendation.py`, `analysis.py`, `about.py`. The folder is named `app_pages/` rather than `pages/` to avoid clashing with Streamlit's automatic multipage folder.
  - `ui.py` holds the Streamlit helpers: cached loaders, scoring, sidebar, `show(fig, compact)`.
  - `content/{id,en}/*.md` holds the long page text.
- **Logic in `spk/`** (pure Python, no Streamlit, covered by pytest):

  | Module | Role |
  |---|---|
  | `config.py` | features, criteria, weight profiles A/B/C, paths, `SAFETY_PERCENTILE=90`, `REFERRAL_CONTACT`, `EXAMPLE_PROFILES`, `INPUT_RANGES` |
  | `gform.py` + `gform_mapping.json` | Google Form export → 11 Kaggle-scale features + target. Drops PII. Quality report. Resolves duplicate question titles by how well each column's answers parse |
  | `retrain.py` | Compares 7 strategies with repeated 5-fold CV on real data: S0 Kaggle as-is, S1 real only, S2 combined with weight 1/10/50, S3 warm start +200/+600 trees. S4 (extended features) is reported only. The lowest MAE is deployed |
  | `model.py` | `split`, `train`, `metrics`, `load` (active = real model if present; `SPK_MODEL=base\|real` overrides), `load_base` |
  | `smart.py` | utility, score, rank, recommendation; `perturb`, `sensitivity` (one student), `stability` (population, random ±pct), `population_sensitivity` |
  | `recommend.py` | `assess()`: one student → prediction, percentile, ranking, contributions, sensitivity, safety flag |
  | `explain.py` | weight × utility contributions and the narrative "why" |
  | `i18n.py` | ID/EN strings, questionnaire question text, option labels |
  | `plots.py` | bilingual matplotlib charts |

- **Scripts:**

  | Script | Purpose |
  |---|---|
  | `scripts/train.py --stage kaggle` | rebuild the base model |
  | `scripts/train.py --stage real --gform <file> [--dry-run]` | retrain on real answers |
  | `scripts/train.py --stage compare` | writes `models/model_comparison.json` |
  | `scripts/inspect_gform.py` | check the column mapping against an export |
  | `scripts/evaluate.py --gform <new file>` | test the active model on new answers |
  | `scripts/make_synthetic_gform.py` | writes `data/sample_gform.csv`, 250 **synthetic** rows |

- **Tests:** `app/tests/`, 39 passing.
  - Parsing of every questionnaire option.
  - SMART reproduces the notebook's metrics and cell-92 recommendation counts.
  - Synthetic end-to-end retraining.
  - Every page in ID and EN, profiles B and C, the safety rule, and the language-switch regression.
- **Features added for the rubric:**
  - top 3 alternatives with a contribution chart and narrative;
  - per-student ±10/±20% sensitivity table;
  - global stability (±10%: 94.6% of top recommendations unchanged for profile A);
  - fairness panel by gender;
  - disclaimer and safety rule (top 10% predicted anxiety → counseling + referral);
  - PII dropped on upload;
  - evaluation on new labeled uploads;
  - "Risiko tinggi / Risiko rendah" example buttons.
- **Other files:**
  - Root `.streamlit/config.toml` is a copy of `app/.streamlit/config.toml`, in case Cloud reads config from the repo root.
  - `.gitignore` covers `app/data/private/`, `app/reports/private/`, and `deliverables/build/node_modules/`.

### 4.2 Documents

| Item | Location |
|---|---|
| CRISP-DM phase docs, rewritten to match the app | `PPT-Doc_CRISP-DM/fase1-business-understanding.md` … `fase6-deployment.md` |
| Original design drafts, archived | `PPT-Doc_CRISP-DM/_rancangan-awal/` |
| Laporan Teknis DM | `deliverables/laporan-dm/Laporan-Teknis-Data-Mining.docx` (+ compiled `laporan-teknis-dm.md`) |
| User Manual | `deliverables/user-manual/User-Manual-SPK-SMART-Kecemasan.docx` (source `user-manual.md`) |
| Screenshots | `deliverables/user-manual/screens/` (raw + element boxes as JSON) and `figures/` (annotated) |
| Final deck | `deliverables/ppt/Presentasi-SPK-SMART-Kecemasan.pptx` |
| Build tooling | `deliverables/build/` |

Build tooling in `deliverables/build/`:

| File | Role |
|---|---|
| `md2docx.js` | Markdown → docx converter: tables, lists, images, `[[TOC]]`, `[[PAGEBREAK]]`, ⟦placeholder⟧ highlight. `buildWithToc` does two passes to fill the TOC with real page numbers |
| `build_laporan.js`, `build_manual.js`, `build_ppt.js` | build each deliverable |
| `annotate.py` | numbered callouts on screenshots; splits tall figures at blank rows |
| `render.sh` | docx/pptx → PDF with ONLYOFFICE `x2t` |
| `preview.py` | page PNGs + contact sheets |
| `pdf_pages.py` | page text extraction, used to find TOC page numbers |

Rebuild:
```bash
cd deliverables/build && npm install
node build_laporan.js && node build_manual.js && node build_ppt.js
../../app/.venv/bin/python preview.py ../ppt/Presentasi-SPK-SMART-Kecemasan.pptx /tmp/prev 4 1100   # visual check
```

## 5. Key findings (already reflected in app and docs)

- **Notebook bug:** in weight profile A, the Exercise weights sum to **1.05**. The app uses `normalize(WEIGHTS_A_NOTEBOOK)`, which changes Exercise wins from 8,866 to 6,905 of 20,000. Tests still reproduce the notebook counts with the raw weights.
- **Algorithm comparison** (5-fold CV MAE on Kaggle): Linear Regression 0.768, Gradient Boosting 0.773, RF 0.779, Decision Tree 0.881, mean baseline 1.224. Stated honestly; RF is kept for continuity, non-linear robustness, and warm start.
- The Kaggle data is university students aged 17–29, apparently synthetic. The target population is SMA students, hence the retraining pipeline.
- **Fixed:** the language switch reset the input-mode radio (a `format_func` quirk). Keys now include the language, and the choice lives in `input_mode_choice` / `batch_demo_choice`.
- **Fixed:** `INPUT_RANGES` was widened (age 12–30, grade 0–100, sleep ≤ 12) so SMA rows are not blanked.
- Notebook cell 62 used an undefined `criteria_plot`. The app uses `CRITERIA`.

## 6. Current git state

- Branch `future` is pushed to `origin`. Commits on top of `main` (774c88a): `820abe8`, `bffd801`, `c8ff862`, `ec14cac`, `4b73246`.
- **The PR is NOT opened yet.** There is no `gh` CLI on this machine. Open it at: https://github.com/UKRIDA-Developer-Team/SIMBULL-SMART/pull/new/future
- Untracked on purpose, not committed: `context.pdf` (questionnaire + a different PKM summary), `rubricGuide/`, `.claude/launch.json`.
- **Warning:** in the user's shell, `gh` is aliased to `git push`. Never call bare `gh`.

## 7. Open tasks (in order)

1. **Open and merge the PR** into `main`.
2. **Deploy on Streamlit Community Cloud.** This needs the user's account: branch `main`, file `app/streamlit_app.py`, Python 3.12, private repo access. Then smoke-test the URL: every page in ID/EN, one student, and an upload of `app/data/sample_gform.csv`.
3. **Run the real data** once the user places the export at `app/data/private/gform_raw.csv`:
   ```bash
   cd app
   python scripts/inspect_gform.py data/private/gform_raw.csv   # fix "header" in spk/gform_mapping.json if a field is missing/ambiguous
   python scripts/train.py --stage real --gform data/private/gform_raw.csv
   ```
   Commit only `models/rf_real_model.joblib`, `models/rf_real_model_metadata.json`, and `models/real_summary.json`. `reports/private/real_data_report.md` holds the numbers for the docs and stays private.
4. **Fill ⟦ISI⟧ placeholders**, then rebuild the docs:
   - `PPT-Doc_CRISP-DM/fase1` (D4, S4), `fase2` (respondent count, §2.3.1 stats), `fase3` (rows/holdout), `fase4` (strategy table), `fase5` (CV/holdout/new data, fairness, business goals), `fase6` (app URL);
   - `deliverables/build/build_laporan.js` (app URL in the appendix);
   - `deliverables/user-manual/user-manual.md` (app URL, evaluation-form link);
   - `deliverables/build/build_ppt.js` (respondent count, real MAE and strategy, app URL).
5. Set the real counselor/psychologist contact in `REFERRAL_CONTACT` (`app/spk/config.py`).
6. Create the user-evaluation Google Form. The 5 questions are in User Manual Appendix B.
7. **PKM proposal (not started).** It needs:
   - the PKM 2026 template (linked in the rubric, not in the repo);
   - the scheme (KC / RE / PI …);
   - a resolution of the conflict: `context.pdf`'s "Ringkasan" describes a *face-expression lightweight-model benchmark for mahasiswa*, not this SPK app.

   Akt 2024 grading focuses on the **Bab Metode**: data collection, the decision-algorithm stages, and result analysis. Do not invent citations; use real references (PubMed/consensus tools are available).
8. After deployment, retake the screenshots if the UI changed, then rerun `annotate.py` and `build_manual.js`.

## 8. Practical notes for the next session

- **Environment:** `app/.venv` (Python 3.14, pinned `requirements.txt` + `openpyxl`, `pytest`). Run tests with `cd app && .venv/bin/python -m pytest -q` (about 30–120 s).
- **Preview server:** `.claude/launch.json` config `spk-streamlit` on port 8501. Restart the server after changing `ui.py` or `spk/*`: page files reload on rerun, imported modules do not.
- **AppTest limitation:** widgets with a `format_func` cannot be driven through `set_value` or a button click. Tests inject `session_state` instead (see `tests/test_app.py`).
- **Screenshot method** (no headless browser installed): in the in-app browser, emulate a 1400×900 viewport, inject `html-to-image` from jsdelivr, and POST PNGs to a tiny local receiver on `127.0.0.1:8765` that writes to `deliverables/user-manual/screens/` (the receiver script was temporary; recreate it if needed). Workarounds:
  - Expanders need the style forced open: `details.open=true; style.height='auto'`.
  - Tab clicks do not rerun the page, so reload after code changes.
- **Rendering check:** the Read tool cannot render PDFs (no poppler). Use `preview.py`, which calls `x2t` with format 1029 and produces contact sheets.
- **Style rules the user set:** Bahasa Indonesia for deliverables; app strings bilingual; code identifiers in English.
