import re

DEFAULT_PREAMBLE = (
    "\\documentclass[12pt]{article}\n"
    "\\usepackage{amsmath,amssymb,amsfonts}\n"
    "\\usepackage[utf8]{inputenc}\n"
    "\\usepackage{geometry}\n"
    "\\geometry{a4paper, margin=1in}\n"
    "\\begin{document}\n"
)

DOCUMENT_END = "\\end{document}"


def post_process_latex(raw_latex: str) -> str:
    """
    Fix common LLM LaTeX output issues:
    - Strip markdown code fences.
    - Ensure a minimal preamble/document wrapper.
    - Normalize escaped newlines.
    """
    if raw_latex is None:
        return ""

    latex = raw_latex.strip()

    # Strip ```latex ... ``` or ``` ... ``` fences.
    latex = re.sub(r"^```(?:latex)?\s*\n?", "", latex)
    latex = re.sub(r"\n?```\s*$", "", latex)

    # Normalize escaped newlines.
    latex = latex.replace("\\\\n", "\n")

    # If no documentclass, wrap with a minimal preamble + document env.
    if "\\documentclass" not in latex:
        latex = DEFAULT_PREAMBLE + latex + "\n" + DOCUMENT_END
    elif DOCUMENT_END not in latex:
        # Ensure we close the document if the model forgot.
        latex = latex + "\n" + DOCUMENT_END

    return latex.strip()


def extract_document_body(raw_latex: str) -> str:
    """
    Return only the LaTeX document body (between \\begin{document} and \\end{document}).
    If boundaries are missing, return the sanitized string.
    """
    latex = post_process_latex(raw_latex)
    begin = latex.find("\\begin{document}")
    end = latex.rfind("\\end{document}")
    if begin == -1 or end == -1 or end <= begin:
        return latex
    return latex[begin + len("\\begin{document}") : end].strip()


def wrap_latex_document(body: str) -> str:
    """
    Wrap a LaTeX body in a single document preamble and environment.
    """
    return (DEFAULT_PREAMBLE + body + "\n" + DOCUMENT_END).strip()
