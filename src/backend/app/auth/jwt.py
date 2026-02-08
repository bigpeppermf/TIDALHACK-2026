import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional
from urllib.request import Request, urlopen

try:
    import jwt
except Exception as exc:  # pragma: no cover - import error handled at runtime
    jwt = None
    _JWT_IMPORT_ERROR = exc


class AuthError(Exception):
    """Raised for auth failures that should return HTTP 401."""


class AuthConfigError(Exception):
    """Raised for missing or invalid auth configuration."""


@dataclass(frozen=True)
class ClerkClaims:
    sub: str
    iss: str
    email: Optional[str]


_JWKS_CACHE: Dict[str, Any] = {"fetched_at": 0.0, "jwks": None}
_JWKS_TTL_SECONDS = 300


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise AuthConfigError(f"{name} is not set")
    return value


def _normalize_issuer(issuer: str) -> str:
    return issuer.rstrip("/")


def _get_jwks_url(issuer: str) -> str:
    # Allow overriding for self-hosted proxies or test setups.
    return os.getenv("CLERK_JWKS_URL") or f"{issuer}/.well-known/jwks.json"


def _fetch_jwks(jwks_url: str) -> Dict[str, Any]:
    now = time.time()
    cached = _JWKS_CACHE.get("jwks")
    fetched_at = _JWKS_CACHE.get("fetched_at", 0.0)
    # Cache JWKS to avoid refetching on every request.
    if cached and now - fetched_at < _JWKS_TTL_SECONDS:
        return cached

    req = Request(jwks_url, headers={"User-Agent": "monogram-backend"})
    with urlopen(req, timeout=5) as resp:
        payload = resp.read().decode("utf-8")
    jwks = json.loads(payload)
    _JWKS_CACHE["jwks"] = jwks
    _JWKS_CACHE["fetched_at"] = now
    return jwks


def _get_public_key(jwks: Dict[str, Any], kid: str):
    if jwt is None:
        raise AuthConfigError("PyJWT is not installed") from _JWT_IMPORT_ERROR

    keys = jwks.get("keys") or []
    for key in keys:
        if key.get("kid") == kid:
            return jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
    raise AuthError("Unknown key id")


def _get_bearer_token(authorization: Optional[str]) -> str:
    if not authorization:
        raise AuthError("Missing Authorization header")
    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1].strip():
        raise AuthError("Invalid Authorization header")
    return parts[1].strip()


def validate_clerk_jwt(authorization: Optional[str]) -> ClerkClaims:
    """
    Validate a Clerk session JWT and return essential claims.

    We enforce issuer + audience from env to avoid trusting token-provided values.
    """
    if jwt is None:
        raise AuthConfigError("PyJWT is not installed") from _JWT_IMPORT_ERROR

    token = _get_bearer_token(authorization)
    issuer = _normalize_issuer(_require_env("CLERK_ISSUER"))
    audience = _require_env("CLERK_AUDIENCE")

    try:
        unverified_header = jwt.get_unverified_header(token)
    except Exception as exc:
        raise AuthError("Invalid JWT header") from exc

    kid = unverified_header.get("kid")
    if not kid:
        raise AuthError("Missing key id in token header")

    jwks_url = _get_jwks_url(issuer)
    jwks = _fetch_jwks(jwks_url)
    public_key = _get_public_key(jwks, kid)

    try:
        # Signature, exp, aud, and iss are validated by PyJWT.
        claims = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=audience,
            issuer=issuer,
        )
    except jwt.ExpiredSignatureError as exc:
        raise AuthError("Token expired") from exc
    except jwt.InvalidIssuerError as exc:
        raise AuthError("Invalid token issuer") from exc
    except jwt.InvalidAudienceError as exc:
        raise AuthError("Invalid token audience") from exc
    except jwt.PyJWTError as exc:
        raise AuthError("Invalid token") from exc

    sub = claims.get("sub")
    iss = claims.get("iss")
    if not sub or not iss:
        raise AuthError("Missing required claims")

    email = claims.get("email")
    return ClerkClaims(sub=sub, iss=iss, email=email)
