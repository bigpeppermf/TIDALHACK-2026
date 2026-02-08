from pathlib import Path
from typing import Tuple


def compile_pdf(tex_path: Path) -> Path:
    """
    Compile a .tex file into a PDF.
    Returns the path to the generated PDF.
    """
    raise NotImplementedError


def convert_html(tex_path: Path) -> Path:
    """
    Convert a .tex file into HTML.
    Returns the path to the generated HTML file.
    """
    raise NotImplementedError
