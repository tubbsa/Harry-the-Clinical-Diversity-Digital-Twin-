# app/pages/Report.py
from __future__ import annotations

import json
import os
import platform
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, Optional

import streamlit as st

# Robust imports (don’t crash the page; show errors in Debug)
CLINICAL_IMPORT_ERR = None
PDF_IMPORT_ERR = None

try:
    from src import clinical_reporter
except Exception as e:
    clinical_reporter = None
    CLINICAL_IMPORT_ERR = e

try:
    from pdf.scorecard_pdf import build_pdf
except Exception as e:
    build_pdf = None
    PDF_IMPORT_ERR = e


APP_ROOT = Path(__file__).resolve().parents[2]  # repo root
MODEL_DIR = APP_ROOT / "model"


def _init_state() -> None:
    st.session_state.setdefault("payload", {})          # your form should populate this
    st.session_state.setdefault("report", None)         # dict
    st.session_state.setdefault("pdf_bytes", None)      # bytes
    st.session_state.setdefault("report_error", None)   # traceback str


def _safe_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, indent=2, default=str).encode("utf-8")


def _reset() -> None:
    st.session_state.clear()
    try:
        st.cache_data.clear()
        st.cache_resource.clear()
    except Exception:
        pass
    st.success("Reset complete. Reloading artifacts...")
    st.rerun()


def _artifact_checks() -> Dict[str, bool]:
    out: Dict[str, bool] = {}
    if not MODEL_DIR.exists():
        out["model/ (missing)"] = False
        return out
    for p in sorted(MODEL_DIR.glob("*")):
        if p.is_file():
            out[str(p.relative_to(APP_ROOT))] = True
    return out


def _generate(payload: Dict[str, Any]) -> Dict[str, Any]:
    if clinical_reporter is None:
        raise RuntimeError(f"clinical_reporter import failed: {CLINICAL_IMPORT_ERR!r}")

    # Required entrypoint
    if hasattr(clinical_reporter, "generate") and callable(clinical_reporter.generate):
        return clinical_reporter.generate(payload)

    raise AttributeError("src/clinical_reporter.py must define generate(payload)->dict")


def page() -> None:
    st.set_page_config(page_title="Clinical LLM Report", layout="wide")
    _init_state()

    st.title("Clinical LLM Report")
    st.caption("Generate a clinician-facing narrative + downloads. Debug tab shows what’s missing.")

    # Action row
    a1, a2, a3 = st.columns([2, 1, 1])

    with a1:
        if st.button("Generate Clinical LLM Report", type="primary", use_container_width=True):
            st.session_state["report_error"] = None
            st.session_state["report"] = None
            st.session_state["pdf_bytes"] = None

            payload = st.session_state.get("payload") or {}
            if not isinstance(payload, dict):
                payload = {}

            try:
                with st.status("Generating report…", expanded=True) as status:
                    st.write("Payload keys:", list(payload.keys()) if payload else "∅ (empty)")

                    report = _generate(payload)
                    if not isinstance(report, dict) or not report:
                        raise ValueError("Report generation returned empty or non-dict output.")

                    st.session_state["report"] = report

                    # Optional PDF
                    if build_pdf is not None:
                        pdf_bytes = build_pdf(report)
                        if isinstance(pdf_bytes, (bytes, bytearray)) and len(pdf_bytes) > 0:
                            st.session_state["pdf_bytes"] = bytes(pdf_bytes)
                        else:
                            st.warning("PDF builder returned empty bytes (JSON download will still work).")
                    else:
                        st.info("PDF builder import failed; JSON download will still work.")

                    status.update(label="Report generated.", state="complete", expanded=False)

            except Exception:
                st.session_state["report_error"] = traceback.format_exc()
                st.error("Report generation failed. See Details/Debug.")
                st.code(st.session_state["report_error"], language="text")

    with a2:
        if st.button("Reset Digital Twin", use_container_width=True):
            _reset()

    with a3:
        st.write("")  # spacer

    report: Optional[Dict[str, Any]] = st.session_state.get("report")
    pdf_bytes: Optional[bytes] = st.session_state.get("pdf_bytes")
    err: Optional[str] = st.session_state.get("report_error")

    tabs = st.tabs(["Summary", "Details", "Downloads", "Debug"])

    with tabs[0]:
        st.subheader("Summary")
        if not report:
            st.warning("No report yet — click **Generate Clinical LLM Report**.")
        else:
            summary = report.get("summary") or report.get("narrative") or report.get("text") or ""
            if summary.strip():
                st.write(summary)
            else:
                st.info("Report exists but has no summary/narrative field.")
                st.json(report)

    with tabs[1]:
        st.subheader("Details")
        if err:
            st.error("Last error:")
            st.code(err, language="text")
        if report:
            st.json(report)
        else:
            st.info("Nothing to show yet.")

    with tabs[2]:
        st.subheader("Downloads")

        st.download_button(
            "Download JSON",
            data=_safe_json_bytes(report) if report else b"",
            file_name="clinical_report.json",
            mime="application/json",
            disabled=not bool(report),
            use_container_width=True,
        )

        st.download_button(
            "Download PDF",
            data=pdf_bytes if pdf_bytes else b"",
            file_name="clinical_report.pdf",
            mime="application/pdf",
            disabled=not bool(pdf_bytes),
            use_container_width=True,
        )

        if report and not pdf_bytes:
            st.info("PDF not available (import failed or builder returned empty). Check Debug tab.")

    with tabs[3]:
        st.subheader("Debug (temporary)")
        st.caption("Remove this tab after validation.")

        st.write("**Session keys:**", sorted(list(st.session_state.keys())))
        st.json(
            {
                "has_payload": bool(st.session_state.get("payload")),
                "has_report": bool(report),
                "has_pdf": bool(pdf_bytes),
                "has_error": bool(err),
            }
        )

        st.write("**Environment**")
        st.json(
            {
                "python": sys.version,
                "executable": sys.executable,
                "platform": platform.platform(),
                "cwd": os.getcwd(),
            }
        )
        st.write("**Repo/model paths**")
        st.json(
            {
                "repo_root": str(APP_ROOT),
                "repo_root_exists": APP_ROOT.exists(),
                "model_dir": str(MODEL_DIR),
                "model_dir_exists": MODEL_DIR.exists(),
                "artifacts": _artifact_checks(),
            }
        )

        st.write("**Import errors**")
        st.json(
            {
                "clinical_reporter_import_error": repr(CLINICAL_IMPORT_ERR) if CLINICAL_IMPORT_ERR else None,
                "pdf_import_error": repr(PDF_IMPORT_ERR) if PDF_IMPORT_ERR else None,
            }
        )


page()
