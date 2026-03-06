# Source Adapter Guide

## Purpose
Collector adapters fetch source-specific data and return normalized tender records for shared ingestion and scoring pipelines.

## Adapter Contract
Implement `collector.base.BaseCollector`:

- Input: `SourceConfig`
- Output: `CollectorOutput`
  - `items: list[NormalizedTenderInput]`
  - `parser_version: str`
  - `raw_snapshot: str | None`

## Required Normalized Fields
Each `NormalizedTenderInput` should provide at minimum:
- `title`
- `source_type`
- `source_name`
- `source_url`
- `summary` and/or `raw_text`
- `official_verified`
- `signal_found`

Recommended fields:
- `external_id`
- `publishing_date`
- `deadline_date`
- `institution_name`
- `city`
- `tender_type`

## Adapter Selection
`collector.factory.get_collector()` chooses adapters based on `source_config.config_json.adapter`.

Current adapters:
- `mock_official` -> `MockOfficialCollector`
- `mock_signal_news` -> `MockSignalNewsCollector`
- `generic_html` -> `GenericHtmlCollector`
- `ilan_gov_tr_api` -> `IlanGovTrApiCollector`
- `rss_feed` -> `RssFeedCollector`
- `json_api` -> `JsonApiCollector`

## ilan.gov.tr Official API Adapter
`IlanGovTrApiCollector` combines multiple official endpoints to improve coverage:
- `Ad/AdsByFilter` (paginated list, may return empty depending on platform filters)
- `AdHomePage/*` feeds (`GetAdsByPublishTime`, `GetAdsFeatured`, `GetLeastPopularAds`, `GetPopularAdsOfToday`)
- `Ad/GetAdSourceAds` source grouped feed
- `AdDetail/GetAdDetail` for detail enrichment

Key configuration options in `source_configs.config_json`:
- `page_size`, `pages`, `sorting`
- `include_ads_by_filter`
- `include_homepage_endpoints`
- `include_ad_source_ads`
- `require_quick_match`, `detail_only_for_match`
- `max_detail_requests`, `max_ads_total`
- optional `prefilter_terms` override

## JSON API Adapter
`JsonApiCollector` fetches a REST endpoint that returns JSON and maps a configurable path to normalized tenders. Suitable for EKAP/KIK-style APIs.

Key configuration in `source_configs.config_json`:
- `api_url` (required): full URL to GET or POST
- `method`: `GET` (default) or `POST`
- `items_path`: dot path to the array of items (e.g. `data.items`, `items`)
- `field_mapping`: map normalized field names to JSON keys (e.g. `{"title": "baslik", "summary": "ozet"}`)
- `max_items`, `timeout_seconds`, optional `headers`, optional `body` for POST

## Generic HTML Adapter
`GenericHtmlCollector` expects selector config in `source_configs.config_json`:
- `list_path`
- `item_selector`
- `title_selector`
- `link_selector`
- optional `summary_selector`

## RSS Feed Adapter
`RssFeedCollector` supports multi-feed ingestion for early signal discovery:
- `feed_urls` (list) or `feed_url` (single URL)
- optional `max_items` (default `60`)
- optional `timeout_seconds` (default `20`)

Supported feed item fields:
- RSS: `title`, `link`, `description`, `guid`, `pubDate`
- Atom: `title`, `link[href]`, `summary`, `id`, `published/updated`

## Reliability Practices
- The runner retries failed collections with backoff.
- Raw source payload is snapshot-saved under `collector/snapshots/`.
- Collector run details are persisted in `collector_runs`.
- Duplicate prevention uses:
  1. `(source_name, external_id)` when available
  2. `dedupe_key` hash
  3. content checksum fallback

## Official vs Signal Handling
- Official records: `official_verified=true`, `signal_found=false`
- News/early signals: `signal_found=true`, `official_verified=false`
- When an existing signal is later found from official source, the system updates verification and logs an event.

## Adding a New Adapter
1. Create `collector/adapters/<name>_collector.py`.
2. Extend `BaseCollector` and implement `collect()`.
3. Return normalized records only (no DB writes in adapter).
4. Register in `collector/factory.py`.
5. Add/update `SourceConfig` with `config_json.adapter`.
6. Add tests for parser and normalization behavior.
