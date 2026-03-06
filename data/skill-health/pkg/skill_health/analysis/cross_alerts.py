"""
Cross-temporal alerts: detect patterns by combining metrics from hourly, daily, weekly, monthly.
Reads JSON outputs from previous analyses.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

RHR_RISE_THRESHOLD_BPM = 5.0
SPO2_LOW_THRESHOLD_PCT = 95.0
SPO2_VERY_LOW_THRESHOLD_PCT = 94.0


def _find_metric(metrics: list[dict[str, Any]], name: str) -> dict[str, Any] | None:
    """Return the first metric with metric_name equal to name, or None."""
    for m in metrics:
        if m.get("metric_name") == name:
            return m
    return None


def _find_metric_with_prefix(
    metrics: list[dict[str, Any]], prefix: str
) -> dict[str, Any] | None:
    """Return the first metric with metric_name that starts with prefix, or None."""
    for m in metrics:
        metric_name = m.get("metric_name", "")
        if isinstance(metric_name, str) and metric_name.startswith(prefix):
            return m
    return None


def _get_stat(metric: dict[str, Any] | None, key: str) -> Any:
    """Return stats[key] from metric, or None."""
    if metric is None:
        return None
    return metric.get("stats", {}).get(key)


def load_metrics_from_outputs_dir(outputs_dir: Path) -> dict[str, list[dict[str, Any]]]:
    """
    Load the most recent JSON report of each type from outputs_dir.

    Returns dict with keys: "hourly", "daily", "weekly", "monthly", "sleep".
    Each value is a list of metric dicts (empty list if no file found).
    """
    result: dict[str, list[dict[str, Any]]] = {
        "hourly": [],
        "daily": [],
        "weekly": [],
        "monthly": [],
        "sleep": [],
    }
    if not outputs_dir.exists() or not outputs_dir.is_dir():
        return result

    patterns = {
        "hourly": "hourly_*.json",
        "daily": "daily_*.json",
        "weekly": "weekly_*.json",
        "monthly": "monthly_*.json",
        "sleep": "sleep_*.json",
    }
    for key, pattern in patterns.items():
        files = sorted(outputs_dir.glob(pattern), reverse=True)
        if files:
            try:
                content = json.loads(files[0].read_text(encoding="utf-8"))
                result[key] = content if isinstance(content, list) else []
            except (json.JSONDecodeError, OSError):
                pass
    return result


def build_cross_alerts(
    metrics_context: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    """
    Detect cross-temporal patterns from metrics. Returns list of alert dicts.

    Args:
        metrics_context: Dict from load_metrics_from_outputs_dir with keys
            "hourly", "daily", "weekly", "monthly".
    """
    alerts: list[dict[str, Any]] = []
    daily = metrics_context.get("daily", [])
    weekly = metrics_context.get("weekly", [])
    monthly = metrics_context.get("monthly", [])
    sleep = metrics_context.get("sleep", [])

    # Pre-illness: RHR↑ 5+ bpm + SpO2↓ + fragmented sleep + low steps
    rhr_trend = _find_metric(weekly, "rhr_trending_weekly")
    rhr_rise = _get_stat(rhr_trend, "value")
    spo2_weekly = _find_metric(weekly, "spo2_variance_weekly")
    spo2_sleep = _find_metric_with_prefix(sleep, "spo2_sleep_summary_last_")
    spo2_min_sleep = _get_stat(spo2_sleep, "min_pct") if spo2_sleep else None
    spo2_min_week = _get_stat(spo2_weekly, "min_pct") if spo2_weekly else None
    spo2_min = (
        spo2_min_sleep if spo2_min_sleep is not None else spo2_min_week
    )
    sleep_frag = _find_metric_with_prefix(sleep, "sleep_fragmentation_hr_spikes_last_")
    frag_events = _get_stat(sleep_frag, "fragmentation_events") or 0
    rhr_sleep = _find_metric_with_prefix(sleep, "resting_hr_during_sleep_last_")
    steps_daily = _find_metric(daily, "activity_windows_daily")
    dead_hours = _get_stat(steps_daily, "dead_hours") or 0

    if (
        rhr_rise is not None
        and rhr_rise >= RHR_RISE_THRESHOLD_BPM
        and (spo2_min is None or spo2_min < SPO2_LOW_THRESHOLD_PCT)
        and frag_events > 5
        and dead_hours >= 10
    ):
        alerts.append(
            {
                "pattern_id": "pre_illness",
                "pattern_name": "Pre-illness signature",
                "severity": "high",
                "signals": {
                    "rhr_rise_bpm": rhr_rise,
                    "spo2_min_pct": spo2_min,
                    "sleep_fragmentation_events": frag_events,
                    "dead_hours": dead_hours,
                },
                "message": "RHR up 5+ bpm, low SpO2, fragmented sleep and reduced activity. Possible illness in 24-48h.",
            }
        )

    # Overtraining: RHR elevated + more exercise + worse sleep (weekly)
    if rhr_trend and _get_stat(rhr_trend, "flag_rising_rhr"):
        ex_cons = _find_metric(weekly, "exercise_consistency_weekly")
        sleep_debt = _find_metric(weekly, "sleep_debt_weekly")
        debt = _get_stat(sleep_debt, "value") or 0
        days_ex = _get_stat(ex_cons, "days_with_exercise") or 0
        if debt > 5 and days_ex >= 4:
            alerts.append(
                {
                    "pattern_id": "overtraining",
                    "pattern_name": "Overtraining in development",
                    "severity": "medium",
                    "signals": {
                        "rhr_rising": True,
                        "sleep_debt_hours": debt,
                        "days_with_exercise": days_ex,
                    },
                    "message": "RHR elevated with high exercise load and sleep debt. Consider rest.",
                }
            )

    # Sleep apnea: SpO2 <95% persistent + fragmentation
    if spo2_min is not None and spo2_min < SPO2_LOW_THRESHOLD_PCT and frag_events > 3:
        alerts.append(
            {
                "pattern_id": "sleep_apnea",
                "pattern_name": "Possible sleep apnea",
                "severity": "medium",
                "signals": {
                    "spo2_min_pct": spo2_min,
                    "sleep_fragmentation_events": frag_events,
                },
                "message": "Persistently low SpO2 with sleep fragmentation. Consider evaluation.",
            }
        )

    # Burnout: steps down + worse sleep + RHR up + less exercise (monthly)
    cv_fitness = _find_metric(monthly, "cardiovascular_fitness_monthly")
    activity = _find_metric(monthly, "activity_sustainability_monthly")
    sleep_monthly = _find_metric(monthly, "sleep_consistency_monthly")
    ex_monthly = _find_metric(monthly, "exercise_consistency_monthly")

    step_trend = _get_stat(activity, "step_trend_second_minus_first_half")
    rhr_month_trend = _get_stat(cv_fitness, "value")
    missing_nights = _get_stat(sleep_monthly, "nights_without_data") or 0
    days_ex_month = _get_stat(ex_monthly, "days_with_exercise") or 0

    if (
        step_trend is not None
        and step_trend < -5000
        and (rhr_month_trend is None or rhr_month_trend >= 2)
        and missing_nights > 5
        and days_ex_month < 10
    ):
        alerts.append(
            {
                "pattern_id": "burnout",
                "pattern_name": "Burnout pattern",
                "severity": "medium",
                "signals": {
                    "step_trend": step_trend,
                    "rhr_trend_bpm": rhr_month_trend,
                    "nights_without_sleep_data": missing_nights,
                    "days_with_exercise": days_ex_month,
                },
                "message": "Declining steps, elevated RHR, poor sleep coverage and less exercise. Sustainability at risk.",
            }
        )

    # Device inconsistency: steps present but very few HR readings (daily)
    steps_metric = _find_metric(daily, "exercise_vs_spontaneous_ratio_daily")
    if steps_metric and rhr_sleep:
        steps_instances = steps_metric.get("n_instances", 0) or 0
        hr_instances = rhr_sleep.get("n_instances", 0) or 0
        if steps_instances > 20 and hr_instances < 5:
            alerts.append(
                {
                    "pattern_id": "device_inconsistency",
                    "pattern_name": "Device inconsistency",
                    "severity": "low",
                    "signals": {
                        "steps_data_points": steps_instances,
                        "heart_rate_data_points": hr_instances,
                    },
                    "message": "Steps data present but very few heart rate readings. Check wearable fit/settings.",
                }
            )

    return alerts
