# src/narrative.py
from __future__ import annotations

from typing import Any, Dict, Optional


def build_narrative(
    payload: Dict[str, Any],
    preds: Dict[str, Any],
    score: Optional[Any] = None,
    nf_actions: Optional[Any] = None,
    bandit_actions: Optional[Any] = None,
) -> str:
    """
    Always returns narrative text.
    If you later add an LLM call, keep a fallback template so UI never goes blank.
    """
    lines = []
    lines.append("Digital Twin Clinical Summary")
    lines.append("")
    lines.append("Trial inputs (as provided):")
    if payload:
        for k, v in sorted(payload.items()):
            lines.append(f"- {k}: {v}")
    else:
        lines.append("- (no payload found in session_state['payload'])")

    lines.append("")
    lines.append("Predicted subgroup representation:")
    if preds:
        for k, v in sorted(preds.items()):
            lines.append(f"- {k}: {v}")
    else:
        lines.append("- (none)")

    if score is not None:
        lines.append("")
        lines.append(f"ICER Diversity Score: {score}")

    if nf_actions is not None or bandit_actions is not None:
        lines.append("")
        lines.append("Recommended Design Considerations (informational):")
        lines.append(f"- Neuro-Fuzzy: {nf_actions}")
        lines.append(f"- Bandit/RL: {bandit_actions}")

    lines.append("")
    lines.append("Disclaimer: This output is informational decision support only and not medical advice.")
    return "\n".join(lines)
