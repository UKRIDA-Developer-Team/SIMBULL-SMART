import numpy as np
import pandas as pd
import pytest

from spk import config, data, model, recommend, smart


@pytest.fixture(scope="module")
def scored():
    rf, meta = model.load_base()
    df = data.load_dataset()
    crit = df[config.FEATURES].copy()
    crit["rf_anxiety_score"] = model.predict(rf, df)
    return rf, meta, df, crit


def test_base_model_matches_notebook(scored):
    rf, meta, df, _ = scored
    _, X_test, _, y_test = model.split(df)
    m = model.metrics(y_test, model.predict(rf, X_test))
    assert m["mae"] == pytest.approx(0.7668, abs=1e-4)
    assert m["r2"] == pytest.approx(0.6136, abs=1e-4)


def test_profile_weights_sum_to_one():
    for name, profile in config.WEIGHT_PROFILES.items():
        for alt, w in profile.items():
            assert sum(w.values()) == pytest.approx(1.0), (name, alt)
    assert sum(config.WEIGHTS_A_NOTEBOOK["Exercise"].values()) == pytest.approx(1.05)


def test_zero_perturbation_changes_nothing(scored):
    _, meta, _, crit = scored
    u = smart.utility(crit[config.CRITERIA].head(3000), meta["smart_bounds"])
    for w in (config.WEIGHTS_A, config.WEIGHTS_B):
        assert smart.population_sensitivity(u, w, deltas=(0.0,)).to_numpy().max() == 0


def test_notebook_recommendation_counts(scored):
    # Notebook cell 92: Model A / Model B best-recommendation counts on the 20k sample
    # (reproduced with the notebook's un-normalized weights A).
    _, _, _, crit = scored
    for weights, expected in [
        (config.WEIGHTS_A_NOTEBOOK, {"Counseling": 1863, "Exercise": 8866, "Relaxation": 2152, "Sleep": 4796, "Study": 2323}),
        (config.WEIGHTS_B, {"Counseling": 7553, "Exercise": 4673, "Relaxation": 172, "Sleep": 5662, "Study": 1940}),
    ]:
        result, _ = smart.run(crit[config.CRITERIA], weights)
        assert result["Best_Recommendation"].value_counts().to_dict() == expected


def test_single_assessment_equals_batch(scored):
    rf, meta, df, crit = scored
    refq = recommend.reference_quantiles(rf, df.head(2000), meta["smart_bounds"])
    batch, _ = smart.run(crit[config.CRITERIA].head(50), config.WEIGHTS_A, meta["smart_bounds"])
    for i in (0, 7, 42):
        a = recommend.assess(rf, meta, df.iloc[i][config.FEATURES], config.WEIGHTS_A, refq)
        assert a.priority == pytest.approx(batch.iloc[i]["smart_score"])
        assert a.best == batch.iloc[i]["Best_Recommendation"]
        assert a.contributions.sum(axis=1)[a.best] == pytest.approx(a.ranking.iloc[0])


def test_perturb_renormalizes():
    w = smart.perturb(config.WEIGHTS_A, "sleep_hours", 0.2)
    for alt in config.ALTERNATIVES:
        assert sum(w[alt].values()) == pytest.approx(1.0)
    assert w["Sleep"]["sleep_hours"] > config.WEIGHTS_A["Sleep"]["sleep_hours"]


def test_equal_weights_are_fully_stable(scored):
    _, meta, _, crit = scored
    u = smart.utility(crit[config.CRITERIA].head(500), meta["smart_bounds"])
    s = smart.stability(u, config.WEIGHTS_A, n=20)
    assert 0.5 < s["top1_unchanged"] <= 1.0


def test_percentile_bounds():
    q = list(np.linspace(0, 10, 101))
    assert recommend.percentile(-1, q) == 0
    assert recommend.percentile(11, q) == 100
    assert recommend.percentile(5, q) == pytest.approx(50)
