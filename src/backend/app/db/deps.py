'''creates per-request resources

cleans them up automatically

keeps routes clean and declarative'''
from app.db.session import SessionLocal

def get_db():
    if SessionLocal is None:
        raise RuntimeError(
            "DATABASE_URL is not set. Add it to your .env to use database features."
        )
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
