from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.auth_tokens import decode_access_token
from app.core.config import settings
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User


bearer = HTTPBearer(auto_error=False)


@dataclass
class CurrentUser:
    id: Optional[int]
    email: str
    role: UserRole


TOKEN_ROLE_MAP = {
    settings.admin_token: UserRole.ADMIN,
    settings.analyst_token: UserRole.ANALYST,
    settings.viewer_token: UserRole.VIEWER,
}


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer),
    db: Session = Depends(get_db),
) -> CurrentUser:
    if settings.auth_disabled and credentials is None:
        return CurrentUser(id=None, email="dev-admin@local", role=UserRole.ADMIN)

    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Kimlik doğrulama belirteci eksik")

    token = credentials.credentials
    role = TOKEN_ROLE_MAP.get(token)
    if role is not None:
        return CurrentUser(id=None, email=f"{role.value}@local", role=role)

    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Geçersiz kimlik doğrulama belirteci")

    user = db.get(User, payload.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Kullanıcı bulunamadı veya pasif")

    try:
        user_role = UserRole(user.role)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Geçersiz kullanıcı rolü") from exc

    return CurrentUser(id=user.id, email=user.email, role=user_role)


def require_admin(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu işlem için yönetici rolü gerekir")
    return user
