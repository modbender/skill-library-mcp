"""Eventbrite API — all 3 cities.

Free API token: https://www.eventbrite.com/platform/api
Env var: EVENTBRITE_TOKEN
Covers: tech events, community events, cultural events, family.
"""

from __future__ import annotations
import logging
import os
from datetime import datetime
from typing import Optional

import requests

from ..models import AgeGroup, City, Event, EventType
from .base import BaseFetcher

log = logging.getLogger(__name__)

BASE_URL = "https://www.eventbriteapi.com/v3/events/search/"

_CITY_LOCATIONS: dict[City, str] = {
    City.TEL_AVIV:  "Tel Aviv, Israel",
    City.BARCELONA: "Barcelona, Spain",
    City.NEW_YORK:  "New York, NY, United States",
}

# Eventbrite category IDs
_CATEGORY_IDS: dict[EventType, str] = {
    EventType.CONCERT:   "103",  # Music
    EventType.JAZZ:      "103",
    EventType.THEATRE:   "105",  # Performing & Visual Arts
    EventType.ART:       "105",
    EventType.COMEDY:    "105",
    EventType.SPORT:     "108",
    EventType.FAMILY:    "115",  # Family & Education
    EventType.FESTIVAL:  "103",
    EventType.COMMUNITY: "113",
}

_TYPE_KEYWORDS: dict[EventType, list[str]] = {
    EventType.JAZZ:      ["jazz"],
    EventType.CONCERT:   ["concert", "live music", "gig"],
    EventType.THEATRE:   ["theatre", "theater", "play", "performance"],
    EventType.CINEMA:    ["film", "cinema", "screening", "movie"],
    EventType.COMEDY:    ["comedy", "stand up", "stand-up"],
    EventType.ART:       ["art", "exhibition", "gallery"],
    EventType.FESTIVAL:  ["festival"],
    EventType.FAMILY:    ["family", "kids", "children"],
}


def _classify_types(title: str, desc: str) -> list[EventType]:
    text = (title + " " + desc).lower()
    found = [t for t, kws in _TYPE_KEYWORDS.items() if any(k in text for k in kws)]
    return found or [EventType.OTHER]


def _parse_dt(val: Optional[dict]) -> Optional[datetime]:
    if not val:
        return None
    local = val.get("local") or val.get("utc")
    if not local:
        return None
    try:
        return datetime.fromisoformat(local.replace("Z", "+00:00"))
    except Exception:
        return None


class EventbriteFetcher(BaseFetcher):
    source_name = "eventbrite"
    supported_cities = [City.TEL_AVIV, City.BARCELONA, City.NEW_YORK]

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.environ.get("EVENTBRITE_TOKEN", "")

    def fetch(
        self,
        city: City,
        start: datetime,
        end: datetime,
        event_types: Optional[list[EventType]] = None,
        limit: int = 50,
    ) -> list[Event]:
        if not self.token:
            log.warning("EVENTBRITE_TOKEN not set — skipping Eventbrite fetcher")
            return []

        location = _CITY_LOCATIONS.get(city)
        if not location:
            return []

        # Pick category for main type filter
        category = None
        if event_types:
            for et in event_types:
                if et in _CATEGORY_IDS:
                    category = _CATEGORY_IDS[et]
                    break

        params: dict = {
            "location.address":         location,
            "location.within":          "10km",
            "start_date.range_start":   start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "start_date.range_end":     end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "page_size":                min(limit, 50),
            "expand":                   "venue,ticket_classes",
        }
        if category:
            params["categories"] = category

        headers = {"Authorization": f"Bearer {self.token}"}

        try:
            resp = requests.get(BASE_URL, params=params, headers=headers, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            log.warning("Eventbrite API error: %s", exc)
            return []

        events: list[Event] = []
        for item in data.get("events", []):
            title = item.get("name", {}).get("text", "")
            desc  = item.get("description", {}).get("text", "") or ""

            types = _classify_types(title, desc)
            if event_types and not any(t in types for t in event_types):
                continue

            age_str   = item.get("age_restriction", "") or ""
            age_groups = [AgeGroup.FAMILY] if "family" in title.lower() or "kids" in title.lower() else [AgeGroup.ADULTS]

            venue_obj  = item.get("venue") or {}
            venue_name = venue_obj.get("name", "")
            address    = (venue_obj.get("address") or {}).get("localized_address_display", "")

            # Price
            tickets    = item.get("ticket_classes") or []
            prices     = [t.get("cost", {}).get("major_value") for t in tickets if t.get("cost")]
            prices     = [float(p) for p in prices if p]
            is_free    = item.get("is_free", False) or (all(p == 0 for p in prices) if prices else False)
            price_min  = min(prices) if prices and not is_free else None
            price_max  = max(prices) if prices and not is_free else None
            currency   = (tickets[0].get("cost") or {}).get("currency", "") if tickets else ""

            events.append(Event(
                id          = item.get("id", ""),
                source      = self.source_name,
                city        = city,
                title       = title,
                description = desc[:400],
                url         = item.get("url", ""),
                image_url   = (item.get("logo") or {}).get("url", ""),
                event_types = types,
                age_groups  = age_groups,
                start       = _parse_dt(item.get("start")),
                end         = _parse_dt(item.get("end")),
                venue_name  = venue_name,
                address     = address,
                is_free     = is_free,
                price_min   = price_min,
                price_max   = price_max,
                currency    = currency,
                ticket_url  = item.get("url", ""),
            ))

        return events
