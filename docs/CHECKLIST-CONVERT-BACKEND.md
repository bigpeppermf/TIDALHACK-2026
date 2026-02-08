# ⚙️ Teammate 2 — Backend Checklist

> **Role:** Backend Development & AI Integration
> **Stack:** Python, FastAPI, Gemini Vision API, Pillow, Clerk, PostgreSQL
> **Work in:** `src/backend/`
> **Code ref:** `docs/BACKEND-CONVERT-REFERENCE.md`
> Last updated: Feb 8, 2026

---

## 🏁 Phase 1 — Setup (Hours 0–4)

### With Teammate 1

- [x] Align on project scope and review docs together
- [x] Review API contract in `ARCHITECTURE.md` — agree on request/response shapes
- [x] Set up `.env` with `GEMINI_API_KEY`
- [x] Confirm both dev servers run without port conflicts (you: `:8000`, them: `:5173`)

### Solo

- [x] Create Python venv: `python -m venv .venv && source .venv/bin/activate`
- [x] Create `requirements.txt` (see BACKEND-CONVERT-REFERENCE.md)
- [x] `pip install -r requirements.txt`
- [x] Create FastAPI app shell in `app/main.py`
- [x] Add CORS middleware (allow origin from `FRONTEND_URL` env var)
- [x] Add `GET /api/health` endpoint — return `{ "status": "ok", "version": "1.0.0" }`
- [x] Verify `uvicorn app.main:app --reload --port 8000` works
- [x] Test Gemini API: send a test page image, confirm you get text back
- [x] Confirm API key + model work: `gemini-2.5-flash`

**✅ Milestone:** FastAPI running on `:8000`. Gemini API responds to test page images.

---

## 🔗 Phase 2 — Core Pipeline (Hours 4–10)

### Image Processing

- [x] Create `app/utils/image.py`
- [x] `preprocess_image()`: accept raw bytes, return base64 string
- [x] Convert to RGB (strip alpha channels)
- [x] Resize if larger than 2048px (thumbnail with LANCZOS)
- [x] Enhance contrast (1.5x — helps with pencil/whiteboard)
- [x] Apply sharpen filter
- [x] Encode to base64 JPEG (quality 90)

### Gemini Integration

- [x] Create `app/services/gemini.py`
- [x] Write `SYSTEM_PROMPT` — the LaTeX conversion prompt
- [x] `convert_image_to_latex(base64_image, context)` function
- [x] SDK: `google-genai` (`genai.Client` API) ✅
- [x] Test: send preprocessed image → get LaTeX back

### LaTeX Post-Processing

- [x] Create `app/services/latex.py`
- [x] `post_process_latex()`: strip markdown fences from Gemini output
- [x] Ensure `\documentclass` preamble exists (inject if missing)
- [x] Fix common escape issues (`\\n` → actual newlines)
- [x] `extract_document_body()`: extract content between `\begin{document}` and `\end{document}`
- [x] `wrap_latex_document()`: wrap body with standard preamble

### Convert Endpoint

- [x] Create `app/routes/convert.py`
- [x] `POST /api/convert` — accept `multipart/form-data` with `file` field (PDF **and** images)
- [x] Accept optional `?context=` query param (default: `"general"`)
- [x] Validate file type: only pdf/jpeg/png/webp → 422 if wrong
- [x] Validate file size: max 10 MB → 413 if too large
- [x] Validate PDF magic bytes (`%PDF`)
- [x] Pipeline: validate → PDF to images → preprocess → Gemini → post-process → combine
- [x] Multi-page support: process up to 5 pages, combine bodies
- [x] Return: `{ "success": true, "latex": "...", "raw_text": "...", "processing_time_ms": 1234 }`
- [x] Register router in `main.py` with `/api` prefix

### Export Endpoint

- [x] Create `app/routes/export.py`
- [x] `POST /api/export` — accept `{ "latex": "...", "filename": "notes" }`
- [x] Validate non-empty LaTeX content
- [x] Sanitize filename (strip extensions, normalize whitespace)
- [x] Return `.tex` file download response
- [x] Register router in `main.py`

### Testing

- [x] Test `/api/convert` with `curl`
- [x] Test with: clean pen, pencil, whiteboard, dense math, mixed text+math
- [ ] Test with 5+ different handwriting PDFs
- [ ] Tune the prompt based on what fails

### Integration

- [x] Confirm Teammate 1 can call your API from the Vue frontend
- [x] Fix any CORS issues that come up
- [x] Verify response shape matches `ARCHITECTURE.md` contract

**✅ Milestone:** All endpoints working. Frontend can upload and get LaTeX back.

---

## 🗄️ Phase 2.5 — Database & Tex Storage

### Schema

- [x] Set up PostgreSQL with SQLAlchemy
- [x] Create `users` table (UUID pk, `oauth_provider`, `oauth_sub`, `email`, `full_name`, `avatar_url`, `created_at`)
- [x] Create `tex_files` table (UUID pk, `user_id` FK, `filename`, `latex_content`, `created_at`, `updated_at`)
- [x] `session.py`: conditional engine creation from `DATABASE_URL` env var
- [x] `deps.py`: `get_db` session dependency

### CRUD

- [x] `crud.py`: `get_recent_tex_files`, `get_tex_file_by_id`, `create_tex_file`, `update_tex_file`, `delete_tex_file`
- [x] All queries scoped to `user_id`

### Tex Routes (`app/routes/tex.py`)

- [x] `GET /api/tex` — list recent files (with `limit` query param)
- [x] `GET /api/tex/{id}` — get single file with content
- [x] `POST /api/tex` — create new file
- [x] `PUT /api/tex/{id}` — update existing file
- [x] `GET /api/tex/{id}/download` — download `.tex` file
- [x] `GET /api/tex/{id}/files` — list inferred project files from LaTeX source
- [x] `POST /api/tex/{id}/compile` — server-side pdflatex compile, return base64 PDF
- [x] All routes use `Depends(get_current_user)` and `Depends(get_db)`
- [x] Ownership enforced on every operation

---

## 🔐 Phase 2.75 — Authentication (Clerk)

- [x] Install `clerk-backend-api` SDK
- [x] Create `app/auth/clerk.py` with `authenticate_request()`
- [x] JWT validation via Clerk SDK (`AuthenticateRequestOptions`)
- [x] Issuer + audience verification
- [x] `ClerkIdentity` dataclass: `user_id`, `email`, `full_name`, `avatar_url`
- [x] User lookup from Clerk API for profile info
- [x] `app/deps.py`: `get_current_user` resolves JWT → User model
- [x] Auto-create user on first login
- [x] Update user profile (email, name, avatar) on subsequent logins
- [x] Dev bypass with `AUTH_DEV_BYPASS=1` (fixed dev user UUID)
- [x] Startup validation: check required env vars present
- [x] Error handling: `ClerkAuthError` (401), `ClerkConfigError` (500), `ClerkServiceError` (502)

---

## 📤 Phase 2.9 — Export Formats (PDF / HTML / TEX)

- [x] Create `app/services/tex_export.py` with `export_tex_file()` function
- [x] `ExportFormat` type: `"pdf"` | `"html"` | `"tex"`
- [x] `ExportResult` dataclass: `content`, `mime_type`, `filename`
- [x] TEX export: return raw UTF-8 source
- [x] PDF export: write to temp dir → `pdflatex` subprocess → return PDF bytes
- [x] HTML export: write to temp dir → `pandoc -f latex -t html --mathml -s` → return HTML bytes
- [x] Temp directory cleanup in all paths
- [x] Create `app/routes/tex_export.py` with `GET /api/tex-files/{id}/export?format=...`
- [x] Auth + ownership enforced
- [x] Register router in `main.py`

---

## ✨ Phase 3 — Hardening & Extras (Hours 10–18)

### Prompt Engineering

- [x] Add `context` query param support: math, chemistry, physics, general
- [x] Write `CONTEXT_HINTS` dict with subject-specific prompt additions
- [x] `get_system_prompt(context)` returns base prompt + context hint
- [x] Added rule 8: ignore handwritten graphs, insert placeholder boxes
- [ ] Test each context variant with appropriate PDFs

### Robustness

- [x] MIME type validation: check `file.content_type` before processing
- [x] File size validation: reject before reading full file if possible
- [x] Gemini error handling: catch rate limits (429), API down (503), bad response
- [x] Return structured error JSON for every failure case
- [ ] Add request logging: print processing times, image sizes, errors to console

### Nice-to-Have (if time)

- [ ] Rate limiting middleware (prevent API key abuse)
- [ ] Batch endpoint: `POST /api/convert/batch` — accept multiple PDFs
- [x] PDF export: server-side `pdflatex` compile
- [ ] TIDAL API integration: ambient music endpoint for frontend
- [ ] Caching: if same PDF hash is sent twice, return cached result

**✅ Milestone:** Backend handles all edge cases gracefully. Prompt is well-tuned.

---

## 🎤 Phase 4 — Demo Prep (Hours 18–24)

- [ ] Collect 3–5 strong demo PDFs with Teammate 1
- [ ] Run every demo PDF through the API, verify clean LaTeX output
- [ ] Fix any prompt issues found during testing
- [ ] Ensure backend stays up for 30+ minutes without crashing
- [ ] Help build slide deck
- [ ] Practice demo — be ready to explain the backend in 30 seconds

---

## 🪓 Cut List (drop these first if behind)

1. ❌ TIDAL music integration
2. ❌ Batch endpoint
3. ❌ Rate limiting
4. ❌ Caching
5. ❌ Request logging middleware

### 🛡️ Never Cut

- ✅ `POST /api/convert` — the core endpoint
- ✅ Image preprocessing (makes recognition quality much better)
- ✅ LaTeX post-processing (Gemini often wraps in markdown fences)
- ✅ Error handling (don't let the demo crash on a bad PDF)
- ✅ CORS config (frontend can't connect without it)
- ✅ Clerk auth (required for dashboard + editor flow)
- ✅ Tex storage CRUD (projects need to persist)

---

## 🏆 Your Demo Day Checklist

- [ ] Backend running on `:8000`
- [ ] `.env` has valid `GEMINI_API_KEY`
- [ ] `.env` has `CLERK_SECRET_KEY`, `CLERK_ISSUER`, `CLERK_AUDIENCE`
- [ ] `.env` has `DATABASE_URL` pointing to running PostgreSQL
- [ ] `GET /api/health` returns `200`
- [ ] All demo PDFs convert successfully
- [ ] Dashboard lists saved projects
- [ ] Editor compiles and shows PDF preview
- [ ] No unhandled exceptions in terminal
- [ ] Internet connection stable (Gemini API + Clerk require it)
