from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api_v1.endpoints import auth as auth_endpoints
from app.api.api_v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.db.session import SessionLocal
from app.services.data_hygiene_service import purge_mock_tenders
from app.services.tender_service import (
    archive_expired_tenders,
    delete_tenders_past_tender_date,
    fill_missing_dates_from_text,
)
from app.workers.scheduler import start_scheduler, stop_scheduler

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    db = SessionLocal()
    try:
        if settings.auto_purge_mock_data:
            purged = purge_mock_tenders(db)
            if purged:
                logger.info("Mock kayıt temizliği uygulandı", extra={"purged_tenders": purged})
        filled = fill_missing_dates_from_text(db)
        if filled:
            logger.info("Eksik ihale tarihleri metinden dolduruldu", extra={"updated_count": filled})
        archived = archive_expired_tenders(db)
        if archived:
            logger.info("Başlangıçta tarihi geçmiş ihaleler arşivlendi", extra={"archived_count": archived})
        deleted = delete_tenders_past_tender_date(db)
        if deleted:
            logger.info("İhale günü geçen kayıtlar silindi", extra={"deleted_count": deleted})
    finally:
        db.close()

    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

api_prefixes = [settings.api_v1_prefix]
for fallback_prefix in ("/api/v1", "/api"):
    if fallback_prefix not in api_prefixes:
        api_prefixes.append(fallback_prefix)

for prefix in api_prefixes:
    app.include_router(api_router, prefix=prefix)

# Login'in kesin bulunması için auth router'ı doğrudan da mount et (prefix olmadan: POST /auth/login)
app.include_router(auth_endpoints.router, prefix="/api/v1")
app.include_router(auth_endpoints.router, prefix="/api")
app.include_router(auth_endpoints.router)  # POST http://localhost:8000/auth/login


@app.get("/")
def root() -> dict[str, str]:
    return {"service": settings.app_name, "status": "çalışıyor"}
