from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db import crud
from app.deps import get_current_user, get_db
from app.services.tex_export import export_tex_file, ExportFormat

router = APIRouter()


@router.get("/tex-files/{tex_file_id}/export")
def export_tex_file_route(
    tex_file_id: str,
    format: ExportFormat = Query(..., description="pdf | html | tex"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Export a LaTeX file the user is already viewing in the editor/dashboard.
    """
    tex_file = crud.get_tex_file_by_id(
        db=db,
        user_id=user.id,
        tex_id=tex_file_id,
    )
    if tex_file is None:
        raise HTTPException(status_code=404, detail="File not found")

    try:
        result = export_tex_file(
            tex_source=tex_file.latex_content,
            format=format,
            filename=tex_file.filename,
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid export format")
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        # Preserve compile errors with stderr where available.
        stderr = getattr(exc, "stderr", None)
        detail = stderr.strip() if isinstance(stderr, str) and stderr.strip() else "LaTeX export failed"
        raise HTTPException(status_code=422, detail=detail)

    return Response(
        content=result.content,
        media_type=result.mime_type,
        headers={"Content-Disposition": f'attachment; filename="{result.filename}"'},
    )
