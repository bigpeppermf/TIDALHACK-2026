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
