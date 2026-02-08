import logging
import os
from dataclasses import dataclass
from typing import Any, Iterable, Optional

import httpx
from clerk_backend_api import Clerk

try:
    from clerk_backend_api.jwks_helpers import AuthenticateRequestOptions
except Exception:  # pragma: no cover - fall back for older SDKs
    from clerk_backend_api.security.types import AuthenticateRequestOptions


logger = logging.getLogger(__name__)


class ClerkAuthError(Exception):
    """Raised for auth failures that should return HTTP 401."""


class ClerkConfigError(Exception):
    """Raised when required Clerk configuration is missing."""


class ClerkServiceError(Exception):
    """Raised when Clerk API calls fail."""


@dataclass(frozen=True)
class ClerkIdentity:
    user_id: str
    email: Optional[str]
    full_name: Optional[str]
    avatar_url: Optional[str]


_CLERK_CLIENT: Clerk | None = None


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ClerkConfigError(f"{name} is not set")
    return value


def _get_clerk_client() -> Clerk:
    global _CLERK_CLIENT
    if _CLERK_CLIENT is None:
        secret_key = _require_env("CLERK_SECRET_KEY")
        _CLERK_CLIENT = Clerk(bearer_auth=secret_key)
    return _CLERK_CLIENT


def _get_attr(obj: Any, *names: str) -> Optional[Any]:
    if obj is None:
        return None
    for name in names:
        if isinstance(obj, dict) and name in obj:
            return obj.get(name)
        if hasattr(obj, name):
            value = getattr(obj, name)
            if value is not None:
                return value
    return None


def _extract_primary_email(user: Any) -> Optional[str]:
    primary_id = _get_attr(user, "primary_email_address_id", "primaryEmailAddressId")
    email_addresses = _get_attr(user, "email_addresses", "emailAddresses")
    if not email_addresses:
        return None
    try:
        for entry in email_addresses:
            entry_id = _get_attr(entry, "id", "id")
            if primary_id and entry_id == primary_id:
                return _get_attr(entry, "email_address", "emailAddress")
        # Fallback to the first address if primary isn't found.
        return _get_attr(email_addresses[0], "email_address", "emailAddress")
    except Exception:
        return None


def _extract_full_name(user: Any) -> Optional[str]:
    full_name = _get_attr(user, "full_name", "fullName")
    if full_name:
        return full_name
    first_name = _get_attr(user, "first_name", "firstName")
    last_name = _get_attr(user, "last_name", "lastName")
    if first_name or last_name:
        return " ".join(part for part in [first_name, last_name] if part)
    return None


def _build_request(method: str, url: str, headers: dict[str, str]) -> httpx.Request:
    # Clerk expects a request object with headers, including Authorization.
    return httpx.Request(method=method, url=url, headers=headers)


def authenticate_request(method: str, url: str, headers: dict[str, str]) -> ClerkIdentity:
    if "authorization" not in {k.lower() for k in headers.keys()}:
        raise ClerkAuthError("Missing Authorization header")

    clerk = _get_clerk_client()
    audience = _require_env("CLERK_AUDIENCE")
    issuer = _require_env("CLERK_ISSUER")

    httpx_request = _build_request(method, url, headers)

    try:
        options = AuthenticateRequestOptions(audience=[audience])
        request_state = clerk.authenticate_request(httpx_request, options=options)
    except Exception as exc:
        logger.error("Clerk request authentication failed", exc_info=True)
        raise ClerkServiceError("Clerk authentication failed") from exc

    is_signed_in = _get_attr(request_state, "is_signed_in", "isSignedIn")
    if not is_signed_in:
        raise ClerkAuthError("Invalid or expired session token")

    payload = _get_attr(request_state, "payload") or {}
    user_id = payload.get("sub") or payload.get("user_id")
    token_issuer = payload.get("iss")
    if not user_id:
        raise ClerkAuthError("Missing subject in token payload")
    if token_issuer and token_issuer.rstrip("/") != issuer.rstrip("/"):
        raise ClerkAuthError("Invalid token issuer")

    try:
        user = clerk.users.get(user_id=user_id)
    except Exception as exc:
        logger.error("Clerk user lookup failed", exc_info=True)
        raise ClerkServiceError("Clerk user lookup failed") from exc

    email = _extract_primary_email(user)
    full_name = _extract_full_name(user)
    avatar_url = _get_attr(user, "image_url", "imageUrl")

    return ClerkIdentity(
        user_id=user_id,
        email=email,
        full_name=full_name,
        avatar_url=avatar_url,
    )
