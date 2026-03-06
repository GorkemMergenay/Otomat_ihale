from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.collector_run import CollectorRun
from app.models.enums import ClassificationLabel, CollectorRunStatus
from app.models.source_config import SourceConfig
from app.models.tender import Tender
from app.services.tender_service import non_mock_tender_condition, upcoming_deadline_count


def get_overview(db: Session) -> dict[str, int]:
    today = date.today()
    day_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    last_24h = datetime.now(timezone.utc) - timedelta(hours=24)

    total_tenders = db.scalar(
        select(func.count()).select_from(Tender).where(non_mock_tender_condition())
    ) or 0
    newly_found_today = (
        db.scalar(
            select(func.count())
            .select_from(Tender)
            .where(non_mock_tender_condition())
            .where(Tender.created_at >= day_start)
        )
        or 0
    )
    highly_relevant_count = (
        db.scalar(
            select(func.count())
            .select_from(Tender)
            .where(non_mock_tender_condition())
            .where(Tender.classification_label == ClassificationLabel.HIGHLY_RELEVANT.value)
        )
        or 0
    )
    official_verified_count = (
        db.scalar(
            select(func.count())
            .select_from(Tender)
            .where(non_mock_tender_condition())
            .where(Tender.official_verified.is_(True))
        )
        or 0
    )
    active_sources = (
        db.scalar(select(func.count()).select_from(SourceConfig).where(SourceConfig.is_active.is_(True))) or 0
    )
    source_failures_last_24h = (
        db.scalar(
            select(func.count())
            .select_from(CollectorRun)
            .where(CollectorRun.status == CollectorRunStatus.FAILED.value)
            .where(CollectorRun.started_at >= last_24h)
        )
        or 0
    )

    return {
        "total_tenders": total_tenders,
        "newly_found_today": newly_found_today,
        "highly_relevant_count": highly_relevant_count,
        "approaching_deadlines": upcoming_deadline_count(db, today, within_days=7),
        "official_verified_count": official_verified_count,
        "active_sources": active_sources,
        "source_failures_last_24h": source_failures_last_24h,
    }
