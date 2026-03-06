"""
Weekly analysis: filter bundle by 7-day window, compute trends, ghost days, exercise consistency.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

import pandas as pd

from skill_health.models import HealthDataBundle
from skill_health.report import TimeWindow, build_data_quality, datetime_to_iso, metric

GHOST_DAY_STEPS_THRESHOLD = 500
# Days with fewer than this many HR readings are considered device-not-worn
_DEVICE_WORN_HR_MIN = 5
SLEEP_TARGET_HOURS = 8.0
RHR_TREND_THRESHOLD_BPM = 3.0


def _compute_rhr_trend(
    rhr_by_day: list[float],
) -> tuple[float | None, float | None, float | None, bool]:
    """Return mean_first, mean_second, trend_bpm, and rising flag."""
    if len(rhr_by_day) < 2:
        mean_first = float(rhr_by_day[0]) if rhr_by_day else None
        return mean_first, None, None, False

    first_half = rhr_by_day[: max(1, len(rhr_by_day) // 2)]
    second_half = rhr_by_day[len(rhr_by_day) // 2 :]
    mean_first = sum(first_half) / len(first_half)
    mean_second = sum(second_half) / len(second_half)
    trend_bpm = mean_second - mean_first
    return mean_first, mean_second, trend_bpm, trend_bpm >= RHR_TREND_THRESHOLD_BPM


def _compute_weekend_ratio(
    weekend_steps: list[float], weekday_steps: list[float]
) -> tuple[float | None, float | None, float | None]:
    """Return avg_weekend, avg_weekday, and weekend/weekday ratio."""
    avg_weekend = sum(weekend_steps) / len(weekend_steps) if weekend_steps else None
    avg_weekday = sum(weekday_steps) / len(weekday_steps) if weekday_steps else None
    if avg_weekend is None or avg_weekday is None or avg_weekday <= 0:
        return avg_weekend, avg_weekday, None
    return avg_weekend, avg_weekday, avg_weekend / avg_weekday


def _rhr_for_day(
    hr_df: pd.DataFrame, sleep_df: pd.DataFrame, day_start: datetime, day_end: datetime
) -> float | None:
    """Estimate RHR for a single day: min HR during sleep, else min HR of day."""
    if hr_df.empty or "timestamp" not in hr_df.columns:
        return None
    day_hr = hr_df[(hr_df["timestamp"] >= day_start) & (hr_df["timestamp"] <= day_end)]
    if day_hr.empty:
        return None
    if sleep_df.empty or "start_time" not in sleep_df.columns:
        return float(day_hr["bpm"].min())
    day_sleep = sleep_df[
        (
            (
                (sleep_df["start_time"] >= day_start)
                & (sleep_df["start_time"] <= day_end)
            )
            | ((sleep_df["end_time"] >= day_start) & (sleep_df["end_time"] <= day_end))
            | (
                (sleep_df["start_time"] <= day_start)
                & (sleep_df["end_time"] >= day_end)
            )
        )
    ]
    if not day_sleep.empty:
        hr_during_sleep: list[float] = []
        for _, row in day_sleep.iterrows():
            mask = (day_hr["timestamp"] >= row["start_time"]) & (
                day_hr["timestamp"] <= row["end_time"]
            )
            hr_during_sleep.extend(day_hr.loc[mask, "bpm"].tolist())
        if hr_during_sleep:
            return float(min(hr_during_sleep))
    return float(day_hr["bpm"].min())


def _steps_for_day(
    steps_df: pd.DataFrame, day_start: datetime, day_end: datetime
) -> float:
    """Total steps for a single day."""
    if steps_df.empty or "timestamp" not in steps_df.columns:
        return 0.0
    day_steps = steps_df[
        (steps_df["timestamp"] >= day_start) & (steps_df["timestamp"] <= day_end)
    ]
    return float(day_steps["steps"].sum()) if not day_steps.empty else 0.0


def _sleep_hours_for_day(
    sleep_df: pd.DataFrame, day_start: datetime, day_end: datetime
) -> float | None:
    """Total sleep duration (hours) overlapping the day."""
    if sleep_df.empty or "start_time" not in sleep_df.columns:
        return None
    day_sleep = sleep_df[
        (
            (
                (sleep_df["start_time"] >= day_start)
                & (sleep_df["start_time"] <= day_end)
            )
            | ((sleep_df["end_time"] >= day_start) & (sleep_df["end_time"] <= day_end))
            | (
                (sleep_df["start_time"] <= day_start)
                & (sleep_df["end_time"] >= day_end)
            )
        )
    ]
    if day_sleep.empty:
        return None
    total_minutes = 0.0
    for _, row in day_sleep.iterrows():
        overlap_start = max(row["start_time"], day_start)
        overlap_end = min(row["end_time"], day_end)
        total_minutes += (overlap_end - overlap_start).total_seconds() / 60
    return total_minutes / 60.0 if total_minutes > 0 else None


def infer_week_end_date_from_bundle(bundle: HealthDataBundle) -> date:
    """
    Infer the most recent date with data (end of week window).
    Prefers steps max when available, so the analyzed week has step data (avoids ghost days
    when steps are in a different range than sleep/exercise).
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
        return date.today()
    return max(candidates)


def build_weekly_report(
    bundle: HealthDataBundle, week_end_date: date
) -> list[dict[str, Any]]:
    """
    Build metric list for weekly analysis. Filters bundle by 7-day window ending on week_end_date.
    """
    day_end_dt = datetime.combine(week_end_date, datetime.max.time())
    day_start_dt = datetime.combine(
        week_end_date - timedelta(days=6), datetime.min.time()
    )
    tw = TimeWindow(
        start=datetime_to_iso(day_start_dt),
        end=datetime_to_iso(day_end_dt),
        resolution="7d",
    )

    week_steps = (
        bundle.steps[
            (bundle.steps["timestamp"] >= day_start_dt)
            & (bundle.steps["timestamp"] <= day_end_dt)
        ]
        if not bundle.steps.empty
        else pd.DataFrame()
    )
    week_hr = (
        bundle.heart_rate[
            (bundle.heart_rate["timestamp"] >= day_start_dt)
            & (bundle.heart_rate["timestamp"] <= day_end_dt)
        ]
        if not bundle.heart_rate.empty
        else pd.DataFrame()
    )
    week_sleep = (
        bundle.sleep_sessions[
            (
                (
                    (bundle.sleep_sessions["start_time"] >= day_start_dt)
                    & (bundle.sleep_sessions["start_time"] <= day_end_dt)
                )
                | (
                    (bundle.sleep_sessions["end_time"] >= day_start_dt)
                    & (bundle.sleep_sessions["end_time"] <= day_end_dt)
                )
                | (
                    (bundle.sleep_sessions["start_time"] <= day_start_dt)
                    & (bundle.sleep_sessions["end_time"] >= day_end_dt)
                )
            )
        ]
        if not bundle.sleep_sessions.empty
        else pd.DataFrame()
    )
    week_exercise = (
        bundle.exercise_sessions[
            (bundle.exercise_sessions["start_time"] >= day_start_dt)
            & (bundle.exercise_sessions["start_time"] <= day_end_dt)
        ]
        if not bundle.exercise_sessions.empty
        else pd.DataFrame()
    )
    week_spo2 = (
        bundle.oxygen_saturation[
            (bundle.oxygen_saturation["timestamp"] >= day_start_dt)
            & (bundle.oxygen_saturation["timestamp"] <= day_end_dt)
        ]
        if not bundle.oxygen_saturation.empty
        else pd.DataFrame()
    )

    metrics_out: list[dict[str, Any]] = []

    # RHR trending: first 3 days vs last 3 days
    rhr_by_day: list[float] = []
    for i in range(7):
        d = week_end_date - timedelta(days=6 - i)
        ds = datetime.combine(d, datetime.min.time())
        de = datetime.combine(d, datetime.max.time())
        rhr = _rhr_for_day(week_hr, week_sleep, ds, de)
        if rhr is not None:
            rhr_by_day.append(rhr)

    mean_first, mean_second, rhr_trend_bpm, rhr_trend_flag = _compute_rhr_trend(
        rhr_by_day
    )

    metrics_out.append(
        metric(
            metric_name="rhr_trending_weekly",
            description="RHR trend: first vs second half of week (bpm difference).",
            purpose="Rising RHR >3-5 bpm may signal overtraining, illness, dehydration, stress.",
            variables_used=[
                "heart_rate.timestamp",
                "heart_rate.bpm",
                "sleep_sessions.start_time",
                "sleep_sessions.end_time",
            ],
            time_window=tw,
            n_instances=len(rhr_by_day),
            stats={
                "value": rhr_trend_bpm,
                "mean_rhr_first_half": mean_first,
                "mean_rhr_second_half": mean_second,
                "rhr_by_day": rhr_by_day if rhr_by_day else None,
                "flag_rising_rhr": rhr_trend_flag,
            },
            extra={"units": "bpm", "threshold_bpm": RHR_TREND_THRESHOLD_BPM},
        )
    )

    # Ghost days: days with almost 0 activity
    # Classify each ghost day: device_not_worn (< 5 HR readings) vs sedentary (has HR)
    ghost_days = 0
    steps_per_day: dict[str, float] = {}
    ghost_days_dates: list[str] = []
    ghost_days_device_not_worn_dates: list[str] = []
    for i in range(7):
        d = week_end_date - timedelta(days=6 - i)
        ds = datetime.combine(d, datetime.min.time())
        de = datetime.combine(d, datetime.max.time())
        s = _steps_for_day(week_steps, ds, de)
        steps_per_day[d.isoformat()] = s
        day_hr_count = (
            int(((week_hr["timestamp"] >= ds) & (week_hr["timestamp"] <= de)).sum())
            if not week_hr.empty
            else 0
        )
        device_worn = day_hr_count >= _DEVICE_WORN_HR_MIN
        if s < GHOST_DAY_STEPS_THRESHOLD:
            ghost_days += 1
            ghost_days_dates.append(d.isoformat())
            if not device_worn:
                ghost_days_device_not_worn_dates.append(d.isoformat())

    ghost_days_device_not_worn = len(ghost_days_device_not_worn_dates)

    metrics_out.append(
        metric(
            metric_name="ghost_days_weekly",
            description=(
                "Days with very low activity (< 500 steps). "
                "Classified into device_not_worn (< 5 HR readings) vs sedentary (has HR data)."
            ),
            purpose="Identify illness, recovery, or sedentary patterns. Distinguish from device not worn.",
            variables_used=["steps.timestamp", "steps.steps", "heart_rate.timestamp"],
            time_window=tw,
            n_instances=7,
            stats={
                "value": ghost_days,
                "ghost_days_device_not_worn": ghost_days_device_not_worn,
                "ghost_days_sedentary": ghost_days - ghost_days_device_not_worn,
                "ghost_days_dates": ghost_days_dates,
                "ghost_days_device_not_worn_dates": ghost_days_device_not_worn_dates,
                "flag_has_ghost_days": ghost_days > 0,
            },
            extra=None,
            data_quality=build_data_quality(
                coverage=1.0,
                reliability="high",
                notes=(
                    [
                        f"{ghost_days_device_not_worn} ghost day(s) appear to be device-not-worn, not true sedentarism."
                    ]
                    if ghost_days_device_not_worn > 0
                    else []
                ),
            ),
        )
    )

    # Exercise consistency: days with formal exercise
    exercise_dates: set[date] = set()
    if not week_exercise.empty:
        for _, row in week_exercise.iterrows():
            exercise_dates.add(row["start_time"].date())
    days_with_exercise = len(exercise_dates)

    metrics_out.append(
        metric(
            metric_name="exercise_consistency_weekly",
            description="Number of days with at least one exercise session.",
            purpose="Track consistency of formal exercise vs target.",
            variables_used=[
                "exercise_sessions.start_time",
                "exercise_sessions.end_time",
            ],
            time_window=tw,
            n_instances=7,
            stats={
                "days_with_exercise": days_with_exercise,
                "exercise_sessions_total": len(week_exercise),
                "target_days": 5,
            },
            extra={"units": "days"},
        )
    )

    # Weekend compensation: weekend vs weekday steps
    weekend_steps: list[float] = []
    weekday_steps: list[float] = []
    for d_str, s in steps_per_day.items():
        d = datetime.strptime(d_str, "%Y-%m-%d").date()
        wd = d.weekday()
        if wd >= 5:
            weekend_steps.append(s)
        else:
            weekday_steps.append(s)

    avg_weekend, avg_weekday, weekend_compensation_ratio = _compute_weekend_ratio(
        weekend_steps, weekday_steps
    )

    metrics_out.append(
        metric(
            metric_name="weekend_compensation_weekly",
            description="Weekend (Sat/Sun) vs weekday average steps ratio.",
            purpose="Detect compensation: walking more on weekends after sedentary week.",
            variables_used=["steps.timestamp", "steps.steps"],
            time_window=tw,
            n_instances=7,
            stats={
                "avg_weekend_steps": avg_weekend,
                "avg_weekday_steps": avg_weekday,
                "weekend_weekday_ratio": weekend_compensation_ratio,
                "flag_weekend_compensation": (
                    weekend_compensation_ratio is not None
                    and weekend_compensation_ratio > 1.3
                ),
            },
            extra={"units": "ratio"},
        )
    )

    # Sleep debt: sum of (target - actual) per night
    sleep_debt_hours = 0.0
    nights_with_sleep = 0
    for i in range(7):
        d = week_end_date - timedelta(days=6 - i)
        ds = datetime.combine(d, datetime.min.time())
        de = datetime.combine(d, datetime.max.time())
        hrs = _sleep_hours_for_day(week_sleep, ds, de)
        if hrs is not None:
            nights_with_sleep += 1
            debt = max(0.0, SLEEP_TARGET_HOURS - hrs)
            sleep_debt_hours += debt

    metrics_out.append(
        metric(
            metric_name="sleep_debt_weekly",
            description="Accumulated sleep debt: sum of (target 8h - actual) per night.",
            purpose="Track cumulative sleep shortfall.",
            variables_used=["sleep_sessions.start_time", "sleep_sessions.end_time"],
            time_window=tw,
            n_instances=nights_with_sleep,
            stats={
                "value": sleep_debt_hours,
                "target_hours_per_night": SLEEP_TARGET_HOURS,
                "nights_with_data": nights_with_sleep,
            },
            extra={"units": "hours"},
        )
    )

    # SpO2 variance within week
    if not week_spo2.empty and "spo2_pct" in week_spo2.columns:
        spo2_vals = week_spo2["spo2_pct"].dropna()
        spo2_std = float(spo2_vals.std()) if len(spo2_vals) > 1 else 0.0
        spo2_mean = float(spo2_vals.mean())
        spo2_min = float(spo2_vals.min())
        metrics_out.append(
            metric(
                metric_name="spo2_variance_weekly",
                description="SpO2 variance within the week.",
                purpose="Week-to-week drops may indicate respiratory issues or altitude.",
                variables_used=[
                    "oxygen_saturation.timestamp",
                    "oxygen_saturation.spo2_pct",
                ],
                time_window=tw,
                n_instances=len(spo2_vals),
                stats={
                    "mean_pct": spo2_mean,
                    "std_pct": spo2_std,
                    "min_pct": spo2_min,
                    "flag_low_spo2": spo2_min < 94,
                },
                extra={"units": "%", "low_threshold_pct": 94},
            )
        )

    # Sunday night syndrome: Sunday RHR vs weekly avg (if Sunday in window)
    sunday_date = None
    for i in range(7):
        d = week_end_date - timedelta(days=6 - i)
        if d.weekday() == 6:
            sunday_date = d
            break
    sunday_rhr = None
    if sunday_date is not None:
        ds = datetime.combine(sunday_date, datetime.min.time())
        de = datetime.combine(sunday_date, datetime.max.time())
        sunday_rhr = _rhr_for_day(week_hr, week_sleep, ds, de)

    weekly_avg_rhr = sum(rhr_by_day) / len(rhr_by_day) if rhr_by_day else None
    sunday_rhr_diff = (
        (sunday_rhr - weekly_avg_rhr)
        if sunday_rhr is not None and weekly_avg_rhr is not None
        else None
    )

    metrics_out.append(
        metric(
            metric_name="sunday_night_syndrome_weekly",
            description="Sunday RHR vs weekly average (anticipatory stress pattern).",
            purpose="Higher Sunday RHR may indicate stress about the week ahead.",
            variables_used=[
                "heart_rate.timestamp",
                "heart_rate.bpm",
                "sleep_sessions.start_time",
                "sleep_sessions.end_time",
            ],
            time_window=tw,
            n_instances=len(rhr_by_day),
            stats={
                "sunday_rhr": sunday_rhr,
                "weekly_avg_rhr": weekly_avg_rhr,
                "sunday_rhr_diff_vs_avg": sunday_rhr_diff,
                "flag_sunday_elevated": (
                    sunday_rhr_diff is not None and sunday_rhr_diff >= 3.0
                ),
            },
            extra={"units": "bpm"},
        )
    )

    return metrics_out
