"""Type semantics analysis. Lightweight, snippet-safe type awareness. Advisory/warning only."""
from __future__ import annotations

import ast
from typing import List

from app.schemas import Location, StaticAnalysisFinding


def _line(node: ast.AST) -> int:
    return getattr(node, "lineno", 1) or 1


def _check_any_usage(tree: ast.AST) -> List[StaticAnalysisFinding]:
    """Excessive or unsafe use of Any. AST: look for ast.Name(id='Any') in annotations."""
    findings: List[StaticAnalysisFinding] = []
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef) and n.returns is not None:
            if isinstance(n.returns, ast.Name) and n.returns.id == "Any":
                findings.append(
                    StaticAnalysisFinding(
                        domain="types",
                        rule_id="types.return_any",
                        title="Return type is Any",
                        location=Location(line=_line(n), function=n.name),
                        severity="advisory",
                        explanation="Return type annotated as Any loses type safety and intent.",
                        suggestion="Use a concrete return type where possible.",
                    )
                )
        if isinstance(n, ast.arg) and n.annotation is not None:
            if isinstance(n.annotation, ast.Name) and n.annotation.id == "Any":
                findings.append(
                    StaticAnalysisFinding(
                        domain="types",
                        rule_id="types.param_any",
                        title="Parameter typed as Any",
                        location=Location(line=_line(n)),
                        severity="advisory",
                        explanation="Parameter annotated as Any reduces type checking benefit.",
                        suggestion="Use a more specific type if possible.",
                    )
                )
    return findings


def run_types(source: str) -> List[StaticAnalysisFinding]:
    """Run type semantics checks. No mypy; no external stubs. Advisory/warning only."""
    if not source or not source.strip():
        return []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    findings: List[StaticAnalysisFinding] = []
    findings.extend(_check_any_usage(tree))
    seen: set[tuple[str, int]] = set()
    unique = []
    for f in sorted(findings, key=lambda x: (x.location.line, x.rule_id)):
        key = (f.rule_id, f.location.line)
        if key not in seen:
            seen.add(key)
            unique.append(f)
    return unique
