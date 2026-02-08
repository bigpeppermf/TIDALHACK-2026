# Backend Auth & Account System — Reference

This document explains how authentication is expected to work
once fully implemented.

---

## Identity Model

The backend does NOT trust frontend user IDs.

Identity is derived from:
- OAuth provider (e.g. `clerk`)
- OAuth subject (`sub` claim)

These map to:
- `users.oauth_provider`
- `users.oauth_sub`

---

## Token Flow

1. Frontend authenticates user via Clerk
2. Clerk issues a session JWT
3. Frontend sends:
   Authorization: Bearer <JWT>
4. Backend validates token via Clerk SDK
5. Backend resolves or creates user
6. Request proceeds with internal `user.id`

---

## Implementation Notes (Current)

- Auth validation lives in `src/backend/app/auth/clerk.py`.
- `get_current_user` in `src/backend/app/deps.py`:
  - Validates the Clerk JWT via Clerk SDK
  - Resolves or creates the `users` row
  - Returns the SQLAlchemy `User` object
- Clerk SDK handles token verification and JWKS fetching internally.

---

## Required Environment Variables

- `CLERK_SECRET_KEY`
- `CLERK_ISSUER`
- `CLERK_AUDIENCE`

Optional (dev only):
- `AUTH_DEV_BYPASS=1` to bypass auth locally

---

## `get_current_user` Responsibility

Must:
- Parse Authorization header
- Validate JWT
- Extract identity claims
- Resolve DB user
- Return SQLAlchemy user object

Must NOT:
- Trust frontend-provided IDs
- Create users without validation
- Leak auth logic into routes

---

## Security Rules

- Backend is source of truth
- Client never sends `user_id`
- JWT must be validated on every request
- All queries must be scoped to `user.id`

---

## Supported Providers

Initial:
- Clerk

Future:
- Additional OAuth providers
- Multiple identities per user (optional)

---

## Non-Goals (Explicit)

- No refresh token logic (Clerk handles this)
- No session storage
- No cookies (Bearer token only)
