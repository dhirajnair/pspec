"""Request/response schemas for PEP 8 check API and PYBP extension."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class CheckRequest(BaseModel):
    """Body for POST /api/check."""

    code: str = Field(..., min_length=1, description="Python source code to validate")
    pybp_enabled: bool = Field(True, description="Include Best Practice (PYBP) advisories when True")


class Issue(BaseModel):
    """A single PEP 8 violation. Rule mapping layer: code → PEP 8 section + quote."""

    code: str = Field(..., description="Rule/detection code e.g. E302, W291")
    message: str = Field(..., description="Short description")
    line: int = Field(..., ge=1, description="1-based line number")
    column: Optional[int] = Field(None, ge=0, description="0-based column if applicable")
    pep8_quote: str = Field(..., description="Verbatim or near-verbatim PEP 8 text")
    pep8_section: str = Field(..., description="Section title or reference")
    pep8_section_url: Optional[str] = Field(None, description="Canonical PEP 8 section URL fragment")
    suggestion: str = Field(..., description="How to fix")


class PybpAdvisory(BaseModel):
    """A single PYBP best-practice advisory. Advisory only; never an error."""

    rule_id: str = Field(..., description="Stable namespaced rule id e.g. pybp.func.length")
    title: str = Field(..., description="Concise rule title")
    category: str = Field(..., description="PYBP category e.g. Function Design")
    line: int = Field(..., ge=1, description="1-based line number")
    function: Optional[str] = Field(None, description="Function name if applicable")
    class_name: Optional[str] = Field(None, description="Class name if applicable")
    explanation: str = Field(..., description="What is observed")
    authority: str = Field(..., description="Source e.g. Clean Code, Python Docs")
    citation: str = Field(..., description="Chapter, URL, or section")
    suggestion: str = Field(..., description="Non-prescriptive improvement guidance")
    severity: str = Field(..., description="One of: info, advisory, warning")


class Location(BaseModel):
    """Location of a static analysis finding."""

    line: int = Field(..., ge=1, description="1-based line number")
    column: Optional[int] = Field(None, ge=0)
    function: Optional[str] = None
    class_name: Optional[str] = None


class StaticAnalysisFinding(BaseModel):
    """Single finding from advanced static analysis (types, dataflow, errors, security, metrics, insights)."""

    domain: str = Field(..., description="Analysis domain e.g. types, dataflow, security")
    rule_id: str = Field(..., description="Stable rule id")
    title: str = Field(..., description="Short title")
    location: Location = Field(..., description="Where the finding applies")
    severity: str = Field(..., description="violation | warning | advisory")
    explanation: str = Field(..., description="What is observed")
    suggestion: str = Field(..., description="How to improve")


class CheckResponse(BaseModel):
    """Response from POST /api/check. PEP 8 issues + optional PYBP advisories + optional static analysis findings."""

    ok: bool = Field(..., description="True if validation ran successfully")
    pep8_date: str = Field(..., description="PEP 8 revision date for UI")
    pep8_url: str = Field(..., description="Official PEP 8 source URL")
    pep8_revision: str = Field(..., description="Revision identifier for reports")
    issues: List[Issue] = Field(default_factory=list, description="PEP 8 violations, sorted by line, then column")
    advisories: List[PybpAdvisory] = Field(default_factory=list, description="PYBP best-practice advisories when requested")
    findings: List[StaticAnalysisFinding] = Field(
        default_factory=list,
        description="Advanced static analysis findings (types, dataflow, errors, security, metrics, insights), ordered by domain authority",
    )
    error: Optional[str] = Field(None, description="Backend error message when ok is False")
