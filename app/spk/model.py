import json

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from . import config
from .data import encode_gender


def metrics(y_true, y_pred) -> dict:
    mse = mean_squared_error(y_true, y_pred)
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "mse": float(mse),
        "rmse": float(np.sqrt(mse)),
        "r2": float(r2_score(y_true, y_pred)) if len(y_true) > 1 else float("nan"),
    }


def kaggle_test_set(reference: pd.DataFrame):
    """Kaggle rows the app scores the model on: the reference population, part of the test set.

    No model has trained on these rows. The headline metrics in the metadata come from the
    whole test set. Returns (X, y) with gender still as text.
    """
    return reference[config.FEATURES], reference[config.TARGET]


def train(train_rows: pd.DataFrame, test_rows: pd.DataFrame):
    """Fit the RF on the training rows and score it on the test rows. Returns (model, metrics)."""
    model = RandomForestRegressor(**config.RF_PARAMS)
    model.fit(encode_gender(train_rows[config.FEATURES]), train_rows[config.TARGET])
    return model, metrics(test_rows[config.TARGET], predict(model, test_rows))


def predict(model, df: pd.DataFrame) -> np.ndarray:
    return model.predict(encode_gender(df[config.FEATURES]))


def save(model, metadata: dict, model_path=config.MODEL_PATH, metadata_path=config.METADATA_PATH):
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path, compress=3)
    metadata = {
        "model_type": "RandomForestRegressor",
        "target": config.TARGET,
        "features": config.FEATURES,
        "gender_map": config.GENDER_MAP,
        "sklearn_version": sklearn.__version__,
        "hyperparameters": {k: v for k, v in config.RF_PARAMS.items()},
        **metadata,
    }
    metadata_path.write_text(json.dumps(metadata, indent=2))


def load(model_path=None, metadata_path=None):
    """Load the active model (real if present, else base) unless paths are given."""
    if model_path is None:
        model_path, metadata_path = config.active_model_paths()
    model = joblib.load(model_path)
    # Predict on one thread. With several threads the trees' outputs are summed in a varying
    # order, so the same student can differ in the last bit between two calls, which is enough
    # to flip the safety rule for a prediction exactly at the cutoff.
    model.set_params(n_jobs=1)
    metadata = json.loads(metadata_path.read_text())
    metadata.setdefault("data_source", "kaggle")
    return model, metadata


def load_base():
    return load(config.MODEL_PATH, config.METADATA_PATH)
