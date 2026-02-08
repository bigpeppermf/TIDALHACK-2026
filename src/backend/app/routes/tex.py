from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.db import crud

router = APIRouter()



# LIST RECENT TEX FILES


@router.get("/api/tex")
def list_tex_files(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    # TEMP: replaced by OAuth later
    user_id = "mock-user-id"

    files = crud.get_recent_tex_files(
        db=db,
        user_id=user_id,
        limit=limit
    )

    return [
        {
            "id": f.id,
            "filename": f.filename,
            "created_at": f.created_at,
        }
        for f in files
    ]



# GET SINGLE TEX FILE


@router.get("/api/tex/{tex_id}")
def get_tex_file(
    tex_id: str,
    db: Session = Depends(get_db),
):
    user_id = "mock-user-id"

    tex_file = crud.get_tex_file_by_id(
        db=db,
        user_id=user_id,
        tex_id=tex_id
    )

    if tex_file is None:
        raise HTTPException(status_code=404, detail="File not found")

    return {
        "id": tex_file.id,
        "filename": tex_file.filename,
        "latex": tex_file.latex_content,
        "created_at": tex_file.created_at,
        "updated_at": tex_file.updated_at,
    }



# CREATE NEW TEX FILE


@router.post("/api/tex")
def create_tex_file(
    payload: dict,
    db: Session = Depends(get_db),
):
    user_id = "mock-user-id"

    filename = payload.get("filename")
    latex = payload.get("latex")

    if not filename or not latex:
        raise HTTPException(
            status_code=422,
            detail="Both 'filename' and 'latex' are required"
        )

    tex_file = crud.create_tex_file(
        db=db,
        user_id=user_id,
        filename=filename,
        latex=latex
    )

    return {
        "id": tex_file.id,
        "filename": tex_file.filename,
        "created_at": tex_file.created_at,
    }



# UPDATE EXISTING TEX FILE


@router.put("/api/tex/{tex_id}")
def update_tex_file(
    tex_id: str,
    payload: dict,
    db: Session = Depends(get_db),
):
    user_id = "mock-user-id"

    tex_file = crud.get_tex_file_by_id(
        db=db,
        user_id=user_id,
        tex_id=tex_id
    )

    if tex_file is None:
        raise HTTPException(status_code=404, detail="File not found")

    filename = payload.get("filename")
    latex = payload.get("latex")

    if filename is None and latex is None:
        raise HTTPException(
            status_code=422,
            detail="At least one of 'filename' or 'latex' must be provided"
        )

    updated = crud.update_tex_file(
        db=db,
        tex_file=tex_file,
        filename=filename,
        latex=latex
    )

    return {
        "id": updated.id,
        "filename": updated.filename,
        "updated_at": updated.updated_at,
    }



# DOWNLOAD TEX FILE


@router.get("/api/tex/{tex_id}/download")
def download_tex_file(
    tex_id: str,
    db: Session = Depends(get_db),
):
    user_id = "mock-user-id"

    tex_file = crud.get_tex_file_by_id(
        db=db,
        user_id=user_id,
        tex_id=tex_id
    )

    if tex_file is None:
        raise HTTPException(status_code=404, detail="File not found")

    return Response(
        content=tex_file.latex_content,
        media_type="application/x-tex",
        headers={
            "Content-Disposition": f'attachment; filename="{tex_file.filename}"'
        }
    )
