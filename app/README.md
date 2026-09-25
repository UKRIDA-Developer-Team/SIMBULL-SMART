# SPK SMART Kecemasan – Streamlit app

This app is the deployable version of `code/Copy of EskulSPK2026_SMART_Final.ipynb`. A Random Forest predicts a student's `anxiety_score` (0–10). SMART then uses that score and seven other criteria to:

- rank how urgently each student needs attention (priority score), and
- rank five interventions: Sleep, Exercise, Study, Counseling, Relaxation.

The model is pretrained on a Kaggle sample. It can be retrained on the team's real Google Form answers when that confidential export is dropped in (see [Real questionnaire data](#real-questionnaire-data)).

The UI is bilingual (Bahasa Indonesia / English) and has four pages: Home, Recommendation, Analysis, and About.

## Layout

```
app/
├── streamlit_app.py          # entry point: st.navigation, language toggle, weight-profile sidebar
├── ui.py                     # Streamlit helpers: cached loaders, scoring, sidebar, footer
├── app_pages/
│   ├── home.py               # problem, users, workflow, call to action
│   ├── recommendation.py     # one student (questionnaire or 11 features) / many students (upload)
│   ├── analysis.py           # data, model, SMART, sensitivity, fairness
│   └── about.py              # method, architecture, limitations, ethics
├── content/{id,en}/*.md      # long page text per language
├── spk/
│   ├── config.py             # features, criteria, benefit/cost, weight profiles, paths, safety settings
│   ├── data.py               # Kaggle download + sampling, gender encoding, CSV validation
│   ├── gform.py              # Google Form export -> 11 features + target, PII removal, quality report
│   ├── gform_mapping.json    # which form column feeds which field; answer tables
│   ├── model.py              # RF split/train/evaluate/save/load (active model = real if present)
│   ├── retrain.py            # Kaggle -> real-data retraining strategies and selection
│   ├── smart.py              # utility, SMART score, rank, recommendation, sensitivity, stability
│   ├── recommend.py          # assess(): one student -> prediction, percentile, ranking, safety flag
│   ├── explain.py            # weight × utility contributions and the narrative "why"
│   ├── i18n.py               # UI strings (id/en)
│   └── plots.py              # notebook charts + new ones, all bilingual
├── scripts/
│   ├── train.py              # --stage kaggle | real | compare
│   ├── inspect_gform.py      # check a form export against the mapping before training
│   ├── evaluate.py           # score the deployed model on new labeled answers
│   └── make_synthetic_gform.py  # SYNTHETIC export for tests and the demo
├── tests/                    # pytest: parsing, SMART == notebook, retraining, every page in both languages
├── data/
│   ├── dataset.csv           # Kaggle 20k sample (committed)
│   ├── sample_gform.csv      # SYNTHETIC form export, 250 rows (committed, no real people)
│   └── private/              # real exports (gitignored, never committed)
├── models/                   # base model + metadata, model_comparison.json, and after retraining
│                             # rf_real_model.joblib + metadata + real_summary.json (aggregates only)
└── reports/private/          # retraining report with answer examples (gitignored)
```

## Run locally

```bash
cd app
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-train.txt
streamlit run streamlit_app.py
pytest                                   # about 40 s
```

The Kaggle model and data are committed. To rebuild them, run `python scripts/train.py --stage kaggle`, which downloads about 131 MB from Kaggle. To use an existing `dataset.csv` instead, add `--csv path`.

## Real questionnaire data

The Google Form export is confidential. Keep it under `app/data/private/`, which git ignores.

```bash
cp "<Google Form export>.csv" data/private/gform_raw.csv
python scripts/inspect_gform.py data/private/gform_raw.csv        # 1. check the column mapping
python scripts/train.py --stage real --gform data/private/gform_raw.csv   # 2. retrain
streamlit run streamlit_app.py                                    # 3. the app now uses the real model
python scripts/evaluate.py --gform data/private/gform_new.csv     # 4. later: test on new answers
```

1. **Inspect.** Every field in `spk/gform_mapping.json` must resolve to exactly one column. If a field is missing or ambiguous, copy the exact column name into its `"header"` and run the inspect step again. The report also lists answers that could not be parsed.
2. **Retrain.** The step compares seven strategies with repeated 5-fold CV on the real answers: Kaggle model as is, real only, Kaggle + real with weights 1/10/50, and warm start with +200/+600 trees. It deploys the one with the lowest MAE and writes:
   - `models/rf_real_model.joblib` and its metadata,
   - `models/real_summary.json` (aggregates only; groups under 5 people are hidden),
   - `reports/private/real_data_report.md` (keep private).

   Commit the model and the summary, never the export. To dry-run on the synthetic file, use `python scripts/train.py --stage real --gform data/sample_gform.csv --dry-run`.
3. **Use.** The app loads the real model automatically. `SPK_MODEL=base` forces the Kaggle model and `SPK_MODEL=real` forces the real one.
4. **Test on new data.** The Recommendation page's upload tab does the same check interactively. If the file has the Psikologis answers, it shows MAE/RMSE/R² for the active model and the base model.

Form answers become model features as follows (see `spk/gform.py::derive`):

| Model feature | Form answers |
|---|---|
| age | birth date and timestamp |
| study_hours_per_day, sleep_hours | "1 jam 30 menit" → 1.5 |
| academic_performance | report-card average |
| exam_pressure | Likert 1–5 → 1–10 |
| stress_level | mean of too-many-tasks, not-enough-time, late tasks, late-night study, × 10 |
| physical_activity | exercise days (0 / 1-2 / 3-4 / 5-6 / 7 → 0 / 1.5 / 3.5 / 5.5 / 7) |
| financial_stress | reverse of "enough pocket money", × 10 |
| family_expectation | fear of disappointing parents + family grade demands, × 10 |
| burnout_score | time-splitting trouble + exhaustion + lost interest, × 10 |
| **anxiety_score** (target) | the 5 Psikologis items, concentration item reversed: 0–20 → 0–10 |

The target items are never used as features. Timestamp, birth date, school, info source, and friend's name are dropped as soon as age is computed.

## Deploy to Streamlit Community Cloud

1. Push the repo to GitHub. It is private; give Streamlit access when prompted.
2. On share.streamlit.io, click Create app. Pick the repo, branch `main`, and main file `app/streamlit_app.py`.
3. Under Advanced settings, pick Python 3.12 or newer. The app needs no secrets.
4. Open the URL. Check each page in ID and EN, submit one student, and upload `data/sample_gform.csv`.

## Things that changed vs the notebook

- **Weight profile A is normalized.** In the notebook, the Exercise weights sum to 1.05. That makes Exercise win for 8,866 of 20,000 students. The app scales each alternative's weights to sum to 1, and then Exercise wins for 6,905. `config.WEIGHTS_A_NOTEBOOK` keeps the original, and a test reproduces the notebook's counts with it.
- **Retrain with the pinned versions.** Joblib pickles are tied to the scikit-learn version. `scripts/train.py` rebuilds the model with the versions in `requirements.txt`. The metrics match the notebook: MAE 0.7668, RMSE 0.9546, R² 0.6136.
- **Algorithm comparison** (`--stage compare`, 5-fold CV MAE): Random Forest 0.779, Linear Regression 0.768, Gradient Boosting 0.773, Decision Tree 0.881, mean baseline 1.224. RF is kept for continuity and non-linear robustness; the About and Analysis pages state this.
- **Reference bounds for SMART.** The notebook normalizes with the min and max of the whole dataset. A single student has no such range, so training saves the dataset bounds in the metadata (`smart_bounds`).
- **Weight C** gives equal weights, so all alternatives tie and the result is always "Sleep". The app keeps it only as a control and shows a warning.
- **Notebook bug:** cell 62 uses `criteria_plot`, which is never defined. `plots.correlation_heatmap` uses `CRITERIA` instead.
