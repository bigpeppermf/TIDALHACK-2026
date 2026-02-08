# TIDALHACK-2026

Base repo scaffold for hackathon development.

## Quick start

1. Clone and enter the repo.
2. Copy `.env.example` to `.env` and fill values if needed.
3. Pick a stack and initialize in place:
   - Web app: `npm init -y` (or `pnpm init`)
   - Python app: `python -m venv .venv && pip install -r requirements.txt`
4. Build inside `src/` and add tests in `tests/`.

## Suggested structure

- `src/` app source code
- `tests/` automated tests
- `docs/` notes, architecture sketches, API plans

## Tech stack (frontend compatible)

Backend (Python)
- FastAPI + Uvicorn
- Google Gemini SDK (`google-genai`)
- Pillow, pdf2image
- python-dotenv

Frontend (Node)
- Vite + Vue 3
- KaTeX for LaTeX preview
- shadcn/ui components (or equivalent)

Shared contract
- `POST /api/convert` returns `{ "success": true, "latex": "...", "processing_time_ms": 1234 }`
- `POST /api/export` returns a `.tex` file
- CORS allowlist includes `http://localhost:5173`

## Local dev (stack alignment)

1. Backend
   - `python -m venv .venv && source .venv/bin/activate`
   - `pip install -r requirements.txt`
   - Set `GEMINI_API_KEY` in `.env`
   - Run: `uvicorn app.main:app --reload --port 8000` from `src/backend`
2. Frontend
   - `npm install`
   - `npm run dev` (default: `http://localhost:5173`)

Docs: `docs/ARCHITECTURE.md`, `docs/BACKEND-REFERENCE.md`, `docs/FRONTEND-REFERENCE.md`

## Hackathon planning checklist

- Problem statement
- Target users
- Core demo flow (3-5 minutes)
- Must-have features
- Nice-to-have features
- Data/API dependencies
- Roles and ownership

## Git workflow

- Create short-lived feature branches from `main`.
- Open PRs early, merge small changes frequently.
- Keep commits focused and descriptive.
