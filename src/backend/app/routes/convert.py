import io
import os
import tempfile
import time
from typing import List

from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from app.services.gemini import convert_image_to_latex
from app.services.latex import extract_document_body, wrap_latex_document
from app.utils.image import preprocess_image
from app.utils.pdf import pdf_to_images

router = APIRouter()

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024


def _validate_pdf_upload(file: UploadFile, file_bytes: bytes) -> None:
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=422, detail="Supported format: pdf")

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File too large (max 10MB)")

    if not file_bytes.startswith(b"%PDF"):
        raise HTTPException(status_code=422, detail="Invalid PDF file")


def _image_to_base64(img) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return preprocess_image(buf.getvalue())


@router.post("/convert")
async def convert(
    file: UploadFile = File(...),
    context: str = Query(default="general"),
):
    file_bytes = await file.read()
    _validate_pdf_upload(file, file_bytes)

    start = time.time()

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file_bytes)
            temp_path = tmp.name

        images = pdf_to_images(temp_path, max_pages=5)
        if not images:
            raise HTTPException(status_code=422, detail="No pages found in PDF")

        page_bodies: List[str] = []
        raw_text_pages: List[str] = []
        for img in images:
            base64_img = _image_to_base64(img)
            try:
                raw = convert_image_to_latex(base64_img, context=context)
            except Exception as exc:
                message = str(exc) or "Gemini API error"
                if "429" in message:
                    raise HTTPException(status_code=429, detail="Gemini rate limit")
                if "503" in message or "ServiceUnavailable" in message:
                    raise HTTPException(status_code=503, detail="Service unavailable")
                raise HTTPException(status_code=500, detail=f"Gemini API error: {message}")

            raw_text_pages.append(raw)
            body = extract_document_body(raw)
            page_bodies.append(body)

        combined_body = "\n\n".join(page_bodies)
        latex = wrap_latex_document(combined_body)
        raw_text = "\n\n".join(raw_text_pages)

        processing_ms = int((time.time() - start) * 1000)
        return {
            "success": True,
            "latex": latex,
            "raw_text": raw_text,
            "processing_time_ms": processing_ms,
        }
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
