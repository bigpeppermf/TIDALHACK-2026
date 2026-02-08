from datetime import datetime, timezone
import uuid

import pytest
from sqlalchemy.exc import IntegrityError

from app.db import models


def _create_user(db_session, user_id=None):
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


def test_user_model_creation(db_session):
    user = _create_user(db_session)
    assert user.id is not None
    assert user.oauth_provider == "test-provider"
    assert user.oauth_sub == "test-sub"
    assert user.created_at is not None


def test_texfile_model_creation(db_session, test_user_id):
    _create_user(db_session, user_id=test_user_id)
    tex_file = models.TexFile(
        user_id=test_user_id,
        filename="main.tex",
        latex_content="\\begin{document}Hi\\end{document}",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db_session.add(tex_file)
    db_session.commit()
    db_session.refresh(tex_file)

    assert tex_file.id is not None
    assert tex_file.user_id == test_user_id
    assert tex_file.filename == "main.tex"
    assert tex_file.latex_content


def test_uuid_primary_keys_exist(db_session):
    user = _create_user(db_session)
    assert isinstance(user.id, (str, uuid.UUID))

    tex_file = models.TexFile(
        user_id=user.id,
        filename="paper.tex",
        latex_content="content",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db_session.add(tex_file)
    db_session.commit()
    db_session.refresh(tex_file)

    assert isinstance(tex_file.id, (str, uuid.UUID))


def test_foreign_key_ownership_enforced(db_session):
    tex_file = models.TexFile(
        user_id="nonexistent-user",
        filename="bad.tex",
        latex_content="content",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db_session.add(tex_file)

    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_required_fields_enforced(db_session):
    user = models.User(
        oauth_provider=None,
        oauth_sub="sub",
        email="user@example.com",
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(user)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    _create_user(db_session, user_id="user-with-tex")
    tex_file = models.TexFile(
        user_id="user-with-tex",
        filename=None,
        latex_content="content",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db_session.add(tex_file)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
