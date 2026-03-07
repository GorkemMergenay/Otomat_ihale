from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_admin, require_analyst
from app.db.session import get_db
from app.models.enums import TenderStatus
from app.models.tender_event import TenderEvent
from app.schemas.common import Page
from app.schemas.tender import TenderEventRead, TenderListFilters, TenderRead, TenderUpdate
from app.services.scoring_service import rescore_tender
from app.services.tender_service import get_tender, list_tenders, update_tender

router = APIRouter(prefix="/tenders", tags=["tenders"])


@router.get("", response_model=Page[TenderRead])
def get_tenders(
    search: Optional[str] = None,
    city: Optional[str] = None,
    institution_name: Optional[str] = None,
    min_score: Optional[float] = Query(default=None, ge=0, le=100),
    source_name: Optional[str] = None,
    tender_status: Optional[TenderStatus] = Query(default=None, alias="status"),
    official_verified: Optional[bool] = None,
    publish_date_from: Optional[date] = None,
    publish_date_to: Optional[date] = None,
    deadline_from: Optional[date] = None,
    deadline_to: Optional[date] = None,
    active_only: bool = Query(default=True, description="Sadece geçerli (son tarihi geçmemiş) ihaleler"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    sort_by: str = Query(default="total_score", description="Sıralama: total_score, deadline_date, publishing_date"),
    sort_order: str = Query(default="desc", description="desc = en alakalı/geç önce"),
    _: object = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Page[TenderRead]:
    filters = TenderListFilters(
        search=search,
        city=city,
        institution_name=institution_name,
        min_score=min_score,
        source_name=source_name,
        status=tender_status,
        official_verified=official_verified,
        publish_date_from=publish_date_from,
        publish_date_to=publish_date_to,
        deadline_from=deadline_from,
        deadline_to=deadline_to,
        active_only=active_only,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    tenders, total = list_tenders(db, filters)
    return Page[TenderRead](items=[TenderRead.model_validate(t) for t in tenders], total=total, page=page, page_size=page_size)


@router.get("/{tender_id}", response_model=TenderRead)
def get_tender_detail(
    tender_id: int,
    _: object = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TenderRead:
    tender = get_tender(db, tender_id)
    if not tender:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="İhale kaydı bulunamadı")
    return TenderRead.model_validate(tender)


@router.get("/{tender_id}/events", response_model=list[TenderEventRead])
def get_tender_events(
    tender_id: int,
    _: object = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[TenderEventRead]:
    events = db.scalars(
        select(TenderEvent).where(TenderEvent.tender_id == tender_id).order_by(TenderEvent.created_at.desc())
    ).all()
    return [TenderEventRead.model_validate(event) for event in events]


@router.patch("/{tender_id}", response_model=TenderRead)
def patch_tender(
    tender_id: int,
    payload: TenderUpdate,
    _: object = Depends(require_analyst),
    db: Session = Depends(get_db),
) -> TenderRead:
    tender = get_tender(db, tender_id)
    if not tender:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="İhale kaydı bulunamadı")

    tender = update_tender(db, tender, payload)
    return TenderRead.model_validate(tender)


@router.post("/{tender_id}/reprocess", response_model=TenderRead)
def reprocess_tender(
    tender_id: int,
    _: object = Depends(require_admin),
    db: Session = Depends(get_db),
) -> TenderRead:
    tender = get_tender(db, tender_id)
    if not tender:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="İhale kaydı bulunamadı")

    rescore_tender(db, tender)
    return TenderRead.model_validate(tender)
