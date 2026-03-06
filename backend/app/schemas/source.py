from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import SourceType


class SourceConfigBase(BaseModel):
    name: str
    source_type: SourceType
    base_url: str
    is_active: bool = True
    crawl_frequency: str = "0 */6 * * *"
    config_json: dict[str, Any] = Field(default_factory=dict)


class SourceConfigCreate(SourceConfigBase):
    pass


class SourceConfigUpdate(BaseModel):
    name: str | None = None
    base_url: str | None = None
    is_active: bool | None = None
    crawl_frequency: str | None = None
    config_json: dict[str, Any] | None = None


class SourceConfigRead(SourceConfigBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    last_run_at: datetime | None
    last_success_at: datetime | None
    last_failure_at: datetime | None
    last_error: str | None
    created_at: datetime
    updated_at: datetime
