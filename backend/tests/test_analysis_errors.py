"""Unit tests for the error & exception semantics engine."""
from __future__ import annotations

import pytest

from app.analysis.errors import run_errors
from tests.conftest import assert_finding


class TestErrorsEdgeCases:
    """Edge cases: empty, invalid syntax, no exception handling."""

    def test_empty_string_returns_empty(self):
        assert run_errors("") == []

    def test_whitespace_only_returns_empty(self):
        assert run_errors("  \n\t ") == []

    def test_invalid_syntax_returns_empty(self):
        assert run_errors("try:") == []

    def test_no_try_except_returns_empty(self):
        code = """
def add(a, b):
    return a + b
"""
        assert run_errors(code) == []


class TestErrorsNegative:
    """Valid exception handling that should not trigger (or only expected) findings."""

    def test_specific_exception_with_handling(self):
        code = """
try:
    int("x")
except ValueError as e:
    log(e)
"""
        findings = run_errors(code)
        assert not any(f.rule_id == "errors.bare_except" for f in findings)
        assert not any(f.rule_id == "errors.caught_and_ignored" for f in findings)

    def test_exception_with_non_pass_body_no_silent_catch(self):
        code = """
try:
    foo()
except Exception:
    raise
"""
        findings = run_errors(code)
        silent = [f for f in findings if f.rule_id == "errors.silent_catch"]
        assert len(silent) == 0


class TestErrorsPositive:
    """Valid code that triggers error findings."""

    def test_bare_except_triggered(self):
        code = """
try:
    foo()
except:
    pass
"""
        findings = run_errors(code)
        bare = [f for f in findings if f.rule_id == "errors.bare_except"]
        assert len(bare) == 1
        assert_finding(bare[0], "errors", "errors.bare_except", title_substr="Bare")
        assert bare[0].severity == "warning"

    def test_exception_with_only_pass_caught_and_ignored(self):
        code = """
try:
    bar()
except Exception:
    pass
"""
        findings = run_errors(code)
        caught = [f for f in findings if f.rule_id == "errors.caught_and_ignored"]
        assert len(caught) >= 1
        assert_finding(caught[0], "errors", "errors.caught_and_ignored", title_substr="ignored")

    def test_silent_catch_triggered(self):
        code = """
try:
    x = 1
except ValueError:
    pass
"""
        findings = run_errors(code)
        silent = [f for f in findings if f.rule_id == "errors.silent_catch"]
        assert len(silent) == 1
        assert_finding(silent[0], "errors", "errors.silent_catch", title_substr="Silent")

    def test_bare_except_and_silent_both_possible(self):
        code = """
try:
    pass
except:
    pass
"""
        findings = run_errors(code)
        rule_ids = [f.rule_id for f in findings]
        assert "errors.bare_except" in rule_ids
        assert "errors.silent_catch" in rule_ids

    def test_domain_and_severity(self):
        code = "try:\n    pass\nexcept:\n    pass"
        findings = run_errors(code)
        assert len(findings) >= 1
        for f in findings:
            assert f.domain == "errors"
            assert f.severity in ("warning", "advisory")
