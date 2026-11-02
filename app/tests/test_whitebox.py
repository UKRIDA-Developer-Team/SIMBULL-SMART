"""White-box tests: designed from the code (its branches, paths and internal properties).

Techniques
- BC  branch coverage: each side of every `if` in the unit is executed and checked
- PC  path coverage: each distinct route through a small function
- PR  property tests of the algorithm (mathematical facts the implementation must satisfy)

Each test name starts with its case ID (wb01...). tests/TESTING.md maps every case to the code
it covers. Statement coverage of spk/: python scripts/coverage_report.py -m whitebox
Run only these with: pytest -m whitebox
"""
from math import comb
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

import ui
from spk import config, crispdm, data, explain, i18n, model, recommend, smart, xai

pytestmark = pytest.mark.whitebox


class Linear:
    """A transparent stand-in model: prediction = sum(beta * x) + intercept on the encoded features."""

    def __init__(self, beta: dict, intercept: float = 0.0):
        self.beta = pd.Series(beta, dtype=float).reindex(config.FEATURES).fillna(0.0)
        self.intercept = intercept

    def predict(self, X):
        return X[config.FEATURES].to_numpy(float) @ self.beta.to_numpy() + self.intercept


class Product:
    """Pure interaction model: prediction = x_a * x_b."""

    def __init__(self, a: str, b: str):
        self.a, self.b = a, b

    def predict(self, X):
        return X[self.a].to_numpy(float) * X[self.b].to_numpy(float)


@pytest.fixture(scope="module")
def meta():
    return model.load_base()[1]


@pytest.fixture(scope="module")
def background():
    return xai.background_sample(data.load_dataset(), n=30)


def student(**changes):
    base = {f: config.INPUT_RANGES[f][2] for f in config.FEATURES if f != "gender"} | {"gender": "Male"}
    return base | changes


# ---------------------------------------------------------------- smart.py

def frame(**cols):
    return pd.DataFrame({c: cols.get(c, [5.0] * len(next(iter(cols.values())))) for c in config.CRITERIA})


def test_wb01_utility_every_branch():
    """BC smart.utility: hi == lo -> 1.0; benefit -> (x-lo)/(hi-lo); cost -> (hi-x)/(hi-lo);
    clip below 0 and above 1."""
    bounds = {c: {"min": 0.0, "max": 10.0} for c in config.CRITERIA}
    bounds["burnout_score"] = {"min": 4.0, "max": 4.0}                     # hi == lo branch
    df = frame(rf_anxiety_score=[2.5, -5.0, 15.0], sleep_hours=[2.5, -5.0, 15.0], burnout_score=[0.0, 4.0, 9.0])
    u = smart.utility(df, bounds)
    assert u["burnout_score"].tolist() == [1.0, 1.0, 1.0]
    assert u["rf_anxiety_score"].tolist() == [0.25, 0.0, 1.0]              # benefit, then both clips
    assert u["sleep_hours"].tolist() == [0.75, 1.0, 0.0]                   # cost, then both clips


def test_wb02_utility_without_bounds_uses_the_frame():
    """BC smart.utility: bounds=None -> min/max come from the frame itself (notebook behaviour)."""
    df = frame(rf_anxiety_score=[1.0, 3.0, 5.0], academic_performance=[60.0, 80.0, 100.0])
    u = smart.utility(df)
    assert u["rf_anxiety_score"].tolist() == [0.0, 0.5, 1.0]
    assert u["academic_performance"].tolist() == [1.0, 0.5, 0.0]
    assert (u["study_hours_per_day"] == 1.0).all()                         # constant column


def test_wb03_perturb_branches():
    """BC smart.perturb: a normal profile is renormalized to 1; an all-zero profile (total == 0)
    is returned unchanged instead of dividing by zero; a missing criterion stays 0."""
    w = smart.perturb({"Sleep": {"sleep_hours": 0.5, "burnout_score": 0.5}}, "sleep_hours", 0.2)
    assert sum(w["Sleep"].values()) == pytest.approx(1.0)
    assert w["Sleep"]["sleep_hours"] == pytest.approx(0.6 / 1.1)
    zero = smart.perturb({"Sleep": {"sleep_hours": 0.0}}, "sleep_hours", 0.2)
    assert zero == {"Sleep": {"sleep_hours": 0.0}}
    missing = smart.perturb({"Sleep": {"burnout_score": 1.0}}, "sleep_hours", 0.2)
    assert missing["Sleep"]["sleep_hours"] == 0.0 and missing["Sleep"]["burnout_score"] == 1.0


def test_wb04_dense_rank_and_tie_break():
    """PC smart.rank (dense ties) and smart.best_alternative (a tie goes to the first alternative,
    which is why profile C always says Sleep)."""
    assert smart.rank(pd.Series([0.5, 0.9, 0.5, 0.1])).tolist() == [2, 1, 2, 3]
    tie = pd.DataFrame([[0.4] * len(config.ALTERNATIVES)], columns=config.ALTERNATIVES)
    assert smart.best_alternative(tie)["Best_Recommendation"].iloc[0] == config.ALTERNATIVES[0]


def test_wb05_sensitivity_grid_and_zero_delta():
    """PC smart.sensitivity: one row per criterion x delta; a zero delta never changes the result."""
    u = smart.utility(frame(rf_anxiety_score=[7.0], sleep_hours=[4.0]),
                      {c: {"min": 0.0, "max": 10.0} for c in config.CRITERIA})
    s = smart.sensitivity(u, config.WEIGHTS_A, deltas=(0.0, 0.5))
    assert len(s) == len(config.CRITERIA) * 2
    assert not s.loc[s["delta"] == 0.0, "changed"].any()


def test_wb05b_run_stability_and_population_paths():
    """PC smart.run (columns and order), smart.stability (no jitter -> nothing changes; jitter ->
    shares within 0-1) and smart.population_sensitivity (zero delta -> 0 for every criterion)."""
    rng = np.random.default_rng(0)
    crit = pd.DataFrame(rng.uniform(0, 10, (200, len(config.CRITERIA))), columns=config.CRITERIA)
    result, u = smart.run(crit, config.WEIGHTS_A, {c: {"min": 0.0, "max": 10.0} for c in config.CRITERIA})
    assert list(result.columns[:2]) == ["smart_score", "rank"]
    assert result["Best_Recommendation"].isin(config.ALTERNATIVES).all()
    still = smart.stability(u, config.WEIGHTS_A, n=5, pct=0.0)
    assert still["top1_unchanged"] == 1.0 and still["top3_unchanged"] == 1.0 and still["top1_min"] == 1.0
    moved = smart.stability(u, config.WEIGHTS_A, n=5, pct=0.5)
    assert 0 <= moved["top1_min"] <= moved["top1_unchanged"] <= 1
    zero = smart.population_sensitivity(u, config.WEIGHTS_A, deltas=(0.0,))
    assert (zero.to_numpy() == 0).all() and list(zero.index) == config.CRITERIA


def test_wb06_normalize_sums_each_alternative_to_one():
    """PR config.normalize: every alternative's weights sum to 1 and keep their proportions."""
    w = config.normalize({"Exercise": {"a": 0.3, "b": 0.75}})
    assert sum(w["Exercise"].values()) == pytest.approx(1.0)
    assert w["Exercise"]["b"] / w["Exercise"]["a"] == pytest.approx(2.5)


# ---------------------------------------------------------------- recommend.py, config.py, data.py

def test_wb07_percentile_clamps_and_interpolates():
    """BC recommend.percentile: below the lowest quantile -> 0, above the highest -> 100,
    otherwise linear interpolation."""
    q = list(np.linspace(2, 4, 101))
    assert recommend.percentile(1.0, q) == 0.0
    assert recommend.percentile(5.0, q) == 100.0
    assert recommend.percentile(3.0, q) == pytest.approx(50.0)
    assert recommend.percentile(2.5, q) == pytest.approx(25.0)


def test_wb07a_reference_quantiles_shape():
    """PC recommend.reference_quantiles: 101 sorted quantiles for prediction and priority."""
    rf, meta = model.load_base()
    q = recommend.reference_quantiles(rf, data.load_dataset().head(300), meta["smart_bounds"])
    for key in ("rf_anxiety_score", "smart_score"):
        assert len(q[key]) == 101 and np.all(np.diff(q[key]) >= 0)


def test_wb07b_safety_cutoff_is_the_inverse_of_percentile():
    """PR recommend.cutoff: the value at the 90th percentile; percentile(cutoff) == 90; a prediction
    exactly at the cutoff is flagged (>=), a hair below is not."""
    q = list(np.sort(np.random.default_rng(1).normal(3, 1.5, 101)))
    c = recommend.cutoff(q)
    assert c == q[90]
    assert recommend.percentile(c, q) == pytest.approx(90.0)
    refq = {"rf_anxiety_score": q, "smart_score": list(np.linspace(0, 1, 101))}
    assert (c >= recommend.cutoff(refq["rf_anxiety_score"])) and not (c - 1e-9 >= recommend.cutoff(q))
    # the other branch: a percentile between two stored quantiles is interpolated
    assert recommend.cutoff(q, 90.5) == pytest.approx((q[90] + q[91]) / 2)


@pytest.mark.parametrize("env,real_exists,expected", [
    ("base", True, "base"), ("real", False, "real"), ("auto", True, "real"), ("auto", False, "base"), (None, False, "base"),
])
def test_wb08_active_model_paths(monkeypatch, tmp_path, env, real_exists, expected):
    """PC config.active_model_paths: SPK_MODEL=base|real forces a model; auto (or unset) uses the
    real model only when its file exists."""
    real = tmp_path / "rf_real_model.joblib"
    if real_exists:
        real.write_bytes(b"x")
    monkeypatch.setattr(config, "REAL_MODEL_PATH", real)
    if env is None:
        monkeypatch.delenv("SPK_MODEL", raising=False)
    else:
        monkeypatch.setenv("SPK_MODEL", env)
    path, _ = config.active_model_paths()
    assert path == (real if expected == "real" else config.MODEL_PATH)


def test_wb09_encode_gender_branches():
    """BC data.encode_gender: text -> fixed codes; numeric codes pass through; unknown text raises."""
    text = pd.DataFrame({"gender": ["Female", "Male", "Other"]})
    assert data.encode_gender(text)["gender"].tolist() == [0, 1, 2]
    codes = pd.DataFrame({"gender": [1, 0]})
    assert data.encode_gender(codes)["gender"].tolist() == [1, 0]
    with pytest.raises(ValueError, match="Unknown gender"):
        data.encode_gender(pd.DataFrame({"gender": ["Robot"]}))


def test_wb10_validate_values_branches():
    """BC data.validate_values: numeric gender codes are mapped back to text; non-numeric and
    missing values are counted separately."""
    rows = pd.DataFrame([student() for _ in range(3)])
    rows["gender"] = [0, 1, 2]
    rows["sleep_hours"] = ["7", "lots", None]
    clean, issues = data.validate_values(rows)
    assert clean["gender"].tolist() == ["Female", "Male", "Other"]
    assert issues["non_numeric"] == {"sleep_hours": 1}
    assert issues["missing"] == {"sleep_hours": 2}


# ---------------------------------------------------------------- explain.py

def fake_assessment(scores: dict, utility_value: float):
    criteria = pd.Series({c: 5.0 for c in config.CRITERIA})
    utility = pd.Series({c: utility_value for c in config.CRITERIA})
    contrib = explain.contributions(utility, config.WEIGHTS_A)
    ranking = pd.Series(scores).sort_values(ascending=False)
    return SimpleNamespace(ranking=ranking, criteria=criteria, utility=utility, contributions=contrib,
                           priority=0.5, priority_percentile=50.0)


@pytest.mark.parametrize("gap,lines", [(0.01, 5), (0.05, 4)])
def test_wb11_narrative_small_gap_branch(gap, lines):
    """BC explain.narrative: a gap under 0.02 to the runner-up adds the 'also consider' line."""
    a = fake_assessment({"Sleep": 0.6, "Exercise": 0.6 - gap, "Study": 0.1, "Counseling": 0.1, "Relaxation": 0.1}, 0.8)
    out = explain.narrative(a, "A", "en")
    assert len(out) == lines
    assert any("also worth considering" in line for line in out) is (gap < 0.02)


@pytest.mark.parametrize("u,phrase", [(0.8, "short sleep"), (0.2, "sleep hours 5.0")])
def test_wb12_narrative_driver_wording_branch(u, phrase):
    """BC explain.narrative: a driver with utility >= 0.5 reads as a problem ('short sleep'),
    below 0.5 as a plain value ('sleep hours 5.0')."""
    a = fake_assessment({"Sleep": 0.9, "Exercise": 0.5, "Study": 0.1, "Counseling": 0.1, "Relaxation": 0.1}, u)
    drivers = explain.narrative(a, "A", "en")[1]
    assert phrase in drivers


def test_wb13_top_drivers_skip_zero_contributions():
    """BC explain.top_drivers: criteria that add nothing (weight or utility 0) are never named."""
    contrib = pd.DataFrame([[0.3, 0.0, 0.1] + [0.0] * (len(config.CRITERIA) - 3)],
                           index=["Sleep"], columns=config.CRITERIA)
    assert explain.top_drivers(contrib, "Sleep", k=3) == [config.CRITERIA[0], config.CRITERIA[2]]


def test_wb14_shap_narrative_branches():
    """BC explain.shap_narrative: no upward effect -> 'no factor pushes up' line; downward effects ->
    their own line; a SMART link adds the last line."""
    values = pd.Series(0.0, index=config.FEATURES)
    values["stress_level"] = -1.0
    expl = xai.ShapExplanation(base_value=3.0, prediction=2.0, values=values, features=pd.Series(student()))
    plain = explain.shap_narrative(expl, None, "en")
    assert len(plain) == 3 and "No factor pushes" in plain[1] and "academic stress level" in plain[2]
    linked = explain.shap_narrative(expl, {"contribution": 0.1, "alternative": "Sleep", "score": 0.5, "share": 0.2}, "en")
    assert len(linked) == 4 and "20%" in linked[-1]
    # value wording: gender as text, age and grades as whole numbers, the rest with one decimal
    values = pd.Series(0.0, index=config.FEATURES)
    values[["gender", "age", "sleep_hours"]] = [0.3, 0.2, 0.1]
    up = explain.shap_narrative(xai.ShapExplanation(3.0, 3.6, values, pd.Series(student(age=16))), None, "en")[1]
    assert "gender Male (+0.30)" in up and "age 16 (+0.20)" in up and "sleep hours 7.0 (+0.10)" in up


# ---------------------------------------------------------------- xai.py: Shapley values

def test_wb15_coalitions_enumerate_every_subset():
    """PR xai.coalitions: 2^m distinct rows, row k holds the bits of k."""
    m = 5
    masks = xai.coalitions(m)
    assert masks.shape == (32, m)
    assert len({tuple(r) for r in masks}) == 32
    assert all(masks[k, j] == bool((k >> j) & 1) for k in range(32) for j in range(m))


@pytest.mark.parametrize("m", [1, 2, 5, 11])
def test_wb16_shapley_weights_sum_to_one(m):
    """PR xai.shapley_weights: over all coalitions without feature i, the weights sum to 1."""
    w = xai.shapley_weights(m)
    assert sum(comb(m - 1, s) * w[s] for s in range(m)) == pytest.approx(1.0)


def test_wb17_shapley_linear_model_is_exact(background):
    """PR: for a linear model, interventional Shapley values are beta_i * (x_i - mean of the
    background) exactly; a feature with beta 0 gets 0 (dummy); the values add up (efficiency)."""
    beta = {"stress_level": 0.4, "burnout_score": 0.3, "sleep_hours": -0.2, "gender": 0.5}
    lin = Linear(beta, intercept=1.0)
    x = student(stress_level=8.0, burnout_score=6.0, sleep_hours=4.5, gender="Female")
    expl = xai.shapley_values(lin, x, background)
    xs = xai.encode(pd.DataFrame([x])).iloc[0]
    mean_bg = xai.encode(background).mean()
    for f in config.FEATURES:
        assert expl.values[f] == pytest.approx(lin.beta[f] * (xs[f] - mean_bg[f]), abs=1e-9), f
    assert expl.values["age"] == 0.0
    assert expl.base_value + expl.values.sum() == pytest.approx(expl.prediction, abs=1e-9)


def test_wb18_shapley_symmetry_splits_an_interaction_equally():
    """PR: for f = x_a * x_b with a symmetric background, both features get the same share and the
    shares add up to f(x) - E[f]."""
    bg = pd.DataFrame([student(stress_level=1.0, burnout_score=1.0), student(stress_level=3.0, burnout_score=3.0)])
    m = Product("stress_level", "burnout_score")
    expl = xai.shapley_values(m, student(stress_level=5.0, burnout_score=5.0), bg)
    assert expl.values["stress_level"] == pytest.approx(expl.values["burnout_score"])
    assert expl.values.drop(["stress_level", "burnout_score"]).abs().max() == 0
    assert expl.values.sum() == pytest.approx(25.0 - (1.0 + 9.0) / 2)


def test_wb19_shapley_on_the_random_forest_is_additive(background):
    """PR on the deployed RF: base value = mean prediction of the background, and the values add
    up to model.predict for the student."""
    rf, _ = model.load_base()
    x = config.EXAMPLE_PROFILES["high"]
    expl = xai.shapley_values(rf, x, background)
    assert expl.base_value == pytest.approx(model.predict(rf, background).mean())
    assert expl.base_value + expl.values.sum() == pytest.approx(model.predict(rf, pd.DataFrame([x]))[0])
    assert list(expl.ordered().index[:2]) == ["stress_level", "burnout_score"]


# ---------------------------------------------------------------- xai.py: what-if and global methods

def test_wb20_counterfactual_branches(meta):
    """BC xai.counterfactuals: a factor better than its target gets no scenario; a worse one does,
    for both directions (+1 sleep, -1 stress); one scenario -> no 'all' row, two -> an 'all' row."""
    lin = Linear({"stress_level": 0.5, "sleep_hours": -0.3}, intercept=2.0)
    ref = pd.DataFrame([student(sleep_hours=h) for h in (5.0, 6.0, 9.0)])
    assert xai.reference_targets(ref)["sleep_hours"] == 6.0 and set(xai.reference_targets(ref)) == set(xai.ACTIONABLE)
    targets = {f: config.INPUT_RANGES[f][2] for f in xai.ACTIONABLE}
    good = student()                                             # every factor exactly at target
    assert list(xai.counterfactuals(lin, meta, good, config.WEIGHTS_A, targets).index) == ["current"]

    one = xai.counterfactuals(lin, meta, student(sleep_hours=4.0), config.WEIGHTS_A, targets)
    assert list(one.index) == ["current", "sleep_hours"]
    assert one.loc["sleep_hours", "to"] == targets["sleep_hours"]
    assert one.loc["sleep_hours", "delta_prediction"] == pytest.approx(-0.3 * (targets["sleep_hours"] - 4.0))

    two = xai.counterfactuals(lin, meta, student(sleep_hours=4.0, stress_level=9.0), config.WEIGHTS_A, targets)
    assert list(two.index) == ["current", "stress_level", "sleep_hours", "all"]
    assert two.loc["all", "delta_prediction"] == pytest.approx(
        two.loc["stress_level", "delta_prediction"] + two.loc["sleep_hours", "delta_prediction"])


def test_wb21_partial_dependence_of_a_linear_model(background):
    """PR xai.partial_dependence: for a linear model the PDP has slope beta, every ICE curve is
    parallel to it, and the default grid stays inside the 5th-95th percentile."""
    lin = Linear({"sleep_hours": -0.3, "stress_level": 0.5})
    out = xai.partial_dependence(lin, background, "sleep_hours", n_grid=6, ice_rows=10)
    slope = np.diff(out["pdp"]) / np.diff(out["grid"])
    assert np.allclose(slope, -0.3)
    assert np.allclose(np.diff(out["ice"], axis=1) / np.diff(out["grid"]), -0.3)
    q = background["sleep_hours"].quantile([0.05, 0.95])
    assert out["grid"].min() >= q.iloc[0] - 1e-9 and out["grid"].max() <= q.iloc[1] + 1e-9


def test_wb22_permutation_importance_of_an_unused_feature_is_zero(background):
    """PR xai.permutation_importance: shuffling a feature the model ignores changes nothing;
    shuffling a used feature increases the error; output is sorted largest first."""
    lin = Linear({"stress_level": 1.0})
    y = lin.predict(xai.encode(background))
    imp = xai.permutation_importance(lin, background, y, n_repeats=3)
    assert imp.index[0] == "stress_level" and imp.loc["stress_level", "mean"] > 0
    assert imp.drop("stress_level")["mean"].abs().max() == 0
    assert imp["mean"].is_monotonic_decreasing


def test_wb23_smart_link_share(meta):
    """PC xai.smart_link: the predicted-anxiety contribution divided by the winning score."""
    rf, _ = model.load_base()
    refq = {"rf_anxiety_score": list(np.linspace(0, 10, 101)), "smart_score": list(np.linspace(0, 1, 101))}
    a = recommend.assess(rf, meta, config.EXAMPLE_PROFILES["high"], config.WEIGHTS_A, refq)
    link = xai.smart_link(a)
    assert link["alternative"] == a.best
    assert link["share"] == pytest.approx(a.contributions.loc[a.best, "rf_anxiety_score"] / a.ranking.iloc[0])


# ---------------------------------------------------------------- crispdm.py, ui.py

def test_wb24_success_criteria_status_branches():
    """BC crispdm.success_criteria: met, not met and pending for every input that can be missing;
    D4 reads holdout MAE when present, else CV MAE."""
    ok = crispdm.success_criteria({"mae": 0.7, "r2": 0.65}, 1.2, ["stress_level", "burnout_score"], 0.95, None)
    assert ok.loc[["D1", "D2", "D3", "S1", "S2", "S3"], "status"].eq("met").all()
    assert ok.loc[["D4", "S4"], "status"].eq("pending").all()

    bad = crispdm.success_criteria({"mae": 1.5, "r2": 0.4}, 1.2, ["age", "gender"], 0.5, None, safety_percentile=95)
    assert bad.loc[["D1", "D2", "D3", "S1", "S3"], "status"].eq("not_met").all()

    unknown = crispdm.success_criteria({"mae": 0.7, "r2": 0.65}, None, ["stress_level", "burnout_score"], None, None)
    assert unknown.loc[["D1", "S1"], "status"].eq("pending").all()

    good = {"mae": 0.7, "r2": 0.65}
    holdout = {"selected": "S3_warm_200", "strategies": {"S3_warm_200": {"holdout_mae": 0.9, "cv_mae": 2.0},
                                                         "S0_kaggle": {"holdout_mae": 1.1, "cv_mae": 1.0}}}
    assert crispdm.success_criteria(good, 1.2, [], 0.95, holdout).loc["D4", "status"] == "met"
    cv_only = {"selected": "S1_real", "strategies": {"S1_real": {"cv_mae": 1.3}, "S0_kaggle": {"cv_mae": 1.0}}}
    assert crispdm.success_criteria(good, 1.2, [], 0.95, cv_only).loc["D4", "status"] == "not_met"


def test_wb25_column_roles_and_test_count(tmp_path):
    """PC crispdm: every Kaggle column gets a role (leakage columns flagged); count_tests counts
    test functions per file and survives a missing folder."""
    decisions = crispdm.column_decisions(data.load_dataset())
    assert set(decisions.index) == set(crispdm.COLUMN_ROLES)
    assert decisions.loc["mental_health_index", "role"] == "leakage"
    assert decisions.loc["stress_level", "r"] > 0.7
    (tmp_path / "test_blackbox.py").write_text("def test_a():\n    pass\n\ndef test_b():\n    pass\n")
    (tmp_path / "test_other.py").write_text("def test_c():\n    pass\ndef helper():\n    pass\n")
    assert crispdm.count_tests(tmp_path) == {"blackbox": 2, "whitebox": 0, "total": 3, "files": 2}
    assert crispdm.count_tests(tmp_path / "missing")["total"] == 0
    dup = pd.DataFrame({"a": [1, 1, None]})
    assert crispdm.data_quality(dup) == {"rows": 3, "columns": 1, "missing": 1, "duplicates": 1}


@pytest.mark.parametrize("pct,band", [(95, "top"), (90, "top"), (89.9, "high"), (60, "high"), (59.9, "mid"),
                                      (40, "mid"), (39.9, "low"), (0, "low")])
def test_wb26_band_every_branch(pct, band):
    """BC ui.band: the four plain-language bands and their exact boundaries (90, 60, 40)."""
    assert ui.band(pct) == band


def test_wb27_i18n_fallbacks():
    """BC i18n: a missing key returns the key itself; a missing language falls back to Indonesian;
    every new xAI and Data Mining key exists in both languages."""
    assert i18n.t("no_such_key", "en") == "no_such_key"
    assert i18n.t("nav_home", "fr") == i18n.t("nav_home", "id")
    for key, entry in i18n.S.items():
        if key.startswith(("xai_", "dm_", "an_xai")):
            assert entry.get("id") and entry.get("en"), key
