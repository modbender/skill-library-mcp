"""
Monthly analysis: filter bundle by calendar month, compute trends and sustainability.
"""

from __future__ import annotations

import calendar
from datetime import date, datetime
from typing import Any

import pandas as pd

from skill_health.analysis.weekly import (
    _rhr_for_day,
    _sleep_hours_for_day,
    _steps_for_day,
)
from skill_health.models import HealthDataBundle
from skill_health.report import TimeWindow, build_data_quality, datetime_to_iso, metric

GHOST_DAY_STEPS_THRESHOLD = 500
_DEVICE_WORN_HR_MIN = 5
RHR_TREND_THRESHOLD_BPM = 3.0
SPO2_LOW_THRESHOLD_PCT = 94


def _compute_rhr_trend(
    rhr_by_day: list[float],
) -> tuple[float | None, float | None, float | None, bool]:
    """Return mean_first, mean_second, trend_bpm, and rising flag."""
    if len(rhr_by_day) < 2:
        mean_first = float(rhr_by_day[0]) if rhr_by_day else None
        return mean_first, None, None, False

    half = len(rhr_by_day) // 2
    first_half = rhr_by_day[:half]
    second_half = rhr_by_day[half:]
    mean_first = sum(first_half) / len(first_half)
    mean_second = sum(second_half) / len(second_half)
    trend_bpm = mean_second - mean_first
    return mean_first, mean_second, trend_bpm, trend_bpm >= RHR_TREND_THRESHOLD_BPM


def infer_month_end_date_from_bundle(bundle: HealthDataBundle) -> date:
    """
    Infer the most recent date with data (end of month window).
    Prefers steps max when available, so the analyzed month has step data.
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


def build_monthly_report(
    bundle: HealthDataBundle, month_end_date: date
) -> list[dict[str, Any]]:
    """
    Build metric list for monthly analysis. Filters bundle by the calendar month
    containing month_end_date.
    """
    year, month = month_end_date.year, month_end_date.month
    _, last_day = calendar.monthrange(year, month)
    month_end = date(year, month, last_day)
    month_start = date(year, month, 1)
    day_start_dt = datetime.combine(month_start, datetime.min.time())
    day_end_dt = datetime.combine(month_end, datetime.max.time())

    tw = TimeWindow(
        start=datetime_to_iso(day_start_dt),
        end=datetime_to_iso(day_end_dt),
        resolution="1M",
    )

    month_steps = (
        bundle.steps[
            (bundle.steps["timestamp"] >= day_start_dt)
            & (bundle.steps["timestamp"] <= day_end_dt)
        ]
        if not bundle.steps.empty
        else pd.DataFrame()
    )
    month_hr = (
        bundle.heart_rate[
            (bundle.heart_rate["timestamp"] >= day_start_dt)
            & (bundle.heart_rate["timestamp"] <= day_end_dt)
        ]
        if not bundle.heart_rate.empty
        else pd.DataFrame()
    )
    month_sleep = (
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
    month_exercise = (
        bundle.exercise_sessions[
            (bundle.exercise_sessions["start_time"] >= day_start_dt)
            & (bundle.exercise_sessions["start_time"] <= day_end_dt)
        ]
        if not bundle.exercise_sessions.empty
        else pd.DataFrame()
    )
    month_spo2 = (
        bundle.oxygen_saturation[
            (bundle.oxygen_saturation["timestamp"] >= day_start_dt)
            & (bundle.oxygen_saturation["timestamp"] <= day_end_dt)
        ]
        if not bundle.oxygen_saturation.empty
        else pd.DataFrame()
    )
    month_calories = (
        bundle.calories[
            (bundle.calories["start_time"] <= day_end_dt)
            & (bundle.calories["end_time"] >= day_start_dt)
        ]
        if not bundle.calories.empty
        else pd.DataFrame()
    )
    month_distance = (
        bundle.distance[
            (bundle.distance["start_time"] <= day_end_dt)
            & (bundle.distance["end_time"] >= day_start_dt)
        ]
        if not bundle.distance.empty
        else pd.DataFrame()
    )

    metrics_out: list[dict[str, Any]] = []
    num_days = last_day

    days_with_steps = (
        int(month_steps["timestamp"].dt.date.nunique()) if not month_steps.empty else 0
    )
    last_steps_date = (
        month_steps["timestamp"].max().date() if not month_steps.empty else None
    )
    steps_coverage = days_with_steps / num_days if num_days > 0 else 0.0
    steps_coverage_notes: list[str] = []
    if last_steps_date is not None and last_steps_date < month_end:
        steps_coverage_notes.append(
            f"Month incomplete: latest steps data on {last_steps_date.isoformat()}."
        )
    if days_with_steps < num_days:
        steps_coverage_notes.append(
            f"Steps data available for {days_with_steps} of {num_days} day(s) in month."
        )
    steps_coverage_reliability = (
        "unavailable"
        if days_with_steps == 0
        else ("medium" if steps_coverage < 1.0 else "high")
    )

    # RHR trend: first vs second half of month
    rhr_by_day: list[float] = []
    for d in range(1, num_days + 1):
        day_date = date(year, month, d)
        ds = datetime.combine(day_date, datetime.min.time())
        de = datetime.combine(day_date, datetime.max.time())
        rhr = _rhr_for_day(month_hr, month_sleep, ds, de)
        if rhr is not None:
            rhr_by_day.append(rhr)

    mean_first, mean_second, rhr_trend_bpm, rhr_trend_flag = _compute_rhr_trend(
        rhr_by_day
    )

    metrics_out.append(
        metric(
            metric_name="cardiovascular_fitness_monthly",
            description="RHR trend: first vs second half of month (bpm difference).",
            purpose="Improving RHR (negative trend) indicates better fitness; rising may signal overtraining or stress.",
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
                "flag_rising_rhr": rhr_trend_flag,
            },
            extra={"units": "bpm", "threshold_bpm": RHR_TREND_THRESHOLD_BPM},
        )
    )

    # Ghost days with device-worn classification
    ghost_days = 0
    steps_per_day: dict[str, float] = {}
    steps_per_day_classified: dict[str, dict] = {}
    for d in range(1, num_days + 1):
        day_date = date(year, month, d)
        ds = datetime.combine(day_date, datetime.min.time())
        de = datetime.combine(day_date, datetime.max.time())
        s = _steps_for_day(month_steps, ds, de)
        steps_per_day[day_date.isoformat()] = s
        day_hr_count = (
            int(((month_hr["timestamp"] >= ds) & (month_hr["timestamp"] <= de)).sum())
            if not month_hr.empty
            else 0
        )
        device_worn = day_hr_count >= _DEVICE_WORN_HR_MIN
        steps_per_day_classified[day_date.isoformat()] = {
            "steps": s,
            "device_worn": device_worn,
            "hr_readings": day_hr_count,
        }
        if s < GHOST_DAY_STEPS_THRESHOLD:
            ghost_days += 1

    ghost_days_device_not_worn = sum(
        1
        for v in steps_per_day_classified.values()
        if v["steps"] < GHOST_DAY_STEPS_THRESHOLD and not v["device_worn"]
    )

    metrics_out.append(
        metric(
            metric_name="ghost_days_monthly",
            description=(
                "Days with very low activity (< 500 steps). "
                "Classified into device_not_worn vs sedentary based on HR readings."
            ),
            purpose="Identify illness, recovery, or sedentary patterns. Distinguish from device not worn.",
            variables_used=["steps.timestamp", "steps.steps", "heart_rate.timestamp"],
            time_window=tw,
            n_instances=num_days,
            stats={
                "value": ghost_days,
                "ghost_days_device_not_worn": ghost_days_device_not_worn,
                "ghost_days_sedentary": ghost_days - ghost_days_device_not_worn,
                "flag_has_ghost_days": ghost_days > 0,
            },
            extra={
                "threshold_steps": GHOST_DAY_STEPS_THRESHOLD,
                "device_worn_hr_min": _DEVICE_WORN_HR_MIN,
                "note": "See steps_per_day_classified in weekly report for per-day breakdown.",
            },
            data_quality=build_data_quality(
                coverage=steps_coverage,
                reliability=steps_coverage_reliability,
                notes=[
                    *(
                        [
                            f"{ghost_days_device_not_worn} ghost day(s) classified as device-not-worn."
                        ]
                        if ghost_days_device_not_worn > 0
                        else []
                    ),
                    *steps_coverage_notes,
                ],
            ),
        )
    )

    # Exercise consistency
    exercise_dates: set[date] = set()
    if not month_exercise.empty:
        for _, row in month_exercise.iterrows():
            exercise_dates.add(row["start_time"].date())
    days_with_exercise = len(exercise_dates)

    metrics_out.append(
        metric(
            metric_name="exercise_consistency_monthly",
            description="Number of days with at least one exercise session.",
            purpose="Track habit sustainability.",
            variables_used=[
                "exercise_sessions.start_time",
                "exercise_sessions.end_time",
            ],
            time_window=tw,
            n_instances=num_days,
            stats={
                "days_with_exercise": days_with_exercise,
                "exercise_sessions_total": len(month_exercise),
            },
            extra={"units": "days"},
        )
    )

    # Sleep: nights without data, avg hours
    nights_with_sleep = 0
    total_sleep_hours = 0.0
    for d in range(1, num_days + 1):
        day_date = date(year, month, d)
        ds = datetime.combine(day_date, datetime.min.time())
        de = datetime.combine(day_date, datetime.max.time())
        hrs = _sleep_hours_for_day(month_sleep, ds, de)
        if hrs is not None:
            nights_with_sleep += 1
            total_sleep_hours += hrs
    avg_sleep_hours = (
        total_sleep_hours / nights_with_sleep if nights_with_sleep > 0 else None
    )
    nights_without_data = num_days - nights_with_sleep

    metrics_out.append(
        metric(
            metric_name="sleep_consistency_monthly",
            description="Sleep coverage and average duration.",
            purpose="Nights without data may indicate device not worn or insomnia.",
            variables_used=["sleep_sessions.start_time", "sleep_sessions.end_time"],
            time_window=tw,
            n_instances=nights_with_sleep,
            stats={
                "nights_with_data": nights_with_sleep,
                "nights_without_data": nights_without_data,
                "avg_sleep_hours": avg_sleep_hours,
                "flag_missing_nights": nights_without_data > 3,
            },
            extra={"units": "hours"},
        )
    )

    # SpO2 anomalies
    if not month_spo2.empty and "spo2_pct" in month_spo2.columns:
        spo2_vals = month_spo2["spo2_pct"].dropna()
        spo2_min = float(spo2_vals.min()) if not spo2_vals.empty else None
        spo2_mean = float(spo2_vals.mean()) if not spo2_vals.empty else None
        low_count = int((spo2_vals < SPO2_LOW_THRESHOLD_PCT).sum())
        metrics_out.append(
            metric(
                metric_name="spo2_anomalies_monthly",
                description="SpO2 range and count of low readings (< 94%).",
                purpose="Persistently low SpO2 may indicate apnea or respiratory issues.",
                variables_used=[
                    "oxygen_saturation.timestamp",
                    "oxygen_saturation.spo2_pct",
                ],
                time_window=tw,
                n_instances=len(spo2_vals),
                stats={
                    "min_pct": spo2_min,
                    "mean_pct": spo2_mean,
                    "readings_below_threshold": low_count,
                    "flag_low_spo2": low_count > 0,
                },
                extra={"low_threshold_pct": SPO2_LOW_THRESHOLD_PCT},
            )
        )

    # Activity sustainability: total steps, trend
    total_steps = sum(steps_per_day.values())
    if len(steps_per_day) >= 2:
        sorted_days = sorted(steps_per_day.keys())
        half = len(sorted_days) // 2
        first_half_steps = sum(steps_per_day[d] for d in sorted_days[:half])
        second_half_steps = sum(steps_per_day[d] for d in sorted_days[half:])
        step_trend = second_half_steps - first_half_steps
    else:
        step_trend = None

    metrics_out.append(
        metric(
            metric_name="activity_sustainability_monthly",
            description="Total steps and trend (first vs second half of month).",
            purpose="Declining steps month-over-month may signal burnout or lifestyle change.",
            variables_used=["steps.timestamp", "steps.steps"],
            time_window=tw,
            n_instances=num_days,
            stats={
                "total_steps": total_steps,
                "step_trend_second_minus_first_half": step_trend,
            },
            extra={"units": "steps"},
            data_quality=build_data_quality(
                coverage=steps_coverage,
                reliability=steps_coverage_reliability,
                notes=steps_coverage_notes,
            ),
        )
    )

    # Caloric efficiency: distance / total_kcal (active_kcal not available in current export)
    if not month_calories.empty and not month_distance.empty:
        total_kcal_month = float(month_calories["total_kcal"].sum())
        active_kcal_month = float(month_calories["active_kcal"].sum())
        active_measured = (
            bool(month_calories["active_kcal_measured"].any())
            if "active_kcal_measured" in month_calories.columns
            else False
        )
        distance_m = (
            float(month_distance["distance_m"].sum())
            if "distance_m" in month_distance.columns
            else 0.0
        )
        distance_km = (
            float(month_distance["distance_km"].sum())
            if "distance_km" in month_distance.columns
            else (distance_m / 1000.0 if distance_m > 0 else 0.0)
        )
        # Use total_kcal as the reliable denominator; active_kcal is only used if measured
        efficiency = (
            distance_km / total_kcal_month
            if total_kcal_month > 0 and distance_km > 0
            else None
        )
        metrics_out.append(
            metric(
                metric_name="caloric_efficiency_monthly",
                description=(
                    "Distance per calorie (km / total_kcal). "
                    "Uses total_kcal because active_kcal is not measured in the current export. "
                    "Efficiency includes basal cost, so values differ from active-only formulas."
                ),
                purpose=(
                    "Track locomotion efficiency over time. "
                    "Improving ratio may indicate better fitness. "
                    "Compare only against other months with same formula."
                ),
                variables_used=[
                    "calories.total_kcal",
                    "distance.distance_km",
                ],
                time_window=tw,
                n_instances=len(month_calories),
                stats={
                    "value": efficiency,
                    "total_kcal": total_kcal_month,
                    "active_kcal_measured": active_measured,
                    "total_distance_km": distance_km,
                    **({"active_kcal": active_kcal_month} if active_measured else {}),
                },
                extra={"units": "km/total_kcal", "kcal_source": "total_kcal"},
                data_quality=build_data_quality(
                    coverage=1.0 if efficiency is not None else 0.0,
                    reliability="medium",
                    notes=[
                        "Efficiency uses total_kcal (active + basal), not active_kcal alone. "
                        "Cannot compare with standard km/active_kcal benchmarks."
                    ],
                ),
            )
        )

    # Best exercise hour: hour with most exercise activity
    if not month_exercise.empty:
        month_exercise_copy = month_exercise.copy()
        month_exercise_copy["hour"] = month_exercise_copy["start_time"].dt.hour
        hour_counts = month_exercise_copy.groupby("hour", as_index=True).size()
        best_hour = int(hour_counts.idxmax()) if not hour_counts.empty else None
        best_hour_sessions = int(hour_counts.max()) if not hour_counts.empty else None
    else:
        best_hour = None
        best_hour_sessions = None

    metrics_out.append(
        metric(
            metric_name="best_exercise_hour_monthly",
            description="Hour of day with most exercise sessions.",
            purpose="Optimize timing based on historical adherence.",
            variables_used=["exercise_sessions.start_time"],
            time_window=tw,
            n_instances=len(month_exercise),
            stats={
                "best_hour": best_hour,
                "sessions_at_best_hour": best_hour_sessions,
            },
            extra={"units": "hour (0-23)"},
        )
    )

    return metrics_out
