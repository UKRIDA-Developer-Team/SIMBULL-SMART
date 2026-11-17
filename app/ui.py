"""Streamlit-only helpers shared by every page: language, cached loaders, layout pieces, settings."""
import html
import json

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from spk import config, data, gform, i18n, model, recommend, smart, xai

PROFILES = {"A": config.WEIGHTS_A, "B": config.WEIGHTS_B, "C": config.WEIGHTS_C}
CONTENT_DIR = config.APP_DIR / "content"
ASSETS_DIR = config.APP_DIR / "assets"

# Material Symbols shown next to each intervention.
ALT_ICONS = {"Sleep": "bedtime", "Exercise": "directions_run", "Study": "menu_book",
             "Counseling": "forum", "Relaxation": "self_improvement"}


# ---------- language ----------

def lang() -> str:
    return (st.session_state.get("lang") or i18n.DEFAULT).lower()


def T(key: str, **fmt) -> str:
    return i18n.t(key, lang(), **fmt)


def content(name: str, suffix: str = ".md") -> str:
    path = CONTENT_DIR / lang() / f"{name}{suffix}"
    if not path.exists():
        path = CONTENT_DIR / i18n.DEFAULT / f"{name}{suffix}"
    return path.read_text()


def profile_key() -> str:
    # The picker widget (see profile_picker) holds the newest choice before its own line runs.
    picked = st.session_state.get(f"profile_{lang()}")
    if picked in PROFILES:
        st.session_state["profile"] = picked
    return st.session_state.get("profile") or "A"


def profile_label(key: str | None = None) -> str:
    return T(f"profile_{key or profile_key()}")


def weights() -> dict:
    return PROFILES[profile_key()]


def show(fig, compact: bool = False):
    """Render a Matplotlib figure. compact=True keeps its natural size (small heatmaps, bar charts)."""
    # A compact figure is shown at its physical size (inches x 96 CSS px), capped by the column.
    st.pyplot(fig, width=int(fig.get_figwidth() * 96) if compact else "stretch")
    plt.close(fig)


# ---------- cached loaders ----------

MODELS = ("real", "kaggle")   # real = retrained on the questionnaire answers, kaggle = base model


def available_models() -> list[str]:
    """The models that exist on disk, the default (SPK_MODEL / auto) first."""
    have = [k for k in MODELS if (config.REAL_MODEL_PATH if k == "real" else config.MODEL_PATH).exists()]
    default = "real" if config.active_model_paths()[0] == config.REAL_MODEL_PATH else "kaggle"
    return sorted(have, key=lambda k: k != default)


def model_key() -> str:
    """The model this session uses: the reader's choice in the settings popover, else the default."""
    have = available_models()
    # Like profile_key: the picker widget holds the newest choice before its own line runs.
    picked = st.session_state.get(f"model_choice_{lang()}")
    if picked in have:
        st.session_state["model_choice"] = picked
    choice = st.session_state.get("model_choice")
    return choice if choice in have else have[0]


@st.cache_resource(show_spinner=False)
def load_model(kind: str):
    if kind == "real":
        return model.load(config.REAL_MODEL_PATH, config.REAL_METADATA_PATH)
    return model.load_base()


def load_active():
    """The model chosen for this session (both stay loaded, so switching is instant)."""
    return load_model(model_key())


def load_base():
    return load_model("kaggle")


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


# Cached results depend on the model, so every cached helper takes the model key as an argument.

def reference_quantiles(kind: str | None = None) -> dict:
    return _reference_quantiles(kind or model_key())


@st.cache_data(show_spinner=False)
def _reference_quantiles(kind: str) -> dict:
    rf, meta = load_model(kind)
    if meta.get("reference_quantiles"):
        return meta["reference_quantiles"]
    return recommend.reference_quantiles(rf, load_reference(), meta["smart_bounds"])


def predict_frame(df: pd.DataFrame) -> pd.Series:
    return _predict_frame(df, model_key())


@st.cache_data(show_spinner=False)
def _predict_frame(df: pd.DataFrame, kind: str) -> pd.Series:
    rf, _ = load_model(kind)
    return pd.Series(model.predict(rf, df), index=df.index, name="rf_anxiety_score")


def score(df: pd.DataFrame, profile: str, use_reference_bounds: bool = True):
    """Predict + SMART for a frame of students. Returns (result sorted by priority, utility)."""
    return _score(df, profile, use_reference_bounds, model_key())


@st.cache_data(show_spinner=False)
def _score(df: pd.DataFrame, profile: str, use_reference_bounds: bool, kind: str):
    _, meta = load_model(kind)
    crit = df[config.FEATURES].copy()
    crit["rf_anxiety_score"] = _predict_frame(df[config.FEATURES], kind)
    bounds = meta["smart_bounds"] if use_reference_bounds else None
    result, utility = smart.run(crit[config.CRITERIA], PROFILES[profile], bounds)
    result = pd.concat([df[config.FEATURES], crit[["rf_anxiety_score"]], result], axis=1)
    return result.sort_values("smart_score", ascending=False), utility


# ---------- explainable AI (cached: one Shapley explanation is ~0.4 s) ----------

@st.cache_data(show_spinner=False)
def xai_background() -> pd.DataFrame:
    return xai.background_sample(load_reference())


@st.cache_data(show_spinner=False)
def xai_targets() -> dict:
    return xai.reference_targets(load_reference())


@st.cache_data(show_spinner=False, max_entries=256)
def _shap(items: tuple, kind: str):
    rf, _ = load_model(kind)
    return xai.shapley_values(rf, dict(items), xai_background())


def shap_explanation(features: dict | pd.Series):
    """Exact Shapley explanation of the chosen model's prediction for one student."""
    return _shap(tuple((f, features[f]) for f in config.FEATURES), model_key())


@st.cache_data(show_spinner=False)
def kaggle_test_set():
    """The Kaggle test set: the cleaned reference sample. Training rows come from the rest of the
    Kaggle file, so every training strategy leaves these rows unseen."""
    return model.kaggle_test_set(load_reference().reset_index(drop=True))


PERMUTATION_ROWS = 5_000


def permutation_importance(base: bool = False) -> pd.DataFrame:
    """Permutation importance on a fixed 5,000-row sample of the reference rows (55 predictions).

    base=True scores the Kaggle base model, which is what the Kaggle success criteria judge."""
    return _permutation_importance("kaggle" if base else model_key())


@st.cache_data(show_spinner=False)
def _permutation_importance(kind: str) -> pd.DataFrame:
    rf, _ = load_model(kind)
    X_test, y_test = kaggle_test_set()
    sample = X_test.sample(min(PERMUTATION_ROWS, len(X_test)), random_state=config.RANDOM_STATE)
    return xai.permutation_importance(rf, sample, y_test.loc[sample.index], n_repeats=5)


def impute_medians() -> dict:
    _, meta = load_active()
    return meta.get("impute_medians") or gform.feature_medians(load_reference())


# ---------- plain-language bands ----------

def band(percentile: float) -> str:
    """Where a student sits in the reference population, as a short phrase key."""
    if percentile >= config.SAFETY_PERCENTILE:
        return "top"
    if percentile >= 60:
        return "high"
    if percentile >= 40:
        return "mid"
    return "low"


# ---------- page chrome ----------

def setup():
    """Global styles, logo and language switch. Called once per run from the entry script."""
    st.html(f"<style>{(ASSETS_DIR / 'style.css').read_text()}</style>")
    st.logo(str(ASSETS_DIR / "logo.svg"), size="large")
    with st.container(key="lang_switch"):
        st.segmented_control(T("lang"), options=[k.upper() for k in i18n.LANGS], key="lang", required=True,
                             default=i18n.DEFAULT.upper(), label_visibility="collapsed")


def page_header(title: str, lead: str | None = None, eyebrow: str | None = None):
    if eyebrow:
        st.html(f"<p class='spk-eyebrow'>{html.escape(eyebrow)}</p>")
    st.title(title, anchor=False)
    if lead:
        st.html(f"<p class='spk-lead'>{html.escape(lead)}</p>")


def section(title: str, lead: str | None = None):
    st.subheader(title, anchor=False)
    if lead:
        st.caption(lead)


def stable_choice(widget, label, options, state, fmt, **kw):
    """Radio or segmented control whose choice survives a language switch and page changes.

    Widgets with a format_func lose their selection when the labels change, so the
    widget key includes the language and the choice itself lives in `state`.
    """
    options = list(options)
    current = st.session_state.get(state)
    if current not in options:
        current = options[0]
    key = f"{state}_{lang()}"
    if widget is st.radio:
        value = st.radio(label, options, index=options.index(current), key=key, format_func=fmt, **kw)
    else:
        value = widget(label, options, default=current, required=True, key=key, format_func=fmt, **kw)
    st.session_state[state] = value
    return value


def profile_picker():
    """Model and weight-profile settings in a popover, kept out of the way of first-time users."""
    models = available_models()
    with st.popover(T("profile_button", p=profile_key(), m=T(f"model_short_{model_key()}")), icon=":material/tune:"):
        if len(models) > 1:
            st.markdown(f"**{T('model_choice')}**")
            st.caption(T("model_choice_intro"))
            stable_choice(st.radio, T("model_choice"), models, "model_choice", lambda k: T(f"model_opt_{k}"),
                          label_visibility="collapsed", captions=[model_caption(k) for k in models])
        st.markdown(f"**{T('profile')}**")
        st.caption(T("profile_intro"))
        stable_choice(st.radio, T("profile"), PROFILES, "profile", profile_label, label_visibility="collapsed",
                      captions=[T(f"profile_{k}_desc") for k in PROFILES])
        st.caption(model_note())


def profile_warning():
    if profile_key() == "C":
        st.warning(T("profile_c_warning"), icon=":material/info:")


def model_caption(kind: str) -> str:
    """One line per model for the picker: what it was trained on and how well it does on real students."""
    _, meta = load_model(kind)
    strategies = (real_summary() or {}).get("strategies", {})
    key = "S0_kaggle" if kind == "kaggle" else (real_summary() or {}).get("selected")
    real_mae = strategies.get(key, {}).get("holdout_mae")
    text = T(f"model_opt_{kind}_desc", n=f"{meta.get('n_rows', 0):,}", r2=meta["metrics"]["r2"])
    return text + (" " + T("model_opt_real_mae", mae=real_mae) if real_mae is not None else "")


def model_note() -> str:
    _, meta = load_active()
    source = {"kaggle": "src_kaggle", "kaggle+gform": "src_real", "gform": "src_gform"}[meta["data_source"]]
    strategy = f" · {meta['strategy']}" if meta.get("strategy") else ""
    return T("model_badge", source=T(source), n=f"{meta.get('n_rows', 0):,}", strategy=strategy)


def bars(rows: list[tuple[str, float, str]], scale: float = 1.0, highlight_first: bool = True) -> str:
    """Horizontal bar list as HTML. rows = (label, value, value text). Bar length = value / scale."""
    items = []
    for i, (label, value, text) in enumerate(rows):
        pct = max(0.0, min(100.0, 100 * value / scale)) if scale else 0
        cls = "spk-bar is-lead" if (highlight_first and i == 0) else "spk-bar"
        items.append(
            f"<div class='{cls}'><div class='spk-bar-label'>{html.escape(label)}</div>"
            f"<div class='spk-bar-track'><div class='spk-bar-fill' style='width:{pct:.1f}%'></div></div>"
            f"<div class='spk-bar-value'>{html.escape(text)}</div></div>")
    return f"<div class='spk-bars'>{''.join(items)}</div>"


def scroll_to_top(token: object = ""):
    """Bring the view back to the top, e.g. after a long form turns into its result.

    Streamlit runs an st.html script again only when the HTML changes, so callers that scroll more
    than once pass a token that changes each time.
    """
    st.html(f"""<script>/* scroll {html.escape(str(token))} */
      (() => {{
        const toTop = () => {{
          for (const el of [document.querySelector('[data-testid="stMain"]'),
                            document.querySelector('[data-testid="stAppViewContainer"]'),
                            document.scrollingElement]) {{ if (el) el.scrollTo({{top: 0}}); }}
        }};
        toTop();
        setTimeout(toTop, 150);   // again once the rest of the rerun has laid out
      }})();
    </script>""", unsafe_allow_javascript=True)


def footer():
    st.html(
        "<div class='spk-footer'>"
        f"<p>{T('disclaimer_plain')}</p>"
        f"<p>{T('privacy_note')}</p>"
        f"<p class='spk-footer-team'>{T('footer_team')}</p>"
        "</div>")


def artifacts_ok() -> bool:
    path, _ = config.active_model_paths()
    return path.exists() and config.DATA_PATH.exists()
