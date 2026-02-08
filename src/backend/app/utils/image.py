import base64
import io
from PIL import Image, ImageEnhance, ImageFilter

MAX_SIZE = 2048
JPEG_QUALITY = 90
CONTRAST_FACTOR = 1.5


def preprocess_image(image_bytes: bytes) -> str:
    """
    GOAL: Normalize an image for Gemini Vision:
    - RGB only
    - Resize if too large
    - Increase contrast
    - Sharpen strokes
    - Encode as base64 JPEG

    Returns:
        base64-encoded JPEG string
    """

    img = Image.open(io.BytesIO(image_bytes))

    # Ensure RGB (strip alpha)
    if img.mode != "RGB":
        img = img.convert("RGB")

    # Resize while preserving aspect ratio
    w, h = img.size
    if max(w, h) > MAX_SIZE:
        scale = MAX_SIZE / max(w, h)
        img = img.resize(
            (int(w * scale), int(h * scale)),
            Image.LANCZOS
        )

    # Improve handwriting contrast
    img = ImageEnhance.Contrast(img).enhance(CONTRAST_FACTOR)

    # Sharpen edges
    img = img.filter(ImageFilter.SHARPEN)

    # Encode to base64 JPEG
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=JPEG_QUALITY)
    buffer.seek(0)

    return base64.b64encode(buffer.read()).decode("utf-8")
