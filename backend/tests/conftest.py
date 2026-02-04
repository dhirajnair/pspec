"""Shared pytest fixtures and helpers for analysis engine tests."""
from __future__ import annotations

from typing import Optional


def assert_finding(finding, domain: str, rule_id: str, line: Optional[int] = None, title_substr: Optional[str] = None):
    """Assert a finding has expected domain, rule_id, and optionally line/title."""
    assert finding.domain == domain, f"expected domain {domain!r}, got {finding.domain!r}"
    assert finding.rule_id == rule_id, f"expected rule_id {rule_id!r}, got {finding.rule_id!r}"
    if line is not None:
        assert finding.location.line == line, f"expected line {line}, got {finding.location.line}"
    if title_substr is not None:
        assert title_substr in finding.title, f"expected {title_substr!r} in title {finding.title!r}"
    assert finding.explanation
    assert finding.suggestion
    assert finding.severity
