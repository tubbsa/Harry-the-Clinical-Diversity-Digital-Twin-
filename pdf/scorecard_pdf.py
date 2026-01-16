# pdf/scorecard_pdf.py
from __future__ import annotations

import io
from typing import Any, Dict, Optional

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def build_pdf(report: Dict[str, Any]) -> bytes:
    """
    Build an in-memory PDF and return bytes suitable for st.download_button.
    Never writes to disk.

    Optional fields:
      - report["summary"] or report["narrative"]
      - report["predictions"] (dict)
      - report["score"] (number/str)
      - report["meta"]["title"] (str)
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    meta = report.get("meta") or {}
    title = meta.get("title") or "Clinical Trial Diversity Report"

    y = height - 50
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, str(title)[:120])
    y -= 25

    score = report.get("score")
    if score is not None:
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, f"ICER Diversity Score: {score}")
        y -= 18

    summary = str(report.get("summary") or report.get("narrative") or "")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Narrative Summary:")
    y -= 15
    c.setFont("Helvetica", 10)

    if summary.strip():
        for line in summary.splitlines():
            c.drawString(60, y, line[:120])
            y -= 12
            if y < 80:
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 10)
    else:
        c.drawString(60, y, "(no summary provided)")
        y -= 12

    preds = report.get("predictions") or {}
    y -= 10
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Predicted Subgroup Representation:")
    y -= 15
    c.setFont("Helvetica", 10)

    if isinstance(preds, dict) and preds:
        for k, v in preds.items():
            c.drawString(60, y, f"{k}: {v}")
            y -= 12
            if y < 80:
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 10)
    else:
        c.drawString(60, y, "(none)")
        y -= 12

    c.showPage()
    c.save()

    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


def _coerce_report(report: Any) -> Dict[str, Any]:
    """Ensure we always pass a dict into build_pdf()."""
    if isinstance(report, dict):
        return report
    if report is None:
        return {"summary": "(no report provided)", "predictions": {}, "meta": {}}
    return {"summary": str(report), "predictions": {}, "meta": {}}


def generate_pdf_scorecard(report: Optional[Dict[str, Any]] = None, **kwargs) -> bytes:
    """
    Backwards-compatible function expected by app/Main.py.

    Handles all of these call styles safely:
      1) generate_pdf_scorecard(report_dict)
      2) generate_pdf_scorecard(report=report_dict, title="...")
      3) generate_pdf_scorecard(title="...")   <-- Main.py currently does this (missing report)

    We accept arbitrary kwargs to avoid TypeErrors.
    """
    # If Main.py forgot to pass report, try common kwarg names
    if report is None:
        report = (
            kwargs.get("report")
            or kwargs.get("report_dict")
            or kwargs.get("payload")
            or kwargs.get("data")
        )

    report_dict = _coerce_report(report)

    # Inject title into meta if provided
    title = kwargs.get("title")
    if title:
        meta = dict(report_dict.get("meta") or {})
        meta["title"] = title
        report_dict["meta"] = meta

    # If Main.py passes score separately, inject it too
    if "score" in kwargs and report_dict.get("score") is None:
        report_dict["score"] = kwargs.get("score")

    # If it passes summary separately, inject it
    if "summary" in kwargs and not report_dict.get("summary"):
        report_dict["summary"] = kwargs.get("summary")

    return build_pdf(report_dict)
