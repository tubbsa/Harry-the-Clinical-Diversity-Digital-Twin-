# ============================================================
# pdrr_chart.py — PDRR bar chart (Trial / Disease Prevalence)
# DASHBOARD-READY, NONE-SAFE
# ============================================================

from typing import Any, Dict, Union

import numpy as np
import pandas as pd
import plotly.graph_objects as go

try:
    from utils.constants import DISPLAY_LABELS
except Exception:
    DISPLAY_LABELS = {}

# -----------------------------
# Display-only label mappings
# -----------------------------
RENAME_MAP = {
    "white_pct": "White %",
    "black_pct": "Black %",
    "asian_pct": "Asian %",
    "aian_pct": "American Indian / Alaska Native %",
    "female_pct": "Female %",
    "male_pct": "Male %",
    "age65_pct": "Age 65+ %",
}

DEMO_MAP = {
    0: "White",
    1: "Black",
    2: "Asian",
    3: "American Indian / Alaska Native",
    4: "Female",
    5: "Male",
    6: "Age 65+",
}


def _to_dataframe(breakdown: Union[pd.DataFrame, Dict[str, Any]]) -> pd.DataFrame:
    if isinstance(breakdown, pd.DataFrame):
        return breakdown.copy()
    elif isinstance(breakdown, dict):
        if breakdown and isinstance(next(iter(breakdown.values())), dict):
            df = pd.DataFrame.from_dict(breakdown, orient="index")
            df.index.name = "group"
            return df.reset_index()
        return pd.DataFrame([breakdown])
    else:
        raise TypeError("breakdown must be a dict or pandas.DataFrame")


def _find_group_column(df: pd.DataFrame) -> str:
    for cand in ["group", "subgroup", "category", "label"]:
        if cand in df.columns:
            return cand
    df["group"] = df.index.astype(str)
    return "group"


def _ensure_pdrr_column(df: pd.DataFrame) -> pd.DataFrame:
    for c in ["pdrr", "PDRR", "pdr_ratio", "pdrr_ratio"]:
        if c in df.columns:
            df["pdrr"] = df[c].astype(float)
            return df

    trial_candidates = ["trial_frac", "trial", "pred_frac", "predicted", "trial_pct"]
    prev_candidates = ["prev_frac", "prevalence", "disease_prev", "prev_pct"]

    trial_col = next((c for c in trial_candidates if c in df.columns), None)
    prev_col = next((c for c in prev_candidates if c in df.columns), None)

    if trial_col and prev_col:
        df["pdrr"] = (
            df[trial_col].astype(float)
            / df[prev_col].replace(0, np.nan).astype(float)
        ).fillna(0.0)
        return df

    # Neutral fallback so chart still renders
    df["pdrr"] = 1.0
    return df


def _coerce_int_like(x: Any) -> Any:
    """Convert int-like values (e.g., '3', 3.0) to int; otherwise return as-is."""
    if x is None:
        return x
    if isinstance(x, (int, np.integer)):
        return int(x)
    if isinstance(x, float) and np.isfinite(x) and float(x).is_integer():
        return int(x)
    if isinstance(x, str):
        s = x.strip()
        if s.isdigit():
            try:
                return int(s)
            except Exception:
                return x
    return x


def make_pdrr_bar_chart(
    breakdown: Union[pd.DataFrame, Dict[str, Any]],
    threshold: float = 0.8,
) -> go.Figure:
    df = _to_dataframe(breakdown)
    group_col = _find_group_column(df)
    df = _ensure_pdrr_column(df)

    # -----------------------------
    # Human-readable labels (display-only)
    # -----------------------------
    def prettify_label(g: Any) -> str:
        # 0) External labels override if your app defines them
        # (Keeps existing behavior but doesn’t break numeric mapping)
        if g in DISPLAY_LABELS:
            return str(DISPLAY_LABELS[g])

        # 1) numeric demographic codes -> readable
        gi = _coerce_int_like(g)
        if isinstance(gi, int) and gi in DEMO_MAP:
            return f"{DEMO_MAP[gi]} %"

        # 2) known snake_case percent keys -> friendly labels
        gs = str(g)
        if gs in RENAME_MAP:
            return RENAME_MAP[gs]

        # 3) fallback normalization (handles 'white_pct', 'age65', etc.)
        base = gs.replace("_pct", "").replace("_", " ").lower()
        mapping = {
            "white": "White",
            "black": "Black",
            "asian": "Asian",
            "female": "Female",
            "male": "Male",
            "age65": "Age 65+",
            "age 65": "Age 65+",
            "aian": "American Indian / Alaska Native",
            "american indian alaska native": "American Indian / Alaska Native",
        }
        label = mapping.get(base, base.title())
        # If the thing already looks like a percent label, add %; otherwise don’t force it.
        return f"{label} %"

    df["display_label"] = df[group_col].apply(prettify_label)

    # Sort by PDRR (under-represented first)
    df = df.sort_values("pdrr").reset_index(drop=True)

    x_labels = df["display_label"].tolist()
    ymax = max(1.2, np.ceil(df["pdrr"].max() * 10) / 10)

    colors = np.where(df["pdrr"] < threshold, "#D55E00", "#4C72B0")

    fig = go.Figure()
    fig.add_bar(
        x=x_labels,
        y=df["pdrr"].tolist(),
        marker_color=colors,
        text=[f"{v:.2f}" for v in df["pdrr"]],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Enrollment ÷ Disease Prevalence: %{y:.2f}<extra></extra>",
        showlegend=False,
    )

    # Equity threshold line
    fig.add_hline(
        y=threshold,
        line_dash="dash",
        line_width=2,
        line_color="#333333",
        annotation_text=f"Equity threshold ({threshold})",
        annotation_position="top left",
        annotation_font_size=12,
    )

    fig.update_layout(
        title=dict(
            text="Enrollment Relative to Disease Burden (PDRR)",
            font=dict(size=20),
            pad=dict(b=12),
        ),
        xaxis=dict(
            title="Demographic Group",
            type="category",
            tickangle=30,
            tickfont=dict(size=12),
        ),
        yaxis=dict(
            title="Enrollment Relative to Disease Burden",
            range=[0, ymax],
            tickfont=dict(size=12),
        ),
        margin=dict(l=60, r=40, t=130, b=80),
        template="plotly_white",
        annotations=[
            dict(
                text=(
                    "Compares predicted trial enrollment to disease prevalence for each demographic group. "
                    "Values below the equity threshold indicate under-representation."
                ),
                xref="paper",
                yref="paper",
                x=0,
                y=1.10,
                showarrow=False,
                align="left",
                font=dict(size=13, color="#555"),
            ),
            dict(
                text="Orange = under-represented • Blue = adequately represented",
                xref="paper",
                yref="paper",
                x=1,
                y=1.10,
                showarrow=False,
                align="right",
                font=dict(size=12, color="#555"),
            ),
        ],
    )

    return fig

