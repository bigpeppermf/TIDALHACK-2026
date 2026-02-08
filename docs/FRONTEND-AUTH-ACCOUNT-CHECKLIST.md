# Frontend Auth & Account System — Checklist

Tracks frontend work required to support real user authentication.

---

## PHASE 0 — Current State

- [x] Clerk placeholder user ID stored in localStorage
- [x] Used only for filtering local projects
- [x] No auth headers on API calls
- [x] No session awareness in backend

---

## PHASE 1 — Clerk Setup

- [ ] Install Clerk SDK
- [ ] Initialize Clerk provider
- [ ] Add sign-in / sign-up UI
- [ ] Confirm session token availability

---

## PHASE 2 — API Auth Integration

- [ ] Extract session JWT
- [ ] Attach token to all API calls:
  - `Authorization: Bearer <token>`
- [ ] Remove reliance on localStorage user ID

---

## PHASE 3 — UX Guards

- [ ] Block dashboard access when signed out
- [ ] Redirect unauthenticated users
- [ ] Handle 401 responses gracefully

---

## PHASE 4 — Cleanup

- [ ] Remove `clerk-user-id` usage
- [ ] Trust backend for identity
