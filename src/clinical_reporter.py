# src/clinical_reporter.py
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, Union

from src import narrative


def _as_dict(x: Any) -> Dict[str, Any]:
    return x if isinstance(x, dict) else {}


def _as_list(x: Any) -> List[Any]:
    if x is None:
        return []
    if isinstance(x, list):
        return x
    return [x]


def generate(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stable entrypoint for Streamlit.

    Expected payload (from Main.py report_payload):
      - trial_context: dict (phase/conditions/intervention)
      - predicted_representation: dict (e.g., white_pct, black_pct, female_pct...)
      - icer_score: float/int
      - recommended_actions: dict with keys:
            neuro_fuzzy: list[str]
            bandit: list[dict]
      - disclaimer: str

    Returns a JSON-serializable dict:
      - summary: str
      - predictions: dict (mirrors predicted_representation)
      - score: float/int (mirrors icer_score)
      - nf_actions: list
      - bandit_actions: list
      - inputs_used: original payload
      - meta: dict
    """
    # Normalize payload
    if payload is None:
        payload = {}
    if not isinstance(payload, dict):
        payload = {"_raw_payload": str(payload)}

    # Map from your Main.py keys (preferred)
    preds = _as_dict(payload.get("predicted_representation"))
    score = payload.get("icer_score")

    recs = _as_dict(payload.get("recommended_actions"))
    nf_actions = _as_list(recs.get("neuro_fuzzy"))
    bandit_actions = _as_list(recs.get("bandit"))

    # Back-compat: if other parts of the code pass these legacy keys
    if not preds:
        preds = _as_dict(payload.get("preds"))
    if score is None:
        score = payload.get("score")
    if not nf_actions:
        nf_actions = _as_list(payload.get("nf_actions"))
    if not bandit_actions:
        bandit_actions = _as_list(payload.get("bandit_actions"))

    # Build narrative text (always returns a string)
    text = narrative.build_narrative(
        payload=payload,
        preds=preds,
        score=score,
        nf_actions=nf_actions,
        bandit_actions=bandit_actions,
    )

    return {
        "summary": text,
        "predictions": preds,
        "score": score,
        "nf_actions": nf_actions,
        "bandit_actions": bandit_actions,
        "inputs_used": payload,
        "meta": {"report_version": "1.0"},
    }


def build_llm_report(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Backwards-compatible alias for code that imports build_llm_report.
    """
    return generate(payload)

