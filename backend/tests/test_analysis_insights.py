"""Unit tests for the insight synthesis engine."""
from __future__ import annotations

import pytest

from app.schemas import Location, StaticAnalysisFinding
from app.analysis.insights import run_insights
from tests.conftest import assert_finding


def _finding(domain: str, rule_id: str, explanation: str = "") -> StaticAnalysisFinding:
    return StaticAnalysisFinding(
        domain=domain,
        rule_id=rule_id,
        title="Test",
        location=Location(line=1),
        severity="advisory",
        explanation=explanation or "Test",
        suggestion="Test",
    )


class TestInsightsEdgeCases:
    """Edge cases: no findings, empty list."""

    def test_empty_findings_returns_empty(self):
        assert run_insights("code", []) == []

    def test_single_finding_no_synthesis_rule_applies(self):
        findings = [_finding("types", "types.param_any")]
        assert run_insights("code", findings) == []

    def test_one_security_finding_no_elevated_risk(self):
        findings = [_finding("security", "security.dangerous_eval")]
        result = run_insights("code", findings)
        elevated = [f for f in result if f.rule_id == "insights.elevated_risk"]
        assert len(elevated) == 0


class TestInsightsPositive:
    """Findings that trigger insight synthesis."""

    def test_two_security_findings_elevated_risk(self):
        findings = [
            _finding("security", "security.dangerous_eval"),
            _finding("security", "security.unsafe_deserialization"),
        ]
        result = run_insights("code", findings)
        elevated = [f for f in result if f.rule_id == "insights.elevated_risk"]
        assert len(elevated) == 1
        assert_finding(elevated[0], "insights", "insights.elevated_risk", title_substr="risk")
        assert "2" in elevated[0].explanation or "Multiple" in elevated[0].explanation

    def test_three_security_findings_still_one_elevated_risk(self):
        findings = [
            _finding("security", "a"),
            _finding("security", "b"),
            _finding("security", "c"),
        ]
        result = run_insights("code", findings)
        elevated = [f for f in result if f.rule_id == "insights.elevated_risk"]
        assert len(elevated) == 1
        assert "3" in elevated[0].explanation

    def test_metrics_with_complexity_and_nesting_triggers_complexity_context(self):
        findings = [
            _finding(
                "metrics",
                "metrics.complexity",
                explanation="Cyclomatic complexity: 5; max nesting depth: 3. Reported for review.",
            ),
        ]
        result = run_insights("code", findings)
        complexity_insight = [f for f in result if f.rule_id == "insights.complexity_context"]
        assert len(complexity_insight) == 1
        assert_finding(complexity_insight[0], "insights", "insights.complexity_context", title_substr="Complexity")

    def test_metrics_without_nesting_depth_text_no_complexity_insight(self):
        findings = [
            _finding("metrics", "metrics.complexity", explanation="Only cyclo."),
        ]
        result = run_insights("code", findings)
        complexity_insight = [f for f in result if f.rule_id == "insights.complexity_context"]
        assert len(complexity_insight) == 0

    def test_both_elevated_risk_and_complexity_context_can_appear(self):
        findings = [
            _finding("security", "a"),
            _finding("security", "b"),
            _finding(
                "metrics",
                "metrics.complexity",
                explanation="Cyclomatic complexity: 10; max nesting depth: 4. Reported.",
            ),
        ]
        result = run_insights("code", findings)
        rule_ids = [f.rule_id for f in result]
        assert "insights.elevated_risk" in rule_ids
        assert "insights.complexity_context" in rule_ids

    def test_insights_domain_and_severity(self):
        findings = [
            _finding("security", "a"),
            _finding("security", "b"),
        ]
        result = run_insights("code", findings)
        for f in result:
            assert f.domain == "insights"
            assert f.severity == "advisory"
            assert f.location.line == 1
