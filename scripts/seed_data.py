from __future__ import annotations

import os
from datetime import datetime, timezone

from sqlalchemy import delete, func, inspect, select, text

from app.core.config import settings
from app.core.passwords import hash_password
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.keyword_rule import KeywordRule
from app.models.notification import Notification
from app.models.source_config import SourceConfig
from app.models.tender import Tender
from app.models.tender_document import TenderDocument
from app.models.tender_event import TenderEvent
from app.models.user import User
from collector.runner import CollectorRunner


SEED_SOURCES = [
    {
        "name": "ilan.gov.tr Resmi İhale API",
        "source_type": "official",
        "base_url": "https://www.ilan.gov.tr",
        "is_active": True,
        "crawl_frequency": "0 */2 * * *",
        "config_json": {
            "adapter": "ilan_gov_tr_api",
            "page_size": 60,
            "pages": 8,
            "sorting": "publishStartDate desc",
            "include_ads_by_filter": True,
            "include_homepage_endpoints": True,
            "include_ad_source_ads": True,
            "require_quick_match": True,
            "detail_only_for_match": True,
            "max_detail_requests": 220,
            "max_ads_total": 1500,
        },
    },
    {
        "name": "Google News - Otomat/Kiosk İhale Sinyalleri",
        "source_type": "news",
        "base_url": "https://news.google.com",
        "is_active": True,
        "crawl_frequency": "0 */3 * * *",
        "config_json": {
            "adapter": "rss_feed",
            "feed_urls": [
                "https://news.google.com/rss/search?q=ihale+otomat+OR+kiosk+OR+%22self+servis%22&hl=tr&gl=TR&ceid=TR:tr",
                "https://news.google.com/rss/search?q=%22sat%C4%B1%C5%9F+alan%C4%B1+kiralama%22+ihale&hl=tr&gl=TR&ceid=TR:tr",
            ],
            "max_items": 100,
        },
    },
    {
        "name": "Bing News - Kamu İhale Sinyalleri",
        "source_type": "news",
        "base_url": "https://www.bing.com",
        "is_active": True,
        "crawl_frequency": "0 */4 * * *",
        "config_json": {
            "adapter": "rss_feed",
            "feed_urls": [
                "https://www.bing.com/news/search?q=ihale+otomat+kiosk+mikro+market&format=RSS&setlang=tr-TR",
                "https://www.bing.com/news/search?q=belediye+ihale+sat%C4%B1%C5%9F+alan%C4%B1+kiralama&format=RSS&setlang=tr-TR",
            ],
            "max_items": 80,
        },
    },
    {
        "name": "Google News - Kurum Duyuru Sinyalleri",
        "source_type": "public_announcement",
        "base_url": "https://news.google.com",
        "is_active": True,
        "crawl_frequency": "0 */4 * * *",
        "config_json": {
            "adapter": "rss_feed",
            "feed_urls": [
                "https://news.google.com/rss/search?q=%22havaliman%C4%B1%22+%22i%C5%9Fletme+hakk%C4%B1%22+ihale&hl=tr&gl=TR&ceid=TR:tr",
                "https://news.google.com/rss/search?q=%22%C3%BCniversite%22+%22self+servis%22+ihale&hl=tr&gl=TR&ceid=TR:tr",
            ],
            "max_items": 80,
        },
    },
    {
        "name": "EKAP İhale Duyuruları (Şablon)",
        "source_type": "official",
        "base_url": "https://ekap.kik.gov.tr",
        "is_active": False,
        "crawl_frequency": "0 */6 * * *",
        "config_json": {
            "adapter": "generic_html",
            "template_source": True,
            "list_path": "/",
            "item_selector": ".announcement-item",
            "title_selector": "a",
            "link_selector": "a",
            "summary_selector": ".summary",
            "notes": "Seçicileri kaynağın güncel HTML yapısına göre düzenleyin.",
        },
    },
    {
        "name": "DHMİ İhale ve Kiralama Duyuruları (Şablon)",
        "source_type": "institution",
        "base_url": "https://www.dhmi.gov.tr",
        "is_active": False,
        "crawl_frequency": "0 */6 * * *",
        "config_json": {
            "adapter": "generic_html",
            "template_source": True,
            "list_path": "/",
            "item_selector": ".duyuru-item",
            "title_selector": "a",
            "link_selector": "a",
            "summary_selector": ".duyuru-ozet",
            "notes": "Havalimanı/kiralama duyuru sayfaları için selector güncellemesi gerekir.",
        },
    },
    {
        "name": "TCDD Duyurular (Şablon)",
        "source_type": "institution",
        "base_url": "https://www.tcdd.gov.tr",
        "is_active": False,
        "crawl_frequency": "0 */8 * * *",
        "config_json": {
            "adapter": "generic_html",
            "template_source": True,
            "list_path": "/duyurular",
            "item_selector": ".list-item",
            "title_selector": "a",
            "link_selector": "a",
            "summary_selector": "p",
            "notes": "İstasyon/terminal ticari alan duyuruları için örnek şablon.",
        },
    },
    {
        "name": "İBB İhale Duyuruları (Şablon)",
        "source_type": "institution",
        "base_url": "https://www.ibb.istanbul",
        "is_active": False,
        "crawl_frequency": "0 */6 * * *",
        "config_json": {
            "adapter": "generic_html",
            "template_source": True,
            "list_path": "/tr-TR/duyurular",
            "item_selector": ".news-item",
            "title_selector": "a",
            "link_selector": "a",
            "summary_selector": ".news-summary",
            "notes": "Belediye tesisleri ve kiralama duyuruları için kaynak şablonu.",
        },
    },
    {
        "name": "Ankara Büyükşehir İhale Duyuruları (Şablon)",
        "source_type": "institution",
        "base_url": "https://www.ankara.bel.tr",
        "is_active": False,
        "crawl_frequency": "0 */8 * * *",
        "config_json": {
            "adapter": "generic_html",
            "template_source": True,
            "list_path": "/duyurular",
            "item_selector": ".duyuru-list-item",
            "title_selector": "a",
            "link_selector": "a",
            "summary_selector": ".duyuru-list-item__text",
            "notes": "Kurum sayfası yapısına göre selector güncellemesi gerekebilir.",
        },
    },
    {
        "name": "Kamu İhale Kurumu Duyuru Sinyalleri (Şablon)",
        "source_type": "public_announcement",
        "base_url": "https://www.kik.gov.tr",
        "is_active": False,
        "crawl_frequency": "0 */12 * * *",
        "config_json": {
            "adapter": "generic_html",
            "template_source": True,
            "list_path": "/Duyurular",
            "item_selector": ".duyuru-item",
            "title_selector": "a",
            "link_selector": "a",
            "summary_selector": ".duyuru-ozet",
            "notes": "Resmi duyuru sinyali için erken tespit kaynağı şablonu.",
        },
    },
    {
        "name": "Üniversite Kampüs Duyuruları - Örnek (Şablon)",
        "source_type": "institution",
        "base_url": "https://www.hacettepe.edu.tr",
        "is_active": False,
        "crawl_frequency": "0 */12 * * *",
        "config_json": {
            "adapter": "generic_html",
            "template_source": True,
            "list_path": "/duyurular",
            "item_selector": ".announcement-item",
            "title_selector": "a",
            "link_selector": "a",
            "summary_selector": ".announcement-summary",
            "notes": "Kampüs satış/işletme alanı duyuruları için örnek kurum şablonu.",
        },
    },
    {
        "name": "Sağlık Kurumu Duyuruları - Örnek (Şablon)",
        "source_type": "institution",
        "base_url": "https://www.saglik.gov.tr",
        "is_active": False,
        "crawl_frequency": "0 */12 * * *",
        "config_json": {
            "adapter": "generic_html",
            "template_source": True,
            "list_path": "/TR,0/duyurular.html",
            "item_selector": ".duyuru-item",
            "title_selector": "a",
            "link_selector": "a",
            "summary_selector": ".duyuru-item__summary",
            "notes": "Hastane kampüs duyuruları için örnek şablon.",
        },
    },
    # JSON API kaynakları (EKAP/KIK vb. API'ler için şablon)
    {
        "name": "EKAP / KIK JSON API (Şablon)",
        "source_type": "official",
        "base_url": "https://ekap.kik.gov.tr",
        "is_active": False,
        "crawl_frequency": "0 */6 * * *",
        "config_json": {
            "adapter": "json_api",
            "template_source": True,
            "api_url": "https://ekap.kik.gov.tr/api/ilan/listesi",
            "items_path": "data",
            "field_mapping": {
                "title": "baslik",
                "summary": "ozet",
                "external_id": "ilanId",
                "source_url": "detayUrl",
                "publishing_date": "yayinTarihi",
                "deadline_date": "sonBasvuruTarihi",
                "institution_name": "kurumAdi",
                "city": "il",
            },
            "max_items": 200,
            "notes": "API endpoint ve alan adları kurum dokümantasyonuna göre güncellenmeli.",
        },
    },
    {
        "name": "Google News - Mikro Market ve Akıllı Dolap",
        "source_type": "news",
        "base_url": "https://news.google.com",
        "is_active": True,
        "crawl_frequency": "0 */4 * * *",
        "config_json": {
            "adapter": "rss_feed",
            "feed_urls": [
                "https://news.google.com/rss/search?q=mikro+market+akıllı+dolap+ihale&hl=tr&gl=TR&ceid=TR:tr",
                "https://news.google.com/rss/search?q=otomat+cihaz+tedarik+ihale&hl=tr&gl=TR&ceid=TR:tr",
            ],
            "max_items": 60,
        },
    },
    {
        "name": "Google News - Belediye ve Kamu İşletme İhaleleri",
        "source_type": "public_announcement",
        "base_url": "https://news.google.com",
        "is_active": True,
        "crawl_frequency": "0 */5 * * *",
        "config_json": {
            "adapter": "rss_feed",
            "feed_urls": [
                "https://news.google.com/rss/search?q=belediye+ihale+işletme+kiralama&hl=tr&gl=TR&ceid=TR:tr",
                "https://news.google.com/rss/search?q=kamu+ihale+satış+noktası&hl=tr&gl=TR&ceid=TR:tr",
            ],
            "max_items": 60,
        },
    },
]

OPTIONAL_MOCK_SOURCES = [
    {
        "name": "EKAP Mock Official (Demo)",
        "source_type": "official",
        "base_url": "https://ekap-kamu.test",
        "is_active": False,
        "crawl_frequency": "0 */6 * * *",
        "config_json": {"adapter": "mock_official"},
    },
    {
        "name": "Kamu Gündem Mock News (Demo)",
        "source_type": "news",
        "base_url": "https://kamu-gundem.test",
        "is_active": False,
        "crawl_frequency": "0 */12 * * *",
        "config_json": {"adapter": "mock_signal_news"},
    },
]

MOCK_ADAPTERS = {"mock_official", "mock_signal_news"}

DEFAULT_SEED_PASSWORD = os.getenv("SEED_DEFAULT_PASSWORD", "Otomat123!")

SEED_USERS = [
    {"name": "Admin User", "email": "admin@otomat.local", "role": "admin", "is_active": True},
    {"name": "Analyst User", "email": "analyst@otomat.local", "role": "analyst", "is_active": True},
    {"name": "Viewer User", "email": "viewer@otomat.local", "role": "viewer", "is_active": True},
]

SEED_KEYWORDS = [
    # Direct
    {"keyword": "otomat", "category": "direct", "weight": 5.0, "matching_type": "contains"},
    {"keyword": "vending", "category": "direct", "weight": 4.8, "matching_type": "contains"},
    {"keyword": "satış otomatı", "category": "direct", "weight": 5.0, "matching_type": "contains"},
    {"keyword": "kahve otomatı", "category": "direct", "weight": 5.0, "matching_type": "contains"},
    {"keyword": "içecek otomatı", "category": "direct", "weight": 4.7, "matching_type": "contains"},
    {"keyword": "snack otomatı", "category": "direct", "weight": 4.6, "matching_type": "contains"},
    {"keyword": "self servis kiosk", "category": "direct", "weight": 4.9, "matching_type": "contains"},
    {"keyword": "akıllı kiosk", "category": "direct", "weight": 4.5, "matching_type": "contains"},
    {"keyword": "akıllı dolap", "category": "direct", "weight": 4.2, "matching_type": "contains"},
    {"keyword": "mikro market", "category": "direct", "weight": 4.0, "matching_type": "contains"},
    {"keyword": "unattended retail", "category": "direct", "weight": 4.3, "matching_type": "contains"},
    # Related commercial
    {"keyword": "büfe alanı", "category": "commercial", "weight": 3.4, "matching_type": "contains"},
    {"keyword": "satış alanı kiralama", "category": "commercial", "weight": 3.6, "matching_type": "contains"},
    {"keyword": "işletme hakkı", "category": "commercial", "weight": 3.8, "matching_type": "contains"},
    {"keyword": "self servis satış", "category": "commercial", "weight": 3.7, "matching_type": "contains"},
    {"keyword": "yiyecek içecek satış ünitesi", "category": "commercial", "weight": 3.5, "matching_type": "contains"},
    {"keyword": "kiosk alanı", "category": "commercial", "weight": 3.2, "matching_type": "contains"},
    {"keyword": "terminal satış noktası", "category": "commercial", "weight": 3.2, "matching_type": "contains"},
    {"keyword": "bekleme alanı satış hizmeti", "category": "commercial", "weight": 3.6, "matching_type": "contains"},
    {"keyword": "pos cihazlı satış ünitesi", "category": "technical", "weight": 3.4, "matching_type": "contains"},
    # Institution signals
    {"keyword": "havalimanı", "category": "institution_signal", "weight": 2.8, "matching_type": "contains"},
    {"keyword": "metro", "category": "institution_signal", "weight": 2.6, "matching_type": "contains"},
    {"keyword": "belediye tesisi", "category": "institution_signal", "weight": 2.4, "matching_type": "contains"},
    {"keyword": "üniversite kampüsü", "category": "institution_signal", "weight": 2.8, "matching_type": "contains"},
    {"keyword": "hastane", "category": "institution_signal", "weight": 2.5, "matching_type": "contains"},
    {"keyword": "spor tesisi", "category": "institution_signal", "weight": 2.1, "matching_type": "contains"},
    {"keyword": "sosyal tesis", "category": "institution_signal", "weight": 2.0, "matching_type": "contains"},
    {"keyword": "terminal", "category": "institution_signal", "weight": 2.4, "matching_type": "contains"},
    {"keyword": "istasyon", "category": "institution_signal", "weight": 2.3, "matching_type": "contains"},
    {"keyword": "kamu tesisi", "category": "institution_signal", "weight": 2.2, "matching_type": "contains"},
    # Negative
    {
        "keyword": "temizlik hizmeti",
        "category": "negative",
        "weight": 3.5,
        "matching_type": "contains",
        "is_negative": True,
    },
    {
        "keyword": "inşaat malzemesi",
        "category": "negative",
        "weight": 3.2,
        "matching_type": "contains",
        "is_negative": True,
    },
]


def seed_users() -> None:
    db = SessionLocal()
    try:
        for user in SEED_USERS:
            password_hash = hash_password(DEFAULT_SEED_PASSWORD)
            existing = db.scalar(select(User).where(User.email == user["email"]))
            if not existing:
                db.add(
                    User(
                        **user,
                        password_hash=password_hash,
                        password_updated_at=datetime.now(timezone.utc),
                    )
                )
                continue

            existing.name = user["name"]
            existing.role = user["role"]
            existing.is_active = user["is_active"]
            if not existing.password_hash:
                existing.password_hash = password_hash
                existing.password_updated_at = datetime.now(timezone.utc)
            db.add(existing)
        db.commit()
    finally:
        db.close()


def ensure_user_auth_columns() -> None:
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    if "users" not in table_names:
        return

    existing_columns = {column["name"] for column in inspector.get_columns("users")}
    statements: list[str] = []

    if "password_hash" not in existing_columns:
        statements.append("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255) DEFAULT ''")
    if "last_login_at" not in existing_columns:
        statements.append("ALTER TABLE users ADD COLUMN last_login_at DATETIME")
    if "password_updated_at" not in existing_columns:
        statements.append("ALTER TABLE users ADD COLUMN password_updated_at DATETIME")

    if not statements:
        return

    db = SessionLocal()
    try:
        for ddl in statements:
            db.execute(text(ddl))
        db.commit()
    finally:
        db.close()


def seed_sources() -> None:
    db = SessionLocal()
    try:
        include_mock = os.getenv("SEED_INCLUDE_MOCK_SOURCES", "false").strip().lower() in {"1", "true", "yes"}
        source_payloads = list(SEED_SOURCES)
        if include_mock:
            source_payloads.extend(OPTIONAL_MOCK_SOURCES)

        for source_payload in source_payloads:
            existing = db.scalar(select(SourceConfig).where(SourceConfig.name == source_payload["name"]))
            if existing:
                for key, value in source_payload.items():
                    setattr(existing, key, value)
                db.add(existing)
            else:
                db.add(SourceConfig(**source_payload))

        for row in db.scalars(select(SourceConfig)).all():
            adapter = (row.config_json or {}).get("adapter")
            if adapter in MOCK_ADAPTERS and not include_mock:
                row.is_active = False
                db.add(row)

        db.commit()
    finally:
        db.close()


def seed_keywords() -> None:
    db = SessionLocal()
    try:
        for rule in SEED_KEYWORDS:
            existing = db.scalar(select(KeywordRule).where(KeywordRule.keyword == rule["keyword"]))
            if not existing:
                db.add(
                    KeywordRule(
                        keyword=rule["keyword"],
                        category=rule["category"],
                        weight=rule["weight"],
                        is_active=True,
                        is_negative=rule.get("is_negative", False),
                        matching_type=rule.get("matching_type", "contains"),
                        target_field=rule.get("target_field", "any"),
                    )
                )
        db.commit()
    finally:
        db.close()


def run_collectors() -> None:
    db = SessionLocal()
    try:
        sources = db.scalars(select(SourceConfig).where(SourceConfig.is_active.is_(True))).all()
        runner = CollectorRunner(db)
        for source in sources:
            runner.run_source(source)
        total = db.scalar(select(func.count()).select_from(Tender))
        print(f"Seeded tenders total: {total}")
    finally:
        db.close()


def purge_legacy_mock_tenders() -> None:
    db = SessionLocal()
    try:
        mock_ids = db.scalars(select(Tender.id).where(Tender.parser_version.like("mock-%"))).all()
        if not mock_ids:
            return

        db.execute(delete(TenderEvent).where(TenderEvent.tender_id.in_(mock_ids)))
        db.execute(delete(TenderDocument).where(TenderDocument.tender_id.in_(mock_ids)))
        db.execute(delete(Notification).where(Notification.tender_id.in_(mock_ids)))
        db.execute(delete(Tender).where(Tender.id.in_(mock_ids)))
        db.commit()
        print(f"Mock kalıntı temizliği tamamlandı: {len(mock_ids)} ihale silindi.")
    finally:
        db.close()


def main() -> None:
    print(f"Veritabanı kullanılıyor: {settings.database_url}")
    Base.metadata.create_all(bind=engine)
    ensure_user_auth_columns()
    seed_users()
    seed_sources()
    seed_keywords()
    purge_legacy_mock_tenders()
    run_collectors()
    print("Seed işlemi tamamlandı.")


if __name__ == "__main__":
    main()
