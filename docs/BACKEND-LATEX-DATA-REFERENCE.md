# Backend LaTeX Data – Reference

> Canonical reference for the LaTeX storage API.

---

## 1. Data Models

### User (db/models.py)

| Column | Type | Notes |
|---|---|---|
| id | UUID (PK) | `server_default=gen_random_uuid()` |
| oauth_provider | String(32) | e.g. `"clerk"` |
| oauth_sub | String(255) | Clerk user ID (`user_…`) |
| email | String(320), nullable | Optional profile email |
| full_name | String(200), nullable | Display name from Clerk |
| avatar_url | String(2048), nullable | Profile image URL |
| created_at | DateTime(tz) | Auto-set |
| updated_at | DateTime(tz) | Auto-set on update |

### TexFile (db/models.py)

| Column | Type | Notes |
|---|---|---|
| id | UUID (PK) | `server_default=gen_random_uuid()` |
| user_id | UUID (FK → users.id) | Cascade delete |
| filename | String(255) | Default `"untitled.tex"` |
| latex_content | Text | Full LaTeX source |
| created_at | DateTime(tz) | Auto-set |
| updated_at | DateTime(tz) | Auto-set on update |

Relationships: `User.tex_files` ↔ `TexFile.owner`.

---

## 2. Session & DB

- **Engine**: Async SQLAlchemy 2.0 via `create_async_engine` with `pool_pre_ping=True`, pool size 5.
- **Session factory**: `async_sessionmaker(expire_on_commit=False)`.
- **DB URL**: `DATABASE_URL` env var (or default `postgresql+psycopg://postgres:postgres@localhost:5432/tidalhack`).
- **Dependency**: `get_db()` yields an `AsyncSession` per request.
- **Tables**: Created at startup via `Base.metadata.create_all` (sync fallback using `psycopg2`).

---

## 3. CRUD Layer (db/crud.py)

| Function | Signature | Notes |
|---|---|---|
| `create_tex_file` | `(db, user_id, filename, latex)` | Returns new `TexFile` |
| `get_tex_file` | `(db, file_id, user_id)` | Ownership-scoped lookup |
| `list_tex_files` | `(db, user_id, limit=20)` | Ordered by `updated_at DESC`, capped 1-50 |
| `update_tex_file` | `(db, file_id, user_id, filename?, latex?)` | Partial update, returns updated or `None` |
| `delete_tex_file` | `(db, file_id, user_id)` | Returns `True`/`False` |

All functions filter by `user_id` to enforce data ownership.

---

## 4. API Contract

Base path: `/api/tex` (router prefix in `routes/tex.py`).

### POST /api/tex

Create a new TeX file.

- **Auth**: Required (Clerk JWT)
- **Body**: `{ "filename": "doc.tex", "latex": "\\documentclass{article}..." }`
  - `filename` defaults to `"untitled.tex"`, `latex` defaults to `""`
- **Response 201**: `{ "id", "filename", "latex", "created_at", "updated_at" }`

### GET /api/tex

List user's TeX files.

- **Auth**: Required
- **Query**: `limit` (int, default 20, min 1, max 50)
- **Response 200**: `{ "files": [{ "id", "filename", "created_at", "updated_at" }] }`
  - Note: list items omit `latex_content` for performance.

### GET /api/tex/{id}

Get single file with content.

- **Auth**: Required
- **Response 200**: `{ "id", "filename", "latex", "created_at", "updated_at" }`
- **Response 404**: Not found or not owned.

### PUT /api/tex/{id}

Update file.

- **Auth**: Required
- **Body**: `{ "filename"?: "new.tex", "latex"?: "..." }`
- **Response 200**: Updated file object.
- **Response 404**: Not found or not owned.

### DELETE /api/tex/{id}

Delete file.

- **Auth**: Required
- **Response 200**: `{ "deleted": true }`
- **Response 404**: Not found or not owned.

### GET /api/tex/{id}/download

Download as `.tex` file.

- **Auth**: Required
- **Headers**: `Content-Disposition: attachment; filename="<filename>"`
- **Response 200**: Plain text LaTeX content.

### GET /api/tex/{id}/files

Inferred file tree from LaTeX source.

- **Auth**: Required
- **Response 200**: `{ "files": ["main.tex", "images/fig1.png", ...] }`
  - Extracts `\input`, `\include`, `\includegraphics`, `\bibliography` references.

### POST /api/tex/{id}/compile

Server-side compilation.

- **Auth**: Required
- **Response 200**: `{ "pdf_base64": "...", "log": "..." }`
- **Response 422**: Compilation failure with log output.
- **Implementation**: Writes temp `.tex` file → runs `pdflatex` twice → reads PDF → returns base64.

---

## 5. Auth Flow

1. Frontend sends `Authorization: Bearer <clerk_session_token>`.
2. `get_current_user(request, db)` (in `deps.py`) authenticates via Clerk SDK.
3. Calls `clerk_authenticate(token)` which returns `ClerkIdentity(user_id, email, first_name, last_name, image_url)`.
4. Upserts user row: `INSERT … ON CONFLICT (oauth_provider, oauth_sub) DO UPDATE`.
5. Returns `User` ORM object — injected into route handlers.
6. Dev bypass: If `AUTH_DEV_BYPASS=1`, skips Clerk and uses a fixed dev user.

---

## 6. Implementation Map

| Concern | File |
|---|---|
| Models | `src/backend/app/db/models.py` |
| CRUD | `src/backend/app/db/crud.py` |
| DB session | `src/backend/app/db/session.py` |
| DB dependency | `src/backend/app/db/deps.py` |
| Tex routes | `src/backend/app/routes/tex.py` |
| Compile + files | `src/backend/app/routes/tex.py` |
| Auth dependency | `src/backend/app/deps.py` |
| Clerk auth | `src/backend/app/auth/clerk.py` |
| LaTeX tools | `src/backend/app/utils/latex_tools.py` |
