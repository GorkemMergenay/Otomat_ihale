from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.enums import DeliveryStatus, NotificationChannel, NotificationType


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tender_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tenders.id", ondelete="SET NULL"), nullable=True)
    channel: Mapped[NotificationChannel] = mapped_column(String(50), nullable=False, index=True)
    recipient: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    notification_type: Mapped[NotificationType] = mapped_column(String(80), nullable=False, index=True)
    delivery_status: Mapped[DeliveryStatus] = mapped_column(
        String(50), nullable=False, default=DeliveryStatus.PENDING.value, index=True
    )
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
