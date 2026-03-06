from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.notification import Notification
from app.schemas.notification import NotificationRead

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationRead])
def list_notifications(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _: object = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[NotificationRead]:
    offset = (page - 1) * page_size
    rows = db.scalars(
        select(Notification).order_by(Notification.created_at.desc()).offset(offset).limit(page_size)
    ).all()
    return [NotificationRead.model_validate(row) for row in rows]
