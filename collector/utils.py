from __future__ import annotations

import hashlib
from datetime import date
from typing import Optional

from classifier.text_utils import normalize_text


def build_dedupe_key(
    title: str,
    institution_name: Optional[str],
    publishing_date: Optional[date],
    source_url: str,
    external_id: Optional[str],
    source_name: str,
) -> str:
    if external_id:
        return normalize_text(f"{source_name}:{external_id}")

    base = "|".join(
        [
            normalize_text(title),
            normalize_text(institution_name or ""),
            publishing_date.isoformat() if publishing_date else "",
            normalize_text(source_url),
        ]
    )
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def content_checksum(summary: Optional[str], raw_text: Optional[str]) -> str:
    content = f"{summary or ''}|{raw_text or ''}"
    return hashlib.sha256(content.encode("utf-8")).hexdigest()
