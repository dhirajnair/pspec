"""Unit tests for the data-flow analysis engine."""
from __future__ import annotations

import pytest

from app.analysis.dataflow import run_dataflow
from tests.conftest import assert_finding


class TestDataflowEdgeCases:
    """Edge cases: empty, invalid syntax, no shadowing."""

    def test_empty_string_returns_empty(self):
        assert run_dataflow("") == []

    def test_whitespace_only_returns_empty(self):
        assert run_dataflow("   \n  ") == []

    def test_invalid_syntax_returns_empty(self):
        assert run_dataflow("def (") == []

    def test_module_with_only_functions_no_module_assigns(self):
        code = """
def foo():
    x = 1
    return x
"""
        assert run_dataflow(code) == []


class TestDataflowNegative:
    """Valid code without shadowing."""

    def test_only_module_level_assigns(self):
        code = """
a = 1
b = 2
"""
        assert run_dataflow(code) == []

    def test_function_assigns_different_names_than_module(self):
        code = """
count = 0
def inc():
    n = count + 1
    return n
"""
        assert run_dataflow(code) == []

    def test_nested_function_different_names(self):
        code = """
x = 1
def outer():
    y = 2
    def inner():
        z = 3
        return z
    return y
"""


class TestDataflowPositive:
    """Valid code that triggers shadowing."""

    def test_shadowing_module_var_inside_function(self):
        code = """
name = "global"
def greet():
    name = "local"
    return name
"""
        findings = run_dataflow(code)
        assert len(findings) >= 1
        shadow = [f for f in findings if f.rule_id == "dataflow.shadowing"]
        assert len(shadow) == 1
        assert_finding(shadow[0], "dataflow", "dataflow.shadowing", line=4, title_substr="shadowing")
        assert "name" in shadow[0].explanation

    def test_shadowing_multiple_module_names(self):
        code = """
a = 1
b = 2
def f():
    a = 10
    b = 20
    return a + b
"""
        findings = run_dataflow(code)
        shadow = [f for f in findings if f.rule_id == "dataflow.shadowing"]
        assert len(shadow) == 2
        lines = [f.location.line for f in shadow]
        assert 5 in lines and 6 in lines

    def test_domain_and_severity(self):
        code = """
x = 0
def f():
    x = 1
    return x
"""
        findings = run_dataflow(code)
        assert len(findings) == 1
        assert findings[0].domain == "dataflow"
        assert findings[0].severity == "advisory"
        assert findings[0].location.function == "f"
