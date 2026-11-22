"""Report chapter 3: the SMART calculation worked out for one student, step by step, with real numbers.

Every number here comes from the same recommend.assess() call the app zone uses, so the ranking in
3.7 matches the result page exactly. The tables only lay the intermediate values out.
"""
from decimal import ROUND_HALF_UP, Decimal

import pandas as pd
import streamlit as st

import report
import result_views as rv
import ui
from spk import config, i18n, recommend, smart

L = ui.lang()
T = ui.T
tr = report.tr
N = len(config.CRITERIA)

ch = report.Chapter(3, [(k, T(f"calc_s_{k}")) for k in
                        ("input", "pred", "criteria", "utility", "weights", "scores", "rank", "priority", "sens", "xai")])

# ---------------------------------------------------------------- which student
sources = (["last"] if st.session_state.get("assess_features") else []) + ["high", "low"]
if st.session_state.get("calc_source") not in sources:
    st.session_state["calc_source"] = sources[0]
source = ui.stable_choice(st.segmented_control, T("calc_pick"), sources, "calc_source",
                          lambda s: T(f"calc_src_{s}"))
features = (dict(st.session_state["assess_features"]) if source == "last"
            else ui.example_features(source))
st.caption(T("calc_pick_note", m=T(f"model_short_{ui.model_key()}")))

rf, meta = ui.load_active()
quantiles = ui.reference_quantiles()
a = recommend.assess(rf, meta, features, ui.weights(), quantiles)
bounds = meta["smart_bounds"]


def num(v: float, d: int = 2) -> str:
    return f"{float(v):.{d}f}"


# The worked example in 3.3-3.6 carries every shown number forward rounded to 4 decimals (half up),
# so each cell, column sum and formula can be redone by hand from the numbers on the page. The app
# itself scores with full precision; the two differ by less than 0.001.
STEP = Decimal("0.0001")


def q4(v) -> Decimal:
    return Decimal(repr(float(v))).quantize(STEP, rounding=ROUND_HALF_UP)


def utility_4(c: str) -> tuple[Decimal, Decimal, Decimal, Decimal, Decimal]:
    """(x, min, max, unclipped u, u) for one criterion, from the 4-decimal x, min and max."""
    x, lo, hi = q4(a.criteria[c]), q4(bounds[c]["min"]), q4(bounds[c]["max"])
    if hi == lo:
        return x, lo, hi, Decimal(1), Decimal(1)
    raw = ((x - lo) if config.CRITERIA_TYPE[c] == "benefit" else (hi - x)) / (hi - lo)
    return x, lo, hi, q4(raw), min(max(q4(raw), Decimal(0)), Decimal(1))


# ---------------------------------------------------------------- 3.1 input
ch.section("input", T("calc_input_lead"))
ch.table(pd.DataFrame({
    T("calc_feature"): [i18n.feature(f, L) for f in config.FEATURES],
    T("calc_code"): [f"`{f}`" for f in config.FEATURES],
    T("value"): [num(a.features[f]) if isinstance(a.features[f], float) else str(a.features[f])
                 for f in config.FEATURES],
}).set_index(T("calc_feature")), T("calc_input_cap"))

# ---------------------------------------------------------------- 3.2 RF prediction
ch.section("pred", T("calc_pred_lead"))
st.latex(r"\hat{y} = \frac{1}{B}\sum_{b=1}^{B} T_b(\mathbf{x}) = " + num(a.rf_score))
report.metric_row([(T("res_pred"), f"{a.rf_score:.2f} / 10"),
                   (T("calc_pct"), f"{a.rf_percentile:.0f}"),
                   (T("calc_trees"), str(meta.get("n_estimators_total", meta.get("hyperparameters", {}).get("n_estimators", "-"))))])
st.caption(T("calc_pred_note", group=ui.reference_group()))
st.markdown(f"**{T('cmp_title')}**")
rv.compare_models(features, a)

# ---------------------------------------------------------------- 3.3 criteria
bounds_group = (ui.reference_group("kaggle") if meta.get("smart_bounds_source", "kaggle") == "kaggle"
                else ui.reference_group())
ch.section("criteria", T("calc_criteria_lead", group=bounds_group))
U4 = {c: utility_4(c) for c in config.CRITERIA}
ch.table(pd.DataFrame({
    T("criterion"): [i18n.feature(c, L) for c in config.CRITERIA],
    T("type"): [T(config.CRITERIA_TYPE[c]) for c in config.CRITERIA],
    "x": [str(U4[c][0]) for c in config.CRITERIA],
    "min": [str(U4[c][1]) for c in config.CRITERIA],
    "max": [str(U4[c][2]) for c in config.CRITERIA],
}).set_index(T("criterion")), T("calc_criteria_cap"))

# ---------------------------------------------------------------- 3.4 utility
ch.section("utility", T("calc_utility_lead"))
c1, c2 = st.columns(2, gap="medium")
with c1:
    st.caption("Benefit")
    st.latex(r"u_i = \frac{x_i - \min_i}{\max_i - \min_i}")
with c2:
    st.caption("Cost")
    st.latex(r"u_i = \frac{\max_i - x_i}{\max_i - \min_i}")
rows = []
for c in config.CRITERIA:
    x, lo, hi, raw, u = U4[c]
    expr = f"({x} − {lo}) / ({hi} − {lo})" if config.CRITERIA_TYPE[c] == "benefit" else f"({hi} − {x}) / ({hi} − {lo})"
    rows.append({T("criterion"): i18n.feature(c, L), T("calc_subst"): f"{expr} = {raw}",
                 "u": str(u) + ("" if raw == u else f" ({T('calc_clipped')})")})
ch.table(pd.DataFrame(rows).set_index(T("criterion")), T("calc_utility_cap"),
         note=T("calc_utility_note") + " " + T("calc_round_note"))

# ---------------------------------------------------------------- 3.5 weights
ch.section("weights", T("calc_weights_lead"))
W = smart.weight_matrix(ui.weights())
W4 = W.map(q4)
w_table = W4.copy()
w_table.loc["Σ"] = W4.sum()
w_table.index = [i18n.feature(c, L) if c in config.CRITERIA else c for c in w_table.index]
w_table.columns = [i18n.alt(x, L) for x in w_table.columns]
ch.table(w_table.map(str), T("calc_weights_cap"))

# ---------------------------------------------------------------- 3.6 alternative scores
ch.section("scores", T("calc_scores_lead"))
st.latex(r"S_j = \sum_{i=1}^{%d} w_{ij}\,u_i" % N)
contrib = pd.DataFrame({alt: [q4(W4.loc[c, alt] * U4[c][4]) for c in config.CRITERIA] for alt in config.ALTERNATIVES},
                       index=config.CRITERIA)                       # criteria x alternatives, w*u
c_table = contrib.copy()
c_table.loc[T("calc_score_row")] = contrib.sum()
c_table.index = [i18n.feature(c, L) if c in config.CRITERIA else c for c in c_table.index]
c_table.columns = [i18n.alt(x, L) for x in c_table.columns]
best_col = i18n.alt(a.best, L)
ch.caption("tab", T("calc_scores_cap"))
st.table(c_table.map(str).style.apply(
    lambda col: ["background-color: #E6F0ED; font-weight: 600" if col.name == best_col else "" for _ in col], axis=0))
terms = [r"%s \cdot %s" % (W4.loc[c, a.best], U4[c][4]) for c in config.CRITERIA if W.loc[c, a.best] > 0]
lines = [" + ".join(terms[i:i + 4]) for i in range(0, len(terms), 4)]      # four terms per line
st.latex(r"\begin{aligned} S_{\text{%s}} &= %s \\ &= %s \end{aligned}" % (
    i18n.alt(a.best, L), r" \\ &\quad + ".join(lines), contrib[a.best].sum()))
st.caption(T("calc_scores_note", alt=i18n.alt(a.best, L), s=num(a.ranking.iloc[0], 4)))

# ---------------------------------------------------------------- 3.7 ranking
ch.section("rank", T("calc_rank_lead"))
top = float(a.ranking.iloc[0])
ch.table(pd.DataFrame({
    T("rank"): range(1, len(a.ranking) + 1),
    T("calc_alt"): [i18n.alt(x, L) for x in a.ranking.index],
    "S": [num(s, 3) for s in a.ranking],
    T("calc_gap"): ["–"] + [num(s - top, 3) for s in a.ranking.iloc[1:]],
}).set_index(T("rank")), T("calc_rank_cap"))
st.html(rv.ranking_bars(a))
gap = top - float(a.ranking.iloc[1])
st.caption(T("calc_rank_note", alt=i18n.alt(a.best, L), gap=gap))

# ---------------------------------------------------------------- 3.8 priority and safety rule
ch.section("priority", T("calc_priority_lead"))
st.latex(r"P = \sum_{i=1}^{%d} \tfrac{1}{%d}\,u_i = %s" % (N, N, num(a.priority, 3)))
cutoff = recommend.cutoff(quantiles["rf_anxiety_score"])
report.metric_row([(T("res_priority"), num(a.priority, 3)),
                   (T("calc_pct"), f"{a.priority_percentile:.0f}"),
                   (T("calc_cutoff", p=config.SAFETY_PERCENTILE), num(cutoff))])
st.latex(r"\hat{y} = %s \;%s\; Q_{%d} = %s" % (num(a.rf_score), r"\ge" if a.safety else "<",
                                                config.SAFETY_PERCENTILE, num(cutoff)))
if a.safety:
    st.error(T("calc_safety_on"), icon=":material/priority_high:")
else:
    st.success(T("calc_safety_off"), icon=":material/check_circle:")

# ---------------------------------------------------------------- 3.9 sensitivity for this student
ch.section("sens")
ch.caption("tab", T("calc_sens_cap"))
rv.sensitivity_grid(a)

# ---------------------------------------------------------------- 3.10 explanation for this student
ch.section("xai")
rv.xai_panel(a, features, "calc")

ch.end()
