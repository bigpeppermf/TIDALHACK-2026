from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response

from app.services.tex_export import export_tex_file, ExportFormat
from app.deps import get_current_user  # adjust if needed

router = APIRouter()


@router.get("/tex-files/{tex_file_id}/export")
def export_tex_file_route(
    tex_file_id: int,
    format: ExportFormat = Query(..., description="pdf | html | tex"),
    user=Depends(get_current_user),
):
    """
    Export a LaTeX file the user is already viewing in the editor/dashboard.
    """
    # TODO:
    # - fetch tex file by id
    # - verify ownership
    # - pass content to service
    raise NotImplementedError
