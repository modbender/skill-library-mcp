"""
Helpers for building JSON report payloads: time windows, metric dicts, numeric stats.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import pandas as pd


@dataclass
class TimeWindow:
    """Time window for a metric: start, end (ISO), and resolution (e.g. '1h', '1d')."""

    start: str
    end: str
    resolution: str


def datetime_to_iso(dt: datetime) -> str:
    """Return compact ISO string (minutes precision); use UTC if naive."""
    normalized = dt.replace(second=0, microsecond=0)
    if normalized.tzinfo is None:
        normalized = normalized.replace(tzinfo=timezone.utc)
    return normalized.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def _round_floats(value: Any, ndigits: int = 2) -> Any:
    """Recursively round floats in dicts/lists for compact output."""
    if isinstance(value, float):
        return round(value, ndigits)
    if isinstance(value, list):
        return [_round_floats(v, ndigits=ndigits) for v in value]
    if isinstance(value, dict):
        return {k: _round_floats(v, ndigits=ndigits) for k, v in value.items()}
    return value


def describe_numeric(series: pd.Series) -> dict[str, Any]:
    """
    Return summary stats for a numeric series (mean, std, min, quartiles, max).
    Returns dict with None values if series is empty or all-NaN.
    """
    empty_stats = {
        "mean": None,
        "std": None,
        "min": None,
        "p25": None,
        "p50": None,
        "p75": None,
        "max": None,
    }
    if series.empty:
        return empty_stats
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if clean.empty:
        return empty_stats
    return {
        "mean": float(clean.mean()),
        "std": float(clean.std(ddof=0)) if len(clean) > 1 else 0.0,
        "min": float(clean.min()),
        "p25": float(clean.quantile(0.25)),
        "p50": float(clean.quantile(0.50)),
        "p75": float(clean.quantile(0.75)),
        "max": float(clean.max()),
    }


def metric(
    *,
    metric_name: str,
    description: str,
    purpose: str,
    variables_used: list[str],
    time_window: TimeWindow,
    n_instances: int,
    stats: dict[str, Any],
    extra: dict[str, Any] | None = None,
    data_quality: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Build a single metric dict for JSON output.

    Args:
        metric_name: Short identifier.
        description: What the metric measures.
        purpose: Why it is useful (alerts, trends, etc.).
        variables_used: List of data sources/columns used.
        time_window: Start/end/resolution of the analysis window.
        n_instances: Number of data points used.
        stats: Value(s) and optional distribution (e.g. value, mean, min, max).
        extra: Optional units, thresholds, notes.
        data_quality: Optional quality metadata for the consuming LLM.
            Keys: coverage (float 0-1), reliability ("high"/"medium"/"low"/"unavailable"),
            notes (list[str] with caveats).

    Returns:
        Dict suitable for JSON serialization.
    """
    payload: dict[str, Any] = {
        "metric_name": metric_name,
        "description": description,
        "purpose": purpose,
        "variables_used": variables_used,
        "time_window": {
            "s": time_window.start,
            "e": time_window.end,
            "r": time_window.resolution,
        },
        "n_instances": int(n_instances),
        "stats": _round_floats(stats),
    }
    if extra:
        payload["extra"] = _round_floats(extra)
    if data_quality:
        notes = data_quality.get("notes", [])
        compact = {k: v for k, v in data_quality.items() if k != "notes"}
        if notes:
            compact["notes"] = notes
        payload["data_quality"] = _round_floats(compact)
    return payload


def build_data_quality(
    *,
    coverage: float,
    reliability: str,
    notes: list[str] | None = None,
) -> dict[str, Any]:
    """
    Build a data_quality dict for use in metric().

    Args:
        coverage: Fraction of the period with actual data (0.0–1.0).
        reliability: "high" (n>=20, complete data), "medium" (n 5-19, partial),
                     "low" (n<5, important caveats), "unavailable" (cannot compute).
        notes: List of human-readable caveats for the consuming LLM.

    Returns:
        Dict with coverage, reliability and notes.
    """
    return {
        "cov": float(coverage),
        "rel": reliability,
        "notes": notes or [],
    }
