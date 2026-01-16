# ============================================================
# rebuild_artifacts.py (FINAL VERSION — GUARANTEED TO WORK)
# ============================================================

import pandas as pd
import numpy as np
import re
import os
import scipy.sparse as sp
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OrdinalEncoder
from sklearn.model_selection import train_test_split
from catboost import CatBoostRegressor, Pool
import pickle

# ---------------------------------------
# LOAD YOUR TRAINING DATASET
# ---------------------------------------
DATA_PATH = "/Users/abigailtubbs/Desktop/Fall 2025/Dissertation F25/Harry/AssigneddiversitytofeaturesCLEANEDFORTRAINING.xlsx"
df = pd.read_excel(DATA_PATH, engine="openpyxl")

print("Loaded Excel:", df.shape)

# ---------------------------------------
# CLEANING HELPER FUNCTIONS
# ---------------------------------------
def normalize_missing(x):
    if pd.isna(x): return np.nan
    s = str(x).strip().lower()
    if s in ["", "na", "n/a", "none", "not provided"]:
        return np.nan
    return x

def parse_age_to_years(x):
    if pd.isna(x): return np.nan
    s = str(x).lower()
    m = re.match(r"(\d+)[^\d]*(year|month|week|day)", s)
    if not m: return np.nan
    v = float(m.group(1))
    u = m.group(2)
    if u.startswith("year"): return v
    if u.startswith("month"): return v/12
    if u.startswith("week"): return v/52
    if u.startswith("day"): return v/365
    return np.nan

def parse_study_design(s):
    if pd.isna(s): s=""
    t = str(s).lower()

    # Allocation
    if "random" in t: A="Randomized"
    elif "non-random" in t: A="Non-Randomized"
    else: A="Unknown"

    # Intervention
    if "parallel" in t: M="Parallel"
    elif "crossover" in t: M="Crossover"
    elif "single group" in t: M="Single Group"
    else: M="Unknown"

    # Masking
    if "quadruple" in t: K="Quadruple"
    elif "triple" in t: K="Triple"
    elif "double" in t: K="Double"
    elif "single" in t: K="Single"
    else: K="Unknown"

    # Primary Purpose
    PURPOSES=["treatment","prevention","diagnostic","screening","supportive","basic","health"]
    P="Unknown"
    for pp in PURPOSES:
        if pp in t:
            P=pp.title()
            break
    return A, M, K, P

def map_sex(s):
    s=str(s).lower()
    if "all" in s: return "All"
    if "female" in s and "male" not in s: return "Female"
    if "male" in s and "female" not in s: return "Male"
    return "Unknown"

# ---------------------------------------
# APPLY CLEANING LOGIC
# ---------------------------------------
df = df.applymap(normalize_missing)

df["eligibility_min_age_yrs"] = df["eligibility_min_age"].apply(parse_age_to_years)
df["eligibility_max_age_yrs"] = df["eligibility_max_age"].apply(parse_age_to_years)

df["min_age_missing"] = df["eligibility_min_age_yrs"].isna().astype(int)
df["max_age_missing"] = df["eligibility_max_age_yrs"].isna().astype(int)

df["eligibility_min_age_yrs"].fillna(df["eligibility_min_age_yrs"].median(), inplace=True)
df["eligibility_max_age_yrs"].fillna(df["eligibility_max_age_yrs"].median(), inplace=True)

alloc=[]; inter=[]; mask=[]; prim=[]
for s in df["Study Design"]:
    a, i, m, p = parse_study_design(s)
    alloc.append(a)
    inter.append(i)
    mask.append(m)
    prim.append(p)

df["allocation"] = alloc
df["intervention_model"] = inter
df["masking"] = mask
df["primary_purpose"] = prim
df["eligibility_sex"] = df["eligibility_sex"].apply(map_sex)

# ---------------------------------------
# TARGET COLUMNS
# ---------------------------------------
TARGET_COLS = [
 "white_pct","black_pct","asian_pct","aian_pct","nhpi_pct",
 "male_pct","female_pct","age65_pct"
]

df = df.dropna(subset=TARGET_COLS)

# ---------------------------------------
# TEXT FEATURES
# ---------------------------------------
df["merged_text"] = (
    df["exclusion_text"].fillna("") + " " +
    df["inclusion_text"].fillna("") + " " +
    df["Conditions"].fillna("") + " " +
    df["Interventions"].fillna("") + " " +
    df["Primary Outcome Measures"].fillna("") + " " +
    df["Secondary Outcome Measures"].fillna("")
)

tfidf = TfidfVectorizer(max_features=3000, ngram_range=(1,2), stop_words="english")
X_text = tfidf.fit_transform(df["merged_text"])

# ---------------------------------------
# CATEGORICAL FEATURES
# ---------------------------------------
CAT_COLS = [
 "eligibility_sex","Sponsor","Collaborators","Phases","Funder Type",
 "Study Type","allocation","intervention_model","masking","primary_purpose"
]

encoder = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
X_cat = encoder.fit_transform(df[CAT_COLS])

# ---------------------------------------
# NUMERIC FEATURES
# ---------------------------------------
NUM_COLS = [
 "eligibility_min_age_yrs","eligibility_max_age_yrs",
 "min_age_missing","max_age_missing"
]

X_num = df[NUM_COLS].values

# ---------------------------------------
# FINAL MATRIX
# ---------------------------------------
X_final = sp.hstack([X_num, X_cat, X_text], format="csr")
y = df[TARGET_COLS].values

# ---------------------------------------
# TRAIN CATBOOST
# ---------------------------------------
X_train, X_val, y_train, y_val = train_test_split(
    X_final, y, test_size=0.20, random_state=42
)

model = CatBoostRegressor(
    iterations=400,
    depth=6,
    learning_rate=0.05,
    loss_function="MultiRMSE",
    random_seed=42,
    verbose=50
)

model.fit(Pool(X_train, y_train), eval_set=(X_val, y_val))

# ---------------------------------------
# SAVE ARTIFACTS
# ---------------------------------------
os.makedirs("model", exist_ok=True)

with open("model/tfidf.pkl", "wb") as f:
    pickle.dump(tfidf, f)

with open("model/encoder.pkl", "wb") as f:
    pickle.dump(encoder, f)

model.save_model("model/catboost.cbm")

print("DONE — created model artifacts:")
print(os.listdir("model"))
