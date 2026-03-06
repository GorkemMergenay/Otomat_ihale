#!/usr/bin/env bash
# Backend'i proje kökünden çalıştırır. Python 3.10+ ve .env gerekir.
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! python3 -c 'import sys; exit(0 if sys.version_info >= (3, 9) else 1)' 2>/dev/null; then
  echo "Hata: Bu proje Python 3.9 veya üzeri gerektirir. Mevcut: $(python3 --version 2>/dev/null || echo 'python3 bulunamadı')"
  exit 1
fi

if [ ! -f "$ROOT/.env" ]; then
  cp "$ROOT/.env.example" "$ROOT/.env"
  echo ".env dosyası oluşturuldu. İsteğe bağlı: DATABASE_URL ve diğer değerleri düzenleyin."
fi

# SQLite ile yerel çalıştırma (PostgreSQL yoksa)
if grep -q "postgresql" "$ROOT/.env" 2>/dev/null; then
  echo "DATABASE_URL .env içinde PostgreSQL olarak ayarlı. PostgreSQL çalışıyor olmalı."
else
  echo "DATABASE_URL SQLite kullanıyor (yerel dev.db)."
fi

export PYTHONPATH="$ROOT/backend:$ROOT"

# Migrasyon (ilk kurulumda)
if [ ! -f "$ROOT/dev.db" ] && grep -q "sqlite" "$ROOT/.env" 2>/dev/null; then
  echo "Veritabanı migrasyonu çalıştırılıyor..."
  (cd "$ROOT/backend" && PYTHONPATH="$ROOT/backend" DATABASE_URL="${DATABASE_URL:-sqlite:///../dev.db}" python -m alembic upgrade head)
  echo "Seed verisi yükleniyor (isteğe bağlı: PYTHONPATH=$ROOT/backend:$ROOT python $ROOT/scripts/seed_data.py)"
fi

echo "Backend başlatılıyor: http://localhost:8000"
exec python3 -m uvicorn app.main:app --reload --app-dir "$ROOT/backend" --host 0.0.0.0 --port 8000
