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


def train(df: pd.DataFrame):
    """Train the RF exactly like the notebook. Returns (model, metrics, X_test, y_test)."""
    rf_df = df.sample(frac=config.TRAIN_FRAC, random_state=config.RANDOM_STATE)
    X = encode_gender(rf_df[config.FEATURES])
    y = rf_df[config.TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=config.RANDOM_STATE
    )
    model = RandomForestRegressor(**config.RF_PARAMS)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    metrics = {
        "mae": float(mean_absolute_error(y_test, y_pred)),
        "mse": float(mse),
        "rmse": float(np.sqrt(mse)),
        "r2": float(r2_score(y_test, y_pred)),
    }
    return model, metrics, X_test, y_test


def predict(model, df: pd.DataFrame) -> np.ndarray:
    return model.predict(encode_gender(df[config.FEATURES]))


def save(model, metadata: dict):
    config.MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, config.MODEL_PATH, compress=3)
    metadata = {
        "model_type": "RandomForestRegressor",
        "target": config.TARGET,
        "features": config.FEATURES,
        "gender_map": config.GENDER_MAP,
        "sklearn_version": sklearn.__version__,
        "hyperparameters": {k: v for k, v in config.RF_PARAMS.items()},
        **metadata,
    }
    config.METADATA_PATH.write_text(json.dumps(metadata, indent=2))


def load():
    model = joblib.load(config.MODEL_PATH)
    metadata = json.loads(config.METADATA_PATH.read_text())
    return model, metadata
