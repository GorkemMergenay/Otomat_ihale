from __future__ import annotations

import enum


class SourceType(str, enum.Enum):
    OFFICIAL = "official"
    PUBLIC_ANNOUNCEMENT = "public_announcement"
    NEWS = "news"
    INSTITUTION = "institution"


class TenderStatus(str, enum.Enum):
    NEW = "new"
    AUTO_FLAGGED = "auto_flagged"
    UNDER_REVIEW = "under_review"
    RELEVANT = "relevant"
    HIGH_PRIORITY = "high_priority"
    PROPOSAL_CANDIDATE = "proposal_candidate"
    IGNORED = "ignored"
    ARCHIVED = "archived"


class ClassificationLabel(str, enum.Enum):
    HIGHLY_RELEVANT = "highly_relevant"
    RELEVANT = "relevant"
    MAYBE_RELEVANT = "maybe_relevant"
    IRRELEVANT = "irrelevant"


class MatchingType(str, enum.Enum):
    EXACT = "exact"
    CONTAINS = "contains"
    FUZZY = "fuzzy"


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


class NotificationChannel(str, enum.Enum):
    EMAIL = "email"
    TELEGRAM = "telegram"


class NotificationType(str, enum.Enum):
    NEW_HIGHLY_RELEVANT = "new_highly_relevant"
    OFFICIAL_VERIFIED = "official_verified"
    DEADLINE_APPROACHING = "deadline_approaching"
    SCORE_THRESHOLD = "score_threshold"


class DeliveryStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    SKIPPED = "skipped"


class CollectorRunStatus(str, enum.Enum):
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
