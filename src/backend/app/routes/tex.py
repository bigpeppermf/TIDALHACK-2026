import base64
import re
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.db import crud
from app.db.models import User
from app.services.tex_export import export_tex_file

router = APIRouter()

IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".webp",
    ".bmp",
    ".tiff",
    ".pdf",
}


def _normalize_main_tex_filename(filename: str | None) -> str:
    safe = (filename or "main.tex").strip()
    if not safe:
        return "main.tex"
    if "." not in safe.rsplit("/", maxsplit=1)[-1]:
        return f"{safe}.tex"
    return safe


def _infer_project_files(filename: str, latex_source: str) -> list[dict[str, Any]]:
    by_path: dict[str, dict[str, Any]] = {}

    def add_file(path: str, kind: str, editable: bool = False, stored: bool = False):
        normalized = path.strip().lstrip("./")
        if not normalized:
            return

        existing = by_path.get(normalized)
        if existing:
            existing["stored"] = bool(existing["stored"]) or stored
            existing["editable"] = bool(existing["editable"]) or editable
            return

        by_path[normalized] = {
            "path": normalized,
            "kind": kind,
            "editable": editable,
            "stored": stored,
        }

    def add_parent_directories(path: str):
        segments = path.split("/")
        if len(segments) <= 1:
            return
        for index in range(1, len(segments)):
            directory = "/".join(segments[:index])
            if directory:
                add_file(directory, kind="dir", editable=False, stored=False)

    main_path = _normalize_main_tex_filename(filename)
    add_file(main_path, kind="tex", editable=True, stored=True)
    add_parent_directories(main_path)

    for match in re.findall(r"\\(?:input|include)\{([^}]+)\}", latex_source):
        for raw in match.split(","):
            candidate = raw.strip()
            if not candidate:
                continue
            path = candidate if "." in candidate.rsplit("/", maxsplit=1)[-1] else f"{candidate}.tex"
            add_file(path, kind="tex", editable=False, stored=False)
            add_parent_directories(path)

    for match in re.findall(r"\\bibliography\{([^}]+)\}", latex_source):
        for raw in match.split(","):
            candidate = raw.strip()
            if not candidate:
                continue
            path = candidate if candidate.endswith(".bib") else f"{candidate}.bib"
            add_file(path, kind="bib", editable=False, stored=False)
            add_parent_directories(path)

    for match in re.findall(r"\\addbibresource(?:\[[^\]]*\])?\{([^}]+)\}", latex_source):
        candidate = match.strip()
        if not candidate:
            continue
        path = candidate if candidate.endswith(".bib") else f"{candidate}.bib"
        add_file(path, kind="bib", editable=False, stored=False)
        add_parent_directories(path)

    for match in re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", latex_source):
        candidate = match.strip()
        if not candidate:
            continue
        extension = ""
        if "." in candidate.rsplit("/", maxsplit=1)[-1]:
            extension = f".{candidate.rsplit('.', maxsplit=1)[-1].lower()}"
        kind = "image" if extension in IMAGE_EXTENSIONS else "asset"
        add_file(candidate, kind=kind, editable=False, stored=False)
        add_parent_directories(candidate)

    main_entry = by_path.pop(main_path)
    remaining = sorted(
        by_path.values(),
        key=lambda entry: (entry["kind"] != "dir", str(entry["path"]).lower()),
    )
    return [main_entry, *remaining]


# LIST RECENT TEX FILES


@router.get("/api/tex")
def list_tex_files(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    files = crud.get_recent_tex_files(
        db=db,
        user_id=user.id,
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
    user: User = Depends(get_current_user),
):
    tex_file = crud.get_tex_file_by_id(
        db=db,
        user_id=user.id,
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
    user: User = Depends(get_current_user),
):
    filename = payload.get("filename")
    latex = payload.get("latex")

    if not filename or not latex:
        raise HTTPException(
            status_code=422,
            detail="Both 'filename' and 'latex' are required"
        )

    tex_file = crud.create_tex_file(
        db=db,
        user_id=user.id,
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
    user: User = Depends(get_current_user),
):
    tex_file = crud.get_tex_file_by_id(
        db=db,
        user_id=user.id,
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
    user: User = Depends(get_current_user),
):
    tex_file = crud.get_tex_file_by_id(
        db=db,
        user_id=user.id,
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


@router.delete("/api/tex/{tex_id}")
def delete_tex_file_route(
    tex_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    tex_file = crud.get_tex_file_by_id(
        db=db,
        user_id=user.id,
        tex_id=tex_id
    )

    if tex_file is None:
        raise HTTPException(status_code=404, detail="File not found")

    crud.delete_tex_file(db=db, tex_file=tex_file)

    return {"success": True, "id": str(tex_id)}


@router.get("/api/tex/{tex_id}/files")
def list_project_files(
    tex_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    tex_file = crud.get_tex_file_by_id(
        db=db,
        user_id=user.id,
        tex_id=tex_id
    )

    if tex_file is None:
        raise HTTPException(status_code=404, detail="File not found")

    files = _infer_project_files(
        filename=tex_file.filename,
        latex_source=tex_file.latex_content,
    )

    return {
        "project_id": str(tex_file.id),
        "files": files,
    }


@router.post("/api/tex/{tex_id}/compile")
def compile_tex_project(
    tex_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    tex_file = crud.get_tex_file_by_id(
        db=db,
        user_id=user.id,
        tex_id=tex_id
    )

    if tex_file is None:
        raise HTTPException(status_code=404, detail="File not found")

    try:
        result = export_tex_file(
            tex_source=tex_file.latex_content,
            format="pdf",
            filename=tex_file.filename,
        )
    except RuntimeError as exc:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Compiler unavailable",
                "detail": str(exc),
            },
        )
    except Exception as exc:
        stderr = getattr(exc, "stderr", None)
        detail = stderr.strip() if isinstance(stderr, str) and stderr.strip() else str(exc)
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": "LaTeX compile failed",
                "detail": detail,
            },
        )

    encoded_pdf = base64.b64encode(result.content).decode("ascii")
    return {
        "success": True,
        "project_id": str(tex_file.id),
        "filename": result.filename,
        "pdf_base64": encoded_pdf,
    }
