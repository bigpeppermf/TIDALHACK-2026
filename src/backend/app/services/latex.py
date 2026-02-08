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
