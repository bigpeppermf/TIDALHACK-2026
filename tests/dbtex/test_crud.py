from datetime import datetime, timedelta, timezone

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


def test_create_tex_file(db_session, test_user_id):
    _create_user(db_session, test_user_id)
    tex_file = crud.create_tex_file(
        db=db_session,
        user_id=test_user_id,
        filename="main.tex",
        latex="\\begin{document}Hello\\end{document}",
    )

    assert tex_file.id is not None
    assert tex_file.user_id == test_user_id
    assert tex_file.filename == "main.tex"
    assert tex_file.latex_content


def test_get_recent_tex_files_scoped_to_user(db_session, test_user_id):
    _create_user(db_session, test_user_id)
    _create_user(db_session, "other-user")

    first = crud.create_tex_file(
        db=db_session,
        user_id=test_user_id,
        filename="a.tex",
        latex="A",
    )
    second = crud.create_tex_file(
        db=db_session,
        user_id=test_user_id,
        filename="b.tex",
        latex="B",
    )
    crud.create_tex_file(
        db=db_session,
        user_id="other-user",
        filename="c.tex",
        latex="C",
    )

    first.created_at = datetime.now(timezone.utc) - timedelta(days=1)
    second.created_at = datetime.now(timezone.utc)
    db_session.commit()

    files = crud.get_recent_tex_files(db=db_session, user_id=test_user_id, limit=10)

    assert len(files) == 2
    assert [f.id for f in files] == [second.id, first.id]
    assert all(f.user_id == test_user_id for f in files)


def test_get_tex_file_by_id_enforces_ownership(db_session, test_user_id):
    _create_user(db_session, test_user_id)
    _create_user(db_session, "other-user")

    tex_file = crud.create_tex_file(
        db=db_session,
        user_id=test_user_id,
        filename="main.tex",
        latex="content",
    )

    owned = crud.get_tex_file_by_id(
        db=db_session,
        user_id=test_user_id,
        tex_id=tex_file.id,
    )
    assert owned is not None

    not_owned = crud.get_tex_file_by_id(
        db=db_session,
        user_id="other-user",
        tex_id=tex_file.id,
    )
    assert not_owned is None


def test_update_tex_file(db_session, test_user_id):
    _create_user(db_session, test_user_id)

    tex_file = crud.create_tex_file(
        db=db_session,
        user_id=test_user_id,
        filename="main.tex",
        latex="old",
    )

    updated = crud.update_tex_file(
        db=db_session,
        tex_file=tex_file,
        filename="updated.tex",
        latex="new",
    )

    assert updated.filename == "updated.tex"
    assert updated.latex_content == "new"
    assert updated.updated_at is not None


def test_delete_tex_file(db_session, test_user_id):
    _create_user(db_session, test_user_id)

    tex_file = crud.create_tex_file(
        db=db_session,
        user_id=test_user_id,
        filename="main.tex",
        latex="content",
    )

    crud.delete_tex_file(db=db_session, tex_file=tex_file)

    found = crud.get_tex_file_by_id(
        db=db_session,
        user_id=test_user_id,
        tex_id=tex_file.id,
    )
    assert found is None
