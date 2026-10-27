"""Password hashing (Argon2id) and JWT helpers."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from app.core.config import get_settings

_hasher = PasswordHasher()  # Argon2id with the library's default parameters
_DUMMY_HASH = _hasher.hash("not-a-real-password")  # burns equal time for unknown emails


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str | None) -> bool:
    """Pass None for unknown users: a dummy hash is checked so timing does not reveal them."""
    try:
        ok = _hasher.verify(password_hash or _DUMMY_HASH, password)
    except (VerificationError, InvalidHashError):
        return False
    return ok and password_hash is not None


def create_access_token(user_id: str) -> tuple[str, datetime]:
    s = get_settings()
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=s.access_token_expire_minutes)
    payload = {"sub": user_id, "jti": uuid.uuid4().hex, "iat": now, "exp": expires}
    return jwt.encode(payload, s.jwt_secret_key, algorithm=s.jwt_algorithm), expires


def decode_access_token(token: str) -> dict:
    """Raises jwt.InvalidTokenError (including expiry) when the token is not valid."""
    s = get_settings()
    return jwt.decode(
        token, s.jwt_secret_key, algorithms=[s.jwt_algorithm], options={"require": ["exp", "sub", "jti"]}
    )
