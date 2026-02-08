# ⚙️ Backend Code Reference — Python

> **Teammate 2's code reference. Reflects actual implementation.**
> Last updated: Feb 8, 2026

---

## Dependencies

```
fastapi
uvicorn
python-dotenv
google-genai
python-multipart
pdf2image
pillow
sqlalchemy>=2.0
psycopg2-binary>=2.9
clerk-backend-api
httpx
```

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## FastAPI App (`app/main.py`)

```python
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load .env from project root (three levels up from this file)
_env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(_env_path)

from app.routes.convert import router as convert_router
from app.routes.export import router as export_router
from app.routes.tex_export import router as tex_export_router
from app.routes import tex

app = FastAPI()

# Startup validation — check Clerk env vars unless dev bypass is on
@app.on_event("startup")
def _validate_auth_env():
    if os.getenv("AUTH_DEV_BYPASS", "").lower() in {"1", "true", "yes"}:
        return
    for var in ("CLERK_SECRET_KEY", "CLERK_ISSUER", "CLERK_AUDIENCE"):
        if not os.getenv(var):
            raise RuntimeError(f"{var} is required for authentication")

# CORS
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(convert_router, prefix="/api")
app.include_router(export_router, prefix="/api")
app.include_router(tex.router)          # /api/tex routes (prefix built-in)
app.include_router(tex_export_router, prefix="/api")  # /api/tex-files/{id}/export

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"success": False, "error": exc.detail})

@app.exception_handler(Exception)
async def unhandled_exception_handler(_request: Request, _exc: Exception):
    return JSONResponse(status_code=500, content={"success": False, "error": "Internal server error"})

@app.get("/api/health")
def health():
    return {"status": "ok", "version": "1.0.0"}
```

```bash
# Run from src/backend/
uvicorn app.main:app --reload --port 8000
```

---

## Gemini API — google-genai SDK (`app/services/gemini.py`)

Uses the new `google-genai` SDK (`genai.Client`), not the older `google-generativeai` package.

```python
import base64
import os
from google import genai
from google.genai import types

def convert_image_to_latex(base64_image: str, context: str = "general") -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY")

    client = genai.Client(api_key=api_key)
    prompt = get_system_prompt(context)
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    response = client.models.generate_content(
        model=model_name,
        contents=[
            types.Part.from_bytes(data=base64.b64decode(base64_image), mime_type="image/jpeg"),
        ],
        config=types.GenerateContentConfig(system_instruction=prompt),
    )
    return response.text
```

---

## The LaTeX Prompt (`app/services/gemini.py`)

```python
SYSTEM_PROMPT = """You are an expert OCR and LaTeX typesetting engine specializing
in handwritten academic content.

INPUT: An image of handwritten notes, equations, or diagrams.
OUTPUT: Clean, compilable LaTeX code.

RULES:
1. Output ONLY valid LaTeX code — no explanations, no markdown fences
2. Include a complete document preamble:
   \\documentclass[12pt]{article}
   \\usepackage{amsmath,amssymb,amsfonts}
   \\usepackage[utf8]{inputenc}
   \\usepackage{geometry}
   \\geometry{a4paper, margin=1in}
3. Use \\section{} for headers, \\begin{align} for displayed math
4. Use $...$ for inline math
5. If text is illegible, insert: \\textcolor{red}{[illegible]}
6. NEVER invent content not present in the image
7. For diagrams, add: % [Diagram: description]
8. Ignore any hand written graph and instead add a box as a place holder
"""

CONTEXT_HINTS = {
    "math": "Pay special attention to integrals, derivatives, summation notation, limits, and Greek letters.",
    "chemistry": "Use the mhchem package for chemical equations. Recognize molecular structures and reaction arrows.",
    "physics": "Recognize vector notation, bra-ket notation, circuit diagrams, and unit expressions.",
    "general": "Preserve headings, bullet points, and inline math as written.",
}

def get_system_prompt(context: str = "general") -> str:
    hint = CONTEXT_HINTS.get(context, CONTEXT_HINTS["general"])
    return SYSTEM_PROMPT + f"\n\nCONTEXT: {hint}"
```

---

## Image Preprocessing (`app/utils/image.py`)

```python
import base64, io
from PIL import Image, ImageEnhance, ImageFilter

MAX_SIZE = 2048
JPEG_QUALITY = 90
CONTRAST_FACTOR = 1.5

def preprocess_image(image_bytes: bytes) -> str:
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode != "RGB":
        img = img.convert("RGB")
    w, h = img.size
    if max(w, h) > MAX_SIZE:
        scale = MAX_SIZE / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    img = ImageEnhance.Contrast(img).enhance(CONTRAST_FACTOR)
    img = img.filter(ImageFilter.SHARPEN)
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=JPEG_QUALITY)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")
```

---

## LaTeX Post-Processing (`app/services/latex.py`)

```python
import re

DEFAULT_PREAMBLE = (
    "\\documentclass[12pt]{article}\n"
    "\\usepackage{amsmath,amssymb,amsfonts}\n"
    "\\usepackage[utf8]{inputenc}\n"
    "\\usepackage{geometry}\n"
    "\\geometry{a4paper, margin=1in}\n"
    "\\begin{document}\n"
)
DOCUMENT_END = "\\end{document}"

def post_process_latex(raw_latex: str) -> str:
    ...  # Strip fences, inject preamble if missing, fix escapes

def extract_document_body(raw_latex: str) -> str:
    ...  # Extract content between \begin{document} and \end{document}

def wrap_latex_document(body: str) -> str:
    ...  # Wrap body with standard preamble
```

---

## PDF to Images (`app/utils/pdf.py`)

```python
from pdf2image import convert_from_path
from PIL import Image, ImageEnhance

def pdf_to_images(pdf_path: str, dpi: int = 300, max_pages: int = 5) -> list[Image.Image]:
    images = convert_from_path(pdf_path, dpi=dpi, fmt="png", grayscale=True)
    processed = []
    for img in images[:max_pages]:
        img = ImageEnhance.Contrast(img).enhance(1.4)
        processed.append(img)
    return processed
```

---

## Convert Endpoint (`app/routes/convert.py`)

- Accepts PDF and image files (jpeg/png/webp)
- Validates MIME type and file size (10 MB max)
- PDF: validates magic bytes, converts to images, processes each page
- Image: preprocesses directly
- Multi-page support: up to 5 pages, combines bodies
- Returns: `{ "success": true, "latex": "...", "raw_text": "...", "processing_time_ms": ... }`

---

## Export Endpoint (`app/routes/export.py`)

- `POST /api/export` — accepts `{ "latex": "...", "filename": "notes" }`
- Validates non-empty LaTeX content
- Sanitizes filename (strips extensions, normalizes whitespace)
- Returns `.tex` file download

---

## Tex CRUD Routes (`app/routes/tex.py`)

All routes require `Depends(get_current_user)` and `Depends(get_db)`.

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/tex` | List recent files (limit param) |
| `GET` | `/api/tex/{id}` | Get single file with content |
| `POST` | `/api/tex` | Create new file |
| `PUT` | `/api/tex/{id}` | Update file |
| `GET` | `/api/tex/{id}/download` | Download `.tex` |
| `GET` | `/api/tex/{id}/files` | Inferred project file tree |
| `POST` | `/api/tex/{id}/compile` | Server-side pdflatex → base64 PDF |

---

## Export Formats (`app/services/tex_export.py`)

```python
ExportFormat = Literal["pdf", "html", "tex"]

@dataclass
class ExportResult:
    content: bytes
    mime_type: str
    filename: str

def export_tex_file(tex_source: str, format: ExportFormat, filename: str) -> ExportResult:
    ...  # TEX: raw source, PDF: pdflatex, HTML: pandoc --mathml
```

Route: `GET /api/tex-files/{id}/export?format=pdf|html|tex`

---

## Database Models (`app/db/models.py`)

```python
class User(Base):
    __tablename__ = "users"
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    oauth_provider = Column(Text, nullable=False)
    oauth_sub = Column(Text, nullable=False)
    email = Column(Text, nullable=True)
    full_name = Column(Text, nullable=True)
    avatar_url = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)

class TexFile(Base):
    __tablename__ = "tex_files"
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    filename = Column(Text, nullable=False)
    latex_content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=False)
```

---

## Authentication (`app/auth/clerk.py` + `app/deps.py`)

- `authenticate_request()`: validates Clerk JWT via SDK, returns `ClerkIdentity`
- `get_current_user()`: resolves identity → User model (create if first login)
- Dev bypass: `AUTH_DEV_BYPASS=1` returns fixed dev user
- Error classes: `ClerkAuthError` (401), `ClerkConfigError` (500), `ClerkServiceError` (502)

---

## Error Handling Cheat Sheet

| Situation | HTTP Code | What to Return |
|---|---|---|
| No file uploaded | 400 | `"No file provided"` |
| Wrong file type | 422 | `"Supported formats: jpeg, png, webp, pdf"` |
| File > 10 MB | 413 | `"File too large (max 10MB)"` |
| Invalid PDF | 422 | `"Invalid PDF file"` |
| No pages in PDF | 422 | `"No pages found in PDF"` |
| Gemini rate limited | 429 | `"Gemini rate limit"` |
| Gemini API down | 503 | `"Service unavailable"` |
| Missing auth | 401 | `"Unauthorized"` |
| File not found | 404 | `"File not found"` |
| Compile failure | 422 | `"LaTeX compile failed"` + stderr |
| Tool missing | 500 | `"pdflatex not installed"` / `"pandoc not installed"` |
| Unknown error | 500 | `"Internal server error"` |

---

## Testing

```bash
# Health check
curl http://localhost:8000/api/health

# Convert a PDF (no auth needed)
curl -X POST http://localhost:8000/api/convert -F "file=@test_notes.pdf"

# Convert with context
curl -X POST "http://localhost:8000/api/convert?context=math" -F "file=@math.pdf"

# Export raw .tex
curl -X POST http://localhost:8000/api/export \
  -H "Content-Type: application/json" \
  -d '{"latex": "\\documentclass{article}\\n\\begin{document}\\nHello\\n\\end{document}", "filename": "test"}' \
  --output test.tex

# Run backend tests
cd src/backend && pytest tests/ -v
```
