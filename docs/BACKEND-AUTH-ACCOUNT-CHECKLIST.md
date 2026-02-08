# Backend Auth & Account System — Checklist

This document tracks implementation of real user authentication and account handling
to replace the current mock-user setup.

Scope:
- Backend user identity
- JWT validation
- User persistence
- Request-level auth enforcement

Out of scope:
- UI styling
- Permissions/roles beyond user ownership
- Multi-tenant orgs (future)

---

## PHASE 0 — Current State (Baseline)

- [x] `users` table exists
- [x] `oauth_provider` column exists
- [x] `oauth_sub` column exists
- [x] Backend routes use `Depends(get_current_user)`
- [x] `get_current_user` uses Clerk JWT validation
- [x] JWT validation is implemented
- [x] Token parsing is implemented
- [x] No auth middleware (dependency-based only)

---

## PHASE 1 — Auth Strategy Definition

- [x] Choose auth source (Clerk)
- [x] Choose token type (JWT session token)
- [ ] Decide validation method
  - [x] Clerk public keys (JWKS)
  - [x] Issuer + audience verification
- [x] Decide backend pattern
  - [x] Dependency-based auth (FastAPI)
  - [ ] Optional middleware (future)

---

## PHASE 2 — JWT Validation

- [x] Accept `Authorization: Bearer <token>` header
- [x] Decode JWT without trusting payload
- [ ] Validate:
  - [x] Signature
  - [x] Issuer
  - [x] Audience
  - [x] Expiration
- [ ] Extract claims:
  - [x] `sub`
  - [x] `iss`
  - [x] `email` (if present)

---

## PHASE 3 — User Resolution

- [x] Map JWT → internal user
- [ ] Lookup user by:
  - [x] `oauth_provider`
  - [x] `oauth_sub`
- [ ] If user exists:
  - [x] Load user
- [ ] If user does not exist:
  - [x] Create user row
  - [x] Store provider + sub
  - [x] Store email (nullable)

---

## PHASE 4 — Replace Mock Dependency

- [x] Remove hardcoded user in `deps.py`
- [x] Implement real `get_current_user`:
  - [x] Reads JWT
  - [x] Validates token
  - [x] Resolves user
- [ ] Ensure all protected routes still use:
  - [x] `Depends(get_current_user)`

---

## PHASE 5 — Data Ownership Enforcement

- [x] Ensure all queries filter by `user_id`
- [ ] Reject access to:
  - [x] Other users’ tex files
  - [x] Other users’ conversions
- [x] Never accept `user_id` from client

---

## PHASE 6 — Failure Handling

- [x] Missing token → 401
- [x] Invalid token → 401
- [x] Expired token → 401
- [x] Unknown provider → 401
- [x] User lookup failure → 500 (logged)

---

## PHASE 7 — Testing

- [ ] Unit test JWT decoding
- [ ] Unit test user creation on first login
- [ ] Unit test repeated login reuse
- [ ] Route-level auth tests
