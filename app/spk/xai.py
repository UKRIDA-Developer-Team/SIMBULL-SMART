"""Explainable AI (xAI) for the Random Forest stage and for the whole RF -> SMART result.

Local, for one student:
- shapley_values(): exact Shapley values (interventional SHAP) of the RF prediction. With 11
  features there are only 2**11 = 2,048 feature coalitions, so every coalition is enumerated
  against a fixed background sample instead of being approximated. The values add up exactly:
  base value + sum(phi) = prediction.
- counterfactuals() / what_if(): "what if" scenarios. One actionable factor moves to the level
  of a typical student (reference median), then RF + SMART run again to show how the prediction,
  the priority and the recommendation change.

Global, for the whole model:
- permutation_importance(): how much the MAE grows when one feature's values are shuffled.
- partial_dependence(): the average prediction (PDP) and per-student curves (ICE) along one feature.

Pure numpy/pandas, no Streamlit and no extra dependency. Models only need .predict() on a frame
of the encoded features (gender as its numeric code), like the trained RandomForestRegressor.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import factorial

import os

import numpy as np
import pandas as pd

from . import config, smart
from .data import encode_gender

# Background rows for Shapley values: 100 keeps one explanation under ~0.5 s (2,048 x 100 rows).
BACKGROUND_SIZE = 100

# Factors a counselor can work on, and which direction is healthier:
# +1 = more is healthier (sleep, exercise), -1 = less is healthier.
ACTIONABLE = {
    "stress_level": -1,
    "burnout_score": -1,
    "exam_pressure": -1,
    "sleep_hours": +1,
    "physical_activity": +1,
    "study_hours_per_day": -1,
    "financial_stress": -1,
    "family_expectation": -1,
}


# ---------------------------------------------------------------- helpers

def encode(df: pd.DataFrame, features=config.FEATURES) -> pd.DataFrame:
    """Model input frame: the feature columns in order, gender as its numeric code, floats."""
    return encode_gender(df[list(features)]).astype(float)


def background_sample(df: pd.DataFrame, n: int = BACKGROUND_SIZE, seed: int = config.RANDOM_STATE) -> pd.DataFrame:
    """A fixed random sample of the reference population: the 'average student' Shapley compares against."""
    return df[config.FEATURES].sample(min(n, len(df)), random_state=seed).reset_index(drop=True)


def coalitions(m: int) -> np.ndarray:
    """All 2**m subsets of m features as a boolean matrix; row k holds the bits of k (bit j = feature j)."""
    return ((np.arange(2 ** m)[:, None] >> np.arange(m)) & 1).astype(bool)


def shapley_weights(m: int) -> np.ndarray:
    """w[s] = s! (m - s - 1)! / m!, the weight of a coalition of size s that excludes the feature."""
    return np.array([factorial(s) * factorial(m - s - 1) / factorial(m) for s in range(m)])


# ---------------------------------------------------------------- local: Shapley values

@dataclass
class ShapExplanation:
    base_value: float          # mean prediction over the background (the "average student")
    prediction: float          # the model's prediction for this student
    values: pd.Series          # feature -> Shapley value (sum = prediction - base_value)
    features: pd.Series        # the student's raw feature values

    def ordered(self) -> pd.Series:
        """Shapley values, largest absolute effect first."""
        return self.values.reindex(self.values.abs().sort_values(ascending=False).index)

    def raising(self, k: int = 3, min_effect: float = 0.05) -> pd.Series:
        v = self.values[self.values >= min_effect].sort_values(ascending=False)
        return v.head(k)

    def lowering(self, k: int = 3, min_effect: float = 0.05) -> pd.Series:
        v = self.values[self.values <= -min_effect].sort_values()
        return v.head(k)


def coalition_values(model, x: pd.Series | dict, background: pd.DataFrame, features=config.FEATURES) -> np.ndarray:
    """v[k] = mean prediction when the features in coalition k take the student's values and the
    others keep each background row's values (interventional expectation)."""
    features = list(features)
    m = len(features)
    xs = encode(pd.DataFrame([dict(x)]), features).to_numpy()[0]
    bg = encode(background, features).to_numpy()
    masks = coalitions(m)
    rows = np.where(masks[:, None, :], xs[None, None, :], bg[None, :, :]).reshape(-1, m)
    preds = predict_chunks(model, pd.DataFrame(rows, columns=features))
    return preds.reshape(2 ** m, len(bg)).mean(axis=1)


def predict_chunks(model, frame: pd.DataFrame, chunk: int = 8_192) -> np.ndarray:
    """model.predict over row chunks in parallel threads (tree traversal releases the GIL).

    The loaded forest predicts on one thread, so every chunk sums its trees in a fixed order:
    the result is bit-identical to one model.predict call, only faster for the 200k rows of
    an exact Shapley explanation.
    """
    if len(frame) <= chunk:
        return np.asarray(model.predict(frame), dtype=float)
    from concurrent.futures import ThreadPoolExecutor

    parts = [frame.iloc[i:i + chunk] for i in range(0, len(frame), chunk)]
    with ThreadPoolExecutor(max_workers=min(len(parts), os.cpu_count() or 1)) as pool:
        return np.concatenate([np.asarray(p, dtype=float) for p in pool.map(model.predict, parts)])


def shapley_from_values(v: np.ndarray, m: int) -> np.ndarray:
    """Exact Shapley values from the 2**m coalition values (classic weighted marginal contributions)."""
    idx = np.arange(2 ** m)
    size = coalitions(m).sum(axis=1)
    w = shapley_weights(m)
    phi = np.empty(m)
    for j in range(m):
        without = idx[((idx >> j) & 1) == 0]
        phi[j] = float(np.sum(w[size[without]] * (v[without | (1 << j)] - v[without])))
    return phi


def shapley_values(model, x: pd.Series | dict, background: pd.DataFrame, features=config.FEATURES) -> ShapExplanation:
    """Exact interventional Shapley values for one student's prediction."""
    features = list(features)
    v = coalition_values(model, x, background, features)
    phi = shapley_from_values(v, len(features))
    x = pd.Series(dict(x))[features]
    return ShapExplanation(base_value=float(v[0]), prediction=float(v[-1]),
                           values=pd.Series(phi, index=features), features=x)


def smart_link(assessment) -> dict:
    """How the RF stage feeds the SMART result: the predicted-anxiety criterion's share of the
    recommended alternative's score."""
    best = assessment.best
    part = float(assessment.contributions.loc[best, "rf_anxiety_score"])
    total = float(assessment.ranking.iloc[0])
    return {"alternative": best, "contribution": part, "score": total,
            "share": part / total if total else 0.0}


# ---------------------------------------------------------------- local: counterfactual what-if

def what_if(model, meta: dict, features: dict | pd.Series, weights_dict: dict,
            scenarios: list[tuple[str, dict]]) -> pd.DataFrame:
    """Re-run RF + SMART for each scenario. scenarios = [(label, {feature: new value})].

    The first output row ("current") is the student as entered. Columns: prediction, priority,
    best, best_score and the change from the current row.
    """
    base = pd.Series(dict(features))[config.FEATURES]
    rows = [base.to_dict()]
    labels = ["current"]
    for label, changes in scenarios:
        row = base.copy()
        for f, value in changes.items():
            row[f] = value
        rows.append(row.to_dict())
        labels.append(label)
    frame = pd.DataFrame(rows, index=labels)[config.FEATURES]
    crit = frame.copy()
    crit["rf_anxiety_score"] = model.predict(encode(frame))
    u = smart.utility(crit[config.CRITERIA], meta["smart_bounds"])
    alt = smart.alternative_scores(u, weights_dict)
    out = pd.DataFrame({
        "prediction": crit["rf_anxiety_score"],
        "priority": smart.smart_score(u),
        "best": alt.idxmax(axis=1),
        "best_score": alt.max(axis=1),
    })
    out["delta_prediction"] = out["prediction"] - out.loc["current", "prediction"]
    out["delta_priority"] = out["priority"] - out.loc["current", "priority"]
    out["best_changed"] = out["best"] != out.loc["current", "best"]
    return out


def counterfactuals(model, meta: dict, features: dict | pd.Series, weights_dict: dict,
                    targets: dict, actionable: dict = ACTIONABLE) -> pd.DataFrame:
    """One scenario per actionable factor that is worse than its target (usually the reference
    median), plus one scenario with all of them together. Factors already at or better than
    the target get no scenario.

    Returns the what_if() frame with two more columns: feature and the from/to values.
    """
    x = pd.Series(dict(features))
    scenarios, info = [], {}
    for f, direction in actionable.items():
        current, target = float(x[f]), float(targets[f])
        worse = current < target if direction > 0 else current > target
        if worse:
            scenarios.append((f, {f: target}))
            info[f] = (current, target)
    if len(scenarios) > 1:
        scenarios.append(("all", {f: t for f, (_, t) in info.items()}))
    out = what_if(model, meta, features, weights_dict, scenarios)
    out["feature"] = [None] + [label for label, _ in scenarios]
    out["from"] = [None] + [info[f][0] if f in info else None for f, _ in scenarios]
    out["to"] = [None] + [info[f][1] if f in info else None for f, _ in scenarios]
    return out


def reference_targets(reference: pd.DataFrame) -> dict:
    """Typical-student levels (medians of the reference population) for the counterfactuals."""
    return {f: float(reference[f].median()) for f in ACTIONABLE}


# ---------------------------------------------------------------- global

def permutation_importance(model, X: pd.DataFrame, y, n_repeats: int = 5,
                           seed: int = config.RANDOM_STATE) -> pd.DataFrame:
    """Increase in MAE when one feature column is shuffled (model-agnostic importance).

    Returns a frame indexed by feature with columns mean and std, largest first.
    """
    rng = np.random.default_rng(seed)
    Xe = encode(X)
    y = np.asarray(y, dtype=float)
    base = np.mean(np.abs(y - predict_chunks(model, Xe)))
    rows = {}
    for f in config.FEATURES:
        drops = []
        for _ in range(n_repeats):
            shuffled = Xe.copy()
            shuffled[f] = rng.permutation(shuffled[f].to_numpy())
            drops.append(np.mean(np.abs(y - predict_chunks(model, shuffled))) - base)
        rows[f] = {"mean": float(np.mean(drops)), "std": float(np.std(drops))}
    return pd.DataFrame(rows).T.sort_values("mean", ascending=False)


def partial_dependence(model, X: pd.DataFrame, feature: str, grid=None, n_grid: int = 20,
                       ice_rows: int = 40, seed: int = config.RANDOM_STATE) -> dict:
    """PDP and ICE for one feature.

    Every row of X gets the feature set to each grid value in turn; the PDP is the mean prediction
    per grid value and ICE keeps the curves of a sample of rows. The default grid spans the
    5th-95th percentile of the feature.
    """
    Xe = encode(X)
    if grid is None:
        grid = np.unique(np.quantile(Xe[feature], np.linspace(0.05, 0.95, n_grid)))
    grid = np.asarray(grid, dtype=float)
    stacked = pd.concat([Xe.assign(**{feature: g}) for g in grid], ignore_index=True)
    preds = np.asarray(model.predict(stacked), dtype=float).reshape(len(grid), len(Xe))
    rng = np.random.default_rng(seed)
    pick = rng.choice(len(Xe), size=min(ice_rows, len(Xe)), replace=False)
    return {"feature": feature, "grid": grid, "pdp": preds.mean(axis=1), "ice": preds[:, pick].T}
