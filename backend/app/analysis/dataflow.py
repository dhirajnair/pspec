"""Data-flow analysis. Snippet-local only; shadowing. No inter-procedural."""
from __future__ import annotations

import ast
from typing import List, Set

from app.schemas import Location, StaticAnalysisFinding


def _line(node: ast.AST) -> int:
    return getattr(node, "lineno", 1) or 1


def run_dataflow(source: str) -> List[StaticAnalysisFinding]:
    """Snippet-local data-flow: variable shadowing (inner scope redefining outer)."""
    if not source or not source.strip():
        return []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    findings: List[StaticAnalysisFinding] = []
    module_names: Set[str] = set()
    for stmt in tree.body:
        if isinstance(stmt, ast.Assign):
            for t in stmt.targets:
                if isinstance(t, ast.Name):
                    module_names.add(t.id)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for n in ast.walk(node):
                if isinstance(n, ast.Assign):
                    for t in n.targets:
                        if isinstance(t, ast.Name) and t.id in module_names:
                            findings.append(
                                StaticAnalysisFinding(
                                    domain="dataflow",
                                    rule_id="dataflow.shadowing",
                                    title="Variable shadowing",
                                    location=Location(line=_line(n), function=node.name),
                                    severity="advisory",
                                    explanation=f"'{t.id}' shadows a name from module scope.",
                                    suggestion="Rename the inner variable to avoid confusion.",
                                )
                            )
    seen: set[tuple[str, int]] = set()
    unique = []
    for f in sorted(findings, key=lambda x: (x.location.line, x.rule_id)):
        key = (f.rule_id, f.location.line)
        if key not in seen:
            seen.add(key)
            unique.append(f)
    return unique
