"""Streamlit-only helpers shared by every page: language, cached loaders, layout pieces, settings."""
import base64
import html
import json

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from spk import config, data, gform, i18n, model, recommend, smart, xai

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


def weights() -> dict:
    """The SMART weights (one set, domain-weighted; see config.WEIGHTS_A)."""
    return config.WEIGHTS_A


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
    # The picker widget (see model_picker) holds the newest choice before its own line runs.
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


def score(df: pd.DataFrame, use_reference_bounds: bool = True):
    """Predict + SMART for a frame of students. Returns (result sorted by priority, utility)."""
    return _score(df, use_reference_bounds, model_key())


@st.cache_data(show_spinner=False)
def _score(df: pd.DataFrame, use_reference_bounds: bool, kind: str):
    _, meta = load_model(kind)
    crit = df[config.FEATURES].copy()
    crit["rf_anxiety_score"] = _predict_frame(df[config.FEATURES], kind)
    bounds = meta["smart_bounds"] if use_reference_bounds else None
    result, utility = smart.run(crit[config.CRITERIA], config.WEIGHTS_A, bounds)
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


def example_features(kind: str) -> dict:
    """Model features of an example student (config.EXAMPLE_ANSWERS), as the questionnaire would give."""
    return gform.derive(pd.DataFrame([config.EXAMPLE_ANSWERS[kind]])).iloc[0][config.FEATURES].to_dict()


def impute_medians() -> dict:
    _, meta = load_active()
    return meta.get("impute_medians") or gform.feature_medians(load_reference())


# ---------- the comparison group behind percentiles and bands ----------

def reference_group(kind: str | None = None) -> str:
    """Who a student is compared with for percentiles, bands and the referral cutoff.

    Model riil: the questionnaire respondents the model was retrained on (only their quantiles ship).
    Kaggle model: the 20,000-row Kaggle test sample."""
    kind = kind or model_key()
    _, meta = load_model(kind)
    if kind == "real" and meta.get("reference_quantiles"):
        return T("ref_group_real", n=f"{meta.get('n_rows', 0):,}")
    return T("ref_group_kaggle", n=f"{len(load_reference()):,}")


def band_help(kind: str) -> str:
    """Tooltip for a band chip: which group, and the value range of each band (kind = anx | prio)."""
    q = reference_quantiles()["rf_anxiety_score" if kind == "anx" else "smart_score"]
    fmt = (lambda v: f"{v:.2f}") if kind == "anx" else (lambda v: f"{v:.3f}")
    label = (lambda b: T(f"band_{b}")) if kind == "anx" else (lambda b: T(f"prio_{b}"))
    p40, p60, p90 = q[40], q[60], q[config.SAFETY_PERCENTILE]
    return T("band_help", group=reference_group(), low=label("low"), mid=label("mid"), high=label("high"),
             top=label("top"), p40=fmt(p40), p60=fmt(p60), p90=fmt(p90)) + (T("band_help_anx") if kind == "anx" else "")


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

# The app has two zones that share one top bar: "app" for counselors (assess one student or a
# class) and "report" for examiners (the technical report, one chapter per page).
# Each entry: (key, page file, nav label key, url path).
ZONES = {
    "app": [
        ("home", "app_pages/home.py", "nav_home", "home"),
        ("student", "app_pages/recommendation.py", "nav_student", "student"),
        ("class", "app_pages/batch.py", "nav_class", "class"),
        ("help", "app_pages/help.py", "nav_help", "help"),
    ],
    "report": [
        ("ch1", "app_pages/report/data.py", "ch1_nav", "report-data"),
        ("ch2", "app_pages/report/model.py", "ch2_nav", "report-model"),
        ("ch3", "app_pages/report/calculation.py", "ch3_nav", "report-calculation"),
        ("ch4", "app_pages/report/xai.py", "ch4_nav", "report-xai"),
        ("ch5", "app_pages/report/smart.py", "ch5_nav", "report-smart"),
        ("ch6", "app_pages/report/fairness.py", "ch6_nav", "report-fairness"),
        ("ch7", "app_pages/report/crispdm.py", "ch7_nav", "report-crispdm"),
        ("ch8", "app_pages/report/architecture.py", "ch8_nav", "report-architecture"),
    ],
}
PAGE_FILE = {key: path for pages in ZONES.values() for key, path, _, _ in pages}


def build_pages() -> list:
    """Every page of both zones, for st.navigation. The first app page is the default."""
    return [st.Page(path, title=T(label), url_path=url, default=(key == "home"))
            for pages in ZONES.values() for key, path, label, url in pages]


def zone_of(url_path: str) -> str:
    return "report" if any(url == url_path for *_, url in ZONES["report"]) else "app"


def setup(current):
    """Global styles, the zone's own styles, and the top bar. Called once per run from the entry script."""
    url = current.url_path or "home"          # the default page reports an empty url path
    zone = zone_of(url)
    css = (ASSETS_DIR / "style.css").read_text() + (ASSETS_DIR / f"zone_{zone}.css").read_text()
    st.html(f"<style>{css}</style>")
    topbar(zone, url)


def _logo_uri() -> str:
    return "data:image/svg+xml;base64," + base64.b64encode((ASSETS_DIR / "logo.svg").read_bytes()).decode()


def topbar(zone: str, current_url: str):
    """Brand, the zone's page links, and two small switches: zone (App | Report) and language."""
    with st.container(key="topbar", horizontal=True, vertical_alignment="center", gap="medium"):
        st.html(f"<div class='spk-brand'><img src='{_logo_uri()}' alt='SI SMART'></div>", width="content")
        with st.container(key="topnav", horizontal=True, vertical_alignment="center", gap=None):
            for key, path, label, url in ZONES[zone]:
                active = "_on" if url == current_url else ""
                with st.container(key=f"nav_{key}{active}", width="content"):
                    st.page_link(path, label=T(label))
        with st.container(key="topctl", horizontal=True, vertical_alignment="center", gap="small", width="content"):
            labels = {z: T(f"zone_{z}") for z in ZONES}
            # The key carries the zone, so the switch always opens on the zone of the page shown.
            picked = st.segmented_control(T("zone"), list(labels.values()), default=labels[zone], required=True,
                                          key=f"zone_{zone}_{lang()}", label_visibility="collapsed")
            # The language lives in a plain session key ("lang"). A widget's own state does not survive
            # st.switch_page (used by the zone switch), so the widget only mirrors it.
            st.session_state["lang_switch"] = lang().upper()
            st.segmented_control(T("lang"), options=[k.upper() for k in i18n.LANGS], key="lang_switch",
                                 required=True, label_visibility="collapsed", on_change=_set_lang)
    if picked != labels[zone]:
        st.switch_page(ZONES["report" if zone == "app" else "app"][0][1])


def _set_lang():
    st.session_state["lang"] = st.session_state["lang_switch"]


def open_calculation(features: dict | None = None):
    """Open report chapter 3 (the worked SMART example) for a student."""
    if features is not None:
        st.session_state["assess_features"] = dict(features)
    st.session_state["calc_source"] = "last"
    st.switch_page(PAGE_FILE["ch3"])


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


def model_picker():
    """The prediction-model choice (two iterations) in a small popover. Hidden with only one model."""
    models = available_models()
    if len(models) < 2:
        return
    with st.popover(T(f"model_short_{model_key()}"), icon=":material/tune:"):
        st.markdown(f"**{T('model_choice')}**")
        st.caption(T("model_choice_intro"))
        stable_choice(st.radio, T("model_choice"), models, "model_choice", lambda k: T(f"model_opt_{k}"),
                      label_visibility="collapsed", captions=[model_caption(k) for k in models])
        st.caption(model_note())


def model_caption(kind: str) -> str:
    """One line per model for the picker: what it was trained on and how well it does on real students."""
    _, meta = load_model(kind)
    strategies = (real_summary() or {}).get("strategies", {})
    key = "S0_kaggle" if kind == "kaggle" else (real_summary() or {}).get("selected")
    real_mae = strategies.get(key, {}).get("holdout_mae")
    text = T(f"model_opt_{kind}_desc", n=f"{meta.get('n_rows', 0):,}", r2=meta["metrics"]["r2"])
    return text + (" " + T("model_opt_real_mae", mae=real_mae) if real_mae is not None else "")


def strategy_label(name: str) -> str:
    """A retraining strategy code (S1_real, S2_combined_w10, S3_warm_200) in plain words."""
    if name.startswith("S2_combined_w"):
        return T("strategy_S2", w=name.removeprefix("S2_combined_w"))
    if name.startswith("S3_warm_"):
        return T("strategy_S3", w=name.removeprefix("S3_warm_"))
    return T(f"strategy_{name}") if f"strategy_{name}" in i18n.S else name


def metrics_source(meta: dict) -> str:
    """Where the active model's metrics were measured, in the reader's language."""
    note = meta.get("metrics_note", "")
    if note.startswith("holdout"):
        return T("metrics_src_holdout")
    if note.startswith("cross"):
        return T("metrics_src_cv")
    return T("metrics_src_kaggle")


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
