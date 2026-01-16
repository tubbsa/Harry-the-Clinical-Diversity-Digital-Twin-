# ------------------------------------------------------------
# PATHS — DEPLOYMENT-SAFE (relative to repo root)
# ------------------------------------------------------------
import os
import pickle
from pathlib import Path
from typing import Any, Dict

import numpy as np
from catboost import CatBoostRegressor
from sentence_transformers import SentenceTransformer

# Allow both package import (src.predictor) and direct local import
try:
    from .schema import SCHEMA_VERSION, coerce_demo_keys
except ImportError:  # pragma: no cover
    from schema import SCHEMA_VERSION, coerce_demo_keys


# src/predictor.py → repo root = parents[1]
REPO_ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = REPO_ROOT / "model"

MODEL_PATH         = MODEL_DIR / "cb_model_multituned.cbm"
ENCODER_PATH       = MODEL_DIR / "encoder.pkl"
CAT_COLS_PATH      = MODEL_DIR / "CAT_COLS.pkl"
NUM_COLS_PATH      = MODEL_DIR / "NUM_COLS.pkl"
TARGET_COLS_PATH   = MODEL_DIR / "TARGET_COLS.pkl"
FEATURE_NAMES_PATH = MODEL_DIR / "FEATURE_NAMES.pkl"

HURDLE_CLF_PATH    = MODEL_DIR / "hurdle_clf.pkl"
HURDLE_REG_PATH    = MODEL_DIR / "hurdle_reg.pkl"


# ------------------------------------------------------------
# LOAD MODELS & ARTIFACTS (ON IMPORT)
# ------------------------------------------------------------
def _require_file(path: Path, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing required artifact '{label}' at: {path}. "
            "Ensure model artifacts are committed to the repository."
        )
    if path.is_file() and path.stat().st_size < 16:
        raise RuntimeError(
            f"Artifact '{label}' looks too small/corrupt: {path} ({path.stat().st_size} bytes)"
        )


# Helpful in Streamlit Cloud logs
print(f"[predictor] CWD={os.getcwd()}")
print(f"[predictor] REPO_ROOT={REPO_ROOT}")
print(f"[predictor] MODEL_DIR={MODEL_DIR}")

_require_file(MODEL_PATH, "cb_model_multituned.cbm")
print(f"[predictor] MODEL_PATH={MODEL_PATH} (bytes={MODEL_PATH.stat().st_size})")

model = CatBoostRegressor()
model.load_model(str(MODEL_PATH))  # IMPORTANT: CatBoost expects a string path reliably


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
