'''
defines:

tables

columns

relationships
'''



import uuid
from sqlalchemy import Column, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from .base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    oauth_provider = Column(
        Text,
        nullable=False
    )

    oauth_sub = Column(
        Text,
        nullable=False
    )

    email = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        TIMESTAMP,
        nullable=False
    )


class TexFile(Base):
    __tablename__ = "tex_files"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    filename = Column(
        Text,
        nullable=False
    )

    latex_content = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        TIMESTAMP,
        nullable=False
    )

    updated_at = Column(
        TIMESTAMP,
        nullable=False
    )
