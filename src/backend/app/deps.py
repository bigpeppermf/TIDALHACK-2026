import logging
from datetime import datetime

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.auth.jwt import AuthConfigError, AuthError, ClerkClaims, validate_clerk_jwt
from app.db.deps import get_db
from app.db.models import User

logger = logging.getLogger(__name__)


def _resolve_or_create_user(db: Session, claims: ClerkClaims) -> User:
    user = (
        db.query(User)
        .filter(
            User.oauth_provider == "clerk",
            User.oauth_sub == claims.sub,
        )
        .first()
    )
    if user:
        # Keep email in sync when Clerk provides an updated value.
        if claims.email and user.email != claims.email:
            user.email = claims.email
            db.commit()
            db.refresh(user)
        return user

    # Create user only after token validation to avoid trusting client input.
    user = User(
        oauth_provider="clerk",
        oauth_sub=claims.sub,
        email=claims.email,
        created_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    try:
        claims = validate_clerk_jwt(authorization)
    except AuthError:
        raise HTTPException(status_code=401, detail="Unauthorized")
    except AuthConfigError as exc:
        logger.error("Auth configuration error: %s", exc)
        raise HTTPException(status_code=500, detail="Internal server error")
    except Exception:
        logger.error("Unexpected auth failure", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

    try:
        return _resolve_or_create_user(db, claims)
    except Exception:
        logger.error("User resolution failed", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
