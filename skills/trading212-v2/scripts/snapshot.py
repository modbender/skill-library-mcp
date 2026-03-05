"""
Portfolio snapshot storage.

Writes and reads daily JSON snapshots so that the summary mode can compare
today's portfolio value with previous days and track performance over
longer periods (week, month, quarter, year).

Snapshot files are stored in ``<project_root>/snapshots/YYYY-MM-DD.json``.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Default directory: <project_root>/snapshots/
_DEFAULT_DIR = Path(__file__).resolve().parents[3] / "snapshots"

# Named periods and their approximate lookback in days.
PERIODS: Dict[str, int] = {
    "1w": 7,
    "1m": 30,
    "3m": 90,
    "1y": 365,
}


def _snapshot_dir() -> Path:
    """Return the snapshot directory, creating it if needed."""
    d = Path(os.environ.get("TRADING212_SNAPSHOT_DIR", str(_DEFAULT_DIR)))
    d.mkdir(parents=True, exist_ok=True)
    return d


def _path_for_date(date_str: str) -> Path:
    return _snapshot_dir() / f"{date_str}.json"


# ------------------------------------------------------------------
# Write
# ------------------------------------------------------------------


def save_snapshot(
    positions: List[Dict[str, Any]],
    cash: float,
    total_value: float,
    date_str: Optional[str] = None,
) -> Path:
    """Persist a portfolio snapshot for the given date (default: today UTC).

    Parameters
    ----------
    positions:
        List of position dicts.  Each must contain at least
        ``ticker``, ``value`` (currentValue in account currency), and
        ``quantity``.  Optionally ``avg_price`` and ``current_price``
        for enriched snapshots.
    cash:
        Available cash in account currency.
    total_value:
        Total portfolio value (positions + cash).
    date_str:
        ISO date string (``YYYY-MM-DD``).  Defaults to today (UTC).

    Returns
    -------
    Path to the written file.
    """
    if date_str is None:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    snapshot: Dict[str, Any] = {
        "date": date_str,
        "total_value": round(total_value, 2),
        "cash": round(cash, 2),
        "positions": [
            {
                "ticker": p["ticker"],
                "value": round(p["value"], 2),
                "quantity": p["quantity"],
                "avg_price": round(p.get("avg_price", 0), 4) if p.get("avg_price") else None,
                "current_price": round(p.get("current_price", 0), 4) if p.get("current_price") else None,
            }
            for p in positions
        ],
    }

    fp = _path_for_date(date_str)
    with open(fp, "w", encoding="utf-8") as fh:
        json.dump(snapshot, fh, indent=2, ensure_ascii=False)
    return fp


# ------------------------------------------------------------------
# Read
# ------------------------------------------------------------------


def load_snapshot(date_str: str) -> Optional[Dict[str, Any]]:
    """Load a snapshot for the given date, or ``None`` if it does not exist."""
    fp = _path_for_date(date_str)
    if not fp.exists():
        return None
    with open(fp, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_previous_snapshot(
    reference_date: Optional[str] = None,
    max_lookback_days: int = 7,
) -> Optional[Dict[str, Any]]:
    """Find the most recent snapshot *before* ``reference_date``.

    Looks back up to ``max_lookback_days`` calendar days.  Returns ``None``
    if no snapshot is found in that window.
    """
    if reference_date is None:
        ref = datetime.now(timezone.utc).date()
    else:
        ref = datetime.strptime(reference_date, "%Y-%m-%d").date()

    for offset in range(1, max_lookback_days + 1):
        day = ref - timedelta(days=offset)
        snap = load_snapshot(day.strftime("%Y-%m-%d"))
        if snap is not None:
            return snap
    return None


def load_snapshot_for_period(
    period: str,
    reference_date: Optional[str] = None,
    tolerance_days: int = 3,
) -> Optional[Dict[str, Any]]:
    """Load the snapshot closest to the target date for a named period.

    Parameters
    ----------
    period:
        One of ``"1w"``, ``"1m"``, ``"3m"``, ``"1y"``.
    reference_date:
        ISO date string for "today".  Defaults to today (UTC).
    tolerance_days:
        How many days around the target date to search.

    Returns ``None`` if no snapshot is found near the target date.
    """
    lookback = PERIODS.get(period)
    if lookback is None:
        return None

    if reference_date is None:
        ref = datetime.now(timezone.utc).date()
    else:
        ref = datetime.strptime(reference_date, "%Y-%m-%d").date()

    target = ref - timedelta(days=lookback)

    # Search around the target date (prefer exact, then nearby).
    for offset in range(0, tolerance_days + 1):
        for delta in ([0] if offset == 0 else [offset, -offset]):
            candidate = target + timedelta(days=delta)
            if candidate >= ref:
                continue
            snap = load_snapshot(candidate.strftime("%Y-%m-%d"))
            if snap is not None:
                return snap

    return None


def compute_performance(
    current_total: float,
    reference_date: Optional[str] = None,
) -> Dict[str, Optional[Dict[str, float]]]:
    """Compute performance over multiple periods relative to snapshots.

    Returns a dict like::

        {
            "1w": {"change_eur": 50.0, "change_pct": 0.4},
            "1m": {"change_eur": 200.0, "change_pct": 1.6},
            "3m": null,
            "1y": null,
        }
    """
    result: Dict[str, Optional[Dict[str, float]]] = {}

    for period_key in PERIODS:
        snap = load_snapshot_for_period(period_key, reference_date=reference_date)
        if snap is None:
            result[period_key] = None
            continue

        prev_total = snap.get("total_value", 0)
        if prev_total <= 0:
            result[period_key] = None
            continue

        change_eur = round(current_total - prev_total, 2)
        change_pct = round((change_eur / prev_total) * 100, 4)
        result[period_key] = {
            "change_eur": change_eur,
            "change_pct": change_pct,
        }

    return result
