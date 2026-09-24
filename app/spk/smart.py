"""SMART method from the notebook, split into pure functions.

Normalization needs min/max per criterion. For batch runs the notebook took them
from the batch itself. For a single student that is impossible (min == max), so
the app passes the reference bounds saved at training time instead.
"""
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
