"""ClawEvents engine — orchestrates fetchers, dedup, filter, rank."""

from __future__ import annotations
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from typing import Optional

from .fetchers import (
    EventbriteFetcher,
    FeverFetcher,
    LevCinemaFetcher,
    NYCOpenDataFetcher,
    TicketmasterFetcher,
    TimeOutILFetcher,
    TLVMunicipalityFetcher,
    XceedFetcher,
)
from .filters import deduplicate, filter_events, rank_events
from .models import AgeGroup, City, Event, EventType, TimeOfDay

log = logging.getLogger(__name__)

# City → which fetchers to use (in priority order)
_CITY_FETCHERS: dict[City, list] = {
    City.TEL_AVIV:  ["tlv_municipality", "eventbrite", "lev_cinema", "timeout_il"],
    City.BARCELONA: ["ticketmaster", "eventbrite", "fever", "xceed"],
    City.NEW_YORK:  ["ticketmaster", "eventbrite", "nyc_open_data", "fever"],
}

_FETCHER_REGISTRY = {
    "tlv_municipality": TLVMunicipalityFetcher,
    "ticketmaster":     TicketmasterFetcher,
    "eventbrite":       EventbriteFetcher,
    "lev_cinema":       LevCinemaFetcher,
    "nyc_open_data":    NYCOpenDataFetcher,
    "timeout_il":       TimeOutILFetcher,
    "fever":            FeverFetcher,
    "xceed":            XceedFetcher,
}


class ClawEventsEngine:
    def __init__(self):
        # Instantiate fetchers once (they read env vars in __init__)
        self._fetchers = {k: cls() for k, cls in _FETCHER_REGISTRY.items()}

    def search(
        self,
        cities:      list[City],
        start:       Optional[datetime]        = None,
        end:         Optional[datetime]        = None,
        event_types: Optional[list[EventType]] = None,
        age_groups:  Optional[list[AgeGroup]]  = None,
        time_of_day: Optional[list[TimeOfDay]] = None,
        free_only:   bool                      = False,
        limit:       int                       = 20,
    ) -> list[Event]:
        now   = datetime.now()
        start = start or now
        end   = end   or (now + timedelta(days=7))

        # Build fetch tasks
        tasks: list[tuple[str, City]] = []
        for city in cities:
            for fname in _CITY_FETCHERS.get(city, []):
                if fname in self._fetchers:
                    tasks.append((fname, city))

        # Fetch in parallel
        raw: list[Event] = []
        with ThreadPoolExecutor(max_workers=6) as pool:
            futures = {
                pool.submit(
                    self._fetchers[fname].fetch,
                    city, start, end, event_types, limit * 2
                ): (fname, city)
                for fname, city in tasks
            }
            for future in as_completed(futures):
                fname, city = futures[future]
                try:
                    results = future.result()
                    log.info("%s → %s: %d events", fname, city.value, len(results))
                    raw.extend(results)
                except Exception as exc:
                    log.warning("Fetcher %s/%s failed: %s", fname, city.value, exc)

        # Post-process
        filtered = filter_events(
            raw,
            cities      = cities,
            event_types = event_types,
            age_groups  = age_groups,
            time_of_day = time_of_day,
            start       = start,
            end         = end,
            free_only   = free_only,
        )
        deduped = deduplicate(filtered)
        ranked  = rank_events(deduped)

        return ranked[:limit]
