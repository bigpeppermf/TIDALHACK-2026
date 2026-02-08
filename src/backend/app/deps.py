import logging
import os
import uuid
from datetime import datetime

from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.auth.clerk import (
    ClerkAuthError,
    ClerkConfigError,
    ClerkIdentity,
    ClerkServiceError,
    authenticate_request,
)
from app.db.deps import get_db
from app.db.models import User

logger = logging.getLogger(__name__)


def _resolve_or_create_user(db: Session, identity: ClerkIdentity) -> User:
    user = (
        db.query(User)
        .filter(
            User.oauth_provider == "clerk",
            User.oauth_sub == identity.user_id,
        )
        .first()
    )
    if user:
        updated = False
        if identity.email and user.email != identity.email:
            user.email = identity.email
            updated = True
        if identity.full_name and user.full_name != identity.full_name:
            user.full_name = identity.full_name
            updated = True
        if identity.avatar_url and user.avatar_url != identity.avatar_url:
            user.avatar_url = identity.avatar_url
            updated = True
        if updated:
            db.commit()
            db.refresh(user)
        return user

    # Create user only after token validation to avoid trusting client input.
    user = User(
        oauth_provider="clerk",
        oauth_sub=identity.user_id,
        email=identity.email,
        full_name=identity.full_name,
        avatar_url=identity.avatar_url,
        created_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _dev_bypass_enabled() -> bool:
    return os.getenv("AUTH_DEV_BYPASS", "").lower() in {"1", "true", "yes"}


def _get_or_create_dev_user(db: Session) -> User:
    dev_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    user = db.query(User).filter(User.id == dev_id).first()
    if user:
        return user
    user = User(
        id=dev_id,
        oauth_provider="dev",
        oauth_sub="dev-user",
        email="dev@example.com",
        full_name="Dev User",
        avatar_url=None,
        created_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_current_user(
    request: Request,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if _dev_bypass_enabled():
        return _get_or_create_dev_user(db)

    headers = dict(request.headers)
    if authorization:
        headers["authorization"] = authorization

    try:
        identity = authenticate_request(
            method=request.method,
            url=str(request.url),
            headers=headers,
        )
    except ClerkAuthError:
        raise HTTPException(status_code=401, detail="Unauthorized")
    except ClerkConfigError as exc:
        logger.error("Auth configuration error: %s", exc)
        raise HTTPException(status_code=500, detail="Internal server error")
    except ClerkServiceError:
        raise HTTPException(status_code=502, detail="Clerk service error")
    except Exception:
        logger.error("Unexpected auth failure", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

    try:
        return _resolve_or_create_user(db, identity)
    except Exception:
        logger.error("User resolution failed", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
