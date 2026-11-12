"""Facts behind the Data Mining (CRISP-DM) page, computed from the data, model and test files.

Pure functions, no Streamlit, so the page shows numbers that cannot drift from the code.
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from . import config

# Phase 2 decision for every column of the Kaggle file (see PPT-Doc_CRISP-DM/fase2).
COLUMN_ROLES = {
    **{c: "feature" for c in config.FEATURES},
    config.TARGET: "target",
    "depression_score": "leakage",
    "mental_health_index": "leakage",
    "risk_level": "leakage",
    "dropout_risk": "leakage",
    "social_support": "weak",
    "screen_time": "weak",
    "internet_usage": "weak",
    "academic_year": "not_applicable",
}
RISK_ORDER = {"Low": 0, "Medium": 1, "High": 2}

# Phase 1 success criteria and their targets (Phase 5 checks them).
R2_TARGET = 0.60
STABILITY_TARGET = 0.90
EXPECTED_TOP_FACTORS = {"stress_level", "burnout_score"}


def target_correlation(df: pd.DataFrame) -> pd.Series:
    """Pearson r of every numeric (or ordinal) column with the anxiety score, target excluded."""
    frame = df.copy()
    if "risk_level" in frame:
        frame["risk_level"] = frame["risk_level"].map(RISK_ORDER)
    numeric = frame.select_dtypes("number")
    return numeric.corr()[config.TARGET].drop(config.TARGET).sort_values(ascending=False)


def column_decisions(df: pd.DataFrame) -> pd.DataFrame:
    """One row per Kaggle column: correlation with the target and the Phase 2 decision."""
    corr = target_correlation(df)
    rows = [{"column": c, "r": float(corr[c]) if c in corr else None, "role": COLUMN_ROLES.get(c, "unused")}
            for c in df.columns]
    return pd.DataFrame(rows).set_index("column")


def data_quality(df: pd.DataFrame) -> dict:
    return {"rows": int(len(df)), "columns": int(df.shape[1]),
            "missing": int(df.isna().sum().sum()), "duplicates": int(df.duplicated().sum())}


def _status(ok: bool | None) -> str:
    return "pending" if ok is None else ("met" if ok else "not_met")


def success_criteria(metrics: dict, baseline_mae: float | None, top_factors: list[str],
                     stability_top1: float | None, real_summary: dict | None,
                     safety_percentile: float = config.SAFETY_PERCENTILE) -> pd.DataFrame:
    """Phase 1 success criteria with the value reached and a status: met, not_met or pending.

    D = data mining, S = decision support. D4 and S4 stay pending until the real questionnaire
    data and the user evaluation exist.
    """
    rows = []
    mae, r2 = metrics.get("mae"), metrics.get("r2")
    rows.append({"code": "D1", "value": f"MAE {mae:.3f} vs {baseline_mae:.3f}" if baseline_mae else f"MAE {mae:.3f}",
                 "status": _status(None if baseline_mae is None else mae < baseline_mae)})
    rows.append({"code": "D2", "value": f"R² {r2:.3f}", "status": _status(r2 >= R2_TARGET)})
    top = list(top_factors[:2])
    rows.append({"code": "D3", "value": ", ".join(top), "status": _status(set(top) == EXPECTED_TOP_FACTORS)})

    d4 = None
    value = "-"
    if real_summary and real_summary.get("strategies"):
        strategies, chosen = real_summary["strategies"], real_summary["selected"]
        key = "holdout_mae" if "holdout_mae" in strategies.get(chosen, {}) else "cv_mae"
        mine, kaggle = strategies[chosen][key], strategies["S0_kaggle"][key]
        d4, value = mine < kaggle, f"{chosen} {mine:.3f} vs S0 {kaggle:.3f}"
    rows.append({"code": "D4", "value": value, "status": _status(d4)})

    rows.append({"code": "S1", "value": "-" if stability_top1 is None else f"{stability_top1:.1%}",
                 "status": _status(None if stability_top1 is None else stability_top1 >= STABILITY_TARGET)})
    rows.append({"code": "S2", "value": "SMART + SHAP + what-if", "status": "met"})
    rows.append({"code": "S3", "value": f"P{safety_percentile:.0f}", "status": _status(safety_percentile <= 90)})
    rows.append({"code": "S4", "value": "-", "status": "pending"})
    return pd.DataFrame(rows).set_index("code")


def count_tests(tests_dir: Path) -> dict:
    """Test functions per kind, read from the test files (parametrized cases count once)."""
    pattern = re.compile(r"^\s*def (test_\w+)", re.MULTILINE)
    counts = {}
    for name, path in (("blackbox", "test_blackbox.py"), ("whitebox", "test_whitebox.py")):
        file = tests_dir / path
        counts[name] = len(pattern.findall(file.read_text())) if file.exists() else 0
    files = sorted(tests_dir.glob("test_*.py")) if tests_dir.exists() else []
    counts["total"] = sum(len(pattern.findall(f.read_text())) for f in files)
    counts["files"] = len(files)
    return counts
