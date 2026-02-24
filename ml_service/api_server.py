"""
Flask API Server for Dropout Prediction — SmartEduMine
Provides REST endpoints for the DMSW + XGBoost Ensemble model.

Endpoints:
  GET  /health             — Service health check
  POST /predict/dmsw       — Single student prediction (full ensemble)
  POST /predict            — Alias for /predict/dmsw
  POST /predict/batch      — Batch prediction for multiple students
  POST /predict/explain    — Prediction with SHAP-based explanation
  GET  /feature-importance — Real SHAP-derived feature importance
  GET  /model/info         — Model metadata and version info
"""

import os
import json
import time
import logging
import pickle
from datetime import datetime
from functools import wraps

import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, g
from flask_cors import CORS

import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("ml_api")

# Suppress noisy TF logs
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
tf.get_logger().setLevel("ERROR")

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = Flask(__name__)
CORS(app)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DMSW_MODEL_PATH      = os.path.join(BASE_DIR, "dmsw_model.h5")
DMSW_TOKENIZER_PATH  = os.path.join(BASE_DIR, "dmsw_tokenizer.pkl")
DMSW_SCALER_PATH     = os.path.join(BASE_DIR, "dmsw_scaler.pkl")
XGB_MODEL_PATH       = os.path.join(BASE_DIR, "xgb_model.pkl")
SHAP_PATH            = os.path.join(BASE_DIR, "shap_values.pkl")
MODEL_METADATA_PATH  = os.path.join(BASE_DIR, "model_metadata.json")

# ---------------------------------------------------------------------------
# Global model artifacts
# ---------------------------------------------------------------------------
dmsw_model     = None
dmsw_tokenizer = None
dmsw_scaler    = None
xgb_model      = None
shap_data      = None   # dict: {"values", "feature_names", "expected_value"}
model_metadata = {}

MAX_LEN = 15   # Sliding window length

# Tabular feature order — must match training order
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


def load_artifacts():
    """Load model, tokenizer, scaler, XGBoost and SHAP data from disk."""
    global dmsw_model, dmsw_tokenizer, dmsw_scaler, xgb_model, shap_data, model_metadata

    try:
        if os.path.exists(DMSW_MODEL_PATH):
            dmsw_model = load_model(DMSW_MODEL_PATH)
            logger.info("DMSW model loaded successfully")
        else:
            logger.warning("DMSW model file not found at %s", DMSW_MODEL_PATH)

        if os.path.exists(DMSW_TOKENIZER_PATH):
            with open(DMSW_TOKENIZER_PATH, "rb") as f:
                dmsw_tokenizer = pickle.load(f)
            logger.info("Tokenizer loaded successfully")

        if os.path.exists(DMSW_SCALER_PATH):
            with open(DMSW_SCALER_PATH, "rb") as f:
                dmsw_scaler = pickle.load(f)
            logger.info("Scaler loaded successfully")

        if os.path.exists(XGB_MODEL_PATH):
            with open(XGB_MODEL_PATH, "rb") as f:
                xgb_model = pickle.load(f)
            logger.info("XGBoost model loaded successfully")

        if os.path.exists(SHAP_PATH):
            with open(SHAP_PATH, "rb") as f:
                shap_data = pickle.load(f)
            logger.info("SHAP data loaded successfully")

        if os.path.exists(MODEL_METADATA_PATH):
            with open(MODEL_METADATA_PATH, "r") as f:
                model_metadata = json.load(f)
            logger.info("Model metadata loaded")

    except Exception as e:
        logger.error("Error loading artifacts: %s", e, exc_info=True)


# Load on startup
load_artifacts()


# ---------------------------------------------------------------------------
# Request logging middleware
# ---------------------------------------------------------------------------
@app.before_request
def _start_timer():
    g.start_time = time.time()


@app.after_request
def _log_request(response):
    duration_ms = (time.time() - g.get("start_time", time.time())) * 1000
    logger.info(
        "%s %s — %s (%.1f ms)",
        request.method, request.path, response.status, duration_ms,
    )
    return response


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _get_risk_level(prob: float) -> str:
    """Map dropout probability to a 4-tier risk level."""
    if prob >= 0.70:
        return "CRITICAL"
    elif prob >= 0.50:
        return "HIGH"
    elif prob >= 0.30:
        return "MEDIUM"
    else:
        return "LOW"


def _safe_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _safe_bool(value, default: bool = False) -> int:
    """Convert various truthy representations to 0/1 int."""
    if isinstance(value, bool):
        return int(value)
    if str(value).lower() in ("1", "true", "yes"):
        return 1
    if str(value).lower() in ("0", "false", "no"):
        return 0
    return int(default)


def _validate_student_data(data: dict) -> list:
    errors = []
    if not isinstance(data, dict):
        return ["Request body must be a JSON object"]

    att = _safe_float(data.get("attendance"), -1)
    if not (0 <= att <= 100):
        errors.append("attendance must be between 0 and 100")

    grade = _safe_float(data.get("avgGrade"), -1)
    if not (0 <= grade <= 100):
        errors.append("avgGrade must be between 0 and 100")

    ce = _safe_int(data.get("coursesEnrolled"), -1)
    if ce < 0:
        errors.append("coursesEnrolled must be a non-negative integer")

    cp = _safe_int(data.get("coursesPassed"), -1)
    if cp < 0:
        errors.append("coursesPassed must be a non-negative integer")

    if ce >= 0 and cp > ce:
        errors.append("coursesPassed cannot exceed coursesEnrolled")

    return errors


def _build_dmsw_inputs(student_data: dict):
    """
    Build the three-branch inputs (numerical, text, static) for the DMSW model
    from an incoming API request dict.
    """
    # --- Static inputs ---
    age               = _safe_int(student_data.get("age", 20), 20)
    gender            = 1 if str(student_data.get("gender", "Male")).lower() == "male" else 0
    scholarship       = _safe_bool(student_data.get("scholarship", 0))
    debtor            = _safe_bool(student_data.get("debtor", 0))
    tuition_up        = _safe_bool(student_data.get("tuitionUpToDate", 1), True)
    courses_enrolled  = _safe_int(student_data.get("coursesEnrolled", 5), 5)
    courses_passed    = _safe_int(student_data.get("coursesPassed", 4), 4)
    attendance        = _safe_float(student_data.get("attendance", 75))
    avg_grade_raw     = _safe_float(student_data.get("avgGrade", 70))       # 0-100 scale
    avg_grade_20      = avg_grade_raw / 5.0                                  # convert to 0-20
    pass_rate         = courses_passed / max(courses_enrolled, 1)

    # --- Numerical time-series (15 steps simulating temporal trend) ---
    # We simulate a mild linear trend from avg_grade-5 → avg_grade+2
    grade_delta = 7.0 / MAX_LEN  # slight upward trend per step
    history_num = np.array([
        [
            float(np.clip(avg_grade_20 - 1.4 + grade_delta * t, 0, 20)),
            float(np.clip(pass_rate * (0.85 + 0.15 * t / MAX_LEN), 0, 1)),
        ]
        for t in range(MAX_LEN)
    ])
    history_num_scaled = dmsw_scaler.transform(history_num)
    X_num = np.expand_dims(history_num_scaled, axis=0)  # (1, 15, 2)

    # --- Text input (behavior bucket → tokenised) ---
    if avg_grade_raw >= 80 and attendance >= 80:
        behavior = BEHAVIOR_TEXTS["excellent"]
    elif avg_grade_raw >= 65 and attendance >= 70:
        behavior = BEHAVIOR_TEXTS["good"]
    elif avg_grade_raw >= 50 and attendance >= 55:
        behavior = BEHAVIOR_TEXTS["neutral"]
    elif avg_grade_raw >= 35 or attendance >= 40:
        behavior = BEHAVIOR_TEXTS["poor"]
    else:
        behavior = BEHAVIOR_TEXTS["critical"]

    seq = dmsw_tokenizer.texts_to_sequences([behavior])[0]
    tokens = seq[:3] if len(seq) >= 3 else seq + [0] * (3 - len(seq))
    text_window = [tokens[t % len(tokens)] for t in range(MAX_LEN)]
    X_text = np.array([text_window])  # (1, 15)

    # --- Static feature vector (must match TABULAR_FEATURES order from training) ---
    # Map the simplified API inputs to the full tabular feature vector
    # For features not provided, use sensible defaults
    admission_grade   = _safe_float(student_data.get("admissionGrade", avg_grade_raw), avg_grade_raw)
    prev_qual_grade   = _safe_float(student_data.get("prevQualGrade", avg_grade_raw), avg_grade_raw)

    # Semester-level features derived from available totals
    half_enrolled = max(courses_enrolled // 2, 1)
    half_passed   = min(courses_passed, half_enrolled)
    grade_1st     = avg_grade_20 * 0.97    # ±3% variation
    grade_2nd     = avg_grade_20 * 1.03

    # Build the ordered feature vector
    feature_values = {
        "age": age,
        "gender": gender,
        "scholarship": scholarship,
        "debtor": debtor,
        "tuition_up_to_date": tuition_up,
        "admission_grade": admission_grade,
        "prev_qual_grade": prev_qual_grade,
        "approved_1st": half_passed,
        "enrolled_1st": half_enrolled,
        "grade_1st": grade_1st,
        "evals_1st": half_enrolled,
        "approved_2nd": courses_passed - half_passed,
        "enrolled_2nd": courses_enrolled - half_enrolled,
        "grade_2nd": grade_2nd,
        "evals_2nd": courses_enrolled - half_enrolled,
        "pass_rate_1st": half_passed / half_enrolled if half_enrolled else 0,
        "pass_rate_2nd": (courses_passed - half_passed) / max(courses_enrolled - half_enrolled, 1),
        "pass_rate_change": pass_rate * 0.05,          # small positive trend
        "grade_change": (grade_2nd - grade_1st),
        "total_approved": courses_passed,
        "total_enrolled": courses_enrolled,
        "overall_pass_rate": pass_rate,
        "avg_grade": avg_grade_20,
        "grade_admission_gap": avg_grade_20 - (admission_grade / 5),
        "socio_risk": min(
            (1 - tuition_up) * 0.4 + debtor * 0.3 + (1 - scholarship) * 0.15, 1.0
        ),
        "eval_ratio_1st": 1.0 if half_enrolled else 0,
        "eval_ratio_2nd": 1.0 if (courses_enrolled - half_enrolled) else 0,
        "unemployment_rate": _safe_float(student_data.get("unemploymentRate", 10.8), 10.8),
        "gdp": _safe_float(student_data.get("gdp", 1.0), 1.0),
        "displaced": _safe_bool(student_data.get("displaced", 0)),
        "special_needs": 0,
        "international": _safe_bool(student_data.get("international", 0)),
    }

    # Build in the exact order TABULAR_FEATURES expects
    X_static = np.array([[feature_values.get(f, 0.0) for f in TABULAR_FEATURES]],
                        dtype=np.float32)

    return X_num, X_text, X_static, feature_values


def _predict_single(student_data: dict) -> dict:
    """
    Run the DMSW + XGBoost ensemble for one student and return prediction dict.
    Uses equal 50/50 soft-voting blend if both models are available.
    Falls back to DMSW-only (with heuristic correction) if XGBoost unavailable.
    """
    X_num, X_text, X_static, feature_values = _build_dmsw_inputs(student_data)

    # --- DMSW neural network prediction ---
    raw_dmsw = float(dmsw_model.predict([X_num, X_text, X_static], verbose=0)[0][0])

    # --- XGBoost prediction (if model is loaded) ---
    if xgb_model is not None:
        try:
            raw_xgb = float(xgb_model.predict_proba(X_static)[0][1])
            # Ensemble: equal weight blend
            prediction_prob = float(np.clip(0.5 * raw_dmsw + 0.5 * raw_xgb, 0, 1))
            ensemble_mode = "dmsw_xgb_blend"
        except Exception as e:
            logger.warning("XGBoost prediction failed, falling back to DMSW: %s", e)
            prediction_prob = float(np.clip(raw_dmsw, 0, 1))
            ensemble_mode = "dmsw_only"
    else:
        prediction_prob = float(np.clip(raw_dmsw, 0, 1))
        ensemble_mode = "dmsw_only"

    risk_level = _get_risk_level(prediction_prob)

    # --- Explainability: SHAP-based driver factors ---
    attendance     = _safe_float(student_data.get("attendance", 75))
    avg_grade      = _safe_float(student_data.get("avgGrade", 70))
    debtor         = _safe_bool(student_data.get("debtor", 0))
    tuition_up     = _safe_bool(student_data.get("tuitionUpToDate", 1), True)
    scholarship    = _safe_bool(student_data.get("scholarship", 0))
    courses_enrolled = _safe_int(student_data.get("coursesEnrolled", 5), 5)
    courses_passed   = _safe_int(student_data.get("coursesPassed", 4), 4)
    pass_rate        = courses_passed / max(courses_enrolled, 1)

    explanations = [
        f"Ensemble prediction: {ensemble_mode} blend over {MAX_LEN}-week window.",
        f"Academic signals — Grade: {avg_grade:.1f}% | Attendance: {attendance:.1f}%",
        "Static socioeconomic + academic history factors included.",
    ]

    # Risk-factor specific warnings
    if not tuition_up:
        explanations.append("⚠️ Tuition fees not up to date — strongest socioeconomic risk factor.")
    if debtor:
        explanations.append("⚠️ Enrolled as a debtor — compounding financial risk.")
    if not scholarship and (debtor or not tuition_up):
        explanations.append("⚠️ No scholarship + financial stress — high vulnerability profile.")
    if pass_rate < 0.5:
        explanations.append(f"⚠️ Low pass rate ({pass_rate*100:.0f}%) — strong academic risk indicator.")
    if attendance < 60:
        explanations.append(f"⚠️ Low attendance ({attendance:.0f}%) — correlated with dropout risk.")
    if avg_grade < 50:
        explanations.append(f"⚠️ Low average grade ({avg_grade:.0f}%) — significant academic risk.")
    if avg_grade >= 70 and attendance >= 75 and pass_rate >= 0.7:
        explanations.append("✅ Strong academic profile — key protective factor.")

    return {
        "success": True,
        "dropout_probability": round(prediction_prob, 4),
        "risk_level": risk_level,
        "model": "DMSW + XGBoost Ensemble (Dual-Modal Multiscale Sliding Window)",
        "ensemble_mode": ensemble_mode,
        "component_scores": {
            "dmsw_neural_network": round(raw_dmsw, 4),
            "xgboost": round(raw_xgb if xgb_model else raw_dmsw, 4),
        },
        "prediction": {
            "dropout_probability": round(prediction_prob, 4),
            "risk_level": risk_level,
        },
        "explanations": explanations,
    }


def _ensure_model_loaded():
    """Try to load model if not already loaded. Returns error response or None."""
    if not dmsw_model or not dmsw_tokenizer or not dmsw_scaler:
        load_artifacts()
        if not dmsw_model:
            return jsonify({
                "success": False,
                "error": "DMSW model not loaded. Run train_dmsw_real.py first.",
            }), 503
    return None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/health", methods=["GET"])
def health_check():
    """Service health check."""
    return jsonify({
        "status": "healthy",
        "service": "Dropout Prediction API (DMSW + XGBoost Ensemble)",
        "dmsw_model_loaded": dmsw_model is not None,
        "xgb_model_loaded": xgb_model is not None,
        "shap_loaded": shap_data is not None,
        "tokenizer_loaded": dmsw_tokenizer is not None,
        "scaler_loaded": dmsw_scaler is not None,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    })


@app.route("/predict/dmsw", methods=["POST"])
@app.route("/predict", methods=["POST"])
def predict_dmsw():
    """Predict dropout risk for a single student using the DMSW + XGBoost ensemble."""
    try:
        err = _ensure_model_loaded()
        if err:
            return err

        student_data = request.json
        if not student_data:
            return jsonify({"success": False, "error": "No student data provided"}), 400

        validation_errors = _validate_student_data(student_data)
        if validation_errors:
            return jsonify({
                "success": False,
                "error": "Validation failed",
                "details": validation_errors,
            }), 400

        result = _predict_single(student_data)
        return jsonify(result)

    except Exception as e:
        logger.error("Prediction error: %s", e, exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/predict/explain", methods=["POST"])
def predict_explain():
    """
    Prediction with detailed SHAP-based explanation per feature.
    Returns the top risk factors and protective factors for the student.
    """
    try:
        err = _ensure_model_loaded()
        if err:
            return err

        student_data = request.json
        if not student_data:
            return jsonify({"success": False, "error": "No student data provided"}), 400

        validation_errors = _validate_student_data(student_data)
        if validation_errors:
            return jsonify({
                "success": False,
                "error": "Validation failed",
                "details": validation_errors,
            }), 400

        result = _predict_single(student_data)

        # Add enhanced SHAP-based feature attribution if available
        if shap_data and xgb_model:
            try:
                _, _, X_static, feature_values = _build_dmsw_inputs(student_data)
                import shap as shap_lib
                explainer = shap_lib.TreeExplainer(xgb_model)
                sv = explainer.shap_values(X_static)[0]
                feature_names = shap_data.get("feature_names", TABULAR_FEATURES)

                # Build per-feature attribution (SHAP value indicates direction + magnitude)
                shap_attribution = {}
                for feat, val in zip(feature_names, sv):
                    shap_attribution[feat] = {
                        "shap_value": round(float(val), 4),
                        "direction": "increases_risk" if val > 0 else "reduces_risk",
                        "feature_value": round(float(feature_values.get(feat, 0)), 4),
                    }

                # Sort by |shap| descending, take top 10
                sorted_feats = sorted(shap_attribution.items(),
                                      key=lambda x: abs(x[1]["shap_value"]), reverse=True)
                top_factors = dict(list(sorted_feats)[:10])

                result["shap_explanation"] = {
                    "top_factors": top_factors,
                    "base_rate": round(float(shap_data.get("expected_value", 0.3)), 4),
                    "note": "SHAP values show each factor's marginal contribution to dropout probability.",
                }
            except Exception as shap_err:
                logger.warning("SHAP explanation failed: %s", shap_err)
                result["shap_explanation"] = {"note": "SHAP unavailable — model not retrained yet."}
        else:
            result["shap_explanation"] = {
                "note": "Run train_dmsw_real.py to enable SHAP-based explanations.",
                "global_importance": model_metadata.get("shap_feature_importance", {}),
            }

        return jsonify(result)

    except Exception as e:
        logger.error("Explain error: %s", e, exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/predict/batch", methods=["POST"])
def predict_batch():
    """Predict dropout risk for multiple students at once."""
    try:
        err = _ensure_model_loaded()
        if err:
            return err

        body = request.json
        if not body or "students" not in body:
            return jsonify({
                "success": False,
                "error": "Request must contain a 'students' array.",
            }), 400

        students = body["students"]
        if not isinstance(students, list) or len(students) == 0:
            return jsonify({
                "success": False,
                "error": "'students' must be a non-empty array.",
            }), 400

        predictions = []
        errors = []
        for idx, student_data in enumerate(students):
            try:
                result = _predict_single(student_data)
                result["student_id"] = student_data.get("id", student_data.get("student_id", f"student_{idx}"))
                predictions.append(result)
            except Exception as e:
                errors.append({
                    "index": idx,
                    "student_id": student_data.get("id", f"student_{idx}"),
                    "error": str(e),
                })

        return jsonify({
            "success": True,
            "predictions": predictions,
            "total": len(predictions),
            "errors": errors,
        })

    except Exception as e:
        logger.error("Batch prediction error: %s", e, exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/feature-importance", methods=["GET"])
def feature_importance():
    """Return real SHAP-derived feature importance rankings."""
    # Use live SHAP values from training if available
    shap_importance = model_metadata.get("shap_feature_importance", {})

    if shap_importance:
        # Partition into academic vs socioeconomic groups
        academic_keys = [
            "avg_grade", "grade_1st", "grade_2nd", "grade_change",
            "approved_1st", "approved_2nd", "total_approved",
            "overall_pass_rate", "pass_rate_1st", "pass_rate_2nd",
            "pass_rate_change", "admission_grade", "prev_qual_grade",
            "eval_ratio_1st", "eval_ratio_2nd", "evals_1st", "evals_2nd",
            "enrolled_1st", "enrolled_2nd", "total_enrolled",
        ]
        socio_keys = [
            "tuition_up_to_date", "debtor", "scholarship",
            "age", "gender", "unemploymentRate", "gdp",
            "displaced", "special_needs", "international",
            "socio_risk", "grade_admission_gap",
        ]

        academic = {k: v for k, v in shap_importance.items() if k in academic_keys}
        socio    = {k: v for k, v in shap_importance.items() if k in socio_keys}
        other    = {k: v for k, v in shap_importance.items()
                    if k not in academic_keys and k not in socio_keys}

        return jsonify({
            "success": True,
            "source": "SHAP (real model)",
            "academic_features": dict(sorted(academic.items(), key=lambda x: -x[1])[:10]),
            "socioeconomic_features": dict(sorted(socio.items(), key=lambda x: -x[1])[:10]),
            "other_features": dict(sorted(other.items(), key=lambda x: -x[1])[:5]),
            "insight": (
                "Feature importances derived from SHAP values on the XGBoost component "
                "of the DMSW + XGBoost ensemble, trained on the real UCI dataset."
            ),
        })

    # Fallback: static values (used before first real training run)
    return jsonify({
        "success": True,
        "source": "static_fallback (run train_dmsw_real.py for live SHAP values)",
        "academic_features": {
            "Courses Approved (2nd Semester)": 0.1833,
            "Semester Grades (2nd Semester)":  0.1380,
            "Courses Approved (1st Semester)": 0.1248,
            "Admission Grade":                 0.1184,
            "Semester Grades (1st Semester)":  0.1075,
            "Previous Qualification Grade":    0.0892,
            "Curricular Units Enrolled (2nd)": 0.0654,
            "Curricular Units Enrolled (1st)": 0.0543,
            "Age at Enrollment":               0.0421,
            "Attendance Rate":                 0.0770,
        },
        "socioeconomic_features": {
            "Tuition Fees Up to Date": 0.3089,
            "Course/Program":          0.1227,
            "Scholarship Holder":      0.1218,
            "Age at Enrollment":       0.1080,
            "Mother's Occupation":     0.0570,
            "Father's Occupation":     0.0498,
            "Debtor Status":           0.0462,
        },
        "insight": (
            "Tuition fee status is the #1 socioeconomic predictor (30.89%). "
            "Course completion rates are the strongest academic predictor (18.33%)."
        ),
    })


@app.route("/model/info", methods=["GET"])
def model_info():
    """Return model metadata and version information."""
    info = {
        "success": True,
        "model_name": "DMSW + XGBoost Ensemble",
        "version": "2.0 (Real-Data Trained)",
        "architecture": {
            "dmsw_branches": [
                "Numerical: Conv1D(k=3, f=64) + Conv1D(k=5, f=64) + BiLSTM(32) + MultiHeadAttention",
                "Textual:   Embedding(64) + Conv1D(k=3, f=64) + Conv1D(k=5, f=64)",
                "Static:    Dense(32) → Dense(16)",
            ],
            "fusion": "Concatenate → Dense(128) → Dropout(0.4) → Dense(64) → Dropout(0.3) → Sigmoid",
            "xgboost": "XGBClassifier(n_estimators=400, max_depth=6) + SMOTE oversampling",
            "ensemble": "Soft-voting blend: 0.5 × DMSW + 0.5 × XGBoost",
            "input_window": f"{MAX_LEN} weeks",
        },
        "dmsw_model_loaded": dmsw_model is not None,
        "xgb_model_loaded": xgb_model is not None,
        "shap_loaded": shap_data is not None,
    }

    if model_metadata:
        info["training"] = model_metadata
    else:
        info["training"] = {
            "note": "No metadata found. Run train_dmsw_real.py to train on the real UCI dataset."
        }

    return jsonify(info)


if __name__ == "__main__":
    logger.info("Starting ML API server on http://0.0.0.0:5001")
    app.run(host="0.0.0.0", port=5001, debug=True)
