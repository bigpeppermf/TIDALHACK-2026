# Backend Auth & Account System — Reference

> Last updated: Feb 8, 2026

---

## Identity Model

The backend does NOT trust frontend user IDs.

Identity is derived from:
- OAuth provider: `"clerk"`
- OAuth subject: `sub` claim from JWT

These map to:
- `users.oauth_provider`
- `users.oauth_sub`

---

## Token Flow

1. Frontend authenticates user via Clerk (`@clerk/vue`)
2. Clerk issues a session JWT
3. Frontend sends: `Authorization: Bearer <JWT>` on every API call
4. Backend validates token via `clerk-backend-api` SDK
5. Backend resolves or creates user (with profile info from Clerk API)
6. Request proceeds with internal `user.id`

---

## Implementation (Current)

### `app/auth/clerk.py`
- `authenticate_request(method, url, headers)` → `ClerkIdentity`
- Uses `Clerk(bearer_auth=secret_key)` SDK client
- Validates via `AuthenticateRequestOptions(audience=[audience])`
- Checks `is_signed_in` on request state
- Verifies issuer from JWT payload
- Fetches full user profile via `clerk.users.get(user_id)`
- Returns `ClerkIdentity(user_id, email, full_name, avatar_url)`

### `app/deps.py`
- `get_current_user(request, authorization, db)` → `User`
- If `AUTH_DEV_BYPASS=1`: returns fixed dev user (UUID `00000000-...0001`)
- Otherwise: calls `authenticate_request()` → resolves/creates User
- Auto-updates profile fields on subsequent logins
- Error mapping: `ClerkAuthError` → 401, `ClerkConfigError` → 500, `ClerkServiceError` → 502

---

## Required Environment Variables

- `CLERK_SECRET_KEY` — Clerk backend API key
- `CLERK_ISSUER` — Expected JWT issuer (`https://<clerk-domain>`)
- `CLERK_AUDIENCE` — Expected JWT audience

Optional (dev only):
- `AUTH_DEV_BYPASS=1` to bypass auth locally

---

## `get_current_user` Responsibility

Must:
- Parse Authorization header
- Validate JWT via Clerk SDK
- Extract identity claims
- Resolve DB user (create if first login)
- Update profile if changed
- Return SQLAlchemy User object

Must NOT:
- Trust frontend-provided IDs
- Create users without validation
- Leak auth logic into routes

---

## Security Rules

- Backend is source of truth for identity
- Client never sends `user_id`
- JWT must be validated on every request
- All queries must be scoped to `user.id`
- Startup validation ensures auth env vars are present

---

## Error Classes

| Class | HTTP | When |
|---|---|---|
| `ClerkAuthError` | 401 | Missing/invalid/expired token, bad issuer |
| `ClerkConfigError` | 500 | Missing `CLERK_SECRET_KEY`, `CLERK_ISSUER`, or `CLERK_AUDIENCE` |
| `ClerkServiceError` | 502 | Clerk API call failed |

---

## User Model

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  oauth_provider TEXT NOT NULL,
  oauth_sub TEXT NOT NULL,
  email TEXT,
  full_name TEXT,
  avatar_url TEXT,
  created_at TIMESTAMP NOT NULL
);
```

---

## Non-Goals

- No refresh token logic (Clerk handles this)
- No session storage
- No cookies (Bearer token only)
- No multi-tenant/org support (future)
