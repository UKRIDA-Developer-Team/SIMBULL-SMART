"""Offline step: build every artifact the Streamlit app loads.

Replaces the Colab/Drive cells of the notebook. Run from the app/ folder.

Stage 1 - pretrain on Kaggle:
    python scripts/train.py --stage kaggle                  # full file from the kagglehub cache or a download
    python scripts/train.py --stage kaggle --full-csv path  # full 1M-row file at this path

    Pipeline: full 1M-row file -> age filter (config.AGE_RANGE) -> 80/20 train/test split,
    stratified by age. The RF trains on every training row and is scored on every test row.
    20,000 test rows become the app's reference population (data/dataset.csv), so the app
    never shows rows the model was trained on. 8,000 training rows are kept for retraining
    on questionnaire data (data/kaggle_retrain.csv.gz).

Hyperparameter search (5-fold CV on 50,000 training rows; copy the winner into config.RF_PARAMS):
    python scripts/train.py --stage tune

Algorithm comparison (5-fold CV on 50,000 training rows, then every model on the full split):
    python scripts/train.py --stage compare

Stage 2 - retrain on the real Google Form answers (confidential, never committed):
    python scripts/train.py --stage real --gform data/private/gform_raw.csv

The kaggle, tune and compare stages read the full Kaggle file (about 131 MB, cached by kagglehub).

Outputs:
    kaggle : data/dataset.csv, data/kaggle_retrain.csv.gz, models/rf_anxiety_model.joblib (+ _metadata.json)
    tune   : models/rf_tuning.json
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


def load_split(args):
    import pandas as pd

    path = Path(args.full_csv) if getattr(args, "full_csv", None) else data.full_csv_path()
    full = pd.read_csv(path)
    train, test, counts = data.split_full(full)
    lo, hi = config.AGE_RANGE
    print(f"Full file: {counts['full']:,} rows <- {path}")
    print(f"Age {lo}-{hi}: {counts['age_filtered']:,} rows kept ({counts['dropped']:,} dropped)")
    print(f"Split {1 - config.TEST_FRAC:.0%}/{config.TEST_FRAC:.0%} by age: train {counts['train']:,}, test {counts['test']:,}")
    return train, test, counts


def stage_kaggle(args):
    train, test, counts = load_split(args)

    reference = data.reference_rows(test)
    config.DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    reference.to_csv(config.DATA_PATH, index=False)
    data.retrain_rows(train).to_csv(config.RETRAIN_DATA_PATH, index=False)
    print(f"Reference population: {len(reference):,} test rows -> {config.DATA_PATH}")
    print(f"Retraining rows: {config.RETRAIN_KAGGLE_ROWS:,} training rows -> {config.RETRAIN_DATA_PATH}")

    rf, metrics = model.train(train, test)
    print("Metrics on the test set:", {k: round(v, 4) for k, v in metrics.items()})
    ref_metrics = model.metrics(reference[config.TARGET], model.predict(rf, reference))
    print("Metrics on the reference rows:", {k: round(v, 4) for k, v in ref_metrics.items()})

    # Reference min/max for SMART utility, taken over the reference population the app
    # normalizes against.
    criteria_df = reference.copy()
    criteria_df["rf_anxiety_score"] = model.predict(rf, reference)
    bounds = smart.compute_bounds(criteria_df[config.CRITERIA])

    ages = train["age"]
    model.save(rf, {"data_source": "kaggle", "metrics": metrics, "metrics_reference_rows": ref_metrics,
                    "smart_bounds": bounds, "n_rows": counts["train"], "age_range": list(config.AGE_RANGE),
                    "ages_in_data": [int(ages.min()), int(ages.max())],
                    "rows": {**counts, "reference": len(reference)}})
    size_mb = config.MODEL_PATH.stat().st_size / 1e6
    print(f"Model: {config.MODEL_PATH} ({size_mb:.1f} MB)")
    print(f"Metadata: {config.METADATA_PATH}")


TUNE_GRID = {
    "max_depth": [6, 8, 10, 12, 16, None],
    "min_samples_leaf": [2, 10, 50, 200, 1000],
    "max_features": ["sqrt", 0.5, 0.75, 1.0],
    "max_samples": [None, 0.3, 0.6],
}
SEARCH_ROWS = 50_000


def search_rows(train):
    rows = data.stratified_rows(train, SEARCH_ROWS)
    return data.encode_gender(rows[config.FEATURES]), rows[config.TARGET]


def stage_tune(args):
    """Random search over TUNE_GRID with 5-fold CV on training rows. The test set is not touched."""
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import KFold, ParameterSampler, cross_validate

    train, _, _ = load_split(args)
    X, y = search_rows(train)
    cv = KFold(5, shuffle=True, random_state=config.RANDOM_STATE)
    fixed = dict(n_estimators=150, random_state=config.RANDOM_STATE, n_jobs=-1)
    notebook = {k: config.RF_PARAMS_NOTEBOOK.get(k) for k in TUNE_GRID}
    candidates = list(ParameterSampler(TUNE_GRID, n_iter=args.tune_iter, random_state=config.RANDOM_STATE))
    candidates += [notebook] if notebook not in candidates else []
    results = []
    for i, params in enumerate(candidates):
        res = cross_validate(RandomForestRegressor(**fixed, **params), X, y, cv=cv,
                             scoring=("r2", "neg_mean_absolute_error"))
        results.append({"params": params, "cv_r2": float(res["test_r2"].mean()),
                        "cv_r2_std": float(res["test_r2"].std()),
                        "cv_mae": float(-res["test_neg_mean_absolute_error"].mean()),
                        "notebook": params == notebook})
        print(f"  {i + 1:2d}/{len(candidates)}  R² {results[-1]['cv_r2']:.4f}  MAE {results[-1]['cv_mae']:.4f}  {params}",
              flush=True)
    results.sort(key=lambda r: -r["cv_r2"])
    out = {"rows": int(len(X)), "folds": 5, "trees_per_setting": fixed["n_estimators"], "grid": TUNE_GRID,
           "settings_tried": len(results), "best": results[0],
           "notebook": next(r for r in results if r["notebook"]), "results": results}
    config.TUNING_PATH.write_text(json.dumps(out, indent=2))
    print(f"Best: R² {results[0]['cv_r2']:.4f}  {results[0]['params']}")
    print(f"Notebook settings: R² {out['notebook']['cv_r2']:.4f}")
    print(f"-> {config.TUNING_PATH}  (copy the best settings into config.RF_PARAMS, then run --stage kaggle)")


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
    # Same age band as the Kaggle rows; a row without a birth date is kept (age is imputed later).
    lo, hi = config.AGE_RANGE
    in_band = prepared.data["age"].isna() | prepared.data["age"].between(lo, hi)
    prepared.data, prepared.form_version = prepared.data[in_band], prepared.form_version[in_band]
    prepared.report["rows_outside_age_range"] = int((~in_band).sum())
    print(f"Cleaning: age {lo}-{hi} keeps {int(in_band.sum())} rows ({int((~in_band).sum())} dropped)")
    if config.TARGET not in prepared.data:
        sys.exit("The export has no Psikologis P01-P05 answers, so there is no target to train on.")

    base, base_meta = model.load_base()
    kaggle = data.load_retrain_rows()
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
    """5-fold CV on 50,000 training rows, then each model fitted on all training rows and scored on the test set."""
    from sklearn.dummy import DummyRegressor
    from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import KFold, cross_validate
    from sklearn.tree import DecisionTreeRegressor

    train, test, _ = load_split(args)
    Xs, ys = search_rows(train)
    Xtr, ytr = data.encode_gender(train[config.FEATURES]), train[config.TARGET]
    Xte, yte = data.encode_gender(test[config.FEATURES]), test[config.TARGET]
    candidates = {
        "Mean baseline": DummyRegressor(),
        "Linear Regression": LinearRegression(),
        "Decision Tree (depth 10)": DecisionTreeRegressor(max_depth=10, min_samples_leaf=2,
                                                          random_state=config.RANDOM_STATE),
        "Gradient Boosting": HistGradientBoostingRegressor(max_iter=500, learning_rate=0.05,
                                                           random_state=config.RANDOM_STATE),
        "Random Forest (deployed)": RandomForestRegressor(**config.RF_PARAMS),
    }
    cv = KFold(5, shuffle=True, random_state=config.RANDOM_STATE)
    out = {}
    for name, est in candidates.items():
        res = cross_validate(est, Xs, ys, cv=cv,
                             scoring=("neg_mean_absolute_error", "neg_root_mean_squared_error", "r2"))
        if name == "Random Forest (deployed)" and config.MODEL_PATH.exists():
            est, _ = model.load_base()                 # the saved base model: same settings and rows
        else:
            est.fit(Xtr, ytr)
        test_m = model.metrics(yte, est.predict(Xte))
        out[name] = {"cv_mae": float(-res["test_neg_mean_absolute_error"].mean()),
                     "cv_rmse": float(-res["test_neg_root_mean_squared_error"].mean()),
                     "cv_r2": float(res["test_r2"].mean()),
                     "test_mae": test_m["mae"], "test_rmse": test_m["rmse"], "test_r2": test_m["r2"],
                     "fit_seconds": float(res["fit_time"].mean())}
        print(f"{name:26s} CV MAE {out[name]['cv_mae']:.4f}  test MAE {test_m['mae']:.4f}  R² {test_m['r2']:.4f}",
              flush=True)
    config.MODEL_COMPARISON_PATH.write_text(json.dumps(out, indent=2))
    print(f"-> {config.MODEL_COMPARISON_PATH}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=["kaggle", "tune", "real", "compare"], default="kaggle")
    parser.add_argument("--full-csv", help="kaggle/tune/compare: the full 1M-row Kaggle CSV (default: kagglehub cache or download)")
    parser.add_argument("--tune-iter", type=int, default=24, help="tune stage: settings sampled from the grid")
    parser.add_argument("--gform", help="real stage: Google Form export (.csv/.xlsx)")
    parser.add_argument("--dry-run", action="store_true", help="real stage: run everything, save only the report")
    args = parser.parse_args()
    if args.stage == "real" and not args.gform:
        parser.error("--stage real needs --gform <export>")
    {"kaggle": stage_kaggle, "tune": stage_tune, "real": stage_real, "compare": stage_compare}[args.stage](args)


if __name__ == "__main__":
    main()
