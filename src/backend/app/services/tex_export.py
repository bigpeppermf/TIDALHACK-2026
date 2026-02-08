from dataclasses import dataclass
import os
import shutil
import subprocess
import tempfile
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
    safe_name = filename or "document"

    if format == "tex":
        return ExportResult(
            content=tex_source.encode("utf-8"),
            mime_type="application/x-tex",
            filename=f"{safe_name}.tex",
        )

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, "input.tex")
        with open(input_path, "w", encoding="utf-8") as handle:
            handle.write(tex_source)

        if format == "html":
            if shutil.which("pandoc") is None:
                raise RuntimeError("pandoc not installed")
            output_path = os.path.join(tmpdir, "output.html")
            subprocess.run(
                ["pandoc", "-f", "latex", "-t", "html", "--mathml", "-s", input_path, "-o", output_path],
                check=True,
                capture_output=True,
                text=True,
            )
            with open(output_path, "rb") as handle:
                content = handle.read()
            return ExportResult(
                content=content,
                mime_type="text/html",
                filename=f"{safe_name}.html",
            )

        if format == "pdf":
            if shutil.which("pdflatex") is None:
                raise RuntimeError("pdflatex not installed")
            subprocess.run(
                [
                    "pdflatex",
                    "-interaction=nonstopmode",
                    "-halt-on-error",
                    "-output-directory",
                    tmpdir,
                    input_path,
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            output_path = os.path.join(tmpdir, "input.pdf")
            with open(output_path, "rb") as handle:
                content = handle.read()
            return ExportResult(
                content=content,
                mime_type="application/pdf",
                filename=f"{safe_name}.pdf",
            )

    raise ValueError("Unsupported format")
