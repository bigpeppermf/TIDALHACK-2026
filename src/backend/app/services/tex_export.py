from dataclasses import dataclass
from typing import Literal


ExportFormat = Literal["pdf", "html", "tex"]


@dataclass
class ExportResult:
    content: bytes
    mime_type: str
    filename: str


def export_tex_file(
    tex_source: str,
    format: ExportFormat,
    filename: str,
) -> ExportResult:
    """
    Convert LaTeX source into the requested format.

    This function:
    - assumes tex_source is already validated and owned by the user
    - does NOT perform auth, DB access, or HTTP logic
    """
    raise NotImplementedError
