import google.generativeai as genai
import os
from PIL import Image

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

PROMPT = """
You are converting handwritten lecture notes into accessible content.

Return ONLY valid JSON with this structure:
{
  "title": "...",
  "sections": [
    {
      "heading": "...",
      "content": ["bullet or sentence", "..."],
      "equations": ["LaTeX equation", "..."]
    }
  ]
}

Rules:
- Do not explain
- Do not include markdown
- Do not include backticks
- Preserve math using LaTeX
"""

def image_to_structured_notes(image: Image.Image) -> str:
    response = model.generate_content([PROMPT, image])
    return response.text
