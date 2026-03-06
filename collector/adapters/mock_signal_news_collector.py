from __future__ import annotations

from datetime import date, timedelta

from collector.base import BaseCollector
from collector.types import CollectorOutput, NormalizedTenderInput


class MockSignalNewsCollector(BaseCollector):
    parser_version = "mock-signal-news-1.0"

    def collect(self) -> CollectorOutput:
        today = date.today()
        items = [
            NormalizedTenderInput(
                title="Şehir Hastanesi Kampüsünde Self Servis Satış Ünitesi ve Kahve Otomatı İhalesi Hazırlığı",
                source_type="news",
                source_name=self.source_config.name,
                source_url=f"{self.source_config.base_url.rstrip('/')}/haber/sehir-hastanesi-kiosk-ihale",
                external_id=None,
                publishing_date=today,
                deadline_date=today + timedelta(days=35),
                institution_name="Ankara Şehir Hastanesi",
                city="Ankara",
                region="İç Anadolu",
                tender_type="duyuru",
                summary="Basın açıklamasında bekleme alanlarına kahve ve atıştırmalık otomatları planlandığı belirtildi.",
                raw_text="Henüz resmi ilan numarası yok. İşletme modeli ve teknik kriterler hazırlık aşamasında.",
                official_verified=False,
                signal_found=True,
                parser_version=self.parser_version,
            )
        ]

        snapshot = "\n".join([item.title for item in items])
        return CollectorOutput(items=items, parser_version=self.parser_version, raw_snapshot=snapshot)
