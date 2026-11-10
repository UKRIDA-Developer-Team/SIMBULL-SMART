"""Selected notebook visuals + model evaluation, sensitivity analysis and fairness checks."""
import pandas as pd
import streamlit as st

import ui
from spk import config, i18n, model, plots, smart, xai

L = ui.lang()
T = ui.T
METRIC_NAMES = {"cv_mae": "MAE CV", "cv_mae_std": "SD MAE CV", "cv_rmse": "RMSE CV", "cv_r2": "R² CV",
                "test_mae": "MAE uji" if L == "id" else "Test MAE", "test_r2": "R² uji" if L == "id" else "Test R²",
                "holdout_mae": "MAE holdout", "holdout_mse": "MSE holdout", "holdout_rmse": "RMSE holdout",
                "holdout_r2": "R² holdout"}
rf, meta = ui.load_active()
base, base_meta = ui.load_base()
reference = ui.load_reference()
summary = ui.real_summary()

ui.page_header(T("an_title"), T("an_lead"))
with st.container(horizontal=True, vertical_alignment="center"):
    st.caption(T("an_population", n=f"{len(reference):,}"))
    st.space("stretch")
    ui.profile_picker()
ui.profile_warning()
profile = ui.profile_key()

tab_data, tab_model, tab_xai, tab_smart, tab_sens, tab_fair = st.tabs(
    [T("an_tab_data"), T("an_tab_model"), T("an_tab_xai"), T("an_tab_smart"), T("an_tab_sens"), T("an_tab_fair")])

result, utility = ui.score(reference[config.FEATURES], profile, True)


@st.cache_data(show_spinner=False)
def base_test_predictions():
    X_test, y_test = ui.kaggle_test_set()
    return X_test, y_test, model.predict(base, X_test)


@st.cache_data(show_spinner=False)
def pdp_curves(features: tuple):
    X_test, _, _ = base_test_predictions()
    sample = X_test.sample(min(400, len(X_test)), random_state=config.RANDOM_STATE)
    return [xai.partial_dependence(rf, sample, f) for f in features]


def chart(fig, key: str, compact: bool = False):
    """A chart on its own white card."""
    with st.container(border=True, key=f"card_{key}"):
        ui.show(fig, compact=compact)


# ---------------------------------------------------------------- data
with tab_data:
    st.caption(T("an_data_intro"))
    ui.section(T("an_kaggle_title"))
    gender = reference["gender"].value_counts()
    k = st.columns(4, gap="small")
    k[0].metric("Baris" if L == "id" else "Rows", f"{len(reference):,}", border=True)
    k[1].metric(i18n.feature("anxiety_score", L) + (" (rata-rata)" if L == "id" else " (mean)"),
                f"{reference[config.TARGET].mean():.2f}", border=True)
    k[2].metric(i18n.feature("age", L), f"{reference['age'].min()}-{reference['age'].max()}", border=True)
    k[3].metric("Fitur model" if L == "id" else "Model features", len(config.FEATURES), border=True)
    st.caption(f"{T('an_gender')}: " + " · ".join(f"{g} {n:,}" for g, n in gender.items()))
    crit = reference[config.FEATURES].copy()
    crit["rf_anxiety_score"] = ui.predict_frame(reference[config.FEATURES])
    chart(plots.criteria_histograms(crit, L), "hists")

    st.space("small")
    ui.section(T("an_real_title"))
    if not summary:
        st.info(T("an_real_none"), icon=":material/info:")
    else:
        q = summary["quality"]
        r = st.columns(3, gap="small")
        r[0].metric("Respons" if L == "id" else "Responses", summary["n_real"], border=True)
        r[1].metric("Duplikat" if L == "id" else "Duplicates", q.get("duplicate_answer_rows", 0), border=True)
        r[2].metric("Straight-lining", q.get("straight_lining_rows", 0), border=True)
        cols = [c for c in summary["feature_stats"] if not c.startswith("x_")]
        chart(plots.quantile_boxes(summary["feature_stats"], cols, L), "boxes")
        st.caption("Box = Q1-Q3, whiskers = 5%-95%, ▲ = mean. " if L == "en" else
                   "Kotak = Q1-Q3, garis = persentil 5-95, ▲ = rata-rata. ")
        corr = pd.DataFrame(summary["correlation"])
        if config.TARGET in corr:
            target_corr = corr[config.TARGET].drop(config.TARGET).sort_values()
            target_corr.index = [i18n.feature(c, L) if c in i18n.FEATURES else c.removeprefix("x_")
                                 for c in target_corr.index]
            chart(plots.matrix_heatmap(target_corr.to_frame(i18n.feature(config.TARGET, L)),
                                       "r (Pearson)", cmap=plots.DIVERGING, center=0), "real_corr", compact=True)
        st.table(pd.Series(summary["gender_counts"], name=T("count")).to_frame().T)

# ---------------------------------------------------------------- model
with tab_model:
    st.caption(T("an_model_intro"))
    ui.section(T("an_metrics"))
    m = meta["metrics"]
    c = st.columns(4, gap="small")
    for col, key, label in zip(c, ["mae", "mse", "rmse", "r2"], ["MAE", "MSE", "RMSE", "R²"]):
        col.metric(label, f"{m[key]:.4f}", border=True)
    if meta["data_source"] != "kaggle":
        st.caption(T("an_metrics_real", s=meta["strategy"], n=meta["n_real"], note=meta.get("metrics_note", "")))

    if summary and summary.get("strategies"):
        st.space("small")
        ui.section(T("an_iter_title"), T("an_iter_lead"))
        s0, s1 = summary["strategies"]["S0_kaggle"], summary["strategies"][summary["selected"]]
        dk = T("an_iter_data_k", n=f"{base_meta.get('rows', {}).get('test', 0):,}")
        dr = T("an_iter_data_r", n=summary.get("holdout_rows", 0))
        iters = pd.DataFrame({
            T("model_opt_kaggle"): {f"MAE · {dk}": base_meta["metrics"]["mae"], f"R² · {dk}": base_meta["metrics"]["r2"],
                                    f"MAE · {dr}": s0.get("holdout_mae"), f"R² · {dr}": s0.get("holdout_r2")},
            T("model_opt_real"): {f"MAE · {dk}": None, f"R² · {dk}": None,
                                  f"MAE · {dr}": s1.get("holdout_mae"), f"R² · {dr}": s1.get("holdout_r2")},
        }).T
        st.table(iters.map(lambda v: "–" if v is None or pd.isna(v) else f"{v:.3f}"))

    X_test, y_test, pred = base_test_predictions()
    st.caption(T("an_base_test", n=f"{len(X_test):,}", total=f"{base_meta.get('rows', {}).get('test', len(X_test)):,}"))
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        chart(plots.actual_vs_predicted(y_test, pred, L), "avp")
    with c2:
        chart(plots.residuals(y_test, pred, L), "resid")
    chart(plots.feature_importance(rf, meta["features"], L), "importance")

    comparison = ui.model_comparison()
    if comparison:
        st.space("small")
        ui.section(T("an_compare"), T("an_compare_note"))
        table = pd.DataFrame(comparison).T[["cv_mae", "cv_rmse", "cv_r2", "test_mae", "test_r2"]]
        c1, c2 = st.columns([1.1, 1], gap="medium")
        with c1:
            st.table(table.round(4).rename(columns=METRIC_NAMES))
        with c2:
            chart(plots.metric_bars(table["cv_mae"].to_dict(), "algo", "Random Forest (deployed)", L), "algo")

    if summary:
        st.space("small")
        ui.section(T("an_strategies"))
        strat = pd.DataFrame(summary["strategies"]).T
        st.table(strat.round(4).rename(columns=METRIC_NAMES))
        chart(plots.metric_bars(strat["cv_mae"].to_dict(), "strategies", summary["selected"], L), "strategies")

    with st.expander(T("an_metadata"), icon=":material/data_object:"):
        st.json({k: v for k, v in meta.items() if k not in ("smart_bounds", "reference_quantiles", "impute_medians")})

# ---------------------------------------------------------------- explainable AI (global)
with tab_xai:
    st.caption(T("an_xai_intro"))
    ui.section(T("an_xai_imp"))
    perm = ui.permutation_importance()
    gini = pd.Series(rf.feature_importances_, index=meta["features"])
    chart(plots.importance_comparison(gini, perm, L), "xai_imp")
    top_perm = list(perm.index[:2])
    top_gini = list(gini.sort_values(ascending=False).index[:2])
    if set(top_perm) == set(top_gini):
        st.caption(T("an_xai_imp_note", a=i18n.feature(top_perm[0], L), b=i18n.feature(top_perm[1], L)))
    gap = [f for f in gini.index if gini[f] >= 0.02 and perm.loc[f, "mean"] < 0.005]
    if gap:
        st.caption(T("an_xai_imp_gap", f=", ".join(i18n.feature(f, L) for f in gap)))

    st.space("small")
    ui.section(T("an_xai_pdp"))
    default = [f for f in perm.index if f in xai.ACTIONABLE][:4]
    picked = st.multiselect(T("an_xai_pdp_pick"), list(xai.ACTIONABLE), default=default, max_selections=4,
                            format_func=lambda f: i18n.feature(f, L), key=f"pdp_pick_{L}")
    if picked:
        chart(plots.pdp_grid(pdp_curves(tuple(picked)), L), "xai_pdp")
    st.caption(T("an_xai_pdp_note"))

    with st.expander(T("an_xai_methods"), icon=":material/psychology:"):
        st.markdown(ui.content("xai_methods"))

# ---------------------------------------------------------------- SMART
with tab_smart:
    st.caption(T("an_smart_intro"))
    ui.section(T("an_criteria"))
    crit_table = pd.DataFrame({
        T("criterion"): [i18n.feature(c, L) for c in config.CRITERIA],
        T("type"): [T(config.CRITERIA_TYPE[c]) for c in config.CRITERIA],
        "min": [meta["smart_bounds"][c]["min"] for c in config.CRITERIA],
        "max": [meta["smart_bounds"][c]["max"] for c in config.CRITERIA],
        "w (priority)": [config.PRIORITY_WEIGHTS[c] for c in config.CRITERIA],
    })
    c1, c2 = st.columns([1.15, 1], gap="medium")
    with c1:
        st.table(crit_table.round(3).set_index(T("criterion")))
    with c2:
        chart(plots.weights_heatmap(ui.weights(), L), "weights")
        if profile == "A":
            st.caption(T("an_weights_note"))

    st.space("small")
    ui.section(T("an_results"))
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        chart(plots.score_histogram(result["smart_score"], L), "smart_hist")
    with c2:
        chart(plots.utility_radar(result, utility, lang=L), "radar")
    chart(plots.recommendation_by_alternative(result, L, f" ({ui.profile_label()})"), "by_alt")
    chart(plots.frequency_vs_utility(result, result, L), "freq")
    c3, c4 = st.columns(2, gap="medium")
    with c3:
        chart(plots.top_heatmap(result, lang=L), "top_heat")
    with c4:
        chart(plots.correlation_heatmap(result, L), "corr")

# ---------------------------------------------------------------- sensitivity
with tab_sens:
    st.caption(T("an_sens_intro"))
    weights = ui.weights()
    for pct in (0.1, 0.2):
        s = smart.stability(utility, weights, n=100, pct=pct)
        ui.section(T("an_sens_global", pct=int(pct * 100), n=s["iterations"]))
        a, b, c = st.columns(3, gap="small")
        a.metric(T("an_top1"), f"{s['top1_unchanged']:.1%}", border=True)
        b.metric(T("an_top3"), f"{s['top3_unchanged']:.1%}", border=True)
        c.metric(T("an_top1_min"), f"{s['top1_min']:.1%}", border=True)
    st.space("small")
    ui.section(T("an_sens_pop"))
    chart(plots.population_sensitivity(smart.population_sensitivity(utility, weights), L), "sens_pop", compact=True)

    st.space("small")
    ui.section(T("an_profiles"))
    all_results = {ui.profile_label(k): ui.score(reference[config.FEATURES], k, True)[0] for k in ui.PROFILES}
    fig, table = plots.model_comparison(all_results, L)
    c1, c2 = st.columns([1.5, 1], gap="medium")
    with c1:
        chart(fig, "profiles")
    with c2:
        st.table(table)
        st.caption(T("profile_c_warning"))

# ---------------------------------------------------------------- fairness
with tab_fair:
    st.caption(T("an_fair_intro"))
    err = pd.DataFrame({"gender": X_test["gender"].to_numpy(), "abs_err": abs(y_test.to_numpy() - pred),
                        "pred": pred, "actual": y_test.to_numpy()})
    fair = err.groupby("gender").agg(n=("abs_err", "size"), mae=("abs_err", "mean"),
                                     mean_pred=("pred", "mean"), mean_actual=("actual", "mean"))
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        chart(plots.fairness_mae(fair, L), "fair_mae")
    with c2:
        st.table(fair.round(3))
    chart(plots.recommendation_mix_by_group(result, reference.loc[result.index, "gender"], L), "fair_mix")
    if summary and summary.get("fairness_holdout"):
        ui.section("Data riil (holdout)" if L == "id" else "Real data (holdout)")
        st.table(pd.DataFrame(summary["fairness_holdout"]).T)

ui.footer()
