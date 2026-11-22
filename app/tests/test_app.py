"""Run every page headlessly in both languages and with both models; fail on any exception."""
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

import ui
from spk import config, model

HIGH_RISK = config.EXAMPLE_PROFILES["high"]
PAGES = [path for pages in ui.ZONES.values() for _, path, _, _ in pages]
CALC = ui.PAGE_FILE["ch3"]


def run(page: str, lang: str, **state) -> AppTest:
    # Widgets with format_func are driven through session_state: AppTest's set_value
    # cannot map a formatted option back to its value.
    at = AppTest.from_file("../streamlit_app.py", default_timeout=180)
    at.session_state["lang"] = lang.upper()
    for k, v in state.items():
        at.session_state[k] = v
    at.run()
    at.switch_page(page).run()
    return at


@pytest.mark.parametrize("lang", ["id", "en"])
@pytest.mark.parametrize("page", PAGES)
def test_page_runs(page, lang):
    at = run(page, lang)
    assert not at.exception, [e.value for e in at.exception]


@pytest.mark.parametrize("page", ["student", "ch3", "ch5"])
def test_pages_with_the_kaggle_model(page):
    at = run(ui.PAGE_FILE[page], "id", model_choice="kaggle", assess_features=HIGH_RISK)
    assert not at.exception, [e.value for e in at.exception]


@pytest.mark.parametrize("lang", ["id", "en"])
def test_single_assessment_result(lang):
    # Clicking a form button makes AppTest re-read every widget, which fails on
    # format_func widgets, so the submitted features are injected directly.
    at = run("app_pages/recommendation.py", lang, assess_features=HIGH_RISK)
    assert not at.exception, [e.value for e in at.exception]
    hero = [h.proto.body for h in at.get("html") if 'class="spk-hero"' in h.proto.body]
    assert hero and ("Top recommendation" if lang == "en" else "Rekomendasi utama") in hero[0]
    assert at.error, "high-risk profile should trigger the safety rule"


@pytest.mark.parametrize("choice", ["real", "kaggle"])
def test_model_choice_switches_the_whole_result(choice):
    """The settings popover offers both model iterations; the result and the comparison follow the choice."""
    at = run("app_pages/recommendation.py", "en", assess_features=HIGH_RISK, model_choice=choice)
    assert not at.exception, [e.value for e in at.exception]
    picker = [r for r in at.radio if any("Iteration" in str(o) for o in r.options)]
    assert picker and len(picker[0].options) == 2
    hero = [h.proto.body for h in at.get("html") if 'class="spk-hero"' in h.proto.body][0]
    rf, meta = model.load(*((config.REAL_MODEL_PATH, config.REAL_METADATA_PATH) if choice == "real"
                            else (config.MODEL_PATH, config.METADATA_PATH)))
    assert f"{model.predict(rf, pd.DataFrame([HIGH_RISK]))[0]:.2f}" in hero
    # The side-by-side comparison of both models lives in report chapter 3.
    calc = run(CALC, "en", assess_features=HIGH_RISK, model_choice=choice, calc_source="last")
    assert not calc.exception, [e.value for e in calc.exception]
    compare = [t for t in calc.table if "Predicted anxiety" in t.value.columns]
    assert compare and len(compare[0].value) == 2       # both models, one row each


def test_edit_answers_shows_form_again():
    at = run("app_pages/recommendation.py", "id", assess_features=HIGH_RISK, reco_step="form")
    assert not at.exception, [e.value for e in at.exception]
    assert not [h for h in at.get("html") if 'class="spk-hero"' in h.proto.body]
    assert at.radio, "the questionnaire should be visible"


def test_class_page_starts_empty():
    """Without an upload nothing is scored until the counselor switches on the sample data."""
    at = run(ui.PAGE_FILE["class"], "id")
    assert not at.exception, [e.value for e in at.exception]
    assert not at.metric and not at.dataframe
    assert any(t.key == "batch_demo" and not t.value for t in at.toggle)


def test_class_demo_is_a_small_kaggle_class():
    """The sample class has 30 Kaggle test rows (no synthetic or real student), lists who to refer,
    and groups every student into exactly one program card."""
    at = run(ui.PAGE_FILE["class"], "id", batch_demo=True)
    assert not at.exception, [e.value for e in at.exception]
    assert any(m.label == "Jumlah siswa" and m.value == "30" for m in at.metric)
    urgent = next(m for m in at.metric if m.label == "Perlu dirujuk segera")
    assert int(urgent.value) >= 1                  # the demo includes a few highly anxious students
    cards = [h.proto.body for h in at.get("html") if h.proto.body.startswith("<div class='spk-prog'>")]
    assert len(cards) == len(config.ALTERNATIVES)
    total = sum(int(c.split("spk-prog-n'>")[1].split("<")[0]) for c in cards)
    assert total == 30


def test_questionnaire_starts_empty():
    """No answer is assumed: every question starts unanswered."""
    at = run(ui.PAGE_FILE["student"], "id")
    assert not at.exception, [e.value for e in at.exception]
    answers = [r for r in at.radio if r.key.startswith("q_")]
    assert len(answers) == 14 and all(r.value is None for r in answers)
    assert all(n.value is None for n in at.number_input)
    assert all(s.value is None for s in at.selectbox if s.key.startswith("q_"))
    assert not [t for t in at.toggle], "the advanced mode is gone"


def test_example_fills_the_form_without_showing_a_result():
    at = run(ui.PAGE_FILE["student"], "id")
    at.button(key="example_high").click().run()
    assert not at.exception, [e.value for e in at.exception]
    assert not [h for h in at.get("html") if 'class="spk-hero"' in h.proto.body]
    answers = lambda: [r.value for r in at.radio if r.key.startswith("q_")]  # noqa: E731
    assert answers() and None not in answers()
    assert at.info, "a note says the example answers are loaded"
    at.button(key="clear_answers").click().run()
    assert set(answers()) == {None}


def test_model_choice_survives_language_switch():
    at = run(ui.PAGE_FILE["ch5"], "id", model_choice="kaggle")
    at.session_state["lang"] = "EN"
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.session_state["model_choice"] == "kaggle"


# ---------------------------------------------------------------- two zones

def test_result_page_is_short_and_links_to_the_calculation():
    """The app-zone result keeps the answer and the reasons; the technical detail moved to chapter 3."""
    at = run(ui.PAGE_FILE["student"], "en", assess_features=HIGH_RISK)
    assert not at.exception, [e.value for e in at.exception]
    assert not at.tabs, "the three-tab xAI card belongs to report chapter 3"
    assert not [t for t in at.table if "Predicted anxiety" in t.value.columns]
    labels = [b.label for b in at.button]
    assert "Open calculation" in labels and "Edit answers" in labels and "Assess another student" in labels
    assert "New assessment" not in labels
    factors = [h.proto.body for h in at.get("html") if "spk-factors" in h.proto.body]
    assert factors and "Burnout score" in factors[0]           # the top Shapley driver of the high-risk example
    assert len(at.slider) == 1                                 # the what-if slider


def test_calculation_chapter_matches_smart():
    """Chapter 3 lays out the same numbers as spk.smart: 10 numbered sections, utilities, scores."""
    from spk import smart
    at = run(CALC, "en", assess_features=HIGH_RISK, calc_source="last")
    assert not at.exception, [e.value for e in at.exception]
    heads = [h.value for h in at.subheader]
    assert [h.split()[0] for h in heads[:10]] == [f"3.{i}" for i in range(1, 11)]

    rf, meta = model.load(*config.active_model_paths())
    crit = pd.DataFrame([HIGH_RISK])[config.FEATURES]
    crit["rf_anxiety_score"] = model.predict(rf, crit)
    u = smart.utility(crit[config.CRITERIA], meta["smart_bounds"]).iloc[0]
    util_table = next(t.value for t in at.table if "Substitution" in t.value.columns)
    shown = [float(str(v).split()[0]) for v in util_table["u"]]
    assert shown == pytest.approx(u.tolist(), abs=1e-3)       # 4-decimal worked example, same utilities
    # The worked example redoes by hand: every cell is w x u from the shown numbers, the last row their sum.
    weights = next(t.value for t in at.table if "Σ" in t.value.index)
    scores_table = next(t.value for t in at.table if "Score S" in t.value.index)
    for alt in scores_table.columns:
        cells = [float(v) for v in scores_table[alt].iloc[:-1]]
        assert cells == pytest.approx([round(float(w) * s + 1e-12, 4) for w, s in
                                       zip(weights[alt].iloc[:-1], shown)], abs=1e-9)
        assert float(scores_table[alt].iloc[-1]) == pytest.approx(sum(cells), abs=1e-9)
    ranking = next(t.value for t in at.table if "Gap to top" in t.value.columns)
    scores = smart.alternative_scores(u.to_frame().T, config.WEIGHTS_A).iloc[0].sort_values(ascending=False)
    assert [float(v) for v in ranking["S"]] == pytest.approx(scores.round(3).tolist(), abs=1e-9)


def test_calculation_chapter_without_an_assessment_uses_the_example():
    at = run(CALC, "id")
    assert not at.exception, [e.value for e in at.exception]
    assert at.session_state["calc_source"] == "high"


def test_zone_of_every_page():
    for zone, pages in ui.ZONES.items():
        for _, _, _, url in pages:
            assert ui.zone_of(url) == zone
    assert ui.zone_of("") == "app"


@pytest.mark.parametrize("lang", ["id", "en"])
def test_top_bar_shows_the_zone_switch(lang):
    at = run(CALC, lang)
    assert not at.exception, [e.value for e in at.exception]
    zone = [s for s in at.button_group if s.key and s.key.startswith("zone_")]
    assert zone and zone[0].key == f"zone_report_{lang}"
