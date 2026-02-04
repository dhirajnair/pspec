"""Integration tests: all engines together, ordering, and API contract."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.analysis import run_types, run_dataflow, run_errors, run_security, run_metrics, run_insights
from app.main import app


class TestAllEnginesTogether:
    """Run all engines on same source; assert no cross-talk and ordering."""

    def test_single_source_triggers_multiple_engines(self):
        code = """
from typing import Any
name = "global"
def f(x: Any) -> Any:
    name = "local"
    try:
        eval("x")
    except:
        pass
    return x
"""
        types_f = run_types(code)
        dataflow_f = run_dataflow(code)
        errors_f = run_errors(code)
        security_f = run_security(code)
        metrics_f = run_metrics(code)
        all_before_insights = types_f + dataflow_f + errors_f + security_f + metrics_f
        insights_f = run_insights(code, all_before_insights)

        assert len(types_f) >= 2
        assert len(dataflow_f) >= 1
        assert len(errors_f) >= 1
        assert len(security_f) >= 1
        assert len(metrics_f) >= 1
        assert len(insights_f) >= 1

        domains = [f.domain for f in types_f + dataflow_f + errors_f + security_f + metrics_f + insights_f]
        assert "types" in domains
        assert "dataflow" in domains
        assert "errors" in domains
        assert "security" in domains
        assert "metrics" in domains
        assert "insights" in domains

    def test_findings_have_required_schema_fields(self):
        code = "def g() -> None: pass"
        metrics_f = run_metrics(code)
        assert len(metrics_f) == 1
        f = metrics_f[0]
        assert hasattr(f, "domain") and f.domain
        assert hasattr(f, "rule_id") and f.rule_id
        assert hasattr(f, "title") and f.title
        assert hasattr(f, "location") and f.location.line >= 1
        assert hasattr(f, "severity") and f.severity
        assert hasattr(f, "explanation") and f.explanation
        assert hasattr(f, "suggestion") and f.suggestion

    def test_clean_code_produces_only_metrics_among_new_engines(self):
        code = """
def add(a: int, b: int) -> int:
    return a + b
"""
        types_f = run_types(code)
        dataflow_f = run_dataflow(code)
        errors_f = run_errors(code)
        security_f = run_security(code)
        metrics_f = run_metrics(code)
        assert len(types_f) == 0
        assert len(dataflow_f) == 0
        assert len(errors_f) == 0
        assert len(security_f) == 0
        assert len(metrics_f) == 1


class TestApiCheckWithFindings:
    """POST /api/check returns findings when advanced is enabled."""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_check_returns_findings_key(self, client):
        r = client.post("/api/check", json={"code": "x = 1"})
        assert r.status_code == 200
        data = r.json()
        assert "findings" in data
        assert isinstance(data["findings"], list)

    def test_check_with_dangerous_code_returns_findings(self, client):
        r = client.post(
            "/api/check",
            json={
                "code": "eval('1')\npassword = 'x'",
                "pybp_enabled": False,
                "enable_types": True,
                "enable_security": True,
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert data["ok"] is True
        findings = data["findings"]
        security = [f for f in findings if f.get("domain") == "security"]
        assert len(security) >= 2

    def test_check_with_advanced_disabled_returns_empty_findings(self, client):
        r = client.post(
            "/api/check",
            json={
                "code": "eval('1')\nname = 'x'\ndef f():\n    name = 'y'",
                "enable_types": False,
                "enable_dataflow": False,
                "enable_errors": False,
                "enable_security": False,
                "enable_metrics": False,
                "enable_insights": False,
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert data["findings"] == []

    def test_check_finding_schema(self, client):
        r = client.post(
            "/api/check",
            json={"code": "def foo(): return 1"},
        )
        assert r.status_code == 200
        data = r.json()
        findings = data["findings"]
        metrics = [f for f in findings if f.get("domain") == "metrics"]
        if metrics:
            m = metrics[0]
            assert "domain" in m
            assert "rule_id" in m
            assert "title" in m
            assert "location" in m and "line" in m["location"]
            assert "severity" in m
            assert "explanation" in m
            assert "suggestion" in m


class TestRegressionGuards:
    """Regression: engines must not break on real-world snippets."""

    def test_async_function(self):
        code = "async def fetch(): return 1"
        assert run_metrics(code)
        assert run_types(code) == []

    def test_class_with_methods(self):
        code = """
class C:
    def __init__(self):
        pass
    def m(self) -> int:
        return 0
"""
        assert run_metrics(code)
        assert run_types(code) == []

    def test_comprehensions(self):
        code = "squares = [x*x for x in range(10)]"
        assert run_dataflow(code) == []
        assert run_metrics(code) == []

    def test_with_statement(self):
        code = """
def use_file():
    with open("x") as f:
        return f.read()
"""
        findings = run_metrics(code)
        assert len(findings) == 1

    def test_multiline_string(self):
        code = 'x = """\nline2\n"""'
        assert run_security(code) == []

    def test_try_except_else_finally(self):
        code = """
try:
    a = 1
except ValueError:
    pass
else:
    b = 2
finally:
    c = 3
"""
        run_errors(code)
