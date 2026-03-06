from __future__ import annotations

import enum
from datetime import date, timedelta

from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.orm import Session

from app.models.enums import TenderStatus
from app.models.tender import Tender
from app.models.tender_event import TenderEvent
from notifier.service import NotificationManager
from app.schemas.tender import TenderListFilters, TenderUpdate


SORTABLE_FIELDS = {
    "deadline_date": Tender.deadline_date,
    "total_score": Tender.total_score,
    "publishing_date": Tender.publishing_date,
    "created_at": Tender.created_at,
}


def non_mock_tender_condition():
    return or_(Tender.parser_version.is_(None), ~Tender.parser_version.like("mock-%"))


def list_tenders(db: Session, filters: TenderListFilters) -> tuple[list[Tender], int]:
    query = select(Tender).where(non_mock_tender_condition())

    if filters.search:
        pattern = f"%{filters.search.lower()}%"
        query = query.where(
            or_(
                func.lower(Tender.title).like(pattern),
                func.lower(Tender.summary).like(pattern),
                func.lower(Tender.institution_name).like(pattern),
            )
        )

    if filters.city:
        query = query.where(Tender.city == filters.city)

    if filters.institution_name:
        query = query.where(Tender.institution_name.ilike(f"%{filters.institution_name}%"))

    if filters.min_score is not None:
        query = query.where(Tender.total_score >= filters.min_score)

    if filters.source_name:
        query = query.where(Tender.source_name == filters.source_name)

    if filters.status:
        query = query.where(Tender.status == filters.status.value)

    if filters.official_verified is not None:
        query = query.where(Tender.official_verified == filters.official_verified)

    if filters.publish_date_from:
        query = query.where(Tender.publishing_date >= filters.publish_date_from)

    if filters.publish_date_to:
        query = query.where(Tender.publishing_date <= filters.publish_date_to)

    if filters.deadline_from:
        query = query.where(Tender.deadline_date >= filters.deadline_from)

    if filters.deadline_to:
        query = query.where(Tender.deadline_date <= filters.deadline_to)

    count_query = select(func.count()).select_from(query.subquery())
    total = db.scalar(count_query) or 0

    sort_col = SORTABLE_FIELDS.get(filters.sort_by, Tender.deadline_date)
    sort_clause = desc(sort_col) if filters.sort_order.lower() == "desc" else asc(sort_col)

    offset = (filters.page - 1) * filters.page_size
    items = db.scalars(query.order_by(sort_clause).offset(offset).limit(filters.page_size)).all()
    return items, total


def get_tender(db: Session, tender_id: int) -> Tender | None:
    return db.scalar(
        select(Tender)
        .where(Tender.id == tender_id)
        .where(non_mock_tender_condition())
        .limit(1)
    )


def update_tender(db: Session, tender: Tender, payload: TenderUpdate) -> Tender:
    previous_status = tender.status
    previous_verified = tender.official_verified

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if isinstance(value, enum.Enum):
            value = value.value
        setattr(tender, field, value)

    db.add(tender)

    if payload.status and payload.status.value != previous_status:
        db.add(
            TenderEvent(
                tender_id=tender.id,
                event_type="status_changed",
                event_data={"from": previous_status, "to": payload.status.value},
            )
        )

    if payload.official_verified is not None and payload.official_verified != previous_verified:
        db.add(
            TenderEvent(
                tender_id=tender.id,
                event_type="official_verification_changed",
                event_data={"from": previous_verified, "to": payload.official_verified},
            )
        )

    db.commit()
    db.refresh(tender)

    if payload.official_verified is True and payload.official_verified != previous_verified:
        NotificationManager(db).notify_official_verified(tender)
    return tender


def set_status(db: Session, tender: Tender, status: TenderStatus, reason: str) -> Tender:
    tender.status = status.value
    db.add(tender)
    db.add(TenderEvent(tender_id=tender.id, event_type="status_changed", event_data={"to": status.value, "reason": reason}))
    db.commit()
    db.refresh(tender)
    return tender


def upcoming_deadline_count(db: Session, today: date, within_days: int = 7) -> int:
    max_date = today + timedelta(days=within_days)
    return (
        db.scalar(
            select(func.count())
            .select_from(Tender)
            .where(non_mock_tender_condition())
            .where(Tender.deadline_date.is_not(None))
            .where(Tender.deadline_date >= today)
            .where(Tender.deadline_date <= max_date)
        )
        or 0
    )
