# pspec

**pspec** is a **snippet-centric static code analyzer for Python**. It evaluates a single Python code snippet in isolation and produces **review-grade feedback** across style, best practices, correctness, safety, and complexity — without requiring project context, dependencies, or execution.

> pspec is designed for **code review, interviews, teaching, and quick quality checks**, not for whole-repository or CI-heavy workflows.

---

## Why pspec exists

Most Python linters and analyzers assume:

* a project layout
* installed dependencies
* import resolution
* configuration files

That makes them heavyweight and poorly suited for **snippets**.

pspec takes a different approach:

* 🔹 **One snippet in, one deterministic analysis out**
* 🔹 No filesystem, no imports, no execution
* 🔹 Clear separation between *spec*, *best practices*, and *engineering signals*
* 🔹 Explanations a senior reviewer would give

---

## Core Principles

* **Snippet-centric by design** – analysis is limited strictly to the provided code
* **Specification-driven** – PEP 8 is treated as law, not opinion
* **Advisory best practices** – engineering judgment is clearly labeled
* **Deterministic & auditable** – same input always yields the same output
* **No auto-fixing** – pspec explains, it does not rewrite

---

## What pspec analyzes

pspec runs multiple **independent analysis engines** on the same snippet. Each engine produces its own findings and never alters the output of others.

### 1️⃣ PEP 8 Compliance (Normative)

* Enforces **PEP 8 style rules** strictly
* Reports:

  * what is wrong
  * where it occurs
  * how to fix it
  * the **exact PEP 8 recommendation**, quoted and cited

PEP 8 is treated as a **versioned specification**, not a guideline.

---

### 2️⃣ PYBP – Python Best Practices (Advisory)

Best-practice signals that affect maintainability and readability, including:

* Large or complex functions
* Deep nesting
* Long parameter lists
* Overloaded classes or modules
* Poor separation of concerns

All PYBP findings are:

* advisory only
* explicitly cited
* never treated as errors

---

### 3️⃣ Type Semantics (Snippet-Local)

Lightweight type awareness without mypy or stubs:

* Missing type annotations (advisory)
* Return type mismatches
* Obvious incompatible operations
* Unsafe use of `Optional` or `Any`

---

### 4️⃣ Data-Flow Analysis

Tracks variable lifecycle within the snippet:

* Use before assignment
* Variable shadowing
* Dead or unreachable code
* Redundant assignments

---

### 5️⃣ Error & Exception Semantics

Detects misleading or unsafe exception patterns:

* Bare or overly broad `except`
* Exceptions caught and ignored
* Control flow altered silently by exceptions

---

### 6️⃣ Security & Misuse Signals

High-confidence, snippet-safe security advisories:

* `eval` / `exec`
* Unsafe `pickle` usage
* Shell execution without sanitization
* Hard-coded secrets (pattern-based)

All security findings are **signals**, not claims of vulnerability.

---

### 7️⃣ Metrics & Complexity

Quantitative context for reviewers:

* Cyclomatic complexity
* Cognitive complexity
* Nesting depth
* Statement counts

Metrics are reported, not enforced.

---

### 8️⃣ Insight Synthesis

pspec correlates findings to produce **reviewer-level insights**, for example:

> "This function is long, complex, and deeply nested — it likely has multiple responsibilities."

Insights never suppress underlying findings and are fully traceable.

---

## What pspec intentionally does NOT do

These are **explicit non-goals**:

* ❌ Project-wide or multi-file analysis
* ❌ Import or dependency resolution
* ❌ Execution of user code
* ❌ Full type checking or stub loading
* ❌ CI, repo scanning, or filesystem access
* ❌ Automatic code fixes

This keeps pspec fast, predictable, and trustworthy for snippets.

---

## Typical Use Cases

* Reviewing code snippets in PR comments
* Python interviews and take-home evaluations
* Teaching Python style and design
* Validating examples for documentation or blogs
* Quick "is this code good?" checks

---

## Output Characteristics

* Findings grouped by analysis domain
* Clear severity levels: violation, warning, advisory
* Stable rule identifiers
* Explicit engine and spec versioning

pspec is suitable for both **human review** and **machine consumption**.

---

## Philosophy

> **PEP 8 is law. Best practices are judgment. Metrics are context.**

pspec exists to make those distinctions explicit.

---

## Status

pspec is actively evolving, but its **core guarantees are stable**:

* Snippet-centric analysis
* Separation of authority
* No silent behavior changes

---

## License

MIT License

---

For **local setup, running the app, tests, and development**, see [DEVELOPMENT.md](DEVELOPMENT.md).
