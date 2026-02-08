# Backend LaTeX Data Reference

## 1. Title and Metadata

Feature name: LaTeX Storage and Retrieval
Intended audience: Backend and API developers
Status: OAuth-ready, backend-first
Related documents: `docs/BACKEND-REFERENCE.md`, `docs/ARCHITECTURE.md`, `docs/CHECKLIST-BACKEND.md`

## 2. Purpose

This feature defines storage and retrieval of user-owned LaTeX artifacts for backend services. LaTeX is the canonical artifact because all exports and views derive from the `.tex` source. OAuth is treated as identity-only; authorization decisions are enforced by backend ownership rules, not provider-specific scopes.

## 3. System Architecture

```
Client -> FastAPI -> Database -> Storage
```

Auth is responsible for identity resolution. Persistence is responsible for metadata and ownership. Storage is responsible for LaTeX content (DB in phase 1, object storage in phase 2).

## 4. Data Model

SQL schema for `users`:

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  provider TEXT NOT NULL,
  provider_user_id TEXT NOT NULL,
  email TEXT,
  display_name TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (provider, provider_user_id)
);
```

SQL schema for `tex_files`:

```sql
CREATE TABLE tex_files (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  filename TEXT NOT NULL,
  latex TEXT NOT NULL,
  source_pdf_filename TEXT,
  page_count INTEGER,
  size_bytes INTEGER NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX tex_files_user_created_idx ON tex_files(user_id, created_at DESC);
```

Explicit ownership rules:
`tex_files.user_id` is always set from the authenticated user context. All reads and writes must include `user_id` filtering at the query boundary.

Uniqueness and constraints:
`users(provider, provider_user_id)` is unique. `tex_files.filename` is not globally unique; per-user uniqueness is optional and enforced only if required by product.

## 5. Authentication Assumptions

Pre-OAuth identity resolution uses a mock user bound to the request context.

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
  "filename": "notes",
  "latex": "\\documentclass{article}...",
  "source_pdf_filename": "lecture1.pdf",
  "page_count": 3
}
```
Response shape:
```json
{
  "success": true,
  "id": "uuid",
  "created_at": "2026-02-08T12:00:00Z"
}
```
Authorization behavior: user resolved from auth context; unauthenticated requests are rejected.

GET /api/tex
Method: GET
Endpoint: `/api/tex`
Request shape: query params `limit` (default 20), `cursor` (optional)
Response shape:
```json
{
  "success": true,
  "items": [
    {
      "id": "uuid",
      "filename": "notes",
      "created_at": "2026-02-08T12:00:00Z",
      "updated_at": "2026-02-08T12:00:00Z",
      "size_bytes": 12345,
      "page_count": 3
    }
  ],
  "next_cursor": "opaque"
}
```
Authorization behavior: list is filtered by authenticated user.

GET /api/tex/{id}
Method: GET
Endpoint: `/api/tex/{id}`
Request shape: path param `id`
Response shape:
```json
{
  "success": true,
  "id": "uuid",
  "filename": "notes",
  "latex": "\\documentclass{article}...",
  "source_pdf_filename": "lecture1.pdf",
  "page_count": 3,
  "size_bytes": 12345,
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

Phase 1 stores LaTeX in `tex_files.latex` inside PostgreSQL.

Phase 2 moves LaTeX blobs to object storage (S3 or GCS) while keeping metadata in PostgreSQL. The schema adds `storage_provider` and `storage_key`, and the API contract remains unchanged.

## 8. Dashboard Data Expectations

Downstream consumers expect: `id`, `filename`, `created_at`, `updated_at`, `size_bytes`, `page_count`.

Typical request flow: `GET /api/tex` for list, `GET /api/tex/{id}` for detail, `GET /api/tex/{id}/download` for export.

## 9. Security and Isolation Rules

All reads and writes are scoped to the authenticated user. No cross-user access is permitted. Server-side validation is the only trusted validation path.

## 10. Design Invariants

LaTeX is the canonical artifact. Clients never provide `user_id`. Ownership is enforced at the database query boundary. API response shapes are stable across storage phases. Storage migration does not alter API contracts.
