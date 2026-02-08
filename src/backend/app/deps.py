from datetime import datetime
from uuid import UUID

from app.db.deps import get_db
from app.db.models import User

_STABLE_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


def get_current_user() -> User:
    return User(
        id=_STABLE_USER_ID,
        oauth_provider="mock",
        oauth_sub="mock-user",
        email="mock-user@example.com",
        created_at=datetime(2026, 1, 1),
    )
