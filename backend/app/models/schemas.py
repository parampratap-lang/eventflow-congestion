from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ForecastRequest(BaseModel):
    event_type: Literal["planned", "unplanned"] = "planned"
    event_cause: str
    latitude: float = Field(..., ge=12.5, le=13.5)
    longitude: float = Field(..., ge=77.0, le=78.0)
    corridor: str = "Non-corridor"
    zone: str = "unknown"
    junction: str = "unknown"
    police_station: str = "unknown"
    start_datetime: datetime
    end_datetime: datetime | None = None
    description: str | None = None


class ForecastResponse(BaseModel):
    impact_score: float
    impact_tier: Literal["Low", "Medium", "High", "Critical"]
    duration_minutes: float
    closure_probability: float
    confidence: float
    similar_event_count: int


class DiversionRoute(BaseModel):
    corridor: str
    reason: str
    distance_km: float


class ResourceRecommendation(BaseModel):
    manpower_officers: int
    barricades: int
    diversions: list[DiversionRoute]
    deploy_minutes_before: int
    deployment_timeline: list[str]
    checklist: list[str]
    rationale: str


class RecommendRequest(BaseModel):
    forecast: ForecastRequest
    forecast_result: ForecastResponse | None = None


class EventSummary(BaseModel):
    id: str
    event_type: str
    event_cause: str
    latitude: float
    longitude: float
    address: str | None = None
    corridor: str
    zone: str
    junction: str
    police_station: str
    priority: str
    status: str
    requires_road_closure: bool
    start_datetime: str | None = None
    end_datetime: str | None = None
    description: str | None = None
    impact_score: float | None = None
    duration_minutes: float | None = None


class EventDetail(EventSummary):
    similar_events: list[EventSummary] = []


class PaginatedEvents(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[EventSummary]


class DashboardStats(BaseModel):
    total_events: int
    planned_events: int
    unplanned_events: int
    active_events: int
    avg_resolution_minutes: float
    top_corridors: list[dict]
    planned_vs_unplanned: dict[str, int]
    cause_breakdown: list[dict]


class ReferenceData(BaseModel):
    corridors: list[str]
    zones: list[str]
    causes: list[str]
    junctions: list[str]
    event_types: list[str]


class InsightsResponse(BaseModel):
    cause_duration: list[dict]
    corridor_duration: list[dict]
    zone_stats: list[dict]
    junction_hotspots: list[dict]
    training_metrics: dict
    overall_median_duration: float
    learning_notes: list[str]
