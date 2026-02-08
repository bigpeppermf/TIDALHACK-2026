# BACKEND – TeX File Export (PDF / HTML / TEX)

## Goal
Allow users to download a stored LaTeX file as:
- `.pdf`
- `.html`
- `.tex`

The output format is determined by a backend query parameter.

---

## Phase 1 — Data Model & Inputs
- [ ] Identify the primary key field used by the LaTeX file model (e.g., `tex_file_id`) and its type
- [ ] Confirm the LaTeX source is already retrieved by the backend for this endpoint and available as a raw string
- [ ] Validate `format` against the allowed set (`pdf | html | tex`) after trimming and lowercasing
- [ ] Reject unsupported or missing `format` with 400 and an allowed-values message

---

## Phase 2 — API Design
- [ ] Register `GET /tex-files/{id}/download` in the backend router
- [ ] Parse `id` from the path and `format` from the query string
- [ ] Authenticate the caller and enforce file ownership for the requested `id`
- [ ] Ignore any client-supplied file paths; only server-created temp paths are used

---

## Phase 3 — TEX Output
- [ ] Return the raw LaTeX source bytes encoded as UTF-8
- [ ] Set headers:
  - `Content-Type: application/x-tex`
  - `Content-Disposition: attachment; filename="{slug}.tex"`
- [ ] Derive `{slug}` from stored metadata; fall back to the file id if missing

---

## Phase 4 — PDF Generation
- [ ] Create a unique temp directory per request
- [ ] Write LaTeX source to `input.tex` within the temp directory
- [ ] Execute `pdflatex` via a subprocess argument list (no shell) with:
  - `-interaction=nonstopmode`
  - `-halt-on-error`
- [ ] Enforce a compile timeout and capture stdout/stderr
- [ ] Verify `input.pdf` exists and is non-empty
- [ ] Return PDF bytes with download headers
- [ ] Cleanup the temp directory in a `finally`/defer block

---

## Phase 5 — HTML Generation (Accessible, MathML-first)
- [ ] Create a unique temp directory per request
- [ ] Write LaTeX source to `input.tex` within the temp directory
- [ ] Execute `pandoc` via a subprocess argument list (no shell) to produce `output.html`
- [ ] Use `-f latex -t html --mathml -s` to emit semantic HTML + MathML
- [ ] Verify `output.html` exists and is non-empty
- [ ] Return HTML bytes with `Content-Type: text/html` and download headers
- [ ] Confirm MathML is present and no image-based equations are emitted
- [ ] Verify screen-reader compatibility (VoiceOver/NVDA/JAWS) on sample output
- [ ] Cleanup the temp directory in a `finally`/defer block

---

## Phase 6 — Error Handling
- [ ] Invalid or missing format → 400
- [ ] File not found → 404
- [ ] Unauthorized access → 403
- [ ] LaTeX compile failure → 422 with stderr excerpt
- [ ] Tool missing or not executable → 500 with actionable error

---

## Phase 7 — Security & Stability
- [ ] Invoke external tools with a fixed argument list (no `shell=True`)
- [ ] Run conversions in isolated temp directories only
- [ ] Enforce maximum LaTeX source size before writing to disk
- [ ] Enforce subprocess timeouts for both PDF and HTML conversions

---

## Phase 8 — Testing
- [ ] Unit test: `format` validation (valid, invalid, missing)
- [ ] Integration test: PDF generation from minimal LaTeX fixture
- [ ] Integration test: HTML generation from minimal LaTeX fixture
- [ ] Snapshot test: `.tex` download body and headers
