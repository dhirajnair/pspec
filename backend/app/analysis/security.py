"""Security & misuse signals. eval/exec, pickle, shell, hardcoded credentials. Advisory only; labeled."""
from __future__ import annotations

import ast
import re
from typing import List

from app.schemas import Location, StaticAnalysisFinding


def _line(node: ast.AST) -> int:
    return getattr(node, "lineno", 1) or 1


# Pattern-based credential hints (advisory only)
CREDENTIAL_PATTERNS = [
    (re.compile(r"(?i)(password|passwd|pwd)\s*=\s*['\"][^'\"]+['\"]"), "Hard-coded password"),
    (re.compile(r"(?i)(api[_-]?key|apikey)\s*=\s*['\"][^'\"]+['\"]"), "Hard-coded API key"),
    (re.compile(r"(?i)(secret)\s*=\s*['\"][^'\"]+['\"]"), "Hard-coded secret"),
]


def run_security(source: str) -> List[StaticAnalysisFinding]:
    """Basic security smells: eval/exec, pickle, shell, hardcoded credentials. Advisory only."""
    if not source or not source.strip():
        return []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    findings: List[StaticAnalysisFinding] = []
    lines = source.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                if func.id in ("eval", "exec"):
                    findings.append(
                        StaticAnalysisFinding(
                            domain="security",
                            rule_id="security.dangerous_eval",
                            title="Use of eval/exec",
                            location=Location(line=_line(node)),
                            severity="advisory",
                            explanation="eval/exec can execute arbitrary code; security risk if input is untrusted.",
                            suggestion="Avoid eval/exec; use ast.literal_eval or structured parsing where possible.",
                        )
                    )
            if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
                if func.attr == "loads" and func.value.id == "pickle":
                    findings.append(
                        StaticAnalysisFinding(
                            domain="security",
                            rule_id="security.unsafe_deserialization",
                            title="Unsafe deserialization (pickle)",
                            location=Location(line=_line(node)),
                            severity="advisory",
                            explanation="Pickle deserialization can execute arbitrary code. Security signal.",
                            suggestion="Prefer JSON or other safe formats; if pickle is required, ensure trusted source only.",
                        )
                    )
                if func.attr in ("system", "popen", "call") and func.value.id in ("os", "subprocess"):
                    findings.append(
                        StaticAnalysisFinding(
                            domain="security",
                            rule_id="security.shell_exec",
                            title="Shell execution",
                            location=Location(line=_line(node)),
                            severity="advisory",
                            explanation="Shell execution without sanitization can be dangerous with user input.",
                            suggestion="Validate/sanitize input; prefer subprocess with list args over shell=True.",
                        )
                    )
    for i, line in enumerate(lines):
        for pat, title in CREDENTIAL_PATTERNS:
            if pat.search(line):
                findings.append(
                    StaticAnalysisFinding(
                        domain="security",
                        rule_id="security.hardcoded_credential",
                        title=title,
                        location=Location(line=i + 1),
                        severity="advisory",
                        explanation="Possible hard-coded credential detected. Security signal.",
                        suggestion="Use environment variables or a secrets manager; never commit credentials.",
                    )
                )
                break
    seen: set[tuple[str, int]] = set()
    unique = []
    for f in sorted(findings, key=lambda x: (x.location.line, x.rule_id)):
        key = (f.rule_id, f.location.line)
        if key not in seen:
            seen.add(key)
            unique.append(f)
    return unique


