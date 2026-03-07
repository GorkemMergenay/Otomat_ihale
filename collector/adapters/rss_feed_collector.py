from __future__ import annotations

from datetime import date, datetime
from email.utils import parsedate_to_datetime
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional

import httpx

from collector.base import BaseCollector
from collector.date_extract import extract_deadline_from_text, extract_any_date_from_text
from collector.types import CollectorOutput, NormalizedTenderInput


class RssFeedCollector(BaseCollector):
    """Collects signal/announcement items from one or more RSS/Atom feeds."""

    parser_version = "rss-feed-1.0"

    def collect(self) -> CollectorOutput:
        cfg = self.source_config.config_json or {}
        feed_urls = cfg.get("feed_urls")
        if not feed_urls and cfg.get("feed_url"):
            feed_urls = [cfg.get("feed_url")]

        if not isinstance(feed_urls, list) or not feed_urls:
            raise ValueError("RssFeedCollector requires `feed_urls` (list) or `feed_url` (string)")

        max_items = int(cfg.get("max_items", 60))
        timeout = float(cfg.get("timeout_seconds", 20))

        raw_snapshots: List[str] = []
        items: List[NormalizedTenderInput] = []

        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            for feed_url in feed_urls:
                response = client.get(str(feed_url))
                response.raise_for_status()
                xml = response.text
                raw_snapshots.append(f"<!-- {feed_url} -->\n{xml}")

                for entry in self._parse_feed(xml):
                    if len(items) >= max_items:
                        break

                    title = entry["title"]
                    summary = entry.get("summary")
                    link = entry.get("link") or str(feed_url)
                    published = entry.get("publishing_date")
                    raw_text = f"{title} {summary or ''}".strip()
                    deadline = extract_deadline_from_text(raw_text)
                    if not published and raw_text:
                        pub = extract_any_date_from_text(raw_text)
                        if pub:
                            published = pub

                    items.append(
                        NormalizedTenderInput(
                            title=title,
                            source_type=self.source_config.source_type,
                            source_name=self.source_config.name,
                            source_url=link,
                            external_id=entry.get("external_id"),
                            publishing_date=published,
                            deadline_date=deadline,
                            summary=summary,
                            raw_text=raw_text,
                            institution_name=self._institution_from_link(link),
                            official_verified=self.source_config.source_type == "official",
                            signal_found=self.source_config.source_type != "official",
                            parser_version=self.parser_version,
                            metadata={"feed_url": str(feed_url)},
                        )
                    )

                if len(items) >= max_items:
                    break

        snapshot = "\n\n".join(raw_snapshots) if raw_snapshots else None
        return CollectorOutput(items=items, parser_version=self.parser_version, raw_snapshot=snapshot)

    def _parse_feed(self, xml: str) -> List[Dict[str, Any]]:
        try:
            root = ET.fromstring(xml)
        except ET.ParseError:
            return []

        rows: List[Dict[str, Any]] = []
        nodes = [node for node in root.iter() if self._tag_name(node.tag) == "item"]
        if not nodes:
            nodes = [node for node in root.iter() if self._tag_name(node.tag) == "entry"]

        for node in nodes:
            title = self._node_text(node, "title")
            if not title:
                continue

            link = self._link_from_node(node)
            summary = self._node_text(node, "description") or self._node_text(node, "summary")
            external_id = self._node_text(node, "guid") or self._node_text(node, "id")
            published_raw = (
                self._node_text(node, "pubDate")
                or self._node_text(node, "published")
                or self._node_text(node, "updated")
            )

            rows.append(
                {
                    "title": title.strip(),
                    "summary": (summary or "").strip() or None,
                    "link": link,
                    "external_id": external_id,
                    "publishing_date": self._parse_date(published_raw),
                }
            )
        return rows

    def _node_text(self, node: ET.Element, tag_name: str) -> Optional[str]:
        for child in node:
            if self._tag_name(child.tag) != tag_name:
                continue
            text = "".join(child.itertext()).strip()
            if text:
                return text
        return None

    def _link_from_node(self, node: ET.Element) -> Optional[str]:
        for child in node:
            if self._tag_name(child.tag) != "link":
                continue

            href = (child.attrib.get("href") or "").strip()
            if href:
                return href

            text = "".join(child.itertext()).strip()
            if text:
                return text
        return None

    def _tag_name(self, tag: str) -> str:
        if "}" in tag:
            return tag.split("}", 1)[1].lower()
        return tag.lower()

    def _parse_date(self, value: Optional[str]) -> Optional[date]:
        if not value:
            return None
        try:
            return parsedate_to_datetime(value).date()
        except Exception:  # noqa: BLE001
            pass

        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
        except ValueError:
            return None

    def _institution_from_link(self, link: str) -> Optional[str]:
        if not link:
            return None
        host = (urlparse(link).hostname or "").strip().lower()
        if not host:
            return None
        return host.removeprefix("www.")
