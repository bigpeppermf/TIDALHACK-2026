import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "backend"))

from app.main import app  # noqa: E402


def test_export_tex_success():
    client = TestClient(app)
    payload = {"latex": "\\documentclass{article}\\begin{document}Hi\\end{document}", "filename": "notes"}
    resp = client.post("/api/export", json=payload)

    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("application/x-tex")
    assert "attachment; filename=notes.tex" in resp.headers.get("content-disposition", "")
    assert resp.text.startswith("\\documentclass")
