# Backend TeX-to-Format Export – Checklist

> Last updated: Feb 8, 2026

---

## PHASE 1 — Requirements

- [x] Define supported output formats: `pdf`, `html`, `docx`, `md`
- [x] Use pdflatex for PDF generation
- [x] Use pandoc for HTML / DOCX / Markdown generation
- [x] Return export results as bytes with MIME type metadata

## PHASE 2 — API Design

- [x] `POST /api/tex-export` route accepting `{ latex, format }`
- [x] Validate `format` against allowed list
- [x] Return file as streaming response with correct `Content-Type`
- [x] Return `Content-Disposition` header for downloads

## PHASE 3 — PDF Export

- [x] Write LaTeX to temporary `.tex` file
- [x] Run `pdflatex` twice (for references / TOC)
- [x] Read resulting `.pdf` bytes
- [x] Return as `application/pdf`
- [x] Handle compilation errors with log output

## PHASE 4 — HTML Export

- [x] Write LaTeX to temporary `.tex` file
- [x] Run `pandoc --from latex --to html --standalone --mathjax`
- [x] Read resulting `.html` bytes
- [x] Return as `text/html`

## PHASE 5 — DOCX / Markdown Export

- [x] DOCX: `pandoc --from latex --to docx`
- [x] Markdown: `pandoc --from latex --to markdown`
- [x] Return with correct MIME types

## PHASE 6 — Error Handling

- [x] Catch `FileNotFoundError` when pdflatex / pandoc not installed
- [x] Catch `subprocess.CalledProcessError` for compilation failures
- [x] Return meaningful error messages to client
- [ ] Add timeout for long-running compilations
- [ ] Sanitize LaTeX input to prevent shell injection

## PHASE 7 — Integration

- [x] Wire route into FastAPI app via `app.include_router`
- [x] Frontend `useExport` composable calls the endpoint
- [x] Editor page export button triggers download
- [ ] Add progress indicator for large exports

## PHASE 8 — Testing

- [x] Basic API test exists (`test_tex_export_route.py`)
- [x] HTML export test exists (`test_tex_export_html.py`)
- [ ] Test each format independently
- [ ] Test error cases (invalid format, bad LaTeX)
- [ ] Test large document export
