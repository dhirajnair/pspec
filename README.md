# pspec — PEP 8 & Python Best Practices

Web app to paste Python code and get **strict, spec-accurate PEP 8 validation** plus **Python Best Practices (PYBP)** advisories. No login; no execution of user code.

- **PEP 8**: Normative style checks (violations with citations and fixes).
- **PYBP**: Advisory best-practice checks (maintainability, readability, error handling, etc.). Can be enabled or disabled independently.

## Run locally

### Prerequisites

- **Node.js** 18+ (for frontend)
- **Python** 3.10+ (for backend)
- **Conda** (for backend env)

### 1. Backend

```bash
cd backend
conda create -n pspec python=3.10 -y
conda activate pspec
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API: http://localhost:8000  
Docs: http://localhost:8000/docs

### 2. Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173  

The dev server proxies `/api` to the backend, so no extra env is needed for local run.

### Optional: Docker (backend only)

```bash
docker compose up backend
```

Then run the frontend locally: `cd frontend && npm install && npm run dev`. Ensure conda env `pspec` is active if running the backend on the host; frontend proxy targets `http://localhost:8000`.

### Optional: production build + single server

```bash
cd frontend && npm run build
cd ../backend && conda activate pspec && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Serve the `frontend/dist` folder at `/` (e.g. with a static middleware or reverse proxy). For local preview only:

```bash
cd frontend && npm run build && npm run preview
```

Then point the preview URL to `VITE_API_URL=http://localhost:8000` if you run the API on 8000.

## Environment (backend)

| Variable | Default | Description |
|----------|---------|-------------|
| `CORS_ORIGINS` | `http://localhost:5173` | Comma-separated allowed origins |
| `MAX_CODE_LENGTH` | `102400` | Max request body size for code (bytes) |
| `PEP8_URL` | `https://peps.python.org/pep-0008/` | Official PEP 8 source URL |
| `PEP8_DATE` | `2021-11-01` | Revision date shown in UI |
| `PEP8_REVISION` | `2021-11-01` | Revision identifier in reports |
| `PEP8_IGNORE` | (empty) | Comma-separated rules to suppress (e.g. `E501` = max line length) |
| `PYBP_ENABLED_BY_DEFAULT` | `true` | When `true`, `/api/check` includes PYBP advisories unless the request sends `pybp_enabled: false`. |

## Environment (frontend)

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `''` | API base URL (empty when using Vite proxy to backend) |

## Detecting PEP 8 spec changes

From `backend/`, run:

```bash
python scripts/detect_pep8_changes.py
```

The script fetches the official PEP 8 page, hashes each tracked section, and compares to `data/pep8_baseline.json`. If a section changed, it prints which section and which **rule codes** are affected (so you can update `app/pep8_map.py`). First time: run with `--accept` to create the baseline. After reviewing any reported change and updating the app, run again with `--accept` to refresh the baseline. Optionally run the script in CI (without `--accept`) to flag when PEP 8 has changed.

## PYBP (Python Best Practices)

PYBP runs in parallel to PEP 8 on the same code: it produces **advisories only** (no errors), with severity `info`, `advisory`, or `warning`. Rules are cited (e.g. Clean Code, Python Docs, PEP 20).

- **Enable/disable**: Use the “Best Practice (PYBP) advisories” checkbox in the UI, or send `pybp_enabled: true|false` in the `POST /api/check` body.
- **Response**: `issues` = PEP 8 violations; `advisories` = PYBP findings (category, rule title, location, explanation, authority, citation, suggestion).
- **Rules**: Each rule has full metadata (category, authority, citation, severity). Categories and examples:
  - **Function Design**: excessive length, cyclomatic complexity, too many parameters, boolean flag arguments
  - **Control Flow & Readability**: deep nesting, else after return
  - **Data Structures & Idioms**: list built in loop with `.append()` (suggest comprehension)
  - **Object-Oriented Design**: class with many methods (god-class signal)
  - **Module & Package Structure**: overloaded module (too many top-level definitions)
  - **Error Handling**: bare except, swallowing exceptions, overly broad catch
  - **Performance & Scalability**: string concatenation in loop
  - **Testability & Maintainability**: global state modification  
  See `backend/app/pybp/checks.py` for the full rule set and citations.

## Project layout

- `backend/` – FastAPI + pycodestyle; `POST /api/check` (PEP 8 + optional PYBP); `app/pybp/` for PYBP engine and rules; `scripts/detect_pep8_changes.py` for PEP 8 change detection.
- `frontend/` – Vite + React; code editor (CodeMirror), results panel (PEP 8 and PYBP sections), PYBP toggle, loading/error/empty states.
- `spec/` – Vision, features, screens, tech, build plan; `pep8-change-detection.md`, `pybp-spec.txt` (PYBP extension); `must_have.md` lists open decisions for production.

## Security

- No execution of user code; static analysis only.
- Request body size limited (see `MAX_CODE_LENGTH`).
- CORS restricted to configured origins.

For production checklist (rate limits, CSP, etc.) see `spec/must_have.md`.
