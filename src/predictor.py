# ============================================================
# predictor.py — Harry the Clinical Trial Diversity Digital Twin
# FINAL VERSION — MiniLM EMBEDDINGS + TABULAR + SOFT OOD
# ============================================================

import os
import numpy as np
import pickle
from typing import Dict, Any

from catboost import CatBoostRegressor
from sentence_transformers import SentenceTransformer

from src.schema import SCHEMA_VERSION, coerce_demo_keys


# ------------------------------------------------------------
# PATHS — MATCH YOUR digital_twin/model DIRECTORY
# ------------------------------------------------------------
BASE_DIR = "/Users/abigailtubbs/Downloads/digital_twin"
MODEL_DIR = os.path.join(BASE_DIR, "model")

MODEL_PATH         = os.path.join(MODEL_DIR, "cb_model_multituned.cbm")
ENCODER_PATH       = os.path.join(MODEL_DIR, "encoder.pkl")
CAT_COLS_PATH      = os.path.join(MODEL_DIR, "CAT_COLS.pkl")
NUM_COLS_PATH      = os.path.join(MODEL_DIR, "NUM_COLS.pkl")
TARGET_COLS_PATH   = os.path.join(MODEL_DIR, "TARGET_COLS.pkl")
FEATURE_NAMES_PATH = os.path.join(MODEL_DIR, "FEATURE_NAMES.pkl")

HURDLE_CLF_PATH    = os.path.join(MODEL_DIR, "hurdle_clf.pkl")
HURDLE_REG_PATH    = os.path.join(MODEL_DIR, "hurdle_reg.pkl")




# ------------------------------------------------------------
# LOAD MODELS & ARTIFACTS (ON IMPORT)
# ------------------------------------------------------------
model = CatBoostRegressor()
model.load_model(MODEL_PATH)

with open(ENCODER_PATH, "rb") as f:
    encoder = pickle.load(f)

with open(CAT_COLS_PATH, "rb") as f:
    CAT_COLS = pickle.load(f)

with open(NUM_COLS_PATH, "rb") as f:
    NUM_COLS = pickle.load(f)

with open(TARGET_COLS_PATH, "rb") as f:
    TARGET_COLS = pickle.load(f)

with open(FEATURE_NAMES_PATH, "rb") as f:
    FEATURE_NAMES = pickle.load(f)

with open(HURDLE_CLF_PATH, "rb") as f:
    hurdle_clf = pickle.load(f)

with open(HURDLE_REG_PATH, "rb") as f:
    hurdle_reg = pickle.load(f)


# ------------------------------------------------------------
# LOAD OOD ARTIFACTS (RESTRICTED FEATURE SPACE)
# ------------------------------------------------------------
OOD_MEAN = np.load(os.path.join(MODEL_DIR, "ood_mean.npy"))
OOD_STD  = np.load(os.path.join(MODEL_DIR, "ood_std.npy"))
OOD_COLS = np.load(
    os.path.join(MODEL_DIR, "ood_cols.npy"),
    allow_pickle=True
).tolist()


print("DEBUG predictor OOD_MEAN shape:", OOD_MEAN.shape)
print("DEBUG predictor OOD_STD shape:", OOD_STD.shape)
print("DEBUG predictor OOD_COLS:", OOD_COLS)


# ------------------------------------------------------------
# TEXT EMBEDDER (REPLACES TF-IDF)
# ------------------------------------------------------------
embedder = SentenceTransformer("all-MiniLM-L6-v2")


# ============================================================
# HELPERS
# ============================================================

def build_text_embedding(payload: Dict[str, Any]) -> np.ndarray:
    """Build 384-dim MiniLM embedding from trial text fields."""
    text_fields = [
        payload.get("inclusion_text", ""),
        payload.get("exclusion_text", ""),
        payload.get("conditions_text", ""),
        payload.get("interventions_text", ""),
        payload.get("primary_outcome_text", ""),
        payload.get("secondary_outcome_text", ""),
    ]
    joined = " ".join(t for t in text_fields if isinstance(t, str))
    return embedder.encode(joined).reshape(1, -1)


def check_ood(x_vec: np.ndarray):
    """
    Restricted diagonal OOD check using stable metadata features only.
    x_vec must already be in FINAL feature space order.
    """

    # Map restricted OOD columns into FINAL feature space
    col_idx = [FEATURE_NAMES.index(c) for c in OOD_COLS]

    x_restricted = x_vec[:, col_idx]

    # Diagonal z-score
    z_vec = np.abs((x_restricted - OOD_MEAN) / OOD_STD)
    z_max = float(np.max(z_vec))

    is_ood = bool(z_max > 3.5)  # conservative, interpretable threshold

    return is_ood, z_max




# ============================================================
# MAIN ENTRYPOINT
# ============================================================

def predict_proportions(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predict demographic proportions for a proposed clinical trial.
    """

    # -----------------------
    # 1. TEXT → EMBEDDING
    # -----------------------
    X_text = build_text_embedding(payload)

    # -----------------------
    # 2. CATEGORICAL FEATURES
    # -----------------------
    cat_vals = [[payload.get(c, "Unknown") for c in CAT_COLS]]
    X_cat = encoder.transform(cat_vals)

    # -----------------------
    # 3. NUMERIC FEATURES (incl. geography)
    # -----------------------
    X_num = np.array([[payload.get(c, 0) for c in NUM_COLS]])

    # -----------------------
    # 4. FINAL FEATURE VECTOR
    # -----------------------
    X = np.hstack([X_text, X_cat, X_num])

    # -----------------------
    # 5. OOD CHECK (FINAL FEATURE SPACE ONLY)
    # -----------------------
    is_ood, z_score = check_ood(X)



    # -----------------------
    # 6. BASE MODEL PREDICTION
    # -----------------------
    raw_preds = model.predict(X).flatten()
    preds = dict(zip(TARGET_COLS, raw_preds))

    # -----------------------
    # 7. HURDLE MODELS (RARE TARGETS)
    # -----------------------
    for label, clf in hurdle_clf.items():
        present = clf.predict(X)[0]
        if present == 0:
            preds[label] = 0.0
        else:
            preds[label] = float(hurdle_reg[label].predict(X)[0])

    # --------------------------------------------------------
    # Canonicalize keys for UI / scoring
    # --------------------------------------------------------
    preds_frac = coerce_demo_keys(preds)
    for k in ["aian_pct", "age65_pct"]:
        preds_frac.setdefault(k, preds.get(k, 0.0))

    return {
        "unreliable_projection": bool(is_ood),
        "ood_score": float(z_score),
        "preds": preds_frac,
        "_schema": SCHEMA_VERSION,
    }
