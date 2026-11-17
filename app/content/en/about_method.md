### Data

| Source | Content | Role |
|---|---|---|
| Kaggle *Student Mental Health & Burnout* (1M rows) | Student age band 14-25 only = 692,545 rows (the file holds ages 17-25), split 80/20: 554,036 training rows, 138,509 test rows | Pretraining; 20,000 test rows are the reference population for analysis |
| Google Form questionnaire for high-school students | ~50 questions (academics, sleep, social media, family, exercise, fatigue, peers, psychological items, eating habits) | Retraining on real data; testing on new data |

The questionnaire data is **confidential**: the raw file never enters the repository, personal columns (timestamp, birth date, school, friend's name) are dropped right after age is computed, and the app only ships aggregate summaries.

### Data preparation

- **Kaggle**: no missing values, no duplicate rows, no impossible values; `gender` has a fixed code (`Female=0, Male=1, Other=2`, the same as the notebook's LabelEncoder). Pipeline: the full 1M-row file → only rows in the student age band 14-25 (the file spans 17-29, so ages 17-25 remain) → an 80/20 train/test split, stratified by age (`random_state=42`). The model trains on all 554,036 training rows and is scored on all 138,509 test rows. 20,000 test rows (`dataset.csv`) are the app's reference population, so charts and percentiles never use training rows.
- **Google Form → 11 model features** (`spk/gform.py`): text answers become numbers, then are scaled to the Kaggle feature ranges. Each item is first mapped to 0-1 (level 1 → 0, top level → 1):
  - study and sleep hours: range text ("1 jam 30 menit") → hours;
  - exam pressure: mean of "pressured by exams" and "grades below my target" → 1-10;
  - stress level: mean of too-many-tasks, not-enough-time, late tasks, late-night study × 10 (late tasks and late-night study have 5 levels, up to "more than 5");
  - financial stress: reverse of "enough pocket money" × 10;
  - family expectation: mean of fear of disappointing parents and family demands × 10 ("I can talk to my family about school problems" was dropped after the real data showed it lowered the score's reliability);
  - burnout: mean of its 3 items × 10;
  - **target** anxiety score: mean of the 7 *Psikologis* items (concentration item reversed) × 10, 0-10.
  The target items are **never** used as features (prevents label leakage).
- **Two form versions in one export**: the form was revised, and rows answered before the revision lack the added questions. Every score averages the items a row has, so original rows keep the original formula (e.g. anxiety = 5 items) and revised rows use all items. The quality report checks this pooling: Cronbach's alpha per score, and on revised rows the correlation and mean shift between the original-item and all-item versions of each score.

### Modeling (Data Mining)

A **Random Forest Regressor** (300 trees, max depth 12, `min_samples_leaf=50`, `max_features=0.75`, `max_samples=0.6`) predicts `anxiety_score`. The settings are the best of 25 tried in a random search with 5-fold cross-validation on 50,000 training rows; the notebook's settings (depth 10, `max_features="sqrt"`) stay in use for the small questionnaire data. With real data, seven strategies are compared by repeated 5-fold cross-validation: the Kaggle model as is, an RF on real data only, Kaggle + real combined with real rows weighted 1/10/50, and warm start (adding 200/600 trees grown on real data). The strategy with the lowest MAE is deployed.

### Decision (DSS - SMART)

1. Eight criteria: RF-predicted anxiety, study hours, report grades, sleep hours, physical activity, financial stress, family expectation, burnout.
2. Utility: *benefit* `u = (x - min)/(max - min)`, *cost* `u = (max - x)/(max - min)`; here "benefit" means **higher = needs more attention**. Min/max come from the reference population so a single student can be scored.
3. **Priority score** = mean utility (equal weights) → student ranking.
4. **Alternative score** = Σ weight × utility with each alternative's own weights (profile A/B/C) → the highest-scoring alternative is recommended.

### Evaluation

MAE, RMSE, R² on the test set; comparison with linear regression, a decision tree, gradient boosting and a mean baseline; per-student and population weight sensitivity (±10%/±20%); stability over 100 random perturbations; weight-profile comparison; fairness check by gender; evaluation on new responses via file upload.
