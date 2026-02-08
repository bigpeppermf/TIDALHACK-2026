from datetime import datetime, timezone

import pytest

from app.db import models


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


def _delete_route_exists(test_client, path, method="DELETE"):
    for route in test_client.app.routes:
        if getattr(route, "path", None) == path and method in getattr(route, "methods", []):
            return True
    return False


def test_full_tex_file_flow(test_client, db_session, test_user_id):
    _create_user(db_session, test_user_id)

    create_payload = {"filename": "flow.tex", "latex": "initial"}
    create_resp = test_client.post("/api/tex", json=create_payload)
    assert create_resp.status_code == 200
    created = create_resp.json()
    tex_id = created["id"]

    list_resp = test_client.get("/api/tex")
    assert list_resp.status_code == 200
    listed_ids = [item["id"] for item in list_resp.json()]
    assert tex_id in listed_ids

    get_resp = test_client.get(f"/api/tex/{tex_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["latex"] == "initial"

    update_payload = {"filename": "flow-updated.tex", "latex": "updated"}
    update_resp = test_client.put(f"/api/tex/{tex_id}", json=update_payload)
    assert update_resp.status_code == 200
    assert update_resp.json()["filename"] == "flow-updated.tex"

    download_resp = test_client.get(f"/api/tex/{tex_id}/download")
    assert download_resp.status_code == 200
    assert download_resp.text == "updated"

    if _delete_route_exists(test_client, "/api/tex/{tex_id}"):
        delete_resp = test_client.delete(f"/api/tex/{tex_id}")
        assert delete_resp.status_code in (200, 204)

        missing_resp = test_client.get(f"/api/tex/{tex_id}")
        assert missing_resp.status_code == 404
