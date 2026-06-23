from __future__ import annotations

import math
from datetime import datetime
from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from app.models.schemas import ForecastRequest, ForecastResponse
from app.services.data_loader import get_aggregates, get_events_df

ARTIFACTS_DIR = Path(__file__).resolve().parents[2] / "artifacts"


@lru_cache(maxsize=1)
def load_models() -> dict:
    path = ARTIFACTS_DIR / "models.pkl"
    if not path.exists():
        raise FileNotFoundError("models.pkl not found. Run train_models.py first.")
    return joblib.load(path)


def _impact_tier(score: float) -> str:
    if score >= 75:
        return "Critical"
    if score >= 55:
        return "High"
    if score >= 35:
        return "Medium"
    return "Low"


def _build_feature_row(req: ForecastRequest, df: pd.DataFrame) -> pd.DataFrame:
    start = pd.Timestamp(req.start_datetime)
    end = pd.Timestamp(req.end_datetime) if req.end_datetime else start + pd.Timedelta(hours=2)
    planned_duration = max((end - start).total_seconds() / 60.0, 15.0)

    corridor = req.corridor or "Non-corridor"
    corridor_counts = df["corridor"].value_counts()
    max_count = corridor_counts.max() or 1
    corridor_density = corridor_counts.get(corridor, 1) / max_count

    row = {
        "event_type": req.event_type,
        "event_cause": req.event_cause,
        "corridor": corridor,
        "zone": req.zone or "unknown",
        "junction": req.junction or "unknown",
        "police_station": req.police_station or "unknown",
        "latitude": req.latitude,
        "longitude": req.longitude,
        "hour_of_day": int(start.hour),
        "day_of_week": int(start.dayofweek),
        "is_weekend": int(start.dayofweek >= 5),
        "corridor_density": float(corridor_density),
        "planned_duration_minutes": float(planned_duration),
    }
    return pd.DataFrame([row])


def count_similar_events(req: ForecastRequest, df: pd.DataFrame) -> int:
    mask = (df["event_cause"] == req.event_cause) & (df["corridor"] == req.corridor)
    return int(mask.sum())


def forecast_event(req: ForecastRequest) -> ForecastResponse:
    models = load_models()
    df = get_events_df()
    X = _build_feature_row(req, df)

    impact = float(models["impact_model"].predict(X)[0])
    duration = float(models["duration_model"].predict(X)[0])
    closure_prob = float(models["closure_model"].predict_proba(X)[0][1])

    # Blend with historical lookup for sparse planned causes
    aggregates = get_aggregates()
    hist = [
        r
        for r in aggregates.get("cause_corridor", [])
        if r.get("event_cause") == req.event_cause and r.get("corridor") == req.corridor
    ]
    if hist:
        duration = 0.6 * duration + 0.4 * float(hist[0].get("median_minutes", duration))

    similar_count = count_similar_events(req, df)
    confidence = min(0.95, 0.45 + similar_count * 0.02)

    impact = float(np.clip(impact, 5, 100))
    duration = float(np.clip(duration, 15, 24 * 60))
    closure_prob = float(np.clip(closure_prob, 0.01, 0.99))

    return ForecastResponse(
        impact_score=round(impact, 1),
        impact_tier=_impact_tier(impact),
        duration_minutes=round(duration, 1),
        closure_probability=round(closure_prob, 3),
        confidence=round(confidence, 2),
        similar_event_count=similar_count,
    )


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))
