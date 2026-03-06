from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api_v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.db.session import SessionLocal
from app.services.data_hygiene_service import purge_mock_tenders
from app.workers.scheduler import start_scheduler, stop_scheduler

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.auto_purge_mock_data:
        db = SessionLocal()
        try:
            purged = purge_mock_tenders(db)
            if purged:
                logger.info("Mock kayıt temizliği uygulandı", extra={"purged_tenders": purged})
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


@app.get("/")
def root() -> dict[str, str]:
    return {"service": settings.app_name, "status": "çalışıyor"}
