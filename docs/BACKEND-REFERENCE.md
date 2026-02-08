# ⚙️ Backend Code Reference — Python

> **Teammate 2's code snippets. Pull what you need as you build.**
> Last updated: Feb 7, 2026 (via Context7 MCP)

---

## Dependencies

```
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
python-multipart>=0.0.12
google-genai>=1.0.0
Pillow>=11.0.0
python-dotenv>=1.0.0
pydantic>=2.0.0
```

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## FastAPI App Shell

```python
# src/backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="ScribeTeX API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
```

```bash
# Run from src/backend/
uvicorn app.main:app --reload --port 8000
```

---

## Gemini API — Option A: Official SDK (Recommended)

```python
# src/backend/app/services/gemini.py
import os
import base64
from google import genai
from google.genai import types

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def convert_image_to_latex(base64_image: str, context: str = "general") -> str:
    prompt = get_system_prompt(context)
    image_bytes = base64.b64decode(base64_image)
    
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        contents=[
            types.Part.from_text(prompt),
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
        ]
    )
    
    return response.text
```

---

## Gemini API — Option B: OpenAI-Compatible

```python
# Alternative if you prefer OpenAI client style
import os
import base64
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def convert_image_to_latex(base64_image: str, context: str = "general") -> str:
    prompt = get_system_prompt(context)
    
    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]
        }]
    )
    
    return response.choices[0].message.content
```

> **Pick ONE approach and stick with it.** Don't mix.

---

## The LaTeX Prompt

```python
# src/backend/app/services/gemini.py

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

## Image Preprocessing

```python
# src/backend/app/utils/image.py
from PIL import Image, ImageEnhance, ImageFilter
import io
import base64

def preprocess_image(file_bytes: bytes, max_size: int = 2048) -> str:
    """Optimize image for Gemini Vision API."""
    img = Image.open(io.BytesIO(file_bytes))
    
    # Convert to RGB (strip alpha)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Resize if too large
    if max(img.size) > max_size:
        img.thumbnail((max_size, max_size), Image.LANCZOS)
    
    # Boost contrast (helps with pencil/whiteboard)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.5)
    
    # Sharpen
    img = img.filter(ImageFilter.SHARPEN)
    
    # Encode to base64
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=90)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')
```

---

## LaTeX Post-Processing

```python
# src/backend/app/services/latex.py
import re

def post_process_latex(raw_latex: str) -> str:
    """Fix common Gemini output issues."""
    # Strip markdown code fences
    latex = re.sub(r'^```(?:latex)?\n?', '', raw_latex)
    latex = re.sub(r'\n?```$', '', latex)
    
    # Ensure document preamble exists
    if '\\documentclass' not in latex:
        preamble = (
            '\\documentclass[12pt]{article}\n'
            '\\usepackage{amsmath,amssymb,amsfonts}\n'
            '\\usepackage[utf8]{inputenc}\n'
            '\\usepackage{geometry}\n'
            '\\geometry{a4paper, margin=1in}\n'
            '\\begin{document}\n'
        )
        latex = preamble + latex + '\n\\end{document}'
    
    # Fix escaped newlines
    latex = latex.replace('\\\\n', '\n')
    
    return latex.strip()
```

---

## Convert Endpoint

```python
# src/backend/app/routes/convert.py
from fastapi import APIRouter, UploadFile, File, Query, HTTPException
import time

router = APIRouter()

@router.post("/api/convert")
async def convert(
    file: UploadFile = File(...),
    context: str = Query(default="general")
):
    # Validate file type
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(422, detail="Supported formats: jpeg, png, webp")
    
    # Read and validate size
    file_bytes = await file.read()
    if len(file_bytes) > 10 * 1024 * 1024:
        raise HTTPException(413, detail="File too large (max 10MB)")
    
    start = time.time()
    
    # Pipeline: preprocess → Gemini → post-process
    base64_img = preprocess_image(file_bytes)
    raw_latex = convert_image_to_latex(base64_img, context)
    latex = post_process_latex(raw_latex)
    
    elapsed = round((time.time() - start) * 1000)
    
    return {
        "success": True,
        "latex": latex,
        "processing_time_ms": elapsed
    }
```

---

## Export Endpoint

```python
# src/backend/app/routes/export.py
from fastapi import APIRouter
from fastapi.responses import Response
from pydantic import BaseModel

router = APIRouter()

class ExportRequest(BaseModel):
    latex: str
    filename: str = "notes"

@router.post("/api/export")
async def export_tex(req: ExportRequest):
    return Response(
        content=req.latex,
        media_type="application/x-tex",
        headers={"Content-Disposition": f"attachment; filename={req.filename}.tex"}
    )
```

---

## Error Handling Cheat Sheet

| Situation | HTTP Code | What to Return |
|---|---|---|
| No file uploaded | 400 | `"No file provided"` |
| Wrong file type | 422 | `"Supported formats: jpeg, png, webp"` |
| File > 10MB | 413 | `"File too large (max 10MB)"` |
| Gemini rate limited | 429 | `"Rate limit — try again in a few seconds"` |
| Gemini API down | 503 | `"Service unavailable"` |
| Unknown error | 500 | `"Internal server error"` |

---

## Testing Tips

- Test with `curl` before connecting frontend:
  ```bash
  curl -X POST http://localhost:8000/api/convert \
    -F "file=@test_notes.jpg" \
    -F "context=math"
  ```
- Try 5+ different image types (see CHECKLIST.md Phase 2)
- Log processing times — if > 10s, image might be too large
- The **prompt matters more than the code** — iterate on it
