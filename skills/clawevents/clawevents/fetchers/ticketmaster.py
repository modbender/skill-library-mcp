"""Ticketmaster Discovery API v2 — Barcelona + NYC.

Free API key: https://developer.ticketmaster.com/
Env var: TICKETMASTER_API_KEY
Coverage: 230K+ events, strong in US + Europe.
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

BASE_URL = "https://app.ticketmaster.com/discovery/v2/events.json"

# City → Ticketmaster city/country params
_CITY_PARAMS: dict[City, dict] = {
    City.BARCELONA: {"city": "Barcelona", "countryCode": "ES"},
    City.NEW_YORK:  {"city": "New York",  "countryCode": "US", "stateCode": "NY"},
}

# EventType → Ticketmaster classificationName / genre
_TYPE_TO_TM: dict[EventType, dict] = {
    EventType.CONCERT:   {"classificationName": "music"},
    EventType.JAZZ:      {"classificationName": "music", "genreId": "KnvZfZ7vAve"},  # Jazz genre
    EventType.THEATRE:   {"classificationName": "arts & theatre"},
    EventType.COMEDY:    {"classificationName": "arts & theatre", "subGenreId": "KZazBEonSMnZfZ7v7na"},
    EventType.SPORT:     {"classificationName": "sports"},
    EventType.FESTIVAL:  {"classificationName": "music", "typeId": "KZFzniwnSyZfZ7v7nE"},
    EventType.FAMILY:    {"classificationName": "family"},
}


def _classify_from_tm(seg: str, genre: str) -> list[EventType]:
    seg   = (seg   or "").lower()
    genre = (genre or "").lower()
    types = []
    if "jazz" in genre:
        types.append(EventType.JAZZ)
    if "music" in seg:
        types.append(EventType.CONCERT)
    if "theatre" in seg or "arts" in seg:
        types.append(EventType.THEATRE)
    if "comedy" in genre:
        types.append(EventType.COMEDY)
    if "sport" in seg:
        types.append(EventType.SPORT)
    if "family" in seg:
        types.append(EventType.FAMILY)
        return types + [AgeGroup.FAMILY]  # type: ignore — handled separately
    return types or [EventType.OTHER]


def _parse_dt(date_str: str, time_str: str) -> Optional[datetime]:
    if not date_str:
        return None
    try:
        if time_str:
            return datetime.fromisoformat(f"{date_str}T{time_str}")
        return datetime.fromisoformat(date_str)
    except Exception:
        return None


class TicketmasterFetcher(BaseFetcher):
    source_name = "ticketmaster"
    supported_cities = [City.BARCELONA, City.NEW_YORK]

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("TICKETMASTER_API_KEY", "")

    def fetch(
        self,
        city: City,
        start: datetime,
        end: datetime,
        event_types: Optional[list[EventType]] = None,
        limit: int = 50,
    ) -> list[Event]:
        if not self.api_key:
            log.warning("TICKETMASTER_API_KEY not set — skipping Ticketmaster fetcher")
            return []
        if city not in _CITY_PARAMS:
            return []

        city_params = _CITY_PARAMS[city]

        # If specific types requested, make separate calls per type-mapping and merge
        if event_types:
            # Pick the first matching TM type params; fallback to no classification filter
            tm_extra = {}
            for et in event_types:
                if et in _TYPE_TO_TM:
                    tm_extra = _TYPE_TO_TM[et]
                    break
        else:
            tm_extra = {}

        params = {
            "apikey":          self.api_key,
            "startDateTime":   start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "endDateTime":     end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "size":            min(limit, 200),
            "sort":            "date,asc",
            **city_params,
            **tm_extra,
        }

        try:
            resp = requests.get(BASE_URL, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            log.warning("Ticketmaster API error: %s", exc)
            return []

        raw_events = (
            data.get("_embedded", {}).get("events", [])
            if "_embedded" in data else []
        )

        events: list[Event] = []
        for item in raw_events:
            title = item.get("name", "")
            url   = item.get("url", "")

            # Classification
            classifications = item.get("classifications", [{}])
            seg   = classifications[0].get("segment", {}).get("name", "") if classifications else ""
            genre = classifications[0].get("genre",   {}).get("name", "") if classifications else ""
            types = _classify_from_tm(seg, genre)
            # Fix: if AgeGroup accidentally in types list (from family shortcut above), clean
            types = [t for t in types if isinstance(t, EventType)]

            age_groups: list[AgeGroup] = []
            if "family" in seg.lower() or "family" in genre.lower():
                age_groups = [AgeGroup.FAMILY]
            else:
                age_groups = [AgeGroup.ADULTS]

            # Time
            dates  = item.get("dates", {}).get("start", {})
            start_dt = _parse_dt(dates.get("localDate", ""), dates.get("localTime", ""))
            end_dates = item.get("dates", {}).get("end", {})
            end_dt   = _parse_dt(end_dates.get("localDate", ""), end_dates.get("localTime", "")) if end_dates else None

            # Venue
            venues     = item.get("_embedded", {}).get("venues", [{}])
            venue      = venues[0] if venues else {}
            venue_name = venue.get("name", "")
            address    = venue.get("address", {}).get("line1", "")
            hood       = venue.get("city", {}).get("name", "")

            # Price
            price_ranges = item.get("priceRanges", [])
            price_min = price_ranges[0].get("min") if price_ranges else None
            price_max = price_ranges[0].get("max") if price_ranges else None
            currency  = price_ranges[0].get("currency", "") if price_ranges else ""

            # Image
            images    = item.get("images", [])
            image_url = images[0].get("url", "") if images else ""

            events.append(Event(
                id          = item.get("id", ""),
                source      = self.source_name,
                city        = city,
                title       = title,
                description = "",
                url         = url,
                image_url   = image_url,
                event_types = types,
                age_groups  = age_groups,
                start       = start_dt,
                end         = end_dt,
                venue_name  = venue_name,
                address     = address,
                neighborhood= hood,
                is_free     = (price_min == 0) if price_min is not None else False,
                price_min   = price_min,
                price_max   = price_max,
                currency    = currency,
                ticket_url  = url,
            ))

        return events
