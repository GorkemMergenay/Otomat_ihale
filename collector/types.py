from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any


@dataclass
class NormalizedTenderInput:
    title: str
    source_type: str
    source_name: str
    source_url: str
    external_id: str | None = None
    publishing_date: date | None = None
    deadline_date: date | None = None
    tender_date: date | None = None
    institution_name: str | None = None
    city: str | None = None
    region: str | None = None
    tender_type: str | None = None
    summary: str | None = None
    raw_text: str | None = None
    official_verified: bool = False
    signal_found: bool = True
    parser_version: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CollectorOutput:
    items: list[NormalizedTenderInput]
    parser_version: str
    raw_snapshot: str | None = None
