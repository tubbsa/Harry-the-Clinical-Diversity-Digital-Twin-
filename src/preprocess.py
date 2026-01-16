# ============================================================
# FILE: src/preprocess.py
# ============================================================
import pickle
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

MODEL_DIR = "model/"

with open(MODEL_DIR + "tfidf.pkl", "rb") as f:
    tfidf = pickle.load(f)

with open(MODEL_DIR + "encoder.pkl", "rb") as f:
    encoder = pickle.load(f)

def preprocess_payload(payload: dict):
    # Match training pipeline exactly from Harry 1.pdf
    df = pd.DataFrame([payload])

    # text concat
    df["merged_text"] = (
        df["inclusion_text"].fillna("") + " " +
        df["exclusion_text"].fillna("") + " " +
        df["Conditions"].fillna("") + " " +
        df["Interventions"].fillna("") + " " +
        df["Primary Outcome Measures"].fillna("") + " " +
        df["Secondary Outcome Measures"].fillna("")
    )

    X_text = tfidf.transform(df["merged_text"])

    cat_cols = ["eligibility_sex", "Sponsor", "Collaborators", "Phases",
                "Funder Type", "Study Type", "allocation",
                "intervention_model", "masking", "primary_purpose"]

    X_cat = encoder.transform(df[cat_cols])

    num_cols = ["eligibility_min_age", "eligibility_max_age"]
    X_num = df[num_cols].astype(float).fillna(-1).to_numpy()

    X = np.hstack([X_text.toarray(), X_cat, X_num])
    return X
