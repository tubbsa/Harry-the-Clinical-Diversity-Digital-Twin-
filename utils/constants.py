# ============================================================
# utils/constants.py — Display labels + category order
# ============================================================

# Clean, final category order used in:
# - Predicted Representation table
# - Charts
# - ICER scoring alignment
CATEGORY_ORDER = [
    "white_pct",
    "black_pct",
    "asian_pct",
    "aian_pct",     # American Indian / Alaska Native
    "female_pct",
    "male_pct",
    "age65_pct",
]

# Human-readable display labels
DISPLAY_LABELS = {
    "white_pct": "White (%)",
    "black_pct": "Black (%)",
    "asian_pct": "Asian (%)",
    "aian_pct": "American Indian / Alaska Native (%)",
    "female_pct": "Female (%)",
    "male_pct": "Male (%)",
    "age65_pct": "Age ≥65 (%)",
}

# ------------------------
# Input Form Option Lists
# ------------------------

INCLUSION_OPTIONS = [
    "Adults (≥18)", "Older Adults (≥60)", "Children/Adolescents", "Diagnosis Confirmed",
    "Biomarker Positive", "Genetic Confirmation", "Symptom Severity Threshold",
    "Disease Duration Requirement", "Treatment-Naïve Required", "Stable Medication Regimen",
    "Recent Diagnosis", "Specific Subtype Required", "Laboratory Value Threshold",
    "Imaging Requirement (MRI/CT)", "Functional Test Requirement",
    "Cognitive Screening Requirement", "Performance Status Requirement",
    "Ability to Consent", "Life Expectancy Requirement", "BMI Threshold",
    "Blood Pressure Threshold", "Glycemic Control Threshold", "Organ Function Requirement",
    "Cardiac Function Requirement", "Renal Function Requirement",
    "Hepatic Function Requirement", "Pregnancy Test Required", "Non-Pregnant Required",
    "No Active Infection", "No Recent Surgery", "No Active Substance Use", "Non-Smoker",
    "Reproductive Status Requirement", "Vaccination Status Requirement",
    "Prior Therapy Allowed", "Prior Therapy Not Allowed", "Study Locale Requirement",
    "Language Requirement", "Technology Access Requirement", "Caregiver Availability Required",
]

EXCLUSION_OPTIONS = [
    "Pregnant or Breastfeeding", "Uncontrolled Hypertension", "Uncontrolled Diabetes",
    "Severe Hepatic Impairment", "Severe Renal Impairment", "Cardiovascular Instability",
    "Respiratory Diseases", "Neurological Instability", "Active Malignancy",
    "History of Malignancy", "Recent Major Surgery", "Recent Trauma",
    "Recent Hospitalization", "Severe Psychiatric Condition", "Active Substance Abuse",
    "Active Infection", "Immunocompromised State", "Autoimmune Disorders",
    "Allergy/Hypersensitivity", "Contraindicated Medications", "Recent Experimental Therapy",
    "Prohibited Concomitant Medications", "BMI Exclusion Threshold",
    "Organ Transplant History", "HIV/HBV/HCV Infection", "Cardiac Devices Implanted",
    "Contraindicated for MRI", "Contraindicated for Anesthesia", "Mobility Impairment",
    "Cognitive Impairment", "Poor Performance Status", "Pregnancy Potential Not Controlled",
    "Inadequate Organ Function", "Abnormal Lab Values", "QT Prolongation",
    "Bleeding Disorders", "Recent Vaccine", "Inability to Consent",
    "Other Investigator Judgment Exclusions",
]

CONDITION_OPTIONS = [
    "Hypertension", "Diabetes Mellitus Type 1", "Diabetes Mellitus Type 2", "Obesity",
    "Hyperlipidemia", "Heart Failure", "Atrial Fibrillation", "Coronary Artery Disease",
    "Stroke", "Chronic Kidney Disease", "COPD", "Asthma", "Allergic Diseases", "Cancer",
    "Breast Cancer", "Lung Cancer", "Colorectal Cancer", "Prostate Cancer",
    "Parkinson’s Disease", "Alzheimer’s Disease", "Multiple Sclerosis", "Epilepsy",
    "Major Depressive Disorder", "Anxiety Disorders", "Bipolar Disorder", "Schizophrenia",
    "Arthritis", "Osteoporosis", "Autoimmune Diseases", "Liver Diseases",
    "Viral Infections", "HIV", "COVID-19", "Dermatologic Disorders", "Endocrine Disorders",
    "GI Disorders", "Reproductive Disorders", "Sleep Disorders", "Chronic Pain",
    "General Healthy Volunteer",
]

INTERVENTION_OPTIONS = [
    "Drug - Small Molecule", "Drug - Biologic", "Drug - Chemotherapy",
    "Drug - Immunotherapy", "Drug - Hormonal Therapy", "Drug - Vaccine",
    "Drug - Antibiotic", "Drug - Antiviral", "Drug - Cardiovascular",
    "Drug - Diabetes", "Drug - Neurology", "Drug - Psychiatry",
    "Device - Neuromodulation", "Device - Implantable", "Device - Wearable",
    "Device - Diagnostic", "Device - Monitoring",
    "Procedure - Surgery", "Procedure - Endoscopy", "Procedure - Imaging",
    "Behavioral Therapy", "Cognitive Behavioral Therapy", "Dietary Intervention",
    "Exercise Intervention", "Rehabilitation", "Educational Program",
    "Psychotherapy", "Counseling", "Occupational Therapy", "Physical Therapy",
    "Radiation Therapy", "Telehealth Intervention", "Remote Monitoring",
    "Mobile App Intervention", "Digital Device", "Sham Control", "Placebo",
]

PRIMARY_OUTCOME_OPTIONS = [
    "Overall Survival", "Progression-Free Survival", "Disease-Free Survival",
    "Symptom Score Change", "Quality of Life", "Pain Reduction",
    "Blood Pressure Reduction", "HbA1c Change", "Lipid Level Change",
    "BMI Change", "Functional Status", "6-Minute Walk Test",
    "Cognitive Function", "Depression Scale", "Anxiety Scale",
    "Neurological Function", "Motor Function", "Seizure Frequency",
    "Cardiac Output", "Heart Rate Variability", "Renal Function",
    "Liver Function", "Inflammatory Biomarkers", "Genetic Biomarkers",
    "Imaging Findings", "MRI Biomarkers", "CT Findings",
    "Safety (AEs)", "Serious Adverse Events", "Device Performance",
    "Treatment Adherence", "Therapeutic Dose Response", "Immunogenicity",
    "Infection Rate", "Hospitalization Rate", "Readmission Rate",
    "Time to Event", "Therapeutic Efficacy", "Clinical Remission",
]

SECONDARY_OUTCOME_OPTIONS = [
    "Quality of Life", "Safety (AEs)", "Serious Adverse Events",
    "Medication Adherence", "Biomarker Exploration", "Exploratory Imaging",
    "Dose Response", "Pharmacokinetics", "Pharmacodynamics", "Cognitive Measures",
    "Motor Function", "Pain Scale", "Function Tests", "Mental Health Scores",
    "Sleep Quality", "Weight Change", "Waist Circumference", "Blood Pressure",
    "Heart Rate", "Cardiac Markers", "Blood Sugar", "Lipids",
    "Hormone Levels", "Immunogenicity", "Inflammatory Markers",
    "MRI Measures", "CT Measures", "Ultrasound Measures", "Lab Panels",
    "Hospitalization", "Emergency Visits", "Quality Metrics",
    "Treatment Acceptability", "Treatment Satisfaction",
    "Adherence to Device", "Device Safety", "Device Usability",
    "Exploratory Genetic Markers", "Reproductive Outcomes",
    "Long-Term Follow-Up",
]
