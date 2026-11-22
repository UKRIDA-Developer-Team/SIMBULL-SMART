"""Report chapter 7: the CRISP-DM process, one phase at a time, with live numbers."""
import html
import json

import pandas as pd
import streamlit as st

import report
import ui
from spk import config, crispdm, data, gform, i18n, plots, smart

L = ui.lang()
T = ui.T
rf, meta = ui.load_active()
reference = ui.load_reference()
comparison = ui.model_comparison() or {}
summary = ui.real_summary()
TEXT = json.loads(ui.content("crispdm", ".json"))
PHASES = TEXT["phases"]


# ---------------------------------------------------------------- cached facts

@st.cache_data(show_spinner=False)
def column_decisions() -> pd.DataFrame:
    return crispdm.column_decisions(data.load_dataset())


@st.cache_data(show_spinner=False)
def quality() -> dict:
    """Quality of the reference population (20,000 test rows, all 20 Kaggle columns)."""
    return crispdm.data_quality(data.load_dataset(clean_rows=False))


@st.cache_data(show_spinner=False)
def merge_summary() -> pd.DataFrame:
    return gform.merge_summary()


@st.cache_data(show_spinner=False)
def stability_a() -> float:
    _, utility = ui.score(reference[config.FEATURES], True)
    return smart.stability(utility, config.WEIGHTS_A, n=100, pct=0.1)["top1_unchanged"]


# ---------------------------------------------------------------- building blocks

def go(i: int):
    """Prev/next buttons. A mounted widget ignores a new default, so the stepper gets a fresh key."""
    st.session_state["dm_phase"] = i
    st.session_state["dm_nonce"] = st.session_state.get("dm_nonce", 0) + 1
    st.session_state["dm_scroll_top"] = True


def stepper() -> int:
    """Phase picker. The choice lives in dm_phase; the widget key carries the language (labels
    change) and a counter that the Prev/Next buttons bump."""
    current = st.session_state.get("dm_phase", 0)
    current = current if current in range(len(PHASES)) else 0
    phase = st.segmented_control(
        T("dm_cycle"), list(range(len(PHASES))), default=current, required=True, width="stretch",
        key=f"dm_phase_{L}_{st.session_state.get('dm_nonce', 0)}", label_visibility="collapsed",
        format_func=lambda i: f"{i + 1} · {PHASES[i]['name']}")
    st.session_state["dm_phase"] = phase
    return phase


def card(key: str):
    return st.container(border=True, key=f"card_dm_{key}", height="stretch")


def kpis(items: list[tuple[str, str]]):
    cols = st.columns(len(items), gap="small")
    for col, (label, value) in zip(cols, items):
        col.metric(label, value, border=True)


def flow(lane: str, items: list[str]) -> str:
    arrow = "<span class='spk-icon spk-flow-arrow'>arrow_forward</span>"
    chips = arrow.join(f"<span class='spk-flow-chip'>{html.escape(t)}</span>" for t in items)
    return f"<div class='spk-flow'><span class='spk-flow-lane'>{html.escape(lane)}</span>{chips}</div>"


def table(spec: dict):
    st.markdown(f"**{spec['title']}**")
    st.table(pd.DataFrame(spec["rows"], columns=spec["columns"]).set_index(spec["columns"][0]))


def side(p: dict):
    """Right-hand card: key decisions, outputs and where the code lives."""
    with card("side"):
        st.markdown(f"**{T('dm_decisions')}**")
        st.markdown("\n".join(f"- {d}" for d in p["decisions"]))
        st.markdown(f"**{T('dm_outputs')}**")
        st.html("<div class='spk-tags'>" + "".join(f"<span class='spk-tag'>{html.escape(o)}</span>"
                                                    for o in p["outputs"]) + "</div>")
        st.markdown(f"**{T('dm_code')}**")
        st.html("<div class='spk-code-list'>" + "".join(f"<code>{html.escape(c)}</code>" for c in p["code"]) + "</div>")


# ---------------------------------------------------------------- header and stepper
if st.session_state.pop("dm_scroll_top", False):
    ui.scroll_to_top(st.session_state.get("dm_nonce", 0))
ch = report.Chapter(7, [], settings=False)
phase = stepper()
st.caption(f":material/autorenew: {TEXT['loop']}")
p = PHASES[phase]

with st.container(border=True, key="card_dm_hero"):
    st.html(f"""
<div class="spk-phase-hero">
  <span class="spk-icon spk-icon-tile">{p['icon']}</span>
  <div>
    <p class="spk-phase-n">{T('dm_phase_of', i=phase + 1, n=len(PHASES))}</p>
    <p class="spk-phase-title">{html.escape(p['name'])}</p>
    <p class="spk-phase-q">{html.escape(p['question'])}</p>
  </div>
</div>""")

# ---------------------------------------------------------------- live numbers per phase
X_test, y_test = ui.kaggle_test_set()
rows = ui.load_base()[1].get("rows", {})          # row counts of each preparation step (base model)
age_lo, age_hi = config.AGE_RANGE
if phase == 0:
    kpis([(T("dm_k_bgoals"), "3"), (T("dm_k_dmgoals"), "4"), (T("dm_kpi_criteria"), str(len(config.CRITERIA))),
          (T("dm_k_alts"), str(len(config.ALTERNATIVES)))])
elif phase == 1:
    q = quality()
    kpis([(T("dm_kpi_rows"), f"{q['rows']:,}"), (T("dm_columns_n"), str(q["columns"])),
          (T("dm_missing"), str(q["missing"])), (T("dm_duplicates"), str(q["duplicates"]))])
elif phase == 2:
    kpis([(T("dm_split_full"), f"{rows.get('full', 0):,}"),
          (T("dm_split_age", lo=age_lo, hi=age_hi), f"{rows.get('age_filtered', 0):,}"),
          (T("dm_split_train"), f"{rows.get('train', 0):,}"), (T("dm_split_test"), f"{rows.get('test', 0):,}")])
elif phase == 3:
    hp = meta.get("hyperparameters", {})
    rf_cv = comparison.get("Random Forest (deployed)", {}).get("cv_mae")
    kpis([(T("dm_k_trees"), str(meta.get("n_estimators_total", hp.get("n_estimators")))),
          (T("dm_k_depth"), str(hp.get("max_depth"))),
          (T("dm_k_cvmae"), f"{rf_cv:.3f}" if rf_cv else "-"), (T("dm_k_algos"), str(len(comparison) or "-"))])
elif phase == 4:
    tests = crispdm.count_tests(config.APP_DIR / "tests")
    kpis([(T("dm_kpi_mae"), f"{meta['metrics']['mae']:.3f}"), (T("dm_kpi_r2"), f"{meta['metrics']['r2']:.3f}"),
          (T("dm_k_stability"), f"{stability_a():.1%}"), (T("dm_k_tests"), f"{tests['blackbox']} + {tests['whitebox']}")])
else:
    kpis([(T("dm_k_pages"), f"{len(ui.ZONES['app'])} + {len(ui.ZONES['report'])}"), (T("dm_k_langs"), "ID · EN"), (T("dm_k_source"), ui.T(
        {"kaggle": "src_kaggle", "kaggle+gform": "src_real", "gform": "src_gform"}[meta["data_source"]])),
          ("scikit-learn", meta.get("sklearn_version", "?"))])

# ---------------------------------------------------------------- what was done
st.space("small")
ui.section(T("dm_did"))
cols = st.columns(len(p["steps"]), gap="small")
for i, (col, step) in enumerate(zip(cols, p["steps"]), start=1):
    with col.container(border=True, key=f"card_dm_step{i}", height="stretch"):
        st.html(f"<span class='spk-step'>{i}</span>")
        st.markdown(f"**{step['t']}**")
        st.caption(step["d"])

# ---------------------------------------------------------------- evidence + decisions
st.space("small")
main, right = st.columns([1.45, 1], gap="medium")
with right:
    side(p)
with main, card("main"):
    if phase == 0:
        table(p["table"])
        st.markdown(f"**{T('about_criteria')}**")
        st.table(pd.DataFrame({T("criterion"): [i18n.feature(c, L) for c in config.CRITERIA],
                               T("type"): [T(config.CRITERIA_TYPE[c]) for c in config.CRITERIA]}).set_index(T("criterion")))

    elif phase == 1:
        decisions = column_decisions()
        role_labels = {r: T(f"dm_role_{r}") for r in set(crispdm.COLUMN_ROLES.values()) | {"unused"}}
        ui.show(plots.target_correlation_bars(decisions.drop(index=config.TARGET, errors="ignore"), role_labels, L),
                compact=True)
        with st.expander(T("dm_columns"), icon=":material/table_rows:"):
            st.dataframe(pd.DataFrame({
                "r": decisions["r"].map(lambda v: "-" if pd.isna(v) else f"{v:+.2f}"),
                T("dm_role"): decisions["role"].map(role_labels)}), width="stretch")

    elif phase == 2:
        st.markdown(f"**{T('dm_pipeline')}**")
        st.html(flow("Kaggle", ["1M", T("dm_split_age", lo=age_lo, hi=age_hi),
                                "Seleksi 11 fitur" if L == "id" else "Select 11 features", "Encoding gender",
                                "Split 80/20 per usia" if L == "id" else "Split 80/20 by age", "Random Forest"]))
        st.html(flow("Google Form", ["Cocokkan kolom" if L == "id" else "Match columns",
                                     "Buang data pribadi" if L == "id" else "Drop personal data",
                                     "Teks → angka" if L == "id" else "Text → numbers",
                                     "11 fitur + target" if L == "id" else "11 features + target",
                                     "Imputasi" if L == "id" else "Imputation", "Holdout + CV"]))
        st.caption(T("dm_split_note", lo=age_lo, hi=age_hi, dropped=f"{rows.get('dropped', 0):,}",
                     amin=int(reference["age"].min()), amax=int(reference["age"].max()),
                     ref=f"{rows.get('reference', len(reference)):,}"))
        st.space("small")
        table(p["table"])
        with st.expander(T("dm_merge_title"), icon=":material/merge:"):
            merged = merge_summary()
            names = merged.index.map(lambda c: i18n.feature(c, L) if c in config.FEATURES + [config.TARGET] else c)
            st.dataframe(pd.DataFrame({
                T("dm_merge_n"): merged["questions"].to_list(),
                T("dm_merge_fields"): merged["fields"].to_list(),
                T("dm_merge_rule"): merged["rule"].to_list(),
                T("dm_merge_role"): [T(f"dm_merge_role_{r}") for r in merged["role"]],
            }, index=pd.Index(names, name=T("dm_merge_output"))), width="stretch")
            st.caption(T("dm_merge_note"))

    elif phase == 3:
        if comparison:
            st.markdown(f"**{T('dm_algos')}**")
            algos = pd.DataFrame(comparison).T[["cv_mae", "cv_r2", "test_mae", "test_r2"]].sort_values("cv_mae")
            ui.show(plots.metric_bars(algos["cv_mae"].to_dict(), "algo", "Random Forest (deployed)", L), compact=True)
            st.table(algos.round(3).rename(columns={"cv_mae": "MAE CV", "cv_r2": "R² CV", "test_mae": "MAE test",
                                                    "test_r2": "R² test"}))
        table(p["table"])
        st.caption(ui.model_note())

    elif phase == 4:
        # D1-D3 judge the Kaggle base model on the Kaggle test set; D4 judges the retraining on real data.
        perm = ui.permutation_importance(base=True)
        base_meta = ui.load_base()[1]
        baseline = comparison.get("Mean baseline", {}).get("test_mae")
        criteria = crispdm.success_criteria(base_meta["metrics"], baseline, list(perm.index), stability_a(), summary)
        criteria.loc["D3", "value"] = ", ".join(i18n.feature(f, L) for f in perm.index[:2])
        st.markdown(f"**{T('dm_success')}**")
        st.table(pd.DataFrame({
            T("dm_criterion"): [T(f"dm_crit_{c}") for c in criteria.index],
            T("dm_result"): [T("dm_no_result") if v in ("", "-") else v for v in criteria["value"]],
            T("dm_status"): [T(f"dm_{s}") for s in criteria["status"]],
        }).set_index(T("dm_criterion")))
        st.caption(T("dm_stability_note", n=f"{len(reference):,}") + " " + T("dm_s4_note"))
        tests = crispdm.count_tests(config.APP_DIR / "tests")
        st.markdown(f"**{T('dm_testing')}**")
        t = st.columns(3, gap="small")
        t[0].metric(T("dm_tests_bb"), tests["blackbox"])
        t[1].metric(T("dm_tests_wb"), tests["whitebox"])
        t[2].metric(T("dm_tests_total"), tests["total"])
        st.caption(T("dm_tests_note"))
        st.page_link(ui.PAGE_FILE["ch5"], label=T("dm_open_analysis"), icon=":material/monitoring:")

    else:
        st.markdown(f"**{T('dm_arch')}**")
        st.html(flow("Offline", ["Kaggle + Google Form", "scripts/train.py", "models/*.joblib + metadata"]))
        st.html(flow("Online", ["Streamlit Cloud", "spk/ (RF, SMART, xAI)", "Guru BK" if L == "id" else "Counselor"]))
        st.space("small")
        st.markdown(f"**{T('dm_k_pages')}**")
        pages = [("person_search", T("zone_app"), " · ".join(T(label) for _, _, label, _ in ui.ZONES["app"])),
                 ("article", T("zone_report"), " · ".join(T(label) for _, _, label, _ in ui.ZONES["report"]))]
        st.markdown("\n".join(f"- :material/{icon}: **{name}** · {desc}" for icon, name, desc in pages))

# ---------------------------------------------------------------- previous / next
st.space("small")
with st.container(horizontal=True, gap="small"):
    if phase > 0:
        st.button(f"{T('dm_prev')}: {PHASES[phase - 1]['name']}", icon=":material/arrow_back:", type="tertiary",
                  on_click=go, args=(phase - 1,), key="dm_prev")
    st.space("stretch")
    if phase < len(PHASES) - 1:
        st.button(f"{T('dm_next')}: {PHASES[phase + 1]['name']}", icon=":material/arrow_forward:", icon_position="right",
                  on_click=go, args=(phase + 1,), key="dm_next")

ch.end()
