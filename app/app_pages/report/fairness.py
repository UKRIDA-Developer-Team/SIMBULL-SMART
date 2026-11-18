"""Report chapter 6: fairness - model error and recommendation mix by gender."""
import pandas as pd
import streamlit as st

import report
import ui
from spk import plots

L = ui.lang()
T = ui.T
tr = report.tr
reference = ui.load_reference()
summary = ui.real_summary()

sections = [("mae", tr("Galat model per gender", "Model error by gender")),
            ("mix", tr("Rekomendasi per gender", "Recommendations by gender"))]
if summary and summary.get("fairness_holdout"):
    sections.append(("real", tr("Data riil (holdout)", "Real data (holdout)")))
ch = report.Chapter(6, sections)

X_test, y_test, pred = report.base_test_predictions()
result, _ = report.population()

ch.section("mae", T("an_fair_intro"))
err = pd.DataFrame({"gender": X_test["gender"].to_numpy(), "abs_err": abs(y_test.to_numpy() - pred),
                    "pred": pred, "actual": y_test.to_numpy()})
fair = err.groupby("gender").agg(n=("abs_err", "size"), mae=("abs_err", "mean"),
                                 mean_pred=("pred", "mean"), mean_actual=("actual", "mean"))
c1, c2 = st.columns([1.2, 1], gap="medium", vertical_alignment="center")
with c1:
    ch.figure(plots.fairness_mae(fair, L), tr("MAE per gender (data uji Kaggle).", "MAE by gender (Kaggle test set)."))
with c2:
    ch.table(fair.round(3), tr("Galat dan rata-rata per gender.", "Error and means by gender."))

ch.section("mix")
ch.figure(plots.recommendation_mix_by_group(result, reference.loc[result.index, "gender"], L),
          tr("Komposisi rekomendasi utama per gender.", "Top-recommendation mix by gender."))

if summary and summary.get("fairness_holdout"):
    ch.section("real")
    ch.table(pd.DataFrame(summary["fairness_holdout"]).T,
             tr("Galat model riil per gender pada holdout siswa riil.", "Real-model error by gender on the real holdout."))

ch.end()
