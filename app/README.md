# SPK SMART Kecemasan – Streamlit app

This app is the deployable version of `code/Copy of EskulSPK2026_SMART_Final.ipynb`. A Random Forest predicts a student's `anxiety_score` (0–10). SMART then uses that score and seven other criteria to:

- rank how urgently each student needs attention (priority score), and
- rank five interventions: Sleep, Exercise, Study, Counseling, Relaxation.

The model is pretrained on a Kaggle sample. It can be retrained on the team's real Google Form answers when that confidential export is dropped in (see [Real questionnaire data](#real-questionnaire-data)).

The UI is bilingual (Bahasa Indonesia / English) and has five pages: Home, Recommendation, Analysis, Data Mining, and About. Pages sit in a top navigation bar; the ID/EN switch is on the right of that bar, and the SMART weight profile is a small setting on the Recommendation and Analysis pages.

## Layout

```
app/
├── streamlit_app.py          # entry point: top navigation, logo, language switch
├── ui.py                     # Streamlit helpers: cached loaders, scoring, page header, weight-profile picker, footer
├── assets/                   # style.css (layout and components on top of the theme), logo.svg, mark.svg
├── app_pages/
│   ├── home.py               # what it does, how it works, the five kinds of support, call to action
│   ├── recommendation.py     # one student (questionnaire -> result card) / a whole class (upload -> priority list)
│   ├── analysis.py           # data, model, xAI (global), SMART, sensitivity, fairness
│   ├── data_mining.py        # the CRISP-DM process, phase by phase, with live numbers
│   └── about.py              # method, architecture, limitations, ethics
├── content/{id,en}/*.md      # long page text per language (About, Data Mining phases, xAI methods)
├── spk/
│   ├── config.py             # features, criteria, benefit/cost, weight profiles, paths, safety settings
│   ├── data.py               # Kaggle download + sampling, gender encoding, CSV validation
│   ├── gform.py              # Google Form export -> 11 features + target, PII removal, quality report
│   ├── gform_mapping.json    # which form column feeds which field; answer tables
│   ├── model.py              # RF split/train/evaluate/save/load (active model = real if present)
│   ├── retrain.py            # Kaggle -> real-data retraining strategies and selection
│   ├── smart.py              # utility, SMART score, rank, recommendation, sensitivity, stability
│   ├── recommend.py          # assess(): one student -> prediction, percentile, ranking, safety flag
│   ├── explain.py            # weight × utility contributions and the narrative "why" (SMART and Shapley)
│   ├── xai.py                # explainable AI: exact Shapley values, what-if, permutation importance, PDP/ICE
│   ├── crispdm.py            # facts for the Data Mining page: column roles, success criteria, test counts
│   ├── i18n.py               # UI strings (id/en)
│   └── plots.py              # notebook charts + new ones, all bilingual
├── scripts/
│   ├── train.py              # --stage kaggle | real | compare
│   ├── inspect_gform.py      # check a form export against the mapping before training
│   ├── evaluate.py           # score the deployed model on new labeled answers
│   ├── make_synthetic_gform.py  # synthetic export generator, used only by the tests
│   ├── merge_report.py       # which questions are merged into which feature / SMART criterion
│   └── coverage_report.py    # statement coverage of spk/ with the standard library
├── tests/                    # pytest: black-box, white-box, SMART and model pins, retraining, every page
│   └── TESTING.md            # test plan: every black-box and white-box case
├── data/
│   ├── dataset.csv           # 20,000 Kaggle test rows, ages 14-25 (committed): the app's reference population
│   ├── kaggle_retrain.csv.gz # 8,000 Kaggle training rows mixed into questionnaire retraining (committed)
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
pytest                                   # about 75 s; -m blackbox or -m whitebox for one suite
python scripts/coverage_report.py        # the same, plus statement coverage of spk/
```

The Kaggle model and data are committed. To rebuild them, run `python scripts/train.py --stage kaggle`. It needs the full 1M-row Kaggle file: it uses the kagglehub cache when present, else downloads about 131 MB; `--full-csv path` points at a local copy. `--stage tune` repeats the hyperparameter search and `--stage compare` the algorithm comparison; both read the same full file. Training takes a few minutes and the model file is about 29 MB.

## Real questionnaire data

**Current result (304 responses, `data/private/gform_data.csv`).** 292 responses remain after the age band and the target check (233 development, 59 holdout). Selected strategy: S1, real data only (holdout MAE 1.113, R² 0.441; CV MAE 1.251, R² 0.204). The Kaggle model as is scores holdout MAE 1.874, R² −0.346. The reliability check removed "can talk to my family" from `family_expectation` (it lowered Cronbach's alpha from 0.53 to 0.37). `reports/question_merge_report.md` shows which questions feed which feature and criterion.

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

   Commit the model and the summary, never the export. To try the pipeline without saving a model, add `--dry-run`.
3. **Use.** The app loads the real model automatically. In the app, the **Profile · Model** popover switches between iteration 1 (Kaggle) and iteration 2 (real data) for the session; every page follows the choice, the result screen compares both models for one student, and Analysis → Model shows both models on both test sets. `SPK_MODEL=base` or `SPK_MODEL=real` sets the default.
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

## Explainable AI (xAI)

Every result explains itself at both stages of the pipeline (`spk/xai.py`, shown on the Recommendation page):

- **Why this predicted anxiety?** Exact Shapley values (interventional SHAP) for the Random Forest prediction. With 11 features there are 2,048 feature coalitions, so all of them are evaluated against 100 random reference students instead of being sampled; the values add up exactly to prediction − average. A waterfall chart and a short narrative show which answers push the score up or down.
- **How does the prediction become a recommendation?** The predicted anxiety is one SMART criterion; the card shows its share of the winning alternative's score and the weight × utility bars of every alternative.
- **What if?** Each factor a counselor can work on (stress, burnout, exam pressure, sleep, exercise, study hours, financial stress, family expectation) moves to a typical student's level, and RF + SMART run again. A slider lets the user try any value. These are model simulations, not causal claims, and the page says so.

The whole-class view can explain any student in the priority list the same way. The Analysis page adds global explanations: Gini vs permutation importance and PDP/ICE curves. No extra package is needed (no `shap`), so Streamlit Cloud deploys as before.

## Testing

`tests/TESTING.md` is the test plan. Black-box tests (`pytest -m blackbox`) are designed from the specification with equivalence partitioning, boundary values, a decision table for the safety rule, metamorphic relations, and system tests of the running app. White-box tests (`pytest -m whitebox`) cover every branch of the SMART, explanation, xAI and model-selection code and check algorithm properties (Shapley efficiency, dummy, symmetry, the linear case). `scripts/coverage_report.py` reports statement coverage of `spk/` (97.5% with the whole suite).

## Look and feel

The theme lives in `.streamlit/config.toml` (colors, Plus Jakarta Sans from Google Fonts, radii); `assets/style.css` adds the page width, cards, the result card and bar lists. Charts in `spk/plots.py` share one Matplotlib style and fixed colors: one color per intervention and one per criterion, checked for color-vision deficiency. Keep `.streamlit/config.toml` at the repo root identical to the one in `app/`.

## Deploy to Streamlit Community Cloud

1. Push the repo to GitHub. It is private; give Streamlit access when prompted.
2. On share.streamlit.io, click Create app. Pick the repo, branch `main`, and main file `app/streamlit_app.py`.
3. Under Advanced settings, pick Python 3.12 or newer. The app needs no secrets.
4. Open the URL. Check each page in ID and EN, submit one student, and open the whole-class view (it uses the Kaggle test sample when nothing is uploaded).

## Things that changed vs the notebook

- **Weight profile A is normalized.** In the notebook, the Exercise weights sum to 1.05. On the 20,000 reference students that makes Exercise win for 9,338. The app scales each alternative's weights to sum to 1, and then Exercise wins for 7,323. `config.WEIGHTS_A_NOTEBOOK` keeps the original, and a test pins the counts for both.
- **Retrain with the pinned versions.** Joblib pickles are tied to the scikit-learn version. `scripts/train.py` rebuilds the model with the versions in `requirements.txt`.
- **Age cleaning.** The notebook trains on every age in its 2% sample (17-29). The app keeps the student age band 14-25 (`config.AGE_RANGE`): 14 covers the questionnaire students, and because the Kaggle file starts at 17, ages 17-25 remain (692,545 of 1,000,000 rows). The data has no missing, duplicate or impossible values; removing outliers or extreme rows did not raise R², so no other rows are dropped.
- **Full file, 80/20 split.** The notebook trains on 8,000 rows and tests on 2,000. The app uses the whole age-filtered file and splits it 80/20, stratified by age: 554,036 training rows and 138,509 test rows. 20,000 test rows become `dataset.csv`, the reference population for charts, percentiles and SMART bounds, so the app never shows rows the model was trained on.
- **Tuned settings.** `--stage tune` runs a random search (25 settings, 5-fold CV on 50,000 training rows; `models/rf_tuning.json`). Best: 300 trees, `max_depth=12, min_samples_leaf=50, max_features=0.75, max_samples=0.6` (CV R² 0.5996; notebook settings 0.5966). The notebook settings stay in use for the small questionnaire data (`config.RF_PARAMS_NOTEBOOK`).
- **Metrics.** Test set (138,509 rows): MAE 0.7583, RMSE 0.9470, R² 0.6077. The notebook reports 0.7668, 0.9546, 0.6136 on its own 2,000 rows, a lucky split: over 40 other splits its method averages R² 0.599. On the 137,365 test rows neither model trained on, the notebook model scores R² 0.598 and the deployed model 0.608. With 138,509 test rows R² moves by under ±0.002 between split seeds.
- **R² ceiling.** On this dataset R² stops near 0.61 with the 11 features: linear regression 0.606, gradient boosting 0.608 and the Random Forest 0.608 on the test set. A forest trained on the linear residuals scores R² -0.01, so the remaining 40% of the variance is noise the inputs do not carry. `mental_health_index` would give 0.80, but it is computed from the target (`10 - 0.4 stress - 0.3 anxiety - 0.3 depression`), so it stays excluded as leakage.
- **Algorithm comparison** (`--stage compare`: 5-fold CV MAE on 50,000 training rows, then test R² with all training rows): Random Forest 0.761 / 0.608, Linear Regression 0.760 / 0.606, Gradient Boosting 0.761 / 0.608, Decision Tree 0.799 / 0.601, mean baseline 1.213 / 0.000. RF is kept for continuity and non-linear robustness; the About and Analysis pages state this.
- **Reference bounds for SMART.** The notebook normalizes with the min and max of the whole dataset. A single student has no such range, so training saves the dataset bounds in the metadata (`smart_bounds`).
- **Weight C** gives equal weights, so all alternatives tie and the result is always "Sleep". The app keeps it only as a control and shows a warning.
- **Notebook bug:** cell 62 uses `criteria_plot`, which is never defined. `plots.correlation_heatmap` uses `CRITERIA` instead.
