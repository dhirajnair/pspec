"""Unit tests for the security & misuse signals engine."""
from __future__ import annotations

import pytest

from app.analysis.security import run_security
from tests.conftest import assert_finding


class TestSecurityEdgeCases:
    """Edge cases: empty, invalid syntax, no dangerous constructs."""

    def test_empty_string_returns_empty(self):
        assert run_security("") == []

    def test_whitespace_only_returns_empty(self):
        assert run_security("  \n ") == []

    def test_invalid_syntax_returns_empty(self):
        assert run_security("eval(") == []

    def test_safe_code_only_returns_empty(self):
        code = """
def add(a, b):
    return a + b
"""
        assert run_security(code) == []


class TestSecurityNegative:
    """Valid code that must not trigger security findings."""

    def test_ast_literal_eval_not_eval(self):
        code = """
import ast
x = ast.literal_eval("[1,2,3]")
"""
        findings = run_security(code)
        assert not any(f.rule_id == "security.dangerous_eval" for f in findings)

    def test_json_loads_not_pickle(self):
        code = """
import json
data = json.loads(s)
"""
        assert not any(f.rule_id == "security.unsafe_deserialization" for f in run_security(code))

    def test_subprocess_run_with_list_not_shell(self):
        code = """
import subprocess
subprocess.run(["ls", "-la"])
"""
        findings = run_security(code)
        shell = [f for f in findings if f.rule_id == "security.shell_exec"]
        assert len(shell) == 0

    def test_password_in_comment_not_credential(self):
        code = "# password was reset by user"
        findings = run_security(code)
        cred = [f for f in findings if f.rule_id == "security.hardcoded_credential"]
        assert len(cred) == 0


class TestSecurityPositive:
    """Valid code that triggers security findings."""

    def test_eval_triggered(self):
        code = "x = eval('1+1')"
        findings = run_security(code)
        ev = [f for f in findings if f.rule_id == "security.dangerous_eval"]
        assert len(ev) == 1
        assert_finding(ev[0], "security", "security.dangerous_eval", title_substr="eval")

    def test_exec_triggered(self):
        code = "exec('print(1)')"
        findings = run_security(code)
        ex = [f for f in findings if f.rule_id == "security.dangerous_eval"]
        assert len(ex) == 1

    def test_pickle_loads_triggered(self):
        code = """
import pickle
data = pickle.loads(buf)
"""
        findings = run_security(code)
        pk = [f for f in findings if f.rule_id == "security.unsafe_deserialization"]
        assert len(pk) == 1
        assert_finding(pk[0], "security", "security.unsafe_deserialization", title_substr="pickle")

    def test_os_system_triggered(self):
        code = """
import os
os.system("ls")
"""
        findings = run_security(code)
        shell = [f for f in findings if f.rule_id == "security.shell_exec"]
        assert len(shell) == 1
        assert_finding(shell[0], "security", "security.shell_exec", title_substr="Shell")

    def test_subprocess_call_triggered(self):
        code = """
import subprocess
subprocess.call("ls", shell=True)
"""
        findings = run_security(code)
        shell = [f for f in findings if f.rule_id == "security.shell_exec"]
        assert len(shell) >= 1

    def test_hardcoded_password_triggered(self):
        code = 'password = "secret123"'
        findings = run_security(code)
        cred = [f for f in findings if f.rule_id == "security.hardcoded_credential"]
        assert len(cred) >= 1
        assert any("password" in f.title.lower() or "Hard-coded" in f.title for f in cred)

    def test_hardcoded_api_key_triggered(self):
        code = 'api_key = "sk-xxxx"'
        findings = run_security(code)
        cred = [f for f in findings if f.rule_id == "security.hardcoded_credential"]
        assert len(cred) >= 1

    def test_multiple_security_findings(self):
        code = """
eval("1")
import pickle
pickle.loads(b"x")
password = "x"
"""
        findings = run_security(code)
        assert len(findings) >= 3
        rule_ids = [f.rule_id for f in findings]
        assert "security.dangerous_eval" in rule_ids
        assert "security.unsafe_deserialization" in rule_ids
        assert "security.hardcoded_credential" in rule_ids

    def test_all_findings_advisory(self):
        code = 'eval("1")\npassword = "x"'
        findings = run_security(code)
        for f in findings:
            assert f.domain == "security"
            assert f.severity == "advisory"
