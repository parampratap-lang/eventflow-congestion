# EventFlow — Event-Driven Congestion Intelligence Platform

Forecast event-related traffic impact and recommend optimal manpower, barricading, and diversion plans using historical Bangalore Astram traffic data.

## Problem

Political rallies, festivals, sports events, construction, and sudden gatherings create localized traffic breakdowns. Today, event impact is rarely quantified in advance, resource deployment is experience-driven, and there is no structured post-event learning loop.

**EventFlow** addresses this by combining historical incident data with ML forecasting and rule-based operations recommendations.

## Live Demo

**GitHub:** https://github.com/parampratap-lang/eventflow-congestion

**Deploy on Render (one-click):** https://dashboard.render.com/blueprint/new?repo=https://github.com/parampratap-lang/eventflow-congestion

After connecting your Render account and clicking **Deploy Blueprint**, the app will be available at your Render service URL (e.g. `https://eventflow.onrender.com`).

## Features

- **Impact Forecasting** — Predict congestion score, clearance duration, and road-closure probability for planned or unplanned events
- **Resource Recommendations** — Officer count, barricades, diversion corridors, deployment timeline, and ops checklist
- **Event Explorer** — Interactive map of 8,000+ historical incidents with filters and similar-event lookup
- **Learning Insights** — Post-event analytics by cause, corridor, zone, and junction hotspots

## Dataset

Anonymized Astram traffic event data for Bangalore (~8,173 records):

- 467 planned events (construction, public events, processions, VIP movements)
- 7,706 unplanned events (breakdowns, accidents, water logging, etc.)

Stored at [`data/astram_events.csv`](data/astram_events.csv).

## Hackathon Submission

See [HACKATHON.md](HACKATHON.md) for the full problem statement, demo script, and judge-facing summary.

## Architecture

```
React (Vite) UI  →  FastAPI  →  sklearn models + aggregates
                         ↓
                  Astram CSV (parquet cache)
```

**ML models (validation metrics):**

| Model | Metric |
|-------|--------|
| Impact score | MAE ~6.6 |
| Duration | MAE ~111 min |
| Road closure | Accuracy ~92.6% |

## Local Development

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/train_models.py
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend dev server proxies `/api` to `http://localhost:8000`.

### Production build (single service)

```bash
cd frontend && npm run build
cp -r dist ../backend/static
cd ../backend && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/stats` | Dashboard KPIs |
| GET | `/api/events` | Paginated events with filters |
| GET | `/api/events/{id}` | Event detail + similar events |
| POST | `/api/forecast` | Impact forecast |
| POST | `/api/recommend` | Resource deployment plan |
| GET | `/api/insights` | Learning aggregates |
| GET | `/api/reference` | Dropdown reference data |

## Deploy on Render

1. Push this repo to GitHub
2. In [Render Dashboard](https://dashboard.render.com), click **New → Blueprint**
3. Connect the GitHub repo — Render reads [`render.yaml`](render.yaml)
4. Deploy — the web service builds frontend + backend and serves both from one URL

Environment variables (optional):

- `CORS_ORIGINS` — comma-separated origins for local dev cross-origin requests

## Hackathon Demo Script (3 min)

1. **Dashboard** — Show 8K+ events, planned vs unplanned split, top corridors
2. **Event Explorer** — Filter `public_event`, click cricket match near CBD
3. **Event Planner** — Load "Political Rally" demo → High impact, officers, barricades, diversions
4. **Learning Insights** — Show slow corridors and recurring junction hotspots

## Team / License

Built for hackathon demonstration. Dataset is anonymized; do not commit real credentials.
