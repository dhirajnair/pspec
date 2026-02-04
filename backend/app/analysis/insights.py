"""Insight synthesis. Combine findings into high-level reviewer insights. Deterministic; never suppress."""
from __future__ import annotations

from typing import List

from app.schemas import Location, StaticAnalysisFinding


def run_insights(
    _source: str,
    findings_so_far: List[StaticAnalysisFinding],
) -> List[StaticAnalysisFinding]:
    """
    Synthesize high-level insights from existing findings. Does not suppress any finding.
    E.g. repeated security signals → elevated risk; large + complex + nested → multiple responsibilities.
    """
    insights: List[StaticAnalysisFinding] = []
    security_count = sum(1 for f in findings_so_far if f.domain == "security")
    if security_count >= 2:
        insights.append(
            StaticAnalysisFinding(
                domain="insights",
                rule_id="insights.elevated_risk",
                title="Elevated risk profile",
                location=Location(line=1),
                severity="advisory",
                explanation=f"Multiple security signals ({security_count}) in snippet; consider focused review.",
                suggestion="Address security findings and re-run analysis.",
            )
        )
    metrics_findings = [f for f in findings_so_far if f.domain == "metrics"]
    if metrics_findings and "nesting depth" in metrics_findings[0].explanation and "Cyclomatic" in metrics_findings[0].explanation:
        insights.append(
            StaticAnalysisFinding(
                domain="insights",
                rule_id="insights.complexity_context",
                title="Complexity context",
                location=Location(line=1),
                severity="advisory",
                explanation="Metrics indicate non-trivial complexity; function may have multiple responsibilities.",
                suggestion="Consider splitting or simplifying; use metrics to prioritize review.",
            )
        )
    return insights
