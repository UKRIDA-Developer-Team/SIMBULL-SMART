"""Constants lifted from the notebook (code/Copy of EskulSPK2026_SMART_Final.ipynb)."""
import os
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = APP_DIR / "data" / "dataset.csv"
SAMPLE_GFORM_PATH = APP_DIR / "data" / "sample_gform.csv"      # SYNTHETIC demo export
PRIVATE_DATA_DIR = APP_DIR / "data" / "private"                  # real exports, gitignored
PRIVATE_REPORT_DIR = APP_DIR / "reports" / "private"             # reports with examples, gitignored

# Base model: pretrained on the Kaggle sample (the notebook's model).
MODEL_PATH = APP_DIR / "models" / "rf_anxiety_model.joblib"
METADATA_PATH = APP_DIR / "models" / "rf_anxiety_model_metadata.json"
# Real model: base model retrained on the Google Form answers (scripts/train.py --stage real).
REAL_MODEL_PATH = APP_DIR / "models" / "rf_real_model.joblib"
REAL_METADATA_PATH = APP_DIR / "models" / "rf_real_model_metadata.json"
REAL_SUMMARY_PATH = APP_DIR / "models" / "real_summary.json"     # aggregates only, no rows
MODEL_COMPARISON_PATH = APP_DIR / "models" / "model_comparison.json"


def active_model_paths():
    """SPK_MODEL=auto (default) uses the real model when it exists; base|real force one."""
    choice = os.environ.get("SPK_MODEL", "auto")
    if choice == "real" or (choice == "auto" and REAL_MODEL_PATH.exists()):
        return REAL_MODEL_PATH, REAL_METADATA_PATH
    return MODEL_PATH, METADATA_PATH

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

def normalize(weights_dict: dict) -> dict:
    """Scale each alternative's weights to sum to 1 (a SMART requirement)."""
    return {alt: {c: v / sum(w.values()) for c, v in w.items()} for alt, w in weights_dict.items()}


# Weight A: domain-weighted, exactly as in the notebook (cell 68).
# Note: the notebook's Exercise weights sum to 1.05, which inflates Exercise scores by 5%.
# The app uses the normalized version WEIGHTS_A below.
WEIGHTS_A_NOTEBOOK = {
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

WEIGHTS_A = normalize(WEIGHTS_A_NOTEBOOK)

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

# (min, max, default) for the advanced form and CSV validation. Covers the Kaggle sample
# (ages 17-29) and the questionnaire population (SMA students, sleep up to 12 h).
INPUT_RANGES = {
    "age": (12, 30, 17),
    "study_hours_per_day": (0.0, 14.0, 5.0),
    "academic_performance": (0.0, 100.0, 75.0),
    "exam_pressure": (1.0, 10.0, 6.0),
    "stress_level": (0.0, 10.0, 4.3),
    "sleep_hours": (3.0, 12.0, 7.0),
    "physical_activity": (0.0, 7.0, 3.0),
    "financial_stress": (0.0, 10.0, 5.0),
    "family_expectation": (0.0, 10.0, 6.0),
    "burnout_score": (0.0, 10.0, 1.8),
}

# ---- Retraining on real questionnaire data ----
REAL_RF_OVERRIDES = dict(min_samples_leaf=3)   # small data: bigger leaves, less memorization
REAL_MIN_ROWS_FOR_BOUNDS = 50                   # below this, keep Kaggle SMART bounds
SUPPRESS_BELOW = 5                              # aggregate cells with fewer rows are hidden

# ---- Ethics / safety ----
# Predicted anxiety at or above this percentile of the reference population always
# shows Counseling and a referral note, whatever the SMART ranking says.
SAFETY_PERCENTILE = 90
# Fill in before deployment (school counselor / campus psychologist / local service).
REFERRAL_CONTACT = {
    "id": "Guru BK sekolah atau psikolog/layanan kesehatan jiwa terdekat",
    "en": "The school counselor (guru BK) or the nearest psychologist / mental-health service",
}

# Example profiles for demos and user testing (Recommendation page buttons).
EXAMPLE_PROFILES = {
    "high": {"age": 17, "gender": "Female", "study_hours_per_day": 9.0, "academic_performance": 58.0,
             "exam_pressure": 9.5, "stress_level": 8.5, "sleep_hours": 4.5, "physical_activity": 0.5,
             "financial_stress": 8.0, "family_expectation": 9.0, "burnout_score": 8.0},
    "low": {"age": 16, "gender": "Male", "study_hours_per_day": 3.0, "academic_performance": 85.0,
            "exam_pressure": 3.0, "stress_level": 2.0, "sleep_hours": 8.0, "physical_activity": 5.0,
            "financial_stress": 2.0, "family_expectation": 4.0, "burnout_score": 1.0},
}
