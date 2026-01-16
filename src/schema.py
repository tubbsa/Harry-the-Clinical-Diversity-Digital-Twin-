# ============================================================
# schema.py — Canonical demographic schema + adapters
# ============================================================

SCHEMA_VERSION = "SCHEMA_V1"

# Canonical keys used everywhere in UI + scoring
GROUP_KEYS = [
    "white_pct",
    "black_pct",
    "asian_pct",
    "ai_an_pct",          # American Indian / Alaska Native
    "nhpi_pct",
    "female_pct",
    "male_pct",
    "age65_plus_pct",
]

# Common aliases observed across pipeline/UI refactors
KEY_ALIASES = {
    # race
    "white": "white_pct",
    "race_white": "white_pct",
    "White %": "white_pct",
    "black": "black_pct",
    "race_black": "black_pct",
    "asian": "asian_pct",
    "race_asian": "asian_pct",
    "aian": "ai_an_pct",
    "ai_an": "ai_an_pct",
    "American Indian / Alaska Native (%)": "ai_an_pct",
    "nhpi": "nhpi_pct",
    # sex
    "female": "female_pct",
    "sex_female": "female_pct",
    "male": "male_pct",
    "sex_male": "male_pct",
    # age
    "age65": "age65_plus_pct",
    "age_65_plus": "age65_plus_pct",
    "age>=65_pct": "age65_plus_pct",
}

def _coerce_range(v):
    """Accept None, [0,1], or [0,100]; coerce to percentage [0,100]."""
    if v is None:
        return None
    try:
        v = float(v)
    except Exception:
        return None
    if 0 <= v <= 1:
        return v * 100.0
    if 0 <= v <= 100:
        return v
    return None

def coerce_demo_keys(preds: dict) -> dict:
    """
    Adapter to canonicalize demographic outputs.
    - Renames via KEY_ALIASES
    - Ensures all GROUP_KEYS exist (missing -> None)
    - PRESERVES FRACTIONS (0–1). No % scaling here.
    """
    out = {k: None for k in GROUP_KEYS}
    if not preds:
        return out

    for k, v in preds.items():
        ck = KEY_ALIASES.get(k, k)
        if ck in out:
            # Preserve fractions; only clip to [0, 1]
            if v is None:
                out[ck] = None
            else:
                out[ck] = max(0.0, min(1.0, float(v)))

    return out

