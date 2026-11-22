"""App zone, one student: questionnaire (or the 11 model values) -> a short, clear result.

The full calculation for the same student lives in report chapter 3 (app_pages/report/calculation.py).
"""
import html

import pandas as pd
import streamlit as st

import result_views as rv
import ui
from spk import config, explain, gform, i18n, recommend

L = ui.lang()
T = ui.T
MAPPING = gform.load_mapping()
SCALES = MAPPING["scales"]

with st.container(horizontal=True, vertical_alignment="bottom", gap="small"):
    with st.container():
        ui.page_header(T("student_title"), T("student_lead"))
    ui.model_picker()
st.space("small")


# ---------------------------------------------------------------- one student: input
HOURS = [0.25, 0.5] + [x / 2 for x in range(2, 24)]
SLEEP = [x / 2 for x in range(8, 25)]
DAYS = MAPPING["value_maps"]["exercise_days"]          # answer label -> days per week
DAY_LABELS = list(DAYS)
# Widget key per form field (the language is appended: option labels change with it).
WIDGET = {"gender": "q_gender", "age": "q_age", "study_hours": "q_study", "report_grade": "q_grade",
          "sleep_duration": "q_sleep", "exercise_days": "q_days"}


def widget_key(field: str) -> str:
    return f"{WIDGET.get(field, 'q_' + field)}_{L}"


def show_result(features: dict):
    st.session_state["assess_features"] = features
    st.session_state["reco_step"] = "result"
    st.session_state["scroll_top"] = True


def edit_answers():
    st.session_state["reco_step"] = "form"


def clear_answers():
    for k in [k for k in st.session_state if k.startswith("q_") or k == "example_loaded"]:
        del st.session_state[k]


def new_assessment():
    clear_answers()
    st.session_state.pop("assess_features", None)
    st.session_state["reco_step"] = "form"


def fill_example(kind: str):
    """Put an example student's answers into the form. The counselor reviews them and submits."""
    for field, value in config.EXAMPLE_ANSWERS[kind].items():
        st.session_state[widget_key(field)] = (DAY_LABELS.index(next(k for k, v in DAYS.items() if v == value))
                                               if field == "exercise_days" else value)
    st.session_state["example_loaded"] = kind


def q_section(n: int, title: str, hint: str | None = None):
    """A numbered card that groups related questions."""
    box = st.container(border=True, key=f"card_q{n}")
    hint_html = f"<p class='spk-q-hint'>{html.escape(hint)}</p>" if hint else ""
    box.html(f"<div class='spk-q-head'><span class='spk-step'>{n}</span>"
             f"<div><p class='spk-q-title'>{html.escape(title)}</p>{hint_html}</div></div>")
    return box


def scale_input(field: str, scale: str, container):
    options = gform.scale_labels(SCALES[scale])
    return container.radio(
        i18n.question(field, L), options=list(range(1, len(options) + 1)), index=None, horizontal=True,
        format_func=lambda i: i18n.option_label(scale, i - 1, options[i - 1], L), key=widget_key(field),
        persist_state="session")


def questionnaire_form():
    """18 questions, all empty at the start. Nothing is assumed: every answer must be given."""
    f = {}
    pick = T("q_pick")
    with st.form("questionnaire", border=False):
        box = q_section(1, T("sec_q_identity"), T("sec_q_identity_hint"))
        c1, c2 = box.columns(2, gap="medium")
        f["gender"] = c1.radio(i18n.question("gender", L), ["Male", "Female"], index=0, horizontal=True,
                               key=widget_key("gender"), persist_state="session",
                               format_func=lambda g: {"Male": "Laki-laki", "Female": "Perempuan"}[g] if L == "id" else g)
        f["age"] = c2.number_input(T("age_q"), 12, 30, "min", key=widget_key("age"), placeholder=T("q_type"),
                                   persist_state="session")

        box = q_section(2, T("sec_q_study"), T("sec_q_study_hint"))
        c1, c2 = box.columns(2, gap="medium", vertical_alignment="bottom")
        f["study_hours"] = c1.selectbox(i18n.question("study_hours", L), HOURS, index=None, placeholder=pick,
                                        key=widget_key("study_hours"), persist_state="session",
                                        format_func=lambda h: i18n.hours_label(h, L))
        f["report_grade"] = c2.number_input(i18n.question("report_grade", L), 0.0, 100.0, "min", 0.5,
                                            key=widget_key("report_grade"), placeholder=T("q_type"),
                                            persist_state="session")
        f["late_night"] = scale_input("late_night", "late_night5", box)
        f["time_insufficient"] = scale_input("time_insufficient", "insufficient4", box)
        f["late_tasks"] = scale_input("late_tasks", "late_tasks5", box)
        f["below_target"] = scale_input("below_target", "freq5a", box)

        box = q_section(3, T("sec_q_pressure"), T("sec_q_pressure_hint"))
        f["many_tasks"] = scale_input("many_tasks", "freq5", box)
        f["exam_stress"] = scale_input("exam_stress", "freq5", box)
        f["fear_parents"] = scale_input("fear_parents", "freq5", box)
        f["family_demand"] = scale_input("family_demand", "freq5", box)

        box = q_section(4, T("sec_q_life"), T("sec_q_life_hint"))
        f["sleep_duration"] = box.selectbox(i18n.question("sleep_duration", L), SLEEP, index=None, placeholder=pick,
                                            key=widget_key("sleep_duration"), persist_state="session",
                                            format_func=lambda h: i18n.hours_label(h, L))
        day = box.radio(i18n.question("exercise_days", L), list(range(len(DAY_LABELS))), index=None, horizontal=True,
                        key=widget_key("exercise_days"), persist_state="session",
                        format_func=lambda i: i18n.option_label("exercise_days", i, DAY_LABELS[i], L))
        f["exercise_days"] = None if day is None else DAYS[DAY_LABELS[day]]
        f["pocket_money"] = scale_input("pocket_money", "jajan5", box)

        box = q_section(5, T("sec_q_burnout"), T("sec_q_burnout_hint"))
        f["time_split"] = scale_input("time_split", "agree5", box)
        f["exhausted"] = scale_input("exhausted", "agree5", box)
        f["lost_interest"] = scale_input("lost_interest", "agree5", box)
        submitted = st.form_submit_button(T("submit"), type="primary", icon=":material/arrow_forward:",
                                          icon_position="right", width="stretch")
    if submitted:
        missing = [field for field, value in f.items() if value is None]
        if missing:
            names = [T("age_q") if m == "age" else i18n.question(m, L) for m in missing]
            st.error(T("q_missing", n=len(missing)) + "\n\n" + "\n".join(f"- {n}" for n in names),
                     icon=":material/error:")
            return
        st.session_state.pop("example_loaded", None)
        show_result(gform.derive(pd.DataFrame([f])).iloc[0][config.FEATURES].to_dict())
        st.rerun()


def input_view():
    main, side = st.columns([2.2, 1], gap="large")
    with side.container(key="side_sticky"):
        with st.container(border=True, key="card_tips"):
            st.markdown(f"**{T('tips_title')}**")
            st.markdown("\n".join(f"- {T(f'tips_{i}')}" for i in range(1, 5)))
        with st.container(border=True, key="card_examples"):
            st.markdown(f"**{T('examples')}**")
            st.caption(T("examples_help"))
            for kind in ("high", "low"):
                st.button(T(f"example_{kind}"), key=f"example_{kind}", width="stretch",
                          on_click=fill_example, args=(kind,))
            st.button(T("q_clear"), key="clear_answers", width="stretch", type="tertiary",
                      icon=":material/restart_alt:", on_click=clear_answers)
    with main:
        loaded = st.session_state.get("example_loaded")
        if loaded:
            st.info(T("example_loaded", name=T(f"example_{loaded}")), icon=":material/edit_note:")
        questionnaire_form()


# ---------------------------------------------------------------- one student: result
def render_result(features: dict):
    rf, meta = ui.load_active()
    a = recommend.assess(rf, meta, features, ui.weights(), ui.reference_quantiles())

    if st.session_state.pop("scroll_top", False):
        ui.scroll_to_top()
    st.button(T("back_edit"), icon=":material/arrow_back:", type="tertiary", on_click=edit_answers)

    if a.safety:
        st.error(f"**{T('safety_title')}** · " +
                 T("safety_body", pct=100 - config.SAFETY_PERCENTILE, contact=config.REFERRAL_CONTACT[L]),
                 icon=":material/priority_high:")

    with st.container(border=True, key="card_hero"):
        st.html(rv.hero_html(a))

    c1, c2 = st.columns([1, 1.15], gap="medium")
    with c1.container(border=True, key="card_rank", height="stretch"):
        st.markdown(f"**{T('res_rank')}**")
        st.caption(T("res_rank_help"))
        st.html(rv.ranking_bars(a))
    with c2.container(border=True, key="card_why", height="stretch"):
        st.markdown(f"**{T('res_why', alt=i18n.alt(a.best, L))}**")
        st.markdown("\n".join(f"- {line}" for line in explain.narrative(a, L, ui.reference_group())))

    rv.factor_card(features, "result")

    with st.container(border=True, key="card_cta", horizontal=True, vertical_alignment="center", gap="medium"):
        with st.container():
            st.markdown(f"**{T('cta_calc_t')}**")
            st.caption(T("cta_calc_d"))
        if st.button(T("cta_calc_btn"), icon=":material/arrow_forward:", icon_position="right", key="open_calc"):
            ui.open_calculation()

    # Starting over clears the form; "Ubah jawaban" above keeps the answers.
    st.button(T("next_student"), icon=":material/person_add:", type="tertiary", on_click=new_assessment,
              key="next_student")


# ---------------------------------------------------------------- page body
if st.session_state.get("assess_features") and st.session_state.get("reco_step") != "form":
    render_result(st.session_state["assess_features"])
else:
    input_view()

ui.footer()
