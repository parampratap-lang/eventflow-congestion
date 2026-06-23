FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends nodejs npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY data/ data/
COPY backend/ backend/
COPY frontend/ frontend/

RUN python backend/scripts/train_models.py \
    && cd frontend && npm ci && npm run build && cp -r dist ../backend/static

WORKDIR /app/backend
ENV PORT=8000
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
