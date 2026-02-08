# Editor Data Flow

> How data flows through the Editor page.

---

## 1. Entry Point

User navigates to `/editor?id=<projectId>` from the Dashboard (clicking a `ProjectRow`).

---

## 2. Load Flow

```
EditorPage.vue mounted
  └─ useProjects().loadProjectDetail(id)
       └─ authFetch(`/api/tex/${id}`)
            └─ Backend: deps.get_current_user → Clerk JWT → User
            └─ Backend: crud.get_tex_file(db, id, user.id)
            └─ Returns: { id, filename, latex, created_at, updated_at }
       └─ upsertProject(detailToProject(response))
       └─ Updates projectsState ref + localStorage
  └─ CodeMirror initialized with project.latex
  └─ File tree loaded via fetchProjectFiles(id)
       └─ authFetch(`/api/tex/${id}/files`)
       └─ Returns: { files: [{ path, kind, editable, stored }] }
```

---

## 3. Edit Flow

```
User types in CodeMirror
  └─ @update:modelValue fires
  └─ Debounced saveLatex(id, newLatex)
       └─ authFetch PUT `/api/tex/${id}` { latex: newLatex }
       └─ Backend: crud.update_tex_file(db, id, user.id, latex=newLatex)
       └─ Returns: updated file
       └─ upsertProject() updates local state + localStorage
```

---

## 4. Compile Flow

```
User clicks "Compile" button
  └─ useProjects().compileProject(id)
       └─ authFetch POST `/api/tex/${id}/compile`
       └─ Backend:
            └─ crud.get_tex_file(db, id, user.id)
            └─ Write latex to temp file
            └─ Run `pdflatex` twice
            └─ Read PDF bytes → base64 encode
            └─ Return: { success: true, pdf_base64: "..." }
       └─ decodeBase64ToBytes(pdf_base64)
       └─ Returns: Uint8Array
  └─ PDF.js renders Uint8Array into <canvas>
       └─ pdfjsLib.getDocument({ data: pdfBytes })
       └─ page.render({ canvasContext, viewport })
```

---

## 5. Export Flow

```
User clicks export button (PDF / HTML / TEX)
  └─ useExport().exportFile({ format, texFileId: id })
       └─ fetch GET `/api/tex-files/${id}/export?format=pdf`
       └─ Backend: export_tex_file(latex, format)
            └─ pdflatex (PDF) or pandoc (HTML/DOCX/MD)
            └─ Returns: StreamingResponse with file bytes
       └─ Browser receives blob
       └─ downloadBlob(blob, filename) → triggers download
```

---

## 6. Rename Flow

```
User renames project
  └─ useProjects().renameProject(id, newName)
       └─ authFetch PUT `/api/tex/${id}` { filename: newName.tex }
       └─ upsertProject() with updated name
```

---

## 7. State Architecture

```
                  ┌──────────────────┐
                  │   Clerk Auth     │
                  │  (JWT session)   │
                  └────────┬─────────┘
                           │ getToken()
                  ┌────────▼─────────┐
                  │   authFetch()    │
                  │  (lib/authFetch) │
                  └────────┬─────────┘
                           │ Bearer token
              ┌────────────▼────────────┐
              │    useProjects()         │
              │  (composables/           │
              │   useProjects.ts)        │
              │                          │
              │  projectsState (ref)     │
              │  localStorage cache      │
              └───────┬──────┬──────────┘
                      │      │
           ┌──────────▼┐  ┌──▼──────────┐
           │ Dashboard  │  │   Editor    │
           │ (list)     │  │ (detail)    │
           └────────────┘  └─────────────┘
```

### Key Points

1. **Single source of truth**: `projectsState` ref in `useProjects` is shared across views.
2. **Dual storage**: localStorage for offline resilience + backend API for persistence.
3. **Merge strategy**: Remote projects are upserted into local state; local-only entries preserved.
4. **Auth scoping**: All API calls include Clerk JWT → backend filters by `user.id`.
5. **Optimistic updates**: Local state updated immediately; API call happens in background.

---

## 8. CodeMirror Setup

- **Language**: `@codemirror/legacy-modes/mode/stex` (LaTeX/TeX syntax).
- **Extensions**: Autocomplete, search, key bindings (default + search).
- **Theme**: Custom or default CodeMirror theme.
- **Two-way binding**: `v-model` via `vue-codemirror` component.

---

## 9. PDF Preview

- **Library**: `pdfjs-dist` 5.4.
- **Worker**: Loaded from `/pdf.worker.mjs` (in `public/`).
- **Rendering**: Full page rendered to `<canvas>` at device pixel ratio.
- **Navigation**: Page controls for multi-page documents.
- **Source**: Compile response `pdf_base64` → `Uint8Array` → `pdfjsLib.getDocument()`.
