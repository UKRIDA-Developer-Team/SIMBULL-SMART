"""Constants lifted from the notebook (code/Copy of EskulSPK2026_SMART_Final.ipynb)."""
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = APP_DIR / "data" / "dataset.csv"
MODEL_PATH = APP_DIR / "models" / "rf_anxiety_model.joblib"
METADATA_PATH = APP_DIR / "models" / "rf_anxiety_model_metadata.json"

KAGGLE_DATASET = "sharmajicoder/student-mental-health-and-burnout"
KAGGLE_FILE = "student_mental_health_burnout_1M.csv"

SAMPLE_FRAC = 0.02      # 1M -> 20k rows (dataset.csv)
TRAIN_FRAC = 0.5        # 20k -> 10k rows for the RF
RANDOM_STATE = 42

# ---- Random Forest ----
TARGET = "anxiety_score"
FEATURES = [
    "age", "gender", "study_hours_per_day", "academic_performance", "exam_pressure",
    "stress_level", "sleep_hours", "physical_activity",
    "financial_stress", "family_expectation", "burnout_score",
]
# Same mapping LabelEncoder produced in the notebook (alphabetical).
GENDER_MAP = {"Female": 0, "Male": 1, "Other": 2}

RF_PARAMS = dict(
    n_estimators=200,
    min_samples_split=2,
    min_samples_leaf=2,
    max_features="sqrt",
    max_depth=10,
    random_state=RANDOM_STATE,
    n_jobs=-1,
)

# ---- SMART ----
CRITERIA = [
    "rf_anxiety_score",
    "study_hours_per_day",
    "academic_performance",
    "sleep_hours",
    "physical_activity",
    "financial_stress",
    "family_expectation",
    "burnout_score",
]

CRITERIA_TYPE = {
    "rf_anxiety_score": "benefit",
    "study_hours_per_day": "benefit",
    "academic_performance": "cost",
    "sleep_hours": "cost",
    "physical_activity": "cost",
    "financial_stress": "benefit",
    "family_expectation": "benefit",
    "burnout_score": "benefit",
}

PRIORITY_WEIGHTS = {c: 1 / len(CRITERIA) for c in CRITERIA}

ALTERNATIVES = ["Sleep", "Exercise", "Study", "Counseling", "Relaxation"]

# Weight A: domain-weighted
WEIGHTS_A = {
    "Sleep": {
        "rf_anxiety_score": 0.15, "study_hours_per_day": 0.10, "academic_performance": 0.10,
        "sleep_hours": 0.40, "physical_activity": 0.05, "financial_stress": 0.05,
        "family_expectation": 0.05, "burnout_score": 0.10,
    },
    "Exercise": {
        "rf_anxiety_score": 0.15, "study_hours_per_day": 0.05, "academic_performance": 0.05,
        "sleep_hours": 0.05, "physical_activity": 0.45, "financial_stress": 0.05,
        "family_expectation": 0.05, "burnout_score": 0.20,
    },
    "Study": {
        "rf_anxiety_score": 0.10, "study_hours_per_day": 0.40, "academic_performance": 0.30,
        "sleep_hours": 0.00, "physical_activity": 0.00, "financial_stress": 0.05,
        "family_expectation": 0.05, "burnout_score": 0.10,
    },
    "Counseling": {
        "rf_anxiety_score": 0.30, "study_hours_per_day": 0.05, "academic_performance": 0.05,
        "sleep_hours": 0.05, "physical_activity": 0.05, "financial_stress": 0.20,
        "family_expectation": 0.15, "burnout_score": 0.15,
    },
    "Relaxation": {
        "rf_anxiety_score": 0.20, "study_hours_per_day": 0.05, "academic_performance": 0.05,
        "sleep_hours": 0.20, "physical_activity": 0.10, "financial_stress": 0.15,
        "family_expectation": 0.15, "burnout_score": 0.10,
    },
}

# Weight B: nearly balanced
WEIGHTS_B = {
    "Sleep": {
        "rf_anxiety_score": 0.15, "study_hours_per_day": 0.15, "academic_performance": 0.10,
        "sleep_hours": 0.20, "physical_activity": 0.10, "financial_stress": 0.10,
        "family_expectation": 0.10, "burnout_score": 0.10,
    },
    "Exercise": {
        "rf_anxiety_score": 0.15, "study_hours_per_day": 0.10, "academic_performance": 0.10,
        "sleep_hours": 0.10, "physical_activity": 0.20, "financial_stress": 0.10,
        "family_expectation": 0.10, "burnout_score": 0.15,
    },
    "Study": {
        "rf_anxiety_score": 0.15, "study_hours_per_day": 0.20, "academic_performance": 0.15,
        "sleep_hours": 0.10, "physical_activity": 0.10, "financial_stress": 0.10,
        "family_expectation": 0.10, "burnout_score": 0.10,
    },
    "Counseling": {
        "rf_anxiety_score": 0.20, "study_hours_per_day": 0.10, "academic_performance": 0.10,
        "sleep_hours": 0.10, "physical_activity": 0.10, "financial_stress": 0.15,
        "family_expectation": 0.15, "burnout_score": 0.10,
    },
    "Relaxation": {
        "rf_anxiety_score": 0.20, "study_hours_per_day": 0.10, "academic_performance": 0.10,
        "sleep_hours": 0.15, "physical_activity": 0.10, "financial_stress": 0.10,
        "family_expectation": 0.10, "burnout_score": 0.15,
    },
}

# Weight C: equal weights (base control). Every alternative ties, so idxmax
# always returns the first one ("Sleep") - keep it only for comparison.
WEIGHTS_C = {alt: dict(PRIORITY_WEIGHTS) for alt in ALTERNATIVES}

WEIGHT_PROFILES = {
    "A - Domain-weighted": WEIGHTS_A,
    "B - Nearly balanced": WEIGHTS_B,
    "C - Equal (control)": WEIGHTS_C,
}

# Input ranges for the single-student form (from file.describe() on the 20k sample).
INPUT_RANGES = {
    "age": (17, 29, 23),
    "study_hours_per_day": (0.0, 14.0, 5.0),
    "academic_performance": (40.0, 100.0, 71.0),
    "exam_pressure": (1.0, 10.0, 6.0),
    "stress_level": (0.0, 10.0, 4.3),
    "sleep_hours": (3.0, 10.0, 6.5),
    "physical_activity": (0.0, 7.0, 3.0),
    "financial_stress": (0.0, 10.0, 5.0),
    "family_expectation": (0.0, 10.0, 6.0),
    "burnout_score": (0.0, 10.0, 1.8),
}
