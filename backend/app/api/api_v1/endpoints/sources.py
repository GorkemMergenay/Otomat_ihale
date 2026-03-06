from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_admin
from app.db.session import get_db
from app.models.source_config import SourceConfig
from app.schemas.source import SourceConfigCreate, SourceConfigRead, SourceConfigUpdate
from app.services.collector_service import trigger_manual_crawl_for_source

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("", response_model=list[SourceConfigRead])
def list_sources(
    _: object = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[SourceConfigRead]:
    rows = db.scalars(select(SourceConfig).order_by(SourceConfig.name.asc())).all()
    return [SourceConfigRead.model_validate(row) for row in rows]


@router.post("", response_model=SourceConfigRead, status_code=status.HTTP_201_CREATED)
def create_source(
    payload: SourceConfigCreate,
    _: object = Depends(require_admin),
    db: Session = Depends(get_db),
) -> SourceConfigRead:
    row = SourceConfig(**payload.model_dump(mode="json"))
    db.add(row)
    db.commit()
    db.refresh(row)
    return SourceConfigRead.model_validate(row)


@router.patch("/{source_id}", response_model=SourceConfigRead)
def update_source(
    source_id: int,
    payload: SourceConfigUpdate,
    _: object = Depends(require_admin),
    db: Session = Depends(get_db),
) -> SourceConfigRead:
    row = db.get(SourceConfig, source_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kaynak bulunamadı")

    for key, value in payload.model_dump(exclude_unset=True, mode="json").items():
        setattr(row, key, value)

    db.add(row)
    db.commit()
    db.refresh(row)
    return SourceConfigRead.model_validate(row)


@router.delete("/{source_id}", status_code=status.HTTP_200_OK)
def delete_source(
    source_id: int,
    _: object = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    row = db.get(SourceConfig, source_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kaynak bulunamadı")
    db.delete(row)
    db.commit()
    return {"status": "deleted"}


@router.post("/{source_id}/trigger-crawl")
def trigger_source_crawl(
    source_id: int,
    _: object = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    row = db.get(SourceConfig, source_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kaynak bulunamadı")

    trigger_manual_crawl_for_source(db, row)
    return {"status": "triggered", "source": row.name}
