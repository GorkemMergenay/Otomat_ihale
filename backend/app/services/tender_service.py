from __future__ import annotations

import enum
from datetime import date, datetime, timedelta, timezone
from typing import List, Optional, Tuple

from sqlalchemy import and_, asc, desc, func, or_, select, update
from sqlalchemy.orm import Session

from app.core.config import settings
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


def active_tender_condition(today: Optional[date] = None):
    """Sadece son tarihi geçmemiş ve arşivlenmemiş ihaleler."""
    if today is None:
        today = date.today()
    return and_(
        non_mock_tender_condition(),
        Tender.status != TenderStatus.ARCHIVED.value,
        or_(Tender.deadline_date.is_(None), Tender.deadline_date >= today),
    )


def list_tenders(db: Session, filters: TenderListFilters) -> Tuple[List[Tender], int]:
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

    if filters.active_only:
        today = date.today()
        query = query.where(Tender.status != TenderStatus.ARCHIVED.value).where(
            or_(Tender.deadline_date.is_(None), Tender.deadline_date >= today)
        )

    count_query = select(func.count()).select_from(query.subquery())
    total = db.scalar(count_query) or 0

    sort_col = SORTABLE_FIELDS.get(filters.sort_by, Tender.deadline_date)
    sort_clause = desc(sort_col) if filters.sort_order.lower() == "desc" else asc(sort_col)

    offset = (filters.page - 1) * filters.page_size
    items = db.scalars(query.order_by(sort_clause).offset(offset).limit(filters.page_size)).all()
    return items, total


def get_tender(db: Session, tender_id: int) -> Optional[Tender]:
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
            .where(active_tender_condition(today))
            .where(Tender.deadline_date.is_not(None))
            .where(Tender.deadline_date <= max_date)
        )
        or 0
    )


def archive_expired_tenders(db: Session) -> int:
    """
    Son tarihi geçmiş veya çok eski (tarihsiz) ihaleleri arşivler.
    - deadline_date < bugün -> arşivle
    - deadline_date yok, publishing_date < (bugün - archive_no_deadline_after_days) -> arşivle
    - deadline_date ve publishing_date yok, created_at çok eski -> arşivle
    """
    today = date.today()
    after_days = max(1, getattr(settings, "archive_no_deadline_after_days", 60))
    cutoff_date = today - timedelta(days=after_days)
    cutoff_dt = datetime(cutoff_date.year, cutoff_date.month, cutoff_date.day, 0, 0, 0, tzinfo=timezone.utc)

    # 1) Son tarihi geçmiş olanlar
    q1 = (
        update(Tender)
        .where(non_mock_tender_condition())
        .where(Tender.status != TenderStatus.ARCHIVED.value)
        .where(Tender.deadline_date.is_not(None))
        .where(Tender.deadline_date < today)
        .values(status=TenderStatus.ARCHIVED.value)
    )
    r1 = db.execute(q1)

    # 2) Son tarihi yok ama yayın tarihi çok eski
    q2 = (
        update(Tender)
        .where(non_mock_tender_condition())
        .where(Tender.status != TenderStatus.ARCHIVED.value)
        .where(Tender.deadline_date.is_(None))
        .where(Tender.publishing_date.is_not(None))
        .where(Tender.publishing_date < cutoff_date)
        .values(status=TenderStatus.ARCHIVED.value)
    )
    r2 = db.execute(q2)

    # 3) Ne son tarihi ne yayın tarihi var; kayıt tarihi çok eski
    q3 = (
        update(Tender)
        .where(non_mock_tender_condition())
        .where(Tender.status != TenderStatus.ARCHIVED.value)
        .where(Tender.deadline_date.is_(None))
        .where(Tender.publishing_date.is_(None))
        .where(Tender.created_at < cutoff_dt)
        .values(status=TenderStatus.ARCHIVED.value)
    )
    r3 = db.execute(q3)

    db.commit()
    return (r1.rowcount or 0) + (r2.rowcount or 0) + (r3.rowcount or 0)


def fill_missing_dates_from_text(db: Session) -> int:
    """
    Tarihi eksik ihalelerin raw_text/title/summary alanlarından tarih çıkarıp günceller.
    Güncellenen kayıt sayısını döner.
    """
    try:
        from collector.date_extract import extract_any_date_from_text, extract_deadline_from_text
    except ImportError:
        return 0

    tenders = db.scalars(
        select(Tender)
        .where(non_mock_tender_condition())
        .where(Tender.status != TenderStatus.ARCHIVED.value)
        .where(or_(Tender.deadline_date.is_(None), Tender.publishing_date.is_(None)))
    ).all()

    updated = 0
    for t in tenders:
        text = " ".join(filter(None, [t.title, t.summary, t.raw_text]))
        if not text.strip():
            continue
        changed = False
        if not t.deadline_date:
            deadline = extract_deadline_from_text(text)
            if deadline:
                t.deadline_date = deadline
                changed = True
        if not t.publishing_date:
            pub = extract_any_date_from_text(text)
            if pub:
                t.publishing_date = pub
                changed = True
        if changed:
            db.add(t)
            updated += 1
    if updated:
        db.commit()
    return updated
