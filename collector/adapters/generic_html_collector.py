from __future__ import annotations

from datetime import date
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from collector.base import BaseCollector
from collector.date_extract import extract_deadline_from_text, extract_any_date_from_text, extract_tender_date_from_text
from collector.types import CollectorOutput, NormalizedTenderInput


class GenericHtmlCollector(BaseCollector):
    """Template collector driven by selector config.

    Expected `source_config.config_json` keys:
    - `list_path`: relative URL path
    - `item_selector`: CSS selector for announcement blocks
    - `title_selector`: CSS selector inside each item
    - `link_selector`: CSS selector inside each item (href expected)
    - optional: `summary_selector`
    """

    parser_version = "generic-html-1.0"

    def collect(self) -> CollectorOutput:
        cfg = self.source_config.config_json or {}
        list_path = cfg.get("list_path", "")
        item_selector = cfg.get("item_selector")
        title_selector = cfg.get("title_selector")
        link_selector = cfg.get("link_selector")
        summary_selector = cfg.get("summary_selector")

        if not item_selector or not title_selector or not link_selector:
            raise ValueError("GenericHtmlCollector requires item_selector/title_selector/link_selector")

        url = urljoin(self.source_config.base_url, list_path)

        with httpx.Client(timeout=20) as client:
            response = client.get(url)
            response.raise_for_status()

        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        items: list[NormalizedTenderInput] = []

        for node in soup.select(item_selector):
            title_node = node.select_one(title_selector)
            link_node = node.select_one(link_selector)
            if not title_node or not link_node:
                continue

            title = title_node.get_text(" ", strip=True)
            href = link_node.get("href")
            if not title or not href:
                continue

            summary = None
            if summary_selector:
                summary_node = node.select_one(summary_selector)
                if summary_node:
                    summary = summary_node.get_text(" ", strip=True)

            raw_text = f"{title} {summary or ''}"
            deadline = extract_deadline_from_text(raw_text)
            tender_date = extract_tender_date_from_text(raw_text) or deadline
            publishing_date = extract_any_date_from_text(raw_text) or date.today()
            date_selector = cfg.get("date_selector")
            if date_selector:
                date_node = node.select_one(date_selector)
                if date_node:
                    raw_date = date_node.get_text(" ", strip=True)
                    if raw_date:
                        publishing_date = extract_any_date_from_text(raw_date) or publishing_date
                        if not deadline:
                            deadline = extract_deadline_from_text(raw_date)
                        if not tender_date:
                            tender_date = extract_tender_date_from_text(raw_date) or deadline

            source_url = urljoin(self.source_config.base_url, href)
            items.append(
                NormalizedTenderInput(
                    title=title,
                    source_type=self.source_config.source_type,
                    source_name=self.source_config.name,
                    source_url=source_url,
                    publishing_date=publishing_date,
                    deadline_date=deadline,
                    tender_date=tender_date,
                    summary=summary,
                    raw_text=raw_text,
                    official_verified=self.source_config.source_type == "official",
                    signal_found=self.source_config.source_type != "official",
                    parser_version=self.parser_version,
                )
            )

        return CollectorOutput(items=items, parser_version=self.parser_version, raw_snapshot=html)
