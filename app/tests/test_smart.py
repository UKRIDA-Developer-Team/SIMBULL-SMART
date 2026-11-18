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


def test_base_model_metrics(scored):
    # Base model: full Kaggle file -> age 14-25 -> 80/20 split by age, tuned settings
    # (scripts/train.py --stage kaggle). The reference rows are 20,000 rows of the test set.
    rf, meta, df, _ = scored
    assert meta["rows"] == {"full": 1_000_000, "age_filtered": 692_545, "dropped": 307_455,
                            "train": 554_036, "test": 138_509, "reference": config.REFERENCE_ROWS}
    assert meta["n_rows"] == meta["rows"]["train"] and meta["hyperparameters"] == config.RF_PARAMS
    assert meta["metrics"]["mae"] == pytest.approx(0.7583, abs=1e-4)      # whole test set
    assert meta["metrics"]["r2"] == pytest.approx(0.6077, abs=1e-4)
    X, y = model.kaggle_test_set(df)
    m = model.metrics(y, model.predict(rf, X))
    assert m["mae"] == pytest.approx(meta["metrics_reference_rows"]["mae"], abs=1e-9)
    assert m["mae"] == pytest.approx(0.7539, abs=1e-4)
    assert m["r2"] == pytest.approx(0.6131, abs=1e-4)


def test_weights_sum_to_one():
    for alt, w in config.WEIGHTS_A.items():
        assert sum(w.values()) == pytest.approx(1.0), alt
    assert sum(config.WEIGHTS_A_NOTEBOOK["Exercise"].values()) == pytest.approx(1.05)


def test_zero_perturbation_changes_nothing(scored):
    _, meta, _, crit = scored
    u = smart.utility(crit[config.CRITERIA].head(3000), meta["smart_bounds"])
    assert smart.population_sensitivity(u, config.WEIGHTS_A, deltas=(0.0,)).to_numpy().max() == 0


def test_recommendation_counts_on_cleaned_sample(scored):
    # Best-recommendation counts on the reference rows (20,000 test rows), batch min-max as in notebook
    # cell 92. The first row uses the notebook's un-normalized weights A.
    _, _, _, crit = scored
    for weights, expected in [
        (config.WEIGHTS_A_NOTEBOOK, {"Counseling": 1956, "Exercise": 9338, "Relaxation": 2421, "Sleep": 4648, "Study": 1637}),
        (config.WEIGHTS_A, {"Counseling": 2337, "Exercise": 7323, "Relaxation": 3220, "Sleep": 5238, "Study": 1882}),
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
