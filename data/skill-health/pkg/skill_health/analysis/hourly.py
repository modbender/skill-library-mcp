"""
Hourly analysis: last-hour metrics and real-time style alerts (inactivity, HR flags).
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import pandas as pd

from skill_health.models import HealthDataBundle
from skill_health.report import (
    TimeWindow,
    build_data_quality,
    datetime_to_iso,
    metric,
)


def _filter_last_hour(
    df: pd.DataFrame, timestamp_column: str, window_end: datetime
) -> pd.DataFrame:
    """Return rows whose timestamp is in [window_end - 1h, window_end]."""
    window_start = window_end - timedelta(hours=1)
    if df.empty:
        return df
    return df[
        (df[timestamp_column] >= window_start) & (df[timestamp_column] <= window_end)
    ]


def _detect_hr_jumps(heart_rate_in_window: pd.DataFrame) -> dict[str, Any]:
    """
    Detect HR jumps >30 bpm within <=5 minutes (arrhythmia-like pattern).
    Returns flag, n_events, max_jump_bpm.
    """
    if heart_rate_in_window.empty:
        return {"flag": False, "n_events": 0, "max_jump_bpm": None}

    hr_sorted = heart_rate_in_window.sort_values("timestamp").copy()
    hr_sorted["delta_bpm"] = hr_sorted["bpm"].diff()
    hr_sorted["delta_t_sec"] = hr_sorted["timestamp"].diff().dt.total_seconds()

    candidates = hr_sorted[
        (hr_sorted["delta_t_sec"] > 0)
        & (hr_sorted["delta_t_sec"] <= 5 * 60)
        & (hr_sorted["delta_bpm"].abs() > 30)
    ]

    if candidates.empty:
        return {"flag": False, "n_events": 0, "max_jump_bpm": None}

    return {
        "flag": True,
        "n_events": int(len(candidates)),
        "max_jump_bpm": float(candidates["delta_bpm"].abs().max()),
    }


def build_hourly_report(
    bundle: HealthDataBundle, now: datetime
) -> list[dict[str, Any]]:
    """
    Build a list of metric dicts for the last-hour analysis (steps, calories, HR, flags).

    Args:
        bundle: Loaded and deduplicated health data.
        now: End of the one-hour window (inclusive).

    Returns:
        List of metric dicts suitable for JSON output.
    """
    window_start = now - timedelta(hours=1)
    time_window_1h = TimeWindow(
        start=datetime_to_iso(window_start),
        end=datetime_to_iso(now),
        resolution="1h",
    )
    metrics_out: list[dict[str, Any]] = []

    steps_in_window = _filter_last_hour(bundle.steps, "timestamp", now)
    steps_total = (
        float(steps_in_window["steps"].sum()) if not steps_in_window.empty else 0.0
    )

    metrics_out.append(
        metric(
            metric_name="steps_last_hour_total",
            description="Total steps recorded during the last hour.",
            purpose="Detect inactivity patterns and short-term activity changes.",
            variables_used=["steps.timestamp", "steps.steps"],
            time_window=time_window_1h,
            n_instances=len(steps_in_window),
            stats={"value": steps_total},
            extra={"units": "steps"},
        )
    )

    # Calories overlapping last hour
    if not bundle.calories.empty:
        overlap_mask = (bundle.calories["end_time"] >= window_start) & (
            bundle.calories["start_time"] <= now
        )
        calories_in_window = bundle.calories[overlap_mask]
        active_kcal = float(calories_in_window["active_kcal"].sum())
        total_kcal = float(calories_in_window["total_kcal"].sum())
        n_calories_rows = len(calories_in_window)
        active_kcal_measured = (
            bool(calories_in_window["active_kcal_measured"].any())
            if "active_kcal_measured" in calories_in_window.columns
            else False
        )
    else:
        active_kcal = 0.0
        total_kcal = 0.0
        n_calories_rows = 0
        active_kcal_measured = False

    metrics_out.append(
        metric(
            metric_name="active_kcal_last_hour_total",
            description=(
                "Total active calories overlapping the last hour. "
                "active_kcal_measured=false means the source export does not provide active calories."
            ),
            purpose="Track short-term metabolic load and detect unusual spikes.",
            variables_used=[
                "calories.start_time",
                "calories.end_time",
                "calories.active_kcal",
            ],
            time_window=time_window_1h,
            n_instances=n_calories_rows,
            stats={"value": active_kcal, "active_kcal_measured": active_kcal_measured},
            extra={"units": "kcal"},
            data_quality=build_data_quality(
                coverage=1.0 if n_calories_rows > 0 else 0.0,
                reliability=(
                    "unavailable"
                    if not active_kcal_measured
                    else ("high" if n_calories_rows >= 5 else "medium")
                ),
                notes=(
                    [
                        "active_kcal not available in current export; value is 0.0 fill, not real measurement."
                    ]
                    if not active_kcal_measured
                    else []
                ),
            ),
        )
    )
    metrics_out.append(
        metric(
            metric_name="total_kcal_last_hour_total",
            description="Total calories (active + basal) overlapping the last hour. This is the reliable caloric signal.",
            purpose="Context for energy expenditure. Prefer over active_kcal when active is unmeasured.",
            variables_used=[
                "calories.start_time",
                "calories.end_time",
                "calories.total_kcal",
            ],
            time_window=time_window_1h,
            n_instances=n_calories_rows,
            stats={"value": total_kcal},
            extra={"units": "kcal"},
            data_quality=build_data_quality(
                coverage=1.0 if n_calories_rows > 0 else 0.0,
                reliability=(
                    "high"
                    if n_calories_rows >= 2
                    else "low" if n_calories_rows > 0 else "unavailable"
                ),
            ),
        )
    )

    # Heart rate in last hour
    hr_in_window = _filter_last_hour(bundle.heart_rate, "timestamp", now)
    if not hr_in_window.empty:
        hr_mean = float(hr_in_window["bpm"].mean())
        hr_max = float(hr_in_window["bpm"].max())
        hr_min = float(hr_in_window["bpm"].min())
    else:
        hr_mean = None
        hr_max = None
        hr_min = None

    metrics_out.append(
        metric(
            metric_name="heart_rate_last_hour_mean",
            description="Average heart rate during the last hour.",
            purpose="Detect elevated heart rate at rest or stress responses.",
            variables_used=["heart_rate.timestamp", "heart_rate.bpm"],
            time_window=time_window_1h,
            n_instances=len(hr_in_window),
            stats={"value": hr_mean, "min": hr_min, "max": hr_max},
            extra={"units": "bpm"},
        )
    )
    metrics_out.append(
        metric(
            metric_name="heart_rate_last_hour_max",
            description="Maximum heart rate during the last hour.",
            purpose="Spot acute spikes that may need attention.",
            variables_used=["heart_rate.timestamp", "heart_rate.bpm"],
            time_window=time_window_1h,
            n_instances=len(hr_in_window),
            stats={"value": hr_max},
            extra={"units": "bpm"},
        )
    )

    # Long inactivity flag (>=45 min zero steps during 09:00–22:00)
    long_inactivity = False
    if 9 <= now.hour <= 22:
        if not steps_in_window.empty:
            steps_series = steps_in_window.set_index("timestamp")["steps"]
            bins_5min = steps_series.resample("5min").sum()
            consecutive_zero = 0
            for val in bins_5min.values:
                if val == 0:
                    consecutive_zero += 1
                    if consecutive_zero >= 9:  # 9 * 5 min = 45 min
                        long_inactivity = True
                        break
                else:
                    consecutive_zero = 0
        else:
            long_inactivity = True

    metrics_out.append(
        metric(
            metric_name="inactivity_long_flag",
            description="Prolonged inactivity (>=45 min zero steps) during active hours (09:00–22:00).",
            purpose="Early detection of unusual sedentarism when expected to be active.",
            variables_used=["steps.timestamp", "steps.steps"],
            time_window=time_window_1h,
            n_instances=len(steps_in_window),
            stats={"value": long_inactivity},
            extra={"threshold_minutes": 45, "active_hours": "09:00-22:00"},
        )
    )

    # High rest HR: mean HR > 100 with very low steps
    high_rest_hr = False
    if hr_mean is not None and steps_total < 50:
        high_rest_hr = hr_mean > 100
    metrics_out.append(
        metric(
            metric_name="high_rest_hr_flag",
            description="Average HR > 100 bpm with very low steps in the last hour.",
            purpose="Potential stress, dehydration, illness, or tachycardia at rest.",
            variables_used=[
                "heart_rate.timestamp",
                "heart_rate.bpm",
                "steps.timestamp",
                "steps.steps",
            ],
            time_window=time_window_1h,
            n_instances=len(hr_in_window),
            stats={"value": high_rest_hr},
            extra={"hr_threshold_bpm": 100, "steps_threshold": 50},
        )
    )

    # Possible bradycardia while awake
    possible_brady_awake = False
    if hr_min is not None and steps_total > 0:
        possible_brady_awake = hr_min < 50
    metrics_out.append(
        metric(
            metric_name="possible_bradycardia_awake_flag",
            description="HR < 50 bpm with some movement in the last hour.",
            purpose="Potential bradycardia during wakefulness (athletes differ).",
            variables_used=[
                "heart_rate.timestamp",
                "heart_rate.bpm",
                "steps.timestamp",
                "steps.steps",
            ],
            time_window=time_window_1h,
            n_instances=len(hr_in_window),
            stats={"value": possible_brady_awake},
            extra={"hr_threshold_bpm": 50, "notes": "Interpret with context."},
        )
    )

    # HR jump (arrhythmia-like)
    hr_jump = _detect_hr_jumps(hr_in_window)
    metrics_out.append(
        metric(
            metric_name="arrhythmia_like_hr_jump_flag",
            description="HR jump > 30 bpm within <= 5 minutes (pattern-only).",
            purpose="Early warning for measurement artifacts or arrhythmia-like patterns.",
            variables_used=["heart_rate.timestamp", "heart_rate.bpm"],
            time_window=time_window_1h,
            n_instances=len(hr_in_window),
            stats={
                "value": hr_jump["flag"],
                "n_events": hr_jump["n_events"],
                "max_jump_bpm": hr_jump["max_jump_bpm"],
            },
            extra={"jump_threshold_bpm": 30, "time_threshold_seconds": 300},
        )
    )

    # Calories per step (efficiency proxy)
    # Uses total_kcal since active_kcal is not measured in the current export.
    kcal_per_step = (
        (total_kcal / steps_total) if (steps_total > 0 and total_kcal > 0) else None
    )
    metrics_out.append(
        metric(
            metric_name="total_kcal_per_step_last_hour",
            description=(
                "Total calories per step during the last hour (uses total_kcal). "
                "Previously named active_kcal_per_step; renamed because active_kcal is not available."
            ),
            purpose=(
                "Detect unusual effort/fatigue vs baseline. "
                "Note: includes basal calories, so absolute value is not comparable to active-only ratios."
            ),
            variables_used=["calories.total_kcal", "steps.steps"],
            time_window=time_window_1h,
            n_instances=len(steps_in_window),
            stats={
                "value": kcal_per_step,
                "active_kcal_measured": active_kcal_measured,
            },
            extra={"units": "kcal/step", "kcal_source": "total_kcal"},
            data_quality=build_data_quality(
                coverage=1.0 if kcal_per_step is not None else 0.0,
                reliability="low" if kcal_per_step is not None else "unavailable",
                notes=[
                    "Uses total_kcal (includes basal) because active_kcal is not measured. "
                    "Do not compare directly with active-only kcal/step ratios."
                ],
            ),
        )
    )

    return metrics_out


def infer_now_from_bundle(bundle: HealthDataBundle) -> datetime:
    """
    Infer the reference timestamp 'now' from the latest data point in the bundle.
    Used to anchor the "last hour" window to real data rather than wall clock.
    """
    candidates: list[datetime] = []
    if not bundle.steps.empty:
        ts = bundle.steps["timestamp"].max()
        if pd.notna(ts):
            candidates.append(
                ts.to_pydatetime() if hasattr(ts, "to_pydatetime") else ts
            )
    if not bundle.heart_rate.empty:
        ts = bundle.heart_rate["timestamp"].max()
        if pd.notna(ts):
            candidates.append(
                ts.to_pydatetime() if hasattr(ts, "to_pydatetime") else ts
            )
    if not bundle.calories.empty:
        ts = bundle.calories["end_time"].max()
        if pd.notna(ts):
            candidates.append(
                ts.to_pydatetime() if hasattr(ts, "to_pydatetime") else ts
            )
    if not bundle.sleep_sessions.empty:
        ts = bundle.sleep_sessions["end_time"].max()
        if pd.notna(ts):
            candidates.append(
                ts.to_pydatetime() if hasattr(ts, "to_pydatetime") else ts
            )
    if not candidates:
        raise ValueError("Cannot infer 'now' from empty health data bundle")
    return max(candidates)
