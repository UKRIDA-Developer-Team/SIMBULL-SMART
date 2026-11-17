"""Run every page headlessly in both languages and all weight profiles; fail on any exception."""
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

PAGES = ["app_pages/home.py", "app_pages/recommendation.py", "app_pages/analysis.py", "app_pages/data_mining.py",
         "app_pages/about.py"]


def run(page: str, lang: str, profile: str = "A", **state) -> AppTest:
    # Widgets with format_func are driven through session_state: AppTest's set_value
    # cannot map a formatted option back to its value.
    at = AppTest.from_file("../streamlit_app.py", default_timeout=180)
    at.session_state["lang"] = lang.upper()
    at.session_state["profile"] = profile
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


@pytest.mark.parametrize("profile", ["B", "C"])
def test_analysis_other_profiles(profile):
    at = run("app_pages/analysis.py", "id", profile)
    assert not at.exception, [e.value for e in at.exception]


from spk import config, model

HIGH_RISK = config.EXAMPLE_PROFILES["high"]


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
    compare = [t for t in at.table if "Predicted anxiety" in t.value.columns]
    assert compare and len(compare[0].value) == 2       # both models, one row each


def test_edit_answers_shows_form_again():
    at = run("app_pages/recommendation.py", "id", assess_features=HIGH_RISK, reco_step="form")
    assert not at.exception, [e.value for e in at.exception]
    assert not [h for h in at.get("html") if 'class="spk-hero"' in h.proto.body]
    assert at.radio, "the questionnaire should be visible"


def test_batch_demo_is_the_kaggle_sample():
    """Without an upload the class view scores the Kaggle test sample; there is no synthetic demo."""
    at = run("app_pages/recommendation.py", "id", reco_view="batch")
    assert not at.exception, [e.value for e in at.exception]
    assert any(m.label == "Jumlah siswa" and m.value == "20,000" for m in at.metric)
    assert not [r for r in at.radio if "SINTETIS" in str(r.options)]


def test_language_switch_keeps_input_mode():
    at = run("app_pages/recommendation.py", "id", input_mode_choice="adv")
    at.session_state["lang"] = "EN"
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.session_state["input_mode_choice"] == "adv"
    assert any(s.label == "Sleep hours" for s in at.slider)


def test_profile_survives_language_switch():
    at = run("app_pages/analysis.py", "id", "B")
    at.session_state["lang"] = "EN"
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.session_state["profile"] == "B"
