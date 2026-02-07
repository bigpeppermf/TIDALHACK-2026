# 🧪 ScribeTeX — Test Cases

> **How to verify everything works before demo day**
> Last updated: Feb 7, 2026

---

## Testing Strategy

We have **3 levels** of testing. For a 24-hour hackathon, focus on **Level 1 first**, then Level 2 during polish. Level 3 only if you have time.

| Level | What | When | How |
|---|---|---|---|
| **1. Smoke Tests** | Does it work at all? | After each feature | Manual — curl + browser |
| **2. Edge Case Tests** | Does it handle bad input? | Phase 3 (polish) | Manual — feed it weird stuff |
| **3. Automated Tests** | Repeatable checks | Only if time | pytest + Vitest scripts |

---

## Level 1 — Smoke Tests (Do These First)

### ⚙️ Backend Smoke Tests

| # | Test | How | Expected Result |
|---|---|---|---|
| B1 | Health check | `curl http://localhost:8000/api/health` | `{ "status": "ok" }` |
| B2 | Convert — clean handwriting | `curl -X POST http://localhost:8000/api/convert -F "file=@clean_notes.jpg"` | `{ "success": true, "latex": "\\documentclass..." }` |
| B3 | Convert — math equations | Same curl with a photo of math | LaTeX with `\int`, `\sum`, `\frac`, etc. |
| B4 | Convert — whiteboard photo | Same curl with whiteboard photo | LaTeX output (may be lower quality, that's ok) |
| B5 | Export endpoint | `curl -X POST http://localhost:8000/api/export -H "Content-Type: application/json" -d '{"latex": "\\documentclass{article}", "filename": "test"}'` | File download response |
| B6 | LaTeX compiles | Copy output LaTeX → paste in Overleaf or `pdflatex` | Compiles without errors |

### 🎨 Frontend Smoke Tests

| # | Test | How | Expected Result |
|---|---|---|---|
| F1 | Pages load | Open `localhost:5173` and `localhost:5173/convert` | Both pages render without errors |
| F2 | Upload works | Drag-and-drop a JPEG onto upload zone | Image preview appears |
| F3 | Upload via picker | Click file picker, select an image | Image preview appears |
| F4 | Full flow | Upload image → wait → see result | LaTeX appears in editor + KaTeX preview renders |
| F5 | Copy button | Click "Copy to Clipboard" | LaTeX string in clipboard (paste to verify) |
| F6 | Download button | Click "Download .tex" | `.tex` file downloads, open it, content matches |
| F7 | Live editing | Edit LaTeX in editor | KaTeX preview updates in real time |
| F8 | Loading state | Upload image, watch during processing | Spinner/animation shows, disappears when done |

---

## Level 2 — Edge Case Tests

### ⚙️ Backend Edge Cases

| # | Test | Input | Expected |
|---|---|---|---|
| BE1 | Wrong file type | Upload a `.txt` or `.pdf` file | 422 error: "Supported formats: jpeg, png, webp" |
| BE2 | Oversized file | Upload a 15MB image | 413 error: "File too large (max 10MB)" |
| BE3 | No file sent | POST with empty body | 400 or 422 error |
| BE4 | Corrupted image | Upload a renamed `.txt` as `.jpg` | Graceful error, not a crash |
| BE5 | Very small image | Upload a 10x10px image | Returns something (may be low quality) |
| BE6 | Blank/white image | Upload a blank white image | Returns minimal/empty LaTeX, doesn't crash |
| BE7 | Rotated image | Upload a 90° rotated photo | Still attempts recognition |
| BE8 | Invalid context param | `?context=foobar` | Falls back to "general" or returns error |
| BE9 | Rapid requests | Send 5 requests in 2 seconds | Handles gracefully (queue or rate limit) |
| BE10 | API key missing | Unset `GEMINI_API_KEY` | Clear error message, not unhandled exception |

### 🎨 Frontend Edge Cases

| # | Test | Action | Expected |
|---|---|---|---|
| FE1 | Backend offline | Stop backend, try to convert | Friendly error message in UI, no white screen |
| FE2 | Slow response | Backend takes 10+ seconds | Loading animation keeps playing, no timeout |
| FE3 | Empty LaTeX response | Backend returns `{ "latex": "" }` | Handled gracefully, editor shows empty |
| FE4 | Invalid LaTeX | Backend returns broken LaTeX | KaTeX shows error message, doesn't crash page |
| FE5 | Upload then cancel | Select file, then clear/reselect | State resets properly |
| FE6 | Double click convert | Click upload twice rapidly | Doesn't send duplicate requests |
| FE7 | Very long LaTeX | Backend returns 10,000+ character LaTeX | Editor and preview handle it (may scroll) |
| FE8 | Mobile viewport | Resize browser to 375px width | Layout doesn't break completely |
| FE9 | Copy with empty result | Click copy before any conversion | Doesn't crash, maybe shows toast "Nothing to copy" |

---

## Level 3 — Automated Tests (Only If Time)

### ⚙️ Backend — pytest

```
tests/
├── test_health.py
├── test_convert.py
├── test_image_processing.py
└── test_latex_processing.py
```

#### `test_health.py`

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
```

#### `test_convert.py`

```python
import os

def test_convert_valid_image():
    with open("tests/fixtures/clean_notes.jpg", "rb") as f:
        r = client.post("/api/convert", files={"file": ("test.jpg", f, "image/jpeg")})
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert "\\documentclass" in data["latex"]
    assert data["processing_time_ms"] > 0

def test_convert_invalid_type():
    r = client.post("/api/convert", files={"file": ("test.txt", b"hello", "text/plain")})
    assert r.status_code == 422

def test_convert_oversized():
    big_file = b"x" * (11 * 1024 * 1024)  # 11MB
    r = client.post("/api/convert", files={"file": ("big.jpg", big_file, "image/jpeg")})
    assert r.status_code == 413
```

#### `test_image_processing.py`

```python
from app.utils.image import preprocess_image
from PIL import Image
import io

def test_preprocess_converts_rgba_to_rgb():
    img = Image.new("RGBA", (100, 100), (255, 0, 0, 128))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    result = preprocess_image(buf.getvalue())
    assert isinstance(result, str)  # base64 string
    assert len(result) > 0

def test_preprocess_resizes_large_image():
    img = Image.new("RGB", (5000, 5000), (255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    result = preprocess_image(buf.getvalue(), max_size=2048)
    # Decode and check size
    import base64
    decoded = base64.b64decode(result)
    result_img = Image.open(io.BytesIO(decoded))
    assert max(result_img.size) <= 2048
```

#### `test_latex_processing.py`

```python
from app.services.latex import post_process_latex

def test_strips_markdown_fences():
    raw = "```latex\n\\documentclass{article}\n```"
    result = post_process_latex(raw)
    assert "```" not in result
    assert "\\documentclass" in result

def test_adds_preamble_if_missing():
    raw = "Hello world \\( x^2 \\)"
    result = post_process_latex(raw)
    assert "\\documentclass" in result
    assert "\\begin{document}" in result

def test_preserves_existing_preamble():
    raw = "\\documentclass[11pt]{article}\n\\begin{document}\nHello\n\\end{document}"
    result = post_process_latex(raw)
    assert result.count("\\documentclass") == 1
```

#### Run tests:

```bash
cd src/backend
pip install pytest httpx
pytest tests/ -v
```

### 🎨 Frontend — Vitest (if scaffolded with testing)

```bash
npm install -D vitest @vue/test-utils happy-dom
```

```typescript
// tests/useExport.test.ts
import { describe, it, expect, vi } from 'vitest'
import { useExport } from '../src/composables/useExport'

describe('useExport', () => {
  it('copies text to clipboard', async () => {
    const mockClipboard = { writeText: vi.fn().mockResolvedValue(undefined) }
    Object.assign(navigator, { clipboard: mockClipboard })
    
    const { copyToClipboard } = useExport()
    await copyToClipboard('\\documentclass{article}')
    
    expect(mockClipboard.writeText).toHaveBeenCalledWith('\\documentclass{article}')
  })
})
```

---

## 📷 Test Image Set

Create a `tests/fixtures/` folder with these images:

| # | Image | Type | Tests |
|---|---|---|---|
| 1 | `clean_notes.jpg` | Black pen on white paper | Baseline — should work well |
| 2 | `math_equations.jpg` | Calculus (integrals, limits) | Math symbol recognition |
| 3 | `whiteboard.jpg` | Whiteboard photo with glare | Handles noise/glare |
| 4 | `pencil_notes.jpg` | Light pencil on lined paper | Low contrast handling |
| 5 | `dense_math.jpg` | Full page of dense equations | Large output handling |
| 6 | `mixed_content.jpg` | Text + equations + diagrams | Structure preservation |
| 7 | `rotated.jpg` | Photo taken at an angle | Orientation handling |
| 8 | `blank.jpg` | Blank white page | Edge case — empty input |

> **Tip:** Take these photos with your phone during setup. Real photos are better test data than synthetic images.

---

## 🏃 Quick Test Commands Cheat Sheet

```bash
# Backend health
curl http://localhost:8000/api/health

# Convert an image
curl -X POST http://localhost:8000/api/convert -F "file=@tests/fixtures/clean_notes.jpg"

# Convert with math context
curl -X POST "http://localhost:8000/api/convert?context=math" -F "file=@tests/fixtures/math_equations.jpg"

# Export LaTeX
curl -X POST http://localhost:8000/api/export \
  -H "Content-Type: application/json" \
  -d '{"latex": "\\documentclass{article}\\n\\begin{document}\\nHello\\n\\end{document}", "filename": "test"}' \
  --output test.tex

# Run pytest
cd src/backend && pytest tests/ -v

# Run vitest
cd src/frontend && npx vitest run
```
