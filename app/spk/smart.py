"""SMART method from the notebook, split into pure functions.

Normalization needs min/max per criterion. For batch runs the notebook took them
from the batch itself. For a single student that is impossible (min == max), so
the app passes the reference bounds saved at training time instead.
"""
import numpy as np
import pandas as pd

from . import config


def compute_bounds(df_criteria: pd.DataFrame) -> dict:
    return {
        c: {"min": float(df_criteria[c].min()), "max": float(df_criteria[c].max())}
        for c in config.CRITERIA
    }


def utility(df_criteria: pd.DataFrame, bounds: dict | None = None) -> pd.DataFrame:
    """Min-max utility per criterion; benefit = higher is worse-off, cost = inverted."""
    bounds = bounds or compute_bounds(df_criteria)
    out = pd.DataFrame(index=df_criteria.index)
    for col in config.CRITERIA:
        lo, hi = bounds[col]["min"], bounds[col]["max"]
        if hi == lo:
            out[col] = 1.0
            continue
        if config.CRITERIA_TYPE[col] == "benefit":
            u = (df_criteria[col] - lo) / (hi - lo)
        else:
            u = (hi - df_criteria[col]) / (hi - lo)
        # clip so inputs outside the reference range stay in [0, 1]
        out[col] = u.clip(0.0, 1.0)
    return out


def smart_score(df_utility: pd.DataFrame, weights: dict = config.PRIORITY_WEIGHTS) -> pd.Series:
    return sum(df_utility[c] * w for c, w in weights.items())


def rank(scores: pd.Series) -> pd.Series:
    return scores.rank(method="dense", ascending=False).astype(int)


def alternative_scores(df_utility: pd.DataFrame, weights_dict: dict) -> pd.DataFrame:
    return pd.DataFrame(
        {alt: smart_score(df_utility, w) for alt, w in weights_dict.items()},
        index=df_utility.index,
    )


def best_alternative(df_score: pd.DataFrame) -> pd.DataFrame:
    result = df_score.copy()
    result["Best_Recommendation"] = result[config.ALTERNATIVES].idxmax(axis=1)
    result["Recommendation_Score"] = result[config.ALTERNATIVES].max(axis=1)
    return result


def run(df_criteria: pd.DataFrame, weights_dict: dict, bounds: dict | None = None):
    """criteria -> utility -> priority score/rank + best recommendation. Returns (result, utility)."""
    u = utility(df_criteria, bounds)
    result = best_alternative(alternative_scores(u, weights_dict))
    result.insert(0, "smart_score", smart_score(u))
    result.insert(1, "rank", rank(result["smart_score"]))
    return result, u


# ---------- sensitivity analysis ----------

def weight_matrix(weights_dict: dict) -> pd.DataFrame:
    """criteria x alternatives."""
    return pd.DataFrame(weights_dict).reindex(config.CRITERIA).fillna(0.0)[config.ALTERNATIVES]


def perturb(weights_dict: dict, criterion: str, delta: float) -> dict:
    """Scale one criterion's weight by (1 + delta) in every alternative, then renormalize to 1."""
    out = {}
    for alt, w in weights_dict.items():
        w = dict(w)
        w[criterion] = w.get(criterion, 0.0) * (1 + delta)
        total = sum(w.values())
        out[alt] = {c: v / total for c, v in w.items()} if total else w
    return out


def sensitivity(u_row: pd.DataFrame, weights_dict: dict, deltas=(-0.2, -0.1, 0.1, 0.2)) -> pd.DataFrame:
    """One student: does the top recommendation change when a criterion weight moves by delta?"""
    base_best = best_alternative(alternative_scores(u_row, weights_dict))["Best_Recommendation"].iloc[0]
    rows = []
    for c in config.CRITERIA:
        for d in deltas:
            scores = alternative_scores(u_row, perturb(weights_dict, c, d)).iloc[0]
            rows.append({"criterion": c, "delta": d, "best": scores.idxmax(),
                         "best_score": float(scores.max()), "changed": scores.idxmax() != base_best})
    return pd.DataFrame(rows)


def stability(u: pd.DataFrame, weights_dict: dict, n: int = 100, pct: float = 0.1,
              seed: int = config.RANDOM_STATE) -> dict:
    """Population: jitter every weight by U(1-pct, 1+pct), renormalize, repeat n times.

    Returns the share of students whose top-1 stays the same, and whose top-3 set stays the same.
    """
    rng = np.random.default_rng(seed)
    W = weight_matrix(weights_dict).to_numpy()
    U = u[config.CRITERIA].to_numpy()
    base = U @ W
    base_top1 = base.argmax(axis=1)
    base_top3 = np.sort(np.argsort(-base, axis=1)[:, :3], axis=1)
    top1, top3 = [], []
    for _ in range(n):
        Wp = W * rng.uniform(1 - pct, 1 + pct, size=W.shape)
        Wp = Wp / Wp.sum(axis=0, keepdims=True)
        s = U @ Wp
        top1.append(float((s.argmax(axis=1) == base_top1).mean()))
        top3.append(float((np.sort(np.argsort(-s, axis=1)[:, :3], axis=1) == base_top3).all(axis=1).mean()))
    return {"top1_unchanged": float(np.mean(top1)), "top3_unchanged": float(np.mean(top3)),
            "top1_min": float(np.min(top1)), "iterations": n, "pct": pct}


def population_sensitivity(u: pd.DataFrame, weights_dict: dict, deltas=(-0.2, -0.1, 0.1, 0.2)) -> pd.DataFrame:
    """criterion x delta -> share of students whose top recommendation changes."""
    U = u[config.CRITERIA].to_numpy()
    base = (U @ weight_matrix(weights_dict).to_numpy()).argmax(axis=1)
    out = pd.DataFrame(index=config.CRITERIA, columns=list(deltas), dtype=float)
    for c in config.CRITERIA:
        for d in deltas:
            W = weight_matrix(perturb(weights_dict, c, d)).to_numpy()
            out.loc[c, d] = float(((U @ W).argmax(axis=1) != base).mean())
    return out
