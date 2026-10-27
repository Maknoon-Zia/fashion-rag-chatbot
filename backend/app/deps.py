"""FastAPI dependencies: bearer-token authentication."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import decode_access_token
from app.services import auth_service

_bearer = HTTPBearer(auto_error=False)
_UNAUTHORIZED = {"WWW-Authenticate": "Bearer"}


@dataclass
class AuthContext:
    user: dict[str, Any]
    claims: dict[str, Any]


def require_auth(creds: HTTPAuthorizationCredentials | None = Depends(_bearer)) -> AuthContext:
    if creds is None or creds.scheme.lower() != "bearer":
        raise HTTPException(401, "Please sign in to continue.", headers=_UNAUTHORIZED)
    try:
        claims = decode_access_token(creds.credentials)
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Your session has expired. Please sign in again.", headers=_UNAUTHORIZED) from None
    if auth_service.is_revoked(claims["jti"]):
        raise HTTPException(401, "Your session has ended. Please sign in again.", headers=_UNAUTHORIZED)
    user = auth_service.get_user(claims["sub"])
    if user is None:
        raise HTTPException(401, "Account not found. Please sign in again.", headers=_UNAUTHORIZED)
    return AuthContext(user=user, claims=claims)


def require_user(auth: AuthContext = Depends(require_auth)) -> dict[str, Any]:
    return auth.user
