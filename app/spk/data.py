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


def validate_values(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Coerce the 11 feature columns, blank out impossible values, report what changed.

    Returns (frame, issues) where issues = {"non_numeric": {col: n}, "out_of_range": {col: n},
    "bad_gender": [values], "missing": {col: n}}.
    """
    out = df.copy()
    issues = {"non_numeric": {}, "out_of_range": {}, "bad_gender": [], "missing": {}}
    for c in config.FEATURES:
        if c == "gender":
            if pd.api.types.is_numeric_dtype(out[c]):
                inverse = {v: k for k, v in config.GENDER_MAP.items()}
                out[c] = out[c].map(inverse)
            s = out[c].astype("string").str.strip().str.capitalize()
            bad = s.notna() & ~s.isin(list(config.GENDER_MAP))
            issues["bad_gender"] = sorted(map(str, s[bad].unique()))
            out[c] = s.where(~bad).astype(object)
            continue
        num = pd.to_numeric(out[c], errors="coerce")
        n_bad = int((num.isna() & out[c].notna()).sum())
        if n_bad:
            issues["non_numeric"][c] = n_bad
        lo, hi = config.INPUT_RANGES[c][:2]
        outside = num.notna() & ~num.between(lo, hi)
        if outside.any():
            issues["out_of_range"][c] = int(outside.sum())
        out[c] = num.where(~outside)
    issues["missing"] = {c: int(n) for c, n in out[config.FEATURES].isna().sum().items() if n}
    return out, issues
