def test_scoring_requires_fractions():
    from src.scoring import compute_icer_score

    preds = {
        "white_pct": 0.12,
        "black_pct": 0.10,
        "asian_pct": 0.05,
        "aian_pct": 0.02,
        "female_pct": 0.55,
        "male_pct": 0.45,
        "age65_pct": 0.30,
    }

    score, _ = compute_icer_score(preds)
    assert score > 0
