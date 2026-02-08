'''Creating and configuring the connection between FastAPI app and Postgres.'''

from sqlalchemy.orm import declarative_base

Base = declarative_base()
