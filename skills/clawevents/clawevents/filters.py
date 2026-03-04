"""Filter, deduplicate, and rank events."""

from __future__ import annotations
from datetime import datetime
from typing import Optional

from .models import AgeGroup, City, Event, EventType, TimeOfDay


def filter_events(
    events: list[Event],
    cities:       Optional[list[City]]      = None,
    event_types:  Optional[list[EventType]] = None,
    age_groups:   Optional[list[AgeGroup]]  = None,
    time_of_day:  Optional[list[TimeOfDay]] = None,
    start:        Optional[datetime]        = None,
    end:          Optional[datetime]        = None,
    free_only:    bool                      = False,
) -> list[Event]:
    out = events

    if cities:
        out = [e for e in out if e.city in cities]

    if event_types:
        out = [e for e in out if any(t in e.event_types for t in event_types)]

    if age_groups:
        out = [e for e in out if any(a in e.age_groups for a in age_groups)]

    if time_of_day:
        out = [e for e in out if e.time_of_day in time_of_day]

    if start:
        out = [e for e in out if e.start is None or e.start >= start]

    if end:
        out = [e for e in out if e.start is None or e.start <= end]

    if free_only:
        out = [e for e in out if e.is_free]

    return out


def deduplicate(events: list[Event]) -> list[Event]:
    """Remove near-duplicate events (same title + same start time across sources)."""
    seen: set[str] = set()
    out: list[Event] = []
    for e in events:
        key = f"{e.title.lower().strip()}|{e.start.isoformat() if e.start else ''}"
        if key not in seen:
            seen.add(key)
            out.append(e)
    return out


def rank_events(events: list[Event]) -> list[Event]:
    """Sort by start time; events with no time go last."""
    return sorted(events, key=lambda e: (e.start is None, e.start or datetime.max))
