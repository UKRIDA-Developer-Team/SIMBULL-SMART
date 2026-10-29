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
            for label in (opt if isinstance(opt, list) else [opt]):
                assert gform._lookup(label, table) == i + 1, (name, label)
                assert gform._lookup(f"{i + 1}.{label}", table) == i + 1, (name, label)
    for name, values in m["value_maps"].items():
        table = {gform.norm(k): v for k, v in values.items()}
        for opt, v in values.items():
            assert gform._lookup(opt, table) == v
    # en dash and spacing variants from Google Forms
    assert gform._lookup("21.00–21.59 WIB", gform.scale_table(m["scales"]["bedtime5"])) == 2
    assert gform._lookup("2 - 3 kali", gform.scale_table(m["scales"]["late_night5"])) == 3
    # the ">5" option added in the revised form, with and without a space
    for text in (">5 kali", "> 5 kali"):
        assert gform._lookup(text, gform.scale_table(m["scales"]["late_night5"])) == 5
    for text in ("> 5", ">5"):
        assert gform._lookup(text, gform.scale_table(m["scales"]["late_tasks5"])) == 5
    # one level, two labels: "Selalu" on the revised form, "Sangat sering" if it gets unified
    for text in ("Selalu", "Sangat sering"):
        assert gform._lookup(text, gform.scale_table(m["scales"]["freq5a"])) == 5


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
    for col in ("Timestamp", "Nama Sekolah", "Tanggal Lahir (Birth Date)", make_synthetic_gform.ESSAY_TITLE):
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
        "many_tasks": 5, "time_insufficient": 4, "late_tasks": 5, "late_night": 5,
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
    raw = export.drop(columns=["Jenis Kelamin (Gender)"])
    with pytest.raises(ValueError, match="gender"):
        gform.prepare(raw)


def test_original_rows_keep_original_formulas():
    """Without the revised items, every composite reduces to the original-form formula."""
    fields = pd.DataFrame([{
        "exam_stress": 3, "many_tasks": 2, "time_insufficient": 3, "late_tasks": 2, "late_night": 4,
        "fear_parents": 2, "family_demand": 4, "time_split": 2, "exhausted": 4, "lost_interest": 3,
        "pocket_money": 2, "p1_nervous": 4, "p2_worry": 3, "p3_focus": 2, "p4_distracted": 3, "p5_hard_finish": 2,
    }])
    d = gform.derive(fields).iloc[0]
    assert d["exam_pressure"] == pytest.approx(1 + (3 - 1) * 9 / 4)
    assert d["family_expectation"] == pytest.approx(10 * ((2 - 1) / 4 + (4 - 1) / 4) / 2)
    assert d[config.TARGET] == pytest.approx(((4 - 1) + (3 - 1) + (5 - 2) + (3 - 1) + (2 - 1)) / 2)
    # "4-5 kali" is level 4 of 5 on both versions (0.75), so both rounds share one value
    assert d["stress_level"] == pytest.approx(10 * (0.25 + 2 / 3 + 0.25 + 0.75) / 4)


def test_revised_items_join_their_composites():
    fields = pd.DataFrame([{
        "exam_stress": 5, "below_target": 1, "fear_parents": 1, "family_demand": 3, "family_talk": 5,
        "p1_nervous": 5, "p2_worry": 5, "p3_focus": 1, "p4_distracted": 5, "p5_hard_finish": 5,
        "p6_irritable": 1, "p7_avoid": 1, "sleep_onset": 5, "night_waking": 3, "sleep_restless": 1,
    }])
    d = gform.derive(fields).iloc[0]
    assert d["exam_pressure"] == pytest.approx(1 + 9 * 0.5)
    # family_talk is reversed: talking freely (5) adds no family pressure
    assert d["family_expectation"] == pytest.approx(10 * (0 + 0.5 + 0) / 3)
    assert d[config.TARGET] == pytest.approx(10 * 5 / 7)
    assert d["x_sleep_quality"] == pytest.approx(5.0)


def test_target_needs_every_original_item():
    fields = pd.DataFrame([{"p1_nervous": 5, "p2_worry": np.nan, "p3_focus": 1, "p4_distracted": 5,
                            "p5_hard_finish": 5, "p6_irritable": 5, "p7_avoid": 5}])
    assert np.isnan(gform.derive(fields).iloc[0][config.TARGET])


def test_mixed_export_tags_versions_and_pools(export):
    raw = pd.read_csv(pd.io.common.StringIO(export.to_csv(index=False)), dtype=str)
    out = gform.prepare(raw, reference_date="2026-09-01")
    versions = out.form_version
    assert set(versions) == {"original", "revised"}
    assert out.report["rows_by_form_version"] == versions.value_counts().sort_index().to_dict()
    df = out.data
    assert df[config.FEATURES + [config.TARGET]].notna().all().all()
    # revised-only extras stay empty for original rows (no fake medians)
    assert df.loc[versions == "original", "x_sleep_quality"].isna().all()
    assert df.loc[versions == "revised", "x_sleep_quality"].notna().all()
    assert {"exam_pressure", "family_expectation", config.TARGET} <= set(out.report["item_set_check"])
    assert out.report["reliability"][config.TARGET]["items"] == 7
    assert out.report["reliability"][f"{config.TARGET} (original items)"]["items"] == 5
    # the ">5" options exist only on the revised form
    late = gform.encode(raw, gform.resolve_columns(raw))
    assert (late.loc[gform.form_version(late, gform.load_mapping()) == "original", "late_night"] < 5).all()


def test_legacy_export_still_parses():
    """An export taken before the revision: original titles, none of the added columns."""
    legacy = make_synthetic_gform.generate(n=60, seed=7, legacy=True)
    raw = pd.read_csv(pd.io.common.StringIO(legacy.to_csv(index=False)), dtype=str)
    assert "Jenis Kelamin" in raw.columns and "Kualitas tidur" not in " ".join(raw.columns)
    out = gform.prepare(raw, reference_date="2026-09-01")
    assert set(out.form_version) == {"original"}
    assert out.data[config.FEATURES + [config.TARGET]].notna().all().all()
    assert "x_sleep_quality" not in out.data


def test_removed_question_columns_do_not_block(export):
    """Columns of questions removed from the form may linger in the export; they are ignored."""
    raw = pd.read_csv(pd.io.common.StringIO(export.to_csv(index=False)), dtype=str)
    some = raw.index[:20]
    raw["Seberapa puas kamu dengan nilai-nilaimu saat ini?"] = None
    raw.loc[some, "Seberapa puas kamu dengan nilai-nilaimu saat ini?"] = "3"
    raw["Kualitas tidur [Seberapa sering kamu sulit tidur kembali setelah terbangun di tengah malam?]"] = None
    raw["Kualitas tidur lama [Seberapa sering kamu bermimpi buruk?]"] = None
    raw.loc[some, "Kualitas tidur lama [Seberapa sering kamu bermimpi buruk?]"] = "Sering"
    res = gform.resolve_columns(raw)
    assert res.ok
    assert res.columns["night_waking"].endswith("lalu sulit tidur kembali?]")
    # two columns fit an optional item equally well: left out and reported, never fatal
    assert "sleep_restless" in res.skipped
    out = gform.prepare(raw, reference_date="2026-09-01")
    assert "sleep_restless" in out.report["skipped_ambiguous_fields"]
