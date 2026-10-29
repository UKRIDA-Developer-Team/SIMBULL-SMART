"""Offline step: build every artifact the Streamlit app loads.

Replaces the Colab/Drive cells of the notebook. Run from the app/ folder.

Stage 1 - pretrain on Kaggle (the notebook's model):
    python scripts/train.py --stage kaggle               # download from Kaggle, sample 20k, train
    python scripts/train.py --stage kaggle --csv path    # reuse an existing dataset.csv

Stage 2 - retrain on the real Google Form answers (confidential, never committed):
    python scripts/train.py --stage real --gform data/private/gform_raw.csv

Algorithm justification (baselines vs RF, 5-fold CV on the Kaggle training rows):
    python scripts/train.py --stage compare

Outputs:
    kaggle : data/dataset.csv, models/rf_anxiety_model.joblib (+ _metadata.json)
    real   : models/rf_real_model.joblib (+ _metadata.json), models/real_summary.json (aggregates),
             reports/private/real_data_report.md (gitignored)
    compare: models/model_comparison.json
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from spk import config, data, gform, model, retrain, smart  # noqa: E402


def stage_kaggle(args):
    if args.csv:
        df = data.load_dataset(args.csv)
    else:
        df = data.download_sample()
    config.DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(config.DATA_PATH, index=False)
    print(f"Dataset: {len(df)} rows -> {config.DATA_PATH}")

    rf, metrics, _, _ = model.train(df)
    print("Metrics:", {k: round(v, 4) for k, v in metrics.items()})

    # Reference min/max for SMART utility, taken over the full 20k sample
    # (same population the notebook normalized over).
    criteria_df = df.copy()
    criteria_df["rf_anxiety_score"] = model.predict(rf, df)
    bounds = smart.compute_bounds(criteria_df[config.CRITERIA])

    model.save(rf, {"data_source": "kaggle", "metrics": metrics, "smart_bounds": bounds,
                    "n_rows": len(df)})
    size_mb = config.MODEL_PATH.stat().st_size / 1e6
    print(f"Model: {config.MODEL_PATH} ({size_mb:.1f} MB)")
    print(f"Metadata: {config.METADATA_PATH}")


def write_report(path: Path, metadata: dict, summary: dict, quality: dict):
    rows = ["| Strategy | CV MAE (±sd) | CV RMSE | CV R² | Holdout MAE | Holdout R² |",
            "|---|---|---|---|---|---|"]
    for name, s in summary["strategies"].items():
        mark = " **(selected)**" if name == summary["selected"] else ""
        rows.append(f"| {name}{mark} | {s['cv_mae']:.4f} ± {s['cv_mae_std']:.4f} | {s['cv_rmse']:.4f} | "
                    f"{s['cv_r2']:.4f} | {s.get('holdout_mae', float('nan')):.4f} | "
                    f"{s.get('holdout_r2', float('nan')):.4f} |")
    imp = sorted(summary["feature_importance"].items(), key=lambda kv: -kv[1])
    lines = [
        "# Real-data retraining report",
        "",
        f"Generated {metadata['trained_at']}. PRIVATE: contains answer examples; do not commit.",
        "",
        f"- Real rows used: {summary['n_real']} (holdout {summary['holdout_rows']})",
        f"- Selected strategy: **{summary['selected']}**",
        f"- Deployed metrics ({metadata['metrics_note']}): "
        + ", ".join(f"{k.upper()} {v:.4f}" for k, v in metadata["metrics"].items()),
        f"- Base (Kaggle) metrics on Kaggle test set: "
        + ", ".join(f"{k.upper()} {v:.4f}" for k, v in metadata["base_metrics_kaggle"].items()),
        f"- SMART bounds source: {metadata['smart_bounds_source']}",
        "",
        "## Strategy comparison",
        "",
        *rows,
        "",
        "## Feature importance (deployed model)",
        "",
        *[f"- {k}: {v:.4f}" for k, v in imp],
        "",
        "## Fairness on holdout (by gender)",
        "",
        "```json", json.dumps(summary["fairness_holdout"], indent=2), "```",
        "",
        "## Holdout by form version (original vs revised questionnaire)",
        "",
        "```json", json.dumps(summary["holdout_by_form_version"], indent=2), "```",
        "",
        "## Data quality",
        "",
        "```json", json.dumps(quality, indent=2, ensure_ascii=False, default=str), "```",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def stage_real(args):
    raw = gform.read_export(args.gform)
    prepared = gform.prepare(raw)
    print(f"Export: {prepared.report['rows_raw']} rows -> {prepared.report['rows_clean']} clean")
    if config.TARGET not in prepared.data:
        sys.exit("The export has no Psikologis P01-P05 answers, so there is no target to train on.")

    base, base_meta = model.load_base()
    kaggle = data.load_dataset()
    final, metadata, summary = retrain.run(prepared.data, kaggle, base, base_meta, prepared.report,
                                           strata=prepared.form_version)

    if args.dry_run:
        print("Dry run: nothing saved.")
    else:
        model.save(final, metadata, config.REAL_MODEL_PATH, config.REAL_METADATA_PATH)
        config.REAL_SUMMARY_PATH.write_text(json.dumps(summary, indent=2, default=str))
        print(f"Model: {config.REAL_MODEL_PATH}")
        print(f"Summary (aggregates only): {config.REAL_SUMMARY_PATH}")
    report = config.PRIVATE_REPORT_DIR / "real_data_report.md"
    write_report(report, metadata, summary, prepared.report)
    print(f"Report (private): {report}")
    print("Deployed metrics:", {k: round(v, 4) for k, v in metadata["metrics"].items()})


def stage_compare(args):
    from sklearn.dummy import DummyRegressor
    from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import KFold, cross_validate
    from sklearn.tree import DecisionTreeRegressor

    X_train, X_test, y_train, y_test = model.split(data.load_dataset())
    Xtr, Xte = data.encode_gender(X_train), data.encode_gender(X_test)
    candidates = {
        "Mean baseline": DummyRegressor(),
        "Linear Regression": LinearRegression(),
        "Decision Tree (depth 10)": DecisionTreeRegressor(max_depth=10, min_samples_leaf=2,
                                                          random_state=config.RANDOM_STATE),
        "Gradient Boosting": GradientBoostingRegressor(random_state=config.RANDOM_STATE),
        "Random Forest (deployed)": RandomForestRegressor(**config.RF_PARAMS),
    }
    cv = KFold(5, shuffle=True, random_state=config.RANDOM_STATE)
    out = {}
    for name, est in candidates.items():
        res = cross_validate(est, Xtr, y_train, cv=cv,
                             scoring=("neg_mean_absolute_error", "neg_root_mean_squared_error", "r2"))
        test = model.metrics(y_test, est.fit(Xtr, y_train).predict(Xte))
        out[name] = {"cv_mae": float(-res["test_neg_mean_absolute_error"].mean()),
                     "cv_rmse": float(-res["test_neg_root_mean_squared_error"].mean()),
                     "cv_r2": float(res["test_r2"].mean()),
                     "test_mae": test["mae"], "test_rmse": test["rmse"], "test_r2": test["r2"],
                     "fit_seconds": float(res["fit_time"].mean())}
        print(f"{name:26s} CV MAE {out[name]['cv_mae']:.4f}  test MAE {test['mae']:.4f}  R² {test['r2']:.4f}")
    config.MODEL_COMPARISON_PATH.write_text(json.dumps(out, indent=2))
    print(f"-> {config.MODEL_COMPARISON_PATH}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=["kaggle", "real", "compare"], default="kaggle")
    parser.add_argument("--csv", help="kaggle stage: use this CSV instead of downloading from Kaggle")
    parser.add_argument("--gform", help="real stage: Google Form export (.csv/.xlsx)")
    parser.add_argument("--dry-run", action="store_true", help="real stage: run everything, save only the report")
    args = parser.parse_args()
    if args.stage == "real" and not args.gform:
        parser.error("--stage real needs --gform <export>")
    {"kaggle": stage_kaggle, "real": stage_real, "compare": stage_compare}[args.stage](args)


if __name__ == "__main__":
    main()
