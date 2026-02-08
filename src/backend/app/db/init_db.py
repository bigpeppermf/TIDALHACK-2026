from app.db.base import Base
from app.db.session import engine
from app.db import models  # noqa: F401  # Ensure models are registered


def init_db() -> None:
    if engine is None:
        return
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
