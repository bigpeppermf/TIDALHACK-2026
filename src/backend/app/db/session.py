import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

# Default to SQLite if no PostgreSQL DATABASE_URL is provided
if not DATABASE_URL:
    _db_dir = Path(__file__).resolve().parents[3]  # src/backend level
    _db_path = _db_dir / "monogram.db"
    DATABASE_URL = f"sqlite:///{_db_path}"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    # SQLite needs check_same_thread=False for FastAPI's threaded model
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
