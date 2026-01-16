# ============================================================
# FILE: tests/test_scoring.py
# (uses small fixture Excel)
# ============================================================
import pandas as pd
from src.scoring import compute_icer_score

def test_scoring_fixture(tmp_path):
    # minimal fixture: weights sheet
    df = pd.DataFrame({
        "component": ["white_pct","black_pct"],
        "weight": [1.0, 2.0]
    })
    fx = tmp_path/"fixture.xlsx"
    with pd.ExcelWriter(fx) as w:
        df.to_excel(w, sheet_name="Weights", index=False)

    preds = {"white_pct": 10, "black_pct": 20}
    meta = {}

    score, breakdown = compute_icer_score(preds, meta)
    assert score >= 0
    assert len(breakdown) == 2
