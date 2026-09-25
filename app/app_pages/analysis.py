"""Selected notebook visuals + model evaluation, sensitivity analysis and fairness checks."""
import pandas as pd
import streamlit as st

import ui
from spk import config, i18n, model, plots, smart

L = ui.lang()
METRIC_NAMES = {"cv_mae": "MAE CV", "cv_mae_std": "SD MAE CV", "cv_rmse": "RMSE CV", "cv_r2": "R² CV",
                "test_mae": "MAE uji" if L == "id" else "Test MAE", "test_r2": "R² uji" if L == "id" else "Test R²",
                "holdout_mae": "MAE holdout", "holdout_mse": "MSE holdout", "holdout_rmse": "RMSE holdout",
                "holdout_r2": "R² holdout"}
rf, meta = ui.load_active()
base, base_meta = ui.load_base()
reference = ui.load_reference()
summary = ui.real_summary()
profile = ui.profile_key()

st.title("📊 " + ui.T("an_title"))
st.caption(ui.T("an_population", n=f"{len(reference):,}"))

tab_data, tab_model, tab_smart, tab_sens, tab_fair = st.tabs(
    [ui.T("an_tab_data"), ui.T("an_tab_model"), ui.T("an_tab_smart"), ui.T("an_tab_sens"), ui.T("an_tab_fair")])

result, utility = ui.score(reference[config.FEATURES], profile, True)


@st.cache_data(show_spinner=False)
def base_test_predictions():
    _, X_test, _, y_test = model.split(reference.reset_index(drop=True))
    return X_test, y_test, model.predict(base, X_test)


# ---------------------------------------------------------------- data
with tab_data:
    st.subheader(ui.T("an_kaggle_title"))
    k1, k2, k3 = st.columns(3)
    k1.metric("Rows" if L == "en" else "Baris", f"{len(reference):,}")
    k2.metric(i18n.feature("anxiety_score", L) + " (mean)", f"{reference[config.TARGET].mean():.2f}")
    k3.metric(i18n.feature("age", L), f"{reference['age'].min()}-{reference['age'].max()}")
    crit = reference[config.FEATURES].copy()
    crit["rf_anxiety_score"] = ui.predict_frame(reference[config.FEATURES])
    ui.show(plots.criteria_histograms(crit, L))
    gender = reference["gender"].value_counts()
    st.table(gender.rename(ui.T("count")).to_frame().T)

    st.subheader(ui.T("an_real_title"))
    if not summary:
        st.info(ui.T("an_real_none"))
    else:
        q = summary["quality"]
        r1, r2, r3 = st.columns(3)
        r1.metric("Respons" if L == "id" else "Responses", summary["n_real"])
        r2.metric("Duplikat" if L == "id" else "Duplicates", q.get("duplicate_answer_rows", 0))
        r3.metric("Straight-lining", q.get("straight_lining_rows", 0))
        cols = [c for c in summary["feature_stats"] if not c.startswith("x_")]
        ui.show(plots.quantile_boxes(summary["feature_stats"], cols, L))
        st.caption("Box = Q1-Q3, whiskers = 5%-95%, ▲ = mean. " if L == "en" else
                   "Kotak = Q1-Q3, garis = persentil 5-95, ▲ = rata-rata. ")
        corr = pd.DataFrame(summary["correlation"])
        if config.TARGET in corr:
            target_corr = corr[config.TARGET].drop(config.TARGET).sort_values()
            target_corr.index = [i18n.feature(c, L) if c in i18n.FEATURES else c.removeprefix("x_")
                                 for c in target_corr.index]
            ui.show(plots.matrix_heatmap(target_corr.to_frame(i18n.feature(config.TARGET, L)),
                                         "r (Pearson)", cmap="coolwarm", center=0), compact=True)
        st.table(pd.Series(summary["gender_counts"], name=ui.T("count")).to_frame().T)

# ---------------------------------------------------------------- model
with tab_model:
    st.subheader(ui.T("an_metrics"))
    m = meta["metrics"]
    c = st.columns(4)
    for col, key, label in zip(c, ["mae", "mse", "rmse", "r2"], ["MAE", "MSE", "RMSE", "R²"]):
        col.metric(label, f"{m[key]:.4f}")
    if meta["data_source"] != "kaggle":
        st.caption(ui.T("an_metrics_real", s=meta["strategy"], n=meta["n_real"], note=meta.get("metrics_note", "")))

    X_test, y_test, pred = base_test_predictions()
    st.caption(ui.T("an_base_test"))
    c1, c2 = st.columns(2)
    with c1:
        ui.show(plots.actual_vs_predicted(y_test, pred, L))
    with c2:
        ui.show(plots.residuals(y_test, pred, L))
    ui.show(plots.feature_importance(rf, meta["features"], L), compact=True)

    comparison = ui.model_comparison()
    if comparison:
        st.subheader(ui.T("an_compare"))
        table = pd.DataFrame(comparison).T[["cv_mae", "cv_rmse", "cv_r2", "test_mae", "test_r2"]]
        st.table(table.round(4).rename(columns=METRIC_NAMES))
        ui.show(plots.metric_bars(table["cv_mae"].to_dict(), "algo", "Random Forest (deployed)", L), compact=True)
        st.caption(ui.T("an_compare_note"))

    if summary:
        st.subheader(ui.T("an_strategies"))
        strat = pd.DataFrame(summary["strategies"]).T
        st.table(strat.round(4).rename(columns=METRIC_NAMES))
        ui.show(plots.metric_bars(strat["cv_mae"].to_dict(), "strategies", summary["selected"], L), compact=True)

    with st.expander("Hyperparameters / metadata"):
        st.json({k: v for k, v in meta.items() if k not in ("smart_bounds", "reference_quantiles", "impute_medians")})

# ---------------------------------------------------------------- SMART
with tab_smart:
    crit_table = pd.DataFrame({
        ui.T("criterion"): [i18n.feature(c, L) for c in config.CRITERIA],
        ui.T("type"): [ui.T(config.CRITERIA_TYPE[c]) for c in config.CRITERIA],
        "min": [meta["smart_bounds"][c]["min"] for c in config.CRITERIA],
        "max": [meta["smart_bounds"][c]["max"] for c in config.CRITERIA],
        "w (priority)": [config.PRIORITY_WEIGHTS[c] for c in config.CRITERIA],
    })
    st.table(crit_table.round(3).set_index(ui.T("criterion")))
    ui.show(plots.weights_heatmap(ui.weights(), L), compact=True)
    if profile == "A":
        st.caption(ui.T("an_weights_note"))

    c1, c2 = st.columns(2)
    with c1:
        ui.show(plots.score_histogram(result["smart_score"], L))
    with c2:
        ui.show(plots.utility_radar(result, utility, lang=L))
    ui.show(plots.recommendation_by_alternative(result, L, f" ({ui.profile_label()})"))
    ui.show(plots.frequency_vs_utility(result, result, L), compact=True)
    c3, c4 = st.columns(2)
    with c3:
        ui.show(plots.top_heatmap(result, lang=L))
    with c4:
        ui.show(plots.correlation_heatmap(result, L))

# ---------------------------------------------------------------- sensitivity
with tab_sens:
    weights = ui.weights()
    for pct in (0.1, 0.2):
        s = smart.stability(utility, weights, n=100, pct=pct)
        st.markdown(f"**{ui.T('an_sens_global', pct=int(pct * 100), n=s['iterations'])}**")
        a, b, c = st.columns(3)
        a.metric(ui.T("an_top1"), f"{s['top1_unchanged']:.1%}")
        b.metric(ui.T("an_top3"), f"{s['top3_unchanged']:.1%}")
        c.metric(ui.T("an_top1_min"), f"{s['top1_min']:.1%}")
    ui.show(plots.population_sensitivity(smart.population_sensitivity(utility, weights), L), compact=True)

    st.subheader(ui.T("an_profiles"))
    all_results = {ui.profile_label(k): ui.score(reference[config.FEATURES], k, True)[0] for k in ui.PROFILES}
    fig, table = plots.model_comparison(all_results, L)
    ui.show(fig)
    st.table(table)
    st.caption(ui.T("profile_c_warning"))

# ---------------------------------------------------------------- fairness
with tab_fair:
    st.write(ui.T("an_fair_intro"))
    err = pd.DataFrame({"gender": X_test["gender"].to_numpy(), "abs_err": abs(y_test.to_numpy() - pred),
                        "pred": pred, "actual": y_test.to_numpy()})
    fair = err.groupby("gender").agg(n=("abs_err", "size"), mae=("abs_err", "mean"),
                                     mean_pred=("pred", "mean"), mean_actual=("actual", "mean"))
    c1, c2 = st.columns(2)
    with c1:
        ui.show(plots.fairness_mae(fair, L), compact=True)
    with c2:
        st.table(fair.round(3))
    ui.show(plots.recommendation_mix_by_group(result, reference.loc[result.index, "gender"], L))
    if summary and summary.get("fairness_holdout"):
        st.markdown("**" + ("Data riil (holdout)" if L == "id" else "Real data (holdout)") + "**")
        st.table(pd.DataFrame(summary["fairness_holdout"]).T)

ui.footer()
