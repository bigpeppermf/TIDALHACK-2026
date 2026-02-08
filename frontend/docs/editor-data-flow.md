# Editor Data Flow (PDF/Image -> LaTeX -> Dashboard -> Editor)

## What is functional now
- Conversion output from `/convert` is persisted as a project record, including generated `latex`.
- Dashboard `View` and `Edit` now route to `/editor?projectId=<id>`.
- `/editor` loads the requested project and autosaves LaTeX edits back to the same project record.
- If `projectId` is missing, `/editor` falls back to the most recent project, then to the default template.
- Frontend is bridged to backend Postgres routes at `/api/tex` (`GET list`, `GET by id`, `POST`, `PUT`).

## Local storage contracts
- `monogram-projects`:
  - Array of `ProjectRecord` objects with fields:
    - `id`, `name`, `status`, `updatedAt`, `updatedAtIso`
    - `latex`
    - `sourceFilename`, `sourceKind` (`pdf` | `image` | `unknown`)
    - `thumbnail` (optional)
    - `ownerId` (Clerk-ready, optional)

## Clerk readiness
- Current UI reads `clerk-user-id` from `localStorage` when present.
- `useProjects(ownerId)` filters dashboard/editor records per owner.
- New projects store `ownerId`, so Clerk user scoping can be enabled by setting that value after auth.

## Backend bridge
- The frontend now uses your existing backend routes directly:
  - `GET /api/tex?limit=...`
  - `GET /api/tex/{id}`
  - `POST /api/tex`
  - `PUT /api/tex/{id}`
- In local development, Vite proxies `/api/*` to `http://localhost:8000`.
- If the backend is unreachable, local fallback records still work for editing.

## Recommended backend shape (for Clerk + DB)
- Table: `projects`
  - `id` (text/uuid, primary key)
  - `owner_id` (text, indexed; Clerk user ID)
  - `name` (text)
  - `status` (text)
  - `latex` (text)
  - `source_filename` (text)
  - `source_kind` (text)
  - `thumbnail` (text nullable)
  - `updated_at` (timestamp)
- API behavior:
  - Validate Clerk session server-side.
  - Enforce `owner_id === auth.userId`.
  - Upsert on `PUT /projects/:id`.
  - Return only caller-owned rows.
