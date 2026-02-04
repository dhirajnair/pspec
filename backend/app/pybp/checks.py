"""PYBP rule implementations. Each rule has full metadata per spec §5."""
from __future__ import annotations

import ast
from typing import Any, List

from app.pybp.rules import PybpRule


def _line(node: ast.AST) -> int:
    return getattr(node, "lineno", 1) or 1


def _name(node: ast.AST) -> str | None:
    return getattr(node, "name", None)


# --- Error Handling (§6.6) ---

def _check_bare_except(node: ast.AST, source: str) -> List[dict]:
    """Bare except: blocks. Authority: Python Docs."""
    if not isinstance(node, ast.ExceptHandler):
        return []
    if node.type is None:
        return [
            {
                "line": _line(node),
                "explanation": "Bare except: catches all exceptions including BaseException and system exits.",
                "suggestion": "Catch a specific exception type (e.g. except ValueError:) or at least 'except Exception:'.",
            }
        ]
    return []


# --- Function Design (§6.1) ---

def _count_function_lines(node: ast.FunctionDef, source: str) -> int:
    """Line count of function body (excluding decorators/docstring)."""
    lines = source.splitlines()
    start = node.lineno - 1
    end = node.end_lineno if hasattr(node, "end_lineno") and node.end_lineno else start + 1
    return max(0, end - start)


def _check_long_function(node: ast.AST, source: str) -> List[dict]:
    """Excessive function length. Authority: Clean Code."""
    if not isinstance(node, ast.FunctionDef):
        return []
    nlines = _count_function_lines(node, source)
    if nlines > 50:
        return [
            {
                "line": _line(node),
                "function": node.name,
                "explanation": f"Function has {nlines} lines; long functions are harder to test and maintain.",
                "suggestion": "Consider splitting into smaller functions with single responsibilities.",
            }
        ]
    return []


# --- Control Flow (§6.2) ---

def _nesting_level(node: ast.AST) -> int:
    """Max nesting depth under this node (if/for/while/with/try)."""
    if isinstance(node, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
        child_max = 0
        for child in ast.iter_child_nodes(node):
            child_max = max(child_max, _nesting_level(child))
        return 1 + child_max
    return max((_nesting_level(c) for c in ast.iter_child_nodes(node)), default=0)


def _check_deep_nesting(node: ast.AST, source: str) -> List[dict]:
    """Deep nesting levels. Authority: PEP 20, Python Docs."""
    if not isinstance(node, ast.FunctionDef):
        return []
    depth = 0
    for n in ast.walk(node):
        if isinstance(n, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
            d = _nesting_level(n)
            if d > depth:
                depth = d
    if depth > 4:
        return [
            {
                "line": _line(node),
                "function": node.name,
                "explanation": f"Nesting depth up to {depth} levels; deep nesting reduces readability.",
                "suggestion": "Use early returns or extract nested logic into helper functions.",
            }
        ]
    return []


def _cyclo_complexity(node: ast.AST) -> int:
    """Cyclomatic complexity: 1 + number of decision points."""
    total = 1
    for n in ast.walk(node):
        if isinstance(n, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
            total += 1
        elif isinstance(n, ast.BoolOp):
            total += len(n.values) - 1
        elif isinstance(n, ast.comprehension):
            total += 1
            if n.ifs:
                total += len(n.ifs)
    return total


def _check_cyclomatic_complexity(node: ast.AST, source: str) -> List[dict]:
    """High cyclomatic complexity. Authority: Clean Code, Effective Python."""
    if not isinstance(node, ast.FunctionDef):
        return []
    c = _cyclo_complexity(node)
    if c > 10:
        return [
            {
                "line": _line(node),
                "function": node.name,
                "explanation": f"Cyclomatic complexity is {c}; high complexity makes testing and reasoning harder.",
                "suggestion": "Simplify conditionals or split into smaller functions.",
            }
        ]
    return []


def _node_in_class(node: ast.FunctionDef, tree: ast.AST) -> bool:
    for n in ast.walk(tree):
        if isinstance(n, ast.ClassDef) and n is not node:
            for c in ast.walk(n):
                if c is node:
                    return True
    return False


def _check_too_many_params(node: ast.AST, source: str) -> List[dict]:
    """Too many parameters. Authority: Clean Code, Effective Python."""
    if not isinstance(node, ast.FunctionDef):
        return []
    nargs = len(node.args.args) + len(node.args.kwonlyargs)
    if node.args.vararg:
        nargs += 1
    if node.args.kwarg:
        nargs += 1
    try:
        tree = ast.parse(source)
        if _node_in_class(node, tree) and node.args.args:
            nargs -= 1  # exclude self
    except Exception:
        pass
    if nargs > 7:
        return [
            {
                "line": _line(node),
                "function": node.name,
                "explanation": f"Function has {nargs} parameters; many parameters complicate the API and call sites.",
                "suggestion": "Consider an options object, *args/**kwargs for optional args, or splitting responsibilities.",
            }
        ]
    return []


def _check_boolean_flag_args(node: ast.AST, source: str) -> List[dict]:
    """Boolean flag arguments. Authority: Clean Code."""
    if not isinstance(node, ast.FunctionDef):
        return []
    flags: List[str] = []
    for a in node.args.args:
        if isinstance(a, ast.arg) and a.arg and a.arg not in ("self", "cls"):
            if a.arg.startswith("is_") or a.arg.startswith("has_") or a.arg in ("flag", "enabled", "disabled"):
                flags.append(a.arg)
    for i, d in enumerate(node.args.defaults or []):
        if isinstance(d, ast.Constant) and isinstance(d.value, bool):
            idx = len(node.args.args) - len(node.args.defaults) + i
            if 0 <= idx < len(node.args.args):
                name = node.args.args[idx].arg
                if name not in flags:
                    flags.append(name)
    if not flags:
        return []
    return [
        {
            "line": _line(node),
            "function": node.name,
            "explanation": f"Boolean-like parameter(s): {', '.join(flags)}; flag arguments often indicate two code paths.",
            "suggestion": "Consider splitting into two functions or a small options object.",
        }
    ]


def _check_else_after_return(node: ast.AST, source: str) -> List[dict]:
    """Else after return: if body returns, else is redundant. Authority: PEP 20, Python Docs."""
    if not isinstance(node, ast.If):
        return []
    if node.orelse and len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
        return []  # elif chain
    last_in_if = node.body[-1] if node.body else None
    if not isinstance(last_in_if, ast.Return) or not node.orelse:
        return []
    return [
        {
            "line": _line(node.orelse[0]),
            "explanation": "An 'else' block after an 'if' that returns can often be flattened for readability.",
            "suggestion": "Move the else body to the same level as the if; use early return in the if.",
        }
    ]


# --- Data Structures & Idioms (§6.3) ---

def _check_loop_append_pattern(node: ast.AST, source: str) -> List[dict]:
    """Loop with list.append could be list comprehension. Authority: Python Docs, Real Python."""
    if not isinstance(node, ast.For):
        return []
    # Simple heuristic: for x in y: body with body containing list.append(x) or similar
    for stmt in ast.walk(node):
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            c = stmt.value
            if isinstance(c.func, ast.Attribute):
                if c.func.attr == "append" and c.args and isinstance(c.func.value, ast.Name):
                    return [
                        {
                            "line": _line(node),
                            "explanation": "Building a list in a loop with .append() can often be a list comprehension.",
                            "suggestion": "Consider a list comprehension [f(x) for x in iterable] if the body is simple.",
                        }
                    ]
    return []


# --- OOP (§6.4) ---

def _check_large_class(node: ast.AST, source: str) -> List[dict]:
    """Class with many methods (god-class signal). Authority: Clean Code, Effective Python."""
    if not isinstance(node, ast.ClassDef):
        return []
    methods = [n for n in node.body if isinstance(n, ast.FunctionDef) and not (n.name.startswith("__") and n.name.endswith("__"))]
    if len(methods) > 15:
        return [
            {
                "line": _line(node),
                "class_name": node.name,
                "explanation": f"Class has {len(methods)} public methods; large classes often have too many responsibilities.",
                "suggestion": "Consider splitting into smaller classes or using composition.",
            }
        ]
    return []


# --- Module & Package (§6.5) ---

def _check_overloaded_module(node: ast.AST, source: str) -> List[dict]:
    """Too many top-level definitions. Authority: Cosmic Python, Python Packaging Docs."""
    if not isinstance(node, ast.Module):
        return []
    count = sum(1 for n in node.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)))
    if count > 25:
        return [
            {
                "line": 1,
                "explanation": f"Module has {count} top-level classes/functions; consider splitting into smaller modules.",
                "suggestion": "Group related code into submodules or packages.",
            }
        ]
    return []


# --- Error Handling (more §6.6) ---

def _except_has_only_pass(node: ast.ExceptHandler, source: str) -> bool:
    """True if handler body is effectively empty (pass only)."""
    if not node.body:
        return True
    if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
        return True
    return False


def _check_swallow_exception(node: ast.AST, source: str) -> List[dict]:
    """Swallowing exceptions (except: pass). Authority: Python Docs."""
    if not isinstance(node, ast.ExceptHandler):
        return []
    if node.type is None:
        return []  # Bare except reported by pybp.error.bare_except
    if not _except_has_only_pass(node, source):
        return []
    return [
        {
            "line": _line(node),
            "explanation": "Exception is caught but not logged or re-raised; failures can be hard to diagnose.",
            "suggestion": "At least log the exception; consider re-raising or handling specifically.",
        }
    ]


def _check_broad_exception(node: ast.AST, source: str) -> List[dict]:
    """Catching Exception only. Authority: Python Docs."""
    if not isinstance(node, ast.ExceptHandler):
        return []
    if node.type is None:
        return []
    name = None
    if isinstance(node.type, ast.Name):
        name = node.type.id
    elif isinstance(node.type, ast.Attribute):
        name = node.type.attr
    if name == "Exception" and _except_has_only_pass(node, source):
        return [
            {
                "line": _line(node),
                "explanation": "Catching Exception with no handling can hide bugs; prefer specific exception types.",
                "suggestion": "Catch specific exceptions (e.g. ValueError, KeyError) or log and re-raise.",
            }
        ]
    return []


# --- Performance (§6.7) ---

def _check_string_concat_in_loop(node: ast.AST, source: str) -> List[dict]:
    """Inefficient string concatenation in loop. Authority: Python Docs."""
    if not isinstance(node, ast.For):
        return []
    for n in ast.walk(node):
        if isinstance(n, ast.AugAssign) and isinstance(n.op, ast.Add):
            if isinstance(n.target, ast.Name):
                return [
                    {
                        "line": _line(n),
                        "explanation": "Repeated += on a string in a loop allocates many intermediate strings.",
                        "suggestion": "Collect parts in a list and use ''.join(parts) for better performance.",
                    }
                ]
    return []


# --- Testability (§6.8) ---

def _check_global_assignment(node: ast.AST, source: str) -> List[dict]:
    """Global state modification. Authority: Clean Architecture, testing best practices."""
    if not isinstance(node, ast.FunctionDef):
        return []
    has_global = any(isinstance(s, ast.Global) for s in node.body)
    if not has_global:
        return []
    return [
        {
            "line": _line(node),
            "function": node.name,
            "explanation": "Function modifies global state; this makes testing and reasoning about behavior harder.",
            "suggestion": "Prefer passing dependencies as arguments or using dependency injection.",
        }
    ]


# Rule registry: full metadata per spec §5
PYBP_RULES: List[PybpRule] = [
    PybpRule(
        rule_id="pybp.error.bare_except",
        title="Bare except clause",
        category="Error Handling",
        description="Use of bare except: catches all exceptions.",
        rationale="Bare except can hide bugs and make debugging difficult; it also catches SystemExit and KeyboardInterrupt.",
        authority="Python Docs",
        citation="https://docs.python.org/3/tutorial/errors.html",
        detection_strategy="AST",
        thresholds=None,
        suggestion="Catch a specific exception type or at least 'except Exception:'.",
        severity="warning",
        check=_check_bare_except,
    ),
    PybpRule(
        rule_id="pybp.func.excessive_length",
        title="Excessive function length",
        category="Function Design",
        description="Function body exceeds recommended line count.",
        rationale="Long functions are harder to understand, test, and maintain.",
        authority="Clean Code",
        citation="Clean Code, Robert C. Martin — Functions",
        detection_strategy="AST + metrics",
        thresholds="> 50 lines",
        suggestion="Consider splitting into smaller functions with single responsibilities.",
        severity="advisory",
        check=_check_long_function,
    ),
    PybpRule(
        rule_id="pybp.control.deep_nesting",
        title="Deep nesting",
        category="Control Flow & Readability",
        description="Control flow nesting exceeds recommended depth.",
        rationale="Deep nesting reduces readability and makes code paths harder to follow.",
        authority="PEP 20 (Zen of Python), Python Docs",
        citation="PEP 20 — Readability counts",
        detection_strategy="AST",
        thresholds="> 4 levels",
        suggestion="Use early returns or extract nested logic into helper functions.",
        severity="advisory",
        check=_check_deep_nesting,
    ),
    PybpRule(
        rule_id="pybp.func.cyclomatic_complexity",
        title="High cyclomatic complexity",
        category="Function Design",
        description="Function has many decision branches.",
        rationale="High complexity makes unit testing and reasoning about behavior difficult.",
        authority="Clean Code, Effective Python",
        citation="Clean Code — Functions; Effective Python — Concurrency",
        detection_strategy="AST + metrics",
        thresholds="> 10",
        suggestion="Simplify conditionals or split into smaller functions.",
        severity="advisory",
        check=_check_cyclomatic_complexity,
    ),
    PybpRule(
        rule_id="pybp.func.too_many_parameters",
        title="Too many parameters",
        category="Function Design",
        description="Function accepts more than a recommended number of arguments.",
        rationale="Many parameters complicate the API and make call sites error-prone.",
        authority="Clean Code, Effective Python",
        citation="Clean Code — Function Arguments; Effective Python — Functions",
        detection_strategy="AST",
        thresholds="> 7",
        suggestion="Consider an options object, *args/**kwargs for optional args, or splitting responsibilities.",
        severity="advisory",
        check=_check_too_many_params,
    ),
    PybpRule(
        rule_id="pybp.func.boolean_flag",
        title="Boolean flag arguments",
        category="Function Design",
        description="Function uses boolean parameters to switch behavior.",
        rationale="Flag arguments often indicate two code paths; separate functions can be clearer.",
        authority="Clean Code",
        citation="Clean Code — Robert C. Martin — Function Arguments",
        detection_strategy="AST",
        thresholds=None,
        suggestion="Consider splitting into two functions or a small options object.",
        severity="info",
        check=_check_boolean_flag_args,
    ),
    PybpRule(
        rule_id="pybp.control.else_after_return",
        title="Else after return",
        category="Control Flow & Readability",
        description="If-block ends with return followed by else.",
        rationale="Redundant else can be flattened for readability.",
        authority="PEP 20, Python Docs",
        citation="PEP 20 — Flat is better than nested",
        detection_strategy="AST",
        thresholds=None,
        suggestion="Move the else body to the same level; use early return in the if.",
        severity="info",
        check=_check_else_after_return,
    ),
    PybpRule(
        rule_id="pybp.data.loop_append",
        title="List built in loop with .append()",
        category="Data Structures & Idioms",
        description="Loop builds a list via .append() where a comprehension could apply.",
        rationale="List comprehensions are idiomatic and often clearer and more efficient.",
        authority="Python Docs, Real Python",
        citation="https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions",
        detection_strategy="AST",
        thresholds=None,
        suggestion="Consider a list comprehension [f(x) for x in iterable] if the body is simple.",
        severity="info",
        check=_check_loop_append_pattern,
    ),
    PybpRule(
        rule_id="pybp.oop.large_class",
        title="Class with many methods",
        category="Object-Oriented Design",
        description="Class has a high number of public methods.",
        rationale="Large classes often have too many responsibilities (god object).",
        authority="Clean Code, Effective Python",
        citation="Clean Code — Classes; Effective Python — Classes and Inheritance",
        detection_strategy="AST + metrics",
        thresholds="> 15 public methods",
        suggestion="Consider splitting into smaller classes or using composition.",
        severity="advisory",
        check=_check_large_class,
    ),
    PybpRule(
        rule_id="pybp.module.overloaded",
        title="Overloaded module",
        category="Module & Package Structure",
        description="Module has many top-level classes and functions.",
        rationale="Large modules are hard to navigate and suggest poor separation of concerns.",
        authority="Cosmic Python, Python Packaging Docs",
        citation="Cosmic Python — Structure; https://packaging.python.org/",
        detection_strategy="AST",
        thresholds="> 25",
        suggestion="Group related code into submodules or packages.",
        severity="advisory",
        check=_check_overloaded_module,
    ),
    PybpRule(
        rule_id="pybp.error.swallow",
        title="Swallowing exceptions",
        category="Error Handling",
        description="Exception handler does nothing (e.g. pass only).",
        rationale="Silent catch makes debugging difficult and can hide failures.",
        authority="Python Docs",
        citation="https://docs.python.org/3/tutorial/errors.html",
        detection_strategy="AST",
        thresholds=None,
        suggestion="At least log the exception; consider re-raising or handling specifically.",
        severity="warning",
        check=_check_swallow_exception,
    ),
    PybpRule(
        rule_id="pybp.error.broad_catch",
        title="Overly broad exception catch",
        category="Error Handling",
        description="Catching Exception with no handling.",
        rationale="Can hide bugs; prefer specific exception types.",
        authority="Python Docs",
        citation="https://docs.python.org/3/tutorial/errors.html",
        detection_strategy="AST",
        thresholds=None,
        suggestion="Catch specific exceptions (e.g. ValueError, KeyError) or log and re-raise.",
        severity="advisory",
        check=_check_broad_exception,
    ),
    PybpRule(
        rule_id="pybp.perf.string_concat",
        title="String concatenation in loop",
        category="Performance & Scalability",
        description="Repeated += on a string in a loop.",
        rationale="Creates many intermediate strings; join() is more efficient.",
        authority="Python Docs",
        citation="https://docs.python.org/3/faq/programming.html#what-is-the-most-efficient-way-to-concatenate-many-strings",
        detection_strategy="AST",
        thresholds=None,
        suggestion="Collect parts in a list and use ''.join(parts) for better performance.",
        severity="advisory",
        check=_check_string_concat_in_loop,
    ),
    PybpRule(
        rule_id="pybp.test.global_state",
        title="Global state modification",
        category="Testability & Maintainability",
        description="Function declares global and modifies global state.",
        rationale="Global state makes testing and reasoning about behavior harder.",
        authority="Clean Architecture, Testing best practices",
        citation="Clean Architecture — Robert C. Martin; Testing best practices",
        detection_strategy="AST",
        thresholds=None,
        suggestion="Prefer passing dependencies as arguments or using dependency injection.",
        severity="advisory",
        check=_check_global_assignment,
    ),
]
