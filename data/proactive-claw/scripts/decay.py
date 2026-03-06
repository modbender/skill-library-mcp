#!/usr/bin/env python3
"""
decay.py — Temporal decay weighting utilities.

Provides exponential decay functions for recency-weighted scoring.
Used by proactivity_engine, energy_predictor, adaptive_notifications, memory.

Not a standalone CLI — imported as a library by other modules.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone


def decay_weight(date_str: str, half_life_days: int = 90) -> float:
    """Return exponential decay weight for a date relative to now.
    Recent dates → ~1.0, old dates → approaches 0.0.
    """
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        days_ago = (datetime.now(timezone.utc) - dt).total_seconds() / 86400
        if days_ago < 0:
            return 1.0  # future dates get full weight
        return math.exp(-0.693 * days_ago / max(half_life_days, 1))
    except Exception:
        return 0.5  # fallback for unparseable dates


def weighted_average(values_and_dates: list, half_life_days: int = 90) -> float:
    """Compute decay-weighted average of (value, date_str) pairs."""
    if not values_and_dates:
        return 0.0
    total_weight = 0.0
    weighted_sum = 0.0
    for value, date_str in values_and_dates:
        w = decay_weight(date_str, half_life_days)
        weighted_sum += value * w
        total_weight += w
    return weighted_sum / total_weight if total_weight > 0 else 0.0
