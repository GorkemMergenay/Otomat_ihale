from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class NotificationSubscriberRead(BaseModel):
    id: int
    email: str
    label: str | None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationSubscriberCreate(BaseModel):
    email: EmailStr
    label: str | None = Field(default=None, max_length=100)


class NotificationSubscriberUpdate(BaseModel):
    is_active: bool | None = None
    label: str | None = Field(default=None, max_length=100)
