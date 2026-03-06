from __future__ import annotations

import logging
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models.collector_run import CollectorRun
from app.models.enums import CollectorRunStatus, TenderStatus
from app.models.source_config import SourceConfig
from app.models.tender import Tender
from app.models.tender_event import TenderEvent
from app.services.scoring_service import rescore_tender
from notifier.service import NotificationManager
from classifier.text_utils import normalize_text
from collector.factory import get_collector
from collector.types import NormalizedTenderInput
from collector.utils import build_dedupe_key, content_checksum

logger = logging.getLogger(__name__)

SNAPSHOT_DIR = Path("collector/snapshots")


class CollectorRunner:
    def __init__(self, db: Session, max_retries: int = 3, retry_backoff_seconds: int = 2) -> None:
        self.db = db
        self.max_retries = max_retries
        self.retry_backoff_seconds = retry_backoff_seconds

    def run_source(self, source: SourceConfig) -> int:
        run = CollectorRun(source_config_id=source.id, status=CollectorRunStatus.RUNNING.value)
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)

        source.last_run_at = datetime.now(timezone.utc)
        self.db.add(source)
        self.db.commit()

        parser_version = None
        discovered = 0
        created = 0
        updated = 0
        snapshot_path = None

        for attempt in range(1, self.max_retries + 1):
            try:
                collector = get_collector(source)
                output = collector.collect()
                parser_version = output.parser_version

                if output.raw_snapshot:
                    snapshot_path = self._write_snapshot(source.name, output.raw_snapshot)

                for item in output.items:
                    action = self._upsert_tender(item, output.parser_version)
                    if action == "created":
                        created += 1
                    elif action == "updated":
                        updated += 1

                discovered = len(output.items)

                run.status = CollectorRunStatus.SUCCESS.value
                run.items_discovered = discovered
                run.items_created = created
                run.items_updated = updated
                run.snapshot_path = snapshot_path
                run.parser_version = parser_version
                run.finished_at = datetime.now(timezone.utc)

                source.last_success_at = datetime.now(timezone.utc)
                source.last_error = None

                self.db.add(run)
                self.db.add(source)
                self.db.commit()

                logger.info(
                    "Collector run succeeded",
                    extra={
                        "source": source.name,
                        "items_discovered": discovered,
                        "items_created": created,
                        "items_updated": updated,
                    },
                )
                return discovered

            except Exception as exc:  # noqa: BLE001
                logger.exception("Collector run failed", extra={"source": source.name, "attempt": attempt})
                if attempt == self.max_retries:
                    run.status = CollectorRunStatus.FAILED.value
                    run.error_message = str(exc)
                    run.finished_at = datetime.now(timezone.utc)
                    run.snapshot_path = snapshot_path
                    run.parser_version = parser_version

                    source.last_failure_at = datetime.now(timezone.utc)
                    source.last_error = str(exc)

                    self.db.add(run)
                    self.db.add(source)
                    self.db.commit()
                    return 0

                time.sleep(self.retry_backoff_seconds * attempt)

        return 0

    def _upsert_tender(self, item: NormalizedTenderInput, parser_version: str) -> str:
        normalized_title = normalize_text(item.title)
        dedupe_key = build_dedupe_key(
            title=item.title,
            institution_name=item.institution_name,
            publishing_date=item.publishing_date,
            source_url=item.source_url,
            external_id=item.external_id,
            source_name=item.source_name,
        )
        checksum = content_checksum(item.summary, item.raw_text)

        existing = None
        if item.external_id:
            existing = self.db.scalar(
                select(Tender).where(
                    and_(Tender.source_name == item.source_name, Tender.external_id == item.external_id)
                )
            )
        if not existing:
            existing = self.db.scalar(select(Tender).where(Tender.dedupe_key == dedupe_key))
        if not existing:
            existing = self.db.scalar(
                select(Tender)
                .where(Tender.content_checksum == checksum)
                .where(Tender.publishing_date == item.publishing_date)
                .limit(1)
            )

        if existing:
            previous_verified = existing.official_verified
            existing.title = item.title
            existing.normalized_title = normalized_title
            existing.source_type = item.source_type
            existing.source_url = item.source_url
            existing.external_id = item.external_id
            existing.publishing_date = item.publishing_date
            existing.deadline_date = item.deadline_date
            existing.tender_date = item.tender_date
            existing.institution_name = item.institution_name
            existing.city = item.city
            existing.region = item.region
            existing.tender_type = item.tender_type
            existing.summary = item.summary
            existing.raw_text = item.raw_text
            existing.parser_version = parser_version
            existing.content_checksum = checksum
            existing.official_verified = existing.official_verified or item.official_verified
            existing.signal_found = existing.signal_found or item.signal_found

            self.db.add(existing)
            self.db.flush()

            self.db.add(
                TenderEvent(
                    tender_id=existing.id,
                    event_type="ingestion_updated",
                    event_data={"source": item.source_name, "dedupe_key": dedupe_key},
                )
            )
            if not previous_verified and existing.official_verified:
                self.db.add(
                    TenderEvent(
                        tender_id=existing.id,
                        event_type="official_verified",
                        event_data={"verified_from_source": item.source_name},
                    )
                )

            self.db.commit()
            rescore_tender(self.db, existing)
            if not previous_verified and existing.official_verified:
                NotificationManager(self.db).notify_official_verified(existing)
            return "updated"

        tender = Tender(
            title=item.title,
            normalized_title=normalized_title,
            source_type=item.source_type,
            source_name=item.source_name,
            source_url=item.source_url,
            external_id=item.external_id,
            publishing_date=item.publishing_date,
            deadline_date=item.deadline_date,
            tender_date=item.tender_date,
            institution_name=item.institution_name,
            city=item.city,
            region=item.region,
            tender_type=item.tender_type,
            summary=item.summary,
            raw_text=item.raw_text,
            extracted_keywords=[],
            match_explanation={},
            official_verified=item.official_verified,
            signal_found=item.signal_found,
            status=TenderStatus.NEW.value,
            dedupe_key=dedupe_key,
            content_checksum=checksum,
            parser_version=parser_version,
        )
        self.db.add(tender)
        self.db.flush()

        self.db.add(
            TenderEvent(
                tender_id=tender.id,
                event_type="ingestion_created",
                event_data={"source": item.source_name, "dedupe_key": dedupe_key},
            )
        )

        self.db.commit()
        self.db.refresh(tender)

        rescore_tender(self.db, tender)
        return "created"

    def _write_snapshot(self, source_name: str, content: str) -> str:
        normalized = normalize_text(source_name)
        safe_name = re.sub(r"[^a-z0-9._-]+", "_", normalized).strip("_") or "source"
        now = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
        path = SNAPSHOT_DIR / f"{safe_name}_{now}.html"
        path.write_text(content, encoding="utf-8")
        return str(path)
