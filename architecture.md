# Türkiye Otomat İhale Takip Sistemi - Technical Architecture

## 1. Final Technical Architecture

The MVP is implemented as a modular monorepo with clear service boundaries:

- `backend/` FastAPI application for REST API, business workflow, role-based access control, signed token auth, persistence, scheduler orchestration, and admin operations.
- `collector/` Pluggable source collection framework. Adapters fetch source data, parsers extract content, normalizers output canonical tender payloads.
- `classifier/` Rule-based relevance/classification and explainable scoring engine with interface ready for AI model integration.
- `notifier/` Channel abstraction for outbound notifications (email + Telegram), with de-duplication and cool-down checks.
- `frontend/` Next.js admin dashboard for team operations (overview, list/detail, source/rule management, notification log).
- `infra/` Deployment artifacts (`docker-compose`, Dockerfiles, runtime env defaults).

### Data Flow
1. Source scheduler triggers collector runs (manual trigger + periodic).
2. Collector adapters produce normalized tender candidate records.
3. Duplicate detection checks `external_id`, canonical URL hash, normalized title + institution + date signature.
4. Classifier computes label and score breakdown with structured reasoning trace.
5. Tender is inserted/updated in PostgreSQL with audit history (`tender_events`).
6. Notification rules evaluate state transitions and trigger channel senders.
7. Frontend reads API for operations, triage, and status pipeline actions.

### Truth Hierarchy
- Official portals: source of truth (`official_verified=true`).
- News/press/institution-only discoveries: early signals (`signal_found=true`, `official_verified=false`) until official linkage is found.

### Auditability Design
Each flagged tender stores:
- `classification_label`
- score breakdown (`relevance_score`, `commercial_score`, `technical_score`, `total_score`)
- `match_explanation` (JSON reason trace: matched keyword, weight, field, fuzzy normalization, negative penalties, source trust effect)
- event timeline in `tender_events`

## 2. Folder Structure

```text
.
├── backend/
│   ├── alembic/
│   ├── app/
│   │   ├── api/api_v1/endpoints/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── utils/
│   │   └── workers/
│   ├── alembic.ini
│   └── requirements.txt
├── collector/
│   ├── adapters/
│   ├── normalizers/
│   ├── parsers/
│   └── tests/
├── classifier/
│   └── tests/
├── notifier/
│   └── channels/
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── styles/
│   ├── package.json
│   └── tsconfig.json
├── infra/
│   ├── docker-compose.yml
│   ├── backend.Dockerfile
│   └── frontend.Dockerfile
├── scripts/
├── tests/
├── README.md
├── .env.example
├── architecture.md
├── scoring_rules.md
└── source_adapter_guide.md
```

## 3. Database Schema Summary

Core entities:

1. `tenders`
- Stores canonical tender metadata, scores, classification, truth status (`official_verified`, `signal_found`), status pipeline, ownership, and notes.
- Includes `match_explanation` JSON for explainability and audit.
- Includes `dedupe_key` and indexed fields for search/sort/filter.

2. `tender_documents`
- Linked document metadata (type/url/local copy/checksum/parsed text).

3. `tender_events`
- Immutable timeline of system/user actions (ingestion, status change, score update, verification update, notification dispatch).

4. `source_configs`
- Runtime source controls (active toggle, schedule frequency, parser config, adapter type, last health signals).

5. `keyword_rules`
- Admin-managed weighted matching rules (positive/negative, category, matching type, field hints).

6. `notifications`
- Delivery log with channel, recipient, type, payload, status, and idempotency key.

7. `users`
- Internal users with role-based capability gate (admin/analyst/viewer).

Additional support entity:
- `collector_runs` for source run observability (status, errors, item count, snapshot location).

## 4. Execution Roadmap

1. Backend foundation: config, logging, DB models, Alembic, API skeleton, RBAC-ready dependencies.
2. Collector framework: interface, source adapters (`ilan.gov.tr`, `rss_feed`, `generic_html`), normalization, dedupe checks, run logs.
3. Classifier/scoring: weighted keyword engine + fuzzy normalization + negative keywords + explanation trace; AI placeholder interface.
4. Notifications: event-driven trigger evaluator with email/Telegram senders + cooldown/de-dup.
5. Frontend: Next.js operational dashboard (overview/list/detail/sources/keywords/notifications).
6. Infra & docs: Docker Compose, env templates, setup docs, adapter guide, scoring guide.
7. Tests & seed: classifier/scoring tests, API smoke tests, dedupe tests, realistic Turkish sample seed data.
