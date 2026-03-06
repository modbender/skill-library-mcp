"""
Daily analysis: filter bundle by target date, compute HR zones, activity, and energy.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

import pandas as pd

from skill_health.models import HealthDataBundle
from skill_health.report import TimeWindow, build_data_quality, datetime_to_iso, metric

# HR zone boundaries (bpm)
_HR_ZONE_REST_MAX = 60
_HR_ZONE_MODERATE_MAX = 100
_HR_ZONE_HIGH_MAX = 150

# Step thresholds for activity classification
_DEAD_HOUR_STEPS = 100
_BURST_HOUR_STEPS = 1000

# Device-worn threshold: days with fewer than this many HR readings likely unworn
_DEVICE_WORN_HR_MIN = 5
_TREADMILL_STRIDE_M = 0.75


def _calculate_hr_zones(hr_df: pd.DataFrame) -> dict[str, float]:
    """
    Estimate minutes in each HR zone using actual inter-sample intervals.

    Each sample is assigned a weight equal to the time until the next sample.
    This avoids the error of assuming uniform sampling when gaps vary.
    Formula: minutes_in_zone = sum(forward_interval_sec / 60) for samples in that zone.
    The last sample receives 0 weight (no following sample to measure its duration).
    """
    if hr_df.empty:
        return {
            "rest_minutes": 0.0,
            "moderate_minutes": 0.0,
            "high_minutes": 0.0,
            "maximum_minutes": 0.0,
        }
    hr_sorted = hr_df.sort_values("timestamp").reset_index(drop=True)
    bpm = hr_sorted["bpm"].values
    # forward_interval[i] = seconds between sample i and sample i+1 (last gets 0)
    intervals_sec = hr_sorted["timestamp"].diff().dt.total_seconds()
    forward_intervals_sec = intervals_sec.shift(-1).fillna(0).values

    rest_sec = float(forward_intervals_sec[bpm < _HR_ZONE_REST_MAX].sum())
    moderate_sec = float(
        forward_intervals_sec[
            (bpm >= _HR_ZONE_REST_MAX) & (bpm < _HR_ZONE_MODERATE_MAX)
        ].sum()
    )
    high_sec = float(
        forward_intervals_sec[
            (bpm >= _HR_ZONE_MODERATE_MAX) & (bpm < _HR_ZONE_HIGH_MAX)
        ].sum()
    )
    maximum_sec = float(forward_intervals_sec[bpm >= _HR_ZONE_HIGH_MAX].sum())
    return {
        "rest_minutes": rest_sec / 60.0,
        "moderate_minutes": moderate_sec / 60.0,
        "high_minutes": high_sec / 60.0,
        "maximum_minutes": maximum_sec / 60.0,
    }


def _active_kcal_is_measured(day_calories: pd.DataFrame) -> bool:
    """Return True if at least one calorie row has actual active_kcal data (not filled 0)."""
    if day_calories.empty or "active_kcal_measured" not in day_calories.columns:
        return False
    return bool(day_calories["active_kcal_measured"].any())


def _treadmill_sessions(day_exercise: pd.DataFrame) -> pd.DataFrame:
    """Return treadmill (Kingsmith) exercise sessions for the day."""
    if day_exercise.empty or "source" not in day_exercise.columns:
        return pd.DataFrame()
    return day_exercise[
        day_exercise["source"].str.contains("kingsmith", case=False, na=False)
    ]


def _steps_in_sessions(day_steps: pd.DataFrame, sessions: pd.DataFrame) -> pd.Series:
    """Return a boolean mask for steps within any session window."""
    if day_steps.empty or sessions.empty:
        return pd.Series(False, index=day_steps.index)
    mask = pd.Series(False, index=day_steps.index)
    for _, row in sessions.iterrows():
        session_mask = (day_steps["timestamp"] >= row["start_time"]) & (
            day_steps["timestamp"] <= row["end_time"]
        )
        mask |= session_mask
    return mask


def _treadmill_distance(
    day_distance: pd.DataFrame, treadmill_sessions_df: pd.DataFrame
) -> tuple[float, float]:
    """Return total treadmill distance (km, m) for matching sessions."""
    if day_distance.empty or treadmill_sessions_df.empty:
        return 0.0, 0.0
    if "source" in day_distance.columns:
        day_distance = day_distance[
            day_distance["source"].str.contains("kingsmith", case=False, na=False)
        ]
    if day_distance.empty:
        return 0.0, 0.0
    merged = treadmill_sessions_df.merge(
        day_distance, on=["start_time", "end_time"], how="left"
    )
    distance_km = float(merged.get("distance_km", pd.Series()).fillna(0.0).sum())
    if "distance_m" in merged.columns:
        distance_m = float(merged["distance_m"].fillna(0.0).sum())
    else:
        distance_m = distance_km * 1000
    return distance_km, distance_m


def _estimate_treadmill_steps(
    *,
    day_steps: pd.DataFrame,
    day_distance: pd.DataFrame,
    treadmill_sessions_df: pd.DataFrame,
) -> tuple[float, float, float, bool]:
    """
    Return (treadmill_steps_estimated, treadmill_phone_steps, treadmill_distance_km, from_distance).
    """
    treadmill_steps_estimated = 0.0
    treadmill_phone_steps = 0.0
    treadmill_distance_km = 0.0
    treadmill_steps_from_distance = False

    if treadmill_sessions_df.empty or day_steps.empty:
        return (
            treadmill_steps_estimated,
            treadmill_phone_steps,
            treadmill_distance_km,
            treadmill_steps_from_distance,
        )

    treadmill_mask = _steps_in_sessions(day_steps, treadmill_sessions_df)
    treadmill_phone_steps = float(day_steps.loc[treadmill_mask, "steps"].sum())

    distance_km, distance_m = _treadmill_distance(day_distance, treadmill_sessions_df)
    treadmill_distance_km = distance_km
    if distance_m > 0:
        treadmill_steps_estimated = distance_m / _TREADMILL_STRIDE_M
        treadmill_steps_from_distance = True
    else:
        treadmill_steps_estimated = treadmill_phone_steps

    return (
        treadmill_steps_estimated,
        treadmill_phone_steps,
        treadmill_distance_km,
        treadmill_steps_from_distance,
    )


def _exercise_steps_non_treadmill(
    *,
    day_steps: pd.DataFrame,
    day_exercise: pd.DataFrame,
    treadmill_sessions_df: pd.DataFrame,
) -> float:
    """Return steps within non-treadmill exercise sessions."""
    if day_steps.empty or day_exercise.empty:
        return 0.0
    exercise_mask = _steps_in_sessions(day_steps, day_exercise)
    treadmill_mask = _steps_in_sessions(day_steps, treadmill_sessions_df)
    non_treadmill_mask = exercise_mask & ~treadmill_mask
    return float(day_steps.loc[non_treadmill_mask, "steps"].sum())


def build_daily_report(
    bundle: HealthDataBundle, target_date: date
) -> list[dict[str, Any]]:
    """
    Build metric list for daily analysis. Filters bundle by target_date and computes metrics.
    """
    day_start = datetime.combine(target_date, datetime.min.time())
    day_end = day_start.replace(hour=23, minute=59, second=59)
    tw = TimeWindow(
        start=datetime_to_iso(day_start),
        end=datetime_to_iso(day_end),
        resolution="1d",
    )

    day_steps = (
        bundle.steps[
            (bundle.steps["timestamp"] >= day_start)
            & (bundle.steps["timestamp"] <= day_end)
        ]
        if not bundle.steps.empty
        else pd.DataFrame()
    )
    day_hr = (
        bundle.heart_rate[
            (bundle.heart_rate["timestamp"] >= day_start)
            & (bundle.heart_rate["timestamp"] <= day_end)
        ]
        if not bundle.heart_rate.empty
        else pd.DataFrame()
    )
    day_calories = (
        bundle.calories[
            (bundle.calories["start_time"] <= day_end)
            & (bundle.calories["end_time"] >= day_start)
        ]
        if not bundle.calories.empty
        else pd.DataFrame()
    )
    day_exercise = (
        bundle.exercise_sessions[
            (bundle.exercise_sessions["start_time"] >= day_start)
            & (bundle.exercise_sessions["start_time"] <= day_end)
        ]
        if not bundle.exercise_sessions.empty
        else pd.DataFrame()
    )

    metrics_out: list[dict[str, Any]] = []

    # -- Cardiovascular load zones --
    hr_zones = _calculate_hr_zones(day_hr)
    hr_zone_reliability = (
        "unavailable"
        if day_hr.empty
        else ("high" if len(day_hr) >= 20 else "medium" if len(day_hr) >= 5 else "low")
    )
    metrics_out.append(
        metric(
            metric_name="cardiovascular_load_daily",
            description=(
                "Time spent in HR zones (rest <60, moderate 60-100, high 100-150, maximum >150 bpm)."
                " Computed from actual inter-sample intervals, not uniform sampling assumption."
            ),
            purpose="Assess cardiovascular load and training intensity distribution.",
            variables_used=["heart_rate.timestamp", "heart_rate.bpm"],
            time_window=tw,
            n_instances=len(day_hr),
            stats=hr_zones,
            extra=None,
            data_quality=build_data_quality(
                coverage=min(1.0, len(day_hr) / 288) if not day_hr.empty else 0.0,
                reliability=hr_zone_reliability,
                notes=(
                    [
                        "HR zone times reflect intervals between sparse readings; gaps >30 min are not accounted for."
                    ]
                    if len(day_hr) < 20 and not day_hr.empty
                    else []
                ),
            ),
        )
    )

    # -- Activity windows --
    device_worn = len(day_hr) >= _DEVICE_WORN_HR_MIN
    if not day_steps.empty:
        day_steps_copy = day_steps.copy()
        day_steps_copy["hour"] = day_steps_copy["timestamp"].dt.hour
        hourly = day_steps_copy.groupby("hour", as_index=True)["steps"].sum()
        dead_hours = int((hourly < _DEAD_HOUR_STEPS).sum())
        bursts = int((hourly > _BURST_HOUR_STEPS).sum())
        max_sp = float(hourly.max()) if not hourly.empty else None
        avg_sp = float(hourly.mean()) if not hourly.empty else None
    else:
        dead_hours = 0
        bursts = 0
        hourly = pd.Series(dtype=float)
        max_sp = None
        avg_sp = None
    metrics_out.append(
        metric(
            metric_name="activity_windows_daily",
            description=(
                "Dead hours (< 100 steps) vs activity bursts (> 1000 steps) per hour. "
                "total_hours_with_data counts hours that have at least one step record."
            ),
            purpose="Identify inactivity and high-activity patterns.",
            variables_used=["steps.timestamp", "steps.steps"],
            time_window=tw,
            n_instances=len(hourly),
            stats={
                "dead_hours": dead_hours,
                "activity_bursts": bursts,
                "total_hours_with_data": len(hourly),
                "max_steps_per_hour": max_sp,
                "avg_steps_per_hour": avg_sp,
                "device_worn": device_worn,
            },
            extra=None,
            data_quality=build_data_quality(
                coverage=len(hourly) / 24 if len(hourly) > 0 else 0.0,
                reliability=(
                    "medium"
                    if len(hourly) >= 12
                    else "low" if len(hourly) > 0 else "unavailable"
                ),
                notes=(
                    [
                        "Device likely not worn (< 5 HR readings); step data may be incomplete."
                    ]
                    if not device_worn
                    else []
                ),
            ),
        )
    )

    # -- Exercise vs spontaneous steps --
    # Uses OR-mask deduplication: step records overlapping multiple exercise sessions
    # are counted once, avoiding double-counting from overlapping sessions.
    if not day_steps.empty:
        total_steps = float(day_steps["steps"].sum())
        treadmill_sessions_df = _treadmill_sessions(day_exercise)
        treadmill_sessions = int(len(treadmill_sessions_df))
        day_distance = (
            bundle.distance[
                (bundle.distance["start_time"] >= day_start)
                & (bundle.distance["end_time"] <= day_end)
            ]
            if not bundle.distance.empty
            else pd.DataFrame()
        )
        (
            treadmill_steps_estimated,
            treadmill_phone_steps,
            treadmill_distance_km,
            treadmill_steps_from_distance,
        ) = _estimate_treadmill_steps(
            day_steps=day_steps,
            day_distance=day_distance,
            treadmill_sessions_df=treadmill_sessions_df,
        )
        exercise_steps_non_treadmill = _exercise_steps_non_treadmill(
            day_steps=day_steps,
            day_exercise=day_exercise,
            treadmill_sessions_df=treadmill_sessions_df,
        )

        adjusted_total_steps = (
            total_steps - treadmill_phone_steps + treadmill_steps_estimated
        )
        adjusted_total_steps = max(0.0, adjusted_total_steps)
        exercise_steps = exercise_steps_non_treadmill + treadmill_steps_estimated
        spontaneous = adjusted_total_steps - exercise_steps
        ratio = (
            exercise_steps / adjusted_total_steps if adjusted_total_steps > 0 else 0.0
        )
    else:
        total_steps = 0.0
        exercise_steps = 0.0
        spontaneous = 0.0
        ratio = 0.0
        treadmill_sessions = 0
        treadmill_steps_estimated = 0.0
        treadmill_distance_km = 0.0
        treadmill_steps_from_distance = False
        adjusted_total_steps = 0.0
    metrics_out.append(
        metric(
            metric_name="exercise_vs_spontaneous_ratio_daily",
            description=(
                "Ratio of steps during exercise sessions vs total daily steps. "
                "treadmill_sessions counts Kingsmith sessions (machine exercise, not free walking)."
            ),
            purpose="Compare formal exercise with spontaneous daily movement.",
            variables_used=[
                "steps.timestamp",
                "steps.steps",
                "exercise_sessions.start_time",
                "exercise_sessions.end_time",
                "exercise_sessions.source",
            ],
            time_window=tw,
            n_instances=len(day_steps),
            stats={
                "value": float(ratio),
                "exercise_steps": float(exercise_steps),
                "spontaneous_steps": float(spontaneous),
                "total_steps": float(adjusted_total_steps),
                "exercise_sessions": len(day_exercise),
                "treadmill_sessions": treadmill_sessions,
                "treadmill_steps_estimated": float(treadmill_steps_estimated),
                "treadmill_distance_km": float(treadmill_distance_km),
            },
            extra={
                "units": "ratio (0-1)",
                "treadmill_stride_m": _TREADMILL_STRIDE_M,
            },
            data_quality=(
                build_data_quality(
                    coverage=1.0,
                    reliability=("medium" if treadmill_steps_from_distance else "low"),
                    notes=(
                        [
                            "Treadmill steps estimated from distance using fixed stride length (0.75 m/step)."
                        ]
                        if treadmill_steps_from_distance
                        else [
                            "Treadmill steps fallback to phone accelerometer (distance not available)."
                        ]
                    ),
                )
                if treadmill_sessions > 0
                else None
            ),
        )
    )

    # -- Nighttime activity --
    if not day_steps.empty:
        night_start = day_start.replace(hour=22, minute=0)
        night_end = day_start.replace(hour=6, minute=0) + pd.Timedelta(days=1)
        night_steps = day_steps[
            (day_steps["timestamp"] >= night_start)
            & (day_steps["timestamp"] <= night_end)
        ]
        night_activity = (
            float(night_steps["steps"].sum()) if not night_steps.empty else 0.0
        )
        night_n = len(night_steps)
    else:
        night_activity = 0.0
        night_n = 0
    metrics_out.append(
        metric(
            metric_name="nighttime_activity_density_daily",
            description="Total steps between 22:00 and 06:00.",
            purpose="Detect unusual nighttime activity (insomnia, nocturia, apnea).",
            variables_used=["steps.timestamp", "steps.steps"],
            time_window=tw,
            n_instances=night_n,
            stats={"value": night_activity, "night_hours": 8},
            extra=None,
        )
    )

    # -- Energy balance --
    # active_kcal is 0 in the current data export (column not populated by the source device).
    # total_kcal IS reliable. We report both clearly, marking when active is unmeasured.
    active_kcal_measured = _active_kcal_is_measured(day_calories)
    if not day_calories.empty:
        active = float(day_calories["active_kcal"].sum())
        total = float(day_calories["total_kcal"].sum())
        # Only compute ratio if active was actually measured; otherwise it is meaningless
        active_pct = (
            (active / total * 100) if (total > 0 and active_kcal_measured) else None
        )
        basal_estimate = (total - active) if active_kcal_measured else None
    else:
        active = None
        basal_estimate = None
        total = None
        active_pct = None
    metrics_out.append(
        metric(
            metric_name="energy_balance_daily",
            description=(
                "Energy balance: total_kcal (reliable) and active_kcal (unreliable if unmeasured). "
                "total_kcal is the sum of all calorie windows for the day. "
                "active_kcal_measured=false means the source export did not include active calories."
            ),
            purpose="Assess daily energy expenditure. Use total_kcal when active_kcal is not measured.",
            variables_used=[
                "calories.start_time",
                "calories.end_time",
                "calories.active_kcal",
                "calories.total_kcal",
                "calories.active_kcal_measured",
            ],
            time_window=tw,
            n_instances=len(day_calories),
            stats=(
                {
                    "active_kcal": active,
                    "active_kcal_measured": active_kcal_measured,
                    "basal_kcal_estimate": basal_estimate,
                    "total_kcal": total,
                    "active_percentage": active_pct,
                }
                if active_kcal_measured
                else {
                    "active_kcal_measured": active_kcal_measured,
                    "total_kcal": total,
                }
            ),
            extra={"units": "kcal"},
            data_quality=build_data_quality(
                coverage=1.0 if not day_calories.empty else 0.0,
                reliability=(
                    "unavailable"
                    if day_calories.empty
                    else ("medium" if active_kcal_measured else "low")
                ),
                notes=(
                    [
                        "active_kcal not measured in current export; only total_kcal is reliable."
                    ]
                    if not active_kcal_measured
                    else []
                ),
            ),
        )
    )

    # -- Peak caloric time (uses total_kcal since active is unmeasured) --
    if not day_calories.empty:
        day_cal = day_calories.copy()
        day_cal["hour"] = day_cal["start_time"].dt.hour
        # Use total_kcal as the reliable hourly calorie signal
        hourly_cal = day_cal.groupby("hour", as_index=True)["total_kcal"].sum()
        peak_hour = int(hourly_cal.idxmax()) if not hourly_cal.empty else None
        peak_kcal = float(hourly_cal.max()) if not hourly_cal.empty else None
    else:
        peak_hour = None
        peak_kcal = None
    metrics_out.append(
        metric(
            metric_name="peak_caloric_time_daily",
            description=(
                "Hour of day with highest total caloric expenditure (uses total_kcal, "
                "since active_kcal is not available in the current export)."
            ),
            purpose="Identify peak energy window for optimal exercise timing.",
            variables_used=["calories.start_time", "calories.total_kcal"],
            time_window=tw,
            n_instances=len(day_calories),
            stats={"peak_hour": peak_hour, "peak_total_kcal": peak_kcal},
            extra={"units": "hour (0-23)", "kcal_source": "total_kcal"},
        )
    )

    return metrics_out


def infer_target_date_from_bundle(bundle: HealthDataBundle) -> date:
    """
    Infer the most recent date with data in the bundle.
    Prefers steps max when available for consistency with activity metrics.
    """
    if not bundle.steps.empty:
        return bundle.steps["timestamp"].max().date()
    candidates: list[date] = []
    if not bundle.heart_rate.empty:
        candidates.append(bundle.heart_rate["timestamp"].max().date())
    if not bundle.calories.empty:
        candidates.append(bundle.calories["end_time"].max().date())
    if not bundle.sleep_sessions.empty:
        candidates.append(bundle.sleep_sessions["end_time"].max().date())
    if not candidates:
        from datetime import date as date_type

        return date_type.today()
    return max(candidates)
