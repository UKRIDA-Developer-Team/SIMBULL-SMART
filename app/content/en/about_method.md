### Data

| Source | Content | Role |
|---|---|---|
| Kaggle *Student Mental Health & Burnout* (1M rows) | 2% random sample = 20,000 rows, 20 columns | Pretraining; reference population for analysis |
| Google Form questionnaire for high-school students | ~50 questions (academics, sleep, social media, family, exercise, fatigue, peers, psychological items, eating habits) | Retraining on real data; testing on new data |

The questionnaire data is **confidential**: the raw file never enters the repository, personal columns (timestamp, birth date, school, friend's name) are dropped right after age is computed, and the app only ships aggregate summaries.

### Data preparation

- **Kaggle**: no missing values; `gender` has a fixed code (`Female=0, Male=1, Other=2`, the same as the notebook's LabelEncoder); a 50% sample (10,000 rows) is split 80/20 into train/test (`random_state=42`).
- **Google Form → 11 model features** (`spk/gform.py`): text answers become numbers, then are scaled to the Kaggle feature ranges:
  - study and sleep hours: range text ("1 jam 30 menit") → hours;
  - exam pressure: Likert 1-5 → 1-10;
  - stress level: normalized mean of too-many-tasks, not-enough-time, late tasks, late-night study × 10;
  - financial stress: reverse of "enough pocket money" × 10;
  - family expectation and burnout: mean of their items × 10;
  - **target** anxiety score: sum of the 5 *Psikologis* items (concentration item reversed), 0-20 → 0-10.
  The target items are **never** used as features (prevents label leakage).

### Modeling (Data Mining)

A **Random Forest Regressor** (200 trees, max depth 10, `min_samples_leaf=2`, `max_features="sqrt"`) predicts `anxiety_score`. With real data, seven strategies are compared by repeated 5-fold cross-validation: the Kaggle model as is, an RF on real data only, Kaggle + real combined with real rows weighted 1/10/50, and warm start (adding 200/600 trees grown on real data). The strategy with the lowest MAE is deployed.

### Decision (DSS - SMART)

1. Eight criteria: RF-predicted anxiety, study hours, report grades, sleep hours, physical activity, financial stress, family expectation, burnout.
2. Utility: *benefit* `u = (x - min)/(max - min)`, *cost* `u = (max - x)/(max - min)`; here "benefit" means **higher = needs more attention**. Min/max come from the reference population so a single student can be scored.
3. **Priority score** = mean utility (equal weights) → student ranking.
4. **Alternative score** = Σ weight × utility with each alternative's own weights (profile A/B/C) → the highest-scoring alternative is recommended.

### Evaluation

MAE, RMSE, R² on the test set; comparison with linear regression, a decision tree, gradient boosting and a mean baseline; per-student and population weight sensitivity (±10%/±20%); stability over 100 random perturbations; weight-profile comparison; fairness check by gender; evaluation on new responses via file upload.
