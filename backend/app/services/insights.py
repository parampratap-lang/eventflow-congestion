from __future__ import annotations

import pandas as pd

from app.models.schemas import DashboardStats, EventSummary, InsightsResponse
from app.services.data_loader import get_aggregates, get_events_df, row_to_summary


def get_dashboard_stats() -> DashboardStats:
    df = get_events_df()
    top_corridors = (
        df["corridor"]
        .value_counts()
        .head(8)
        .reset_index()
        .rename(columns={"index": "corridor", "corridor": "count"})
    )
    top_corridors.columns = ["corridor", "count"]

    cause_breakdown = (
        df["event_cause"]
        .value_counts()
        .head(10)
        .reset_index()
        .rename(columns={"index": "cause", "event_cause": "count"})
    )
    cause_breakdown.columns = ["cause", "count"]

    return DashboardStats(
        total_events=len(df),
        planned_events=int((df["event_type"] == "planned").sum()),
        unplanned_events=int((df["event_type"] == "unplanned").sum()),
        active_events=int((df["status"] == "active").sum()),
        avg_resolution_minutes=round(float(df["duration_minutes"].median()), 1),
        top_corridors=top_corridors.to_dict(orient="records"),
        planned_vs_unplanned={
            "planned": int((df["event_type"] == "planned").sum()),
            "unplanned": int((df["event_type"] == "unplanned").sum()),
        },
        cause_breakdown=cause_breakdown.to_dict(orient="records"),
    )


def get_insights() -> InsightsResponse:
    aggregates = get_aggregates()
    df = get_events_df()
    overall = float(aggregates.get("overall_median_duration", df["duration_minutes"].median()))

    notes: list[str] = []
    for row in aggregates.get("corridor_duration", [])[:5]:
        median = float(row.get("median_minutes", overall))
        if median > overall * 1.5:
            ratio = median / overall
            notes.append(
                f"{row['corridor']} resolves incidents {ratio:.1f}x slower than city median — pre-deploy heavier resources."
            )

    for row in aggregates.get("junction_hotspots", [])[:3]:
        notes.append(
            f"Junction {row['junction']}: {int(row['event_count'])} events, "
            f"median {float(row['median_duration']):.0f} min — recurring hotspot."
        )

    return InsightsResponse(
        cause_duration=aggregates.get("cause_duration", []),
        corridor_duration=aggregates.get("corridor_duration", []),
        zone_stats=aggregates.get("zone_stats", []),
        junction_hotspots=aggregates.get("junction_hotspots", []),
        training_metrics=aggregates.get("training_metrics", {}),
        overall_median_duration=overall,
        learning_notes=notes,
    )


def find_similar_events(event_id: str, limit: int = 5) -> list[EventSummary]:
    df = get_events_df()
    match = df[df["id"] == event_id]
    if match.empty:
        return []
    row = match.iloc[0]
    candidates = df[df["id"] != event_id].copy()
    candidates["score"] = 0
    candidates.loc[candidates["event_cause"] == row["event_cause"], "score"] += 3
    candidates.loc[candidates["corridor"] == row["corridor"], "score"] += 2
    if pd.notna(row.get("zone")):
        candidates.loc[candidates["zone"] == row["zone"], "score"] += 1
    top = candidates.sort_values("score", ascending=False).head(limit)
    return [EventSummary(**row_to_summary(r)) for _, r in top.iterrows()]
