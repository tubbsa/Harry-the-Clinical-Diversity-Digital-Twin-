# ============================================================
# nfrules.py — Neuro-Fuzzy Policy Layer (FINAL)
# Abigail's Dissertation
#
# Purpose:
#   Translate model-predicted ICER + domain scores into
#   interpretable, actionable trial design recommendations.
#
# Design:
#   • CatBoost = learning
#   • ICER/CDR = scoring
#   • Fuzzy system = policy interpretation (NOT trained)
#
# Backward compatible with:
#   recommend_nf(payload, preds)
# ============================================================

from simpful import FuzzySystem, FuzzySet, LinguisticVariable


# ------------------------------------------------------------
# Utilities
# ------------------------------------------------------------

def _clamp(x, lo, hi):
    try:
        x = float(x)
    except (TypeError, ValueError):
        return lo
    return max(lo, min(hi, x))


# ------------------------------------------------------------
# Domain score inference helpers
# ------------------------------------------------------------

def _infer_domain_scores(preds):
    """
    Extract domain-level scores from prediction dict.
    Safe defaults if fields are missing.
    """
    return {
        "race": preds.get("race_score", 0.0),
        "sex": preds.get("sex_score", 0.0),
        "age": preds.get("age_score", 0.0),
    }


def _infer_baseline_scores():
    """
    Default parity baselines.
    Matches your ICER rubric:
      race = 6
      sex  = 3
      age  = 3
    """
    return {
        "race": 6.0,
        "sex": 3.0,
        "age": 3.0,
    }


# ------------------------------------------------------------
# PUBLIC ENTRY POINT (used by Main.py)
# ------------------------------------------------------------

def recommend_nf(payload, preds):
    """
    Backward-compatible API.

    Parameters
    ----------
    payload : dict
        Trial design inputs (eligibility, phase, etc.)

    preds : dict
        Model outputs including:
          • icer_score
          • race_score (optional)
          • sex_score  (optional)
          • age_score  (optional)

    Returns
    -------
    list[str]
        Human-readable recommendations
    """

    domain_scores = _infer_domain_scores(preds)
    baseline_scores = _infer_baseline_scores()

    return _recommend_nf_core(
        payload=payload,
        preds=preds,
        domain_scores=domain_scores,
        baseline_scores=baseline_scores,
    )


# ------------------------------------------------------------
# INTERNAL CORE LOGIC (FULL VERSION)
# ------------------------------------------------------------

def _recommend_nf_core(payload, preds, domain_scores, baseline_scores):
    """
    Internal neuro-fuzzy logic.
    Not called directly by the app.
    """

    # --------------------------------------------------------
    # 1. ICER → ACTION INTENSITY (FUZZY)
    # --------------------------------------------------------

    icer = _clamp(preds.get("icer_score", 0), 0, 100)

    FS = FuzzySystem()

    # ICER input
    FS.add_linguistic_variable(
        "ICER",
        LinguisticVariable(
            [
                FuzzySet(points=[[0, 1], [0, 1], [40, 0]], term="LOW"),
                FuzzySet(points=[[30, 0], [50, 1], [70, 0]], term="MEDIUM"),
                FuzzySet(points=[[60, 0], [100, 1], [100, 1]], term="HIGH"),
            ],
            universe_of_discourse=[0, 100],
        ),
    )

    # ACTION output
    FS.add_linguistic_variable(
        "ACTION",
        LinguisticVariable(
            [
                FuzzySet(points=[[0, 1], [0, 1], [3, 0]], term="LIGHT"),
                FuzzySet(points=[[2, 0], [5, 1], [8, 0]], term="MODERATE"),
                FuzzySet(points=[[7, 0], [10, 1], [10, 1]], term="AGGRESSIVE"),
            ],
            universe_of_discourse=[0, 10],
        ),
    )

    FS.add_rules([
        "IF (ICER IS LOW) THEN (ACTION IS AGGRESSIVE)",
        "IF (ICER IS MEDIUM) THEN (ACTION IS MODERATE)",
        "IF (ICER IS HIGH) THEN (ACTION IS LIGHT)",
    ])

    FS.set_variable("ICER", icer)
    action_level = FS.inference()["ACTION"]

    # --------------------------------------------------------
    # 2. DOMAIN GAPS (WHAT to change)
    # --------------------------------------------------------

    gaps = {
        k: baseline_scores.get(k, 0.0) - domain_scores.get(k, 0.0)
        for k in ["race", "sex", "age"]
    }

    # --------------------------------------------------------
    # 3. FEATURE-AWARE RECOMMENDATIONS
    # --------------------------------------------------------

    recs = []

    # ---- Race equity --------------------------------------
    if gaps["race"] > 0.75:
        recs.extend([
            "Increase site diversity by adding community-based or non-academic recruitment locations",
            "Review exclusion criteria that may disproportionately affect under-represented racial groups",
        ])

    # ---- Sex equity ---------------------------------------
    if gaps["sex"] > 0.5:
        if payload.get("eligibility_sex", "").upper() not in ["ALL", "BOTH"]:
            recs.append(
                "Reconsider sex-restricted eligibility criteria where clinically appropriate"
            )
        recs.append(
            "Ensure recruitment materials are inclusive and accessible across genders"
        )

    # ---- Age equity ---------------------------------------
    if gaps["age"] > 0.5:
        max_age = payload.get("eligibility_max_age")
        if max_age is not None and max_age < 75:
            recs.append(
                "Consider increasing the maximum eligible age to improve older-adult representation"
            )
        recs.append(
            "Reduce visit burden or add decentralized options to support older participants"
        )

    # --------------------------------------------------------
    # 4. MODULATE BY ACTION INTENSITY (HOW MUCH)
    # --------------------------------------------------------

    if not recs:
        return ["No major equity-related design changes recommended"]

    if action_level < 3:
        # LIGHT
        return recs[:1]

    elif action_level < 7:
        # MODERATE
        return recs[:3]

    else:
        # AGGRESSIVE
        return recs
