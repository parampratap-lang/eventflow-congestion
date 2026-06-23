#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

cd "$ROOT/backend"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/train_models.py

cd "$ROOT/frontend"
npm ci
npm run build

rm -rf "$ROOT/backend/static"
cp -r dist "$ROOT/backend/static"

echo "Build complete. Start with: cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000"
