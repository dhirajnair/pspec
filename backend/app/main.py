"""PEP 8 Compliance Checker API. Stateless; no execution of user code."""
from __future__ import annotations

from typing import List, Tuple

import pycodestyle
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.pep8_map import get_pep8_info
from app.schemas import CheckResponse, Issue, StaticAnalysisFinding
from app.pybp.engine import run_pybp
from app.pybp.checks import PYBP_RULES
from app.analysis import (
    run_types,
    run_dataflow,
    run_errors,
    run_security,
    run_metrics,
    run_insights,
)


class CollectingReport(pycodestyle.BaseReport):
    """Report that collects (line_number, offset, code, text) for API response."""

    def init_file(self, filename, lines, expected, line_offset):
        super().init_file(filename, lines, expected, line_offset)
        self._errors: List[Tuple[int, int, str, str]] = []

    def error(self, line_number, offset, text, check):
        code = super().error(line_number, offset, text, check)
        if code:
            # text is "E302 expected 2 blank lines..."; code is "E302"
            self._errors.append((line_number, offset, code, text[5:].strip()))
        return code

    def get_file_results(self):
        return self._errors

app = FastAPI(
    title="PEP 8 Compliance Checker API",
    description="Validate Python code against PEP 8. No execution of user code.",
    version="0.1.0",
)
settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


@app.post(
    "/api/check",
    response_model=CheckResponse,
    responses={200: {"description": "Always 200; see body ok/error and issues."}},
)
async def check_pep8(request: Request) -> CheckResponse:
    """
    Validate request body code against PEP 8. Returns issues with PEP 8 quote and suggestion.
    No code execution; static analysis only.
    """
    def err_res(msg: str) -> CheckResponse:
        return CheckResponse(
            ok=False,
            pep8_date=settings.pep8_date,
            pep8_url=settings.pep8_url,
            pep8_revision=settings.pep8_revision,
            issues=[],
            advisories=[],
            findings=[],
            error=msg,
        )
    try:
        body = await request.json()
    except Exception as e:
        return err_res(f"Invalid JSON: {e!s}")
    code = body.get("code") if isinstance(body, dict) else None
    if not isinstance(code, str):
        return err_res("Missing or invalid 'code' field (must be a string).")
    if len(code.encode("utf-8")) > settings.max_code_length:
        return err_res(f"Code exceeds maximum length ({settings.max_code_length} bytes).")
    enable_pep8 = body.get("enable_pep8", settings.enable_pep8) if isinstance(body, dict) else settings.enable_pep8
    enable_pybp = body.get("enable_pybp", body.get("pybp_enabled", settings.enable_pybp)) if isinstance(body, dict) else settings.enable_pybp
    issues = _run_pycodestyle(code) if enable_pep8 else []
    advisories = run_pybp(code, PYBP_RULES) if (isinstance(enable_pybp, bool) and enable_pybp) else []
    findings: List[StaticAnalysisFinding] = []
    if isinstance(body, dict):
        enable_types = body.get("enable_types", settings.enable_types)
        enable_dataflow = body.get("enable_dataflow", settings.enable_dataflow)
        enable_errors = body.get("enable_errors", settings.enable_errors)
        enable_security = body.get("enable_security", settings.enable_security)
        enable_metrics = body.get("enable_metrics", settings.enable_metrics)
        enable_insights = body.get("enable_insights", settings.enable_insights)
    else:
        enable_types = settings.enable_types
        enable_dataflow = settings.enable_dataflow
        enable_errors = settings.enable_errors
        enable_security = settings.enable_security
        enable_metrics = settings.enable_metrics
        enable_insights = settings.enable_insights
    if enable_types:
        findings.extend(run_types(code))
    if enable_dataflow:
        findings.extend(run_dataflow(code))
    if enable_errors:
        findings.extend(run_errors(code))
    if enable_security:
        findings.extend(run_security(code))
    if enable_metrics:
        findings.extend(run_metrics(code))
    if enable_insights:
        findings.extend(run_insights(code, findings))
    return CheckResponse(
        ok=True,
        pep8_date=settings.pep8_date,
        pep8_url=settings.pep8_url,
        pep8_revision=settings.pep8_revision,
        issues=issues,
        advisories=advisories,
        findings=findings,
        error=None,
    )


def _run_pycodestyle(source: str) -> List[Issue]:
    """Run pycodestyle on source string. No file I/O, no execution."""
    lines = source.splitlines(keepends=True)
    if not lines:
        return []
    # Merge pycodestyle default ignore with config (so we add suppressions, not replace).
    default_ignore = getattr(pycodestyle, "DEFAULT_IGNORE", "") or ""
    base_list = [c.strip() for c in default_ignore.split(",") if c.strip()]
    ignore_list = base_list + settings.pep8_ignore_list
    style = pycodestyle.StyleGuide(quiet=True, ignore=ignore_list)
    report = CollectingReport(style.options)
    checker = pycodestyle.Checker(
        lines=lines,
        filename="<paste>",
        options=style.options,
        report=report,
    )
    checker.check_all()
    result: List[Issue] = []
    for line_number, offset, code, text in report.get_file_results():
        pep8_quote, pep8_section, suggestion, section_frag = get_pep8_info(code, text)
        pep8_section_url = f"{settings.pep8_url}#{section_frag}" if section_frag else None
        result.append(
            Issue(
                code=code,
                message=text,
                line=line_number,
                column=offset if offset else None,
                pep8_quote=pep8_quote,
                pep8_section=pep8_section,
                pep8_section_url=pep8_section_url,
                suggestion=suggestion,
            )
        )
    result.sort(key=lambda i: (i.line, i.column or 0))
    return result


@app.get("/")
def root():
    """Health/root; frontend is served separately."""
    return {"service": "pep8-checker-api", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
