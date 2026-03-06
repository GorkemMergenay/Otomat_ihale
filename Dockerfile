# Backend + collector/classifier/notifier — Render, Railway, Fly.io
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Bağımlılıklar (psycopg2 opsiyonel; PostgreSQL yoksa SQLite kullanın)
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

COPY backend /app/backend
COPY collector /app/collector
COPY classifier /app/classifier
COPY notifier /app/notifier
COPY scripts /app/scripts

ENV PYTHONPATH=/app/backend:/app
WORKDIR /app/backend

# Render: PORT=10000, Railway: PORT at runtime
EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head 2>/dev/null || true && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
