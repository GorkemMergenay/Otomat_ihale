from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict

from app.models.enums import DeliveryStatus, NotificationChannel, NotificationType


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tender_id: Optional[int]
    channel: NotificationChannel
    recipient: str
    notification_type: NotificationType
    delivery_status: DeliveryStatus
    payload: dict
    idempotency_key: str
    error_message: Optional[str]
    created_at: datetime
