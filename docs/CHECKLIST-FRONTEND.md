# 🎨 Teammate 1 — Frontend Checklist

> **Role:** Frontend Design & Development
> **Stack:** Vue 3, Clerk Auth, Pinia, Motion-v, shadcn-vue, KaTeX, CodeMirror, PDF.js, TailwindCSS v4
> **Work in:** `frontend/`
> **Code ref:** `docs/FRONTEND-REFERENCE.md`
> Last updated: Feb 8, 2026

---

## 🏁 Phase 1 — Setup (Hours 0–4)

### With Teammate 2

- [x] Align on project scope and review docs together
- [x] Review API contract in `ARCHITECTURE.md` — agree on request/response shapes
- [x] Confirm both dev servers run without port conflicts (you: `:5173`, them: `:8000`)

### Solo

- [x] Scaffold Vue 3 project: `npm create vue@latest` in `frontend/`
- [x] Pick: TypeScript ✅, Vue Router ✅, Pinia ✅, ESLint ✅
- [x] Install deps: `npm install motion-v katex pdfjs-dist mathjax @clerk/vue vue-codemirror @vueuse/core lucide-vue-next`
- [x] Install dev deps: `npm install -D tailwindcss @tailwindcss/vite tw-animate-css`
- [x] Initialize shadcn-vue: `npx shadcn-vue@latest init`
- [x] Add core shadcn components: `npx shadcn-vue@latest add button card input textarea sonner`
- [x] Configure Tailwind v4 (`@theme inline` in `main.css`, `@tailwindcss/vite` plugin)
- [x] Verify `npm run dev` serves on `:5173`
- [x] Create `VITE_CLERK_PUBLISHABLE_KEY=pk_test_...` in `frontend/.env`
- [x] Set up Vite proxy: `/api/*` → `http://localhost:8000` in `vite.config.ts`
- [x] Set up Vue Router: `/`, `/convert`, `/dashboard`, `/editor`, `/settings`
- [x] Initialize Clerk plugin in `main.ts`
- [x] Initialize Pinia store
- [x] Create empty page shells for all routes
- [x] Start Figma designs: upload screen, loading screen, result screen

**✅ Milestone:** Vue dev server running. Router works. Clerk auth initialized. Figma wireframes started.

---

## 🔗 Phase 2 — Core Components (Hours 4–10)

### Upload Flow

- [x] Build `UploadZone.vue` — drag-and-drop area + file picker button
- [x] Add PDF/image filename preview after file is selected
- [x] File validation: only jpeg/png/webp/pdf, max 10 MB, show error if wrong
- [x] Create `useConvert` composable
- [x] Wire upload → calls `POST /api/convert` via Vite proxy → receives LaTeX string

### Result Display

- [x] Build `ResultView.vue` — split layout: PDF preview left, LaTeX right
- [x] Build LaTeX preview with KaTeX rendering (full document rendering with section/list/math support)
- [x] PDF viewer with PDF.js — page navigation (prev/next buttons)
- [x] Source code tab — editable LaTeX textarea
- [x] Copy LaTeX code button
- [x] Download .tex file button
- [x] Error handling for PDF loading
- [x] Loading spinner during PDF load
- [x] Build `LoadingAnimation.vue` — animated stages with progress bar + rotating icon

### Export Actions

- [x] Create `useExport` composable with multi-format support (PDF/HTML/TEX)
- [x] Support both backend-stored exports (`/api/tex-files/{id}/export`) and raw `.tex` download (`/api/export`)
- [x] "Copy to Clipboard" button — copies raw LaTeX string
- [x] "Download .tex" button — saves file locally
- [x] Content-Disposition filename parsing from server response

### Integration

- [x] Connect full flow: upload → loading → result → edit → export
- [x] Test with Teammate 2's live backend
- [x] After conversion, auto-save project to backend via `POST /api/tex`
- [x] "Open In Editor" button routes to `/editor?projectId=...`

**✅ Milestone:** Full UI flow works end-to-end with real backend.

---

## 📊 Phase 2.5 — Dashboard & Editor

### Dashboard (`DashboardPage.vue`)

- [x] Auth guard: redirect to `/` if not signed in
- [x] Fetch projects from backend (`GET /api/tex`)
- [x] Display project list with `ProjectRow.vue` component
- [x] Empty state with upload CTA (`EmptyState.vue`)
- [x] "New Conversion" button → navigate to `/convert`
- [x] "View" / "Edit" → navigate to `/editor?projectId=...`
- [x] Auth error handling (session expiry)

### Editor (`EditorPage.vue`)

- [x] CodeMirror-based LaTeX editor (`LatexEditorPanel.vue`)
- [x] PDF preview panel using PDF.js (compiled PDF from backend)
- [x] Server-side compile via `POST /api/tex/{id}/compile`
- [x] KaTeX-based preview fallback (renders LaTeX sections, lists, math)
- [x] Autosave: debounced `PUT /api/tex/{id}` on code changes (500 ms)
- [x] Save status indicator (idle / saving / saved / error)
- [x] Compile status indicator (idle / dirty / compiling / compiled / error)
- [x] File sidebar: inferred project files from `GET /api/tex/{id}/files`
- [x] Zoom controls for PDF viewer
- [x] Copy / Download / Share buttons
- [x] Share via Web Share API (or clipboard fallback)
- [x] Project hydration from route query param (`projectId`)
- [x] Fallback to most recent project or default template
- [x] Local-only project promotion (auto-save to backend before compile)
- [x] Auth error handling throughout

### Supporting Components

- [x] `ComparisonPanel.vue` — side-by-side document comparison
- [x] `DashboardTopBar.vue` — search bar + upload button
- [x] `ErrorState.vue` — error display with retry
- [x] `LoadingSkeleton.vue` — skeleton loading placeholders
- [x] `ProjectRow.vue` — project list row with thumbnail, status, hover actions

---

## 🔐 Phase 2.75 — Clerk Auth Integration

- [x] Install `@clerk/vue`
- [x] Initialize Clerk plugin in `main.ts` with `VITE_CLERK_PUBLISHABLE_KEY`
- [x] Add `SignInButton` / `UserButton` to `AppNavbar.vue`
- [x] Router auth guards: `/dashboard`, `/editor`, `/settings` require sign-in
- [x] `useAuth()` provides `userId`, `getToken`, `isSignedIn`
- [x] Auth token attached to API calls via `Authorization: Bearer <token>`
- [x] `useProjects(userId)` scopes all project data per user
- [x] Handle 401/403 responses gracefully (session expiry messaging)
- [x] Removed reliance on `localStorage` user ID

---

## ✨ Phase 3 — Polish & Animations (Hours 10–18)

### Landing Page

- [x] Hero section: 4-phase animation (handwriting → selection → spring fall → mouse glow)
- [x] Hero section: "monogram" title split into "mono" + "gram" with dramatic purple shadow
- [x] Color theme: pure black background, darker purple primary (`270 60% 55%`)
- [x] Font setup: Rubik Marker Hatch (headings) + Domine (body) + Caveat (handwriting) via Google Fonts
- [x] `FeaturesGrid.vue` — bento grid of 6 features with intersection observer animations
- [x] `HowItWorks.vue` — 3-step vertical timeline with scroll-triggered animations
- [x] `AppNavbar.vue` — fixed vertical nav (desktop) + top nav (mobile) with Clerk buttons
- [x] `AppFooter.vue` — footer with logo, links, copyright

### Convert Page Animations

- [x] Step indicator bar (Upload → Processing → Result)
- [x] Grid background pattern
- [x] Error state with icon + retry button
- [x] "Open In Editor" and "Retry Cloud Save" buttons in result view

### Motion Animations

- [ ] Upload zone: fade-in on mount (`initial={{ opacity: 0, y: 20 }}`)
- [ ] Upload zone: subtle scale on hover (`hover={{ scale: 1.02 }}`)
- [ ] Result panels: slide in from sides (`initial={{ x: -100 }}`)
- [ ] Buttons: press feedback (`tap={{ scale: 0.95 }}`)
- [ ] Page transitions: fade on route change

### Error States

- [x] API unreachable → friendly error message in UI
- [x] Bad PDF → "Conversion Failed" with error detail
- [x] Auth session expired → messaging in dashboard and editor

### Settings Page

- [x] Profile section with display name + email inputs
- [x] API Keys section (stub)
- [x] Notifications section with toggle switches
- [x] Appearance section (dark mode default note)
- [x] Language section (English only note)
- [x] Sidebar navigation between sections

### Responsive

- [ ] Test on phone viewport (375px)
- [ ] Stack split-panel to vertical on mobile
- [ ] Touch-friendly upload zone

### Nice-to-Have (if time)

- [ ] Dark mode toggle
- [ ] Context dropdown: Math / Chemistry / Physics / General
- [ ] History page: save past conversions in localStorage
- [ ] Camera capture button (mobile)

**✅ Milestone:** App looks demo-ready. Animations are smooth. Edge cases handled.

---

## 🎤 Phase 4 — Demo Prep (Hours 18–24)

- [ ] Test all demo PDFs in the UI (3–5 files)
- [ ] Fix any visual bugs found during testing
- [ ] Help build slide deck (Problem → Solution → Demo → Tech → Future)
- [ ] Ensure app looks great on the demo machine/projector resolution
- [ ] Practice live demo 2–3 times

---

## 🪓 Cut List (drop these first if behind)

1. ❌ Dark mode toggle
2. ❌ History / localStorage (replaced by backend persistence)
3. ❌ Camera capture
4. ❌ Context dropdown (backend hardcodes "general")
5. ❌ Mobile responsiveness (demo on laptop)
6. ~~❌ CodeMirror editor~~ → ✅ Done (replaced textarea)

### 🛡️ Never Cut

- ✅ Upload → Loading → Result flow
- ✅ KaTeX preview rendering
- ✅ Copy + Download buttons
- ✅ Clerk auth (required for dashboard + editor)
- ✅ Dashboard with project list
- ✅ Editor with autosave + compile
- ✅ Landing page hero animation
- ✅ Loading animation (makes demo feel polished)

---

## 🏆 Your Demo Day Checklist

- [ ] Frontend running on `:5173`
- [ ] Connected to backend on `:8000` via Vite proxy
- [ ] `VITE_CLERK_PUBLISHABLE_KEY` set in `frontend/.env`
- [ ] Clerk sign-in works
- [ ] App looks good on demo screen resolution
- [ ] No console errors in browser
- [ ] All demo PDFs load and display correctly
- [ ] Dashboard shows saved projects
- [ ] Editor loads, autosaves, and compiles to PDF
