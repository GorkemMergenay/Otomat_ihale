from __future__ import annotations

import logging
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import settings
from app.db.session import SessionLocal
from app.services.collector_service import trigger_manual_crawl_for_all
from app.services.tender_service import archive_expired_tenders
from notifier.service import NotificationManager

logger = logging.getLogger(__name__)

scheduler: Optional[BackgroundScheduler] = None


def run_scheduled_crawl() -> None:
    db = SessionLocal()
    try:
        archived = archive_expired_tenders(db)
        if archived:
            logger.info("Expired tenders archived", extra={"archived_count": archived})
        triggered = trigger_manual_crawl_for_all(db)
        deadline_notifications = NotificationManager(db).scan_deadline_notifications()
        logger.info("Scheduled crawl completed", extra={"triggered_sources": triggered})
        logger.info(
            "Deadline notification scan completed",
            extra={"sent_notifications": deadline_notifications},
        )
    except Exception:  # noqa: BLE001
        logger.exception("Scheduled crawl failed")
    finally:
        db.close()


def start_scheduler() -> None:
    global scheduler
    if not settings.scheduler_enabled:
        logger.info("Scheduler disabled by configuration")
        return

    if scheduler and scheduler.running:
        return

    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(
        run_scheduled_crawl,
        "interval",
        minutes=settings.scheduler_interval_minutes,
        id="scheduled-crawl",
        max_instances=1,
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started", extra={"interval_minutes": settings.scheduler_interval_minutes})


def stop_scheduler() -> None:
    global scheduler
    if scheduler and scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
