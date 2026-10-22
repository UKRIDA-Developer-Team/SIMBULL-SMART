"""Core feature: questionnaire/feature input -> RF prediction -> SMART ranking, with explanations."""
import html

import pandas as pd
import streamlit as st

import ui
from spk import config, data, explain, gform, i18n, model, recommend
from spk import plots

L = ui.lang()
T = ui.T
MAPPING = gform.load_mapping()
SCALES = MAPPING["scales"]

ui.page_header(T("reco_title"), T("reco_intro"))
with st.container(horizontal=True, vertical_alignment="center", gap="small"):
    view = ui.stable_choice(st.segmented_control, T("nav_reco"), ["single", "batch"], "reco_view",
                            lambda v: T(f"view_{v}"), label_visibility="collapsed")
    st.space("stretch")
    ui.profile_picker()
ui.profile_warning()
st.space("small")


# ---------------------------------------------------------------- one student: input
def show_result(features: dict):
    st.session_state["assess_features"] = features
    st.session_state["reco_step"] = "result"
    st.session_state["scroll_top"] = True


def edit_answers():
    st.session_state["reco_step"] = "form"


def new_assessment():
    for k in [k for k in st.session_state if k.startswith(("q_", "a_"))] + ["assess_features"]:
        del st.session_state[k]
    st.session_state["reco_step"] = "form"


def q_section(n: int, title: str, hint: str | None = None):
    """A numbered card that groups related questions."""
    box = st.container(border=True, key=f"card_q{n}")
    hint_html = f"<p class='spk-q-hint'>{html.escape(hint)}</p>" if hint else ""
    box.html(f"<div class='spk-q-head'><span class='spk-step'>{n}</span>"
             f"<div><p class='spk-q-title'>{html.escape(title)}</p>{hint_html}</div></div>")
    return box


def scale_input(field: str, scale: str, default: int, container):
    options = SCALES[scale]
    return container.radio(
        i18n.question(field, L), options=list(range(1, len(options) + 1)), index=default - 1, horizontal=True,
        format_func=lambda i: i18n.option_label(scale, i - 1, options[i - 1], L), key=f"q_{field}_{L}",
        persist_state="session")


def questionnaire_form():
    hours = [0.25, 0.5] + [x / 2 for x in range(2, 24)]
    sleep = [x / 2 for x in range(8, 25)]
    days = MAPPING["value_maps"]["exercise_days"]
    day_labels = list(days)
    f = {}
    with st.form("questionnaire", border=False):
        box = q_section(1, T("sec_q_identity"), T("sec_q_identity_hint"))
        c1, c2 = box.columns(2, gap="medium")
        f["gender"] = c1.radio(i18n.question("gender", L), ["Male", "Female"], horizontal=True, key=f"q_gender_{L}",
                               format_func=lambda g: {"Male": "Laki-laki", "Female": "Perempuan"}[g] if L == "id" else g,
                               persist_state="session")
        f["age"] = c2.number_input(T("age_q"), 12, 30, 16, key=f"q_age_{L}", persist_state="session")

        box = q_section(2, T("sec_q_study"), T("sec_q_study_hint"))
        c1, c2 = box.columns(2, gap="medium", vertical_alignment="bottom")
        f["study_hours"] = c1.select_slider(i18n.question("study_hours", L), hours, value=2.0, key=f"q_study_{L}",
                                            format_func=lambda h: i18n.hours_label(h, L), persist_state="session")
        f["report_grade"] = c2.number_input(i18n.question("report_grade", L), 0.0, 100.0, 82.0, 0.5,
                                            key=f"q_grade_{L}", persist_state="session")
        f["late_night"] = scale_input("late_night", "late_night4", 2, box)
        f["time_insufficient"] = scale_input("time_insufficient", "insufficient4", 2, box)
        f["late_tasks"] = scale_input("late_tasks", "late_tasks4", 1, box)

        box = q_section(3, T("sec_q_pressure"), T("sec_q_pressure_hint"))
        f["many_tasks"] = scale_input("many_tasks", "freq5", 3, box)
        f["exam_stress"] = scale_input("exam_stress", "freq5", 3, box)
        f["fear_parents"] = scale_input("fear_parents", "freq5", 3, box)
        f["family_demand"] = scale_input("family_demand", "freq5", 3, box)

        box = q_section(4, T("sec_q_life"), T("sec_q_life_hint"))
        f["sleep_duration"] = box.select_slider(i18n.question("sleep_duration", L), sleep, value=7.0, key=f"q_sleep_{L}",
                                                format_func=lambda h: i18n.hours_label(h, L), persist_state="session")
        pick = box.radio(i18n.question("exercise_days", L), list(range(len(day_labels))), index=1, horizontal=True,
                         key=f"q_days_{L}", persist_state="session",
                         format_func=lambda i: i18n.option_label("exercise_days", i, day_labels[i], L))
        f["exercise_days"] = days[day_labels[pick]]
        f["pocket_money"] = scale_input("pocket_money", "jajan5", 4, box)

        box = q_section(5, T("sec_q_burnout"), T("sec_q_burnout_hint"))
        f["time_split"] = scale_input("time_split", "agree5", 3, box)
        f["exhausted"] = scale_input("exhausted", "agree5", 3, box)
        f["lost_interest"] = scale_input("lost_interest", "agree5", 2, box)
        submitted = st.form_submit_button(T("submit"), type="primary", icon=":material/arrow_forward:",
                                          icon_position="right", width="stretch")
    if submitted:
        show_result(gform.derive(pd.DataFrame([f])).iloc[0][config.FEATURES].to_dict())
        st.rerun()


def advanced_form():
    with st.form("advanced", border=False):
        box = q_section(1, T("sec_adv_profile"))
        c1, c2 = box.columns(2, gap="medium")
        values = {}
        lo, hi, default = config.INPUT_RANGES["age"]
        values["age"] = c1.number_input(i18n.feature("age", L), lo, hi, default, key="a_age", persist_state="session")
        values["gender"] = c2.selectbox(i18n.feature("gender", L), list(config.GENDER_MAP), key="a_gender",
                                        persist_state="session")
        box = q_section(2, T("sec_adv_values"))
        cols = box.columns(2, gap="medium")
        numeric = [c for c in config.FEATURES if c not in ("age", "gender")]
        for i, feat in enumerate(numeric):
            lo, hi, default = config.INPUT_RANGES[feat]
            values[feat] = cols[i % 2].slider(i18n.feature(feat, L), float(lo), float(hi), float(default), 0.1,
                                              help=i18n.feature_help(feat, L), key=f"a_{feat}", persist_state="session")
        if st.form_submit_button(T("submit"), type="primary", icon=":material/arrow_forward:", icon_position="right",
                                 width="stretch"):
            show_result(values)
            st.rerun()


def input_view():
    main, side = st.columns([2.2, 1], gap="large")
    with side.container(key="side_sticky"):
        with st.container(border=True, key="card_tips"):
            st.markdown(f"**{T('tips_title')}**")
            st.markdown("\n".join(f"- {T(f'tips_{i}')}" for i in range(1, 5)))
        with st.container(border=True, key="card_examples"):
            st.markdown(f"**{T('examples')}**")
            for key in ("high", "low"):
                st.button(T(f"example_{key}"), key=f"example_{key}", width="stretch",
                          on_click=show_result, args=(dict(config.EXAMPLE_PROFILES[key]),))
    with main:
        adv = st.toggle(T("mode_adv"), value=st.session_state.get("input_mode_choice") == "adv", key=f"adv_{L}",
                        help=T("mode_help"))
        st.session_state["input_mode_choice"] = "adv" if adv else "q"
        if adv:
            advanced_form()
        else:
            questionnaire_form()


# ---------------------------------------------------------------- one student: result
def hero_html(a) -> str:
    best = a.best
    anx_band, prio_band = ui.band(a.rf_percentile), ui.band(a.priority_percentile)
    return f"""
<div class="spk-hero">
  <div class="spk-hero-main">
    <span class="spk-icon spk-icon-tile">{ui.ALT_ICONS[best]}</span>
    <p class="spk-hero-label">{T('res_best')}</p>
    <p class="spk-hero-alt">{html.escape(i18n.alt(best, L))}</p>
    <p class="spk-hero-desc">{html.escape(i18n.alt_desc(best, L))}</p>
    <p class="spk-hero-fine">{T('res_fit', s=float(a.ranking.iloc[0]))}</p>
  </div>
  <div class="spk-hero-stat">
    <p class="spk-hero-label">{T('res_pred')}</p>
    <p class="spk-hero-value">{a.rf_score:.2f}<span> / 10</span></p>
    <span class="spk-chip is-{anx_band}">{T(f'band_{anx_band}')}</span>
    <div class="spk-bar-track"><div class="spk-bar-fill is-{anx_band}" style="width:{min(100, a.rf_score * 10):.1f}%"></div></div>
    <p class="spk-hero-fine">{T('res_pred_note', p=a.rf_percentile)}</p>
  </div>
  <div class="spk-hero-stat">
    <p class="spk-hero-label">{T('res_priority')}</p>
    <p class="spk-hero-value">{a.priority:.3f}<span> / 1</span></p>
    <span class="spk-chip is-{prio_band}">{T(f'prio_{prio_band}')}</span>
    <div class="spk-bar-track"><div class="spk-bar-fill is-{prio_band}" style="width:{min(100, a.priority * 100):.1f}%"></div></div>
    <p class="spk-hero-fine">{T('res_priority_note', p=a.priority_percentile)}</p>
  </div>
</div>"""


def render_result(features: dict):
    rf, meta = ui.load_active()
    a = recommend.assess(rf, meta, features, ui.weights(), ui.reference_quantiles())

    if st.session_state.pop("scroll_top", False):
        ui.scroll_to_top()
    with st.container(horizontal=True, gap="small"):
        st.button(T("back_edit"), icon=":material/arrow_back:", type="tertiary", on_click=edit_answers)
        st.space("stretch")
        st.button(T("new_assessment"), icon=":material/restart_alt:", on_click=new_assessment)

    if a.safety:
        st.error(f"**{T('safety_title')}** · " +
                 T("safety_body", pct=100 - config.SAFETY_PERCENTILE, contact=config.REFERRAL_CONTACT[L]),
                 icon=":material/priority_high:")

    with st.container(border=True, key="card_hero"):
        st.html(hero_html(a))

    c1, c2 = st.columns([1, 1.15], gap="medium")
    with c1.container(border=True, key="card_rank", height="stretch"):
        st.markdown(f"**{T('res_rank')}**")
        st.caption(T("res_rank_help"))
        st.html(ui.bars([(i18n.alt(alt, L), float(s), f"{s:.3f}") for alt, s in a.ranking.items()]))
    with c2.container(border=True, key="card_why", height="stretch"):
        st.markdown(f"**{T('res_why', alt=i18n.alt(a.best, L))}**")
        st.markdown("\n".join(f"- {line}" for line in explain.narrative(a, ui.profile_label(), L)))

    st.space("small")
    with st.expander(T("res_details"), icon=":material/calculate:"):
        t1, t2, t3 = st.tabs([T("res_contrib"), T("res_inputs"), T("res_sens")])
        with t1:
            st.caption(T("res_contrib_help"))
            ui.show(plots.contribution_bars(a.contributions, L))
        with t2:
            table = pd.DataFrame({
                T("criterion"): [i18n.feature(c, L) for c in config.CRITERIA],
                T("value"): [round(float(a.criteria[c]), 2) for c in config.CRITERIA],
                T("type"): [T(config.CRITERIA_TYPE[c]) for c in config.CRITERIA],
                T("utility"): [round(float(a.utility[c]), 3) for c in config.CRITERIA],
            })
            st.table(table.set_index(T("criterion")))
            other = {i18n.feature(k, L): v for k, v in a.features.items() if k not in config.CRITERIA}
            st.caption(", ".join(f"{k}: {v:.2f}" if isinstance(v, float) else f"{k}: {v}" for k, v in other.items()))
        with t3:
            st.caption(T("res_sens_help"))
            sens = a.sensitivity
            grid = sens.pivot(index="criterion", columns="delta", values="best").reindex(config.CRITERIA)
            changed = sens.pivot(index="criterion", columns="delta", values="changed").reindex(config.CRITERIA)
            grid = grid.map(lambda x: i18n.alt(x, L))
            grid.index = [i18n.feature(c, L) for c in grid.index]
            grid.columns = [f"{d:+.0%}" for d in grid.columns]
            changed.index, changed.columns = grid.index, grid.columns
            st.table(grid.style.apply(lambda _: changed.map(
                lambda c: "background-color: #FBEAD2" if c else "").to_numpy(), axis=None))
            k = int(sens["changed"].sum())
            if k == 0:
                st.success(T("res_sens_stable", k=len(sens), n=len(sens)), icon=":material/check_circle:")
            else:
                crit = sens.loc[sens["changed"], "criterion"].value_counts().index[0]
                st.warning(T("res_sens_changes", k=k, n=len(sens), crit=i18n.feature(crit, L)), icon=":material/info:")


# ---------------------------------------------------------------- whole class
def load_batch(upload):
    """Returns (frame with FEATURES [+ target], info message) or raises ValueError with a user message."""
    if upload is None:
        if st.session_state.get("batch_demo_choice", "kaggle") == "kaggle":
            return ui.load_reference()[config.FEATURES], None
        raw = gform.read_export(config.SAMPLE_GFORM_PATH)
    else:
        raw = gform.read_export(upload)

    if set(config.FEATURES) <= set(raw.columns):
        clean, issues = data.validate_values(raw)
        keep = config.FEATURES + ([config.TARGET] if config.TARGET in clean else [])
        if config.TARGET in keep:
            clean[config.TARGET] = pd.to_numeric(clean[config.TARGET], errors="coerce")
        ids = raw["student_id"] if "student_id" in raw else [f"STU{i + 1:05d}" for i in range(len(raw))]
        frame = clean[keep].set_axis(pd.Index(ids, name="student_id"))
        note = T("batch_detected_csv", n=len(frame))
        problems = {k: v for k, v in issues.items() if v and k != "missing"}
        if problems:
            note += f" {problems}"
        return frame, note
    try:
        prepared = gform.prepare(raw)
    except ValueError as err:
        if gform.looks_like_gform(raw):
            raise ValueError(T("batch_bad", err=err)) from err
        missing = data.validate_columns(raw)
        raise ValueError(T("batch_missing_cols", cols=missing, need=config.FEATURES)) from err
    dropped = prepared.report["pii_columns_dropped"]
    note = T("batch_detected_gform", n=len(prepared.data), k=len(dropped), cols=", ".join(dropped))
    frame = prepared.data.drop(columns=[c for c in prepared.data if c.startswith("x_")])
    frame.index.name = "student_id"
    return frame, note


def batch_view():
    up, demo = st.columns([1.6, 1], gap="medium")
    with up:
        upload = st.file_uploader(T("batch_upload"), type=["csv", "xlsx"])
        st.caption(T("batch_upload_help"))
    with demo.container(border=True, key="card_demo"):
        st.markdown(f"**{T('batch_demo_title')}**")
        st.caption(T("batch_demo_lead"))
        ui.stable_choice(st.radio, T("batch_default"), ["kaggle", "gform"], "batch_demo_choice",
                         lambda k: T(f"batch_demo_{k}"), label_visibility="collapsed", disabled=upload is not None)

    try:
        frame, note = load_batch(upload)
    except ValueError as err:
        st.error(str(err), icon=":material/error:")
        return
    if note:
        st.info(note, icon=":material/description:")

    n_missing = int(frame[config.FEATURES].isna().sum().sum())
    if n_missing:
        frame = gform.impute(frame, ui.impute_medians())
        st.caption(T("batch_imputed", n=n_missing))

    use_ref = st.session_state.get("batch_use_ref", True)
    result, utility = ui.score(frame, ui.profile_key(), use_ref)

    # Summary first: how many students, how many urgent, what the class needs most.
    cutoff = ui.reference_quantiles()["rf_anxiety_score"][config.SAFETY_PERCENTILE]
    urgent = int((result["rf_anxiety_score"] >= cutoff).sum())
    mix = result["Best_Recommendation"].value_counts()
    m = st.columns(4, gap="small")
    m[0].metric(T("batch_n"), f"{len(result):,}", border=True)
    m[1].metric(T("batch_urgent"), f"{urgent:,}", border=True, help=T("batch_urgent_help"))
    m[2].metric(T("batch_top_alt"), i18n.alt(mix.index[0], L), border=True)
    m[3].metric(T("batch_mean_anx"), f"{result['rf_anxiety_score'].mean():.2f}", border=True)

    st.space("small")
    head, pick = st.columns([3, 1], vertical_alignment="bottom")
    with head:
        ui.section(T("batch_list"), T("batch_list_help"))
    sizes = [n for n in (10, 20, 50, 100, 250, 500) if n < len(result)] + [min(len(result), 500)]
    top_n = pick.selectbox(T("batch_topn"), sorted(set(sizes)), index=min(1, len(set(sizes)) - 1), key="batch_topn")
    view = result.head(top_n).copy()
    view["Best_Recommendation"] = view["Best_Recommendation"].map(lambda x: i18n.alt(x, L))
    cols = ["rank", "smart_score", "Best_Recommendation", "Recommendation_Score", "rf_anxiety_score"]
    score_col = st.column_config.ProgressColumn
    st.dataframe(
        view[cols + config.ALTERNATIVES], width="stretch",
        column_config={
            "_index": st.column_config.TextColumn(T("student_id")),
            "rank": st.column_config.NumberColumn(T("rank"), format="%d", width="small"),
            "smart_score": score_col(i18n.feature("smart_score", L), min_value=0.0, max_value=1.0, format="%.3f"),
            "Best_Recommendation": st.column_config.TextColumn(T("res_best")),
            "Recommendation_Score": st.column_config.NumberColumn(T("score"), format="%.3f"),
            "rf_anxiety_score": score_col(i18n.feature("rf_anxiety_score", L), min_value=0.0, max_value=10.0,
                                          format="%.2f"),
        } | {a: st.column_config.NumberColumn(i18n.alt(a, L), format="%.3f") for a in config.ALTERNATIVES})
    st.download_button(T("batch_download"), result.to_csv().encode(), "smart_ranking.csv", "text/csv",
                       icon=":material/download:")

    st.space("small")
    c1, c2 = st.columns(2, gap="medium")
    with c1.container(border=True, key="card_mix"):
        ui.show(plots.recommendation_mix(result, L))
    with c2.container(border=True, key="card_hist"):
        ui.show(plots.score_histogram(result["smart_score"], L))

    with st.expander(T("batch_options"), icon=":material/settings:"):
        st.checkbox(T("batch_bounds"), value=True, key="batch_use_ref")

    if config.TARGET in frame and frame[config.TARGET].notna().sum() >= 5:
        st.space("small")
        ui.section(T("batch_eval"), T("batch_eval_help"))
        labeled = frame.dropna(subset=[config.TARGET])
        rf, meta = ui.load_active()
        base, _ = ui.load_base()
        names = {"active": "Model aktif" if L == "id" else "Active model",
                 "base": "Model dasar (Kaggle)" if L == "id" else "Base model (Kaggle)"}
        rows = {names[key]: model.metrics(labeled[config.TARGET], model.predict(m, labeled[config.FEATURES]))
                for key, m in {"active": rf, "base": base}.items()}
        c1, c2 = st.columns([3, 2], gap="medium")
        with c1:
            st.table(pd.DataFrame(rows).T[["mae", "rmse", "r2"]].rename(
                columns={"mae": "MAE", "rmse": "RMSE", "r2": "R²"}).round(4))
            st.caption(f"n = {len(labeled)}")
        with c2.container(border=True, key="card_eval"):
            ui.show(plots.actual_vs_predicted(labeled[config.TARGET], model.predict(rf, labeled[config.FEATURES]), L))


# ---------------------------------------------------------------- page body
if view == "batch":
    batch_view()
elif st.session_state.get("assess_features") and st.session_state.get("reco_step") != "form":
    render_result(st.session_state["assess_features"])
else:
    input_view()

ui.footer()
