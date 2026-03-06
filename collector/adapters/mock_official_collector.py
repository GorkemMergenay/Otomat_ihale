from __future__ import annotations

from datetime import date, timedelta

from collector.base import BaseCollector
from collector.types import CollectorOutput, NormalizedTenderInput


class MockOfficialCollector(BaseCollector):
    parser_version = "mock-official-1.0"

    def collect(self) -> CollectorOutput:
        today = date.today()

        items = [
            NormalizedTenderInput(
                title="İstanbul Havalimanı Yolcu Alanları Self Servis İçecek ve Snack Otomatı Kurulum ve İşletme İhalesi",
                source_type="official",
                source_name=self.source_config.name,
                source_url=f"{self.source_config.base_url.rstrip('/')}/ilan/IST-OTM-2026-01",
                external_id="IST-OTM-2026-01",
                publishing_date=today,
                deadline_date=today + timedelta(days=18),
                institution_name="İGA İstanbul Havalimanı İşletmesi",
                city="İstanbul",
                region="Marmara",
                tender_type="hizmet alımı",
                summary="Self servis kahve, içecek ve atıştırmalık otomatlarının kurulumu ve işletme hakkı devri.",
                raw_text="Kiosk alanları, POS uyumlu satış ünitesi, bakım ve kurulum yükümlülükleri içerir.",
                official_verified=True,
                signal_found=False,
                parser_version=self.parser_version,
            ),
            NormalizedTenderInput(
                title="Ankara Metro İstasyonları Akıllı Kiosk ve Mikro Market Satış Ünitesi İşletme Hakkı",
                source_type="official",
                source_name=self.source_config.name,
                source_url=f"{self.source_config.base_url.rstrip('/')}/ilan/ANK-METRO-2026-02",
                external_id="ANK-METRO-2026-02",
                publishing_date=today,
                deadline_date=today + timedelta(days=26),
                institution_name="EGO Genel Müdürlüğü",
                city="Ankara",
                region="İç Anadolu",
                tender_type="işletme hakkı",
                summary="Metro bekleme alanlarında akıllı dolap, unattended retail ve self servis satış hizmetleri.",
                raw_text="Teknik şartname POS cihazlı satış ünitesi, 7/24 çalışma ve uzaktan izleme içerir.",
                official_verified=True,
                signal_found=False,
                parser_version=self.parser_version,
            ),
        ]

        snapshot = "\n".join([item.title for item in items])
        return CollectorOutput(items=items, parser_version=self.parser_version, raw_snapshot=snapshot)
