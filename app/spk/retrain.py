"""Kaggle-pretrained RF -> retrained on real questionnaire answers.

Strategies compared with repeated k-fold CV on the real data (development part),
then scored once on a real holdout:

    S0_kaggle        base model as is (no retraining)
    S1_real          new RF on real data only
    S2_combined_wN   Kaggle training rows + real rows, real rows weighted N
    S3_warm_N        base forest + N extra trees grown on real data (warm start)
    S4_real_extended real-only RF with the extra questionnaire items (report only,
                     the app cannot ask these, so it is never deployed)

The strategy with the lowest mean CV MAE among S0-S3 is refit on all real rows.
"""
from __future__ import annotations

import copy
import datetime as dt

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import RepeatedKFold, train_test_split

from . import config, smart
from .data import encode_gender
from .model import metrics, predict

STRATEGIES = {
    "S0_kaggle": {},
    "S1_real": {},
    "S2_combined_w1": {"weight": 1},
    "S2_combined_w10": {"weight": 10},
    "S2_combined_w50": {"weight": 50},
    "S3_warm_200": {"add": 200},
    "S3_warm_600": {"add": 600},
}
REPORT_ONLY = "S4_real_extended"


def real_params() -> dict:
    return {**config.RF_PARAMS, **config.REAL_RF_OVERRIDES}


def fit(name: str, base, X_real: pd.DataFrame, y_real: pd.Series,
        X_kaggle: pd.DataFrame, y_kaggle: pd.Series):
    opts = STRATEGIES[name]
    if name == "S0_kaggle":
        return base
    if name == "S1_real":
        return RandomForestRegressor(**real_params()).fit(encode_gender(X_real), y_real)
    if name.startswith("S2_"):
        X = pd.concat([X_kaggle, X_real], ignore_index=True)
        y = pd.concat([y_kaggle, y_real], ignore_index=True)
        w = np.r_[np.ones(len(X_kaggle)), np.full(len(X_real), float(opts["weight"]))]
        return RandomForestRegressor(**config.RF_PARAMS).fit(encode_gender(X), y, sample_weight=w)
    if name.startswith("S3_"):
        model = copy.deepcopy(base)
        model.set_params(warm_start=True, n_estimators=base.n_estimators + opts["add"],
                         **config.REAL_RF_OVERRIDES)
        model.fit(encode_gender(X_real), y_real)
        model.set_params(warm_start=False)
        return model
    raise KeyError(name)


def _extended_frame(df: pd.DataFrame, extras: list[str]) -> pd.DataFrame:
    # Extras stay NaN where a row never saw the question (original-form rows lack the revised
    # items). The forest routes missing values itself; a median would make those rows look average.
    return encode_gender(df[config.FEATURES]).join(df[extras])


def cross_validate(base, dev: pd.DataFrame, X_kaggle, y_kaggle, n_repeats: int = 2,
                   seed: int = config.RANDOM_STATE, log=print) -> dict:
    n_splits = max(2, min(5, len(dev) // 10))
    cv = RepeatedKFold(n_splits=n_splits, n_repeats=n_repeats, random_state=seed)
    X, y = dev[config.FEATURES], dev[config.TARGET]
    extras = [c for c in dev.columns if c.startswith("x_")]
    scores = {name: [] for name in [*STRATEGIES, REPORT_ONLY]}
    for i, (tr, va) in enumerate(cv.split(X)):
        for name in STRATEGIES:
            m = fit(name, base, X.iloc[tr], y.iloc[tr], X_kaggle, y_kaggle)
            scores[name].append(metrics(y.iloc[va], predict(m, X.iloc[va])))
        if extras:
            Xe = _extended_frame(dev, extras)
            m = RandomForestRegressor(**real_params()).fit(Xe.iloc[tr], y.iloc[tr])
            scores[REPORT_ONLY].append(metrics(y.iloc[va], m.predict(Xe.iloc[va])))
        log(f"  fold {i + 1}/{n_splits * n_repeats} done")
    out = {}
    for name, folds in scores.items():
        if not folds:
            continue
        frame = pd.DataFrame(folds)
        out[name] = {
            "cv_mae": float(frame["mae"].mean()), "cv_mae_std": float(frame["mae"].std()),
            "cv_rmse": float(frame["rmse"].mean()), "cv_r2": float(frame["r2"].mean()),
        }
    return out


def select(cv_scores: dict) -> str:
    deployable = {k: v for k, v in cv_scores.items() if k in STRATEGIES}
    return min(deployable, key=lambda k: deployable[k]["cv_mae"])


def reference_quantiles(values) -> list[float]:
    return [float(v) for v in np.quantile(np.asarray(values, dtype=float), np.linspace(0, 1, 101))]


def suppress(counts: pd.Series) -> dict:
    return {str(k): (int(v) if v >= config.SUPPRESS_BELOW else f"<{config.SUPPRESS_BELOW}")
            for k, v in counts.items()}


def feature_stats(df: pd.DataFrame, cols: list[str]) -> dict:
    stats = {}
    for c in cols:
        s = pd.to_numeric(df[c], errors="coerce").dropna()
        if len(s) < config.SUPPRESS_BELOW:
            continue
        q = s.quantile([0.05, 0.25, 0.5, 0.75, 0.95])
        stats[c] = {"mean": float(s.mean()), "std": float(s.std()), "q05": float(q[0.05]),
                    "q25": float(q[0.25]), "q50": float(q[0.5]), "q75": float(q[0.75]),
                    "q95": float(q[0.95])}
    return stats


def group_errors(hold: pd.DataFrame, pred, groups: pd.Series) -> dict:
    """Holdout error per group; groups smaller than SUPPRESS_BELOW are hidden."""
    err = (hold[config.TARGET] - pred).abs()
    pred = pd.Series(pred, index=hold.index)
    out = {}
    for g, idx in hold.groupby(groups).groups.items():
        n = len(idx)
        out[str(g)] = ({"n": n, "mae": float(err.loc[idx].mean()), "mean_pred": float(pred.loc[idx].mean()),
                        "mean_actual": float(hold.loc[idx, config.TARGET].mean())}
                       if n >= config.SUPPRESS_BELOW else {"n": f"<{config.SUPPRESS_BELOW}"})
    return out


def run(real: pd.DataFrame, kaggle: pd.DataFrame, base, base_meta: dict, quality: dict,
        holdout_frac: float = 0.2, log=print, strata: pd.Series | None = None):
    """Full experiment. Returns (final_model, metadata, summary).

    strata (respondent_id -> form version) keeps original and revised rows in the same
    proportion in the development and holdout parts.
    """
    real = real.dropna(subset=[config.TARGET]).copy()
    from .gform import feature_medians, impute
    medians = feature_medians(real)
    real = impute(real, medians)

    from .model import split
    X_kaggle, _, y_kaggle, _ = split(kaggle)
    X_kaggle, y_kaggle = X_kaggle.reset_index(drop=True), y_kaggle.reset_index(drop=True)

    use_holdout = len(real) >= 30
    if use_holdout:
        groups = strata.reindex(real.index) if strata is not None else None
        counts = groups.value_counts() if groups is not None else pd.Series(dtype=int)
        stratify = groups if len(counts) > 1 and counts.min() >= 2 and groups.notna().all() else None
        dev, hold = train_test_split(real, test_size=holdout_frac, random_state=config.RANDOM_STATE,
                                     stratify=stratify)
    else:
        dev, hold = real, real.iloc[0:0]
    log(f"Real rows: {len(real)} (dev {len(dev)}, holdout {len(hold)})")

    log("Cross-validating strategies on real data...")
    scores = cross_validate(base, dev, X_kaggle, y_kaggle, log=log)
    chosen = select(scores)
    log(f"Selected: {chosen}")

    fairness, by_version = {}, {}
    if use_holdout:
        for name in STRATEGIES:
            m = fit(name, base, dev[config.FEATURES], dev[config.TARGET], X_kaggle, y_kaggle)
            pred = predict(m, hold[config.FEATURES])
            scores[name].update({f"holdout_{k}": v for k, v in metrics(hold[config.TARGET], pred).items()})
            if name == chosen:
                fairness = group_errors(hold, pred, hold["gender"])
                if strata is not None:
                    by_version = group_errors(hold, pred, strata.reindex(hold.index))

    final = fit(chosen, base, real[config.FEATURES], real[config.TARGET], X_kaggle, y_kaggle)

    crit = real[config.FEATURES].copy()
    crit["rf_anxiety_score"] = predict(final, real[config.FEATURES])
    if len(real) >= config.REAL_MIN_ROWS_FOR_BOUNDS:
        bounds, bounds_source = smart.compute_bounds(crit[config.CRITERIA]), "real"
    else:
        bounds, bounds_source = base_meta["smart_bounds"], "kaggle"
    priority = smart.smart_score(smart.utility(crit[config.CRITERIA], bounds))

    chosen_metrics = {k.replace("holdout_", ""): v for k, v in scores[chosen].items()
                      if k.startswith("holdout_")} or {
        "mae": scores[chosen]["cv_mae"], "rmse": scores[chosen]["cv_rmse"], "r2": scores[chosen]["cv_r2"]}
    params = final.get_params()
    metadata = {
        "data_source": "kaggle+gform" if chosen != "S1_real" else "gform",
        "strategy": chosen,
        "n_real": int(len(real)),
        "trained_at": dt.datetime.now().isoformat(timespec="seconds"),
        "hyperparameters": {k: params[k] for k in config.RF_PARAMS},
        "n_estimators_total": int(params["n_estimators"]),
        "metrics": chosen_metrics,
        "metrics_note": "holdout of real data" if use_holdout else "cross-validation on real data",
        "base_metrics_kaggle": base_meta["metrics"],
        "smart_bounds": bounds,
        "smart_bounds_source": bounds_source,
        "impute_medians": medians,
        "reference_quantiles": {
            "rf_anxiety_score": reference_quantiles(crit["rf_anxiety_score"]),
            "smart_score": reference_quantiles(priority),
        },
        "n_rows": int(len(real)),
    }

    extras = [c for c in real.columns if c.startswith("x_")]
    corr_cols = config.FEATURES[:1] + config.FEATURES[2:] + [config.TARGET] + extras
    summary = {
        "generated_at": metadata["trained_at"],
        "n_real": int(len(real)),
        "quality": {k: v for k, v in quality.items() if k not in ("unparsed_answers", "unused_columns")}
        | {"unparsed_answer_counts": {k: v["count"] for k, v in quality.get("unparsed_answers", {}).items()}},
        "strategies": scores,
        "selected": chosen,
        "holdout_rows": int(len(hold)),
        "gender_counts": suppress(real["gender"].value_counts()),
        "feature_stats": feature_stats(real, config.FEATURES[:1] + config.FEATURES[2:] + [config.TARGET] + extras),
        "correlation": real[corr_cols].apply(pd.to_numeric, errors="coerce").corr().round(3).to_dict(),
        "fairness_holdout": fairness,
        "holdout_by_form_version": by_version,
        "feature_importance": dict(zip(config.FEATURES, map(float, final.feature_importances_))),
    }
    return final, metadata, summary
