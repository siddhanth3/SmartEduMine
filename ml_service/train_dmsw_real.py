"""
train_dmsw_real.py — SmartEduMine Real-Data Training Script
============================================================
Trains the DMSW (Dual-Modal Multiscale Sliding Window) model on the REAL
UCI Student Dropout dataset (`data.csv`), producing a strongly performing
ensemble of:
  1. An upgraded DMSW neural network (CNN + BiLSTM + Attention)
  2. An XGBoost classifier (tabular path)

Both models are blended via soft-voting for the final prediction.
SHAP values are computed on the XGBoost model for interpretability.

Outputs (all written to the ml_service/ directory):
  - dmsw_model.h5       — updated DMSW Keras model
  - xgb_model.pkl       — XGBoost model
  - shap_values.pkl     — SHAP explanation values (test set)
  - dmsw_scaler.pkl     — feature scaler
  - dmsw_tokenizer.pkl  — behavior tokenizer
  - model_metadata.json — full training report

Usage:
  python train_dmsw_real.py
"""

import json
import os
import pickle
import warnings
from datetime import datetime

import numpy as np
import pandas as pd
import shap
import tensorflow as tf
from imblearn.over_sampling import SMOTE
from sklearn.metrics import (
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.utils.class_weight import compute_class_weight
from tensorflow.keras.layers import (
    Bidirectional,
    Concatenate,
    Conv1D,
    Dense,
    Dropout,
    Embedding,
    GlobalMaxPooling1D,
    Input,
    LSTM,
    LayerNormalization,
    MultiHeadAttention,
    Reshape,
)
from tensorflow.keras.models import Model
from tensorflow.keras.regularizers import l2
from xgboost import XGBClassifier

warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
tf.get_logger().setLevel("ERROR")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REAL_DATA_FILE = os.path.join(BASE_DIR, "data.csv")
MODEL_FILE = os.path.join(BASE_DIR, "dmsw_model.h5")
TOKENIZER_FILE = os.path.join(BASE_DIR, "dmsw_tokenizer.pkl")
SCALER_FILE = os.path.join(BASE_DIR, "dmsw_scaler.pkl")
XGB_MODEL_FILE = os.path.join(BASE_DIR, "xgb_model.pkl")
SHAP_FILE = os.path.join(BASE_DIR, "shap_values.pkl")
METADATA_FILE = os.path.join(BASE_DIR, "model_metadata.json")

# ---------------------------------------------------------------------------
# Hyperparameters
# ---------------------------------------------------------------------------
MAX_LEN = 15          # Temporal window length
EMBEDDING_DIM = 64
VOCAB_SIZE = 500
EPOCHS = 50
BATCH_SIZE = 32
PATIENCE = 8
RANDOM_STATE = 42

# Behavior text buckets derived from academic performance
BEHAVIOR_TEXTS = {
    "excellent": "Active participation in class consistent high performance",
    "good":      "Regular attendance submitted assignment on time",
    "neutral":   "Average performance met basic requirements",
    "poor":      "Missed deadlines struggling with concepts absent repeatedly",
    "critical":  "Absent without leave failed quiz incomplete homework no submission",
}

# ---------------------------------------------------------------------------
# Feature engineering
# ---------------------------------------------------------------------------

def load_and_engineer(path: str):
    """Load UCI data (semicolon-separated), engineer features, return df."""
    print(f"[1/6] Loading real UCI dataset from {path} ...")
    df = pd.read_csv(path, sep=";")
    print(f"      Loaded {len(df)} rows, {df.shape[1]} columns")

    # --- Target: binary (Dropout=1, Graduate/Enrolled=0) ---
    df["dropout_label"] = (df["Target"] == "Dropout").astype(int)

    # --- Rename key columns for clarity ---
    rename_map = {
        "Tuition fees up to date": "tuition_up_to_date",
        "Scholarship holder": "scholarship",
        "Debtor": "debtor",
        "Gender": "gender",
        "Age at enrollment": "age",
        "Admission grade": "admission_grade",
        "Previous qualification (grade)": "prev_qual_grade",
        "Curricular units 1st sem (approved)": "approved_1st",
        "Curricular units 1st sem (enrolled)": "enrolled_1st",
        "Curricular units 1st sem (grade)": "grade_1st",
        "Curricular units 2nd sem (approved)": "approved_2nd",
        "Curricular units 2nd sem (enrolled)": "enrolled_2nd",
        "Curricular units 2nd sem (grade)": "grade_2nd",
        "Curricular units 1st sem (evaluations)": "evals_1st",
        "Curricular units 2nd sem (evaluations)": "evals_2nd",
        "Unemployment rate": "unemployment_rate",
        "GDP": "gdp",
        "Displaced": "displaced",
        "Educational special needs": "special_needs",
        "International": "international",
        "Marital status": "marital_status",
        "Application mode": "application_mode",
        "Course": "course",
    }
    df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

    # --- Derived features ---
    df["pass_rate_1st"] = df["approved_1st"] / (df["enrolled_1st"].replace(0, 1))
    df["pass_rate_2nd"] = df["approved_2nd"] / (df["enrolled_2nd"].replace(0, 1))
    df["pass_rate_change"] = df["pass_rate_2nd"] - df["pass_rate_1st"]   # trend
    df["grade_change"]     = df["grade_2nd"] - df["grade_1st"]            # academic trajectory
    df["total_approved"]   = df["approved_1st"] + df["approved_2nd"]
    df["total_enrolled"]   = df["enrolled_1st"] + df["enrolled_2nd"]
    df["overall_pass_rate"] = df["total_approved"] / (df["total_enrolled"].replace(0, 1))
    df["avg_grade"]        = (df["grade_1st"] + df["grade_2nd"]) / 2
    df["grade_admission_gap"] = df["avg_grade"] - df["admission_grade"]

    # Socioeconomic composite risk score
    df["socio_risk"] = (
        (1 - df["tuition_up_to_date"]) * 0.4
        + df["debtor"] * 0.3
        + (1 - df["scholarship"]) * 0.15
        + df["unemployment_rate"] / 20 * 0.15
    ).clip(0, 1)

    # Attendance proxy: evaluation ratio (students who needed evaluations vs. enrolled)
    df["eval_ratio_1st"] = df["evals_1st"] / (df["enrolled_1st"].replace(0, 1))
    df["eval_ratio_2nd"] = df["evals_2nd"] / (df["enrolled_2nd"].replace(0, 1))

    print(f"      Dropout rate: {df['dropout_label'].mean()*100:.1f}%")
    return df


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


def _behavior_from_row(row) -> str:
    """Map a row's academic profile to a behavior text bucket."""
    g = row.get("avg_grade", 0)
    p = row.get("overall_pass_rate", 0)
    s = row.get("socio_risk", 0)

    if g >= 14 and p >= 0.9:
        return BEHAVIOR_TEXTS["excellent"]
    elif g >= 11 and p >= 0.7:
        return BEHAVIOR_TEXTS["good"]
    elif g >= 8 and p >= 0.5:
        return BEHAVIOR_TEXTS["neutral"]
    elif g >= 5 or p >= 0.2:
        return BEHAVIOR_TEXTS["poor"]
    else:
        return BEHAVIOR_TEXTS["critical"]


def build_dmsw_inputs(df: pd.DataFrame, scaler=None, tokenizer=None):
    """
    Construct the three-branch inputs for the DMSW model:
      X_num   : (N, MAX_LEN, 2)  — scaled [grade, pass_rate] repeated as time steps
      X_text  : (N, MAX_LEN)     — tokenized behavior repeated as time steps
      X_static: (N, n_static)    — full tabular feature vector
    Returns (X_num, X_text, X_static), fitted_scaler, fitted_tokenizer
    """
    from tensorflow.keras.preprocessing.text import Tokenizer

    n = len(df)
    df = df.reset_index(drop=True)

    # --- Build behavior texts ---
    behavior_texts = [_behavior_from_row(df.iloc[i]) for i in range(n)]

    # --- Tokenizer ---
    if tokenizer is None:
        tokenizer = Tokenizer(num_words=VOCAB_SIZE, oov_token="<OOV>")
        tokenizer.fit_on_texts(behavior_texts)

    seqs = tokenizer.texts_to_sequences(behavior_texts)
    # Take first three tokens to carry richer signal
    def seq_to_window(s):
        tokens = s[:3] if len(s) >= 3 else s + [0] * (3 - len(s))
        # Tile to MAX_LEN with slight variation to avoid pure repetition
        window = []
        for i in range(MAX_LEN):
            window.append(tokens[i % len(tokens)])
        return window

    X_text = np.array([seq_to_window(s) for s in seqs])  # (N, MAX_LEN)

    # --- Numerical time series: [avg_grade (normalised 0-20 → 0-100), pass_rate*100] ---
    grades     = df["avg_grade"].fillna(0).values          # 0-20 scale
    pass_rates = df["overall_pass_rate"].fillna(0).values  # 0-1
    grade_change = df["grade_change"].fillna(0).values     # -20 to +20

    # Build per-student 15-step sequence that simulates a trend
    # Step i is the static point with a small linear extrapolation of past trend
    X_num = np.zeros((n, MAX_LEN, 2), dtype=np.float32)
    for idx in range(n):
        g_base  = grades[idx]
        p_base  = pass_rates[idx]
        g_delta = grade_change[idx] / MAX_LEN      # distribute change evenly
        for t in range(MAX_LEN):
            # reverse time: earliest timestep has earlier estimated grade
            g_t = g_base - g_delta * (MAX_LEN - 1 - t)
            p_t = p_base * (0.85 + 0.15 * t / MAX_LEN)  # slight ramp
            X_num[idx, t, 0] = float(np.clip(g_t, 0, 20))
            X_num[idx, t, 1] = float(np.clip(p_t, 0, 1))

    # --- Scale numerical inputs ---
    num_samples, num_timesteps, num_features = X_num.shape
    X_num_flat = X_num.reshape(-1, num_features)
    if scaler is None:
        scaler = StandardScaler()
        X_num_scaled = scaler.fit_transform(X_num_flat)
    else:
        X_num_scaled = scaler.transform(X_num_flat)
    X_num = X_num_scaled.reshape(num_samples, num_timesteps, num_features)

    # --- Static features ---
    available = [f for f in TABULAR_FEATURES if f in df.columns]
    X_static = df[available].fillna(0).values.astype(np.float32)

    return (X_num, X_text, X_static), scaler, tokenizer, len(available)


# ---------------------------------------------------------------------------
# Model architectures
# ---------------------------------------------------------------------------

def build_upgraded_dmsw(vocab_size: int, num_static: int) -> Model:
    """
    Upgraded DMSW model:
      Branch 1 (Numerical) : Conv1D(k=3) + Conv1D(k=5) + BiLSTM + Self-Attention
      Branch 2 (Text)      : Embedding + Conv1D(k=3) + Conv1D(k=5)
      Branch 3 (Static)    : Dense(32) → Dense(16)
      Fusion               : Concat → Dense(128) → Dropout → Dense(64) → Sigmoid
    """
    # -- Branch 1: Numerical multiscale + temporal --
    input_num = Input(shape=(MAX_LEN, 2), name="numerical_input")

    # Multiscale convolutions
    conv_num_s = Conv1D(64, kernel_size=3, activation="relu", padding="same",
                        kernel_regularizer=l2(1e-4))(input_num)
    pool_num_s = GlobalMaxPooling1D()(conv_num_s)

    conv_num_l = Conv1D(64, kernel_size=5, activation="relu", padding="same",
                        kernel_regularizer=l2(1e-4))(input_num)
    pool_num_l = GlobalMaxPooling1D()(conv_num_l)

    # Bidirectional LSTM for temporal patterns
    bilstm_out = Bidirectional(LSTM(32, return_sequences=True))(input_num)

    # Self-attention on the LSTM output
    attn_out = MultiHeadAttention(num_heads=2, key_dim=16)(bilstm_out, bilstm_out)
    attn_norm = LayerNormalization()(attn_out)
    pool_attn = GlobalMaxPooling1D()(attn_norm)

    # -- Branch 2: Textual dual-modal --
    input_text = Input(shape=(MAX_LEN,), name="text_input")
    embedding  = Embedding(input_dim=vocab_size, output_dim=EMBEDDING_DIM)(input_text)

    conv_txt_s = Conv1D(64, kernel_size=3, activation="relu", padding="same")(embedding)
    pool_txt_s = GlobalMaxPooling1D()(conv_txt_s)

    conv_txt_l = Conv1D(64, kernel_size=5, activation="relu", padding="same")(embedding)
    pool_txt_l = GlobalMaxPooling1D()(conv_txt_l)

    # -- Branch 3: Static features --
    input_static = Input(shape=(num_static,), name="static_input")
    dense_s1 = Dense(32, activation="relu", kernel_regularizer=l2(1e-4))(input_static)
    dense_s2 = Dense(16, activation="relu")(dense_s1)

    # -- Fusion --
    merged  = Concatenate()([pool_num_s, pool_num_l, pool_attn, pool_txt_s, pool_txt_l, dense_s2])
    dense1  = Dense(128, activation="relu", kernel_regularizer=l2(1e-4))(merged)
    drop1   = Dropout(0.4)(dense1)
    dense2  = Dense(64, activation="relu")(drop1)
    drop2   = Dropout(0.3)(dense2)
    output  = Dense(1, activation="sigmoid")(drop2)

    model = Model(inputs=[input_num, input_text, input_static], outputs=output)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="binary_crossentropy",
        metrics=["accuracy", tf.keras.metrics.AUC(name="auc")],
    )
    return model


# ---------------------------------------------------------------------------
# Training pipeline
# ---------------------------------------------------------------------------

def train():
    print("=" * 60)
    print("   SmartEduMine — Real-Data DMSW Training")
    print("=" * 60)

    # 1. Load + engineer
    df = load_and_engineer(REAL_DATA_FILE)
    y  = df["dropout_label"].values

    # 2. Build DMSW inputs
    print("[2/6] Building DMSW inputs ...")
    (X_num, X_text, X_static), scaler, tokenizer, num_static = build_dmsw_inputs(df)
    print(f"      X_num={X_num.shape}, X_text={X_text.shape}, X_static={X_static.shape}")

    # Save artifacts
    with open(SCALER_FILE, "wb") as f:
        pickle.dump(scaler, f)
    with open(TOKENIZER_FILE, "wb") as f:
        pickle.dump(tokenizer, f)
    print(f"      Scaler → {SCALER_FILE}")
    print(f"      Tokenizer → {TOKENIZER_FILE}")

    # 3. Train/test split (stratified)
    indices = np.arange(len(y))
    tr_idx, te_idx, y_tr, y_te = train_test_split(
        indices, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )
    X_tr = [x[tr_idx] for x in [X_num, X_text, X_static]]
    X_te = [x[te_idx] for x in [X_num, X_text, X_static]]

    print(f"[3/6] Split: train={len(y_tr)}, test={len(y_te)}")
    print(f"      Train dropout rate: {y_tr.mean()*100:.1f}%")

    # Class weights
    cls_w_arr = compute_class_weight("balanced", classes=np.unique(y_tr), y=y_tr)
    cls_w = {int(c): w for c, w in zip(np.unique(y_tr), cls_w_arr)}
    print(f"      Class weights: {cls_w}")

    # 4. Build and train DMSW neural net
    print("[4/6] Training upgraded DMSW neural network ...")
    model = build_upgraded_dmsw(VOCAB_SIZE, num_static)
    model.summary(print_fn=lambda x: None)  # suppress verbose summary

    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_auc", patience=PATIENCE, restore_best_weights=True,
            mode="max", verbose=1,
        ),
        tf.keras.callbacks.ModelCheckpoint(
            MODEL_FILE, monitor="val_auc", save_best_only=True, mode="max", verbose=0,
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=4, min_lr=1e-5, verbose=1,
        ),
    ]

    history = model.fit(
        X_tr, y_tr,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        validation_data=(X_te, y_te),
        class_weight=cls_w,
        callbacks=callbacks,
        verbose=1,
    )

    # Evaluation
    y_prob_dmsw = model.predict(X_te, verbose=0).flatten()
    y_pred_dmsw = (y_prob_dmsw >= 0.5).astype(int)

    acc_dmsw  = float((y_pred_dmsw == y_te).mean())
    auc_dmsw  = float(roc_auc_score(y_te, y_prob_dmsw))
    f1_dmsw   = float(f1_score(y_te, y_pred_dmsw, zero_division=0))
    prec_dmsw = float(precision_score(y_te, y_pred_dmsw, zero_division=0))
    rec_dmsw  = float(recall_score(y_te, y_pred_dmsw, zero_division=0))
    cm_dmsw   = confusion_matrix(y_te, y_pred_dmsw).tolist()

    print(f"\n  [DMSW]  Accuracy={acc_dmsw*100:.2f}%  AUC={auc_dmsw:.4f}  F1={f1_dmsw:.4f}")

    # 5. XGBoost on tabular features (with SMOTE to handle class imbalance)
    print("[5/6] Training XGBoost classifier ...")
    X_tab = X_static[tr_idx]
    X_tab_te = X_static[te_idx]

    smote = SMOTE(random_state=RANDOM_STATE)
    X_tab_bal, y_tr_bal = smote.fit_resample(X_tab, y_tr)
    print(f"      SMOTE resampled: {len(y_tr_bal)} samples")

    xgb = XGBClassifier(
        n_estimators=400,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=3,
        gamma=0.1,
        reg_alpha=0.1,
        reg_lambda=1.0,
        eval_metric="auc",
        early_stopping_rounds=20,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        verbosity=0,
    )
    xgb.fit(
        X_tab_bal, y_tr_bal,
        eval_set=[(X_tab_te, y_te)],
        verbose=False,
    )

    y_prob_xgb = xgb.predict_proba(X_tab_te)[:, 1]
    y_pred_xgb = (y_prob_xgb >= 0.5).astype(int)
    auc_xgb    = float(roc_auc_score(y_te, y_prob_xgb))
    f1_xgb     = float(f1_score(y_te, y_pred_xgb, zero_division=0))
    print(f"  [XGB]   AUC={auc_xgb:.4f}  F1={f1_xgb:.4f}")

    with open(XGB_MODEL_FILE, "wb") as f:
        pickle.dump(xgb, f)
    print(f"      XGBoost → {XGB_MODEL_FILE}")

    # SHAP values
    print("      Computing SHAP values ...")
    explainer   = shap.TreeExplainer(xgb)
    shap_values = explainer.shap_values(X_tab_te)
    with open(SHAP_FILE, "wb") as f:
        pickle.dump({
            "values": shap_values,
            "feature_names": [f for f in TABULAR_FEATURES if f in df.columns],
            "expected_value": float(explainer.expected_value),
        }, f)
    print(f"      SHAP → {SHAP_FILE}")

    # Feature importance from SHAP (mean |SHAP|)
    available_features = [f for f in TABULAR_FEATURES if f in df.columns]
    shap_importance = {}
    if isinstance(shap_values, list):
        sv = shap_values[1]
    else:
        sv = shap_values
    mean_abs_shap = np.abs(sv).mean(axis=0)
    total = mean_abs_shap.sum()
    for feat, imp in zip(available_features, mean_abs_shap):
        shap_importance[feat] = round(float(imp / total), 4)
    shap_importance = dict(sorted(shap_importance.items(), key=lambda x: -x[1]))

    # 6. Ensemble evaluation (soft voting: 50% DMSW + 50% XGBoost)
    print("[6/6] Evaluating ensemble ...")
    y_prob_ens = 0.5 * y_prob_dmsw + 0.5 * y_prob_xgb
    y_pred_ens = (y_prob_ens >= 0.5).astype(int)

    acc_ens  = float((y_pred_ens == y_te).mean())
    auc_ens  = float(roc_auc_score(y_te, y_prob_ens))
    f1_ens   = float(f1_score(y_te, y_pred_ens, zero_division=0))
    prec_ens = float(precision_score(y_te, y_pred_ens, zero_division=0))
    rec_ens  = float(recall_score(y_te, y_pred_ens, zero_division=0))
    cm_ens   = confusion_matrix(y_te, y_pred_ens).tolist()

    tn, fp, fn, tp = confusion_matrix(y_te, y_pred_ens).ravel()

    print(f"\n{'='*60}")
    print(f"  ENSEMBLE RESULTS")
    print(f"{'='*60}")
    print(f"  Accuracy  : {acc_ens*100:.2f}%")
    print(f"  AUC-ROC   : {auc_ens:.4f}")
    print(f"  F1-Score  : {f1_ens:.4f}")
    print(f"  Precision : {prec_ens:.4f}")
    print(f"  Recall    : {rec_ens:.4f}")
    print(f"  Confusion Matrix: TP={tp} FP={fp} FN={fn} TN={tn}")
    print(f"{'='*60}")

    # Top-10 important features
    top_features = list(shap_importance.items())[:10]
    print("\n  Top-10 Feature Importances (SHAP):")
    for feat, imp in top_features:
        bar = "█" * int(imp * 200)
        print(f"    {feat:<35} {imp:.4f}  {bar}")

    # Save metadata
    metadata = {
        "trained_at": datetime.utcnow().isoformat() + "Z",
        "training_mode": "real_data_UCI",
        "dataset_file": os.path.basename(REAL_DATA_FILE),
        "total_samples": len(y),
        "train_samples": len(y_tr),
        "test_samples": len(y_te),
        "dropout_ratio": f"{y.mean()*100:.1f}%",
        "epochs_completed": len(history.history["loss"]),
        "max_epochs": EPOCHS,
        "early_stopping_patience": PATIENCE,
        "smote_applied": True,

        # DMSW deep model
        "dmsw": {
            "accuracy": round(acc_dmsw, 4),
            "auc_roc": round(auc_dmsw, 4),
            "f1_score": round(f1_dmsw, 4),
            "precision": round(prec_dmsw, 4),
            "recall": round(rec_dmsw, 4),
            "confusion_matrix": cm_dmsw,
        },

        # XGBoost
        "xgboost": {
            "auc_roc": round(auc_xgb, 4),
            "f1_score": round(f1_xgb, 4),
            "n_estimators": xgb.n_estimators,
        },

        # Ensemble (primary result)
        "accuracy": round(acc_ens, 4),
        "auc_roc": round(auc_ens, 4),
        "f1_score": round(f1_ens, 4),
        "precision": round(prec_ens, 4),
        "recall": round(rec_ens, 4),
        "confusion_matrix": {"TP": int(tp), "FP": int(fp), "FN": int(fn), "TN": int(tn)},
        "class_weights": {str(k): round(v, 4) for k, v in cls_w.items()},

        # Feature importance (SHAP)
        "shap_feature_importance": shap_importance,
    }

    with open(METADATA_FILE, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"\n  Metadata → {METADATA_FILE}")
    print(f"  DMSW model → {MODEL_FILE}")
    print("\n  Training complete! ✅")


if __name__ == "__main__":
    train()
