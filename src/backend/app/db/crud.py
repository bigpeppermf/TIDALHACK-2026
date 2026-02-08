from sqlalchemy.orm import Session
from .models import TexFile




# READ — LIST RECENT FILES

def get_recent_tex_files(
    db: Session,
    user_id,
    limit: int = 10
):
    """
    Return the most recent .tex files for a user.
    Ownership is enforced at the query level.
    """
    return (
        db.query(TexFile)
        .filter(TexFile.user_id == user_id)
        .order_by(TexFile.created_at.desc())
        .limit(limit)
        .all()
    )




# READ — GET 1 FILE

def get_tex_file_by_id(
    db: Session,
    user_id,
    tex_id
):
    """
    Retrieve a single .tex file by id.
    Returns None if file does not exist or does not belong to user.
    """
    return (
        db.query(TexFile)
        .filter(
            TexFile.id == tex_id,
            TexFile.user_id == user_id
        )
        .first()
    )




# CREATE — SAVE A NEW FILE



def create_tex_file(
    db: Session,
    user_id,
    filename: str,
    latex: str
):
    """
    Create and persist a new .tex file for a user.
    """
    tex_file = TexFile(
        user_id=user_id,
        filename=filename,
        latex_content=latex
    )

    db.add(tex_file)
    db.commit()
    db.refresh(tex_file)

    return tex_file




# UPDATE — MODIFY FILE



def update_tex_file(
    db: Session,
    tex_file: TexFile,
    filename: str | None = None,
    latex: str | None = None
):
    """
    Update filename and/or LaTeX content for an existing file.
    Caller is responsible for ownership validation.
    """
    if filename is not None:
        tex_file.filename = filename

    if latex is not None:
        tex_file.latex_content = latex

    db.commit()
    db.refresh(tex_file)

    return tex_file




# DELETE — REMOVE FILE



def delete_tex_file(
    db: Session,
    tex_file: TexFile
):
    """
    Permanently delete a .tex file.
    """
    db.delete(tex_file)
    db.commit()
