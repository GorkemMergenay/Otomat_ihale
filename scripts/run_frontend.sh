#!/usr/bin/env bash
# Frontend'i çalıştırır. Node.js 18+ ve npm gerekir.
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/frontend"

if ! command -v npm >/dev/null 2>&1; then
  echo "Hata: npm bulunamadı. Node.js kurun: https://nodejs.org/  veya  brew install node"
  exit 1
fi

[ -d node_modules ] || npm install
echo "Frontend başlatılıyor: http://localhost:3000"
exec npm run dev
