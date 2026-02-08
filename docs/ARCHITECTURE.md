# 🏗️ ScribeTeX — Architecture & API Contract

> **Shared reference for both teammates — system design, API shape, env vars**
> Last updated: Feb 7, 2026

---

## System Diagram

```
┌─────────────────────────────────────────────────────┐
│                    FRONTEND                         │
│       Vue 3  ·  Motion (motion-v)  ·  KaTeX         │
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌───────────────────┐ │
│  │  Upload   │  │  LaTeX   │  │   Live Preview    │ │
│  │  Zone     │  │  Editor  │  │   (KaTeX render)  │ │
│  └────┬─────┘  └────┬─────┘  └───────────────────┘ │
│       │              │                               │
└───────┼──────────────┼───────────────────────────────┘
        │              │
        ▼              ▼
   http://localhost:5173  →  http://localhost:8000
        │              │
┌───────┼──────────────┼───────────────────────────────┐
│       ▼              ▼                               │
│                  BACKEND (Python)                    │
│                    FastAPI                           │
│                                                     │
│  ┌──────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │ POST /convert │  │ GET /health  │  │POST /export│ │
│  └──────┬───────┘  └─────────────┘  └────────────┘ │
│         │                                           │
└─────────┼───────────────────────────────────────────┘
          │
          ▼
┌─────────────────────┐
│   Google Gemini API  │
│   gemini-2.5-flash   │
└─────────────────────┘
```

---

## API Contract

This is what both teammates agree on. Frontend sends requests in this shape, backend returns responses in this shape.

### `POST /api/convert`

**Request:**
- Content-Type: `multipart/form-data`
- Body field: `file` (image — jpeg, png, or webp, max 10MB)
- Query param: `context` (optional — `"general"` | `"math"` | `"chemistry"` | `"physics"`)

**Success Response (200):**
```json
{
  "success": true,
  "latex": "\\documentclass{article}\n\\begin{document}\n...\n\\end{document}",
  "raw_text": "Optional plain text extraction",
  "processing_time_ms": 2340
}
```

**Error Responses:**

| Code | When | Body |
|---|---|---|
| 422 | Bad file format | `{ "success": false, "error": "Supported formats: jpeg, png, webp" }` |
| 413 | File > 10MB | `{ "success": false, "error": "File too large (max 10MB)" }` |
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

## Environment Variables

Both teammates need this `.env` file at the project root:

```bash
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash

# Ports (don't change unless conflict)
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000
```

Frontend also needs a `VITE_API_URL` in its own env or hardcoded:
```bash
# frontend/.env
VITE_API_URL=http://localhost:8000
```

---

## Directory Layout

```
src/
├── backend/                    ← Teammate 2 (⚙️ Backend)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI entry point
│   │   ├── routes/
│   │   │   ├── convert.py      # POST /api/convert
│   │   │   └── export.py       # POST /api/export
│   │   ├── services/
│   │   │   ├── gemini.py       # Gemini API wrapper
│   │   │   └── latex.py        # LaTeX post-processing
│   │   └── utils/
│   │       └── image.py        # Image preprocessing (Pillow)
│   ├── requirements.txt
│   └── .env
│
└── frontend/                   ← Teammate 1 (🎨 Frontend)
    ├── src/
    │   ├── App.vue
    │   ├── main.ts
    │   ├── components/
    │   │   ├── UploadZone.vue
    │   │   ├── LatexEditor.vue
    │   │   ├── LatexPreview.vue
    │   │   ├── ResultView.vue
    │   │   └── LoadingAnimation.vue
    │   ├── composables/
    │   │   ├── useConvert.ts
    │   │   └── useExport.ts
    │   └── views/
    │       ├── HomePage.vue
    │       └── ConvertPage.vue
    ├── package.json
    └── vite.config.ts
```

---

## Gemini Model Quick Facts

| Property | Value |
|---|---|
| Model | `gemini-2.5-flash` |
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
| `CHECKLIST-BACKEND.md` | Teammate 2 ⚙️ | Backend tasks — phased, with cut list |
| `ARCHITECTURE.md` | Both | This file — API contract, system design |
| `FRONTEND-REFERENCE.md` | Teammate 1 🎨 | Vue, Motion, KaTeX code snippets |
| `BACKEND-REFERENCE.md` | Teammate 2 ⚙️ | Python, FastAPI, Gemini code snippets |
| `FIGMA-TO-CODE.md` | Teammate 1 🎨 | Figma → Vue workflow, Tailwind mapping, animation sequence |
| `TESTING.md` | Both | Test cases, edge cases, automated tests |

---

## Communication Between Teammates

- **Don't change the API contract** without telling the other person
- If you need a new field in the response, add it — don't rename existing ones
- Test integration together at the **Phase 2 milestone** (hour ~4–5)
- Use `git` branches: `frontend/*` and `backend/*`, merge to `main` often
