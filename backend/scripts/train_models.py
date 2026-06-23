"""Train sklearn models and precompute aggregates for EventFlow."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from preprocess import preprocess  # noqa: E402

ARTIFACTS_DIR = Path(__file__).resolve().parents[1] / "artifacts"

CATEGORICAL = ["event_type", "event_cause", "corridor", "zone", "junction", "police_station"]
NUMERIC = [
    "latitude",
    "longitude",
    "hour_of_day",
    "day_of_week",
    "is_weekend",
    "corridor_density",
    "planned_duration_minutes",
]


def build_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore", max_categories=50), CATEGORICAL),
            ("num", "passthrough", NUMERIC),
        ]
    )


def train_regressor(X: pd.DataFrame, y: pd.Series, name: str) -> tuple[Pipeline, dict]:
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    pipe = Pipeline(
        [
            ("prep", build_preprocessor()),
            ("model", RandomForestRegressor(n_estimators=120, random_state=42, n_jobs=-1)),
        ]
    )
    pipe.fit(X_train, y_train)
    preds = pipe.predict(X_test)
    metrics = {"mae": float(mean_absolute_error(y_test, preds)), "model": name}
    print(f"{name} MAE: {metrics['mae']:.2f}")
    return pipe, metrics


def train_classifier(X: pd.DataFrame, y: pd.Series) -> tuple[Pipeline, dict]:
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    pipe = Pipeline(
        [
            ("prep", build_preprocessor()),
            ("model", RandomForestClassifier(n_estimators=120, random_state=42, n_jobs=-1)),
        ]
    )
    pipe.fit(X_train, y_train)
    preds = pipe.predict(X_test)
    metrics = {"accuracy": float(accuracy_score(y_test, preds)), "model": "closure"}
    print(f"Closure accuracy: {metrics['accuracy']:.3f}")
    return pipe, metrics


def compute_aggregates(df: pd.DataFrame) -> dict:
    cause_duration = (
        df.groupby("event_cause")["duration_minutes"]
        .agg(["mean", "median", "count"])
        .reset_index()
        .rename(columns={"mean": "avg_minutes", "median": "median_minutes", "count": "event_count"})
    )
    corridor_duration = (
        df.groupby("corridor")["duration_minutes"]
        .agg(["mean", "median", "count"])
        .reset_index()
        .rename(columns={"mean": "avg_minutes", "median": "median_minutes", "count": "event_count"})
    )
    cause_corridor = (
        df.groupby(["event_cause", "corridor"])["duration_minutes"]
        .agg(["median", "count", "mean"])
        .reset_index()
        .rename(columns={"median": "median_minutes", "count": "event_count", "mean": "avg_minutes"})
    )

    zone_stats = (
        df.groupby("zone")
        .agg(
            total_events=("id", "count"),
            planned=("event_type", lambda s: int((s == "planned").sum())),
            unplanned=("event_type", lambda s: int((s == "unplanned").sum())),
            avg_duration=("duration_minutes", "mean"),
        )
        .reset_index()
    )

    junction_stats = (
        df[df["junction"] != "unknown"]
        .groupby("junction")
        .agg(
            event_count=("id", "count"),
            median_duration=("duration_minutes", "median"),
            avg_impact=("impact_score", "mean"),
        )
        .reset_index()
        .sort_values(["event_count", "median_duration"], ascending=[False, False])
        .head(25)
    )

    corridor_coords = (
        df.groupby("corridor")
        .agg(lat=("latitude", "mean"), lng=("longitude", "mean"), events=("id", "count"))
        .reset_index()
    )

    overall_median = float(df["duration_minutes"].median())

    return {
        "cause_duration": cause_duration.to_dict(orient="records"),
        "corridor_duration": corridor_duration.to_dict(orient="records"),
        "cause_corridor": cause_corridor.to_dict(orient="records"),
        "zone_stats": zone_stats.to_dict(orient="records"),
        "junction_hotspots": junction_stats.to_dict(orient="records"),
        "corridor_coords": corridor_coords.to_dict(orient="records"),
        "overall_median_duration": overall_median,
    }


def main() -> None:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    df = preprocess()
    df.to_parquet(ARTIFACTS_DIR / "processed_events.parquet", index=False)

    feature_cols = CATEGORICAL + NUMERIC
    X = df[feature_cols]

    impact_model, impact_metrics = train_regressor(X, df["impact_score"], "impact")
    duration_model, duration_metrics = train_regressor(X, df["duration_minutes"], "duration")
    closure_model, closure_metrics = train_classifier(X, df["closure_label"])

    joblib.dump(
        {
            "impact_model": impact_model,
            "duration_model": duration_model,
            "closure_model": closure_model,
            "feature_cols": feature_cols,
            "categorical": CATEGORICAL,
            "numeric": NUMERIC,
        },
        ARTIFACTS_DIR / "models.pkl",
    )

    aggregates = compute_aggregates(df)
    aggregates["training_metrics"] = {
        "impact": impact_metrics,
        "duration": duration_metrics,
        "closure": closure_metrics,
    }
    (ARTIFACTS_DIR / "aggregates.json").write_text(json.dumps(aggregates, indent=2, default=str))

    print(f"Artifacts saved to {ARTIFACTS_DIR}")


if __name__ == "__main__":
    main()
