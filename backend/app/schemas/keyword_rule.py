from __future__ import annotations

from datetime import datetime
from typing import Optional

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
    keyword: Optional[str] = None
    category: Optional[str] = None
    weight: Optional[float] = None
    is_active: Optional[bool] = None
    is_negative: Optional[bool] = None
    matching_type: Optional[MatchingType] = None
    target_field: Optional[str] = None


class KeywordRuleRead(KeywordRuleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
