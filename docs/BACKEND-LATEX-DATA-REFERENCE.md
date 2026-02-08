# Backend LaTeX Data Reference

## 1. Title and Metadata

Feature name: LaTeX Storage and Retrieval
Intended audience: Backend and API developers
Status: OAuth-ready (mock identity in current code)
Related documents: `docs/ARCHITECTURE.md`, `docs/TESTING.md`, `docs/BACKEND-LATEX-DATA-CHECKLIST.md`

## 2. Purpose

This feature defines storage and retrieval of user-owned LaTeX artifacts for backend services. LaTeX is the canonical artifact because all exports and views derive from the `.tex` source. OAuth is treated as identity-only; authorization decisions are enforced by backend ownership rules, not provider-specific scopes.

## 3. System Architecture

```
Client -> FastAPI -> Database
```

Auth is responsible for identity resolution. Persistence is responsible for metadata and ownership. Storage is currently the database (phase 1).

## 4. Data Model

Current SQL schema for `users` (as implemented in `src/backend/app/db/models.py`):

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  oauth_provider TEXT NOT NULL,
  oauth_sub TEXT NOT NULL,
  email TEXT,
  created_at TIMESTAMP NOT NULL
);
```

Current SQL schema for `tex_files` (as implemented in `src/backend/app/db/models.py`):

```sql
CREATE TABLE tex_files (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  filename TEXT NOT NULL,
  latex_content TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
);
```

Explicit ownership rules:
`tex_files.user_id` is always set from the authenticated user context. All reads and writes must include `user_id` filtering at the query boundary.

Uniqueness and constraints:
`tex_files.filename` is not globally unique; per-user uniqueness is optional and enforced only if required by product.

## 5. Authentication Assumptions

Pre-OAuth identity resolution uses a mock user hardcoded in routes: `mock-user-id`.

Post-OAuth identity resolution maps JWT or session claims to `(provider, provider_user_id)` and then to `users.id`.

Invariants:
Clients never send `user_id`. Backend enforces ownership for every operation. OAuth providers are treated as interchangeable identity sources.

## 6. API Contract

POST /api/tex
Method: POST
Endpoint: `/api/tex`
Request shape:
```json
{
  "filename": "notes.tex",
  "latex": "\\documentclass{article}..."
}
```
Response shape:
```json
{
  "id": "uuid",
  "filename": "notes.tex",
  "created_at": "2026-02-08T12:00:00Z"
}
```
Authorization behavior: user is resolved from the current mock user; OAuth integration is pending.

GET /api/tex
Method: GET
Endpoint: `/api/tex`
Request shape: query params `limit` (default 10, min 1, max 50)
Response shape:
```json
[
  {
    "id": "uuid",
    "filename": "notes.tex",
    "created_at": "2026-02-08T12:00:00Z"
  }
]
```
Authorization behavior: list is filtered by authenticated user.

GET /api/tex/{id}
Method: GET
Endpoint: `/api/tex/{id}`
Request shape: path param `id`
Response shape:
```json
{
  "id": "uuid",
  "filename": "notes.tex",
  "latex": "\\documentclass{article}...",
  "created_at": "2026-02-08T12:00:00Z",
  "updated_at": "2026-02-08T12:00:00Z"
}
```
Authorization behavior: request is rejected if the file is not owned by the authenticated user.

GET /api/tex/{id}/download
Method: GET
Endpoint: `/api/tex/{id}/download`
Request shape: path param `id`
Response shape: `.tex` file download with `Content-Disposition` header
Authorization behavior: same ownership rules as `GET /api/tex/{id}`.

## 7. Storage Strategy

Phase 1 stores LaTeX in `tex_files.latex_content` inside PostgreSQL.

Phase 2 moves LaTeX blobs to object storage (S3 or GCS) while keeping metadata in PostgreSQL. The schema adds `storage_provider` and `storage_key`, and the API contract remains unchanged.

## 8. Dashboard Data Expectations

Downstream consumers expect: `id`, `filename`, `created_at` (list), plus `latex`, `updated_at` (detail).

Typical request flow: `GET /api/tex` for list, `GET /api/tex/{id}` for detail, `GET /api/tex/{id}/download` for export.

## 11. Implementation Map

Database:
- `src/backend/app/db/models.py` — SQLAlchemy models
- `src/backend/app/db/crud.py` — CRUD helpers
- `src/backend/app/db/session.py` — engine + SessionLocal
- `src/backend/app/db/deps.py` — `get_db` dependency

Routes:
- `src/backend/app/routes/tex.py` — `/api/tex` endpoints

## 9. Security and Isolation Rules

All reads and writes are scoped to the authenticated user. No cross-user access is permitted. Server-side validation is the only trusted validation path.

## 10. Design Invariants

LaTeX is the canonical artifact. Clients never provide `user_id`. Ownership is enforced at the database query boundary. API response shapes are stable across storage phases. Storage migration does not alter API contracts.
