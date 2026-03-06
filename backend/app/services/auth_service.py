from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.auth_tokens import create_access_token
from app.core.passwords import verify_password
from app.models.enums import UserRole
from app.models.user import User


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    normalized_email = email.strip().lower()
    user = db.scalar(select(User).where(func.lower(User.email) == normalized_email))
    if user is None or not user.is_active:
        return None

    if not verify_password(password, user.password_hash):
        return None

    user.last_login_at = datetime.now(timezone.utc)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def issue_user_access_token(user: User) -> tuple[str, datetime]:
    role = UserRole(user.role)
    return create_access_token(user_id=user.id, email=user.email, role=role)
