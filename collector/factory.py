from __future__ import annotations

from app.models.source_config import SourceConfig
from collector.adapters.generic_html_collector import GenericHtmlCollector
from collector.adapters.ilan_gov_tr_api_collector import IlanGovTrApiCollector
from collector.adapters.json_api_collector import JsonApiCollector
from collector.adapters.mock_official_collector import MockOfficialCollector
from collector.adapters.mock_signal_news_collector import MockSignalNewsCollector
from collector.adapters.rss_feed_collector import RssFeedCollector
from collector.base import BaseCollector


def get_collector(source: SourceConfig) -> BaseCollector:
    adapter = (source.config_json or {}).get("adapter")
    base_url = (source.base_url or "").lower()

    if adapter == "mock_official":
        return MockOfficialCollector(source)
    if adapter == "mock_signal_news":
        return MockSignalNewsCollector(source)
    if adapter == "ilan_gov_tr_api":
        return IlanGovTrApiCollector(source)
    if adapter == "generic_html":
        return GenericHtmlCollector(source)
    if adapter == "rss_feed":
        return RssFeedCollector(source)
    if adapter == "json_api":
        return JsonApiCollector(source)

    if source.source_type == "official" and "ilan.gov.tr" in base_url:
        return IlanGovTrApiCollector(source)

    if source.source_type == "official":
        return GenericHtmlCollector(source)
    if source.source_type in {"news", "institution", "public_announcement"}:
        return GenericHtmlCollector(source)

    return GenericHtmlCollector(source)
