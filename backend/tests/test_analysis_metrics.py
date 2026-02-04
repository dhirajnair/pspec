"""Unit tests for the metrics & complexity analysis engine."""
from __future__ import annotations

import pytest

from app.analysis.metrics import run_metrics
from tests.conftest import assert_finding


class TestMetricsEdgeCases:
    """Edge cases: empty, invalid syntax, module with no functions."""

    def test_empty_string_returns_empty(self):
        assert run_metrics("") == []

    def test_whitespace_only_returns_empty(self):
        assert run_metrics("  \n ") == []

    def test_invalid_syntax_returns_empty(self):
        assert run_metrics("def (") == []

    def test_module_level_only_no_functions_returns_empty(self):
        code = """
x = 1
y = 2
"""
        assert run_metrics(code) == []


class TestMetricsNegative:
    """Code that produces metrics but no failures (metrics are report-only)."""

    def test_simple_function_has_one_metric_finding(self):
        code = """
def identity(x):
    return x
"""
        findings = run_metrics(code)
        assert len(findings) == 1
        assert findings[0].rule_id == "metrics.complexity"
        assert "Cyclomatic" in findings[0].explanation
        assert "nesting" in findings[0].explanation.lower()

    def test_zero_complexity_still_reported(self):
        code = "def no_branches(): return 42"
        findings = run_metrics(code)
        assert len(findings) == 1
        assert findings[0].domain == "metrics"
        assert findings[0].location.function == "no_branches"


class TestMetricsPositive:
    """Code that produces metrics findings with varying complexity."""

    def test_every_function_gets_metric_finding(self):
        code = """
def a():
    return 1
def b():
    return 2
"""
        findings = run_metrics(code)
        assert len(findings) == 2
        funcs = {f.location.function for f in findings}
        assert funcs == {"a", "b"}

    def test_cyclomatic_complexity_reflected(self):
        code = """
def branchy(x):
    if x > 0:
        pass
    if x < 0:
        pass
    for i in range(3):
        pass
    return x
"""
        findings = run_metrics(code)
        assert len(findings) == 1
        assert "Cyclomatic" in findings[0].explanation and "complexity" in findings[0].explanation
        assert "nesting" in findings[0].explanation.lower()

    def test_nesting_depth_reflected(self):
        code = """
def deep():
    if True:
        if True:
            if True:
                if True:
                    pass
    return 1
"""
        findings = run_metrics(code)
        assert len(findings) == 1
        assert "nesting" in findings[0].explanation.lower()
        assert "depth" in findings[0].explanation.lower()

    def test_class_methods_each_reported(self):
        code = """
class C:
    def m1(self):
        return 1
    def m2(self):
        return 2
"""
        findings = run_metrics(code)
        assert len(findings) == 2
        assert all(f.rule_id == "metrics.complexity" for f in findings)

    def test_domain_severity_and_location(self):
        code = "def foo(): return 1"
        findings = run_metrics(code)
        assert len(findings) == 1
        f = findings[0]
        assert f.domain == "metrics"
        assert f.severity == "advisory"
        assert f.location.line >= 1
        assert f.location.function == "foo"
