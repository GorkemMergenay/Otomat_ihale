from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.enums import ClassificationLabel, SourceType, TenderStatus


class Tender(Base, TimestampMixin):
    __tablename__ = "tenders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    normalized_title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)

    source_type: Mapped[SourceType] = mapped_column(String(50), nullable=False, index=True)
    source_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    external_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)

    publishing_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    deadline_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    tender_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    institution_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    city: Mapped[Optional[str]] = mapped_column(String(120), nullable=True, index=True)
    region: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    tender_type: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)

    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    extracted_keywords: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    match_explanation: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    relevance_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    commercial_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    technical_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False, index=True)
    classification_label: Mapped[ClassificationLabel] = mapped_column(
        String(50), default=ClassificationLabel.IRRELEVANT.value, nullable=False, index=True
    )

    official_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    signal_found: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    status: Mapped[TenderStatus] = mapped_column(
        String(50), default=TenderStatus.NEW.value, nullable=False, index=True
    )

    assigned_to: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    dedupe_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    content_checksum: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    parser_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    last_scored_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    documents = relationship("TenderDocument", back_populates="tender", cascade="all, delete-orphan")
    events = relationship("TenderEvent", back_populates="tender", cascade="all, delete-orphan")


Index("ix_tender_dedupe_signature", Tender.normalized_title, Tender.institution_name, Tender.publishing_date)
