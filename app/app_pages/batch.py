"""App zone, a whole class: upload answers (or try a small demo class) -> who to refer, a priority list, and
student groups per kind of support."""
import html

import pandas as pd
import streamlit as st

import result_views as rv
import ui
from spk import config, data, gform, i18n, model, plots, recommend

L = ui.lang()
T = ui.T

with st.container(horizontal=True, vertical_alignment="bottom", gap="small"):
    with st.container():
        ui.page_header(T("class_title"), T("class_lead"))
    ui.model_picker()
st.space("small")


# ---------------------------------------------------------------- whole class
DEMO_SIZE = 30


def demo_class() -> pd.DataFrame:
    """A class-sized demo from the Kaggle test sample (no real student is ever bundled): 5 rows from the
    top 3% of actual anxiety, so the referral list is not empty, plus 25 others. Fixed seed, same every time."""
    ref = ui.load_reference()
    anxious = ref[ref[config.TARGET] >= ref[config.TARGET].quantile(0.97)].sample(5, random_state=config.RANDOM_STATE)
    others = ref.drop(anxious.index).sample(DEMO_SIZE - 5, random_state=config.RANDOM_STATE)
    return pd.concat([anxious, others])[config.FEATURES]


def template_csv() -> bytes:
    """A CSV with the 11 model columns and two example rows, for schools without the Google Form."""
    rows = pd.DataFrame([ui.example_features(k) for k in ("high", "low")], index=["SISWA01", "SISWA02"])
    rows.index.name = "student_id"
    return rows[config.FEATURES].round(1).to_csv().encode()


def load_batch(upload):
    """Returns (frame with FEATURES [+ target], info message) or raises ValueError with a user message."""
    if upload is None:
        return demo_class(), T("class_demo_note", n=DEMO_SIZE)
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
    short = [h if len(h) <= 40 else h[:39] + "…" for h in dropped]   # the essay title is long
    note = T("batch_detected_gform", n=len(prepared.data), k=len(dropped), cols=", ".join(short))
    frame = prepared.data.drop(columns=[c for c in prepared.data if c.startswith("x_")])
    frame.index.name = "student_id"
    return frame, note


def start_panel():
    """Upload on the left; demo switch, template and how-to on the right. Returns the upload or None."""
    up, side = st.columns([1.6, 1], gap="medium")
    with up:
        upload = st.file_uploader(T("batch_upload"), type=["csv", "xlsx"])
        st.caption(T("batch_upload_help"))
    with side.container(border=True, key="card_demo"):
        st.markdown(f"**{T('batch_demo_title')}**")
        st.toggle(T("class_demo_toggle", n=DEMO_SIZE), key="batch_demo", disabled=upload is not None)
        st.download_button(T("class_template"), template_csv(), "template_kelas.csv", "text/csv",
                           icon=":material/download:", type="tertiary")
    return upload


def empty_state():
    with st.container(border=True, key="card_class_empty"):
        st.markdown(f"**{T('class_empty_t')}**")
        st.markdown("\n".join(f"{i}. {T(f'class_empty_{i}')}" for i in range(1, 4)))


def names(ids) -> str:
    return ", ".join(html.escape(str(i)) for i in ids)


def urgent_section(result: pd.DataFrame, cutoff: float):
    urgent = result[result["urgent"]]
    ui.section(T("class_urgent_t"), T("class_urgent_d", group=ui.reference_group(), cut=cutoff))
    if urgent.empty:
        st.success(T("class_urgent_none"), icon=":material/check_circle:")
        return
    st.dataframe(
        urgent[["rf_anxiety_score", "smart_score", "rec"]], width="stretch",
        column_config={
            "_index": st.column_config.TextColumn(T("student_id")),
            "rf_anxiety_score": st.column_config.NumberColumn(i18n.feature("rf_anxiety_score", L), format="%.2f"),
            "smart_score": st.column_config.NumberColumn(i18n.feature("smart_score", L), format="%.3f"),
            "rec": st.column_config.TextColumn(T("class_rec_col")),
        })
    st.caption(T("class_urgent_note", contact=config.REFERRAL_CONTACT[L]))


def priority_section(result: pd.DataFrame):
    ui.section(T("batch_list"), T("batch_list_help"))
    c1, c2, c3 = st.columns([2, 1.1, 1], gap="medium", vertical_alignment="bottom")
    alts = c1.multiselect(T("class_filter_alt"), config.ALTERNATIVES, key=f"class_alts_{L}",
                          format_func=lambda a: i18n.alt(a, L), placeholder=T("class_filter_all"))
    only_urgent = c2.checkbox(T("class_filter_urgent"), key="class_only_urgent")
    detail = c3.toggle(T("class_detail"), key="class_detail")
    view = result
    if alts:
        view = view[view["Best_Recommendation"].isin(alts)]
    if only_urgent:
        view = view[view["urgent"]]
    st.caption(T("class_shown", n=len(view), total=len(result)))
    cols = ["rank", "smart_score", "rf_anxiety_score", "rec", "urgent"] + (config.ALTERNATIVES if detail else [])
    progress = st.column_config.ProgressColumn
    st.dataframe(
        view[cols], width="stretch", height=min(38 + 35 * len(view), 420),
        column_config={
            "_index": st.column_config.TextColumn(T("student_id")),
            "rank": st.column_config.NumberColumn(T("rank"), format="%d", width="small"),
            "smart_score": progress(i18n.feature("smart_score", L), min_value=0.0, max_value=1.0, format="%.3f"),
            "rf_anxiety_score": progress(i18n.feature("rf_anxiety_score", L), min_value=0.0, max_value=10.0, format="%.2f"),
            "rec": st.column_config.TextColumn(T("res_best")),
            "urgent": st.column_config.CheckboxColumn(T("class_refer_col"), width="small"),
        } | {a: st.column_config.NumberColumn(i18n.alt(a, L), format="%.3f") for a in config.ALTERNATIVES})


def program_section(result: pd.DataFrame):
    """One card per kind of support: how many students, and who (highest priority first)."""
    ui.section(T("class_program_t"), T("class_program_d"))
    cols = st.columns(len(config.ALTERNATIVES), gap="small")
    shown = 8
    for col, alt in zip(cols, config.ALTERNATIVES):
        group = result[result["Best_Recommendation"] == alt]
        extra = result[result["urgent"] & (result["Best_Recommendation"] != alt)] if alt == "Counseling" else None
        with col.container(border=True, key=f"card_prog_{alt}", height="stretch"):
            ids = list(group.index[:shown])
            more = len(group) - len(ids)
            body = names(ids) + (f" {T('class_more', n=more)}" if more > 0 else "") if ids else T("class_program_none")
            add = (f"<p class='spk-prog-extra'>{T('class_program_referred', n=len(extra))}</p>"
                   if extra is not None and len(extra) else "")
            st.html(f"<div class='spk-prog'><span class='spk-icon spk-icon-tile'>{ui.ALT_ICONS[alt]}</span>"
                    f"<p class='spk-prog-name'>{html.escape(i18n.alt(alt, L))}</p>"
                    f"<p class='spk-prog-n'>{len(group)}</p><p class='spk-prog-ids'>{body}</p>{add}</div>")


def one_student(result: pd.DataFrame, frame: pd.DataFrame):
    ui.section(T("class_one_t"), T("class_one_d"))
    with st.container(border=True, key="card_one"):
        c1, c2 = st.columns([1, 1.6], gap="large", vertical_alignment="top")
        sid = c1.selectbox(T("xai_pick"), list(result.index), key="xai_pick_batch")
        feats = frame.loc[[sid], config.FEATURES].iloc[0].to_dict()
        rf, meta = ui.load_active()
        one = recommend.assess(rf, meta, feats, ui.weights(), ui.reference_quantiles())
        c1.markdown(f"**{i18n.alt(one.best, L)}** · {T('res_pred')} {one.rf_score:.2f} / 10")
        if c1.button(T("class_calc_btn"), icon=":material/arrow_forward:", icon_position="right", key="open_calc"):
            ui.open_calculation(feats)
        c2.html(rv.ranking_bars(one))


def evaluation(frame: pd.DataFrame):
    if config.TARGET not in frame or frame[config.TARGET].notna().sum() < 5:
        return
    st.space("small")
    ui.section(T("batch_eval"), T("batch_eval_help"))
    labeled = frame.dropna(subset=[config.TARGET])
    rf, _ = ui.load_active()
    base, _ = ui.load_base()
    labels = {"active": "Model aktif" if L == "id" else "Active model",
              "base": "Model dasar (Kaggle)" if L == "id" else "Base model (Kaggle)"}
    rows = {labels[key]: model.metrics(labeled[config.TARGET], model.predict(m, labeled[config.FEATURES]))
            for key, m in {"active": rf, "base": base}.items()}
    c1, c2 = st.columns([3, 2], gap="medium")
    with c1:
        st.table(pd.DataFrame(rows).T[["mae", "rmse", "r2"]].rename(
            columns={"mae": "MAE", "rmse": "RMSE", "r2": "R²"}).round(4))
        st.caption(f"n = {len(labeled)}")
    with c2.container(border=True, key="card_eval"):
        ui.show(plots.actual_vs_predicted(labeled[config.TARGET], model.predict(rf, labeled[config.FEATURES]), L))


def batch_view():
    upload = start_panel()
    if upload is None and not st.session_state.get("batch_demo"):
        empty_state()
        return
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
    result, _ = ui.score(frame, use_ref)
    quantiles = ui.reference_quantiles()
    cutoff = recommend.cutoff(quantiles["rf_anxiety_score"])
    high_prio = float(quantiles["smart_score"][60])
    result = result.assign(urgent=result["rf_anxiety_score"] >= cutoff,
                           rec=result["Best_Recommendation"].map(lambda x: i18n.alt(x, L)))

    # Summary first: how many students, who must be referred, how many are high priority, what is needed most.
    mix = result["Best_Recommendation"].value_counts()
    m = st.columns(4, gap="small")
    m[0].metric(T("batch_n"), f"{len(result):,}", border=True)
    m[1].metric(T("batch_urgent"), f"{int(result['urgent'].sum()):,}", border=True,
                help=T("batch_urgent_help", group=ui.reference_group(), cut=cutoff))
    m[2].metric(T("class_high_prio"), f"{int((result['smart_score'] >= high_prio).sum()):,}", border=True,
                help=T("class_high_prio_help", group=ui.reference_group(), cut=high_prio))
    m[3].metric(T("batch_top_alt"), i18n.alt(mix.index[0], L), border=True)

    st.space("small")
    urgent_section(result, cutoff)
    st.space("small")
    priority_section(result)
    export = result.assign(program=result["Best_Recommendation"])[
        ["rank", "smart_score", "rf_anxiety_score", "program", "urgent"] + config.ALTERNATIVES]
    st.download_button(T("batch_download"), export.round(4).to_csv().encode(), "rencana_kelas.csv", "text/csv",
                       icon=":material/download:")
    st.space("small")
    program_section(result)
    st.space("small")
    one_student(result, frame)

    with st.expander(T("batch_options"), icon=":material/settings:"):
        st.checkbox(T("batch_bounds"), value=True, key="batch_use_ref")
    evaluation(frame)


batch_view()
ui.footer()
