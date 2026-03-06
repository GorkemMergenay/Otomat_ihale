from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.schemas.dashboard import DashboardOverview
from app.services.dashboard_service import get_overview

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview", response_model=DashboardOverview)
def dashboard_overview(
    _: object = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardOverview:
    return DashboardOverview(**get_overview(db))
