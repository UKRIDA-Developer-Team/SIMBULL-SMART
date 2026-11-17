"""Pick the students for the UTS spreadsheet and record what the app computes for them.

Output: deliverables/uts/uts_data.json (inputs, RF predictions, bounds, weights, app results).
The spreadsheet rebuilds the SMART part with Excel formulas; these app results are the check.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "app"))

import pandas as pd  # noqa: E402

from spk import config, data, model, smart  # noqa: E402
from spk.recommend import assess, reference_quantiles  # noqa: E402

PROFILES = {"A": config.WEIGHTS_A, "B": config.WEIGHTS_B, "C": config.WEIGHTS_C}


def main():
    rf, meta = model.load_base()
    bounds = meta["smart_bounds"]
    df = data.load_dataset()
    # The reference rows are 20,000 rows of the Kaggle test set (never trained on).
    X_test, y_test = model.kaggle_test_set(df)
    test = X_test.copy()
    test["anxiety_score"] = y_test
    crit = test[config.FEATURES].copy()
    crit["rf_anxiety_score"] = model.predict(rf, test)
    res, _ = smart.run(crit[config.CRITERIA], config.WEIGHTS_A, bounds)
    # 8 test-set students: the first row for each alternative (all five covered), then the
    # earliest other rows (at most two per alternative), in row order
    best = res["Best_Recommendation"]
    picked = [best[best == alt].index[0] for alt in config.ALTERNATIVES if (best == alt).any()]
    seen = {alt: 1 for alt in best.loc[picked]}
    for idx in res.index:
        if len(picked) == 8:
            break
        if idx not in picked and seen.get(best[idx], 0) < 2:
            picked.append(idx)
            seen[best[idx]] = seen.get(best[idx], 0) + 1
    picked = sorted(picked)
    if len(seen) < 5:
        raise SystemExit(f"not every alternative covered: {seen}")
    rows = [("S01", "Contoh aplikasi: Risiko tinggi", dict(config.EXAMPLE_PROFILES["high"]), None),
            ("S02", "Contoh aplikasi: Risiko rendah", dict(config.EXAMPLE_PROFILES["low"]), None)]
    for k, idx in enumerate(picked):
        f = {c: (test.at[idx, c] if c == "gender" else float(test.at[idx, c])) for c in config.FEATURES}
        f["age"] = int(f["age"])
        rows.append((f"S{k + 3:02d}", f"Data uji Kaggle (indeks {idx})", f, float(test.at[idx, "anxiety_score"])))

    quant = reference_quantiles(rf, df, bounds)
    students = []
    for sid, source, feats, actual in rows:
        out = {"id": sid, "source": source, "features": feats, "actual_anxiety": actual, "app": {}}
        for p, w in PROFILES.items():
            a = assess(rf, meta, feats, w, quant)
            out["rf_score"] = a.rf_score
            out["rf_percentile"] = a.rf_percentile
            out["safety"] = bool(a.safety)
            out["utility"] = {c: float(a.utility[c]) for c in config.CRITERIA}
            out["app"][p] = {"priority": a.priority,
                             "scores": {k: float(v) for k, v in a.ranking.items()},
                             "best": a.best}
        students.append(out)
    payload = {
        "criteria": config.CRITERIA, "criteria_type": config.CRITERIA_TYPE, "alternatives": config.ALTERNATIVES,
        "bounds": bounds, "weights_A_raw": config.WEIGHTS_A_NOTEBOOK, "weights_B": config.WEIGHTS_B,
        "weights_C": config.WEIGHTS_C, "safety_percentile": config.SAFETY_PERCENTILE,
        "rf_metrics": meta["metrics"], "students": students,
    }
    out = ROOT / "deliverables" / "uts" / "uts_data.json"
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    for s in students:
        print(s["id"], s["source"][:30], round(s["rf_score"], 3), {p: s["app"][p]["best"] for p in "AB"},
              round(s["app"]["A"]["priority"], 4), s["safety"])


if __name__ == "__main__":
    main()
