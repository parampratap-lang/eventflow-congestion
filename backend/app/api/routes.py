from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import (
    EventDetail,
    ForecastRequest,
    ForecastResponse,
    InsightsResponse,
    PaginatedEvents,
    RecommendRequest,
    ReferenceData,
    ResourceRecommendation,
    DashboardStats,
)
from app.services.data_loader import filter_events, get_events_df, row_to_summary
from app.services.forecaster import forecast_event
from app.services.insights import find_similar_events, get_dashboard_stats, get_insights
from app.services.recommender import recommend_resources

router = APIRouter(prefix="/api")


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "eventflow"}


@router.get("/stats", response_model=DashboardStats)
def stats() -> DashboardStats:
    return get_dashboard_stats()


@router.get("/reference", response_model=ReferenceData)
def reference() -> ReferenceData:
    df = get_events_df()
    return ReferenceData(
        corridors=sorted(df["corridor"].dropna().unique().tolist()),
        zones=sorted([z for z in df["zone"].dropna().unique().tolist() if z != "unknown"]),
        causes=sorted(df["event_cause"].dropna().unique().tolist()),
        junctions=sorted([j for j in df["junction"].dropna().unique().tolist() if j != "unknown"])[:100],
        event_types=["planned", "unplanned"],
    )


@router.get("/events", response_model=PaginatedEvents)
def list_events(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    event_type: str | None = None,
    event_cause: str | None = None,
    corridor: str | None = None,
    zone: str | None = None,
    status: str | None = None,
) -> PaginatedEvents:
    df = filter_events(get_events_df(), event_type, event_cause, corridor, zone, status)
    total = len(df)
    start = (page - 1) * page_size
    end = start + page_size
    page_df = df.iloc[start:end]
    items = [row_to_summary(row) for _, row in page_df.iterrows()]
    return PaginatedEvents(total=total, page=page, page_size=page_size, items=items)


@router.get("/events/{event_id}", response_model=EventDetail)
def get_event(event_id: str) -> EventDetail:
    df = get_events_df()
    match = df[df["id"] == event_id]
    if match.empty:
        raise HTTPException(status_code=404, detail="Event not found")
    summary = row_to_summary(match.iloc[0])
    similar = find_similar_events(event_id)
    return EventDetail(**summary, similar_events=similar)


@router.post("/forecast", response_model=ForecastResponse)
def forecast(req: ForecastRequest) -> ForecastResponse:
    return forecast_event(req)


@router.post("/recommend", response_model=ResourceRecommendation)
def recommend(req: RecommendRequest) -> ResourceRecommendation:
    forecast = req.forecast_result or forecast_event(req.forecast)
    return recommend_resources(req.forecast, forecast)


@router.get("/insights", response_model=InsightsResponse)
def insights() -> InsightsResponse:
    return get_insights()
