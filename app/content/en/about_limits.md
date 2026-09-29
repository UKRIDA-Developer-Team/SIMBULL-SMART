### Limitations

- The Kaggle data comes from university students (ages 17-29), while the target users are high-school students; that is why the model is retrained on real questionnaire data.
- Some questionnaire features are **proxies** (e.g. stress level and financial stress), so they do not mean exactly the same as the Kaggle features.
- Self-report, cross-sectional data: prone to social-desirability bias and shows no cause and effect.
- On the Kaggle data, linear regression is slightly more accurate than the Random Forest (CV MAE 0.768 vs 0.779); RF is kept for continuity with the notebook, robustness to non-linear effects, and feature importance.
- Profile A/B weights come from domain judgment and are not yet validated by experts; profile C always ties and serves only as a baseline.

### Ethics, fairness and privacy

- **Not a diagnosis tool.** Results are indications that help school counselors, not clinical labels.
- **Safety rule.** Students whose predicted anxiety is in the top 10% always get counseling and a referral, whatever SMART ranks first.
- **Privacy.** Nothing is stored; uploads are processed in memory; personal columns are dropped; downloads carry no identity; the repository is private and raw data is never committed; aggregate cells with fewer than 5 people are hidden.
- **Fairness.** Prediction error and the recommendation mix are compared by gender on the Analysis page.
