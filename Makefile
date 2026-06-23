.PHONY: install train backend frontend build dev

install:
	cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
	cd frontend && npm install

train:
	cd backend && . .venv/bin/activate && python scripts/train_models.py

backend:
	cd backend && . .venv/bin/activate && uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

build:
	cd backend && . .venv/bin/activate && python scripts/train_models.py
	cd frontend && npm run build
	rm -rf backend/static && cp -r frontend/dist backend/static

dev:
	@echo "Run 'make backend' and 'make frontend' in separate terminals"
