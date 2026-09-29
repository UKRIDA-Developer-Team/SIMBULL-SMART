"""One call from a student's feature values to everything the result screen shows."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from . import config, explain, smart
from .model import predict


@dataclass
class Assessment:
    features: pd.Series        # the 11 model inputs
    criteria: pd.Series        # the 8 SMART criteria values (incl. rf_anxiety_score)
    utility: pd.Series         # 0..1 per criterion
    rf_score: float
    rf_percentile: float
    priority: float
    priority_percentile: float
    ranking: pd.Series         # alternative -> score, best first
    contributions: pd.DataFrame
    sensitivity: pd.DataFrame
    safety: bool

    @property
    def best(self) -> str:
        return self.ranking.index[0]


def percentile(value: float, quantiles: list[float]) -> float:
    """Share (0-100) of the reference population below value, from 101 stored quantiles."""
    q = np.asarray(quantiles, dtype=float)
    return float(np.interp(value, q, np.linspace(0, 100, len(q)), left=0.0, right=100.0))


def reference_quantiles(rf, df: pd.DataFrame, bounds: dict) -> dict:
    """Quantiles of predicted anxiety and SMART priority over a reference population."""
    crit = df[config.FEATURES].copy()
    crit["rf_anxiety_score"] = predict(rf, df)
    priority = smart.smart_score(smart.utility(crit[config.CRITERIA], bounds))
    grid = np.linspace(0, 1, 101)
    return {"rf_anxiety_score": np.quantile(crit["rf_anxiety_score"], grid).tolist(),
            "smart_score": np.quantile(priority, grid).tolist()}


def assess(rf, meta: dict, features: dict | pd.Series, weights_dict: dict, ref_quantiles: dict) -> Assessment:
    row = pd.DataFrame([dict(features)])[config.FEATURES]
    crit = row.copy()
    crit["rf_anxiety_score"] = predict(rf, row)
    crit = crit[config.CRITERIA]
    u = smart.utility(crit, meta["smart_bounds"])
    priority = float(smart.smart_score(u).iloc[0])
    ranking = smart.alternative_scores(u, weights_dict).iloc[0].sort_values(ascending=False)
    rf_score = float(crit["rf_anxiety_score"].iloc[0])
    rf_pct = percentile(rf_score, ref_quantiles["rf_anxiety_score"])
    return Assessment(
        features=row.iloc[0],
        criteria=crit.iloc[0],
        utility=u.iloc[0],
        rf_score=rf_score,
        rf_percentile=rf_pct,
        priority=priority,
        priority_percentile=percentile(priority, ref_quantiles["smart_score"]),
        ranking=ranking,
        contributions=explain.contributions(u.iloc[0], weights_dict),
        sensitivity=smart.sensitivity(u, weights_dict),
        safety=rf_pct >= config.SAFETY_PERCENTILE,
    )
