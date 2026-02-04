"""Request/response schemas for PEP 8 check API."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class CheckRequest(BaseModel):
    """Body for POST /api/check."""

    code: str = Field(..., min_length=1, description="Python source code to validate")


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


class CheckResponse(BaseModel):
    """Response from POST /api/check. Always 200; use ok/error for semantics. Revision metadata per PEP 8 change-detection spec."""

    ok: bool = Field(..., description="True if validation ran successfully")
    pep8_date: str = Field(..., description="PEP 8 revision date for UI")
    pep8_url: str = Field(..., description="Official PEP 8 source URL")
    pep8_revision: str = Field(..., description="Revision identifier for reports")
    issues: List[Issue] = Field(default_factory=list, description="Sorted by line, then column")
    error: Optional[str] = Field(None, description="Backend error message when ok is False")
