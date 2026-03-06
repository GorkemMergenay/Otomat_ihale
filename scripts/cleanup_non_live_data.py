from __future__ import annotations

import argparse
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import delete, func, select

from app.db.session import SessionLocal
from app.models.collector_run import CollectorRun
from app.models.notification import Notification
from app.models.source_config import SourceConfig
from app.models.tender import Tender
from app.models.tender_document import TenderDocument
from app.models.tender_event import TenderEvent


NON_LIVE_ADAPTERS = {"mock_official", "mock_signal_news"}
TEST_HOST_HINTS = (".test", "localhost", "example.com")


@dataclass
class CleanupPlan:
    source_ids: list[int]
    source_names: list[str]
    tender_ids: list[int]
    parser_tender_count: int
    source_tender_count: int
    collector_run_count: int
    tender_count: int
    event_count: int
    document_count: int
    notification_count: int
    snapshot_count: int


def is_non_live_source(source: SourceConfig) -> bool:
    config = source.config_json or {}
    adapter = str(config.get("adapter") or "").strip().lower()
    base_url = (source.base_url or "").lower()

    if bool(config.get("template_source")):
        return False
    if adapter == "ilan_gov_tr_api" or "ilan.gov.tr" in base_url:
        return False
    if adapter in NON_LIVE_ADAPTERS:
        return True
    if any(hint in base_url for hint in TEST_HOST_HINTS):
        return True
    if not source.is_active:
        return True
    return False


def snapshot_prefix(source_name: str) -> str:
    text = unicodedata.normalize("NFKD", source_name).encode("ascii", "ignore").decode("ascii").lower()
    text = re.sub(r"[^a-z0-9]+", " ", text).strip()
    return text.replace(" ", "_") or "source"


def build_plan() -> CleanupPlan:
    db = SessionLocal()
    try:
        sources = db.scalars(select(SourceConfig)).all()
        non_live_sources = [source for source in sources if is_non_live_source(source)]
        source_ids = [source.id for source in non_live_sources]
        source_names = [source.name for source in non_live_sources]

        source_tender_ids = (
            db.scalars(select(Tender.id).where(Tender.source_name.in_(source_names))).all()
            if source_names
            else []
        )
        parser_tender_ids = db.scalars(select(Tender.id).where(Tender.parser_version.like("mock-%"))).all()
        tender_id_set = {int(x) for x in source_tender_ids}
        tender_id_set.update(int(x) for x in parser_tender_ids)
        tender_ids = sorted(tender_id_set)

        if not source_names and not tender_ids:
            return CleanupPlan(
                source_ids=[],
                source_names=[],
                tender_ids=[],
                parser_tender_count=0,
                source_tender_count=0,
                collector_run_count=0,
                tender_count=0,
                event_count=0,
                document_count=0,
                notification_count=0,
                snapshot_count=0,
            )
        collector_run_count = (
            db.scalar(select(func.count()).select_from(CollectorRun).where(CollectorRun.source_config_id.in_(source_ids)))
            or 0
        )
        tender_count = len(tender_ids)
        event_count = (
            db.scalar(select(func.count()).select_from(TenderEvent).where(TenderEvent.tender_id.in_(tender_ids))) or 0
            if tender_ids
            else 0
        )
        document_count = (
            db.scalar(select(func.count()).select_from(TenderDocument).where(TenderDocument.tender_id.in_(tender_ids))) or 0
            if tender_ids
            else 0
        )
        notification_count = (
            db.scalar(select(func.count()).select_from(Notification).where(Notification.tender_id.in_(tender_ids))) or 0
            if tender_ids
            else 0
        )

        snapshots_dir = Path("collector/snapshots")
        snapshot_count = 0
        if snapshots_dir.exists():
            for source_name in source_names:
                prefix = snapshot_prefix(source_name)
                snapshot_count += len(list(snapshots_dir.glob(f"{prefix}_*.html")))

        return CleanupPlan(
            source_ids=source_ids,
            source_names=source_names,
            tender_ids=tender_ids,
            parser_tender_count=len(parser_tender_ids),
            source_tender_count=len(source_tender_ids),
            collector_run_count=int(collector_run_count),
            tender_count=int(tender_count),
            event_count=int(event_count),
            document_count=int(document_count),
            notification_count=int(notification_count),
            snapshot_count=int(snapshot_count),
        )
    finally:
        db.close()


def apply_cleanup(plan: CleanupPlan) -> None:
    if not plan.source_ids and not plan.tender_ids:
        print("Temizlenecek canlı olmayan kaynak bulunamadı.")
        return

    db = SessionLocal()
    try:
        if plan.tender_ids:
            db.execute(delete(TenderEvent).where(TenderEvent.tender_id.in_(plan.tender_ids)))
            db.execute(delete(TenderDocument).where(TenderDocument.tender_id.in_(plan.tender_ids)))
            db.execute(delete(Notification).where(Notification.tender_id.in_(plan.tender_ids)))
            db.execute(delete(Tender).where(Tender.id.in_(plan.tender_ids)))

        if plan.source_ids:
            db.execute(delete(CollectorRun).where(CollectorRun.source_config_id.in_(plan.source_ids)))
            db.execute(delete(SourceConfig).where(SourceConfig.id.in_(plan.source_ids)))

        db.commit()
    finally:
        db.close()

    snapshots_dir = Path("collector/snapshots")
    if snapshots_dir.exists():
        for source_name in plan.source_names:
            prefix = snapshot_prefix(source_name)
            for snapshot in snapshots_dir.glob(f"{prefix}_*.html"):
                snapshot.unlink(missing_ok=True)


def print_plan(plan: CleanupPlan) -> None:
    if not plan.source_ids and not plan.tender_ids:
        print("Temizlenecek canlı olmayan kaynak bulunamadı.")
        return

    print("Temizleme planı:")
    print(f"- Kaynaklar: {len(plan.source_ids)}")
    for name in plan.source_names:
        print(f"  - {name}")
    print(f"- Silinecek ihale: {plan.tender_count}")
    print(f"  - Kaynağa göre: {plan.source_tender_count}")
    print(f"  - Mock parser'a göre: {plan.parser_tender_count}")
    print(f"- Silinecek ihale olayı: {plan.event_count}")
    print(f"- Silinecek doküman: {plan.document_count}")
    print(f"- Silinecek bildirim: {plan.notification_count}")
    print(f"- Silinecek kolektör koşusu: {plan.collector_run_count}")
    print(f"- Silinecek snapshot dosyası: {plan.snapshot_count}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Canlı olmayan kaynak ve ilişkili verileri temizler.")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Temizliği uygular. Bu parametre verilmezse sadece plan gösterilir.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    plan = build_plan()
    print_plan(plan)

    if not args.apply:
        print("Dry-run tamamlandı. Uygulamak için --apply kullanın.")
        return

    apply_cleanup(plan)
    print("Temizlik tamamlandı.")


if __name__ == "__main__":
    main()
