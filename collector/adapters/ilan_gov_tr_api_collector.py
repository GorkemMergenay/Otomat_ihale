from __future__ import annotations

import json
from datetime import date, datetime
from typing import Any, Optional
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from classifier.text_utils import normalize_text
from collector.base import BaseCollector
from collector.types import CollectorOutput, NormalizedTenderInput


class IlanGovTrApiCollector(BaseCollector):
    """Official ilan.gov.tr API collector.

    Uses public endpoints discovered from official frontend bundles:
    - POST /api/api/services/app/Ad/AdsByFilter
    - GET  /api/api/services/app/Ad/GetAdSourceAds
    - GET  /api/api/services/app/AdHomePage/*
    - GET  /api/api/services/app/AdDetail/GetAdDetail?id={id}&isKiwiAd=false
    """

    parser_version = "ilan-govtr-api-1.1"

    API_ADS_BY_FILTER = "/api/api/services/app/Ad/AdsByFilter"
    API_AD_SOURCE_ADS = "/api/api/services/app/Ad/GetAdSourceAds"
    API_AD_DETAIL = "/api/api/services/app/AdDetail/GetAdDetail"
    API_HOMEPAGE_BASE = "/api/api/services/app/AdHomePage"
    HOMEPAGE_ENDPOINTS = (
        "GetAdsByPublishTime",
        "GetAdsFeatured",
        "GetLeastPopularAds",
        "GetPopularAdsOfToday",
    )

    DEFAULT_PREFILTER_TERMS = [
        "otomat",
        "vending",
        "kahve otomat",
        "icecek otomat",
        "atistirmalik",
        "snack",
        "self servis",
        "kiosk",
        "akilli kiosk",
        "akilli dolap",
        "mikro market",
        "unattended retail",
        "satis unitesi",
        "satis alani",
        "isletme hakki",
        "isletme",
        "kiralama",
        "kiraya",
        "kafeterya",
        "kantin",
        "bufe",
        "yiyecek icecek",
        "kullanim hakki",
        "pos",
        "odeme sistemi",
        "havalimani",
        "metro",
        "terminal",
        "istasyon",
        "universite",
        "hastane",
        "spor tesisi",
    ]

    def collect(self) -> CollectorOutput:
        cfg = self.source_config.config_json or {}
        page_size = int(cfg.get("page_size", 40))
        pages = int(cfg.get("pages", 6))
        sorting = str(cfg.get("sorting", "publishStartDate desc"))
        require_quick_match = bool(cfg.get("require_quick_match", True))
        detail_only_for_match = bool(cfg.get("detail_only_for_match", True))
        max_detail_requests = int(cfg.get("max_detail_requests", 160))
        include_ads_by_filter = bool(cfg.get("include_ads_by_filter", True))
        include_homepage_endpoints = bool(cfg.get("include_homepage_endpoints", True))
        include_ad_source_ads = bool(cfg.get("include_ad_source_ads", True))
        max_ads_total = int(cfg.get("max_ads_total", 1500))

        terms = cfg.get("prefilter_terms") or self.DEFAULT_PREFILTER_TERMS
        normalized_terms = [normalize_text(x) for x in terms if x]

        ads: list[dict[str, Any]] = []
        if include_ads_by_filter:
            ads.extend(self._fetch_ads_pages(page_size=page_size, pages=pages, sorting=sorting))
        if include_homepage_endpoints:
            ads.extend(self._fetch_homepage_ads())
        if include_ad_source_ads:
            ads.extend(self._fetch_ad_source_ads())

        items: list[NormalizedTenderInput] = []
        seen_ad_ids: set[int] = set()

        detail_calls = 0
        with httpx.Client(timeout=30) as client:
            for ad in ads:
                ad_id = ad.get("id")
                if not ad_id:
                    continue
                try:
                    ad_id_int = int(ad_id)
                except (TypeError, ValueError):
                    continue

                if ad_id_int in seen_ad_ids:
                    continue
                seen_ad_ids.add(ad_id_int)
                if len(seen_ad_ids) > max_ads_total:
                    break

                quick_text = self._build_quick_text(ad)
                is_quick_match = any(term in quick_text for term in normalized_terms)
                if require_quick_match and not is_quick_match:
                    continue

                detail: dict[str, Any] = {}
                if (not detail_only_for_match or is_quick_match) and detail_calls < max_detail_requests:
                    detail = self._fetch_ad_detail(client, ad_id_int)
                    detail_calls += 1

                normalized = self._to_normalized_input(ad=ad, detail=detail)
                if normalized:
                    items.append(normalized)

        snapshot_payload = {
            "source": self.source_config.name,
            "fetched_at": datetime.utcnow().isoformat(),
            "total_ads": len(ads),
            "candidate_items": len(items),
            "sample_ad_ids": [a.get("id") for a in ads[:20]],
        }

        return CollectorOutput(
            items=items,
            parser_version=self.parser_version,
            raw_snapshot=json.dumps(snapshot_payload, ensure_ascii=False),
        )

    def _fetch_ads_pages(self, page_size: int, pages: int, sorting: str) -> list[dict[str, Any]]:
        endpoint = urljoin(self.source_config.base_url, self.API_ADS_BY_FILTER)
        headers = {
            "Content-Type": "application/json-patch+json",
            "Accept": "text/plain",
        }

        all_ads: list[dict[str, Any]] = []

        with httpx.Client(timeout=30, headers=headers) as client:
            for page in range(pages):
                payload = {
                    "keys": {},
                    "sorting": sorting,
                    "skipCount": page * page_size,
                    "maxResultCount": page_size,
                }
                response = client.post(endpoint, json=payload)
                response.raise_for_status()
                body = response.json()
                result = body.get("result") or {}
                ads = result.get("ads") or []
                if not ads:
                    continue
                all_ads.extend(ads)

        return all_ads

    def _fetch_homepage_ads(self) -> list[dict[str, Any]]:
        ads: list[dict[str, Any]] = []
        with httpx.Client(timeout=30) as client:
            for endpoint_name in self.HOMEPAGE_ENDPOINTS:
                endpoint = urljoin(self.source_config.base_url, f"{self.API_HOMEPAGE_BASE}/{endpoint_name}")
                response = client.get(endpoint)
                response.raise_for_status()
                body = response.json()
                result = body.get("result")
                if isinstance(result, dict):
                    endpoint_ads = result.get("ads") or []
                elif isinstance(result, list):
                    endpoint_ads = result
                else:
                    endpoint_ads = []
                ads.extend(endpoint_ads)
        return ads

    def _fetch_ad_source_ads(self) -> list[dict[str, Any]]:
        endpoint = urljoin(self.source_config.base_url, self.API_AD_SOURCE_ADS)
        response = httpx.get(endpoint, timeout=30)
        response.raise_for_status()
        body = response.json()
        sources = body.get("result") or []
        ads: list[dict[str, Any]] = []
        for source in sources:
            source_name = source.get("displayName") or source.get("name")
            for ad in source.get("ads") or []:
                if source_name and not ad.get("adSourceName"):
                    ad["adSourceName"] = source_name
                ads.append(ad)
        return ads

    def _fetch_ad_detail(self, client: httpx.Client, ad_id: int) -> dict[str, Any]:
        endpoint = urljoin(self.source_config.base_url, self.API_AD_DETAIL)

        for is_kiwi in (False, True):
            response = client.get(endpoint, params={"id": ad_id, "isKiwiAd": str(is_kiwi).lower()})
            if response.status_code >= 400:
                continue
            body = response.json()
            result = body.get("result")
            if isinstance(result, dict):
                return result

        return {}

    def _to_normalized_input(
        self,
        ad: dict[str, Any],
        detail: dict[str, Any],
    ) -> Optional[NormalizedTenderInput]:
        title = (detail.get("title") or ad.get("title") or "").strip()
        if not title:
            return None

        categories = detail.get("categories") or []
        category_names = [c.get("name") for c in categories if c.get("name")]

        content_html = detail.get("content") or ""
        content_text = BeautifulSoup(content_html, "html.parser").get_text(" ", strip=True)

        publishes = detail.get("publishes") or []
        publish_start = None
        publish_end = None
        if publishes:
            publish_start = publishes[0].get("startDate")
            publish_end = publishes[0].get("endDate")

        publishing_date = self._parse_date(ad.get("publishStartDate") or publish_start)
        deadline_date = self._parse_date(publish_end)

        source_url = urljoin(
            self.source_config.base_url,
            detail.get("urlStr") or ad.get("urlStr") or "",
        )

        summary_parts = []
        if category_names:
            summary_parts.append("Kategori: " + " > ".join(category_names[:3]))
        if content_text:
            summary_parts.append(content_text[:400])
        summary = "\n".join(summary_parts) if summary_parts else None

        raw_text_parts = [
            title,
            detail.get("advertiserName") or ad.get("advertiserName") or "",
            " ".join(category_names),
            content_text,
        ]
        raw_text = " ".join(x for x in raw_text_parts if x).strip()

        tender_type = category_names[1] if len(category_names) > 1 else (category_names[0] if category_names else "ihale")

        return NormalizedTenderInput(
            title=title,
            source_type="official",
            source_name=self.source_config.name,
            source_url=source_url,
            external_id=ad.get("adNo") or (str(ad.get("id")) if ad.get("id") else None),
            publishing_date=publishing_date,
            deadline_date=deadline_date,
            institution_name=detail.get("advertiserName") or ad.get("advertiserName"),
            city=detail.get("addressCityName") or ad.get("addressCityName"),
            region=detail.get("addressCountyName") or ad.get("addressCountyName"),
            tender_type=tender_type,
            summary=summary,
            raw_text=raw_text,
            official_verified=True,
            signal_found=False,
            parser_version=self.parser_version,
            metadata={
                "ad_id": ad.get("id"),
                "ad_no": ad.get("adNo"),
                "categories": category_names,
                "ad_source_name": detail.get("adSourceName") or ad.get("adSourceName"),
            },
        )

    def _build_quick_text(self, ad: dict[str, Any]) -> str:
        parts = [
            ad.get("title") or "",
            ad.get("advertiserName") or "",
            ad.get("addressCityName") or "",
            ad.get("addressCountyName") or "",
            ad.get("adSourceName") or "",
            ad.get("urlStr") or "",
        ]
        return normalize_text(" ".join(parts))

    def _parse_date(self, value: Optional[str]) -> Optional[date]:
        if not value:
            return None
        try:
            if "T" in value:
                return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return None
