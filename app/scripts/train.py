"""Offline step: build every artifact the Streamlit app loads.

Replaces the Colab/Drive cells of the notebook. Run from the app/ folder:

    python scripts/train.py               # download from Kaggle, sample 20k, train
    python scripts/train.py --csv path    # reuse an existing dataset.csv (e.g. the one on Drive)

Outputs:
    data/dataset.csv                          20k-row sample
    models/rf_anxiety_model.joblib            RandomForestRegressor
    models/rf_anxiety_model_metadata.json     features, gender map, metrics, SMART bounds
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from spk import config, data, model, smart  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", help="use this CSV instead of downloading from Kaggle")
    args = parser.parse_args()

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

    model.save(rf, {"metrics": metrics, "smart_bounds": bounds, "n_rows": len(df)})
    size_mb = config.MODEL_PATH.stat().st_size / 1e6
    print(f"Model: {config.MODEL_PATH} ({size_mb:.1f} MB)")
    print(f"Metadata: {config.METADATA_PATH}")


if __name__ == "__main__":
    main()
