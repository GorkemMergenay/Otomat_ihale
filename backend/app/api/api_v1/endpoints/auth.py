from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import AuthenticatedUser, LoginRequest, LoginResponse, MeResponse
from app.services.auth_service import authenticate_user, issue_user_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    user = authenticate_user(db, email=payload.email, password=payload.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-posta veya şifre hatalı")

    token, expires_at = issue_user_access_token(user)
    return LoginResponse(access_token=token, expires_at=expires_at, user=AuthenticatedUser.model_validate(user))


@router.get("/me", response_model=MeResponse)
def me(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MeResponse:
    if current_user.id is None:
        pseudo = AuthenticatedUser(
            id=0,
            name="Sistem Kullanıcısı",
            email=current_user.email,
            role=current_user.role,
            is_active=True,
        )
        return MeResponse(user=pseudo)

    user = db.get(User, current_user.id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kullanıcı kaydı bulunamadı")
    return MeResponse(user=AuthenticatedUser.model_validate(user))
