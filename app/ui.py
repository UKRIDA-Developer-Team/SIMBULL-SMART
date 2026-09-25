"""Streamlit-only helpers shared by every page: language, cached loaders, sidebar, footer."""
import json

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from spk import config, data, gform, i18n, model, recommend, smart

PROFILES = {"A": config.WEIGHTS_A, "B": config.WEIGHTS_B, "C": config.WEIGHTS_C}
CONTENT_DIR = config.APP_DIR / "content"


# ---------- language ----------

def lang() -> str:
    return (st.session_state.get("lang") or i18n.DEFAULT).lower()


def T(key: str, **fmt) -> str:
    return i18n.t(key, lang(), **fmt)


def content(name: str) -> str:
    path = CONTENT_DIR / lang() / f"{name}.md"
    if not path.exists():
        path = CONTENT_DIR / i18n.DEFAULT / f"{name}.md"
    return path.read_text()


def profile_key() -> str:
    return st.session_state.get("profile", "A")


def profile_label(key: str | None = None) -> str:
    return T(f"profile_{key or profile_key()}")


def weights() -> dict:
    return PROFILES[profile_key()]


def show(fig):
    st.pyplot(fig)
    plt.close(fig)


# ---------- cached loaders ----------

@st.cache_resource(show_spinner=False)
def load_active():
    return model.load()


@st.cache_resource(show_spinner=False)
def load_base():
    return model.load_base()


@st.cache_data(show_spinner=False)
def load_reference() -> pd.DataFrame:
    df = data.load_dataset()
    return df.assign(student_id=[f"STU{i + 1:05d}" for i in range(len(df))]).set_index("student_id")


@st.cache_data(show_spinner=False)
def load_json(path_str: str):
    path = config.APP_DIR / path_str
    return json.loads(path.read_text()) if path.exists() else None


def real_summary():
    return load_json(str(config.REAL_SUMMARY_PATH.relative_to(config.APP_DIR)))


def model_comparison():
    return load_json(str(config.MODEL_COMPARISON_PATH.relative_to(config.APP_DIR)))


@st.cache_data(show_spinner=False)
def reference_quantiles() -> dict:
    rf, meta = load_active()
    if meta.get("reference_quantiles"):
        return meta["reference_quantiles"]
    return recommend.reference_quantiles(rf, load_reference(), meta["smart_bounds"])


@st.cache_data(show_spinner=False)
def predict_frame(df: pd.DataFrame) -> pd.Series:
    rf, _ = load_active()
    return pd.Series(model.predict(rf, df), index=df.index, name="rf_anxiety_score")


@st.cache_data(show_spinner=False)
def score(df: pd.DataFrame, profile: str, use_reference_bounds: bool = True):
    """Predict + SMART for a frame of students. Returns (result sorted by priority, utility)."""
    _, meta = load_active()
    crit = df[config.FEATURES].copy()
    crit["rf_anxiety_score"] = predict_frame(df[config.FEATURES])
    bounds = meta["smart_bounds"] if use_reference_bounds else None
    result, utility = smart.run(crit[config.CRITERIA], PROFILES[profile], bounds)
    result = pd.concat([df[config.FEATURES], crit[["rf_anxiety_score"]], result], axis=1)
    return result.sort_values("smart_score", ascending=False), utility


def impute_medians() -> dict:
    _, meta = load_active()
    return meta.get("impute_medians") or gform.feature_medians(load_reference())


# ---------- page chrome ----------

def sidebar():
    with st.sidebar:
        st.segmented_control(T("lang"), options=[k.upper() for k in i18n.LANGS], key="lang",
                             default=i18n.DEFAULT.upper(), selection_mode="single")
        st.radio(T("profile"), list(PROFILES), key="profile", help=T("profile_help"),
                 captions=[profile_label(k).split(" - ", 1)[1] for k in PROFILES])
        if profile_key() == "C":
            st.warning(T("profile_c_warning"))
        _, meta = load_active()
        source = {"kaggle": "src_kaggle", "kaggle+gform": "src_real", "gform": "src_real"}[meta["data_source"]]
        st.caption(T("model_badge", source=T(source), n=f"{meta.get('n_rows', 0):,}",
                     strategy=meta.get("strategy", "-")))
        st.divider()
        st.caption(T("disclaimer"))
        st.caption(T("privacy_note"))


def footer():
    st.divider()
    st.caption(T("disclaimer"))


def artifacts_ok() -> bool:
    path, _ = config.active_model_paths()
    return path.exists() and config.DATA_PATH.exists()
