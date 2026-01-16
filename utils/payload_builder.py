# ============================================================
# payload_builder.py — Convert Streamlit form output into
# model-ready payload dict for predictor.py
# ============================================================

def build_payload(inputs: dict) -> dict:
    """
    Convert the dictionary returned by render_form_and_collect_inputs()
    into a payload dict with the exact fields expected by predictor.py.
    """

    # ---------------------------
    # TEXT FIELDS (SEPARATE, NOT MERGED)
    # ---------------------------
    inclusion_text     = "; ".join(inputs.get("inclusion_sel", []))
    exclusion_text     = "; ".join(inputs.get("exclusion_sel", []))
    condition_text     = "; ".join(inputs.get("condition_sel", []))
    intervention_text  = "; ".join(inputs.get("intervention_sel", []))
    primary_text       = "; ".join(inputs.get("primary_sel", []))
    secondary_text     = "; ".join(inputs.get("secondary_sel", []))

    # ---------------------------
    # NUMERIC FIELDS
    # Predictor expects: eligibility_min_age, eligibility_max_age
    # ---------------------------
    min_age = inputs.get("min_age", 0)
    max_age = inputs.get("max_age", 120)

    # ---------------------------
    # CATEGORICAL FIELDS
    # ---------------------------
    payload = {
        # TEXT FIELDS (exact names predictor.py expects)
        "inclusion_text": inclusion_text,
        "exclusion_text": exclusion_text,
        "Conditions": condition_text,
        "Interventions": intervention_text,
        "Primary Outcome Measures": primary_text,
        "Secondary Outcome Measures": secondary_text,

        # NUMERIC
        "eligibility_min_age": min_age,
        "eligibility_max_age": max_age,

        # CATEGORICAL
        "eligibility_sex": inputs.get("eligibility_sex", "Unknown"),
        "Sponsor": inputs.get("sponsor", "Unknown"),
        "Collaborators": inputs.get("collaborators", "Unknown"),
        "Phases": inputs.get("phases", "Unknown"),
        "Funder Type": inputs.get("funder_type", "Unknown"),
        "Study Type": inputs.get("study_type", "Unknown"),
        "allocation": inputs.get("allocation", "Unknown"),
        "intervention_model": inputs.get("intervention_model", "Unknown"),
        "masking": inputs.get("masking", "Unknown"),
        "primary_purpose": inputs.get("primary_purpose", "Unknown"),

        # STATIC KEYS predictor.py expects
        "country": "United States",
        "continent": "North America",
    }

    return payload

