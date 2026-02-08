import base64
import io
from pathlib import Path
import sys
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "backend"))

from app.utils.image import preprocess_image  # noqa: E402
from app.utils.pdf import pdf_to_images  # noqa: E402


pdf_path = Path(__file__).with_name("test_notes.pdf")
if not pdf_path.exists():
    raise FileNotFoundError(
        f"Missing PDF at {pdf_path}. Place test_notes.pdf next to this test file."
    )

images = pdf_to_images(str(pdf_path), max_pages=5)

print(f"Extracted {len(images)} pages")

out_dir = Path(__file__).with_name("out")
out_dir.mkdir(exist_ok=True)

for i, img in enumerate(images):
    out_path = out_dir / f"page_{i+1}.png"
    img.save(out_path)
    print(f"Saved {out_path}")

    # Run AI-optimized preprocessing and save the processed JPEG for inspection.
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    processed_b64 = preprocess_image(buf.getvalue())
    processed_bytes = base64.b64decode(processed_b64)
    processed_img = Image.open(io.BytesIO(processed_bytes))
    processed_path = out_dir / f"page_{i+1}.processed.jpg"
    processed_img.save(processed_path, format="JPEG")
    print(f"Saved {processed_path}")
