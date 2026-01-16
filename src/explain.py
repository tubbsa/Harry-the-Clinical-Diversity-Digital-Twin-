# ============================================================
# explain.py  —  SHAP explainability for your Digital Twin
# ============================================================
# Supports:
#  - Multi-output CatBoost Regressor
#  - TF-IDF text features
#  - Ordinal-encoded categoricals
#  - Numeric engineered features
# ============================================================

import numpy as np
import pandas as pd
import shap
import pickle
import catboost as cb
from catboost import Pool
from .preprocess import preprocess_payload


# ============================================================
# LOAD ARTIFACTS
# ============================================================

# Load trained CatBoost model
model = cb.CatBoostRegressor()
model.load_model("model/catboost.cbm")

# Load TF-IDF vectorizer
with open("model/tfidf.pkl", "rb") as f:
    tfidf = pickle.load(f)

# Load categorical encoder
with open("model/encoder.pkl", "rb") as f:
    encoder = pickle.load(f)


# ============================================================
# FEATURE NAMES (NUM + CAT + TEXT TOKEN NAMES)
# ============================================================

NUM_COLS = [
    "eligibility_min_age_yrs",
    "eligibility_max_age_yrs",
    "min_age_missing",
    "max_age_missing",
]

CAT_COLS = [
    "eligibility_sex",
    "Sponsor",
    "Collaborators",
    "Phases",
    "Funder Type",
    "Study Type",
    "allocation",
    "intervention_model",
    "masking",
    "primary_purpose",
]


def get_tfidf_feature_names():
    """Return TF-IDF token names."""
    return list(tfidf.get_feature_names_out())


def get_full_feature_names():
    """Return [NUM | CAT | TFIDF] names in correct order."""
    return NUM_COLS + CAT_COLS + get_tfidf_feature_names()


# ============================================================
# SHAP COMPUTATION
# ============================================================

def get_shap_values(payload: dict):
    """
    Compute SHAP values for a single payload.
    Returns:
        shap_values: ndarray of shape (n_features+1,)
                     Last element = expected value (bias term)
    """
    # Convert payload to model input
    X = preprocess_payload(payload)

    # Wrap in CatBoost Pool with placeholder feature names
    pool = Pool(
        X,
        feature_names=[f"f{i}" for i in range(X.shape[1])]
    )

    # CatBoost native SHAP values
    shap_vals = model.get_feature_importance(
        type="ShapValues",
        data=pool
    )

    # shap_vals shape = (1, n_features+1)
    return shap_vals[0]


# ============================================================
# HELPER: DataFrame of SHAP values per feature
# ============================================================

def get_shap_dataframe(payload: dict):
    """
    Returns SHAP values as a sorted pandas DataFrame.
    Columns:
        - feature
        - shap_value
        - abs_shap
    """
    shap_vals = get_shap_values(payload)
    feature_names = get_full_feature_names()

    # Drop final bias term
    shap_vals = shap_vals[:-1]

    df = pd.DataFrame({
        "feature": feature_names,
        "shap_value": shap_vals,
    })

    df["abs_shap"] = df["shap_value"].abs()

    return df.sort_values("abs_shap", ascending=False)


# ============================================================
# HELPER: Top contributing TF-IDF tokens
# ============================================================

def get_top_text_tokens(payload: dict, top_n=20):
    """
    Returns top contributing TF-IDF tokens (words & bigrams).
    """
    shap_vals = get_shap_values(payload)[:-1]
    total_features = len(shap_vals)

    # Index excluding numeric + categorical
    text_offset = len(NUM_COLS) + len(CAT_COLS)

    text_shap = shap_vals[text_offset:]
    tokens = get_tfidf_feature_names()

    # Rank by absolute contribution
    idx = np.argsort(np.abs(text_shap))[::-1][:top_n]

    results = []
    for i in idx:
        results.append({
            "token": tokens[i],
            "shap_value": text_shap[i],
            "abs_shap": abs(text_shap[i]),
        })

    return pd.DataFrame(results)


# ============================================================
# OPTIONAL: Waterfall Plot (returns Matplotlib figure)
# ============================================================

def waterfall_plot(payload: dict):
    """
    Generate a SHAP waterfall plot for a single sample.
    """
    shap_vals = get_shap_values(payload)
    feature_names = get_full_feature_names()

    shap_exp = shap.Explanation(
        values=shap_vals[:-1],
        base_values=shap_vals[-1],
        feature_names=feature_names
    )

    return shap.plots.waterfall(shap_exp, max_display=20, show=False)
