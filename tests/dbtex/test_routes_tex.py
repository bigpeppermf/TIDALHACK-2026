from datetime import datetime, timezone

import pytest

from app.db import crud, models


def _create_user(db_session, user_id):
    user = models.User(
        id=user_id,
        oauth_provider="test-provider",
        oauth_sub="test-sub",
        email="user@example.com",
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _create_tex_file(db_session, user_id, filename="main.tex", latex="content"):
    return crud.create_tex_file(
        db=db_session,
        user_id=user_id,
        filename=filename,
        latex=latex,
    )


def test_list_tex_files_returns_only_owned_files(test_client, db_session, test_user_id):
    _create_user(db_session, test_user_id)
    _create_user(db_session, "other-user")

    owned = _create_tex_file(db_session, test_user_id, filename="owned.tex")
    _create_tex_file(db_session, "other-user", filename="other.tex")

    response = test_client.get("/api/tex")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == str(owned.id)
    assert data[0]["filename"] == "owned.tex"
    assert "created_at" in data[0]


def test_get_tex_file_by_id_returns_file(test_client, db_session, test_user_id):
    _create_user(db_session, test_user_id)

    tex_file = _create_tex_file(db_session, test_user_id)

    response = test_client.get(f"/api/tex/{tex_file.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == str(tex_file.id)
    assert data["filename"] == tex_file.filename
    assert data["latex"] == tex_file.latex_content
    assert "created_at" in data
    assert "updated_at" in data


def test_get_tex_file_missing_returns_404(test_client, db_session, test_user_id):
    _create_user(db_session, test_user_id)

    response = test_client.get("/api/tex/nonexistent")
    assert response.status_code == 404


def test_get_tex_file_enforces_ownership(test_client, db_session, test_user_id):
    _create_user(db_session, test_user_id)
    _create_user(db_session, "other-user")

    tex_file = _create_tex_file(db_session, "other-user")

    response = test_client.get(f"/api/tex/{tex_file.id}")
    assert response.status_code == 404


def test_create_tex_file_valid_payload(test_client, db_session, test_user_id):
    _create_user(db_session, test_user_id)

    payload = {"filename": "new.tex", "latex": "content"}
    response = test_client.post("/api/tex", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["filename"] == "new.tex"
    assert "id" in data
    assert "created_at" in data


def test_create_tex_file_invalid_payload(test_client, db_session, test_user_id):
    _create_user(db_session, test_user_id)

    response = test_client.post("/api/tex", json={"filename": "x.tex"})
    assert response.status_code == 422

    response = test_client.post("/api/tex", json={"latex": "content"})
    assert response.status_code == 422


def test_update_tex_file(test_client, db_session, test_user_id):
    _create_user(db_session, test_user_id)

    tex_file = _create_tex_file(db_session, test_user_id)

    payload = {"filename": "updated.tex", "latex": "new"}
    response = test_client.put(f"/api/tex/{tex_file.id}", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == str(tex_file.id)
    assert data["filename"] == "updated.tex"
    assert "updated_at" in data


def test_update_tex_file_missing_returns_404(test_client, db_session, test_user_id):
    _create_user(db_session, test_user_id)

    response = test_client.put("/api/tex/nonexistent", json={"filename": "x"})
    assert response.status_code == 404


def test_update_tex_file_invalid_payload(test_client, db_session, test_user_id):
    _create_user(db_session, test_user_id)

    tex_file = _create_tex_file(db_session, test_user_id)

    response = test_client.put(f"/api/tex/{tex_file.id}", json={})
    assert response.status_code == 422


def test_download_tex_file(test_client, db_session, test_user_id):
    _create_user(db_session, test_user_id)

    tex_file = _create_tex_file(db_session, test_user_id, filename="download.tex", latex="PDF")

    response = test_client.get(f"/api/tex/{tex_file.id}/download")
    assert response.status_code == 200
    assert response.text == "PDF"
    assert response.headers["content-type"].startswith("application/x-tex")
    assert "attachment" in response.headers["content-disposition"].lower()


def test_download_tex_file_missing_returns_404(test_client, db_session, test_user_id):
    _create_user(db_session, test_user_id)

    response = test_client.get("/api/tex/nonexistent/download")
    assert response.status_code == 404


def test_list_project_files_returns_metadata(test_client, db_session, test_user_id):
    _create_user(db_session, test_user_id)
    latex = r"""
    \documentclass{article}
    \begin{document}
    \input{sections/intro}
    \includegraphics[width=\textwidth]{figures/plot.png}
    \bibliography{refs}
    \end{document}
    """
    tex_file = _create_tex_file(db_session, test_user_id, filename="main.tex", latex=latex)

    response = test_client.get(f"/api/tex/{tex_file.id}/files")
    assert response.status_code == 200

    data = response.json()
    assert data["project_id"] == str(tex_file.id)
    paths = {entry["path"]: entry for entry in data["files"]}
    assert "main.tex" in paths
    assert paths["main.tex"]["kind"] == "tex"
    assert paths["main.tex"]["stored"] is True
    assert "sections/intro.tex" in paths
    assert paths["sections/intro.tex"]["kind"] == "tex"
    assert "figures/plot.png" in paths
    assert paths["figures/plot.png"]["kind"] == "image"
    assert "refs.bib" in paths
    assert paths["refs.bib"]["kind"] == "bib"


def test_compile_tex_project_success(monkeypatch, test_client, db_session, test_user_id):
    _create_user(db_session, test_user_id)
    tex_file = _create_tex_file(db_session, test_user_id, filename="main.tex", latex="\\begin{document}ok\\end{document}")

    class _Result:
        content = b"%PDF-1.4"
        filename = "main.pdf"

    def _fake_export_tex_file(*_args, **_kwargs):
        return _Result()

    monkeypatch.setattr("app.routes.tex.export_tex_file", _fake_export_tex_file)

    response = test_client.post(f"/api/tex/{tex_file.id}/compile")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["project_id"] == str(tex_file.id)
    assert data["filename"] == "main.pdf"
    assert isinstance(data["pdf_base64"], str)
    assert len(data["pdf_base64"]) > 0


def test_compile_tex_project_compile_error(monkeypatch, test_client, db_session, test_user_id):
    _create_user(db_session, test_user_id)
    tex_file = _create_tex_file(db_session, test_user_id, filename="main.tex", latex="\\badcommand")

    class _CompileError(Exception):
        def __init__(self):
            super().__init__("compile failed")
            self.stderr = "Undefined control sequence"

    def _fake_export_tex_file(*_args, **_kwargs):
        raise _CompileError()

    monkeypatch.setattr("app.routes.tex.export_tex_file", _fake_export_tex_file)

    response = test_client.post(f"/api/tex/{tex_file.id}/compile")
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert data["error"] == "LaTeX compile failed"
    assert "Undefined control sequence" in data["detail"]
