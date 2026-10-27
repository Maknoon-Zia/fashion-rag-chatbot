"""User registration, login and token revocation (MongoDB is the source of truth)."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from app.core.errors import AppError
from app.core.security import create_access_token, hash_password, verify_password
from app.db.mongo import get_db
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserPublic


def to_user_public(doc: dict[str, Any]) -> UserPublic:
    return UserPublic(id=str(doc["_id"]), name=doc["name"], email=doc["email"], created_at=doc["created_at"])


def register_user(data: RegisterRequest) -> UserPublic:
    users = get_db().users
    if users.find_one({"email": data.email}, {"_id": 1}):
        raise AppError(409, "email_taken", "An account with this email already exists.")
    now = datetime.now(timezone.utc)
    doc = {
        "name": data.name, "email": data.email, "password_hash": hash_password(data.password),
        "created_at": now, "updated_at": now,
    }
    try:
        doc["_id"] = users.insert_one(doc).inserted_id
    except DuplicateKeyError as exc:  # race with another request: the unique index is the real guard
        raise AppError(409, "email_taken", "An account with this email already exists.") from exc
    return to_user_public(doc)


def login_user(data: LoginRequest) -> TokenResponse:
    doc = get_db().users.find_one({"email": data.email})
    if not verify_password(data.password, doc["password_hash"] if doc else None):
        raise AppError(401, "invalid_credentials", "Incorrect email or password.")
    token, expires_at = create_access_token(str(doc["_id"]))
    return TokenResponse(access_token=token, expires_at=expires_at, user=to_user_public(doc))


def get_user(user_id: str) -> dict[str, Any] | None:
    try:
        return get_db().users.find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None


def revoke_token(jti: str, expires_at: datetime) -> None:
    """Logout: remember the token id until it would have expired anyway (TTL index cleans up)."""
    try:
        get_db().revoked_tokens.insert_one({"jti": jti, "expires_at": expires_at})
    except DuplicateKeyError:
        pass


def is_revoked(jti: str) -> bool:
    return get_db().revoked_tokens.find_one({"jti": jti}, {"_id": 1}) is not None
