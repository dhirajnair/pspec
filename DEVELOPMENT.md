# pspec – Development & Deployment

Developer-focused guide: running locally, tests, environment, and project layout.

---

## Prerequisites

- **Node.js** 18+ (frontend)
- **Python** 3.10+ (backend)
- **Conda** (backend env, optional)

---

## Run locally

### 1. Backend

```bash
cd backend
conda create -n pspec python=3.10 -y
conda activate pspec
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API: http://localhost:8000  
- Docs: http://localhost:8000/docs  

### 2. Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

- App: http://localhost:5173  

The dev server proxies `/api` to the backend; no extra env needed for local run.

---

## Running tests (backend)

From `backend/` with the same conda env (or `pip install -r requirements.txt`):

```bash
cd backend
PYTHONPATH=. pytest tests/ -v
```

Tests cover all analysis engines (types, dataflow, errors, security, metrics, insights) with edge cases, positive/negative samples, and API contract checks.

---

## Docker (backend only)

```bash
docker compose up backend
```

Then run the frontend locally: `cd frontend && npm install && npm run dev`. If the backend runs on the host, ensure conda env `pspec` is active; frontend proxy targets `http://localhost:8000`.

---

## Production build + single server

```bash
cd frontend && npm run build
cd ../backend && conda activate pspec && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Serve the `frontend/dist` folder at `/` (e.g. static middleware or reverse proxy).

Local preview only:

```bash
cd frontend && npm run build && npm run preview
```

Set `VITE_API_URL=http://localhost:8000` if the API runs on port 8000.

---

## Environment

### Backend

| Variable | Default | Description |
|----------|---------|-------------|
| `CORS_ORIGINS` | `http://localhost:5173` | Comma-separated allowed origins |
| `MAX_CODE_LENGTH` | `102400` | Max request body size for code (bytes) |
| `PEP8_URL` | `https://peps.python.org/pep-0008/` | Official PEP 8 source URL |
| `PEP8_DATE` | `2021-11-01` | Revision date shown in UI |
| `PEP8_REVISION` | `2021-11-01` | Revision identifier in reports |
| `PEP8_IGNORE` | (empty) | Comma-separated rules to suppress (e.g. `E501`) |
| `PYBP_ENABLED_BY_DEFAULT` | `true` | Include PYBP unless request sends `pybp_enabled: false` |
| `enable_pep8` | `true` | Enable PEP 8 engine |
| `enable_pybp` | `true` | Enable PYBP engine |
| `enable_types` | `true` | Enable type semantics engine |
| `enable_dataflow` | `true` | Enable data-flow engine |
| `enable_errors` | `true` | Enable error & exception engine |
| `enable_security` | `true` | Enable security engine |
| `enable_metrics` | `true` | Enable metrics engine |
| `enable_insights` | `true` | Enable insight synthesis |

### Frontend

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `''` | API base URL (empty when using Vite proxy) |

---

## Detecting PEP 8 spec changes

From `backend/`:

```bash
python scripts/detect_pep8_changes.py
```

Fetches the official PEP 8 page, hashes tracked sections, and compares to `data/pep8_baseline.json`. Prints affected section and **rule codes** (for updating `app/pep8_map.py`). First run: use `--accept` to create the baseline. After updating the app, run again with `--accept` to refresh. Use in CI without `--accept` to flag PEP 8 changes.

---

## Analysis engines (reference)

Output order: PEP 8 → PYBP → Correctness & Safety → Metrics & Insights.

| Engine | Purpose | Output |
|--------|---------|--------|
| **PEP 8** | Style and layout (normative). | Violations with code, line, PEP 8 quote, suggestion. |
| **PYBP** | Best-practice advisories. | Advisories with category, severity, authority, citation. |
| **Type semantics** | Lightweight type awareness. | Advisories for `Any` overuse, optional/return mismatches. |
| **Data-flow** | Snippet-local variable lifecycles. | Advisories for shadowing, redundant assignment. |
| **Error & exception** | Exception-handling patterns. | Warnings/advisories for bare except, silent catch, broad catch. |
| **Security** | Basic security smells. | Advisories for eval/exec, pickle, shell, hardcoded credentials. |
| **Metrics** | Complexity and size (report only). | Per-function cyclomatic complexity and nesting depth. |
| **Insights** | Synthesis of other findings. | High-level advisories (e.g. elevated risk, complexity context). |

Toggles: UI checkboxes or request body (`enable_pep8`, `pybp_enabled`, `enable_types`, etc.). Backend defaults for all are `true`.

---

## PYBP (Python Best Practices)

- **Enable/disable**: “Best Practice (PYBP) advisories” checkbox or `pybp_enabled: true|false` in `POST /api/check`.
- **Response**: `issues` = PEP 8 violations; `advisories` = PYBP findings (category, rule title, location, explanation, authority, citation, suggestion).
- **Rules**: Full metadata per rule. Categories include Function Design, Control Flow, Data Structures, OOP, Module Structure, Error Handling, Performance, Testability. See `backend/app/pybp/checks.py` for the full rule set.

---

## Project layout

- **backend/** – FastAPI + pycodestyle; `POST /api/check` (PEP 8, PYBP, advanced analysis); `app/pybp/` for PYBP; `app/analysis/` for type, dataflow, error, security, metrics, insight engines; `scripts/detect_pep8_changes.py` for PEP 8 change detection.
- **frontend/** – Vite + React; CodeMirror editor; results panel (PEP 8, PYBP, Correctness & Safety, Metrics & Insights); PYBP and Advanced analysis toggles.
- **spec/** – Vision and specs; `pybp-spec.txt`, `adv-static-analysis-spec.txt`, `ui-test-snippets.md`, `must_have.md`.

---

## Security

- No execution of user code; static analysis only.
- Request body size limited (`MAX_CODE_LENGTH`).
- CORS restricted to configured origins.

For production checklist (rate limits, CSP, etc.) see `spec/must_have.md`.
