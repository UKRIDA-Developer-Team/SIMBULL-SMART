# Test plan: black-box and white-box testing

The app is tested at two levels, and every case is an automated pytest test.

- **Black-box tests** (`test_blackbox.py`, marker `blackbox`) are designed from the specification: what a counselor enters and what the system must answer. They do not depend on how the code is written.
- **White-box tests** (`test_whitebox.py`, marker `whitebox`) are designed from the code: every branch of the decision logic, every path of small functions, and the mathematical properties the algorithms must satisfy.
- **Regression and integration tests** (`test_smart.py`, `test_gform.py`, `test_pipeline.py`, `test_app.py`) existed before this split. They check that the retrained base model and the SMART counts stay as recorded, that every questionnaire answer parses, that retraining works end to end, and that every page loads in both languages.

## How to run

From `app/`:

```bash
pytest                                     # everything (about 90 s)
pytest -m blackbox                         # black-box only (about 20 s)
pytest -m whitebox                         # white-box only (about 5 s)
python scripts/coverage_report.py          # everything + statement coverage of spk/
python scripts/coverage_report.py -m whitebox --out reports/coverage.md
```

`scripts/coverage_report.py` measures statement coverage with the standard library (`sys.monitoring`, Python 3.12+), so no extra package is needed.

## Results (2026-11-17)

| Suite | Test cases collected | Result |
|---|---|---|
| Black-box | 58 | all pass |
| White-box | 47 | all pass |
| Regression / integration | 50 | all pass |
| **Total** | **155** | **all pass** |

Statement coverage of `spk/` with the whole suite: **98.2%** (2,176 of 2,217 statements). `smart.py`, `xai.py`, `explain.py`, `recommend.py`, `crispdm.py`, `config.py` and `i18n.py` are at 100%. The lines not run are the Kaggle download (offline only), model saving, and a chart that needs real questionnaire data.

## Black-box cases

Techniques: **EP** equivalence partitioning, **BVA** boundary value analysis, **DT** decision table, **MT** metamorphic testing, **ST** system test of the running app.

| ID | Technique | Input | Expected output |
|---|---|---|---|
| BB-01 | EP | a low-risk, a typical and a high-risk student | anxiety 0-10, priority 0-1, percentiles 0-100, five alternatives ranked best first, utilities 0-1 |
| BB-02 | EP | high-risk vs low-risk example | high-risk has higher prediction, percentile and priority; only high-risk triggers the safety rule |
| BB-03 | BVA | each numeric input at min, min + step, max − step, max | a valid result for every value |
| BB-04 | BVA | each numeric input at min − ε, min, max, max + ε in an uploaded CSV | the two outside values are blanked and reported, the boundary values are kept |
| BB-05 | DT | prediction at percentile 0, 50, 89.9, 90, 90.1, 100 | safety flag only at ≥ 90 |
| BB-06 | MT | the same class in shuffled row order | every student's scores and recommendation unchanged |
| BB-07 | MT | a class with one student duplicated | both copies get identical results |
| BB-08 | MT | one student scored alone and inside a class | same priority, recommendation and safety flag |
| BB-09 | EP / BVA | questionnaire with all lowest, all middle, all highest answers | 11 features inside the allowed ranges, none missing |
| BB-10 | EP | a model-feature CSV, a Google Form export, an unrelated table | accepted as is / converted with personal columns dropped / rejected with the missing columns |
| BB-11 | EP | gender "female", "Robot", "MALE" | "Robot" reported and blanked, the others normalized |
| BB-12 | EP | low-risk and high-risk student | the Shapley waterfall ends exactly at the prediction shown on the result card |
| BB-13 | EP | high-risk and low-risk student | high-risk: one what-if row per factor worse than typical + a combined row that lowers anxiety; low-risk: none |
| BB-14 | MT | what-if that keeps a factor at its current value | identical prediction, priority and recommendation |
| BB-15 | ST | result page, ID and EN | xAI card with three tabs, Shapley narrative, two charts, the what-if slider and metrics |
| BB-16 | ST | what-if slider moved from 8.5 to 4.0 (stress) | the simulated prediction drops |
| BB-17 | ST | Data Mining page, each of the six phases, ID and EN | the phase renders with its name and key decisions; phase 5 shows the success-criteria table |
| BB-18 | ST | whole-class view with the Kaggle demo sample | a student picker and the same AI explanation |

**Defect found by BB-05.** The single-student view compared an interpolated percentile with 90, while the whole-class view compared the prediction with the 90th-percentile value. For a prediction exactly at the cutoff, interpolation returned 89.99999…, so the same student could be flagged in the class list but not on their own result card. Both views now use `recommend.cutoff()`, which returns the stored 90th-percentile value exactly (the Random Forest sums its trees in thread order, so the last bits of a prediction vary between runs, and `np.interp` can round a knot down). BB-05, BB-08 and WB-07b guard the fix.

## White-box cases

Techniques: **BC** branch coverage, **PC** path coverage, **PR** property of the algorithm.

| ID | Technique | Unit | What is covered |
|---|---|---|---|
| WB-01 | BC | `smart.utility` | hi = lo → 1.0; benefit formula; cost formula; clipping below 0 and above 1 |
| WB-02 | BC | `smart.utility` | `bounds=None` → min/max from the frame (notebook behaviour) |
| WB-03 | BC | `smart.perturb` | normal renormalization; all-zero profile (no division by zero); missing criterion |
| WB-04 | PC | `smart.rank`, `smart.best_alternative` | dense ranks with ties; a tie goes to the first alternative (profile C) |
| WB-05 | PC | `smart.sensitivity` | criterion × delta grid; zero delta never changes the result |
| WB-05b | PC | `smart.run`, `stability`, `population_sensitivity` | output columns; no jitter → 100% unchanged; zero delta → 0 |
| WB-06 | PR | `config.normalize` | weights sum to 1 and keep their proportions |
| WB-07 | BC | `recommend.percentile` | clamp below, clamp above, interpolation |
| WB-07a | PC | `recommend.reference_quantiles` | 101 sorted quantiles |
| WB-07b | BC / PR | `recommend.cutoff` | on a stored quantile → that value exactly; between two → interpolated; inverse of `percentile`; a prediction at the cutoff is flagged |
| WB-08 | PC | `config.active_model_paths` | `SPK_MODEL` = base / real / auto with and without the real model / unset |
| WB-09 | BC | `data.encode_gender` | text → codes; numeric pass-through; unknown text raises |
| WB-10 | BC | `data.validate_values` | numeric gender codes → text; non-numeric vs missing counts |
| WB-11 | BC | `explain.narrative` | gap < 0.02 adds the "also consider" line |
| WB-12 | BC | `explain.narrative` | driver wording for utility ≥ 0.5 vs < 0.5 |
| WB-13 | BC | `explain.top_drivers` | zero contributions are never named |
| WB-14 | BC | `explain.shap_narrative` | no upward effect; downward line; SMART link line; value formatting per feature |
| WB-15 | PR | `xai.coalitions` | 2^m distinct subsets, row k = bits of k |
| WB-16 | PR | `xai.shapley_weights` | weights over all coalitions sum to 1 (m = 1, 2, 5, 11) |
| WB-17 | PR | `xai.shapley_values` | linear model: φᵢ = βᵢ(xᵢ − x̄ᵢ) exactly; dummy feature = 0; efficiency |
| WB-18 | PR | `xai.shapley_values` | symmetry: an interaction x_a·x_b is split equally |
| WB-19 | PR | `xai.shapley_values` on the deployed RF | base value = mean background prediction; values add up to `model.predict`; top two = stress, burnout |
| WB-20 | BC | `xai.counterfactuals`, `reference_targets` | factor better than target → no row; worse → row (both directions); one row → no "all"; two → "all" = sum for a linear model |
| WB-21 | PR | `xai.partial_dependence` | linear model: PDP slope = β, ICE curves parallel, grid inside 5-95% |
| WB-22 | PR | `xai.permutation_importance` | unused feature → exactly 0; used feature > 0; sorted |
| WB-23 | PC | `xai.smart_link` | share = anxiety contribution / winning score |
| WB-24 | BC | `crispdm.success_criteria` | met / not met / pending for every criterion; D4 from holdout or CV MAE |
| WB-25 | PC | `crispdm` | column roles, test counting (missing folder), data quality |
| WB-26 | BC | `ui.band` | four bands and the exact boundaries 90 / 60 / 40 |
| WB-27 | BC | `i18n.t` | missing key, missing language fallback, every new key in both languages |
| WB-28 | BC, PR | `data.clean`, `data.load_dataset`, `data.build_training_rows`, `data.retrain_rows`, `model.kaggle_test_set` | rows outside the student age band dropped, both ends kept, raw file untouched; training rows inside the band with equal age shares; no training row is in the test sample |
