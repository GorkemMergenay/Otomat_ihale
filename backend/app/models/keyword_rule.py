from __future__ import annotations

from sqlalchemy import Boolean, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin
from app.models.enums import MatchingType


class KeywordRule(Base, TimestampMixin):
    __tablename__ = "keyword_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    keyword: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    is_negative: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    matching_type: Mapped[MatchingType] = mapped_column(
        String(50), nullable=False, default=MatchingType.CONTAINS.value
    )
    target_field: Mapped[str] = mapped_column(String(50), nullable=False, default="any")
