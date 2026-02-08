# Testing Reference

> Test infrastructure and current coverage.

---

## 1. Test Layout

```
tests/
├── api_tests/
│   ├── test_convert_pdf.py         # Convert endpoint tests
│   └── test_export_tex.py          # Export endpoint tests
├── dbtex/
│   ├── conftest.py                 # DB fixtures (async session, test user)
│   ├── test_crud.py                # CRUD function tests
│   ├── test_integration_tex_flow.py # Full create→read→update→delete flow
│   ├── test_models.py              # ORM model tests
│   └── test_routes_tex.py          # Tex route handler tests
├── image_tests/
│   └── pdf_to_image_test.py        # PDF → image conversion tests
├── latex_tests/
│   └── pdf_to_latex_test.py        # PDF → LaTeX pipeline tests
└── latex_to_format/
    ├── conftest.py                 # Export fixtures
    ├── test_tex_export_html.py     # HTML export tests
    ├── test_tex_export_route.py    # Export route handler tests
    └── fixtures/
        └── sample_symbols.tex      # Test LaTeX document

frontend/
├── src/__tests__/App.spec.ts       # App component test
├── src/components/convert/__tests/ # Convert component tests
├── src/composables/__tests__/      # Composable unit tests
├── src/router/__tests__/           # Router tests
├── src/views/__tests__/            # View component tests
└── e2e/vue.spec.ts                 # Playwright E2E test
```

---

## 2. Backend Tests

### Tools

- **pytest** with `pytest-asyncio` for async tests.
- **httpx** `AsyncClient` for route-level tests against `TestClient`.
- **SQLAlchemy** async sessions with in-memory or test database.

### Running

```bash
cd /path/to/project
pytest tests/ -v
```

### Key Test Areas

| Area | File(s) | What it covers |
|---|---|---|
| Convert API | `api_tests/test_convert_pdf.py` | PDF upload → Gemini → LaTeX response |
| Export API | `api_tests/test_export_tex.py` | LaTeX → PDF/HTML export endpoint |
| DB CRUD | `dbtex/test_crud.py` | create / get / list / update / delete tex files |
| DB Models | `dbtex/test_models.py` | User and TexFile ORM model validation |
| Tex Routes | `dbtex/test_routes_tex.py` | Full route handler tests with auth mocking |
| Integration | `dbtex/test_integration_tex_flow.py` | End-to-end create→edit→compile→delete |
| HTML Export | `latex_to_format/test_tex_export_html.py` | LaTeX → HTML via pandoc |
| Export Route | `latex_to_format/test_tex_export_route.py` | `/api/tex-export` endpoint |
| Image Utils | `image_tests/pdf_to_image_test.py` | PDF page → PNG conversion |
| LaTeX Pipeline | `latex_tests/pdf_to_latex_test.py` | PDF → image → Gemini → LaTeX |

### Auth in Tests

- Tests mock or bypass Clerk authentication.
- `AUTH_DEV_BYPASS=1` can be used for integration tests against a running server.
- Route tests inject a test user via dependency override.

---

## 3. Frontend Tests

### Unit Tests (Vitest)

```bash
cd frontend
npm run test:unit
```

- Uses `@vue/test-utils` for component mounting.
- Uses `jsdom` as the test environment.
- Config in `vitest.config.ts`.

### E2E Tests (Playwright)

```bash
cd frontend
npm run test:e2e
```

- Config in `playwright.config.ts`.
- Basic navigation test in `e2e/vue.spec.ts`.

---

## 4. Coverage Gaps

| Area | Status |
|---|---|
| Convert endpoint (happy path) | ✅ Covered |
| Export endpoint (PDF, HTML) | ✅ Covered |
| Tex CRUD (all operations) | ✅ Covered |
| Compile endpoint | ⚠️ Integration test only |
| Auth guard (401 responses) | ⚠️ Partially covered |
| Frontend composables | ⚠️ Basic tests exist |
| Frontend components | ⚠️ Sparse coverage |
| E2E full user flow | ⚠️ Basic navigation only |
| Multi-user data isolation | ❌ Not tested |
| Rate limiting / abuse | ❌ Not tested |
| Large file uploads | ❌ Not tested |

---

## 5. Test Fixtures

- `tests/latex_to_format/fixtures/sample_symbols.tex` — LaTeX document with math symbols for export tests.
- `tests/api_tests/Hand_written_notes/` — Sample handwritten note images for convert tests.
