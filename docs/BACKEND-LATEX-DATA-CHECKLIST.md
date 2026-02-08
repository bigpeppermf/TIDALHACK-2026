# Backend LaTeX Data Checklist

## PHASE 1 — Data & Schema

- [x] Select PostgreSQL as primary datastore
- [x] Create `users` table
- [ ] Add unique constraint on `users(provider, provider_user_id)`
- [x] Create `tex_files` table
- [x] Add foreign key `tex_files.user_id -> users.id`
- [ ] Add index on `tex_files(user_id, created_at DESC)`

## PHASE 2 — Backend API

- [x] Implement `POST /api/tex`
- [x] Implement `GET /api/tex`
- [x] Implement `GET /api/tex/{id}`
- [x] Implement `GET /api/tex/{id}/download`
- [x] Enforce ownership check in each handler
- [ ] Inject current user via dependency

## PHASE 3 — Auth Compatibility

- [x] Provide mock auth identity for local development
- [ ] Accept OAuth identity claims from JWT or session
- [ ] Map `(provider, provider_user_id)` to `users.id`
- [ ] Reject any client-provided `user_id`

## PHASE 4 — Storage

- [x] Store LaTeX content in `tex_files.latex_content`
- [ ] Persist `size_bytes` for each record
- [ ] Define migration fields for object storage (`storage_provider`, `storage_key`)
- [ ] Ensure API responses are unchanged after migration

## PHASE 5 — Client Integration

- [x] Return list metadata required by clients
- [x] Support `.tex` download with `Content-Disposition`
- [ ] Return consistent error payloads for UI handling

## PHASE 6 — Hardening & Edge Cases

- [ ] Return 401 for unauthenticated requests
- [ ] Return 403 for unauthorized access to another user’s file
- [ ] Return 404 for missing `id`
- [ ] Enforce maximum payload size for LaTeX content
- [ ] Validate filename normalization rules

## PHASE 7 — Demo & Validation

- [x] Run automated tests for DB + API flows (`tests/dbtex`)
- [ ] Run manual API tests for all four endpoints
- [ ] Verify dashboard list and download flows
- [ ] Confirm stable behavior under repeated requests
