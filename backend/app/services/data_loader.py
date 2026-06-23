from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_DIR = ROOT / "artifacts"
DATA_PATH = ROOT.parent / "data" / "astram_events.csv"


@lru_cache(maxsize=1)
def get_events_df() -> pd.DataFrame:
    parquet_path = ARTIFACTS_DIR / "processed_events.parquet"
    if parquet_path.exists():
        return pd.read_parquet(parquet_path)

    # Fallback: load raw CSV with minimal cleaning
    df = pd.read_csv(DATA_PATH, encoding="utf-8-sig", low_memory=False)
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    return df


@lru_cache(maxsize=1)
def get_aggregates() -> dict:
    path = ARTIFACTS_DIR / "aggregates.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def row_to_summary(row: pd.Series) -> dict:
    def dt_str(val) -> str | None:
        if pd.isna(val):
            return None
        return pd.Timestamp(val).isoformat()

    return {
        "id": str(row["id"]),
        "event_type": str(row.get("event_type", "unknown")),
        "event_cause": str(row.get("event_cause", "unknown")),
        "latitude": float(row["latitude"]) if pd.notna(row.get("latitude")) else 0.0,
        "longitude": float(row["longitude"]) if pd.notna(row.get("longitude")) else 0.0,
        "address": str(row["address"]) if pd.notna(row.get("address")) else None,
        "corridor": str(row.get("corridor", "unknown")),
        "zone": str(row.get("zone", "unknown")),
        "junction": str(row.get("junction", "unknown")),
        "police_station": str(row.get("police_station", "unknown")),
        "priority": str(row.get("priority", "Low")),
        "status": str(row.get("status", "unknown")),
        "requires_road_closure": bool(row.get("requires_road_closure", False)),
        "start_datetime": dt_str(row.get("start_datetime")),
        "end_datetime": dt_str(row.get("end_datetime")),
        "description": str(row["description"]) if pd.notna(row.get("description")) else None,
        "impact_score": float(row["impact_score"]) if pd.notna(row.get("impact_score")) else None,
        "duration_minutes": float(row["duration_minutes"]) if pd.notna(row.get("duration_minutes")) else None,
    }


def filter_events(
    df: pd.DataFrame,
    event_type: str | None = None,
    event_cause: str | None = None,
    corridor: str | None = None,
    zone: str | None = None,
    status: str | None = None,
) -> pd.DataFrame:
    out = df.copy()
    if event_type:
        out = out[out["event_type"] == event_type]
    if event_cause:
        out = out[out["event_cause"] == event_cause]
    if corridor:
        out = out[out["corridor"] == corridor]
    if zone:
        out = out[out["zone"] == zone]
    if status:
        out = out[out["status"] == status]
    return out
