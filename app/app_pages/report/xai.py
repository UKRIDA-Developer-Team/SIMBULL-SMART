"""Report chapter 4: global explainable AI - importance (Gini vs permutation), partial dependence, methods."""
import pandas as pd
import streamlit as st

import report
import ui
from spk import i18n, plots, xai

L = ui.lang()
T = ui.T
tr = report.tr
rf, meta = ui.load_active()

ch = report.Chapter(4, [("imp", T("an_xai_imp")), ("pdp", T("an_xai_pdp")), ("methods", T("an_xai_methods"))])

# ---------------------------------------------------------------- importance
ch.section("imp", T("an_xai_intro"))
perm = ui.permutation_importance()
gini = pd.Series(rf.feature_importances_, index=meta["features"])
ch.figure(plots.importance_comparison(gini, perm, L),
          tr("Kepentingan fitur: Gini (dari pohon) vs permutasi (dari data uji).",
             "Feature importance: Gini (from the trees) vs permutation (on test data)."))
top_perm = list(perm.index[:2])
top_gini = list(gini.sort_values(ascending=False).index[:2])
if set(top_perm) == set(top_gini):
    st.caption(T("an_xai_imp_note", a=i18n.feature(top_perm[0], L), b=i18n.feature(top_perm[1], L)))
gap = [f for f in gini.index if gini[f] >= 0.02 and perm.loc[f, "mean"] < 0.005]
if gap:
    st.caption(T("an_xai_imp_gap", f=", ".join(i18n.feature(f, L) for f in gap)))

# ---------------------------------------------------------------- partial dependence
ch.section("pdp", T("an_xai_pdp_note"))
default = [f for f in perm.index if f in xai.ACTIONABLE][:4]
picked = st.multiselect(T("an_xai_pdp_pick"), list(xai.ACTIONABLE), default=default, max_selections=4,
                        format_func=lambda f: i18n.feature(f, L), key=f"pdp_pick_{L}")
if picked:
    ch.figure(plots.pdp_grid(report.pdp_curves(tuple(picked)), L),
              tr("Partial dependence: rata-rata prediksi saat satu fitur diubah.",
                 "Partial dependence: mean prediction as one feature changes."))

# ---------------------------------------------------------------- methods
ch.section("methods")
st.markdown(ui.content("xai_methods"))

ch.end()
