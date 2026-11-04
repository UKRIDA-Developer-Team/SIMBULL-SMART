from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from . import config


def full_csv_path() -> Path:
    """The 1M-row Kaggle CSV: the kagglehub cache when it is there, else a download (about 131 MB)."""
    cache = Path.home() / ".cache" / "kagglehub" / "datasets" / config.KAGGLE_DATASET / "versions"
    cached = sorted(cache.glob(f"*/{config.KAGGLE_FILE}"))
    if cached:
        return cached[-1]
    import kagglehub  # only needed offline, not on Streamlit Cloud

    return Path(kagglehub.dataset_download(config.KAGGLE_DATASET)) / config.KAGGLE_FILE


def split_full(full: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Full file -> age filter -> 80/20 train/test, stratified by age. Returns (train, test, counts)."""
    rows = clean(full)
    train, test = train_test_split(rows, test_size=config.TEST_FRAC, random_state=config.RANDOM_STATE,
                                   stratify=rows["age"])
    counts = {"full": int(len(full)), "age_filtered": int(len(rows)), "dropped": int(len(full) - len(rows)),
              "train": int(len(train)), "test": int(len(test))}
    return train.reset_index(drop=True), test.reset_index(drop=True), counts


def stratified_rows(df: pd.DataFrame, n: int) -> pd.DataFrame:
    """A fixed, age-stratified part of df with n rows (all of df when it is smaller)."""
    if n >= len(df):
        return df.reset_index(drop=True)
    rows, _ = train_test_split(df, train_size=n, random_state=config.RANDOM_STATE, stratify=df["age"])
    return rows.reset_index(drop=True)


def reference_rows(test: pd.DataFrame, n: int = config.REFERENCE_ROWS) -> pd.DataFrame:
    """The app's reference population (dataset.csv): n test rows, every Kaggle column kept."""
    return stratified_rows(test, n)


def retrain_rows(train: pd.DataFrame, n: int = config.RETRAIN_KAGGLE_ROWS) -> pd.DataFrame:
    """Kaggle training rows that strategy S2 mixes with questionnaire rows; small enough that weighted real rows count."""
    return stratified_rows(train, n)[config.FEATURES + [config.TARGET]]


def load_retrain_rows(path=config.RETRAIN_DATA_PATH) -> pd.DataFrame:
    """The Kaggle rows for retraining, written by scripts/train.py --stage kaggle."""
    return pd.read_csv(path, float_precision="round_trip")


def clean(df: pd.DataFrame, age_range: tuple[int, int] = config.AGE_RANGE) -> pd.DataFrame:
    """Keep the rows inside the student age band (both ends inclusive). Order is preserved."""
    lo, hi = age_range
    return df[df["age"].between(lo, hi)].reset_index(drop=True)


def load_dataset(path=config.DATA_PATH, clean_rows: bool = True) -> pd.DataFrame:
    """The reference population (20k test rows, all 20 Kaggle columns). clean_rows re-applies the
    age filter, which keeps every row of the current file; it guards files built another way."""
    df = pd.read_csv(path)
    return clean(df) if clean_rows else df


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
