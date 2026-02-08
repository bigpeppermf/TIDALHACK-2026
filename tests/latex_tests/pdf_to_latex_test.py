import base64
import os
from pathlib import Path
import sys

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "backend"))

from app.services.gemini import convert_image_to_latex  # noqa: E402
from app.services.latex import post_process_latex  # noqa: E402


def _require_env(var_name: str) -> str:
    value = os.getenv(var_name)
    if not value:
        raise RuntimeError(f"Missing {var_name} in environment.")
    return value


def main() -> None:
    load_dotenv(ROOT / ".env")
    _require_env("GEMINI_API_KEY")

    out_dir = Path(__file__).with_name("out")
    out_dir.mkdir(exist_ok=True)

    processed_dir = ROOT / "tests" / "image_tests" / "out"
    if not processed_dir.exists():
        raise FileNotFoundError(
            f"Missing processed images directory at {processed_dir}. "
            "Run tests/image_tests/pdf_to_image_test.py first."
        )

    image_paths = sorted(processed_dir.glob("page_*.processed.jpg"))
    if not image_paths:
        raise FileNotFoundError(
            f"No processed images found in {processed_dir}. "
            "Expected files like page_1.processed.jpg."
        )

    for i, img_path in enumerate(image_paths):
        # The previous test saved processed JPEGs. We base64-encode those bytes here.
        base64_image = base64.b64encode(img_path.read_bytes()).decode("utf-8")
        raw = convert_image_to_latex(base64_image, context="general")
        cleaned = post_process_latex(raw)

        out_path = out_dir / f"page_{i+1}.tex"
        out_path.write_text(cleaned, encoding="utf-8")
        print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
