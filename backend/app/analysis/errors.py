"""Error & exception semantics. Raised but unhandled, caught and ignored, overly broad. Advisory/warning."""
from __future__ import annotations

import ast
from typing import List, Set

from app.schemas import Location, StaticAnalysisFinding


def _line(node: ast.AST) -> int:
    return getattr(node, "lineno", 1) or 1


def _handled_exception_types(tree: ast.AST) -> Set[str]:
    """Exception type names that appear in except handlers."""
    out: Set[str] = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.ExceptHandler):
            if n.type is None:
                out.add("BaseException")
                continue
            if isinstance(n.type, ast.Name):
                out.add(n.type.id)
            elif isinstance(n.type, ast.Tuple):
                for e in n.type.elts:
                    if isinstance(e, ast.Name):
                        out.add(e.id)
    return out


def run_errors(source: str) -> List[StaticAnalysisFinding]:
    """Exception handling: broad catch, silent ignore. Does not alter PEP 8/PYBP outputs."""
    if not source or not source.strip():
        return []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    findings: List[StaticAnalysisFinding] = []
    handled = _handled_exception_types(tree)
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            if node.type is None:
                findings.append(
                    StaticAnalysisFinding(
                        domain="errors",
                        rule_id="errors.bare_except",
                        title="Bare except clause",
                        location=Location(line=_line(node)),
                        severity="warning",
                        explanation="Bare except catches all exceptions including BaseException and system exits.",
                        suggestion="Catch a specific exception type or at least 'except Exception:'.",
                    )
                )
            elif isinstance(node.type, ast.Name) and node.type.id == "Exception":
                # Check if handler is effectively empty
                body = node.body
                if len(body) <= 1 and (not body or (isinstance(body[0], ast.Pass))):
                    findings.append(
                        StaticAnalysisFinding(
                            domain="errors",
                            rule_id="errors.caught_and_ignored",
                            title="Exception caught and ignored",
                            location=Location(line=_line(node)),
                            severity="warning",
                            explanation="Exception is caught but not logged or re-raised.",
                            suggestion="Log the exception or re-raise; avoid silent failure.",
                        )
                    )
            if node.body and len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                findings.append(
                    StaticAnalysisFinding(
                        domain="errors",
                        rule_id="errors.silent_catch",
                        title="Silent exception handler",
                        location=Location(line=_line(node)),
                        severity="advisory",
                        explanation="Handler body is only pass; exceptions are swallowed.",
                        suggestion="At least log; consider re-raising or handling specifically.",
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
