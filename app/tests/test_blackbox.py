"""Black-box tests: designed from the specification (what the system must do), not from the code.

Techniques
- EP  equivalence partitioning: one representative per class of inputs
- BVA boundary value analysis: values at, just inside and just outside each limit
- DT  decision table: every combination of conditions of a rule
- MT  metamorphic testing: a change to the input with a known effect on the output
- ST  system test: the running Streamlit app, as a user sees it

Each test name starts with its case ID (bb01...). tests/TESTING.md lists every case with its
input and expected output. Run only these with: pytest -m blackbox
"""
import numpy as np
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

import make_synthetic_gform
import ui
from spk import config, data, gform, model, recommend, smart, xai

CALC = ui.PAGE_FILE["ch3"]

pytestmark = pytest.mark.blackbox

NUMERIC = [f for f in config.FEATURES if f != "gender"]


@pytest.fixture(scope="module")
def ctx():
    rf, meta = model.load_base()
    ref = data.load_dataset()
    refq = recommend.reference_quantiles(rf, ref.head(4000), meta["smart_bounds"])
    typical = {f: float(ref[f].median()) for f in NUMERIC} | {"gender": "Female", "age": 17}
    return {"rf": rf, "meta": meta, "ref": ref, "refq": refq, "typical": typical}


def assess(ctx, features, weights=config.WEIGHTS_A, refq=None):
    return recommend.assess(ctx["rf"], ctx["meta"], features, weights, refq or ctx["refq"])


# ---------------------------------------------------------------- one student

@pytest.mark.parametrize("profile", ["low", "typical", "high"])
def test_bb01_valid_profiles_meet_the_output_contract(ctx, profile):
    """EP. Any valid student gets: anxiety in 0-10, priority in 0-1, percentiles in 0-100,
    all five alternatives ranked best first, utilities in 0-1."""
    features = ctx["typical"] if profile == "typical" else config.EXAMPLE_PROFILES[profile]
    a = assess(ctx, features)
    assert 0 <= a.rf_score <= 10
    assert 0 <= a.priority <= 1
    assert 0 <= a.rf_percentile <= 100 and 0 <= a.priority_percentile <= 100
    assert sorted(a.ranking.index) == sorted(config.ALTERNATIVES)
    assert a.ranking.is_monotonic_decreasing and a.best == a.ranking.index[0]
    assert a.utility.between(0, 1).all()


def test_bb02_high_risk_student_ranks_above_low_risk_student(ctx):
    """EP. The high-risk class gets a higher prediction, percentile and priority than the
    low-risk class, and only the high-risk student triggers the safety rule."""
    high, low = assess(ctx, config.EXAMPLE_PROFILES["high"]), assess(ctx, config.EXAMPLE_PROFILES["low"])
    assert high.rf_score > low.rf_score
    assert high.rf_percentile > low.rf_percentile
    assert high.priority > low.priority
    assert high.safety and not low.safety


@pytest.mark.parametrize("feature", NUMERIC)
def test_bb03_input_range_boundaries_are_accepted(ctx, feature):
    """BVA. Each numeric input at min, min+step, max-step and max still gives a valid result."""
    lo, hi, _ = config.INPUT_RANGES[feature]
    step = 1 if feature == "age" else 0.1
    for value in (lo, lo + step, hi - step, hi):
        a = assess(ctx, ctx["typical"] | {feature: value})
        assert 0 <= a.rf_score <= 10, (feature, value)
        assert a.utility.between(0, 1).all(), (feature, value)


@pytest.mark.parametrize("feature", NUMERIC)
def test_bb04_values_outside_the_range_are_rejected(feature):
    """BVA. In an uploaded CSV, values just outside the allowed range are blanked and reported;
    the boundary values themselves are kept."""
    lo, hi, _ = config.INPUT_RANGES[feature]
    eps = 1 if feature == "age" else 0.01
    rows = pd.DataFrame([{f: config.INPUT_RANGES[f][2] for f in NUMERIC} | {"gender": "Male"} for _ in range(4)])
    rows[feature] = [lo - eps, lo, hi, hi + eps]
    clean, issues = data.validate_values(rows)
    assert issues["out_of_range"] == {feature: 2}
    assert clean[feature].isna().tolist() == [True, False, False, True]


@pytest.mark.parametrize("pct,expected", [(0, False), (50, False), (89.9, False), (90.0, True), (90.1, True), (100, True)])
def test_bb05_safety_rule_decision_table(ctx, pct, expected):
    """DT. Safety rule: predicted anxiety at or above the 90th percentile of the reference
    population -> counseling + referral; below it -> no flag."""
    features = config.EXAMPLE_PROFILES["high"]
    pred = assess(ctx, features).rf_score
    # reference quantiles placed so that this prediction sits exactly at percentile `pct`
    quantiles = (pred + (np.linspace(0, 100, 101) - pct) * 0.01).tolist()
    refq = {"rf_anxiety_score": quantiles, "smart_score": ctx["refq"]["smart_score"]}
    a = assess(ctx, features, refq=refq)
    assert a.rf_percentile == pytest.approx(pct, abs=1e-6)
    assert a.safety is expected


# ---------------------------------------------------------------- whole class (metamorphic)

def score_batch(ctx, df):
    crit = df[config.FEATURES].copy()
    crit["rf_anxiety_score"] = model.predict(ctx["rf"], df)
    result, _ = smart.run(crit[config.CRITERIA], config.WEIGHTS_A, ctx["meta"]["smart_bounds"])
    return result.assign(rf_anxiety_score=crit["rf_anxiety_score"])


def test_bb06_student_order_does_not_change_results(ctx):
    """MT. Shuffling the rows of an upload leaves every student's scores and recommendation unchanged."""
    batch = ctx["ref"].head(300)
    a = score_batch(ctx, batch)
    b = score_batch(ctx, batch.sample(frac=1, random_state=7))
    cols = ["smart_score", "Best_Recommendation", *config.ALTERNATIVES]
    pd.testing.assert_frame_equal(a.loc[batch.index, cols], b.loc[batch.index, cols])


def test_bb07_duplicate_students_get_identical_results(ctx):
    """MT. Two identical rows get identical scores, rank and recommendation."""
    row = ctx["ref"].head(1)
    result = score_batch(ctx, pd.concat([row, row, ctx["ref"].iloc[1:20]], ignore_index=True))
    first, second = result.loc[0], result.loc[1]
    assert first.equals(second)


def test_bb08_single_assessment_matches_the_batch_row(ctx):
    """MT. Scoring one student alone gives the same priority, recommendation and safety flag as
    scoring them inside a class (reference bounds in both)."""
    batch = score_batch(ctx, ctx["ref"].head(40))
    cutoff = recommend.cutoff(ctx["refq"]["rf_anxiety_score"])
    for i in (0, 13, 39):
        a = assess(ctx, ctx["ref"].iloc[i][config.FEATURES])
        assert a.priority == pytest.approx(batch.loc[i, "smart_score"])
        assert a.best == batch.loc[i, "Best_Recommendation"]
        assert a.safety == (batch.loc[i, "rf_anxiety_score"] >= cutoff)


# ---------------------------------------------------------------- questionnaire and files

QUESTION_FIELDS = {  # field -> (lowest answer, middle answer, highest answer)
    "late_night": (1, 3, 5), "time_insufficient": (1, 2, 4), "late_tasks": (1, 3, 5), "below_target": (1, 3, 5),
    "many_tasks": (1, 3, 5), "exam_stress": (1, 3, 5), "fear_parents": (1, 3, 5), "family_demand": (1, 3, 5),
    "pocket_money": (1, 3, 5), "time_split": (1, 3, 5), "exhausted": (1, 3, 5),
    "lost_interest": (1, 3, 5), "study_hours": (0.25, 3.0, 11.5), "report_grade": (0.0, 75.0, 100.0),
    "sleep_duration": (4.0, 7.0, 12.0), "exercise_days": (0.0, 3.5, 7.0), "age": (12, 16, 30),
}


@pytest.mark.parametrize("level", [0, 1, 2], ids=["all_lowest", "all_middle", "all_highest"])
def test_bb09_any_questionnaire_answer_gives_valid_features(level):
    """EP/BVA. All-lowest, all-middle and all-highest questionnaire answers turn into 11 model
    features inside the allowed ranges, with nothing missing."""
    answers = {f: v[level] for f, v in QUESTION_FIELDS.items()} | {"gender": "Female"}
    features = gform.derive(pd.DataFrame([answers]))[config.FEATURES]
    clean, issues = data.validate_values(features)
    assert not issues["out_of_range"] and not issues["missing"], issues


def test_bb10_upload_classes_are_recognised():
    """EP. Three kinds of upload: a model-feature CSV (accepted as is), a Google Form export
    (converted, personal columns dropped), and an unrelated table (rejected with the missing columns)."""
    features_csv = data.load_dataset().head(5)
    assert data.validate_columns(features_csv) == []

    export = make_synthetic_gform.generate(n=40, seed=5)
    raw = pd.read_csv(pd.io.common.StringIO(export.to_csv(index=False)), dtype=str)
    prepared = gform.prepare(raw, reference_date="2026-09-01")
    allowed = set(config.FEATURES) | {config.TARGET}
    assert all(c in allowed or c.startswith("x_") for c in prepared.data.columns)
    assert "Nama Sekolah" in prepared.report["pii_columns_dropped"]

    unrelated = pd.DataFrame({"name": ["a", "b"], "score": [1, 2]})
    assert data.validate_columns(unrelated) == config.FEATURES
    with pytest.raises(ValueError):
        gform.prepare(unrelated)


def test_bb11_unknown_gender_is_reported():
    """EP. Invalid gender text in an upload is reported and blanked, valid spellings are kept."""
    rows = pd.DataFrame([{f: config.INPUT_RANGES[f][2] for f in NUMERIC} for _ in range(3)])
    rows["gender"] = ["female", "Robot", "MALE"]
    clean, issues = data.validate_values(rows)
    assert issues["bad_gender"] == ["Robot"]
    assert clean["gender"].tolist()[0] == "Female" and pd.isna(clean["gender"].iloc[1])


# ---------------------------------------------------------------- explainable AI, as the user reads it

@pytest.mark.parametrize("profile", ["low", "high"])
def test_bb12_explanation_adds_up_to_the_shown_prediction(ctx, profile):
    """The waterfall starts at the average student and its bars end exactly at the prediction
    shown on the result card."""
    features = config.EXAMPLE_PROFILES[profile]
    expl = xai.shapley_values(ctx["rf"], features, xai.background_sample(ctx["ref"]))
    shown = assess(ctx, features).rf_score
    assert expl.base_value + expl.values.sum() == pytest.approx(shown, abs=1e-9)
    assert expl.prediction == pytest.approx(shown, abs=1e-9)


def test_bb13_what_if_suggestions_follow_the_student(ctx):
    """A high-risk student gets one what-if row per factor worse than typical plus a combined row,
    and the combined row lowers the predicted anxiety. A low-risk student gets none."""
    targets = xai.reference_targets(ctx["ref"])
    high = xai.counterfactuals(ctx["rf"], ctx["meta"], config.EXAMPLE_PROFILES["high"], config.WEIGHTS_A, targets)
    assert "all" in high.index and len(high) >= 3
    assert high.loc["all", "prediction"] < high.loc["current", "prediction"]
    low = xai.counterfactuals(ctx["rf"], ctx["meta"], config.EXAMPLE_PROFILES["low"], config.WEIGHTS_A, targets)
    assert list(low.index) == ["current"]


def test_bb14_what_if_without_change_reproduces_the_result(ctx):
    """MT. A what-if that sets a factor to its current value returns the original result."""
    features = config.EXAMPLE_PROFILES["high"]
    a = assess(ctx, features)
    out = xai.what_if(ctx["rf"], ctx["meta"], features, config.WEIGHTS_A,
                      [("same", {"sleep_hours": features["sleep_hours"]})])
    assert out.loc["same", "prediction"] == pytest.approx(a.rf_score)
    assert out.loc["same", "priority"] == pytest.approx(a.priority)
    assert out.loc["same", "best"] == a.best and not out.loc["same", "best_changed"]


# ---------------------------------------------------------------- system tests (the running app)

def app(page: str, lang: str, **state) -> AppTest:
    at = AppTest.from_file("../streamlit_app.py", default_timeout=240)
    at.session_state["lang"] = lang.upper()
    for k, v in state.items():
        at.session_state[k] = v
    at.run()
    at.switch_page(page).run()
    return at


@pytest.mark.parametrize("lang", ["id", "en"])
def test_bb15_calculation_chapter_shows_the_ai_explanation(lang):
    """ST. Report chapter 3 explains the assessed student with the xAI card: three tabs, the Shapley
    narrative, the waterfall and contribution charts, and the what-if tool."""
    at = app(CALC, lang, assess_features=config.EXAMPLE_PROFILES["high"], calc_source="last")
    assert not at.exception, [e.value for e in at.exception]
    labels = [t.label for t in at.tabs]
    expected = (["Prediksi kecemasan", "Dari prediksi ke rekomendasi", "Bagaimana jika?"] if lang == "id"
                else ["Anxiety prediction", "From prediction to recommendation", "What if?"])
    assert labels[:3] == expected
    assert any(("Model memperkirakan" if lang == "id" else "The model estimates") in m.value for m in at.markdown)
    assert len(at.get("image")) >= 2
    # chapter 3 also shows metrics in 3.2 and 3.8; the what-if tool's three come last
    assert at.slider and len(at.metric) >= 3
    assert [m.label for m in at.metric[-3:]][-1] == ("Rekomendasi utama" if lang == "id" else "Top recommendation")


def test_bb16_what_if_slider_updates_the_result():
    """ST. Moving the what-if slider for the main factor lowers the simulated prediction."""
    high = config.EXAMPLE_PROFILES["high"]
    at = app(CALC, "en", assess_features=high, calc_source="last")
    key = at.slider[0].key                                   # the factor that raises the prediction most
    assert at.slider[0].value == high[key.removeprefix("wi_val_calc_")]   # starts at the student's own value
    # The new slider value goes in through session_state on a fresh run: rerunning after a widget
    # change makes AppTest re-read the format_func widgets on the page, which it cannot do.
    moved = app(CALC, "en", assess_features=high, calc_source="last", **{key: 4.0})
    assert not moved.exception, [e.value for e in moved.exception]
    assert moved.slider[0].value == 4.0
    assert float(moved.metric[-3].value) < float(at.metric[-3].value)   # the what-if prediction


@pytest.mark.parametrize("lang", ["id", "en"])
@pytest.mark.parametrize("phase", range(6))
def test_bb17_data_mining_page_walks_through_crisp_dm(lang, phase):
    """ST. The Data Mining page shows a six-step CRISP-DM stepper; every phase renders its name,
    four "what was done" steps and its key decisions; phase 5 shows the success-criteria table."""
    names = ["Business Understanding", "Data Understanding", "Data Preparation", "Modeling", "Evaluation", "Deployment"]
    at = app(ui.PAGE_FILE["ch7"], lang, dm_phase=phase)
    assert not at.exception, [e.value for e in at.exception]
    hero = [h.proto.body for h in at.get("html") if "spk-phase-hero" in h.proto.body]
    assert hero and names[phase] in hero[0]
    assert ("Keputusan penting" if lang == "id" else "Key decisions") in " ".join(m.value for m in at.markdown)
    if phase == 4:
        assert any("D1" in str(t.value.index.tolist()) for t in at.table)


def test_bb18_class_view_links_one_student_to_the_calculation():
    """ST. In the whole-class view (sample data on) a counselor picks a student, sees their ranking, and can open
    that student's worked calculation."""
    at = app(ui.PAGE_FILE["class"], "en", batch_demo=True)
    assert not at.exception, [e.value for e in at.exception]
    assert any(s.label == "Student" for s in at.selectbox)
    assert any(b.label == "See this student's calculation" for b in at.button)
    assert [h for h in at.get("html") if "spk-bars" in h.proto.body]