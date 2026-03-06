#!/usr/bin/env bash
# Port 8000'deki backend sürecini durdurup yeniden başlatır.
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "Port 8000 kullanılan süreçler kapatılıyor..."
for pid in $(lsof -i :8000 -t 2>/dev/null || true); do
  kill "$pid" 2>/dev/null || true
done
sleep 2
# Zorla kapat
for pid in $(lsof -i :8000 -t 2>/dev/null || true); do
  kill -9 "$pid" 2>/dev/null || true
done
sleep 1

export PYTHONPATH="$ROOT/backend:$ROOT"
echo "Backend başlatılıyor: http://localhost:8000"
echo "Giriş: admin@otomat.local / Otomat123!"
exec .venv/bin/uvicorn app.main:app --reload --app-dir "$ROOT/backend" --host 0.0.0.0 --port 8000
