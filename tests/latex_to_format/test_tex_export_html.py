import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "backend"))

from app.services.tex_export import export_tex_file  # noqa: E402

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
SYMBOLS_TEX_PATH = FIXTURES_DIR / "sample_symbols.tex"


def test_export_tex_file_html():
    latex = SYMBOLS_TEX_PATH.read_text(encoding="utf-8")

    result = export_tex_file(latex, "html", "notes")

    assert result.mime_type == "text/html"
    assert result.filename == "notes.html"
    assert b"<html" in result.content.lower()
    assert b"<math" in result.content.lower()
    assert b"<img" not in result.content.lower()

    out_dir = ROOT / "out"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "tex_export.tex").write_text(latex, encoding="utf-8")
    (out_dir / "tex_export.html").write_bytes(result.content)
