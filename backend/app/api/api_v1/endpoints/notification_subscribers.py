from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_admin
from app.db.session import get_db
from app.models.notification_subscriber import NotificationSubscriber
from app.schemas.notification_subscriber import (
    NotificationSubscriberCreate,
    NotificationSubscriberRead,
    NotificationSubscriberUpdate,
)

router = APIRouter(prefix="/notification-subscribers", tags=["notification-subscribers"])


@router.get("", response_model=list[NotificationSubscriberRead])
def list_subscribers(
    _: object = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[NotificationSubscriberRead]:
    rows = db.scalars(
        select(NotificationSubscriber).order_by(NotificationSubscriber.created_at.desc())
    ).all()
    return [NotificationSubscriberRead.model_validate(r) for r in rows]


@router.post("", response_model=NotificationSubscriberRead, status_code=status.HTTP_201_CREATED)
def add_subscriber(
    payload: NotificationSubscriberCreate,
    _: object = Depends(require_admin),
    db: Session = Depends(get_db),
) -> NotificationSubscriberRead:
    email_normalized = payload.email.strip().lower()
    existing = db.scalar(
        select(NotificationSubscriber).where(
            NotificationSubscriber.email == email_normalized
        )
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bu e-posta adresi zaten kayıtlı.",
        )
    subscriber = NotificationSubscriber(
        email=email_normalized,
        label=payload.label.strip() if payload.label else None,
        is_active=True,
    )
    db.add(subscriber)
    db.commit()
    db.refresh(subscriber)
    return NotificationSubscriberRead.model_validate(subscriber)


@router.patch("/{subscriber_id}", response_model=NotificationSubscriberRead)
def update_subscriber(
  subscriber_id: int,
  payload: NotificationSubscriberUpdate,
  _: object = Depends(require_admin),
  db: Session = Depends(get_db),
) -> NotificationSubscriberRead:
    subscriber = db.get(NotificationSubscriber, subscriber_id)
    if not subscriber:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Abone bulunamadı.")
    if payload.is_active is not None:
        subscriber.is_active = payload.is_active
    if payload.label is not None:
        subscriber.label = payload.label.strip() or None
    db.add(subscriber)
    db.commit()
    db.refresh(subscriber)
    return NotificationSubscriberRead.model_validate(subscriber)


@router.delete("/{subscriber_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subscriber(
  subscriber_id: int,
  _: object = Depends(require_admin),
  db: Session = Depends(get_db),
) -> None:
    subscriber = db.get(NotificationSubscriber, subscriber_id)
    if not subscriber:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Abone bulunamadı.")
    db.delete(subscriber)
    db.commit()
