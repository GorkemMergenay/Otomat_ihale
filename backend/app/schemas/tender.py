from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ClassificationLabel, SourceType, TenderStatus


class TenderDocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_type: str | None
    document_url: str
    local_path: str | None
    checksum: str | None
    created_at: datetime


class TenderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    normalized_title: str
    source_type: SourceType
    source_name: str
    source_url: str
    external_id: str | None
    publishing_date: date | None
    deadline_date: date | None
    tender_date: date | None
    institution_name: str | None
    city: str | None
    region: str | None
    tender_type: str | None
    summary: str | None
    raw_text: str | None
    extracted_keywords: list[str]
    match_explanation: dict[str, Any]
    relevance_score: float
    commercial_score: float
    technical_score: float
    total_score: float
    classification_label: ClassificationLabel
    official_verified: bool
    signal_found: bool
    status: TenderStatus
    assigned_to: int | None
    notes: str | None
    dedupe_key: str
    content_checksum: str | None
    parser_version: str | None
    last_scored_at: datetime | None
    documents: list[TenderDocumentRead] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class TenderUpdate(BaseModel):
    status: TenderStatus | None = None
    notes: str | None = None
    assigned_to: int | None = None
    official_verified: bool | None = None


class TenderListFilters(BaseModel):
    search: str | None = None
    city: str | None = None
    institution_name: str | None = None
    min_score: float | None = Field(default=None, ge=0, le=100)
    source_name: str | None = None
    status: TenderStatus | None = None
    official_verified: bool | None = None
    publish_date_from: date | None = None
    publish_date_to: date | None = None
    deadline_from: date | None = None
    deadline_to: date | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: str = "deadline_date"
    sort_order: str = "asc"


class TenderEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tender_id: int
    event_type: str
    event_data: dict[str, Any]
    created_at: datetime
