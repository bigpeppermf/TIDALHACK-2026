from pdf2image import convert_from_path
from PIL import Image, ImageEnhance
from typing import List


def pdf_to_images(
    pdf_path: str,
    dpi: int = 300,
    max_pages: int = 5
) -> List[Image.Image]:
    """
    Convert a handwritten notes PDF into
    vision-optimized PIL images (one per page).
    """

    # Convert PDF pages to images
    images = convert_from_path(
        pdf_path,
        dpi=dpi,
        fmt="png",
        grayscale=True
    )

    ## process them by turning up the contrast a bit, which helps Gemini Vision read handwriting better.
    processed = []
    for img in images[:max_pages]:
        # Light contrast boost for handwriting
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.4)
        processed.append(img)

    return processed
