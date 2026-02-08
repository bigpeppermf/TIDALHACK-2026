# Backend LaTeX Data Checklist

> Last updated: Feb 8, 2026

---

## PHASE 1 — Data & Schema

- [x] Select PostgreSQL as primary datastore
- [x] Create `users` table (UUID pk, oauth fields, email, full_name, avatar_url)
- [x] Create `tex_files` table (UUID pk, user_id FK, filename, latex_content, timestamps)
- [x] Add foreign key `tex_files.user_id -> users.id` with `ON DELETE CASCADE`
- [ ] Add unique constraint on `users(oauth_provider, oauth_sub)`
- [ ] Add index on `tex_files(user_id, created_at DESC)`

## PHASE 2 — Backend API

- [x] Implement `POST /api/tex` (create new file)
- [x] Implement `GET /api/tex` (list recent, with `limit` param, min 1, max 50)
- [x] Implement `GET /api/tex/{id}` (get single file with content)
- [x] Implement `PUT /api/tex/{id}` (update filename and/or latex)
- [x] Implement `GET /api/tex/{id}/download` (`.tex` file download)
- [x] Implement `GET /api/tex/{id}/files` (inferred project file tree)
- [x] Implement `POST /api/tex/{id}/compile` (server-side pdflatex → base64 PDF)
- [x] Enforce ownership check in each handler
- [x] Inject current user via `Depends(get_current_user)`

## PHASE 3 — Auth Compatibility

- [x] Dev auth bypass for local development (`AUTH_DEV_BYPASS=1`)
- [x] Accept Clerk JWT session tokens
- [x] Map `(provider, oauth_sub)` to `users.id` via `get_current_user`
- [x] Reject any client-provided `user_id`

## PHASE 4 — Storage

- [x] Store LaTeX content in `tex_files.latex_content`
- [ ] Persist `size_bytes` for each record
- [ ] Define migration fields for object storage (`storage_provider`, `storage_key`)

## PHASE 5 — Client Integration

- [x] Return list metadata required by clients (`id`, `filename`, `created_at`)
- [x] Return detail fields (`latex`, `updated_at`)
- [x] Support `.tex` download with `Content-Disposition`
- [x] Return project file tree from LaTeX source analysis

## PHASE 6 — Hardening & Edge Cases

- [x] Return 401 for unauthenticated requests
- [x] Return 404 for missing `id`
- [x] Return 422 for missing required fields
- [ ] Return 403 for unauthorized access to another user's file (currently 404)
- [ ] Enforce maximum payload size for LaTeX content
- [ ] Validate filename normalization rules

## PHASE 7 — Demo & Validation

- [x] Run automated tests for DB + API flows
- [ ] Run manual API tests for all endpoints
- [ ] Verify dashboard list and download flows
- [ ] Confirm stable behavior under repeated requests
