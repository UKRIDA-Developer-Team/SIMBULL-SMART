import json

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

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


def split(df: pd.DataFrame):
    """The notebook's split: 50% sample of the 20k rows, then 80/20 train/test.

    Returns (X_train, X_test, y_train, y_test) with gender still as text.
    """
    rf_df = df.sample(frac=config.TRAIN_FRAC, random_state=config.RANDOM_STATE)
    return train_test_split(
        rf_df[config.FEATURES], rf_df[config.TARGET], test_size=0.2, random_state=config.RANDOM_STATE
    )


def train(df: pd.DataFrame):
    """Train the RF exactly like the notebook. Returns (model, metrics, X_test, y_test)."""
    X_train, X_test, y_train, y_test = split(df)
    model = RandomForestRegressor(**config.RF_PARAMS)
    model.fit(encode_gender(X_train), y_train)
    return model, metrics(y_test, predict(model, X_test)), X_test, y_test


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
    metadata = json.loads(metadata_path.read_text())
    metadata.setdefault("data_source", "kaggle")
    return model, metadata


def load_base():
    return load(config.MODEL_PATH, config.METADATA_PATH)
