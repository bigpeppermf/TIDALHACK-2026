# Frontend Auth & Account – Checklist

> Last updated: Feb 8, 2026

---

## PHASE 1 — Install & Initialize Clerk

- [x] Install `@clerk/vue` package
- [x] Add `VITE_CLERK_PUBLISHABLE_KEY` to `.env`
- [x] Register Clerk plugin in `main.ts` via `app.use(clerkPlugin, { publishableKey })`
- [x] Wrap app with `<SignedIn>` / `<SignedOut>` components as needed

## PHASE 2 — Sign-In / Sign-Up UI

- [x] Add `<SignInButton>` and `<SignUpButton>` to landing page
- [x] Clerk-hosted sign-in / sign-up flow works end-to-end
- [x] User avatar and name shown in top bar when signed in (`<UserButton>`)

## PHASE 3 — Token Attachment

- [x] Create `authFetch` utility (`lib/authFetch.ts`)
- [x] Use `useAuth().getToken()` to obtain Clerk session JWT
- [x] Attach `Authorization: Bearer <token>` header to all API calls
- [x] All composables (`useConvert`, `useExport`, `useProjects`) use `authFetch`

## PHASE 4 — Route Guards

- [x] Protect `/dashboard`, `/editor`, `/settings` routes
- [x] Redirect unauthenticated users to `/` (home)
- [x] Use `useAuth().isSignedIn` in `router.beforeEach` guard
- [x] Allow public access to `/` and `/convert`

## PHASE 5 — Remove Legacy Auth

- [x] Remove `localStorage` user ID fallback
- [x] Remove any hardcoded user identifiers
- [x] All user identity comes from Clerk session

## PHASE 6 — Account Features

- [x] Settings page shows user profile info
- [x] Clerk `<UserButton>` allows profile management
- [ ] Account deletion flow (Clerk dashboard only for now)
- [ ] Email change / verification flow

## PHASE 7 — Demo & Validation

- [x] Sign in → create project → see it in dashboard
- [x] Sign out → protected routes redirect to home
- [x] Token refreshes automatically via Clerk SDK
- [ ] Test with multiple accounts to verify data isolation
