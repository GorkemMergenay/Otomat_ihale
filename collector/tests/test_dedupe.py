from __future__ import annotations

from datetime import date

from collector.utils import build_dedupe_key, content_checksum


def test_dedupe_key_prefers_external_id() -> None:
    key = build_dedupe_key(
        title="A",
        institution_name="B",
        publishing_date=date(2026, 3, 1),
        source_url="https://example.com/tender",
        external_id="X-123",
        source_name="EKAP",
    )
    assert key == "ekap:x-123"


def test_dedupe_key_same_for_normalized_title_variants() -> None:
    key1 = build_dedupe_key(
        title="İzmir Büyükşehir Otomat İhalesi",
        institution_name="İzmir Belediyesi",
        publishing_date=date(2026, 3, 2),
        source_url="https://example.com/tender",
        external_id=None,
        source_name="Portal",
    )
    key2 = build_dedupe_key(
        title="Izmir Buyuksehir  otomat ihalesi",
        institution_name="Izmir Belediyesi",
        publishing_date=date(2026, 3, 2),
        source_url="https://example.com/tender",
        external_id=None,
        source_name="Portal",
    )
    assert key1 == key2


def test_content_checksum_changes_with_text() -> None:
    c1 = content_checksum("summary", "raw")
    c2 = content_checksum("summary", "raw2")
    assert c1 != c2
