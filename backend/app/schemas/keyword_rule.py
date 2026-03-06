from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import MatchingType


class KeywordRuleBase(BaseModel):
    keyword: str
    category: str
    weight: float
    is_active: bool = True
    is_negative: bool = False
    matching_type: MatchingType = MatchingType.CONTAINS
    target_field: str = "any"


class KeywordRuleCreate(KeywordRuleBase):
    pass


class KeywordRuleUpdate(BaseModel):
    keyword: str | None = None
    category: str | None = None
    weight: float | None = None
    is_active: bool | None = None
    is_negative: bool | None = None
    matching_type: MatchingType | None = None
    target_field: str | None = None


class KeywordRuleRead(KeywordRuleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
