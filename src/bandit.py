# ============================================================
# FILE: src/bandit.py
# ============================================================
import random

def bandit_optimize(payload, preds):
    best = {"action": None, "delta": 0}
    for _ in range(10):
        act = random.choice(["expand_age", "reduce_exclusions", "adjust_masking"])
        delta = random.uniform(0, 1)
        if delta > best["delta"]:
            best = {"action": act, "delta": delta}
    return [best]
