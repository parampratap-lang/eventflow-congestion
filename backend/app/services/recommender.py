from __future__ import annotations

from app.models.schemas import DiversionRoute, ForecastRequest, ForecastResponse, ResourceRecommendation
from app.services.data_loader import get_aggregates
from app.services.forecaster import forecast_event, haversine_km


def _base_manpower(tier: str, corridor_events: int) -> int:
    base = {"Low": 3, "Medium": 6, "High": 12, "Critical": 20}.get(tier, 6)
    return int(base + min(corridor_events // 200, 5))


def _barricades(closure_prob: float, cause: str, tier: str) -> int:
    if closure_prob < 0.3 and cause not in {"procession", "vip_movement", "protest"}:
        return 0
    base = {"Low": 4, "Medium": 6, "High": 8, "Critical": 12}.get(tier, 6)
    if cause in {"procession", "vip_movement"}:
        base += 2
    return base


def _deploy_window(cause: str) -> int:
    if cause in {"public_event", "vip_movement", "procession", "protest"}:
        return 90
    if cause == "construction":
        return 30
    return 45


def _diversions(req: ForecastRequest, aggregates: dict) -> list[DiversionRoute]:
    corridors = aggregates.get("corridor_coords", [])
    if not corridors:
        return []

    scored = []
    for c in corridors:
        name = c.get("corridor", "")
        if not name or name == req.corridor:
            continue
        events = int(c.get("events", 0))
        dist = haversine_km(req.latitude, req.longitude, float(c["lat"]), float(c["lng"]))
        if dist > 8:
            continue
        score = events / max(dist, 0.5)
        scored.append((score, name, dist, events))

    scored.sort(key=lambda x: x[0])
    routes: list[DiversionRoute] = []
    for _, name, dist, events in scored[:2]:
        routes.append(
            DiversionRoute(
                corridor=name,
                distance_km=round(dist, 1),
                reason=f"Lower incident density ({events} historical events, {dist:.1f} km away)",
            )
        )
    return routes


def _checklist(req: ForecastRequest, forecast: ForecastResponse) -> list[str]:
    items = [
        "Brief traffic police team and assign sector leads",
        "Verify ambulance and tow truck standby contacts",
        "Update public advisory on social media 2 hours before start",
    ]
    if forecast.closure_probability >= 0.4:
        items.append("Pre-position barricades and signage at closure entry points")
    if req.event_cause in {"public_event", "procession"}:
        items.append("Coordinate with event organizer for crowd dispersal routes")
    if req.event_cause == "construction":
        items.append("Confirm lane closure permits and contractor on-site liaison")
    if forecast.impact_tier in {"High", "Critical"}:
        items.append("Enable corridor-level signal timing override at T-30")
    return items


def recommend_resources(req: ForecastRequest, forecast: ForecastResponse | None = None) -> ResourceRecommendation:
    if forecast is None:
        forecast = forecast_event(req)

    aggregates = get_aggregates()
    corridor_stats = next(
        (r for r in aggregates.get("corridor_duration", []) if r.get("corridor") == req.corridor),
        None,
    )
    corridor_events = int(corridor_stats.get("event_count", 0)) if corridor_stats else 0

    officers = _base_manpower(forecast.impact_tier, corridor_events)
    barricades = _barricades(forecast.closure_probability, req.event_cause, forecast.impact_tier)
    deploy_before = _deploy_window(req.event_cause)
    diversions = _diversions(req, aggregates)

    timeline = [
        f"T-{deploy_before} min: Deploy officers and equipment to {req.corridor}",
        f"T-{max(deploy_before - 30, 15)} min: Activate diversion signage",
        "T-0: Event start — monitor junction flow every 15 minutes",
        f"T+{int(forecast.duration_minutes)} min: Planned stand-down window",
    ]

    rationale = (
        f"Based on {forecast.similar_event_count} similar historical events, "
        f"expected impact is {forecast.impact_tier} ({forecast.impact_score}/100) "
        f"with ~{forecast.duration_minutes:.0f} min clearance time."
    )

    return ResourceRecommendation(
        manpower_officers=officers,
        barricades=barricades,
        diversions=diversions,
        deploy_minutes_before=deploy_before,
        deployment_timeline=timeline,
        checklist=_checklist(req, forecast),
        rationale=rationale,
    )
