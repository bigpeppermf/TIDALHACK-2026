# Backend TeX-to-Format Export – Reference

> Canonical reference for the TeX export pipeline.

---

## 1. Overview

The export system converts LaTeX source into downloadable files in four formats: **PDF**, **HTML**, **DOCX**, and **Markdown**. PDF is produced via `pdflatex`; the other three via `pandoc`.

---

## 2. Core Types

### ExportFormat (services/tex_export.py)

```
Literal["pdf", "html", "docx", "md"]
```

### ExportResult (services/tex_export.py)

| Field | Type | Description |
|---|---|---|
| content | bytes | Exported file content |
| media_type | str | MIME type (e.g. `application/pdf`) |
| filename | str | Suggested download filename |

---

## 3. Service Layer — `export_tex_file()`

**Location**: `src/backend/app/services/tex_export.py`

**Signature**: `async def export_tex_file(latex_content: str, fmt: ExportFormat) -> ExportResult`

### Flow

1. Creates a temporary directory via `tempfile.mkdtemp()`.
2. Writes `latex_content` to `input.tex` inside the temp dir.
3. Based on `fmt`:
   - **pdf**: Runs `pdflatex -interaction=nonstopmode -output-directory=<tmp> input.tex` twice. Reads `input.pdf`.
   - **html**: Runs `pandoc input.tex --from latex --to html --standalone --mathjax -o output.html`. Reads `output.html`.
   - **docx**: Runs `pandoc input.tex --from latex --to docx -o output.docx`. Reads `output.docx`.
   - **md**: Runs `pandoc input.tex --from latex --to markdown -o output.md`. Reads `output.md`.
4. Returns `ExportResult(content, media_type, filename)`.
5. Cleans up temp directory in `finally` block via `shutil.rmtree`.

### MIME Types

| Format | MIME Type | Extension |
|---|---|---|
| pdf | `application/pdf` | `.pdf` |
| html | `text/html` | `.html` |
| docx | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` | `.docx` |
| md | `text/markdown` | `.md` |

### Error Handling

- `FileNotFoundError` → HTTP 500 with message about missing `pdflatex` or `pandoc`.
- `subprocess.CalledProcessError` → HTTP 500 with stderr / log output.
- Unknown format → `ValueError` (caught by route as 400).

---

## 4. Route — `POST /api/tex-export`

**Location**: `src/backend/app/routes/tex_export.py`

### Request

```json
{
  "latex": "\\documentclass{article}\\begin{document}Hello\\end{document}",
  "format": "pdf"
}
```

- `latex` (str, required): LaTeX source code.
- `format` (str, required): One of `pdf`, `html`, `docx`, `md`.

### Response

- **200**: Streaming file download.
  - `Content-Type`: Appropriate MIME type.
  - `Content-Disposition`: `attachment; filename="export.<ext>"`.
- **400**: Invalid format.
- **500**: Compilation or tool error.

### Implementation

```python
@router.post("/tex-export")
async def export_tex(request: ExportRequest):
    result = await export_tex_file(request.latex, request.format)
    return StreamingResponse(
        io.BytesIO(result.content),
        media_type=result.media_type,
        headers={"Content-Disposition": f'attachment; filename="{result.filename}"'}
    )
```

---

## 5. Frontend Integration

### useExport Composable (frontend/src/composables/useExport.ts)

- `exportDocument(latex, format)`: Sends POST to `/api/tex-export`, receives blob, triggers browser download.
- Uses `authFetch` (which attaches the Clerk session token).
- Called from the Editor page export buttons.

### Export UI

- Editor page toolbar offers PDF / HTML / DOCX / Markdown export buttons.
- Triggers `useExport.exportDocument()` with the current CodeMirror content.

---

## 6. Prerequisites

| Tool | Purpose | Install |
|---|---|---|
| `pdflatex` | PDF compilation | `apt install texlive-latex-base texlive-latex-extra` |
| `pandoc` | HTML / DOCX / MD conversion | `apt install pandoc` |

Both must be on `$PATH` for the export service to work.

---

## 7. Implementation Map

| Concern | File |
|---|---|
| Export service | `src/backend/app/services/tex_export.py` |
| Export route | `src/backend/app/routes/tex_export.py` |
| Frontend composable | `frontend/src/composables/useExport.ts` |
| Tests | `tests/latex_to_format/test_tex_export_route.py` |
| Tests (HTML) | `tests/latex_to_format/test_tex_export_html.py` |
