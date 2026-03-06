from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.source_config import SourceConfig
from collector.runner import CollectorRunner


def trigger_manual_crawl_for_source(db: Session, source: SourceConfig) -> int:
    runner = CollectorRunner(db)
    return runner.run_source(source)


def trigger_manual_crawl_for_all(db: Session) -> int:
    sources = db.scalars(select(SourceConfig).where(SourceConfig.is_active.is_(True))).all()
    runner = CollectorRunner(db)
    for source in sources:
        runner.run_source(source)
    return len(sources)
