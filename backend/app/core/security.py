"""Password hashing and constrained JWT creation/validation."""

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import jwt
from pwdlib import PasswordHash

from app.core.config import Settings
from app.core.errors import unauthorized

_password_hasher = PasswordHash.recommended()
_algorithm = "HS256"


def hash_password(password: str) -> str:
    return _password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _password_hasher.verify(password, password_hash)


def create_token(*, subject: UUID, token_type: str, ttl_seconds: int, settings: Settings) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(subject),
        "typ": token_type,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": now,
        "exp": now + timedelta(seconds=ttl_seconds),
        "jti": str(uuid4()),
    }
    return jwt.encode(payload, settings.secret_key.get_secret_value(), algorithm=_algorithm)


def decode_token(*, encoded_token: str, expected_type: str, settings: Settings) -> UUID:
    try:
        payload = jwt.decode(
            encoded_token,
            settings.secret_key.get_secret_value(),
            algorithms=[_algorithm],
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
            options={"require": ["sub", "typ", "exp", "iat", "jti"]},
        )
        if payload["typ"] != expected_type:
            raise ValueError("Unexpected token type")
        return UUID(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError) as exc:
        raise unauthorized("Invalid or expired token") from exc
