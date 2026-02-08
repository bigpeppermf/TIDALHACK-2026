# ⚙️ Teammate 2 — Backend Checklist

> **Role:** Backend Development & AI Integration
> **Stack:** Python, FastAPI, Gemini Vision API, Pillow
> **Work in:** `src/backend/`
> **Code ref:** `docs/BACKEND-REFERENCE.md`

---

## 🏁 Phase 1 — Setup (Hours 0–4)

### With Teammate 1

- [ ] Align on project scope and review docs together
- [ ] Review API contract in `ARCHITECTURE.md` — agree on request/response shapes
- [ ] Set up `.env` with `GEMINI_API_KEY`
- [ ] Confirm both dev servers run without port conflicts (you: `:8000`, them: `:5173`)

### Solo

- [ ] Create Python venv: `python -m venv .venv && source .venv/bin/activate`
- [ ] Create `requirements.txt` (see BACKEND-REFERENCE.md)
- [ ] `pip install -r requirements.txt`
- [ ] Create FastAPI app shell in `src/backend/app/main.py`
- [ ] Add CORS middleware (allow origin `http://localhost:5173`)
- [ ] Add `GET /api/health` endpoint — return `{ "status": "ok", "version": "1.0.0" }`
- [ ] Verify `uvicorn app.main:app --reload --port 8000` works
- [ ] Test Gemini API: send a test page image, confirm you get text back
- [ ] Confirm API key + model work: `gemini-2.5-flash`

**✅ Milestone:** FastAPI running on `:8000`. Gemini API responds to test page images.

---

## 🔗 Phase 2 — Core Pipeline (Hours 4–10)

### Image Processing

- [ ] Create `src/backend/app/utils/image.py`
- [ ] `preprocess_image()`: accept raw bytes, return base64 string
- [ ] Convert to RGB (strip alpha channels)
- [ ] Resize if larger than 2048px (thumbnail with LANCZOS)
- [ ] Enhance contrast (1.5x — helps with pencil/whiteboard)
- [ ] Apply sharpen filter
- [ ] Encode to base64 JPEG (quality 90)

### Gemini Integration

- [ ] Create `src/backend/app/services/gemini.py`
- [ ] Write `SYSTEM_PROMPT` — the LaTeX conversion prompt (see BACKEND-REFERENCE.md)
- [ ] `convert_image_to_latex(base64_image, context)` function
- [ ] Pick ONE SDK approach: official `google-genai` OR OpenAI-compatible
- [ ] Test: send preprocessed image → get LaTeX back

### LaTeX Post-Processing

- [ ] Create `src/backend/app/services/latex.py`
- [ ] `post_process_latex()`: strip markdown fences from Gemini output
- [ ] Ensure `\documentclass` preamble exists (inject if missing)
- [ ] Fix common escape issues (`\\n` → actual newlines)

### Convert Endpoint

- [ ] Create `src/backend/app/routes/convert.py`
- [ ] `POST /api/convert` — accept `multipart/form-data` with `file` field (PDF)
- [ ] Accept optional `?context=` query param (default: `"general"`)
- [ ] Validate file type: only pdf → 422 if wrong
- [ ] Validate file size: max 10MB → 413 if too large
- [ ] Pipeline: validate → PDF to images → preprocess → Gemini → post-process → respond
- [ ] Return: `{ "success": true, "latex": "...", "raw_text": "...", "processing_time_ms": 1234 }`
- [ ] Register router in `main.py`

### Export Endpoint

- [ ] Create `src/backend/app/routes/export.py`
- [ ] `POST /api/export` — accept `{ "latex": "...", "filename": "notes" }`
- [ ] Return `.tex` file download response
- [ ] Register router in `main.py`

### Testing

- [ ] Test `/api/convert` with `curl` (see BACKEND-REFERENCE.md)
- [ ] Test with 5+ different handwriting PDFs
- [ ] Test with: clean pen, pencil, whiteboard, dense math, mixed text+math
- [ ] Tune the prompt based on what fails

### Integration

- [ ] Confirm Teammate 1 can call your API from the Vue frontend
- [ ] Fix any CORS issues that come up
- [ ] Verify response shape matches `ARCHITECTURE.md` contract

**✅ Milestone:** All endpoints working. Frontend can upload and get LaTeX back.

---

## ✨ Phase 3 — Hardening & Extras (Hours 10–18)

### Prompt Engineering

- [ ] Add `context` query param support: math, chemistry, physics, general
- [ ] Write `CONTEXT_HINTS` dict with subject-specific prompt additions
- [ ] `get_system_prompt(context)` returns base prompt + context hint
- [ ] Test each context variant with appropriate PDFs

### Robustness

- [ ] MIME type validation: check `file.content_type` before processing
- [ ] File size validation: reject before reading full file if possible
- [ ] Gemini error handling: catch rate limits (429), API down (503), bad response
- [ ] Return structured error JSON for every failure case
- [ ] Add request logging: print processing times, image sizes, errors to console

### Nice-to-Have (if time)

- [ ] Rate limiting middleware (prevent API key abuse)
- [ ] Batch endpoint: `POST /api/convert/batch` — accept multiple PDFs
- [ ] PDF export: install `pdflatex`, compile `.tex` → `.pdf` server-side
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
3. ❌ PDF export (frontend handles `.tex` download instead)
4. ❌ Rate limiting
5. ❌ Caching
6. ❌ Context-aware prompts (hardcode "general" prompt)

## 🛡️ Never Cut

- ✅ `POST /api/convert` — the core endpoint
- ✅ Image preprocessing (makes recognition quality much better)
- ✅ LaTeX post-processing (Gemini often wraps in markdown fences)
- ✅ Error handling (don't let the demo crash on a bad PDF)
- ✅ CORS config (frontend can't connect without it)

---

## 🏆 Your Demo Day Checklist

- [ ] Backend running on `:8000`
- [ ] `.env` has valid `GEMINI_API_KEY`
- [ ] `GET /api/health` returns `200`
- [ ] All demo PDFs convert successfully
- [ ] No unhandled exceptions in terminal
- [ ] Internet connection stable (Gemini API requires it)
