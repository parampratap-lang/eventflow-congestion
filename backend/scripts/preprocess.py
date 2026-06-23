"""Clean Astram CSV and derive ML features/targets."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "astram_events.csv"
ARTIFACTS_DIR = Path(__file__).resolve().parents[1] / "artifacts"
PROCESSED_PATH = ARTIFACTS_DIR / "processed_events.parquet"

PRIORITY_WEIGHT = {"Low": 1.0, "Medium": 2.0, "High": 3.0, "Critical": 4.0}
MEDIAN_DURATION_BY_CAUSE: dict[str, float] = {}


def _parse_datetime(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, utc=True, errors="coerce")


def _to_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return False
    return str(value).strip().lower() in {"true", "1", "yes"}


def _duration_minutes(row: pd.Series) -> float | None:
    start = row["start_datetime"]
    if pd.isna(start):
        return None

    for col in ("closed_datetime", "resolved_datetime", "end_datetime"):
        end = row.get(col)
        if pd.notna(end) and end > start:
            return max((end - start).total_seconds() / 60.0, 5.0)
    return None


def _corridor_density(df: pd.DataFrame) -> pd.Series:
    counts = df["corridor"].fillna("Non-corridor").value_counts()
    max_count = counts.max() or 1
    return df["corridor"].fillna("Non-corridor").map(lambda c: counts.get(c, 1) / max_count)


def compute_impact_score(row: pd.Series, corridor_density: float) -> float:
    priority = PRIORITY_WEIGHT.get(str(row.get("priority", "Low")), 1.0)
    closure = 1.5 if _to_bool(row.get("requires_road_closure")) else 1.0
    duration = row.get("duration_minutes") or 60.0
    duration_factor = min(duration / 120.0, 3.0)
    planned_boost = 1.2 if str(row.get("event_type")) == "planned" else 1.0
    cause_boost = 1.3 if str(row.get("event_cause")) in {
        "public_event",
        "procession",
        "vip_movement",
        "protest",
    } else 1.0

    raw = priority * closure * duration_factor * planned_boost * cause_boost * (0.7 + 0.3 * corridor_density)
    return float(np.clip(raw * 12.5, 5.0, 100.0))


def load_raw_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, encoding="utf-8-sig", low_memory=False)
    return df


def preprocess(df: pd.DataFrame | None = None) -> pd.DataFrame:
    if df is None:
        df = load_raw_data()

    df = df.copy()
    df.columns = [c.strip() for c in df.columns]

    for col in ("start_datetime", "end_datetime", "closed_datetime", "resolved_datetime", "created_date"):
        if col in df.columns:
            df[col] = _parse_datetime(df[col])

    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df = df[df["latitude"].between(12.5, 13.5) & df["longitude"].between(77.0, 78.0)]

    for col in ("corridor", "zone", "junction", "police_station", "event_cause", "event_type", "priority", "status"):
        if col in df.columns:
            df[col] = df[col].fillna("unknown").astype(str).str.strip()
            df.loc[df[col] == "", col] = "unknown"

    df["requires_road_closure"] = df["requires_road_closure"].apply(_to_bool)
    df["corridor_density"] = _corridor_density(df)
    df["duration_minutes"] = df.apply(_duration_minutes, axis=1)

    # Cap extreme outliers (some events closed months later in data)
    df["duration_minutes"] = df["duration_minutes"].clip(upper=24 * 60)

  # Impute missing durations by cause median
    global MEDIAN_DURATION_BY_CAUSE
    cause_medians = df.groupby("event_cause")["duration_minutes"].median().dropna().to_dict()
    MEDIAN_DURATION_BY_CAUSE = {k: float(v) for k, v in cause_medians.items()}
    overall_median = float(df["duration_minutes"].median() or 90.0)
    df["duration_minutes"] = df["duration_minutes"].fillna(
        df["event_cause"].map(cause_medians).fillna(overall_median)
    )

    df["impact_score"] = df.apply(
        lambda r: compute_impact_score(r, float(r["corridor_density"])), axis=1
    )
    df["closure_label"] = df["requires_road_closure"].astype(int)

    if "start_datetime" in df.columns:
        df["hour_of_day"] = df["start_datetime"].dt.hour.fillna(12).astype(int)
        df["day_of_week"] = df["start_datetime"].dt.dayofweek.fillna(0).astype(int)
        df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
    else:
        df["hour_of_day"] = 12
        df["day_of_week"] = 0
        df["is_weekend"] = 0

    df["planned_duration_minutes"] = 120.0
    mask = df["end_datetime"].notna() & df["start_datetime"].notna()
    df.loc[mask, "planned_duration_minutes"] = (
        (df.loc[mask, "end_datetime"] - df.loc[mask, "start_datetime"]).dt.total_seconds() / 60.0
    ).clip(15, 24 * 60)

    return df.reset_index(drop=True)


def save_processed(df: pd.DataFrame) -> Path:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(PROCESSED_PATH, index=False)
    meta = {
        "median_duration_by_cause": MEDIAN_DURATION_BY_CAUSE,
        "row_count": len(df),
    }
    (ARTIFACTS_DIR / "preprocess_meta.json").write_text(json.dumps(meta, indent=2))
    return PROCESSED_PATH


def main() -> None:
    df = preprocess()
    path = save_processed(df)
    print(f"Processed {len(df)} events -> {path}")


if __name__ == "__main__":
    main()
