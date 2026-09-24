import pandas as pd

from . import config


def download_sample(frac: float = config.SAMPLE_FRAC) -> pd.DataFrame:
    """Download the 1M-row Kaggle CSV and take the same 2% sample as the notebook."""
    import kagglehub  # only needed offline, not on Streamlit Cloud

    path = kagglehub.dataset_download(config.KAGGLE_DATASET)
    full = pd.read_csv(f"{path}/{config.KAGGLE_FILE}")
    return full.sample(frac=frac, random_state=config.RANDOM_STATE).reset_index(drop=True)


def load_dataset(path=config.DATA_PATH) -> pd.DataFrame:
    return pd.read_csv(path)


def encode_gender(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if not pd.api.types.is_numeric_dtype(out["gender"]):
        unknown = set(out["gender"].unique()) - set(config.GENDER_MAP)
        if unknown:
            raise ValueError(f"Unknown gender values: {sorted(unknown)}")
        out["gender"] = out["gender"].map(config.GENDER_MAP)
    return out


def validate_columns(df: pd.DataFrame) -> list[str]:
    """Return feature columns missing from an uploaded CSV."""
    return [c for c in config.FEATURES if c not in df.columns]
