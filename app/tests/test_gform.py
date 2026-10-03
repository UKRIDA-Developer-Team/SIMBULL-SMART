import numpy as np
import pandas as pd
import pytest

from spk import config, gform
import make_synthetic_gform


@pytest.fixture(scope="module")
def export():
    return make_synthetic_gform.generate(n=120, seed=3)


@pytest.mark.parametrize("text,hours", [
    ("Dibawah 30 menit", 0.25), ("30 menit", 0.5), ("1 jam", 1.0), ("1 jam 30 menit", 1.5),
    ("11 jam 30 menit", 11.5), ("3.30 menit", 0.5), ("5.1 jam 30 menit", 1.5), ("17.12 jam", 12.0),
    ("4 jam", 4.0), ("7", 7.0), (None, np.nan),
])
def test_parse_hours(text, hours):
    got = gform.parse_hours(text)
    assert (np.isnan(got) and np.isnan(hours)) or got == pytest.approx(hours)


def test_every_option_in_questionnaire_parses():
    m = gform.load_mapping()
    for name, options in m["scales"].items():
        table = gform.scale_table(options)
        for i, opt in enumerate(options):
            assert gform._lookup(opt, table) == i + 1, (name, opt)
            assert gform._lookup(f"{i + 1}.{opt}", table) == i + 1, (name, opt)
    for name, values in m["value_maps"].items():
        table = {gform.norm(k): v for k, v in values.items()}
        for opt, v in values.items():
            assert gform._lookup(opt, table) == v
    # en dash and spacing variants from Google Forms
    assert gform._lookup("21.00–21.59 WIB", gform.scale_table(m["scales"]["bedtime5"])) == 2
    assert gform._lookup("2 - 3 kali", gform.scale_table(m["scales"]["late_night4"])) == 3


def test_resolve_handles_duplicate_titles(export):
    raw = pd.read_csv(pd.io.common.StringIO(export.to_csv(index=False)), dtype=str)
    res = gform.resolve_columns(raw)
    assert res.ok, (res.missing, res.ambiguous)
    assert res.columns["study_hours"].startswith(make_synthetic_gform.STUDY_TITLE)
    assert res.columns["late_night"] != res.columns["study_hours"]
    assert res.columns["time_insufficient"] != res.columns["late_tasks"]


def test_prepare_drops_pii_and_scales(export):
    raw = pd.read_csv(pd.io.common.StringIO(export.to_csv(index=False)), dtype=str)
    out = gform.prepare(raw, reference_date="2026-09-01")
    df = out.data
    assert list(df.columns[:11]) == config.FEATURES
    assert config.TARGET in df
    for col in ("Timestamp", "Nama Sekolah", "Tanggal Lahir (Birth Date)"):
        assert col in out.report["pii_columns_dropped"]
        assert col not in df.columns
    assert df["exam_pressure"].between(1, 10).all()
    for c in ("stress_level", "financial_stress", "family_expectation", "burnout_score", config.TARGET):
        assert df[c].between(0, 10).all(), c
    assert df["age"].between(14, 19).all()
    assert set(df["gender"]) <= {"Male", "Female"}


def test_derive_formulas():
    fields = pd.DataFrame([{
        "age": 16, "gender": "Female", "study_hours": 2.0, "report_grade": 80, "exam_stress": 5,
        "many_tasks": 5, "time_insufficient": 4, "late_tasks": 4, "late_night": 4,
        "sleep_duration": 6.0, "exercise_days": 1.5, "pocket_money": 1, "fear_parents": 1,
        "family_demand": 3, "time_split": 1, "exhausted": 3, "lost_interest": 5,
        "p1_nervous": 5, "p2_worry": 5, "p3_focus": 1, "p4_distracted": 5, "p5_hard_finish": 5,
    }])
    d = gform.derive(fields).iloc[0]
    assert d["exam_pressure"] == 10
    assert d["stress_level"] == 10
    assert d["financial_stress"] == 10
    assert d["family_expectation"] == pytest.approx(2.5)
    assert d["burnout_score"] == pytest.approx(5.0)
    assert d[config.TARGET] == 10


def test_missing_required_field_is_reported(export):
    raw = export.drop(columns=["Jenis Kelamin"])
    with pytest.raises(ValueError, match="gender"):
        gform.prepare(raw)
