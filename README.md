# PEP 8 Compliance Checker

Web app to paste Python code and get **strict, spec-accurate PEP 8 validation** with citations and suggested fixes. No login; no execution of user code.

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

## Environment (frontend)

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `''` | API base URL (empty when using Vite proxy to backend) |

## Project layout

- `backend/` – FastAPI + pycodestyle; `POST /api/check` returns issues with PEP 8 quote/section/suggestion.
- `frontend/` – Vite + React; code editor (CodeMirror), results panel, loading/error/empty states.
- `spec/` – Vision, features, screens, tech, build plan; `pep8-change-detection.md` (PEP 8 change-detection design); `must_have.md` lists open decisions for production.

## Security

- No execution of user code; static analysis only.
- Request body size limited (see `MAX_CODE_LENGTH`).
- CORS restricted to configured origins.

For production checklist (rate limits, CSP, etc.) see `spec/must_have.md`.
