"""Core feature: questionnaire/feature input -> RF prediction -> SMART ranking, with explanations."""
import pandas as pd
import streamlit as st

import ui
from spk import config, data, explain, gform, i18n, model, recommend
from spk import plots

L = ui.lang()
MAPPING = gform.load_mapping()
SCALES = MAPPING["scales"]

st.title("🔮 " + ui.T("reco_title"))
st.write(ui.T("reco_intro"))

tab_one, tab_many = st.tabs([ui.T("tab_single"), ui.T("tab_batch")])


# ---------------------------------------------------------------- one student
def scale_input(field: str, scale: str, default: int, container=st):
    options = SCALES[scale]
    return container.select_slider(
        i18n.question(field, L), options=list(range(1, len(options) + 1)), value=default,
        format_func=lambda i: i18n.option_label(scale, i - 1, options[i - 1], L), key=f"q_{field}")


def questionnaire_form():
    hours = [0.25, 0.5] + [x / 2 for x in range(2, 24)]
    sleep = [x / 2 for x in range(8, 25)]
    days = MAPPING["value_maps"]["exercise_days"]
    with st.form("questionnaire"):
        st.markdown(f"**{ui.T('sec_q_identity')}**")
        c1, c2 = st.columns(2)
        gender = c1.radio(i18n.question("gender", L), ["Male", "Female"], horizontal=True, key="q_gender",
                          format_func=lambda g: {"Male": "Laki-laki", "Female": "Perempuan"}[g] if L == "id" else g)
        age = c2.number_input(ui.T("age_q"), 12, 30, 16, key="q_age")

        st.markdown(f"**{ui.T('sec_q_study')}**")
        c1, c2 = st.columns(2)
        f = {"gender": gender, "age": age}
        f["study_hours"] = c1.select_slider(i18n.question("study_hours", L), hours, value=2.0, key="q_study",
                                            format_func=lambda h: i18n.hours_label(h, L))
        f["report_grade"] = c2.number_input(i18n.question("report_grade", L), 0.0, 100.0, 82.0, 0.5, key="q_grade")
        f["late_night"] = scale_input("late_night", "late_night4", 2, c1)
        f["time_insufficient"] = scale_input("time_insufficient", "insufficient4", 2, c2)
        f["late_tasks"] = scale_input("late_tasks", "late_tasks4", 1, c1)

        st.markdown(f"**{ui.T('sec_q_pressure')}**")
        c1, c2 = st.columns(2)
        f["many_tasks"] = scale_input("many_tasks", "freq5", 3, c1)
        f["exam_stress"] = scale_input("exam_stress", "freq5", 3, c2)
        f["fear_parents"] = scale_input("fear_parents", "freq5", 3, c1)
        f["family_demand"] = scale_input("family_demand", "freq5", 3, c2)

        st.markdown(f"**{ui.T('sec_q_life')}**")
        c1, c2 = st.columns(2)
        f["sleep_duration"] = c1.select_slider(i18n.question("sleep_duration", L), sleep, value=7.0, key="q_sleep",
                                               format_func=lambda h: i18n.hours_label(h, L))
        day_labels = list(days)
        pick = c2.select_slider(i18n.question("exercise_days", L), list(range(len(day_labels))), value=1,
                                key="q_days",
                                format_func=lambda i: i18n.option_label("exercise_days", i, day_labels[i], L))
        f["exercise_days"] = days[day_labels[pick]]
        f["pocket_money"] = scale_input("pocket_money", "jajan5", 4, c1)

        st.markdown(f"**{ui.T('sec_q_burnout')}**")
        c1, c2, c3 = st.columns(3)
        f["time_split"] = scale_input("time_split", "agree5", 3, c1)
        f["exhausted"] = scale_input("exhausted", "agree5", 3, c2)
        f["lost_interest"] = scale_input("lost_interest", "agree5", 2, c3)
        submitted = st.form_submit_button(ui.T("submit"), type="primary")
    if submitted:
        features = gform.derive(pd.DataFrame([f])).iloc[0][config.FEATURES].to_dict()
        st.session_state["assess_features"] = features


def advanced_form():
    with st.form("advanced"):
        cols = st.columns(3)
        values = {}
        lo, hi, default = config.INPUT_RANGES["age"]
        values["age"] = cols[0].number_input(i18n.feature("age", L), lo, hi, default, key="a_age")
        values["gender"] = cols[1].selectbox(i18n.feature("gender", L), list(config.GENDER_MAP), key="a_gender")
        numeric = [c for c in config.FEATURES if c not in ("age", "gender")]
        for i, feat in enumerate(numeric):
            lo, hi, default = config.INPUT_RANGES[feat]
            values[feat] = cols[(i + 2) % 3].slider(i18n.feature(feat, L), float(lo), float(hi), float(default), 0.1,
                                                   help=i18n.feature_help(feat, L), key=f"a_{feat}")
        if st.form_submit_button(ui.T("submit"), type="primary"):
            st.session_state["assess_features"] = values


def render_result(features: dict):
    rf, meta = ui.load_active()
    a = recommend.assess(rf, meta, features, ui.weights(), ui.reference_quantiles())

    if a.safety:
        contact = config.REFERRAL_CONTACT[L]
        st.error(f"**{ui.T('safety_title')}** — " +
                 ui.T("safety_body", pct=100 - config.SAFETY_PERCENTILE, contact=contact), icon="🚨")

    m1, m2, m3 = st.columns(3)
    m1.metric(ui.T("res_pred"), f"{a.rf_score:.2f} / 10", help=ui.T("res_pred_help", p=a.rf_percentile))
    m2.metric(ui.T("res_priority"), f"{a.priority:.3f}", help=ui.T("res_priority_help", p=a.priority_percentile))
    m3.metric(ui.T("res_best"), i18n.alt(a.best, L), help=i18n.alt_desc(a.best, L))

    st.subheader(ui.T("res_top3"))
    cards = st.columns(3)
    for i, (alt, s) in enumerate(a.ranking.head(3).items()):
        with cards[i].container(border=True):
            st.markdown(f"**#{i + 1} {i18n.alt(alt, L)}** · `{s:.3f}`")
            st.caption(i18n.alt_desc(alt, L))
    if a.safety and "Counseling" not in a.ranking.head(3).index:
        st.info(f"➕ {i18n.alt('Counseling', L)} — {i18n.alt_desc('Counseling', L)}")

    st.subheader(ui.T("res_why"))
    for line in explain.narrative(a, ui.profile_label(), L):
        st.markdown(f"- {line}")
    st.caption(ui.T("res_contrib_help"))
    ui.show(plots.contribution_bars(a.contributions, L))

    with st.expander(ui.T("res_inputs")):
        table = pd.DataFrame({
            ui.T("criterion"): [i18n.feature(c, L) for c in config.CRITERIA],
            ui.T("value"): [round(float(a.criteria[c]), 2) for c in config.CRITERIA],
            ui.T("type"): [ui.T(config.CRITERIA_TYPE[c]) for c in config.CRITERIA],
            ui.T("utility"): [round(float(a.utility[c]), 3) for c in config.CRITERIA],
        })
        st.dataframe(table, hide_index=True, width="stretch")
        other = {i18n.feature(k, L): v for k, v in a.features.items() if k not in config.CRITERIA}
        st.caption(", ".join(f"{k}: {v:.2f}" if isinstance(v, float) else f"{k}: {v}" for k, v in other.items()))

    with st.expander(ui.T("res_sens")):
        st.caption(ui.T("res_sens_help"))
        sens = a.sensitivity
        grid = sens.pivot(index="criterion", columns="delta", values="best").reindex(config.CRITERIA)
        changed = sens.pivot(index="criterion", columns="delta", values="changed").reindex(config.CRITERIA)
        grid = grid.map(lambda x: i18n.alt(x, L))
        grid.index = [i18n.feature(c, L) for c in grid.index]
        grid.columns = [f"{d:+.0%}" for d in grid.columns]
        changed.index, changed.columns = grid.index, grid.columns
        st.dataframe(grid.style.apply(lambda _: changed.map(
            lambda c: "background-color: #f8d7da" if c else "").to_numpy(), axis=None), width="stretch")
        k = int(sens["changed"].sum())
        if k == 0:
            st.success(ui.T("res_sens_stable", k=len(sens), n=len(sens)))
        else:
            crit = sens.loc[sens["changed"], "criterion"].value_counts().index[0]
            st.warning(ui.T("res_sens_changes", k=k, n=len(sens), crit=i18n.feature(crit, L)))


with tab_one:
    mode = st.radio(ui.T("mode"), ["q", "adv"], horizontal=True, key="input_mode",
                    format_func=lambda m: ui.T("mode_q" if m == "q" else "mode_adv"), help=ui.T("mode_help"))
    if mode == "q":
        questionnaire_form()
    else:
        advanced_form()
    if "assess_features" in st.session_state:
        st.divider()
        render_result(st.session_state["assess_features"])


# ---------------------------------------------------------------- many students
def load_batch(upload):
    """Returns (frame with FEATURES [+ target], info message) or raises ValueError with a user message."""
    if upload is None:
        choice = st.radio(ui.T("batch_default"), ["kaggle", "gform"], horizontal=True, key="batch_demo",
                          format_func=lambda k: ui.T(f"batch_demo_{k}"))
        if choice == "kaggle":
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
        note = ui.T("batch_detected_csv", n=len(frame))
        problems = {k: v for k, v in issues.items() if v and k != "missing"}
        if problems:
            note += f" ⚠️ {problems}"
        return frame, note
    try:
        prepared = gform.prepare(raw)
    except ValueError as err:
        if gform.looks_like_gform(raw):
            raise ValueError(ui.T("batch_bad", err=err)) from err
        missing = data.validate_columns(raw)
        raise ValueError(ui.T("batch_missing_cols", cols=missing, need=config.FEATURES)) from err
    dropped = prepared.report["pii_columns_dropped"]
    note = ui.T("batch_detected_gform", n=len(prepared.data), k=len(dropped), cols=", ".join(dropped))
    frame = prepared.data.drop(columns=[c for c in prepared.data if c.startswith("x_")])
    frame.index.name = "student_id"
    return frame, note


with tab_many:
    upload = st.file_uploader(ui.T("batch_upload"), type=["csv", "xlsx"])
    try:
        frame, note = load_batch(upload)
    except ValueError as err:
        st.error(str(err))
        st.stop()
    if note:
        st.info(note)

    n_missing = int(frame[config.FEATURES].isna().sum().sum())
    if n_missing:
        frame = gform.impute(frame, ui.impute_medians())
        st.caption(ui.T("batch_imputed", n=n_missing))

    use_ref = st.checkbox(ui.T("batch_bounds"), value=True, key="batch_use_ref")
    result, utility = ui.score(frame, ui.profile_key(), use_ref)

    top_n = st.slider(ui.T("batch_topn"), 10, min(500, max(10, len(result))), min(20, len(result)), 10)
    view = result.head(top_n).copy()
    view["Best_Recommendation"] = view["Best_Recommendation"].map(lambda x: i18n.alt(x, L))
    cols = ["rank", "smart_score", "Best_Recommendation", "Recommendation_Score", "rf_anxiety_score"]
    labels = {"rank": ui.T("rank"), "smart_score": i18n.feature("smart_score", L),
              "Best_Recommendation": ui.T("res_best"), "Recommendation_Score": ui.T("score"),
              "rf_anxiety_score": i18n.feature("rf_anxiety_score", L)}
    st.dataframe(view[cols + config.ALTERNATIVES].rename(columns=labels | {a: i18n.alt(a, L) for a in config.ALTERNATIVES}),
                 width="stretch")
    st.download_button(ui.T("batch_download"), result.to_csv().encode(), "smart_ranking.csv", "text/csv")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**{ui.T('batch_dist')}**")
        ui.show(plots.recommendation_mix(result, L))
    with c2:
        ui.show(plots.score_histogram(result["smart_score"], L))

    if config.TARGET in frame and frame[config.TARGET].notna().sum() >= 5:
        st.subheader(ui.T("batch_eval"))
        st.caption(ui.T("batch_eval_help"))
        labeled = frame.dropna(subset=[config.TARGET])
        rf, meta = ui.load_active()
        base, _ = ui.load_base()
        rows = {}
        for name, m in {"active": rf, "base (Kaggle)": base}.items():
            rows[name] = model.metrics(labeled[config.TARGET], model.predict(m, labeled[config.FEATURES]))
        st.dataframe(pd.DataFrame(rows).T[["mae", "rmse", "r2"]].round(4), width="stretch")
        ui.show(plots.actual_vs_predicted(labeled[config.TARGET], model.predict(rf, labeled[config.FEATURES]), L))

ui.footer()
