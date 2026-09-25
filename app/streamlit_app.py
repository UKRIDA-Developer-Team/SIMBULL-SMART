"""SPK SMART - student anxiety priority & intervention recommendation.

Run locally:  streamlit run streamlit_app.py   (from the app/ folder)
"""
import pandas as pd
import streamlit as st

from spk import config, data, model, plots, smart

st.set_page_config(page_title="SPK SMART - Anxiety", layout="wide")


# ---------- cached loaders ----------
@st.cache_resource
def load_model():
    return model.load()


@st.cache_data
def load_reference():
    return data.load_dataset()


@st.cache_data
def score_batch(df: pd.DataFrame, profile: str, use_reference_bounds: bool, _bounds: dict):
    rf, _ = load_model()
    criteria_df = df.copy()
    criteria_df["rf_anxiety_score"] = model.predict(rf, df)
    bounds = _bounds if use_reference_bounds else None
    result, utility = smart.run(criteria_df[config.CRITERIA], config.WEIGHT_PROFILES[profile], bounds)
    result = pd.concat([df, criteria_df[["rf_anxiety_score"]], result], axis=1)
    return result.sort_values("smart_score", ascending=False), utility


if not config.MODEL_PATH.exists() or not config.DATA_PATH.exists():
    st.error("Model or dataset missing. Run `python scripts/train.py` first.")
    st.stop()

rf, meta = load_model()
bounds = meta["smart_bounds"]
reference = load_reference()

st.sidebar.title("SPK SMART")
profile = st.sidebar.selectbox("Weight profile", list(config.WEIGHT_PROFILES))
if profile.startswith("C"):
    st.sidebar.warning("Profile C gives equal weights: every alternative ties, so the result is always 'Sleep'.")

tab_single, tab_batch, tab_model = st.tabs(["Single student", "Batch ranking", "Model"])

# ---------- single student ----------
with tab_single:
    st.header("Single student assessment")
    with st.form("student"):
        c1, c2, c3 = st.columns(3)
        values = {}
        with c1:
            lo, hi, default = config.INPUT_RANGES["age"]
            values["age"] = st.number_input("age", lo, hi, default)
            values["gender"] = st.selectbox("gender", list(config.GENDER_MAP))
        numeric = [f for f in config.FEATURES if f not in ("age", "gender")]
        for i, feat in enumerate(numeric):
            lo, hi, default = config.INPUT_RANGES[feat]
            with (c1, c2, c3)[(i + 2) % 3]:
                values[feat] = st.slider(feat, float(lo), float(hi), float(default), 0.1)
        submitted = st.form_submit_button("Assess")

    if submitted:
        student = pd.DataFrame([values])
        student["rf_anxiety_score"] = model.predict(rf, student)
        result, utility = smart.run(student[config.CRITERIA], config.WEIGHT_PROFILES[profile], bounds)
        row = result.iloc[0]

        ref_scores, _ = score_batch(reference, profile, True, bounds)
        percentile = (ref_scores["smart_score"] < row["smart_score"]).mean() * 100

        m1, m2, m3 = st.columns(3)
        m1.metric("Predicted anxiety_score", f"{student['rf_anxiety_score'].iloc[0]:.2f}")
        m2.metric("SMART priority score", f"{row['smart_score']:.3f}",
                  help=f"Higher than {percentile:.1f}% of the reference students")
        m3.metric("Recommendation", row["Best_Recommendation"], f"{row['Recommendation_Score']:.3f}")
        st.caption(f"Priority percentile vs {len(reference):,} reference students: {percentile:.1f}%")

        st.pyplot(plots.single_student_bars(row[config.ALTERNATIVES].astype(float)))
        with st.expander("Utility per criterion"):
            st.dataframe(utility.T.rename(columns={0: "utility"}))

# ---------- batch ----------
with tab_batch:
    st.header("Batch ranking")
    upload = st.file_uploader("CSV with the model feature columns (optional)", type="csv")
    if upload:
        df = pd.read_csv(upload)
        missing = data.validate_columns(df)
        if missing:
            st.error(f"Missing columns: {missing}")
            st.stop()
    else:
        df = reference
        st.caption(f"Using bundled dataset ({len(df):,} rows).")

    if "student_id" not in df.columns:
        df = df.assign(student_id=[f"STU{i + 1:05d}" for i in range(len(df))])
    df = df.set_index("student_id")

    use_ref = st.checkbox(
        "Normalize with reference bounds (off = min/max of this batch, as in the notebook)",
        value=bool(upload),
    )
    result, utility = score_batch(df, profile, use_ref, bounds)

    top_n = st.slider("Show top N", 10, 500, 20, 10)
    show_cols = ["rank", "smart_score", "Best_Recommendation", "Recommendation_Score",
                 "rf_anxiety_score"] + config.ALTERNATIVES
    st.dataframe(result[show_cols].head(top_n), width="stretch")
    st.download_button("Download full ranking (CSV)", result.to_csv().encode(),
                       "smart_ranking.csv", "text/csv")

    st.subheader("Charts")
    c1, c2 = st.columns(2)
    c1.pyplot(plots.score_histogram(result["smart_score"]))
    c2.pyplot(plots.utility_radar(result, utility))
    st.pyplot(plots.recommendation_by_alternative(result, f"Recommendation Score by Alternative ({profile})"))
    c3, c4 = st.columns(2)
    c3.pyplot(plots.top_heatmap(result))
    c4.pyplot(plots.correlation_heatmap(result))

    st.subheader("Weight profile comparison")
    all_results = {
        name: score_batch(df, name, use_ref, bounds)[0] for name in config.WEIGHT_PROFILES
    }
    fig, table = plots.model_comparison({k: v for k, v in all_results.items() if not k.startswith("C")})
    st.pyplot(fig)
    st.dataframe(table)

# ---------- model ----------
with tab_model:
    st.header("Random Forest model")
    m = meta["metrics"]
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("MAE", f"{m['mae']:.4f}")
    k2.metric("MSE", f"{m['mse']:.4f}")
    k3.metric("RMSE", f"{m['rmse']:.4f}")
    k4.metric("R²", f"{m['r2']:.4f}")
    st.pyplot(plots.feature_importance(rf, meta["features"]))
    with st.expander("Metadata"):
        st.json({k: v for k, v in meta.items() if k != "smart_bounds"})
        st.json(meta["smart_bounds"])
