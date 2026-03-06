from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.models.enums import DeliveryStatus, NotificationChannel, NotificationType


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tender_id: int | None
    channel: NotificationChannel
    recipient: str
    notification_type: NotificationType
    delivery_status: DeliveryStatus
    payload: dict[str, Any]
    idempotency_key: str
    error_message: str | None
    created_at: datetime
