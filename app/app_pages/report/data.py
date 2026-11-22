"""Report chapter 1: the data - the Kaggle reference population and the real questionnaire (aggregates)."""
import pandas as pd
import streamlit as st

import report
import ui
from spk import config, i18n, plots

L = ui.lang()
T = ui.T
tr = report.tr
reference = ui.load_reference()
summary = ui.real_summary()

ch = report.Chapter(1, [("kaggle", T("an_kaggle_title")), ("real", T("an_real_title"))])

# ---------------------------------------------------------------- 1.1 Kaggle
ch.section("kaggle", T("an_data_intro"))
gender = reference["gender"].value_counts()
report.metric_row([
    (tr("Baris", "Rows"), f"{len(reference):,}"),
    (i18n.feature("anxiety_score", L) + tr(" (rata-rata)", " (mean)"), f"{reference[config.TARGET].mean():.2f}"),
    (i18n.feature("age", L), f"{reference['age'].min()}-{reference['age'].max()}"),
    (tr("Fitur model", "Model features"), str(len(config.FEATURES))),
])
st.caption(f"{T('an_gender')}: " + " · ".join(f"{g} {n:,}" for g, n in gender.items()))
crit = reference[config.FEATURES].copy()
crit["rf_anxiety_score"] = ui.predict_frame(reference[config.FEATURES])
ch.figure(plots.criteria_histograms(crit, L),
          tr("Sebaran kriteria SMART pada populasi referensi (termasuk prediksi RF).",
             "Distribution of the SMART criteria in the reference population (including the RF prediction)."))

# ---------------------------------------------------------------- 1.2 real questionnaire
ch.section("real")
if not summary:
    st.info(T("an_real_none"), icon=":material/info:")
else:
    q = summary["quality"]
    report.metric_row([(tr("Respons", "Responses"), str(summary["n_real"])),
                       (tr("Duplikat", "Duplicates"), str(q.get("duplicate_answer_rows", 0))),
                       (tr("Jawaban seragam", "Straight-lining"), str(q.get("straight_lining_rows", 0)),
                        T("an_straight_help"))])
    ch.table(pd.Series(summary["gender_counts"], name=T("count")).to_frame().T,
             tr("Jumlah responden per gender.", "Respondents per gender."))
    cols = [c for c in summary["feature_stats"] if not c.startswith("x_")]
    ch.figure(plots.quantile_boxes(summary["feature_stats"], cols, L),
              tr("Ringkasan jawaban kuesioner. Kotak = Q1-Q3, garis = persentil 5-95, ▲ = rata-rata.",
                 "Questionnaire answers. Box = Q1-Q3, whiskers = 5th-95th percentile, ▲ = mean."))
    corr = pd.DataFrame(summary["correlation"])
    if config.TARGET in corr:
        target_corr = corr[config.TARGET].drop(config.TARGET).sort_values()
        target_corr.index = [i18n.feature(c, L) if c in i18n.FEATURES else c.removeprefix("x_")
                             for c in target_corr.index]
        ch.figure(plots.matrix_heatmap(target_corr.to_frame(i18n.feature(config.TARGET, L)),
                                       "r (Pearson)", cmap=plots.DIVERGING, center=0),
                  tr("Korelasi Pearson setiap fitur dengan skor kecemasan (data riil).",
                     "Pearson correlation of each feature with the anxiety score (real data)."), compact=True)

ch.end()
