"""Report chapter 2: the Random Forest model - metrics, iterations, test-set fit, algorithms, strategies."""
import pandas as pd
import streamlit as st

import report
import ui
from spk import plots

L = ui.lang()
T = ui.T
tr = report.tr
METRIC_NAMES = {"cv_mae": "MAE CV", "cv_mae_std": "SD MAE CV", "cv_rmse": "RMSE CV", "cv_r2": "R² CV",
                "test_mae": tr("MAE uji", "Test MAE"), "test_r2": tr("R² uji", "Test R²"),
                "holdout_mae": "MAE holdout", "holdout_mse": "MSE holdout", "holdout_rmse": "RMSE holdout",
                "holdout_r2": "R² holdout"}
rf, meta = ui.load_active()
_, base_meta = ui.load_base()
summary = ui.real_summary()
comparison = ui.model_comparison()

sections = [("metrics", T("an_metrics"))]
if summary and summary.get("strategies"):
    sections.append(("iter", T("an_iter_title")))
sections.append(("fit", tr("Uji pada data Kaggle", "Fit on the Kaggle test set")))
if comparison:
    sections.append(("algo", T("an_compare")))
if summary:
    sections.append(("strat", T("an_strategies")))
sections.append(("meta", T("an_metadata")))
ch = report.Chapter(2, sections)

# ---------------------------------------------------------------- metrics
ch.section("metrics", T("an_model_intro"))
m = meta["metrics"]
report.metric_row([(label, f"{m[key]:.4f}") for key, label in
                   zip(["mae", "mse", "rmse", "r2"], ["MAE", "MSE", "RMSE", "R²"])])
if meta["data_source"] != "kaggle":
    holdout = (summary or {}).get("holdout_rows", 0)
    note = (T("an_metrics_holdout", h=holdout, n=meta["n_real"]) if meta.get("metrics_note", "").startswith("holdout")
            else T("an_metrics_cv"))
    st.caption(T("an_metrics_real", s=ui.strategy_label(meta["strategy"]), n=meta["n_real"], note=note))

# ---------------------------------------------------------------- iterations
if summary and summary.get("strategies"):
    ch.section("iter", T("an_iter_lead"))
    s0, s1 = summary["strategies"]["S0_kaggle"], summary["strategies"][summary["selected"]]
    dk = T("an_iter_data_k", n=f"{base_meta.get('rows', {}).get('test', 0):,}")
    dr = T("an_iter_data_r", n=summary.get("holdout_rows", 0))
    iters = pd.DataFrame({
        T("model_opt_kaggle"): {f"MAE · {dk}": base_meta["metrics"]["mae"], f"R² · {dk}": base_meta["metrics"]["r2"],
                                f"MAE · {dr}": s0.get("holdout_mae"), f"R² · {dr}": s0.get("holdout_r2")},
        T("model_opt_real"): {f"MAE · {dk}": None, f"R² · {dk}": None,
                              f"MAE · {dr}": s1.get("holdout_mae"), f"R² · {dr}": s1.get("holdout_r2")},
    }).T
    ch.table(iters.map(lambda v: "–" if v is None or pd.isna(v) else f"{v:.3f}"),
             tr("Iterasi model pada data uji Kaggle dan holdout siswa riil.",
                "Model iterations on the Kaggle test set and the real-student holdout."))

# ---------------------------------------------------------------- fit on the Kaggle test set
X_test, y_test, pred = report.base_test_predictions()
ch.section("fit", T("an_base_test", n=f"{len(X_test):,}",
                    total=f"{base_meta.get('rows', {}).get('test', len(X_test)):,}"))
c1, c2 = st.columns(2, gap="medium")
with c1:
    ch.figure(plots.actual_vs_predicted(y_test, pred, L), tr("Nilai aktual vs prediksi.", "Actual vs predicted."))
with c2:
    ch.figure(plots.residuals(y_test, pred, L), tr("Sebaran residual.", "Residuals."))
ch.figure(plots.feature_importance(rf, meta["features"], L),
          tr("Kepentingan fitur (Gini) model aktif.", "Feature importance (Gini) of the active model."))

# ---------------------------------------------------------------- algorithms
if comparison:
    ch.section("algo", T("an_compare_note"))
    table = pd.DataFrame(comparison).T[["cv_mae", "cv_rmse", "cv_r2", "test_mae", "test_r2"]]
    ch.table(table.round(4).rename(columns=METRIC_NAMES),
             tr("Perbandingan algoritma (validasi silang 5-fold dan data uji).",
                "Algorithm comparison (5-fold cross-validation and test set)."))
    ch.figure(plots.metric_bars(table["cv_mae"].to_dict(), "algo", "Random Forest (deployed)", L),
              tr("MAE validasi silang per algoritma.", "Cross-validated MAE per algorithm."), compact=True)

# ---------------------------------------------------------------- strategies
if summary:
    ch.section("strat")
    strat = pd.DataFrame(summary["strategies"]).T
    ch.table(strat.round(4).rename(columns=METRIC_NAMES),
             tr("Strategi pelatihan ulang dengan data riil.", "Retraining strategies with the real data."))
    ch.figure(plots.metric_bars(strat["cv_mae"].to_dict(), "strategies", summary["selected"], L),
              tr("MAE validasi silang per strategi.", "Cross-validated MAE per strategy."), compact=True)

# ---------------------------------------------------------------- metadata
ch.section("meta")
st.json({k: v for k, v in meta.items() if k not in ("smart_bounds", "reference_quantiles", "impute_medians")},
        expanded=False)

ch.end()
