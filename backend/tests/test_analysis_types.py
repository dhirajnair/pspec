"""Unit tests for the type semantics analysis engine."""
from __future__ import annotations

import pytest

from app.analysis.types import run_types
from tests.conftest import assert_finding


class TestTypesEdgeCases:
    """Edge cases: empty, whitespace, invalid syntax."""

    def test_empty_string_returns_empty(self):
        assert run_types("") == []

    def test_whitespace_only_returns_empty(self):
        assert run_types("   \n\t  ") == []

    def test_invalid_syntax_returns_empty(self):
        assert run_types("def foo(  ") == []
        assert run_types("if 1 2 3") == []
        assert run_types("'''unclosed") == []

    def test_only_comments_returns_empty(self):
        assert run_types("# comment only") == []


class TestTypesNegative:
    """Valid code that must not produce type findings."""

    def test_no_annotations_no_findings(self):
        code = """
def add(a, b):
    return a + b
"""
        assert run_types(code) == []

    def test_concrete_annotations_no_findings(self):
        code = """
def greet(name: str) -> str:
    return f"Hello {name}"
"""
        assert run_types(code) == []

    def test_optional_annotation_no_any(self):
        code = """
from typing import Optional
def f(x: Optional[int]) -> int:
    return x or 0
"""
        assert run_types(code) == []

    def test_multiple_concrete_params(self):
        code = """
def process(items: list[str], count: int) -> bool:
    return len(items) == count
"""
        assert run_types(code) == []


class TestTypesPositive:
    """Valid code that must trigger type findings."""

    def test_return_any_triggered(self):
        code = """
from typing import Any
def get_data() -> Any:
    return {}
"""
        findings = run_types(code)
        assert len(findings) >= 1
        return_any = [f for f in findings if f.rule_id == "types.return_any"]
        assert len(return_any) == 1
        assert_finding(return_any[0], "types", "types.return_any", title_substr="Any")

    def test_param_any_triggered(self):
        code = """
from typing import Any
def handle(value: Any) -> str:
    return str(value)
"""
        findings = run_types(code)
        assert len(findings) >= 1
        param_any = [f for f in findings if f.rule_id == "types.param_any"]
        assert len(param_any) == 1
        assert_finding(param_any[0], "types", "types.param_any", title_substr="Any")

    def test_both_return_and_param_any(self):
        code = """
from typing import Any
def transform(x: Any) -> Any:
    return x
"""
        findings = run_types(code)
        rule_ids = [f.rule_id for f in findings]
        assert "types.return_any" in rule_ids
        assert "types.param_any" in rule_ids
        assert len(findings) == 2

    def test_multiple_params_any_each_reported(self):
        code = """
from typing import Any
def f(a: Any, b: Any) -> None:
    pass
"""
        findings = run_types(code)
        param_any = [f for f in findings if f.rule_id == "types.param_any"]
        # Dedupe is by (rule_id, line); both params on same line => 1 finding
        assert len(param_any) >= 1
        assert any("Any" in f.title or "Parameter" in f.title for f in param_any)

    def test_domain_and_severity(self):
        code = "def f(x: Any) -> None: pass"
        findings = run_types(code)
        assert len(findings) >= 1
        for f in findings:
            assert f.domain == "types"
            assert f.severity == "advisory"
            assert f.location.line >= 1
