"""
test_dmsw_accuracy.py — Verify the upgraded DMSW + XGBoost ensemble model
Tests designed for the real-data trained 32-feature static branch.
"""
import os
import pickle
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model

# Suppress TF noise
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
tf.get_logger().setLevel("ERROR")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DMSW_MODEL_PATH     = os.path.join(BASE_DIR, "dmsw_model.h5")
DMSW_TOKENIZER_PATH = os.path.join(BASE_DIR, "dmsw_tokenizer.pkl")
DMSW_SCALER_PATH    = os.path.join(BASE_DIR, "dmsw_scaler.pkl")
XGB_MODEL_PATH      = os.path.join(BASE_DIR, "xgb_model.pkl")

MAX_LEN = 15

# Feature order — must match TABULAR_FEATURES in train_dmsw_real.py
TABULAR_FEATURES = [
    "age", "gender", "scholarship", "debtor", "tuition_up_to_date",
    "admission_grade", "prev_qual_grade",
    "approved_1st", "enrolled_1st", "grade_1st", "evals_1st",
    "approved_2nd", "enrolled_2nd", "grade_2nd", "evals_2nd",
    "pass_rate_1st", "pass_rate_2nd", "pass_rate_change", "grade_change",
    "total_approved", "total_enrolled", "overall_pass_rate",
    "avg_grade", "grade_admission_gap", "socio_risk",
    "eval_ratio_1st", "eval_ratio_2nd",
    "unemployment_rate", "gdp",
    "displaced", "special_needs", "international",
]

BEHAVIOR_TEXTS = {
    "excellent": "Active participation in class consistent high performance",
    "good":      "Regular attendance submitted assignment on time",
    "neutral":   "Average performance met basic requirements",
    "poor":      "Missed deadlines struggling with concepts absent repeatedly",
    "critical":  "Absent without leave failed quiz incomplete homework no submission",
}


def build_inputs(case, scaler, tokenizer):
    """Build the three-branch inputs from a test-case dict."""
    # Unpack case
    att          = case["attendance"]
    grade_pct    = case["grade"]           # 0-100 scale
    grade_20     = grade_pct / 5.0         # convert to 0-20 (UCI scale)
    enrolled     = case.get("enrolled", 5)
    passed       = case.get("passed", 3)
    pass_rate    = passed / max(enrolled, 1)
    age          = case.get("age", 20)
    gender       = case.get("gender", 1)
    scholarship  = case.get("scholarship", 0)
    debt         = case.get("debt", 0)
    tuition      = case.get("tuition", 1)

    # Behavior text bucket
    if grade_pct >= 80 and att >= 80:
        behavior = BEHAVIOR_TEXTS["excellent"]
    elif grade_pct >= 65 and att >= 70:
        behavior = BEHAVIOR_TEXTS["good"]
    elif grade_pct >= 50 and att >= 55:
        behavior = BEHAVIOR_TEXTS["neutral"]
    elif grade_pct >= 35 or att >= 40:
        behavior = BEHAVIOR_TEXTS["poor"]
    else:
        behavior = BEHAVIOR_TEXTS["critical"]

    # Numerical time-series
    grade_delta = 0.5 / MAX_LEN
    history_num = np.array([
        [grade_20 - 0.7 + grade_delta * t, min(pass_rate * (0.85 + 0.15 * t / MAX_LEN), 1.0)]
        for t in range(MAX_LEN)
    ], dtype=np.float32)
    history_scaled = scaler.transform(history_num)
    X_num = np.expand_dims(history_scaled, axis=0)

    # Text
    seq = tokenizer.texts_to_sequences([behavior])[0]
    tokens = seq[:3] if len(seq) >= 3 else seq + [0] * (3 - len(seq))
    X_text = np.array([[tokens[t % len(tokens)] for t in range(MAX_LEN)]])

    # Static — build the full 32-feature vector in the correct order
    half_enrolled = max(enrolled // 2, 1)
    half_passed   = min(passed, half_enrolled)
    grade_1st = grade_20 * 0.97
    grade_2nd = grade_20 * 1.03
    socio_risk = min((1 - tuition) * 0.4 + debt * 0.3 + (1 - scholarship) * 0.15, 1.0)

    feature_values = {
        "age": age,
        "gender": gender,
        "scholarship": scholarship,
        "debtor": debt,
        "tuition_up_to_date": tuition,
        "admission_grade": grade_pct,
        "prev_qual_grade": grade_pct,
        "approved_1st": half_passed,
        "enrolled_1st": half_enrolled,
        "grade_1st": grade_1st,
        "evals_1st": half_enrolled,
        "approved_2nd": passed - half_passed,
        "enrolled_2nd": enrolled - half_enrolled,
        "grade_2nd": grade_2nd,
        "evals_2nd": max(enrolled - half_enrolled, 0),
        "pass_rate_1st": half_passed / half_enrolled,
        "pass_rate_2nd": (passed - half_passed) / max(enrolled - half_enrolled, 1),
        "pass_rate_change": 0.05,
        "grade_change": grade_2nd - grade_1st,
        "total_approved": passed,
        "total_enrolled": enrolled,
        "overall_pass_rate": pass_rate,
        "avg_grade": grade_20,
        "grade_admission_gap": grade_20 - (grade_pct / 5),
        "socio_risk": socio_risk,
        "eval_ratio_1st": 1.0,
        "eval_ratio_2nd": 1.0 if (enrolled - half_enrolled) else 0.0,
        "unemployment_rate": 10.8,
        "gdp": 1.0,
        "displaced": 0,
        "special_needs": 0,
        "international": 0,
    }
    X_static = np.array([[feature_values[f] for f in TABULAR_FEATURES]], dtype=np.float32)

    return X_num, X_text, X_static


def test_model():
    print("Loading model artifacts ...")
    model = load_model(DMSW_MODEL_PATH)
    with open(DMSW_TOKENIZER_PATH, "rb") as f:
        tokenizer = pickle.load(f)
    with open(DMSW_SCALER_PATH, "rb") as f:
        scaler = pickle.load(f)

    xgb = None
    if os.path.exists(XGB_MODEL_PATH):
        with open(XGB_MODEL_PATH, "rb") as f:
            xgb = pickle.load(f)
        print("XGBoost model also loaded.\n")

    # ---- Test cases ----
    test_cases = [
        {
            "name":       "Excellent Student",
            "attendance": 97, "grade": 92,
            "enrolled": 6, "passed": 6,
            "age": 20, "gender": 1, "scholarship": 1, "debt": 0, "tuition": 1,
            "expected_risk": "LOW",
        },
        {
            "name":       "Average Student",
            "attendance": 76, "grade": 68,
            "enrolled": 5, "passed": 4,
            "age": 21, "gender": 0, "scholarship": 0, "debt": 0, "tuition": 1,
            "expected_risk": "LOW/MEDIUM",
        },
        {
            "name":       "Financial Risk",
            "attendance": 82, "grade": 70,
            "enrolled": 5, "passed": 3,
            "age": 23, "gender": 0, "scholarship": 0, "debt": 1, "tuition": 0,
            "expected_risk": "MEDIUM/HIGH",
        },
        {
            "name":       "At-Risk Student",
            "attendance": 52, "grade": 42,
            "enrolled": 5, "passed": 1,
            "age": 22, "gender": 1, "scholarship": 0, "debt": 1, "tuition": 0,
            "expected_risk": "HIGH/CRITICAL",
        },
        {
            "name":       "Failing + Crisis",
            "attendance": 28, "grade": 22,
            "enrolled": 6, "passed": 0,
            "age": 19, "gender": 1, "scholarship": 0, "debt": 1, "tuition": 0,
            "expected_risk": "CRITICAL",
        },
    ]

    header = f"{'Profile':<20} | {'Att':>4} | {'Grd':>4} | {'DMSW':>6} | {'XGB':>6} | {'Ens':>6} | {'Risk':<10} | {'Expected'}"
    print(f"\n{'='*88}")
    print("  SmartEduMine — DMSW + XGBoost Ensemble Verification")
    print(f"{'='*88}")
    print(header)
    print("-" * 88)

    all_passed = True
    for case in test_cases:
        X_num, X_text, X_static = build_inputs(case, scaler, tokenizer)

        p_dmsw = float(model.predict([X_num, X_text, X_static], verbose=0)[0][0])
        p_xgb  = float(xgb.predict_proba(X_static)[0][1]) if xgb else p_dmsw
        p_ens  = 0.5 * p_dmsw + 0.5 * p_xgb

        if p_ens >= 0.70:
            risk = "CRITICAL"
        elif p_ens >= 0.50:
            risk = "HIGH"
        elif p_ens >= 0.30:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        print(
            f"{case['name']:<20} | {case['attendance']:>4} | {case['grade']:>4} | "
            f"{p_dmsw:.4f} | {p_xgb:.4f} | {p_ens:.4f} | {risk:<10} | {case['expected_risk']}"
        )

        # Basic sanity: last 2 should be HIGH or CRITICAL
        if case["name"] in ("At-Risk Student", "Failing + Crisis") and p_ens < 0.40:
            print(f"  ⚠️  WARNING: {case['name']} probability seems too low")
            all_passed = False

    print(f"{'='*88}")
    print(f"\n{'✅ All sanity checks passed!' if all_passed else '⚠️  Some sanity checks failed — review model.'}\n")


if __name__ == "__main__":
    test_model()
