# Harry: Clinical Trial Diversity Digital Twin

Harry is an interactive clinical trial diversity digital twin that maps structured protocol design inputs to predicted demographic enrollment, equity metrics, and interpretable design recommendations. The application enables prospective assessment of demographic representation relative to disease prevalence before trial launch.

The system is implemented as a Streamlit-based decision-support interface built on top of a frozen machine learning pipeline and deterministic scoring framework. It is intended for clinical trial designers, operations analysts, and researchers evaluating how protocol design choices influence expected demographic representation and equity-related outcomes.

---

## Repository Structure

digital_twin/
├── MODEL_CARD.md
├── Makefile
├── README.md
├── app/
│ ├── Main.py # Streamlit application entry point
│ ├── init.py
│ └── pages/
│ └── Report.py # Narrative reporting interface
├── charts/
│ ├── pdrr_chart.py # PDRR bar chart visualization
│ └── rep_prev_diverging.py # Representation vs prevalence plots
├── components/
│ ├── form_inputs.py # Structured trial input controls
│ ├── score_tiles.py # Summary score display
│ └── tables.py # ICER-style breakdown table (display-only logic)
├── model/
│ ├── cb_model_multituned.cbm # Trained CatBoost multi-output model
│ ├── encoder.pkl # Frozen categorical encoder
│ ├── hurdle_clf.pkl
│ ├── hurdle_reg.pkl
│ ├── FEATURE_NAMES.pkl
│ ├── TARGET_COLS.pkl
│ ├── NUM_COLS.pkl
│ ├── CAT_COLS.pkl
│ ├── ood_cols.npy
│ ├── ood_mean.npy
│ └── ood_std.npy
├── src/
│ ├── predictor.py # Inference logic
│ ├── preprocess.py # Feature assembly and validation
│ ├── scoring.py # CDR / ICER-style scoring
│ ├── bandit.py
│ ├── narrative.py
│ ├── schema.py
│ └── scoring_constants.py
├── pdf/
│ └── scorecard_pdf.py # PDF scorecard generation
├── utils/
│ ├── constants.py
│ ├── gap_analysis.py
│ └── payload_builder.py
├── tests/
│ ├── test_predictor.py
│ ├── test_scoring.py
│ └── test_gui_smoke.py
├── rebuild_artifacts.py
├── environment.yml
├── requirements.txt
└── venv/ # Local virtual environment (not required for deployment)

---

## System Overview

Harry is implemented as an end-to-end application layer that operationalizes a trained demographic prediction model within a broader trial-level decision-support framework. The application does not retrain models or modify learned parameters at runtime. All predictions, scores, and recommendations are generated using frozen artifacts identical to those used during offline evaluation.

The application integrates:
- Multi-target demographic enrollment prediction
- Deterministic ICER-style composite scoring
- A rule-based neuro-fuzzy policy layer
- Narrative reporting and visualization modules

---

## Application and Deployment Interface

### 1. Structured Trial Inputs and Validation

The application collects trial design information through explicitly typed input controls that mirror structured fields commonly reported in ClinicalTrials.gov. Inputs are organized into logical sections reflecting protocol composition, eligibility criteria, and recruitment scale.

Categorical protocol attributes—including study phase, sponsor type, study type, allocation, intervention model, masking, and primary purpose—are captured using controlled-selection inputs to enforce valid category membership. These selections correspond directly to the categorical features used during model training.

Eligibility criteria are specified through both categorical and numeric inputs. Eligibility sex is selected from predefined categories, while minimum and maximum age limits are entered as bounded numeric values expressed in years. Recruitment scope is represented by numeric inputs capturing the number of recruiting U.S. states, the number of recruiting sites, and planned enrollment size.

Narrative protocol components, including inclusion criteria, exclusion criteria, conditions, interventions, and primary and secondary outcome measures, are assembled through structured text inputs. These narrative fields are combined into a unified protocol text representation using a fixed ordering and normalization procedure.

---

### 2. Input Validation and Schema Enforcement

All user inputs are validated at entry time to ensure consistency with the schema used during model training. Categorical inputs are restricted to known category levels, with missing or unspecified selections mapped to an explicit “Unknown” category. Numeric inputs are constrained using hard bounds consistent with the preprocessing pipeline.

Narrative text inputs are normalized to remove extraneous whitespace and enforce consistent formatting. Inputs that violate schema requirements are rejected prior to inference, preventing silent errors and ensuring that all predictions are generated from well-formed trial specifications.

Upon validation, inputs are transformed into the canonical feature representation expected by the trained model. Narrative fields are concatenated and embedded using the same pretrained transformer model, tokenization settings, truncation length, and pooling strategy used during training. Categorical inputs are encoded using the frozen encoder, and numeric inputs are assembled into a fixed-order feature vector. No preprocessing components are refit at runtime.

---

### 3. Trial-Level Inference and Interactive Analysis

For each completed trial specification, the application executes deterministic inference using a trained CatBoost multi-output regression model. The model outputs a vector of predicted demographic enrollment proportions, with one continuous value between zero and one for each demographic target.

Predictions are displayed in a labeled, target-wise format. Users may interactively modify trial design inputs and immediately observe changes in predicted demographic composition. Because preprocessing logic and model artifacts are frozen, output differences reflect only changes in specified protocol attributes, enabling structured “what-if” analysis.

---

### 4. Composite Scoring and Neuro-Fuzzy Policy Layer

Following demographic prediction, the application computes a Clinical Diversity Representation (CDR) score using a deterministic ICER-style formulation. For each demographic target, predicted enrollment is compared against fixed reference proportions derived from population-based disease prevalence ratios (PDRR).

Per-target deviations are aggregated into a composite score reflecting relative over- or under-representation. The CDR score is used exclusively for comparative assessment across trial designs and does not influence model predictions.

Predicted values and scores are then evaluated by a rule-based neuro-fuzzy policy layer implemented as a deterministic fuzzy inference system. This layer maps CDR scores to graded action intensity levels (e.g., light, moderate, aggressive) using expert-defined membership functions and rules. The policy layer does not modify predictions and does not undergo training.

---

### 5. Narrative Reporting Module

The application includes a narrative reporting module that converts quantitative outputs into structured, human-readable summaries. This module assembles predicted demographic proportions, composite scores, and neuro-fuzzy recommendations into a standardized report using predefined templates.

The narrative module does not invoke an external language model and operates strictly as a post-hoc reporting layer to ensure interpretability and consistency.

---

### 6. Visualization, Diagnostics, and Data Handling

Predicted demographic proportions are presented through tabular and graphical views, including ICER-style breakdown tables and PDRR bar charts. Where available, diagnostic artifacts such as feature attribution summaries are rendered for inspection.

The application operates exclusively on trial-level protocol metadata and does not require patient-level data or protected health information. All inputs are processed in-memory during the user session and are not persistently stored.

All preprocessing logic, encoders, and model artifacts are versioned and identical to those used during offline evaluation. The application supports export of a summary scorecard as a PDF artifact generated from prediction outputs, scores, and visualizations.

---

## Running Locally

```bash
pip install -r requirements.txt
streamlit run app/Main.py
Deployment
The application is compatible with Streamlit Community Cloud, Render, and Hugging Face Spaces. Ensure requirements.txt is present and app/Main.py is configured as the entry point.
Disclaimer
This tool is intended for research and decision-support purposes only. Predictions represent statistical estimates derived from historical registry data and are not intended to replace site-level feasibility assessments, regulatory guidance, or clinical judgment.
Author
Abigail Tubbs
PhD Candidate, Biomedical Engineering
Clinical trial equity, digital twins, and interpretable machine learning

---

### Next steps 
1. Commit this README:
```bash
git add README.md
git commit -m 
git push
