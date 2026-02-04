"""Metrics & complexity analysis. Reported, not enforced. Cyclomatic, cognitive, nesting, statement count."""
from __future__ import annotations

import ast
from typing import List

from app.schemas import Location, StaticAnalysisFinding


def _line(node: ast.AST) -> int:
    return getattr(node, "lineno", 1) or 1


def _cyclomatic(node: ast.AST) -> int:
    """Cyclomatic complexity: 1 + decision points."""
    total = 1
    for n in ast.walk(node):
        if isinstance(n, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
            total += 1
        elif isinstance(n, ast.BoolOp):
            total += len(n.values) - 1
        elif isinstance(n, ast.comprehension):
            total += 1
            total += len(n.ifs or [])
    return total


def _nesting_depth(node: ast.AST) -> int:
    """Max nesting depth under this node (if/for/while/with/try)."""
    if isinstance(node, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
        child_max = 0
        for c in ast.iter_child_nodes(node):
            child_max = max(child_max, _nesting_depth(c))
        return 1 + child_max
    return max((_nesting_depth(c) for c in ast.iter_child_nodes(node)), default=0)


def run_metrics(source: str) -> List[StaticAnalysisFinding]:
    """Report cyclomatic complexity and nesting depth per function. Report only, not enforced."""
    if not source or not source.strip():
        return []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    findings: List[StaticAnalysisFinding] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            cyclo = _cyclomatic(node)
            depth = 0
            for n in ast.walk(node):
                if isinstance(n, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                    d = _nesting_depth(n)
                    if d > depth:
                        depth = d
            findings.append(
                StaticAnalysisFinding(
                    domain="metrics",
                    rule_id="metrics.complexity",
                    title="Function complexity metrics",
                    location=Location(line=_line(node), function=node.name),
                    severity="advisory",
                    explanation=f"Cyclomatic complexity: {cyclo}; max nesting depth: {depth}. Reported for review.",
                    suggestion="High values may indicate need for simplification or extraction.",
                )
            )
    return findings
