# Türkiye Otomat İhale Takip Sistemi (MVP)

Production-oriented MVP to monitor Turkish tender opportunities relevant to vending machines, kiosks, self-service retail, smart cabinets, micro markets, and unattended retail.

## What This MVP Delivers
- Modular source collection with pluggable adapters.
- Normalized tender ingestion with duplicate detection.
- Explainable rule-based classification and scoring.
- Official-vs-signal source truth workflow.
- Notification triggers (email + Telegram abstraction).
- User login/session with signed bearer token.
- FastAPI backend with PostgreSQL + Alembic schema.
- Next.js operational dashboard.
- Dockerized local deployment.
- Seed script with live official source pull and Turkish tender-like baseline records.
- Unit/API/dedupe tests.

## Monorepo Structure
- `backend/` FastAPI app, SQLAlchemy models, migrations, endpoints, scheduler
- `collector/` source adapter framework, parsers, normalizers, runner (ilan.gov.tr, RSS, JSON API, generic HTML)
- `classifier/` rule-based scorer + AI placeholder interface
- `notifier/` notification dispatch and channel senders
- `frontend/` Next.js admin dashboard (genel bakış, ihale listesi sayfalama, detay skor çubukları ve eşleşme gerekçesi, kaynak sağlık rozeti)
- `infra/` Dockerfiles and compose
- `scripts/` operational scripts (`seed_data.py`)
- `tests/` API and scoring tests

## Core Workflow
1. Source run starts (`manual trigger` or scheduler).
2. Adapter returns normalized candidates.
3. Dedup checks (`external_id`, `dedupe_key`, `checksum`).
4. Insert/update tender and write `tender_events`.
5. Classifier computes scores + `match_explanation`.
6. Notification triggers fire with cooldown/idempotency.
7. Dashboard reflects updated pipeline.
8. `%80+` skor eşiği geçişinde e-posta/telegram bildirimi gönderilir.

## Official vs Signal Rule
- Official sources are truth: `official_verified=true`.
- News/press/institution early finds: `signal_found=true`, `official_verified=false`.
- Later official match updates verification and records timeline event.

## Status Pipeline
- `new`
- `auto_flagged`
- `under_review`
- `relevant`
- `high_priority`
- `proposal_candidate`
- `ignored`
- `archived`

## Gereksinimler (yerel çalıştırma)
- **Python 3.9+** (proje Python 3.9 uyumlu hale getirildi)
- **Node.js 18+** ve npm (frontend için)
- Veritabanı: **PostgreSQL** (Docker ile) veya **SQLite** (`.env` içinde `DATABASE_URL=sqlite:///dev.db`)

## Hızlı başlangıç (yerel, Docker yok)

1. **.env** — Proje kökünde `.env` yoksa: `cp .env.example .env`  
   - PostgreSQL kullanmayacaksanız: `.env` içinde `DATABASE_URL=sqlite:///dev.db` olsun.

2. **Backend** (ayrı terminal):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r backend/requirements.txt   # PostgreSQL yoksa psycopg2-binary hatası alırsanız: pip install (diğer paketler)
   PYTHONPATH=backend:. python -m alembic -c backend/alembic.ini upgrade head   # backend/ içinden çalıştırıyorsanız: cd backend && DATABASE_URL=sqlite:///../dev.db python -m alembic upgrade head
   PYTHONPATH=backend:. python scripts/seed_data.py
   ./scripts/run_backend.sh
   ```
   Veya doğrudan: `PYTHONPATH=backend:. uvicorn app.main:app --reload --app-dir backend`  
   Backend: **http://localhost:8000**

3. **Frontend** (ayrı terminal):
   ```bash
   ./scripts/run_frontend.sh
   ```
   Veya: `cd frontend && npm install && npm run dev`  
   Frontend: **http://localhost:3000**

4. **Giriş:** `admin@otomat.local` / `Otomat123!`

## Backend Setup (Local) — detay

```bash
cd /path/to/project
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cp .env.example .env
export PYTHONPATH=backend:.
cd backend && DATABASE_URL=sqlite:///../dev.db python -m alembic upgrade head && cd ..
PYTHONPATH=backend:. python scripts/seed_data.py
uvicorn app.main:app --reload --app-dir backend
```

Backend URL: `http://localhost:8000`

## Frontend Setup (Local)

```bash
cd frontend
npm install
npm run dev
```

Frontend URL: `http://localhost:3000`

Not:
- Frontend API ayarı için `NEXT_PUBLIC_API_BASE_URL` kullanılır.
- Docker içinde daha stabil bağlantı için `NEXT_INTERNAL_API_BASE_URL` değerini servis ağına göre verin (ör: `http://backend:8000/api/v1`).
- Frontend middleware giriş cookie’si (`otomat_auth_token`) olmadan `/login` sayfasına yönlendirir.

## Email Alert Setup (`%80+`)
`.env` içinde en az şu ayarları girin:
- `EMAIL_ENABLED=true`
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`
- `EMAIL_FROM`
- `NOTIFICATION_EMAIL_RECIPIENTS=...` (boş bırakılırsa aktif admin/analyst kullanıcı e-postaları kullanılır)
- `NOTIFICATION_SCORE_THRESHOLD=80`

## Docker Setup

```bash
cd /Users/gorkemmergenay/Documents/New project 2/infra
docker compose up --build
```

Services:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- PostgreSQL: `localhost:5432`

## Seed Data
Run:

```bash
cd /Users/gorkemmergenay/Documents/New project 2
PYTHONPATH=/Users/gorkemmergenay/Documents/New\ project\ 2/backend:/Users/gorkemmergenay/Documents/New\ project\ 2 python scripts/seed_data.py
```

Seeds:
- users
- source configs: `ilan.gov.tr` resmi API, Google/Bing News RSS (otomat, kiosk, mikro market, belediye ihaleleri vb.), EKAP/KIK JSON API şablonu, generic HTML şablonları (EKAP, DHMİ, TCDD, İBB, Ankara, KIK, üniversite, sağlık)
- keyword rules (direct/related/commercial/institution/negative)
- collector runs that ingest real official listings when available

Varsayılan giriş:
- `admin@otomat.local` / `Otomat123!`
- `analyst@otomat.local` / `Otomat123!`
- `viewer@otomat.local` / `Otomat123!`

## API Surface (MVP)
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `GET /api/v1/health/live`
- `GET /api/v1/health/ready`
- `GET /api/v1/dashboard/overview`
- `GET /api/v1/tenders`
- `GET /api/v1/tenders/{id}`
- `GET /api/v1/tenders/{id}/events`
- `PATCH /api/v1/tenders/{id}` (admin)
- `POST /api/v1/tenders/{id}/reprocess` (admin)
- `GET /api/v1/sources`
- `POST /api/v1/sources` (admin)
- `PATCH /api/v1/sources/{id}` (admin)
- `DELETE /api/v1/sources/{id}` (admin)
- `POST /api/v1/sources/{id}/trigger-crawl` (admin)
- `GET /api/v1/keyword-rules`
- `POST /api/v1/keyword-rules` (admin)
- `PATCH /api/v1/keyword-rules/{id}` (admin)
- `DELETE /api/v1/keyword-rules/{id}` (admin)
- `GET /api/v1/notifications`
- `POST /api/v1/actions/manual-crawl` (admin)
- `POST /api/v1/actions/reprocess` (admin)

## Testing

```bash
cd /Users/gorkemmergenay/Documents/New project 2
pytest
```

Included tests:
- classifier scoring behavior
- API smoke tests
- duplicate key/checksum logic
- scoring service update behavior

## Documentation
- `architecture.md`
- `scoring_rules.md`
- `source_adapter_guide.md`

## Notes and Risks
- `ilan.gov.tr` adapter is live and uses multiple official endpoints; endpoint behaviors can change over time.
- RSS araştırma kaynakları erken-sinyal amaçlıdır; resmi doğrulama için resmi kaynak eşlemesi şarttır.
- Real production hardening should add per-source parser contracts, anti-bot handling, legal checks, and richer observability.
- AI classifier integration is intentionally a placeholder (`AIClassifierPlaceholder`) behind interface boundaries.
