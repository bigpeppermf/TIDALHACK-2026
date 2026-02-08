# Frontend Reference

> Canonical reference for the Vue 3 frontend.

---

## 1. Stack & Tooling

| Concern | Tool / Library | Version |
|---|---|---|
| Framework | Vue 3 (Composition API, `<script setup>`) | 3.5 |
| Build | Vite | 7.3 |
| Language | TypeScript | 5.9 |
| CSS | Tailwind CSS v4 (`@tailwindcss/vite` plugin) | 4.1 |
| Animations | tw-animate-css | 1.4 |
| Router | vue-router | 5.0 |
| State | Pinia | 3.0 |
| Auth | @clerk/vue | 1.12+ |
| UI components | shadcn-vue (reka-ui based) | — |
| Icons | lucide-vue-next | 0.563 |
| Motion | motion-v | 1.10 |
| LaTeX rendering | KaTeX | 0.16 |
| Code editor | vue-codemirror + @codemirror/* | 6.x |
| PDF viewer | pdfjs-dist | 5.4 |
| Utilities | @vueuse/core | 14.2 |
| Toasts | vue-sonner | 2.0 |
| Math rendering (alt) | mathjax | 4.1 |
| Linting | ESLint + oxlint | — |
| Formatting | Prettier | 3.8 |
| Unit tests | Vitest + @vue/test-utils | 4.0 |
| E2E tests | Playwright | 1.58 |

---

## 2. Project Structure

```
frontend/
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json / tsconfig.app.json / tsconfig.node.json
├── public/
│   ├── pdf.worker.mjs          # PDF.js web worker
│   └── fonts/
└── src/
    ├── main.ts                  # App bootstrap (Pinia, Clerk, Router)
    ├── App.vue                  # Root component
    ├── assets/
    │   └── main.css             # Global styles + Tailwind
    ├── components/
    │   ├── convert/             # ConvertPage components
    │   │   ├── LatexEditorPanel.vue
    │   │   ├── LoadingAnimation.vue
    │   │   ├── ResultView.vue
    │   │   └── UploadZone.vue
    │   ├── dashboard/           # DashboardPage components
    │   │   ├── ComparisonPanel.vue
    │   │   ├── DashboardTopBar.vue
    │   │   ├── EmptyState.vue
    │   │   ├── ErrorState.vue
    │   │   ├── LoadingSkeleton.vue
    │   │   └── ProjectRow.vue
    │   ├── landing/             # HomePage components
    │   ├── layout/              # App-wide layout
    │   └── ui/                  # shadcn-vue primitives
    ├── composables/
    │   ├── useConvert.ts        # PDF/image → LaTeX conversion
    │   ├── useExport.ts         # LaTeX → PDF/HTML/TEX export
    │   └── useProjects.ts       # CRUD + compile + file tree
    ├── lib/
    │   ├── authFetch.ts         # Clerk-authenticated fetch wrapper
    │   └── utils.ts             # cn() helper
    ├── router/
    │   └── index.ts             # 5 routes + auth guard
    ├── stores/
    │   └── counter.ts           # Pinia example store
    ├── types/
    │   └── project.ts           # ProjectRecord, AddConvertedProjectInput
    └── views/
        ├── HomePage.vue         # Landing page
        ├── ConvertPage.vue      # Upload & convert flow
        ├── DashboardPage.vue    # Project list
        ├── EditorPage.vue       # CodeMirror + PDF preview
        └── SettingsPage.vue     # User settings
```

---

## 3. Bootstrap (main.ts)

```typescript
const app = createApp(App)
app.use(createPinia())
app.use(clerkPlugin, { publishableKey })
app.use(router)
app.mount('#app')
```

Order matters: Pinia → Clerk → Router.

### Environment Variables

| Variable | Required | Description |
|---|---|---|
| `VITE_CLERK_PUBLISHABLE_KEY` | Yes | Clerk publishable key for auth |

No `VITE_API_URL` — the Vite dev server proxies `/api/*` → `http://localhost:8000`.

---

## 4. Routing

| Path | View | Auth | Description |
|---|---|---|---|
| `/` | HomePage | Public | Landing page with sign-in |
| `/convert` | ConvertPage | Public | PDF/image → LaTeX converter |
| `/dashboard` | DashboardPage | Required | Project list |
| `/editor` | EditorPage | Required | LaTeX editor + PDF preview |
| `/settings` | SettingsPage | Required | User profile settings |

### Auth Guard

The `beforeEach` guard waits up to 1.5 s for `window.Clerk` to load, then checks `clerk.isSignedIn`. Unauthenticated users on protected routes redirect to `/`.

---

## 5. Composables

### useConvert

- **Purpose**: Convert uploaded PDF/image to LaTeX via `POST /api/convert`.
- **State**: `loading`, `error`, `result`.
- **Methods**: `convert(file, context)`, `reset()`.
- **Auth**: None required (public endpoint).
- **Note**: Uses plain `fetch` (no auth header).

### useExport

- **Purpose**: Export LaTeX to PDF, HTML, or TEX.
- **Formats**: `pdf`, `html`, `tex`.
- **State**: `exporting`, `error`.
- **Methods**: `exportFile({ format, texFileId?, latex?, filename? })`.
- **Behavior**:
  - If `texFileId` provided: `GET /api/tex-files/{id}/export?format=…`
  - If `format === 'tex'` and no ID: `POST /api/export` with `{ latex, filename }`.
  - Downloads result as blob with correct filename from `Content-Disposition`.

### useProjects

- **Purpose**: Full project CRUD + compile + file tree.
- **State**: `projectsState` (ref), localStorage cache.
- **Auth**: Uses `useAuthFetch()` for all API calls.
- **Key methods**:
  - `loadRemoteProjects()` → `GET /api/tex`
  - `loadProjectDetail(id)` → `GET /api/tex/{id}`
  - `addConvertedProject(input)` → `POST /api/tex`
  - `renameProject(id, name)` → `PUT /api/tex/{id}`
  - `saveLatex(id, latex)` → `PUT /api/tex/{id}`
  - `removeProject(id)` → `DELETE /api/tex/{id}`
  - `compileProject(id)` → `POST /api/tex/{id}/compile`
  - `fetchProjectFiles(id)` → `GET /api/tex/{id}/files`
- **Caching**: Projects stored in localStorage (`monogram-projects`). Remote sync merges with local cache.
- **Compile**: Returns base64 PDF, decoded to `Uint8Array` for PDF.js rendering.

---

## 6. Auth Integration

### authFetch (lib/authFetch.ts)

```typescript
export function useAuthFetch() {
  const auth = useAuth()
  async function authFetch(input, init) {
    const token = await auth.getToken()
    headers.set('Authorization', `Bearer ${token}`)
    return fetch(input, { ...init, headers })
  }
  return { authFetch }
}
```

- Obtains Clerk session JWT via `useAuth().getToken()`.
- Fallback: tries `window.Clerk.session.getToken()`.
- Used by `useProjects` for all authenticated API calls.

### Clerk Components Used

- `<SignInButton>` / `<SignUpButton>` — Landing page.
- `<UserButton>` — Top bar (signed-in state).
- `<SignedIn>` / `<SignedOut>` — Conditional rendering.

---

## 7. Key Components

### Convert Flow

| Component | Purpose |
|---|---|
| `UploadZone` | Drag-and-drop / click file upload |
| `LoadingAnimation` | Processing spinner |
| `LatexEditorPanel` | CodeMirror editor for LaTeX output |
| `ResultView` | Conversion results display |

### Dashboard

| Component | Purpose |
|---|---|
| `DashboardTopBar` | Search + new project button |
| `ProjectRow` | Single project in list (click → editor) |
| `EmptyState` | No projects yet |
| `ErrorState` | Load error display |
| `LoadingSkeleton` | Loading placeholder |
| `ComparisonPanel` | Side-by-side comparison |

### Editor (EditorPage.vue)

- **Left pane**: `vue-codemirror` with LaTeX syntax (via `@codemirror/legacy-modes/mode/stex`).
- **Right pane**: PDF preview using `pdfjs-dist` + `<canvas>`.
- **Toolbar**: Compile button, export dropdown (PDF/HTML/TEX), file info.
- **Autosave**: Saves LaTeX to backend on debounced changes.

---

## 8. Vite Configuration

```typescript
export default defineConfig({
  plugins: [vue(), vueJsx(), vueDevTools(), tailwindcss()],
  resolve: { alias: { '@': './src' } },
  server: {
    proxy: { '/api': { target: 'http://localhost:8000', changeOrigin: true } },
  },
})
```

- **Proxy**: All `/api/*` requests forwarded to the FastAPI backend.
- **Tailwind**: Uses `@tailwindcss/vite` plugin (Tailwind v4 style — no `tailwind.config` file).
- **Alias**: `@` resolves to `src/` for clean imports.

---

## 9. Type System

### ProjectRecord (types/project.ts)

Key fields: `id`, `name`, `updatedAt`, `updatedAtIso`, `status` (`'converted' | 'processing' | 'failed'`), `latex`, `sourceFilename`, `sourceKind`, `ownerId`.

### AddConvertedProjectInput

Input for `addConvertedProject()`: `name`, `latex`, `sourceFilename`, `sourceKind`.

---

## 10. Development

```bash
cd frontend
npm install
npm run dev          # Vite dev server on :5173
npm run build        # Production build
npm run test:unit    # Vitest
npm run test:e2e     # Playwright
npm run lint         # oxlint + eslint
npm run format       # Prettier
```
