from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import require_admin
from app.db.session import get_db
from app.services.collector_service import trigger_manual_crawl_for_all
from app.services.scoring_service import reprocess_all

router = APIRouter(prefix="/actions", tags=["actions"])


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
