"""Advanced static analysis engines. Additive only; no coupling to PEP 8 or PYBP."""
from __future__ import annotations

from app.analysis.types import run_types
from app.analysis.dataflow import run_dataflow
from app.analysis.errors import run_errors
from app.analysis.security import run_security
from app.analysis.metrics import run_metrics
from app.analysis.insights import run_insights

__all__ = ["run_types", "run_dataflow", "run_errors", "run_security", "run_metrics", "run_insights"]
