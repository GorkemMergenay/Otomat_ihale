#!/usr/bin/env bash
# Backend + (isteğe bağlı) frontend başlatır.
# Kullanım: ./scripts/start_all.sh   veya  ./scripts/start_all.sh --frontend
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# .env
if [ ! -f "$ROOT/.env" ]; then
  cp "$ROOT/.env.example" "$ROOT/.env"
  echo ".env oluşturuldu."
fi

# Backend (Python 3.9+)
export PYTHONPATH="$ROOT/backend:$ROOT"
echo "Backend başlatılıyor: http://localhost:8000"
.venv/bin/uvicorn app.main:app --reload --app-dir "$ROOT/backend" --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

if [ "$1" = "--frontend" ]; then
  if ! command -v npm >/dev/null 2>&1; then
    echo "Uyarı: npm bulunamadı. Frontend atlanıyor. Node kurun: https://nodejs.org"
  else
    cd "$ROOT/frontend"
    [ -d node_modules ] || npm install
    echo "Frontend başlatılıyor: http://localhost:3000"
    npm run dev &
    echo "Backend PID: $BACKEND_PID | Durdurmak için: kill $BACKEND_PID ve frontend process"
  fi
fi

wait $BACKEND_PID 2>/dev/null || true
