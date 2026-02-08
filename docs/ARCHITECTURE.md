# 🏗️ monogram — Architecture & API Contract

> **Shared reference for both teammates — system design, API shape, env vars**
> Last updated: Feb 8, 2026 (v3 — math rendering, download dropdowns, dashboard preview, compiler UX)

---

## System Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
│  Vue 3 · Clerk Auth · Pinia · Motion-v · shadcn-vue · KaTeX     │
│  CodeMirror · PDF.js · vue-router · @vueuse/core                 │
│                                                                  │
│  ┌──────────┐ ┌──────────┐ ┌───────────┐ ┌────────────────────┐ │
│  │  Upload   │ │ Dashboard│ │  Editor   │ │   Settings         │ │
│  │  Zone     │ │ (list)   │ │ (CM+PDF)  │ │                    │ │
│  └────┬─────┘ └────┬─────┘ └─────┬─────┘ └────────────────────┘ │
│       │             │             │                               │
└───────┼─────────────┼─────────────┼───────────────────────────────┘
        │             │             │
        ▼             ▼             ▼
   Vite dev proxy  /api/*  →  http://localhost:8000
        │
┌───────┼──────────────────────────────────────────────┐
│       ▼                                              │
│              BACKEND (Python · FastAPI)               │
│                                                      │
│  ┌───────────────┐ ┌───────────────┐ ┌─────────────┐│
│  │POST /api/     │ │ /api/tex CRUD │ │ /api/tex-   ││
│  │  convert      │ │ + /compile    │ │ files/export││
│  └──────┬────────┘ └──────┬────────┘ └─────────────┘│
│         │                  │                         │
│  ┌──────┴──────────────────┴─────────────────┐       │
│  │  Clerk JWT Auth · PostgreSQL · pdflatex   │       │
│  │  pandoc · SQLAlchemy                      │       │
│  └───────────────────────────────────────────┘       │
└──────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────┐
│   Google Gemini API  │
│   gemini-2.5-flash   │
└─────────────────────┘
```

---

## API Contract

### `POST /api/convert`

**Request:**
- Content-Type: `multipart/form-data`
- Body field: `file` (PDF or image — jpeg/png/webp, max 10 MB)
- Query param: `context` (optional — `"general"` | `"math"` | `"chemistry"` | `"physics"`)

**Success Response (200):**
```json
{
  "success": true,
  "latex": "\\documentclass{article}\n\\begin{document}\n...\n\\end{document}",
  "raw_text": "Raw Gemini text output (all pages combined)",
  "processing_time_ms": 2340
}
```

**Error Responses:**

| Code | When | Body |
|---|---|---|
| 422 | Bad file format / invalid PDF | `{ "success": false, "error": "Supported formats: jpeg, png, webp, pdf" }` |
| 413 | File > 10 MB | `{ "success": false, "error": "File too large (max 10MB)" }` |
| 429 | Gemini rate limit | `{ "success": false, "error": "Gemini rate limit" }` |
| 500 | Gemini API error | `{ "success": false, "error": "Gemini API error: ..." }` |
| 503 | Gemini down | `{ "success": false, "error": "Service unavailable" }` |

---

### `GET /api/health`

**Response (200):**
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

---

### `POST /api/export`

**Request:**
```json
{
  "latex": "\\documentclass{article}\\n...",
  "filename": "my_notes"
}
```

**Response:** File download (`application/x-tex`)

---

### `GET /api/tex`

List recent tex files for the authenticated user.

**Query params:** `limit` (default 10, min 1, max 50)

**Response (200):**
```json
[
  { "id": "uuid", "filename": "notes.tex", "created_at": "2026-02-08T12:00:00Z" }
]
```

---

### `GET /api/tex/{id}`

Get a single tex file with full content.

**Response (200):**
```json
{
  "id": "uuid",
  "filename": "notes.tex",
  "latex": "\\documentclass{article}...",
  "created_at": "2026-02-08T12:00:00Z",
  "updated_at": "2026-02-08T12:00:00Z"
}
```

---

### `POST /api/tex`

Create a new tex file.

**Request:**
```json
{ "filename": "notes.tex", "latex": "\\documentclass{article}..." }
```

**Response (200):**
```json
{ "id": "uuid", "filename": "notes.tex", "created_at": "2026-02-08T12:00:00Z" }
```

---

### `PUT /api/tex/{id}`

Update an existing tex file (filename and/or latex content).

**Request:**
```json
{ "filename": "updated.tex", "latex": "\\documentclass{article}..." }
```

**Response (200):**
```json
{ "id": "uuid", "filename": "updated.tex", "updated_at": "2026-02-08T12:00:00Z" }
```

---

### `DELETE /api/tex/{id}`

Delete a tex file. Auth required, ownership enforced.

**Response (200):**
```json
{ "success": true, "id": "uuid" }
```

**Error Response (404):**
```json
{ "success": false, "error": "File not found" }
```

---

### `GET /api/tex/{id}/download`

Download the raw `.tex` file.

**Response:** File download (`application/x-tex`, `Content-Disposition` header)

---

### `GET /api/tex/{id}/files`

List inferred project files from LaTeX source (`\input`, `\includegraphics`, `\bibliography`, etc.).

**Response (200):**
```json
{
  "project_id": "uuid",
  "files": [
    { "path": "main.tex", "kind": "tex", "editable": true, "stored": true },
    { "path": "figures/diagram.png", "kind": "image", "editable": false, "stored": false }
  ]
}
```

---

### `POST /api/tex/{id}/compile`

Server-side compile a tex project to PDF. Returns base64-encoded PDF.

**Response (200):**
```json
{
  "success": true,
  "project_id": "uuid",
  "filename": "notes.pdf",
  "pdf_base64": "JVBERi0xLjQ..."
}
```

**Error Response (422):**
```json
{ "success": false, "error": "LaTeX compile failed", "detail": "stderr..." }
```

---

### `GET /api/tex-files/{id}/export?format=pdf|html|tex`

Export a stored tex file in the requested format. Auth required, ownership enforced.

**Response:** File download with appropriate `Content-Type` and `Content-Disposition`.

| Format | Content-Type | Notes |
|---|---|---|
| `tex` | `application/x-tex` | Raw source |
| `pdf` | `application/pdf` | Server-side `pdflatex` |
| `html` | `text/html` | `pandoc` with `--mathml` (MathML, accessible) |

---

## Authentication

Authentication uses **Clerk** for both frontend and backend.

**Frontend:**
- `@clerk/vue` plugin initialized in `main.ts`
- `useAuth()` provides `userId`, `getToken`, `isSignedIn`
- Auth token attached to all `/api/*` requests via `Authorization: Bearer <token>`
- Route guard blocks `/dashboard`, `/settings`, `/editor` when signed out

**Backend:**
- `clerk-backend-api` SDK validates JWTs via JWKS
- `get_current_user` FastAPI dependency resolves or creates user from JWT claims
- All `/api/tex*` routes require authentication
- Dev bypass available with `AUTH_DEV_BYPASS=1` (returns a fixed dev user)

---

## Environment Variables

Project root `.env`:

```bash
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash

# Ports (don't change unless conflict)
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000

# Database (required for /api/tex features)
DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/monogram

# Auth (Clerk)
CLERK_SECRET_KEY=your_clerk_secret
CLERK_ISSUER=https://<your-clerk-domain>
CLERK_AUDIENCE=your_clerk_audience

# Dev-only auth bypass (do not use in prod)
AUTH_DEV_BYPASS=1
```

Frontend `frontend/.env`:
```bash
VITE_CLERK_PUBLISHABLE_KEY=pk_test_...
```

> **Note:** `VITE_API_URL` is no longer needed. Vite's dev server proxies `/api/*` to `http://localhost:8000` automatically via `vite.config.ts`.

---

## Directory Layout

```
src/
└── backend/
    └── app/
        ├── __init__.py
        ├── main.py              # FastAPI entry, CORS, routers, startup validation
        ├── deps.py              # get_current_user (Clerk JWT → User)
        ├── auth/
        │   ├── __init__.py
        │   └── clerk.py         # Clerk SDK JWT validation + user lookup
        ├── db/
        │   ├── __init__.py
        │   ├── base.py          # SQLAlchemy declarative Base
        │   ├── crud.py          # CRUD helpers for tex_files
        │   ├── deps.py          # get_db session dependency
        │   ├── models.py        # User + TexFile ORM models
        │   └── session.py       # Engine + SessionLocal factory
        ├── routes/
        │   ├── __init__.py
        │   ├── convert.py       # POST /api/convert (PDF + image)
        │   ├── export.py        # POST /api/export (raw .tex download)
        │   ├── tex.py           # /api/tex CRUD + /compile + /files
        │   └── tex_export.py    # GET /api/tex-files/{id}/export
        ├── services/
        │   ├── __init__.py
        │   ├── gemini.py        # Gemini API wrapper (google-genai SDK)
        │   ├── latex.py         # LaTeX post-processing + body extraction
        │   └── tex_export.py    # PDF/HTML/TEX export via pdflatex/pandoc
        └── utils/
            ├── __init__.py
            ├── image.py         # Image preprocessing (Pillow)
            ├── latex_tools.py   # compile_pdf / convert_html stubs
            └── pdf.py           # PDF → image pages (pdf2image)

frontend/
├── src/
│   ├── App.vue
│   ├── main.ts                  # Clerk + Pinia + router init
│   ├── assets/
│   │   └── main.css             # Tailwind v4 @theme + design tokens
│   ├── components/
│   │   ├── convert/
│   │   │   ├── UploadZone.vue
│   │   │   ├── LoadingAnimation.vue
│   │   │   ├── ResultView.vue   # Split: PDF.js viewer + KaTeX preview
│   │   │   └── LatexEditorPanel.vue  # CodeMirror + PDF preview
│   │   ├── dashboard/
│   │   │   ├── ComparisonPanel.vue
│   │   │   ├── DashboardTopBar.vue
│   │   │   ├── EmptyState.vue
│   │   │   ├── ErrorState.vue
│   │   │   ├── LoadingSkeleton.vue
│   │   │   └── ProjectRow.vue
│   │   ├── landing/
│   │   │   ├── HeroSection.vue  # 4-phase animation sequence
│   │   │   ├── FeaturesGrid.vue # Bento grid with observer
│   │   │   └── HowItWorks.vue
│   │   ├── layout/
│   │   │   ├── AppNavbar.vue    # Fixed vertical nav + Clerk buttons
│   │   │   └── AppFooter.vue
│   │   └── ui/                   # shadcn-vue primitives (button, card, etc.)
│   ├── composables/
│   │   ├── useConvert.ts        # /api/convert wrapper
│   │   ├── useExport.ts         # PDF/HTML/TEX export via backend
│   │   └── useProjects.ts       # CRUD, compile, Clerk-scoped, localStorage cache
│   ├── lib/
│   │   ├── authFetch.ts         # Clerk-aware fetch wrapper
│   │   └── utils.ts             # cn() tailwind-merge helper
│   ├── router/
│   │   └── index.ts             # 5 routes with auth guards
│   ├── stores/
│   │   └── counter.ts           # Pinia store (placeholder)
│   ├── types/
│   │   └── project.ts           # ProjectRecord, AddConvertedProjectInput
│   └── views/
│       ├── HomePage.vue         # Navbar + Hero + Features + Footer
│       ├── ConvertPage.vue      # Upload → Loading → Result flow
│       ├── DashboardPage.vue    # Project list + auth guard
│       ├── EditorPage.vue       # Full editor: CM + PDF + autosave + compile
│       └── SettingsPage.vue     # Profile/API/Notifications/Appearance tabs
├── public/
│   ├── pdf.worker.mjs           # PDF.js web worker (copied from node_modules)
│   └── fonts/
├── package.json
└── vite.config.ts               # vue + tailwindcss v4 + devtools + /api proxy
```

---

## Frontend Routes

| Path | View | Auth Required | Description |
|---|---|---|---|
| `/` | `HomePage` | No | Landing page with hero + features |
| `/convert` | `ConvertPage` | No | Upload → loading → result flow |
| `/dashboard` | `DashboardPage` | Yes | List of user projects, create new, delete |
| `/editor` | `EditorPage` | Yes | CodeMirror editor + live KaTeX preview + PDF compile + autosave |
| `/settings` | `SettingsPage` | Yes | User preferences (stub) |

---

## Editor Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+Enter` / `Cmd+Enter` | Recompile (generate PDF) |
| `Ctrl+S` / `Cmd+S` | Recompile (saves and compiles) |
| `Tab` | Indent with tab |
| `Ctrl+Z` / `Cmd+Z` | Undo |
| `Ctrl+Shift+Z` / `Cmd+Shift+Z` | Redo |
| `Ctrl+F` / `Cmd+F` | Find |

---

## Editor Preview Modes

The editor panel supports two preview modes:

1. **Live KaTeX Preview** — Instant client-side rendering of LaTeX to HTML using KaTeX. Shown automatically when no compiled PDF is available. Updates in real-time as you type.
2. **Compiled PDF Preview** — Server-side `pdflatex` compilation. Triggered by clicking "Recompile" or pressing `Ctrl+Enter`. Shows the exact PDF output with page navigation.

### Math Environment Rendering

The live preview properly handles:

- `align*` / `align` → wrapped in `\begin{aligned}...\end{aligned}` for KaTeX
- `gather*` / `gather` / `multline*` → wrapped in `\begin{gathered}...\end{gathered}`
- `equation*` / `equation` → rendered as display math
- `cases`, `pmatrix`, `bmatrix`, `vmatrix` → native KaTeX support
- `eqnarray*`, `split`, `flalign*` → converted to `aligned`
- `\cancel{}`, `\text{}`, `\frac{}{}` — all native KaTeX
- Custom macros: `\R`, `\N`, `\Z`, `\Q`, `\C` → `\mathbb{}`; `\dx`, `\dy`, `\dt`, `\ds` → thin space + variable

### Download Dropdown

The editor footer has a Download dropdown with format options:
- `.tex` — direct client-side download (works offline)
- `.html` — server-side pandoc export (requires saved project)
- `.pdf` — server-side pdflatex export (requires saved project)

---

## Dashboard Features

- **New Conversion** — Upload a document (image/PDF) to convert to LaTeX via Gemini
- **New Project** — Create a blank LaTeX project from template
- **Delete Project** — Remove a project (with backend `DELETE /api/tex/{id}`)
- **LaTeX Snippet Preview** — Each project row shows a brief text excerpt from the LaTeX body
- **View / Edit** — Open project in the full editor
- **Split Layout Preview** — On desktop, the dashboard shows a split layout with the project list on the left and a live KaTeX preview of the selected project on the right
- **Preview Download** — Download dropdown in the preview panel with .tex/.html/.pdf format options
- **Auto-select** — First project is automatically selected for preview on load

---

## Compiler UX

- **Spinner animation** — Both the Recompile button and preview pane show a spinner during compilation
- **Non-blocking editor** — The code editor remains fully editable during PDF compilation
- **Auto-dismissing errors** — Cloud save / export errors auto-dismiss after a few seconds
- **Status badges** — Compile state (Compiled / Compiling / Needs recompile / Error) shown as colored badge in the preview header

---

## Navigation

- **Vertical nav sidebar** — Fixed right sidebar on desktop with links: Home, Features, Convert, Editor, Dashboard
- **Mobile nav** — Hamburger menu with the same links
- **Features link** — Points to `/#features` anchor on the landing page (works from any page)
- **Auth guard** — Dashboard and Editor routes redirect to home if not signed in

---

## Database Auto-Migration

On startup, the backend automatically creates database tables if they don't exist (`Base.metadata.create_all`). This means no manual migration step is needed for initial setup.

---

## Gemini Model Quick Facts

| Property | Value |
|---|---|
| Model | `gemini-2.5-flash` |
| SDK | `google-genai` (new SDK, `genai.Client`) |
| Inputs | Text, images, video, audio |
| Output | Text |
| Max input tokens | 1,048,576 |
| Max output tokens | 65,536 |
| Free tier | 15 RPM / 1,500 RPD |
| API key | https://aistudio.google.com/apikey |

---

## Docs Index

| File | Who | What |
|---|---|---|
| `CHECKLIST-FRONTEND.md` | Teammate 1 🎨 | Frontend tasks — phased, with cut list |
| `CHECKLIST-CONVERT-BACKEND.md` | Teammate 2 ⚙️ | Backend tasks — phased, with cut list |
| `ARCHITECTURE.md` | Both | This file — API contract, system design |
| `FRONTEND-REFERENCE.md` | Teammate 1 🎨 | Vue, Motion, KaTeX code snippets |
| `BACKEND-CONVERT-REFERENCE.md` | Teammate 2 ⚙️ | Python, FastAPI, Gemini code snippets |
| `BACKEND-AUTH-ACCOUNT-REFERENCE.md` | Teammate 2 ⚙️ | Clerk JWT auth flow |
| `BACKEND-AUTH-ACCOUNT-CHECKLIST.md` | Teammate 2 ⚙️ | Auth implementation checklist |
| `BACKEND-LATEX-DATA-REFERENCE.md` | Teammate 2 ⚙️ | Tex storage & retrieval |
| `BACKEND-LATEX-DATA-CHECKLIST.md` | Teammate 2 ⚙️ | Tex data checklist |
| `BACKEND-TEX-TO-FORMAT-REFERENCE.md` | Teammate 2 ⚙️ | PDF/HTML/TEX export reference |
| `BACKEND-TEX-TO-FORMAT-CHECKLIST.md` | Teammate 2 ⚙️ | Export feature checklist |
| `FRONTEND-AUTH-ACCOUNT-CHECKLIST.md` | Teammate 1 🎨 | Frontend auth checklist |
| `FIGMA-TO-CODE.md` | Teammate 1 🎨 | Figma → Vue workflow, Tailwind mapping |
| `TESTING.md` | Both | Test cases, edge cases, automated tests |
