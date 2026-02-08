'''creates per-request resources

cleans them up automatically

keeps routes clean and declarative'''
from app.db.session import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
