# Backend — ID Job-Site Platform API (FastAPI)

## Quick start (local, no Docker)

```bash
cd backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env            # defaults run with mock integrations
uvicorn app.main:app --reload
```

Open http://localhost:8000/docs for the API, or http://localhost:8000/health.

## Quick start (Docker Compose — full stack)

From the repo root:

```bash
cp backend/.env.example backend/.env
docker compose up --build
```

This starts: **api** (FastAPI), **worker** (arq), **postgres**, **redis**, **minio** (S3).

## Tests & lint

```bash
pytest
ruff check . && black --check .
```

## Notes
- Integrations (LLM, WhatsApp, Google, S3) run in **mock/disabled mode** when their
  credentials are absent, so everything works end-to-end without external accounts.
- Secrets are read from the environment only — never commit `.env`.
