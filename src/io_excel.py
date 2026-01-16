# ============================================================
# FILE: src/io_excel.py
# ============================================================
import pandas as pd

EXCEL_PATH = "/Users/abigailtubbs/Desktop/Fall 2025/Dissertation F25/Harry/CDR-Tool_2024.xlsx"

def load_icer_excel():
    try:
        xls = pd.ExcelFile(EXCEL_PATH)
    except Exception as e:
        raise RuntimeError(f"Failed to load Excel at {EXCEL_PATH}: {e}")

    print("Sheets discovered:", xls.sheet_names)
    sheets = {}
    for s in xls.sheet_names:
        sheets[s] = pd.read_excel(xls, sheet_name=s)
    return sheets
