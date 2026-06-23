# EventFlow — Hackathon Submission

## Problem Statement

**Event-Driven Congestion (Planned & Unplanned)**

Political rallies, festivals, sports events, construction, and sudden gatherings create localized traffic breakdowns in Bangalore. Today:

- Event impact is not quantified in advance
- Resource deployment is experience-driven
- There is no post-event learning system

## Our Solution

**EventFlow** uses 8,173 anonymized Astram traffic incidents to:

1. **Forecast** congestion impact, clearance time, and road-closure risk
2. **Recommend** manpower, barricades, diversion corridors, and deployment timelines
3. **Learn** from historical resolution patterns by cause, corridor, zone, and junction

## How It Works

```
Historical CSV → Feature engineering → Random Forest models
                                    ↓
User enters planned event → Forecast API → Resource recommendation engine
                                    ↓
Ops dashboard + map explorer + learning insights
```

## Key Differentiators

| Before | With EventFlow |
|--------|----------------|
| Gut-feel staffing | Data-backed officer + barricade counts |
| Reactive diversions | Pre-planned alternate corridors from history |
| No feedback loop | Junction hotspots and slow-corridor analytics |

## Dataset

- **Source:** Anonymized Astram event data (Bangalore)
- **Records:** 8,173 events
- **Planned:** 467 (construction, public events, processions, VIP movements)
- **Unplanned:** 7,706 (breakdowns, accidents, water logging, etc.)

## Model Performance

| Model | Validation Metric |
|-------|-------------------|
| Impact score | MAE ~6.6 |
| Duration | MAE ~111 min |
| Road closure | Accuracy ~92.6% |

## Demo Flow (3 minutes)

1. **Dashboard** — Total events, planned vs unplanned, top corridors
2. **Event Explorer** — Map filter `public_event`, inspect cricket match near CBD
3. **Event Planner** — Load "Political Rally" demo → forecast + resource plan
4. **Learning Insights** — Slow corridors and recurring junction hotspots

## Tech Stack

- **Backend:** FastAPI, pandas, scikit-learn
- **Frontend:** React, Vite, TypeScript, Tailwind, Leaflet, Recharts
- **Deploy:** Docker + Render Blueprint

## Links

- **Repo:** https://github.com/parampratap-lang/eventflow-congestion
- **Deploy:** https://dashboard.render.com/blueprint/new?repo=https://github.com/parampratap-lang/eventflow-congestion

## Future Work

- Live traffic API integration (Google Maps / city sensors)
- Real-time officer GPS tracking
- Automated post-event outcome logging
- Multi-city model transfer
