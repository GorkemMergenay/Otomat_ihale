from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import require_admin
from app.db.session import get_db
from app.services.collector_service import trigger_manual_crawl_for_all
from app.services.scoring_service import reprocess_all
from app.services.tender_service import (
    archive_expired_tenders,
    delete_tenders_past_tender_date,
    fill_missing_dates_from_text,
)

router = APIRouter(prefix="/actions", tags=["actions"])


@router.post("/archive-expired")
def archive_expired(
    _: object = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, int]:
    """Son tarihi geçmiş ihaleleri arşivler."""
    count = archive_expired_tenders(db)
    return {"archived_count": count}


@router.post("/delete-past-tender-date")
def delete_past_tender_date(
    _: object = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, int]:
    """İhale günü (tender_date) geçmiş kayıtları veritabanından siler."""
    count = delete_tenders_past_tender_date(db)
    return {"deleted_count": count}


@router.post("/fill-missing-dates")
def fill_missing_dates(
    _: object = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, int]:
    """Tarihi eksik ihalelerin metninden yayın/son tarih çıkarıp günceller."""
    count = fill_missing_dates_from_text(db)
    return {"updated_count": count}


@router.post("/manual-crawl")
def manual_crawl(
    _: object = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, int]:
    processed = trigger_manual_crawl_for_all(db)
    return {"triggered_sources": processed}


@router.post("/reprocess")
def manual_reprocess(
    _: object = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, int]:
    processed = reprocess_all(db)
    return {"reprocessed_tenders": processed}
