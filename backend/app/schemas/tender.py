from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ClassificationLabel, SourceType, TenderStatus


class TenderDocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_type: Optional[str]
    document_url: str
    local_path: Optional[str]
    checksum: Optional[str]
    created_at: datetime


class TenderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    normalized_title: str
    source_type: SourceType
    source_name: str
    source_url: str
    external_id: Optional[str]
    publishing_date: Optional[date]
    deadline_date: Optional[date]
    tender_date: Optional[date]
    institution_name: Optional[str]
    city: Optional[str]
    region: Optional[str]
    tender_type: Optional[str]
    summary: Optional[str]
    raw_text: Optional[str]
    extracted_keywords: List[str]
    match_explanation: Dict[str, Any]
    relevance_score: float
    commercial_score: float
    technical_score: float
    total_score: float
    classification_label: ClassificationLabel
    official_verified: bool
    signal_found: bool
    status: TenderStatus
    assigned_to: Optional[int]
    notes: Optional[str]
    dedupe_key: str
    content_checksum: Optional[str]
    parser_version: Optional[str]
    last_scored_at: Optional[datetime]
    documents: List[TenderDocumentRead] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class TenderUpdate(BaseModel):
    status: Optional[TenderStatus] = None
    notes: Optional[str] = None
    assigned_to: Optional[int] = None
    official_verified: Optional[bool] = None


class TenderListFilters(BaseModel):
    search: Optional[str] = None
    city: Optional[str] = None
    institution_name: Optional[str] = None
    min_score: Optional[float] = Field(default=None, ge=0, le=100)
    source_name: Optional[str] = None
    status: Optional[TenderStatus] = None
    official_verified: Optional[bool] = None
    publish_date_from: Optional[date] = None
    publish_date_to: Optional[date] = None
    deadline_from: Optional[date] = None
    deadline_to: Optional[date] = None
    active_only: bool = Field(default=True, description="Sadece son tarihi geçmemiş ihaleler")
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: str = "total_score"
    sort_order: str = "desc"


class TenderEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tender_id: int
    event_type: str
    event_data: Dict[str, Any]
    created_at: datetime
