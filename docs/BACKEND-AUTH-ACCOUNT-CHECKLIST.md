# Backend Auth & Account System — Checklist

> Last updated: Feb 8, 2026

Tracks implementation of real user authentication and account handling.

---

## PHASE 0 — Current State (Baseline)

- [x] `users` table exists with `oauth_provider`, `oauth_sub`, `email`, `full_name`, `avatar_url`
- [x] Backend routes use `Depends(get_current_user)`
- [x] `get_current_user` uses Clerk JWT validation
- [x] JWT validation is implemented via `clerk-backend-api` SDK
- [x] Token parsing is implemented
- [x] Auth is dependency-based (no middleware)
- [x] Auth can be bypassed in dev with `AUTH_DEV_BYPASS=1`

---

## PHASE 1 — Auth Strategy Definition

- [x] Auth source: Clerk
- [x] Token type: JWT session token
- [x] Validation: Clerk SDK (`AuthenticateRequestOptions` with audience)
- [x] Issuer + audience verification
- [x] Pattern: FastAPI dependency-based auth

---

## PHASE 2 — JWT Validation

- [x] Accept `Authorization: Bearer <token>` header
- [x] Validate via Clerk SDK (signature, issuer, audience, expiration)
- [x] Extract claims: `sub` (user_id), `iss` (issuer)
- [x] Clerk SDK handles JWKS fetching internally

---

## PHASE 3 — User Resolution

- [x] Map JWT → internal user via `(oauth_provider="clerk", oauth_sub=sub)`
- [x] If user exists: load and update profile (email, name, avatar)
- [x] If user does not exist: create user row with identity + profile
- [x] Clerk user lookup for email, full_name, avatar_url

---

## PHASE 4 — Replace Mock Dependency

- [x] Remove hardcoded user in `deps.py`
- [x] Implement real `get_current_user`: reads JWT → validates → resolves user
- [x] All protected routes use `Depends(get_current_user)`

---

## PHASE 5 — Data Ownership Enforcement

- [x] All queries filter by `user_id`
- [x] Reject access to other users' tex files
- [x] Never accept `user_id` from client

---

## PHASE 6 — Failure Handling

- [x] Missing token → 401
- [x] Invalid token → 401 (`ClerkAuthError`)
- [x] Expired token → 401
- [x] Missing issuer match → 401
- [x] Clerk config error → 500 (`ClerkConfigError`)
- [x] Clerk service failure → 502 (`ClerkServiceError`)
- [x] User resolution failure → 500 (logged)

---

## PHASE 7 — Testing

- [ ] Unit test JWT decoding
- [ ] Unit test user creation on first login
- [ ] Unit test repeated login reuse
- [ ] Route-level auth tests
