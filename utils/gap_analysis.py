# ============================================================
# gap_analysis.py — Compute largest representation gaps
# (MINIMAL FIX FOR NONE-SAFE OPERATION)
# ============================================================

from utils.constants import DISPLAY_LABELS

def compute_largest_gaps(preds_frac: dict, disease_prev: dict, top_k: int = 3) -> str:
    """
    Computes the largest representation gaps between predicted representation
    (fractions, 0–1) and disease prevalence (fractions, 0–1).

    Returns a human-readable string such as:
    'Asian (−3%), Black (+3%), Female (+42%)'
    """

    gaps = []

    for group, pred in preds_frac.items():
        prev = disease_prev.get(group)

        # Skip if either value is missing
        if pred is None or prev is None:
            continue

        gap = pred - prev  # fraction
        gaps.append((group, gap))

    if not gaps:
        return "No significant gaps detected."

    # Sort by magnitude of gap (largest absolute differences first)
    gaps_sorted = sorted(gaps, key=lambda x: abs(x[1]), reverse=True)
    top = gaps_sorted[:top_k]

    formatted = []
    for group, gap in top:
        label = DISPLAY_LABELS.get(group, group.replace("_pct", "").title())
        sign = "+" if gap > 0 else "−"
        pct = abs(int(round(gap * 100)))
        formatted.append(f"{label} ({sign}{pct}%)")

    return ", ".join(formatted)


