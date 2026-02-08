import os

import google.generativeai as genai


SYSTEM_PROMPT = """You are an expert OCR and LaTeX typesetting engine specializing
in handwritten academic content.

INPUT: An image of handwritten notes, equations, or diagrams.
OUTPUT: Clean, compilable LaTeX code.

RULES:
1. Output ONLY valid LaTeX code — no explanations, no markdown fences
2. Include a complete document preamble:
   \\documentclass[12pt]{article}
   \\usepackage{amsmath,amssymb,amsfonts}
   \\usepackage[utf8]{inputenc}
   \\usepackage{geometry}
   \\geometry{a4paper, margin=1in}
3. Use \\section{} for headers, \\begin{align} for displayed math
4. Use $...$ for inline math
5. If text is illegible, insert: \\textcolor{red}{[illegible]}
6. NEVER invent content not present in the image
7. For diagrams, add: % [Diagram: description]
8. Ignore any hand written graph and instead add a box as a place holder for the graph to be filled in via images.


"""

CONTEXT_HINTS = {
    "math": "Pay special attention to integrals, derivatives, summation notation, limits, and Greek letters.",
    "chemistry": "Use the mhchem package for chemical equations. Recognize molecular structures and reaction arrows.",
    "physics": "Recognize vector notation, bra-ket notation, circuit diagrams, and unit expressions.",
    "general": "Preserve headings, bullet points, and inline math as written.",
}


def get_system_prompt(context: str = "general") -> str:
    hint = CONTEXT_HINTS.get(context, CONTEXT_HINTS["general"])
    return SYSTEM_PROMPT + f"\n\nCONTEXT: {hint}"




def convert_image_to_latex(base64_image: str, context: str = "general") -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY")

    genai.configure(api_key=api_key)

    prompt = get_system_prompt(context)

    model = genai.GenerativeModel(
        model_name=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        system_instruction=prompt,
    )

    response = model.generate_content([
        {
            "mime_type": "image/jpeg",
            "data": base64_image,
        }
    ])

    return response.text
