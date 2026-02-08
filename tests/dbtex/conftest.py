import sys
import types
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.types import String, TypeDecorator

# Ensure src/backend is importable
ROOT = Path(__file__).resolve().parents[2]
SRC_BACKEND = ROOT / "src" / "backend"
if str(SRC_BACKEND) not in sys.path:
    sys.path.insert(0, str(SRC_BACKEND))

# Patch PostgreSQL UUID type to be SQLite-friendly for tests
from sqlalchemy.dialects import postgresql as pg


class CompatUUID(TypeDecorator):
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return str(value)
        if isinstance(value, str):
            return value
        raise ValueError("UUID value must be uuid.UUID or str")

    def process_result_value(self, value, dialect):
        return value


pg.UUID = CompatUUID

# Provide a Base for app.db.models without importing app.db.base
Base = declarative_base()
base_module = types.ModuleType("app.db.base")
base_module.Base = Base
sys.modules["app.db.base"] = base_module

# Provide app.deps for app.routes.tex import compatibility

def _placeholder_get_db():
    raise RuntimeError("get_db dependency should be overridden in tests")


class _PlaceholderUser:
    id = "mock-user-id"


def _placeholder_get_current_user():
    return _PlaceholderUser()


deps_module = types.ModuleType("app.deps")
deps_module.get_db = _placeholder_get_db
deps_module.get_current_user = _placeholder_get_current_user
sys.modules["app.deps"] = deps_module

from app.db import models
from app.main import app as fastapi_app


# Ensure timestamp fields are always set in tests
@event.listens_for(models.User, "before_insert")
def _set_user_created_at(_mapper, _connection, target):
    if target.created_at is None:
        target.created_at = datetime.now(timezone.utc)


@event.listens_for(models.TexFile, "before_insert")
def _set_tex_timestamps_on_insert(_mapper, _connection, target):
    now = datetime.now(timezone.utc)
    if target.created_at is None:
        target.created_at = now
    if target.updated_at is None:
        target.updated_at = now


@event.listens_for(models.TexFile, "before_update")
def _set_tex_updated_at(_mapper, _connection, target):
    target.updated_at = datetime.now(timezone.utc)


@pytest.fixture()
def db_engine():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture()
def db_session(db_engine):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture()
def test_user_id():
    return "mock-user-id"


@pytest.fixture()
def test_client(db_session, test_user_id):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_get_current_user():
        user = db_session.query(models.User).filter(models.User.id == test_user_id).first()
        if user:
            return user
        user = models.User(
            id=test_user_id,
            oauth_provider="test-provider",
            oauth_sub="test-sub",
            email="user@example.com",
            created_at=datetime.now(timezone.utc),
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    fastapi_app.dependency_overrides[deps_module.get_db] = override_get_db
    fastapi_app.dependency_overrides[deps_module.get_current_user] = override_get_current_user
    try:
        from fastapi.testclient import TestClient

        with TestClient(fastapi_app) as client:
            yield client
    finally:
        fastapi_app.dependency_overrides.clear()
