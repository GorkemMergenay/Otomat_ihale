from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

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
    name: Optional[str] = None
    base_url: Optional[str] = None
    is_active: Optional[bool] = None
    crawl_frequency: Optional[str] = None
    config_json: Optional[dict] = None


class SourceConfigRead(SourceConfigBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    last_run_at: Optional[datetime]
    last_success_at: Optional[datetime]
    last_failure_at: Optional[datetime]
    last_error: Optional[str]
    created_at: datetime
    updated_at: datetime
