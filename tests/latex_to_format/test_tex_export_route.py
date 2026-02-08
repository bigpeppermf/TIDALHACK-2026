from datetime import datetime, timezone

from app.db import crud, models
from app.services.tex_export import ExportResult


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


def test_export_html_route_uses_mathml(test_client, db_session, test_user_id, monkeypatch):
    _create_user(db_session, test_user_id)
    tex_file = crud.create_tex_file(
        db=db_session,
        user_id=test_user_id,
        filename="notes.tex",
        latex="\\documentclass{article}\\begin{document}Hello\\end{document}",
    )

    def fake_export(tex_source, format, filename):
        assert format == "html"
        assert tex_source
        return ExportResult(
            content=b"<html><body><math></math></body></html>",
            mime_type="text/html",
            filename="notes.html",
        )

    monkeypatch.setattr("app.routes.tex_export.export_tex_file", fake_export)

    response = test_client.get(f"/api/tex-files/{tex_file.id}/export?format=html")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert b"<math" in response.content
