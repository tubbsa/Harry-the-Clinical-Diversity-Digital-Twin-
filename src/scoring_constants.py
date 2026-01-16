# ============================================================
# scoring_constants.py — Final ICER Scoring Constants
# ============================================================

# ---------------------------
# DISEASE PREVALENCE (0–1)
# ---------------------------
# These values MUST match the inputs used in charts and scoring.
DISEASE_PREVALENCE = {
    "white_pct": 0.090,   # ~9.0% of White adults have CVD
    "black_pct": 0.116,   # ~11.6% of Black adults have CVD
    "asian_pct": 0.043,   # ~4.3% of Asian adults have CVD
    "aian_pct":  0.099,   # ~9.9% of AI/AN adults have CVD

    "female_pct": 0.058,  # ~5.8% of women have CVD
    "male_pct":   0.078,  # ~7.8% of men have CVD

    "age65_pct":  0.240,  # ~24% of adults ≥65 have CVD
}

# ---------------------------
# ALTERNATIVE SEX BURDEN (CVD MORTALITY SHARE)
# ---------------------------
# Defined as the sex distribution of cardiovascular disease deaths.
#
# Source:
# Mosca et al., Circulation. 2011;123:1243–1262.
# Women represent 52.6% of CVD deaths in the United States.
# https://pmc.ncbi.nlm.nih.gov/articles/PMC4039306/
#
# This captures outcome severity and diagnostic/treatment disparities
# not reflected in prevalence alone.
SEX_BURDEN_MORTALITY = {
    "female_pct": 0.526,
    "male_pct":   0.474,
}


# ---------------------------
# GROUP DEFINITIONS
# ---------------------------
# RACE DOMAIN — 4 groups only (ICER core without Hispanic)
RACE_GROUPS = [
    "white_pct",
    "black_pct",
    "asian_pct",
    "aian_pct",
]

# SEX DOMAIN
SEX_GROUPS = [
    "female_pct",
    "male_pct",
]

# AGE DOMAIN
AGE_GROUPS = [
    "age65_pct",
]

# ---------------------------
# DOMAIN MAXIMA
# ---------------------------
DOMAIN_MAX = {
    "race": 12,  # 4 groups * max 3 points
    "sex": 6,    # 2 groups * 3 points
    "age": 3,    # 1 group * 3 points
}
