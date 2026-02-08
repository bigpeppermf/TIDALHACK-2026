# Monogram — Handwriting to LaTeX

> Convert handwritten notes and PDFs into editable LaTeX documents.

---

## Overview

Monogram is a full-stack web application that converts uploaded images and PDFs of handwritten notes into LaTeX source code using Google's Gemini AI. Users can then edit, compile, and export their LaTeX documents in multiple formats.

### Key Features

- **Upload & Convert**: Drag-and-drop PDFs or images → instant LaTeX output via Gemini.
- **LaTeX Editor**: Full CodeMirror 6 editor with LaTeX syntax highlighting.
- **Live Compile**: Server-side `pdflatex` compilation with PDF preview.
- **Multi-format Export**: Download as PDF, HTML, DOCX, or Markdown.
- **Project Management**: Save, rename, and organize LaTeX projects.
- **Authentication**: Clerk-based auth with JWT session tokens.

---

## Tech Stack

### Backend

| Component | Technology |
|---|---|
| Framework | FastAPI (Python) |
| AI | Google Gemini (`google-genai` SDK) |
| Auth | Clerk (`clerk-backend-api`) |
| Database | PostgreSQL via SQLAlchemy 2.0 (async) |
| PDF → Image | `pdf2image` + Poppler |
| LaTeX → PDF | `pdflatex` (TeX Live) |
| LaTeX → HTML/DOCX/MD | Pandoc |

### Frontend

| Component | Technology |
|---|---|
| Framework | Vue 3.5 (Composition API) |
| Build | Vite 7.3 |
| Language | TypeScript 5.9 |
| CSS | Tailwind CSS v4 |
| Auth | @clerk/vue |
| State | Pinia 3.0 |
| Editor | vue-codemirror + CodeMirror 6 |
| PDF Viewer | pdfjs-dist 5.4 |
| UI Kit | shadcn-vue (reka-ui) |
| Icons | lucide-vue-next |
| Math | KaTeX |

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20.19+ or 22.12+
- PostgreSQL
- TeX Live (`pdflatex`)
- Pandoc
- Poppler (`pdftoppm`)

### Backend

```bash
# Install Python dependencies
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY="your-key"
export CLERK_SECRET_KEY="your-key"
export DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/tidalhack"

# Run the server
uvicorn src.backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install

# Set environment variables
echo 'VITE_CLERK_PUBLISHABLE_KEY=pk_test_...' > .env

# Run dev server (proxies /api to localhost:8000)
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## API Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/health` | No | Health check |
| POST | `/api/convert` | No | Upload PDF/image → LaTeX |
| POST | `/api/export` | No | LaTeX → `.tex` file download |
| POST | `/api/tex` | Yes | Create new TeX project |
| GET | `/api/tex` | Yes | List user's TeX projects |
| GET | `/api/tex/{id}` | Yes | Get project with content |
| PUT | `/api/tex/{id}` | Yes | Update project |
| DELETE | `/api/tex/{id}` | Yes | Delete project |
| GET | `/api/tex/{id}/download` | Yes | Download `.tex` file |
| GET | `/api/tex/{id}/files` | Yes | Get inferred file tree |
| POST | `/api/tex/{id}/compile` | Yes | Compile LaTeX → PDF |
| GET | `/api/tex-files/{id}/export` | No | Export to PDF/HTML/DOCX/MD |

---

## Frontend Routes

| Path | Page | Auth Required |
|---|---|---|
| `/` | Landing / Home | No |
| `/convert` | Upload & Convert | No |
| `/dashboard` | Project List | Yes |
| `/editor` | LaTeX Editor | Yes |
| `/settings` | User Settings | Yes |

---

## Project Structure

```
├── requirements.txt
├── src/backend/app/
│   ├── main.py              # FastAPI app setup
│   ├── deps.py              # Auth dependency (Clerk JWT)
│   ├── auth/clerk.py        # Clerk SDK integration
│   ├── db/                  # Models, CRUD, session
│   ├── routes/              # convert, export, tex, tex_export
│   ├── services/            # gemini, latex, tex_export
│   └── utils/               # image, latex_tools, pdf
├── frontend/
│   └── src/
│       ├── views/           # 5 page components
│       ├── components/      # Feature components
│       ├── composables/     # useConvert, useExport, useProjects
│       ├── lib/             # authFetch, utils
│       └── router/          # Routes + auth guard
├── tests/                   # Backend tests
└── docs/                    # Documentation
```

---

## Documentation

| Document | Description |
|---|---|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture & diagrams |
| [FRONTEND-REFERENCE.md](docs/FRONTEND-REFERENCE.md) | Frontend technical reference |
| [BACKEND-CONVERT-REFERENCE.md](docs/BACKEND-CONVERT-REFERENCE.md) | Convert pipeline reference |
| [BACKEND-LATEX-DATA-REFERENCE.md](docs/BACKEND-LATEX-DATA-REFERENCE.md) | LaTeX storage API reference |
| [BACKEND-TEX-TO-FORMAT-REFERENCE.md](docs/BACKEND-TEX-TO-FORMAT-REFERENCE.md) | Export pipeline reference |
| [BACKEND-AUTH-ACCOUNT-REFERENCE.md](docs/BACKEND-AUTH-ACCOUNT-REFERENCE.md) | Auth system reference |
| [TESTING.md](docs/TESTING.md) | Test infrastructure |
| [FIGMA-TO-CODE.md](docs/FIGMA-TO-CODE.md) | Design-to-code guidelines |

---

## License

Hackathon project — TIDAL Hack 2026.
