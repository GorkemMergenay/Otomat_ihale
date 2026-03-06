"""
JSON API collector: fetches a REST endpoint returning JSON and maps
configurable paths to NormalizedTenderInput. Suitable for EKAP/KIK-style
APIs or any tender list API that returns JSON.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any

import httpx

from collector.base import BaseCollector
from collector.types import CollectorOutput, NormalizedTenderInput


def _get_nested(data: dict[str, Any], path: str) -> Any:
    """Get value by dot path, e.g. 'data.items'."""
    for key in path.split("."):
        if not isinstance(data, dict):
            return None
        data = data.get(key)
    return data


def _parse_date(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value if not isinstance(value, datetime) else value.date()
    s = str(value).strip()
    if not s:
        return None
    s = s.replace("Z", "+00:00")
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(s[:10], fmt).date()
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(s).date()
    except ValueError:
        return None


class JsonApiCollector(BaseCollector):
    """
    Collects tenders from a JSON API.

    config_json:
    - api_url: str (required) — full URL to GET (or POST if method is POST)
    - method: "GET" | "POST" (default GET)
    - items_path: str (default "data" or "items") — dot path to array of items
    - field_mapping: dict — map NormalizedTenderInput field names to JSON keys
      e.g. {"title": "baslik", "summary": "ozet", "external_id": "id", "source_url": "link"}
    - max_items: int (default 500)
    - timeout_seconds: float (default 25)
    - headers: dict (optional) — extra HTTP headers
    """

    parser_version = "json-api-1.0"

    DEFAULT_MAPPING = {
        "title": "title",
        "summary": "summary",
        "external_id": "id",
        "source_url": "url",
        "publishing_date": "publishing_date",
        "deadline_date": "deadline_date",
        "institution_name": "institution_name",
        "city": "city",
        "tender_type": "tender_type",
    }

    def collect(self) -> CollectorOutput:
        cfg = self.source_config.config_json or {}
        api_url = cfg.get("api_url") or cfg.get("url")
        if not api_url:
            raise ValueError("JsonApiCollector requires api_url (or url) in config_json")

        method = (cfg.get("method") or "GET").upper()
        items_path = cfg.get("items_path", "data.items")
        if not items_path:
            items_path = "items"
        mapping = {**self.DEFAULT_MAPPING, **(cfg.get("field_mapping") or {})}
        max_items = int(cfg.get("max_items", 500))
        timeout = float(cfg.get("timeout_seconds", 25))
        headers = dict(cfg.get("headers") or {})

        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            if method == "POST":
                body = cfg.get("body")
                response = client.post(api_url, json=body, headers=headers)
            else:
                response = client.get(api_url, headers=headers)
            response.raise_for_status()
            data = response.json()

        raw_list = _get_nested(data, items_path)
        if raw_list is None and "." in items_path:
            raw_list = _get_nested(data, items_path.split(".")[0])
        if not isinstance(raw_list, list):
            raw_list = [data] if isinstance(data, dict) and data else []

        items: list[NormalizedTenderInput] = []
        for raw in raw_list[:max_items]:
            if not isinstance(raw, dict):
                continue
            title = raw.get(mapping["title"]) or raw.get("title") or ""
            if not str(title).strip():
                continue
            source_url = str(raw.get(mapping["source_url"]) or raw.get("url") or raw.get("link") or api_url)
            summary = raw.get(mapping["summary"]) or raw.get("summary") or raw.get("description") or ""
            external_id = raw.get(mapping["external_id"]) or raw.get("id")
            if external_id is not None:
                external_id = str(external_id)

            items.append(
                NormalizedTenderInput(
                    title=str(title).strip(),
                    source_type=self.source_config.source_type,
                    source_name=self.source_config.name,
                    source_url=source_url,
                    external_id=external_id,
                    publishing_date=_parse_date(raw.get(mapping["publishing_date"]) or raw.get("publishing_date") or raw.get("date")),
                    deadline_date=_parse_date(raw.get(mapping["deadline_date"]) or raw.get("deadline_date") or raw.get("deadline")),
                    institution_name=str(raw.get(mapping["institution_name"]) or raw.get("institution_name") or "").strip() or None,
                    city=str(raw.get(mapping["city"]) or raw.get("city") or "").strip() or None,
                    tender_type=str(raw.get(mapping["tender_type"]) or raw.get("tender_type") or "").strip() or None,
                    summary=str(summary).strip() or None,
                    raw_text=f"{title} {summary}".strip(),
                    official_verified=self.source_config.source_type == "official",
                    signal_found=self.source_config.source_type != "official",
                    parser_version=self.parser_version,
                    metadata={"api_url": str(api_url)},
                )
            )

        return CollectorOutput(
            items=items,
            parser_version=self.parser_version,
            raw_snapshot=None,
        )
