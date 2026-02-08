import io
import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "backend"))

from app.main import app  # noqa: E402
from app.utils.pdf import pdf_to_images  # noqa: E402

def test_convert_pdf_success(monkeypatch):
    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError("Missing GEMINI_API_KEY for integration test.")

    pdf_path = ROOT / "tests" / "api_tests" / "Hand_written_notes" / "test_notes.pdf"
    data = pdf_path.read_bytes()

    client = TestClient(app)
    resp = client.post(
        "/api/convert",
        files={"file": ("test_notes.pdf", io.BytesIO(data), "application/pdf")},
    )

    assert resp.status_code == 200
    payload = resp.json()
    assert "latex" in payload
    assert payload["latex"].startswith("\\documentclass")
    assert "processing_time_ms" in payload

    out_dir = ROOT / "tests" / "api_tests" / "out"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "response.tex"
    out_path.write_text(payload["latex"], encoding="utf-8")

    # Save real PDF page images for inspection.
    images_out = out_dir / "images"
    images_out.mkdir(parents=True, exist_ok=True)
    images = pdf_to_images(str(pdf_path), max_pages=5)
    for i, img in enumerate(images):
        img.save(images_out / f"page_{i+1}.png")
