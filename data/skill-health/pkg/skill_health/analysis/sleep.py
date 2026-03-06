"""
Sleep analysis: estimate sleep window from a recent window and compute sleep metrics.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import pandas as pd

from skill_health.models import HealthDataBundle
from skill_health.report import TimeWindow, build_data_quality, datetime_to_iso, metric

SLEEP_GAP_MIN_HOURS = 3
NAP_MIN_MINUTES = 15
NAP_MAX_MINUTES = 120
HR_SPIKE_THRESHOLD_BPM = 20


def _has_sleep_window(sleep_start: datetime | None, sleep_end: datetime | None) -> bool:
    """Return True when both sleep_start and sleep_end are present."""
    return sleep_start is not None and sleep_end is not None


def _slice_window(
    df: pd.DataFrame, start: datetime, end: datetime, timestamp_column: str
) -> pd.DataFrame:
    """Return rows where timestamp_column is within [start, end]."""
    if df.empty:
        return df
    return df[(df[timestamp_column] >= start) & (df[timestamp_column] <= end)]


def _estimate_sleep_window_from_steps(
    steps_df: pd.DataFrame, window_start: datetime, window_end: datetime
) -> tuple[datetime, datetime] | None:
    """
    Estimate sleep window as the longest inactivity gap between step timestamps.
    Returns (sleep_start, sleep_end) or None when no suitable gap is found.
    """
    if steps_df.empty:
        return None

    steps_in_window = steps_df[
        (steps_df["timestamp"] >= window_start) & (steps_df["timestamp"] <= window_end)
    ].sort_values("timestamp")
    if steps_in_window.empty:
        return None

    timestamps = steps_in_window["timestamp"].tolist()
    if len(timestamps) < 2:
        return None
    best_gap = timedelta(0)
    best_window: tuple[datetime, datetime] | None = None
    for current, nxt in zip(timestamps, timestamps[1:], strict=False):
        gap = nxt - current
        if gap > best_gap:
            best_gap = gap
            best_window = (current, nxt)

    if best_window is None or best_gap < timedelta(hours=SLEEP_GAP_MIN_HOURS):
        return None
    return best_window


def _sleep_sessions_in_window(
    sleep_df: pd.DataFrame, window_start: datetime, window_end: datetime
) -> pd.DataFrame:
    """Return sleep sessions that overlap the analysis window."""
    if sleep_df.empty:
        return sleep_df
    mask = (sleep_df["start_time"] <= window_end) & (
        sleep_df["end_time"] >= window_start
    )
    return sleep_df[mask]


def infer_now_from_bundle(bundle: HealthDataBundle) -> datetime:
    """
    Infer the reference timestamp 'now' from the latest data point in the bundle.
    Used to anchor the last-24h sleep window to real data rather than wall clock.
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
    if not bundle.oxygen_saturation.empty:
        ts = bundle.oxygen_saturation["timestamp"].max()
        if pd.notna(ts):
            candidates.append(
                ts.to_pydatetime() if hasattr(ts, "to_pydatetime") else ts
            )
    if not candidates:
        raise ValueError("Cannot infer 'now' from empty health data bundle")
    return max(candidates)


def build_sleep_report(
    bundle: HealthDataBundle, now: datetime, window_hours: int = 30
) -> list[dict[str, Any]]:
    """
    Build sleep-focused metrics using a recent analysis window.

    Args:
        bundle: Loaded and deduplicated health data.
        now: End timestamp for the analysis window.
        window_hours: Window size in hours (default 30).

    Returns:
        List of metric dicts suitable for JSON output.
    """
    window_start = now - timedelta(hours=window_hours)
    window_label = f"last_{window_hours}h"
    time_window = TimeWindow(
        start=datetime_to_iso(window_start),
        end=datetime_to_iso(now),
        resolution=f"{window_hours}h",
    )

    sleep_sessions = _sleep_sessions_in_window(bundle.sleep_sessions, window_start, now)
    sleep_start: datetime | None = None
    sleep_end: datetime | None = None
    sleep_duration_hours: float | None = None
    sleep_source = "unavailable"
    sleep_sessions_count = int(len(sleep_sessions))

    if not sleep_sessions.empty:
        sleep_sessions = sleep_sessions.copy()
        sleep_sessions["duration_seconds"] = (
            sleep_sessions["end_time"] - sleep_sessions["start_time"]
        ).dt.total_seconds()
        today_sessions = sleep_sessions[
            sleep_sessions["end_time"].dt.date == now.date()
        ]
        pick_from = today_sessions if not today_sessions.empty else sleep_sessions
        main_idx = pick_from["duration_seconds"].idxmax()
        sleep_start = pick_from.loc[main_idx, "start_time"]
        sleep_end = pick_from.loc[main_idx, "end_time"]
        if "duration_hours" in sleep_sessions.columns:
            sleep_duration_hours = float(
                pick_from.loc[main_idx, "duration_seconds"] / 3600
            )
        else:
            sleep_duration_hours = float(
                (sleep_end - sleep_start).total_seconds() / 3600
            )
        sleep_source = "sleep_sessions"
    else:
        estimated = _estimate_sleep_window_from_steps(bundle.steps, window_start, now)
        if estimated is not None:
            sleep_start, sleep_end = estimated
            sleep_duration_hours = float(
                (sleep_end - sleep_start).total_seconds() / 3600
            )
            sleep_source = "estimated"

    has_sleep_window = _has_sleep_window(sleep_start, sleep_end)
    base_notes: list[str] = []
    if sleep_source == "estimated":
        base_notes.append(
            "No sleep session data; sleep window estimated from inactivity in the "
            f"last {window_hours}h."
        )
    elif sleep_source == "unavailable":
        base_notes.append(
            f"No sleep window could be inferred from last {window_hours}h data."
        )

    base_quality = build_data_quality(
        coverage=1.0 if has_sleep_window else 0.0,
        reliability=(
            "high"
            if sleep_source == "sleep_sessions"
            else ("low" if sleep_source == "estimated" else "unavailable")
        ),
        notes=base_notes,
    )

    metrics_out: list[dict[str, Any]] = []

    if has_sleep_window:
        sleep_start_iso = datetime_to_iso(sleep_start)
        sleep_end_iso = datetime_to_iso(sleep_end)
    else:
        sleep_start_iso = None
        sleep_end_iso = None
    metrics_out.append(
        metric(
            metric_name=f"sleep_window_{window_label}",
            description=f"Estimated sleep window within the last {window_hours} hours.",
            purpose="Anchor sleep-related metrics to a specific time window.",
            variables_used=[
                "sleep_sessions.start_time",
                "sleep_sessions.end_time",
                "steps.timestamp",
            ],
            time_window=time_window,
            n_instances=sleep_sessions_count,
            stats={
                "start": sleep_start_iso,
                "end": sleep_end_iso,
                "duration_hours": sleep_duration_hours,
                "source": sleep_source,
            },
            data_quality=base_quality,
        )
    )

    # Naps (sleep_sessions only)
    naps: list[dict[str, Any]] = []
    if sleep_source == "sleep_sessions" and not sleep_sessions.empty:
        main_start = sleep_start
        main_end = sleep_end
        naps_source = sleep_sessions[sleep_sessions["start_time"].dt.date == now.date()]
        for _, row in naps_source.iterrows():
            start = row["start_time"]
            end = row["end_time"]
            if start is None or end is None:
                continue
            if not (end <= main_start or start >= main_end):
                continue
            duration_min = float((end - start).total_seconds() / 60)
            if NAP_MIN_MINUTES <= duration_min <= NAP_MAX_MINUTES:
                naps.append(
                    {
                        "start": datetime_to_iso(start),
                        "end": datetime_to_iso(end),
                        "duration_minutes": duration_min,
                    }
                )
        naps_quality = build_data_quality(
            coverage=1.0,
            reliability="high",
            notes=[],
        )
    else:
        naps_quality = build_data_quality(
            coverage=0.0,
            reliability="unavailable",
            notes=base_notes + ["Naps require sleep session data."],
        )

    metrics_out.append(
        metric(
            metric_name=f"naps_detected_{window_label}",
            description="Detected naps from sleep sessions that do not overlap main sleep window.",
            purpose="Identify short daytime sleep episodes.",
            variables_used=["sleep_sessions.start_time", "sleep_sessions.end_time"],
            time_window=time_window,
            n_instances=int(len(sleep_sessions)),
            stats={
                "count": len(naps),
                "total_minutes": (
                    float(sum(n["duration_minutes"] for n in naps)) if naps else 0.0
                ),
                "duration_range_minutes": [NAP_MIN_MINUTES, NAP_MAX_MINUTES],
            },
            data_quality=naps_quality,
        )
    )

    metrics_out.append(
        metric(
            metric_name=f"sleep_duration_{window_label}",
            description="Total sleep duration within the detected sleep window.",
            purpose="Track total sleep time for recovery and health.",
            variables_used=["sleep_sessions.duration_hours", "steps.timestamp"],
            time_window=time_window,
            n_instances=sleep_sessions_count,
            stats={"value": sleep_duration_hours, "source": sleep_source},
            extra={"units": "hours"},
            data_quality=base_quality,
        )
    )

    # Sleep midpoint
    if has_sleep_window:
        midpoint = sleep_start + (sleep_end - sleep_start) / 2
        midpoint_iso: str | None = datetime_to_iso(midpoint)
    else:
        midpoint_iso = None
    metrics_out.append(
        metric(
            metric_name=f"sleep_midpoint_{window_label}",
            description="Midpoint time of the detected sleep window.",
            purpose="Track circadian timing and consistency.",
            variables_used=[
                "sleep_sessions.start_time",
                "sleep_sessions.end_time",
                "steps.timestamp",
            ],
            time_window=time_window,
            n_instances=sleep_sessions_count,
            stats={"value": midpoint_iso},
            data_quality=base_quality,
        )
    )

    # Sleep latency from last activity
    latency_minutes: float | None = None
    if has_sleep_window:
        steps_before_sleep = bundle.steps[bundle.steps["timestamp"] <= sleep_start]
        if not steps_before_sleep.empty:
            last_activity = steps_before_sleep["timestamp"].max()
            latency_minutes = float((sleep_start - last_activity).total_seconds() / 60)
    latency_quality = (
        base_quality
        if latency_minutes is not None
        else build_data_quality(
            coverage=0.0,
            reliability="unavailable",
            notes=base_notes
            + ["No steps found before sleep start to estimate latency."],
        )
    )
    metrics_out.append(
        metric(
            metric_name=f"sleep_latency_estimated_{window_label}",
            description="Estimated sleep latency: time from last activity to sleep start.",
            purpose="Long latency may indicate difficulty falling asleep.",
            variables_used=["steps.timestamp", "sleep_sessions.start_time"],
            time_window=time_window,
            n_instances=sleep_sessions_count,
            stats={"value": latency_minutes},
            extra={"units": "minutes"},
            data_quality=latency_quality,
        )
    )

    # HR metrics during sleep window
    hr_metrics_notes = base_notes.copy()
    hr_sleep = pd.DataFrame()
    if has_sleep_window:
        hr_sleep = _slice_window(
            bundle.heart_rate, sleep_start, sleep_end, "timestamp"
        ).sort_values("timestamp")

    if not hr_sleep.empty:
        hr_min = float(hr_sleep["bpm"].min())
        hr_max = float(hr_sleep["bpm"].max())
        hr_range = hr_max - hr_min
        if len(hr_sleep) > 1:
            hr_diff = hr_sleep["bpm"].diff().abs()
            hr_spikes = int((hr_diff > HR_SPIKE_THRESHOLD_BPM).sum())
        else:
            hr_spikes = 0
        hr_quality = build_data_quality(
            coverage=1.0,
            reliability="high" if sleep_source == "sleep_sessions" else "medium",
            notes=hr_metrics_notes,
        )
    else:
        hr_min = None
        hr_max = None
        hr_range = None
        hr_spikes = 0
        hr_quality = build_data_quality(
            coverage=0.0,
            reliability="unavailable",
            notes=hr_metrics_notes + ["No heart rate samples during sleep window."],
        )

    metrics_out.append(
        metric(
            metric_name=f"resting_hr_during_sleep_{window_label}",
            description="Minimum HR during the sleep window (resting HR proxy).",
            purpose="Track recovery and potential stress signals.",
            variables_used=["heart_rate.timestamp", "heart_rate.bpm"],
            time_window=time_window,
            n_instances=int(len(hr_sleep)),
            stats={"value": hr_min, "hr_min": hr_min, "hr_max": hr_max},
            extra={"units": "bpm"},
            data_quality=hr_quality,
        )
    )

    metrics_out.append(
        metric(
            metric_name=f"hr_range_during_sleep_{window_label}",
            description=(
                "HR range during sleep: max(HR_sleep) - min(HR_sleep). "
                "Not clinical HRV."
            ),
            purpose="Proxy for autonomic variability during sleep.",
            variables_used=["heart_rate.timestamp", "heart_rate.bpm"],
            time_window=time_window,
            n_instances=int(len(hr_sleep)),
            stats={
                "value": hr_range,
                "hr_min_during_sleep": hr_min,
                "hr_max_during_sleep": hr_max,
            },
            extra={"units": "bpm"},
            data_quality=hr_quality,
        )
    )

    metrics_out.append(
        metric(
            metric_name=f"sleep_fragmentation_hr_spikes_{window_label}",
            description="Sleep fragmentation proxy: HR spikes > 20 bpm during sleep.",
            purpose="Detect possible micro-awakenings or restless sleep.",
            variables_used=["heart_rate.timestamp", "heart_rate.bpm"],
            time_window=time_window,
            n_instances=int(len(hr_sleep)),
            stats={
                "fragmentation_events": hr_spikes,
                "hr_spike_threshold_bpm": HR_SPIKE_THRESHOLD_BPM,
            },
            data_quality=hr_quality,
        )
    )

    # SpO2 metrics during sleep window
    spo2_sleep = pd.DataFrame()
    if has_sleep_window:
        spo2_sleep = _slice_window(
            bundle.oxygen_saturation, sleep_start, sleep_end, "timestamp"
        )
    if not spo2_sleep.empty:
        spo2_vals = spo2_sleep["spo2_pct"].dropna()
        spo2_min = float(spo2_vals.min()) if not spo2_vals.empty else None
        spo2_mean = float(spo2_vals.mean()) if not spo2_vals.empty else None
        spo2_quality = build_data_quality(
            coverage=1.0,
            reliability="medium" if sleep_source == "estimated" else "high",
            notes=base_notes,
        )
    else:
        spo2_min = None
        spo2_mean = None
        spo2_quality = build_data_quality(
            coverage=0.0,
            reliability="unavailable",
            notes=base_notes + ["No SpO2 samples during sleep window."],
        )
    metrics_out.append(
        metric(
            metric_name=f"spo2_sleep_summary_{window_label}",
            description="SpO2 summary within the sleep window.",
            purpose="Identify potential nocturnal desaturation.",
            variables_used=[
                "oxygen_saturation.timestamp",
                "oxygen_saturation.spo2_pct",
            ],
            time_window=time_window,
            n_instances=int(len(spo2_sleep)),
            stats={"min_pct": spo2_min, "mean_pct": spo2_mean},
            extra={"units": "%"},
            data_quality=spo2_quality,
        )
    )

    # Awakenings proxy from steps within sleep window
    steps_in_sleep = pd.DataFrame()
    if has_sleep_window:
        steps_in_sleep = _slice_window(
            bundle.steps, sleep_start, sleep_end, "timestamp"
        )
    awakenings = int(len(steps_in_sleep)) if not steps_in_sleep.empty else 0
    awakenings_quality = (
        base_quality
        if has_sleep_window
        else build_data_quality(
            coverage=0.0,
            reliability="unavailable",
            notes=base_notes,
        )
    )
    metrics_out.append(
        metric(
            metric_name=f"sleep_awakenings_proxy_{window_label}",
            description="Proxy awakenings count from step events during sleep window.",
            purpose="Flag possible sleep interruptions (movement-based proxy).",
            variables_used=["steps.timestamp", "steps.steps"],
            time_window=time_window,
            n_instances=int(len(steps_in_sleep)),
            stats={
                "value": awakenings,
                "steps_events_during_sleep": awakenings,
                "hr_spike_events": hr_spikes,
            },
            data_quality=awakenings_quality,
        )
    )

    return metrics_out
