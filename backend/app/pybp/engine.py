"""PYBP engine: runs AST-based rules on source, returns advisories. Does not modify PEP 8."""
from __future__ import annotations

import ast
from typing import List

from app.schemas import PybpAdvisory
from app.pybp.rules import PybpRule, SEVERITIES


def run_pybp(source: str, rules: List[PybpRule]) -> List[PybpAdvisory]:
    """
    Run PYBP rules on source. Same input as PEP 8; independent result set.
    Returns advisories only (severity in info/advisory/warning). No errors.
    """
    if not source or not source.strip():
        return []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    if not rules:
        return []
    advisories: List[PybpAdvisory] = []
    for rule in rules:
        for node in ast.walk(tree):
            for item in rule.check(node, source):
                if not isinstance(item, dict) or rule.severity not in SEVERITIES:
                    continue
                advisories.append(
                    PybpAdvisory(
                        rule_id=rule.rule_id,
                        title=rule.title,
                        category=rule.category,
                        line=item.get("line", 1),
                        function=item.get("function"),
                        class_name=item.get("class_name"),
                        explanation=item.get("explanation", rule.description),
                        authority=rule.authority,
                        citation=rule.citation,
                        suggestion=item.get("suggestion", rule.suggestion),
                        severity=rule.severity,
                    )
                )
    # Dedupe by (rule_id, line); sort by line
    seen: set[tuple[str, int]] = set()
    unique = []
    for a in sorted(advisories, key=lambda x: (x.line, x.rule_id)):
        key = (a.rule_id, a.line)
        if key not in seen:
            seen.add(key)
            unique.append(a)
    return unique
