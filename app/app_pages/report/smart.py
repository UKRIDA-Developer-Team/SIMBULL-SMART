"""Report chapter 5: SMART on the whole reference population, and how stable it is when weights move."""
import pandas as pd
import streamlit as st

import report
import ui
from spk import config, i18n, plots, smart

L = ui.lang()
T = ui.T
tr = report.tr
rf, meta = ui.load_active()
reference = ui.load_reference()

ch = report.Chapter(5, [("criteria", T("an_criteria")), ("results", T("an_results")),
                        ("stability", tr("Stabilitas global", "Global stability")),
                        ("pop", T("an_sens_pop"))])
result, utility = report.population()

# ---------------------------------------------------------------- criteria and weights
ch.section("criteria", T("an_smart_intro"))
crit_table = pd.DataFrame({
    T("criterion"): [i18n.feature(c, L) for c in config.CRITERIA],
    T("type"): [T(config.CRITERIA_TYPE[c]) for c in config.CRITERIA],
    "min": [meta["smart_bounds"][c]["min"] for c in config.CRITERIA],
    "max": [meta["smart_bounds"][c]["max"] for c in config.CRITERIA],
    "w (priority)": [config.PRIORITY_WEIGHTS[c] for c in config.CRITERIA],
})
ch.table(crit_table.round(3).set_index(T("criterion")),
         tr("Kriteria SMART, jenis, batas normalisasi, dan bobot prioritas.",
            "SMART criteria, type, normalization bounds and priority weights."))
ch.figure(plots.weights_heatmap(ui.weights(), L),
          tr("Bobot kriteria per alternatif.", "Criterion weights per alternative."), compact=True)
st.caption(T("an_weights_note"))

# ---------------------------------------------------------------- population results
ch.section("results", T("an_population", n=f"{len(reference):,}"))
c1, c2 = st.columns(2, gap="medium")
with c1:
    ch.figure(plots.score_histogram(result["smart_score"], L), tr("Sebaran skor prioritas.", "Priority score distribution."))
with c2:
    ch.figure(plots.utility_radar(result, utility, lang=L),
              tr("Profil utilitas rata-rata per rekomendasi.", "Mean utility profile per recommendation."))
ch.figure(plots.recommendation_by_alternative(result, L),
          tr("Jumlah siswa per rekomendasi utama.", "Students per top recommendation."))
ch.figure(plots.frequency_vs_utility(result, result, L),
          tr("Frekuensi rekomendasi vs rata-rata skor.", "Recommendation frequency vs mean score."))
c3, c4 = st.columns(2, gap="medium")
with c3:
    ch.figure(plots.top_heatmap(result, lang=L), tr("Skor alternatif siswa prioritas teratas.",
                                                    "Alternative scores of the top-priority students."))
with c4:
    ch.figure(plots.correlation_heatmap(result, L), tr("Korelasi antar skor alternatif.",
                                                       "Correlation between alternative scores."))

# ---------------------------------------------------------------- stability
ch.section("stability", T("an_sens_intro"))
weights = ui.weights()
rows = {}
for pct in (0.1, 0.2):
    s = smart.stability(utility, weights, n=100, pct=pct)
    rows[f"±{int(pct * 100)}%"] = {T("an_top1"): f"{s['top1_unchanged']:.1%}", T("an_top3"): f"{s['top3_unchanged']:.1%}",
                                   T("an_top1_min"): f"{s['top1_min']:.1%}"}
ch.table(pd.DataFrame(rows).T, tr("Bagian siswa yang rekomendasinya tetap setelah semua bobot diacak (100 iterasi).",
                                  "Share of students whose recommendation stays after all weights are jittered (100 runs)."))

# ---------------------------------------------------------------- per-criterion sensitivity
ch.section("pop")
ch.figure(plots.population_sensitivity(smart.population_sensitivity(utility, weights), L),
          tr("Bagian siswa yang rekomendasinya berubah bila bobot satu kriteria digeser.",
             "Share of students whose recommendation changes when one criterion weight moves."), compact=True)

ch.end()
