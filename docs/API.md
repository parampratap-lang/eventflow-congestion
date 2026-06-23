# EventFlow API Reference

Base URL: `/api`

## Health

```
GET /api/health
```

Response:
```json
{ "status": "ok", "service": "eventflow" }
```

## Dashboard Stats

```
GET /api/stats
```

Returns KPIs: total events, planned/unplanned counts, active events, median resolution, top corridors, cause breakdown.

## Events

```
GET /api/events?page=1&page_size=50&event_type=planned&corridor=ORR%20East%201
```

Query params: `page`, `page_size`, `event_type`, `event_cause`, `corridor`, `zone`, `status`

```
GET /api/events/{id}
```

Returns event detail with `similar_events` array.

## Forecast

```
POST /api/forecast
Content-Type: application/json
```

```json
{
  "event_type": "planned",
  "event_cause": "procession",
  "latitude": 12.9716,
  "longitude": 77.6412,
  "corridor": "ORR East 1",
  "zone": "East Zone 1",
  "junction": "unknown",
  "police_station": "HSR Layout",
  "start_datetime": "2025-06-24T10:00:00Z",
  "end_datetime": "2025-06-24T14:00:00Z",
  "description": "Political procession"
}
```

Response:
```json
{
  "impact_score": 58.2,
  "impact_tier": "High",
  "duration_minutes": 95.0,
  "closure_probability": 0.12,
  "confidence": 0.67,
  "similar_event_count": 8
}
```

## Recommend

```
POST /api/recommend
```

```json
{
  "forecast": { "...ForecastRequest..." },
  "forecast_result": { "...optional ForecastResponse..." }
}
```

Response includes `manpower_officers`, `barricades`, `diversions`, `deploy_minutes_before`, `deployment_timeline`, `checklist`, `rationale`.

## Insights

```
GET /api/insights
```

Returns cause/corridor duration stats, zone stats, junction hotspots, training metrics, and automated learning notes.

## Reference Data

```
GET /api/reference
```

Returns dropdown values: corridors, zones, causes, junctions, event_types.
