# Backend Reference – LaTeX Export Formats

## Supported Formats

| Format | Description | Tooling |
|------|------------|--------|
| TEX  | Raw LaTeX source | None |
| PDF  | Compiled document | pdflatex |
| HTML | Web-renderable output (semantic HTML + MathML) | pandoc |

---

## API Endpoint

`GET /api/tex-files/{id}/export?format=pdf|html|tex`

- Auth required (Clerk session JWT)
- Ownership enforced by `user_id`
- Responds with a file download and `Content-Disposition`

---

## Recommended Tooling

### PDF
- `pdflatex`
- Run with flags:
  - `-interaction=nonstopmode`
  - `-halt-on-error`
- Expected output file: `input.pdf`

### HTML (Accessible, MathML-first)
- `pandoc`
  - Input: `input.tex`
  - Output: `output.html`
  - Use explicit format args: `-f latex -t html --mathml -s`
  - Math is represented using native MathML (no images)
  - Output is WCAG 2.1 AA aligned and usable without JavaScript
  - Screen readers: VoiceOver / NVDA / JAWS
- Expected output file: `output.html`

---

## Temp File Strategy
- Create a unique temp directory per request
- Write source to `input.tex`
- Generate output in the same directory
- Remove the directory after the response is sent (always in cleanup)

---

## Execution Flow

1. LaTeX source is already available in memory for the request
2. Validate requested format
3. Write `input.tex` into a new temp directory
4. Produce output based on format (`input.pdf` or `output.html`), or return raw source for `tex`
5. Cleanup temp directory

---

## HTTP Headers

### PDF
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="document.pdf"
```

### HTML
```
Content-Type: text/html
Content-Disposition: attachment; filename="document.html"
```
Notes:
- Output includes semantic HTML structure and embedded MathML.
- Math is accessible to VoiceOver/NVDA/JAWS (MathML support).

### TEX
```
Content-Type: application/x-tex
Content-Disposition: attachment; filename="document.tex"
```

---

## Failure Modes & Responses

| Case | HTTP | Notes |
|----|----|----|
| Invalid or missing format | 400 | Reject early with allowed values |
| File not found | 404 | Unknown id |
| Unauthorized | 403 | Ownership enforced |
| Compile error | 422 | Include stderr excerpt |
| Tool missing | 500 | Log and return actionable error |

---

## Non-Goals
- No presentation-layer rendering
- No client-side format conversion
- No persistent storage of generated outputs
