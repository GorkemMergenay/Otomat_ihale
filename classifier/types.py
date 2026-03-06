from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MatchHit:
    keyword: str
    category: str
    weight: float
    is_negative: bool
    target_field: str
    matched_field: str
    matching_type: str
    match_score: float
    contribution: float


@dataclass
class ClassificationResult:
    relevance_score: float
    commercial_score: float
    technical_score: float
    total_score: float
    classification_label: str
    extracted_keywords: list[str] = field(default_factory=list)
    match_explanation: dict[str, Any] = field(default_factory=dict)
