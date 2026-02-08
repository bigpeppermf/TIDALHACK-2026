import re
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

router = APIRouter()


class ExportRequest(BaseModel):
    latex: str
    filename: str = "notes"


@router.post("/export")
async def export_tex(req: ExportRequest):
    if not req.latex or not req.latex.strip():
        raise HTTPException(status_code=422, detail="LaTeX content is required")

    filename = (req.filename or "").strip() or "notes"
    filename = re.sub(r"\s+", " ", filename)
    filename = re.sub(r"\.(tex|pdf|html)$", "", filename, flags=re.IGNORECASE)
    return Response(
        content=req.latex,
        media_type="application/x-tex",
        headers={"Content-Disposition": f'attachment; filename="{filename}.tex"'},
    )
