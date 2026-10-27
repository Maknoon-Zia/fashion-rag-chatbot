from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Response, status

from app.deps import AuthContext, require_auth, require_user
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserPublic
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest) -> UserPublic:
    return auth_service.register_user(data)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest) -> TokenResponse:
    return auth_service.login_user(data)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(auth: AuthContext = Depends(require_auth)) -> Response:
    expires = datetime.fromtimestamp(auth.claims["exp"], tz=timezone.utc)
    auth_service.revoke_token(auth.claims["jti"], expires)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserPublic)
def me(user: dict[str, Any] = Depends(require_user)) -> UserPublic:
    return auth_service.to_user_public(user)
