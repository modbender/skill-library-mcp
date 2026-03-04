"""NYC Open Data events — free, no key required.

Two datasets:
  - NYC Events Calendar: https://api-portal.nyc.gov/ (city-sponsored events)
  - NYC Parks Special Events: data.cityofnewyork.us (Socrata)
"""

from __future__ import annotations
import hashlib
import logging
from datetime import datetime
from typing import Optional

import requests

from ..models import AgeGroup, City, Event, EventType
from .base import BaseFetcher

log = logging.getLogger(__name__)

# NYC Parks Special Events (Socrata)
PARKS_URL = "https://data.cityofnewyork.us/resource/6v4b-5gp4.json"

_TYPE_KEYWORDS: dict[EventType, list[str]] = {
    EventType.CONCERT:   ["concert", "music", "live"],
    EventType.JAZZ:      ["jazz"],
    EventType.CINEMA:    ["film", "movie", "screening", "cinema"],
    EventType.FAMILY:    ["family", "kids", "children"],
    EventType.COMEDY:    ["comedy"],
    EventType.ART:       ["art", "exhibition"],
    EventType.FESTIVAL:  ["festival"],
    EventType.SPORT:     ["sport", "run", "marathon", "fitness", "dance"],
}


def _classify_types(title: str, desc: str) -> list[EventType]:
    text = (title + " " + desc).lower()
    found = [t for t, kws in _TYPE_KEYWORDS.items() if any(k in text for k in kws)]
    return found or [EventType.COMMUNITY]


def _parse_dt(val: Optional[str]) -> Optional[datetime]:
    if not val:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(val[:26], fmt[:len(val[:26])])
        except ValueError:
            continue
    return None


class NYCOpenDataFetcher(BaseFetcher):
    source_name = "nyc_open_data"
    supported_cities = [City.NEW_YORK]

    def fetch(
        self,
        city: City,
        start: datetime,
        end: datetime,
        event_types: Optional[list[EventType]] = None,
        limit: int = 50,
    ) -> list[Event]:
        if city != City.NEW_YORK:
            return []

        params = {
            "$where":  f"date_and_time >= '{start.strftime('%Y-%m-%dT%H:%M:%S')}' AND date_and_time <= '{end.strftime('%Y-%m-%dT%H:%M:%S')}'",
            "$limit":  limit,
            "$order":  "date_and_time ASC",
        }

        try:
            resp = requests.get(PARKS_URL, params=params, timeout=15)
            resp.raise_for_status()
            items = resp.json()
        except Exception as exc:
            log.warning("NYC Open Data error: %s", exc)
            return []

        events: list[Event] = []
        for item in items:
            title = item.get("event_name") or item.get("eventname") or item.get("name") or ""
            desc  = item.get("category") or item.get("event_type") or ""
            types = _classify_types(title, desc)

            if event_types and not any(t in types for t in event_types):
                continue

            age_groups = [AgeGroup.FAMILY] if "family" in types or "kids" in title.lower() else [AgeGroup.ADULTS]

            uid = hashlib.md5(f"nyc:{title}:{item.get('startdate','')}".encode()).hexdigest()[:12]
            events.append(Event(
                id          = item.get("eventid") or uid,
                source      = self.source_name,
                city        = City.NEW_YORK,
                title       = title,
                description = desc[:400],
                url         = item.get("eventurl") or "https://www.nycgovparks.org/events",
                event_types = types,
                age_groups  = age_groups,
                start       = _parse_dt(item.get("date_and_time") or item.get("startdate")),
                end         = None,
                venue_name  = item.get("location") or "",
                address     = item.get("locationtype") or "",
                neighborhood= item.get("borough") or "",
                is_free     = True,  # Parks events are free
                ticket_url  = item.get("eventurl") or "",
            ))

        return events
