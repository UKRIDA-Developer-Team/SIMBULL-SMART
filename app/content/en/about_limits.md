### Limitations

- The Kaggle data comes from university students. It is cleaned to the student age band 14-25, but the file only holds ages 17-25, so the base model saw no student aged 14-16. The target users are high-school students (about 15-18); that is why the model is retrained on real questionnaire data.
- **Real data.** On 292 high-school responses (ages 14-25 after cleaning) the Kaggle model fails: holdout R² −0.35, MAE 1.87, because these students are far more anxious (mean 5.0 vs 3.0) and other factors dominate (burnout, exam pressure, family expectation). The deployed model is trained on the real answers only: holdout MAE 1.11, R² 0.44 on 59 students, and cross-validated R² 0.20. Errors of about ±1.1 points are fine for ranking students, not for exact scores.
- Some questionnaire features are **proxies** (e.g. stress level and financial stress), so they do not mean exactly the same as the Kaggle features.
- Self-report, cross-sectional data: prone to social-desirability bias and shows no cause and effect.
- On the Kaggle data, linear regression and gradient boosting are as accurate as the Random Forest (test R² 0.606 and 0.608 vs 0.608; CV MAE 0.760, 0.761 and 0.761); RF is kept for continuity with the notebook, robustness to non-linear effects, and feature importance.
- **R² stops near 0.61 on the Kaggle data.** About 40% of the variance of the anxiety score is random noise that no input column carries: linear regression, gradient boosting and the tuned Random Forest all reach 0.606-0.608 on 138,509 test rows. Removing outliers or extreme rows did not raise it. Only `mental_health_index` would lift it (to about 0.80), but that column is computed from the anxiety score itself (`10 - 0.4 stress - 0.3 anxiety - 0.3 depression`). Using it is label leakage, and the questionnaire has no such item.
- The forest relies almost only on stress level and burnout (96% of its feature importance), because those two columns carry nearly all the signal in the Kaggle data. Other factors still count in SMART as separate criteria.
- Profile A/B weights come from domain judgment and are not yet validated by experts; profile C always ties and serves only as a baseline.

### Ethics, fairness and privacy

- **Not a diagnosis tool.** Results are indications that help school counselors, not clinical labels.
- **Safety rule.** Students whose predicted anxiety is in the top 10% always get counseling and a referral, whatever SMART ranks first.
- **Privacy.** Nothing is stored; uploads are processed in memory; personal columns are dropped; downloads carry no identity; the repository is private and raw data is never committed; aggregate cells with fewer than 5 people are hidden.
- **Fairness.** Prediction error and the recommendation mix are compared by gender on the Analysis page.
