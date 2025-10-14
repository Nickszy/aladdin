Aladdin — Reflex App Quickstart

Overview
- Python 3.11+ Reflex web app with a FastAPI API under `aladdin/api`.
- Frontend served by Reflex; ports configured in `rxconfig.py` (`3002` frontend, `8032` backend).
- Data layer uses MySQL (SQLModel) and Supabase; OpenAI-compatible API optional.

Prerequisites
- Python `>=3.11` (verified in this workspace)
- `uv` package manager (installed) or `pip`
- `reflex` CLI (installed)

Environment
- Copy or create `.env` in the project root. Required keys used by services:
  - `SUPABASE_URL`, `SUPABASE_KEY`
  - `OPENAI_API_KEY`, `OPENAI_URL`, `OPENAI_MODEL` (if using AI features)
  - Optional: `aliSUPABASE_URL`, `aliSUPABASE_KEY`
- Database URLs are currently hard-coded in `aladdin/db.py` to MySQL instances. For local dev, consider pointing to a local MySQL or providing a dev-friendly engine.

Install
- Using uv (recommended):
  - `uv sync`
- Using pip (if preferred):
  - `python -m venv .venv && .\.venv\Scripts\activate`
  - `pip install -e .`

Run (Dev)
- Start the app with Reflex:
  - `reflex run`
- Visit: `http://localhost:3002`

Notes
- The app object is defined in `aladdin/aladdin.py` and pages live under `aladdin/pages`.
- FastAPI routes are defined in `aladdin/api/index.py` and mounted via `api_transformer` in the Reflex app.
- If MySQL is unreachable, features that hit the DB will fail; adjust `aladdin/db.py` for a local dev database.
