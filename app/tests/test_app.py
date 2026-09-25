"""Run every page headlessly in both languages and all weight profiles; fail on any exception."""
import pytest
from streamlit.testing.v1 import AppTest

PAGES = ["app_pages/home.py", "app_pages/recommendation.py", "app_pages/analysis.py", "app_pages/about.py"]


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


from spk import config

HIGH_RISK = config.EXAMPLE_PROFILES["high"]


@pytest.mark.parametrize("lang", ["id", "en"])
def test_single_assessment_result(lang):
    # Clicking a form button makes AppTest re-read every widget, which fails on
    # format_func widgets, so the submitted features are injected directly.
    at = run("app_pages/recommendation.py", lang, assess_features=HIGH_RISK)
    assert not at.exception, [e.value for e in at.exception]
    labels = [m.label for m in at.metric]
    assert any(("Top recommendation" if lang == "en" else "Rekomendasi utama") in x for x in labels)
    assert at.error, "high-risk profile should trigger the safety rule"


def test_batch_synthetic_gform():
    at = run("app_pages/recommendation.py", "id", batch_demo_choice="gform")
    assert not at.exception, [e.value for e in at.exception]
    assert any("Google Form" in i.value for i in at.info)


def test_language_switch_keeps_input_mode():
    at = run("app_pages/recommendation.py", "id", input_mode_choice="adv")
    at.session_state["lang"] = "EN"
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.session_state["input_mode_choice"] == "adv"
    assert any(s.label == "Sleep hours" for s in at.slider)
