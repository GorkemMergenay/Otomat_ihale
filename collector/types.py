from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, List, Optional


@dataclass
class NormalizedTenderInput:
    title: str
    source_type: str
    source_name: str
    source_url: str
    external_id: Optional[str] = None
    publishing_date: Optional[date] = None
    deadline_date: Optional[date] = None
    tender_date: Optional[date] = None
    institution_name: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    tender_type: Optional[str] = None
    summary: Optional[str] = None
    raw_text: Optional[str] = None
    official_verified: bool = False
    signal_found: bool = True
    parser_version: Optional[str] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class CollectorOutput:
    items: List[NormalizedTenderInput]
    parser_version: str
    raw_snapshot: Optional[str] = None
