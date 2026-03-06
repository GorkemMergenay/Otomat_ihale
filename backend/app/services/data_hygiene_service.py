from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.tender import Tender
from app.models.tender_document import TenderDocument
from app.models.tender_event import TenderEvent


def purge_mock_tenders(db: Session) -> int:
    try:
        mock_ids = db.scalars(select(Tender.id).where(Tender.parser_version.like("mock-%"))).all()
    except (OperationalError, ProgrammingError):
        db.rollback()
        return 0
    if not mock_ids:
        return 0

    db.execute(delete(TenderEvent).where(TenderEvent.tender_id.in_(mock_ids)))
    db.execute(delete(TenderDocument).where(TenderDocument.tender_id.in_(mock_ids)))
    db.execute(delete(Notification).where(Notification.tender_id.in_(mock_ids)))
    db.execute(delete(Tender).where(Tender.id.in_(mock_ids)))
    db.commit()
    return len(mock_ids)
