"""Tel Aviv Municipality events API — free, no key required.

Endpoint: https://api.tel-aviv.gov.il/poi/events
Covers: DigiTel-sourced city events, cultural events, municipal programmes.
"""

from __future__ import annotations
import logging
from datetime import datetime
from typing import Optional

import os

import requests
from bs4 import BeautifulSoup

from ..models import AgeGroup, City, Event, EventType
from .base import BaseFetcher

log = logging.getLogger(__name__)

BASE_URL = "https://api.tel-aviv.gov.il/poi/events"
# NOTE: The TLV Municipality API requires an Ocp-Apim-Subscription-Key header.
# Register at: https://apiportal.tel-aviv.gov.il
# Set env var: TLV_API_KEY
# Without a key, this fetcher falls back to scraping the public events page.
FALLBACK_URL = "https://www.tel-aviv.gov.il/en/Visit/UpcomingEvents/Pages/default.aspx"

# Rough keyword → EventType mapping for TLV API (Hebrew + English titles)
_TYPE_KEYWORDS: dict[EventType, list[str]] = {
    EventType.JAZZ:      ["jazz", "ג'אז"],
    EventType.CONCERT:   ["concert", "הופעה", "מוזיקה", "music", "live"],
    EventType.THEATRE:   ["theatre", "theater", "תיאטרון", "הצגה"],
    EventType.CINEMA:    ["cinema", "קולנוע", "film", "סרט"],
    EventType.FAMILY:    ["family", "ילדים", "kids", "children", "משפחה"],
    EventType.COMEDY:    ["comedy", "קומדיה", "stand up", "סטנד אפ"],
    EventType.ART:       ["art", "אמנות", "gallery", "גלריה", "exhibition", "תערוכה"],
    EventType.FESTIVAL:  ["festival", "פסטיבל"],
    EventType.SPORT:     ["sport", "ספורט", "marathon", "מרתון", "run", "ריצה"],
}

_AGE_KEYWORDS: dict[AgeGroup, list[str]] = {
    AgeGroup.KIDS:   ["ילדים", "kids", "children", "גן"],
    AgeGroup.FAMILY: ["משפחה", "family", "כל הגילאים", "all ages"],
}


def _classify_types(title: str, desc: str) -> list[EventType]:
    text = (title + " " + desc).lower()
    found = [t for t, kws in _TYPE_KEYWORDS.items() if any(k in text for k in kws)]
    return found or [EventType.OTHER]


def _classify_age(title: str, desc: str) -> list[AgeGroup]:
    text = (title + " " + desc).lower()
    found = [a for a, kws in _AGE_KEYWORDS.items() if any(k in text for k in kws)]
    return found or [AgeGroup.ADULTS]


def _parse_dt(val: Optional[str]) -> Optional[datetime]:
    if not val:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(val[:19], fmt[:len(val[:19])])
        except ValueError:
            continue
    return None


class TLVMunicipalityFetcher(BaseFetcher):
    source_name = "tlv_municipality"
    supported_cities = [City.TEL_AVIV]

    def fetch(
        self,
        city: City,
        start: datetime,
        end: datetime,
        event_types: Optional[list[EventType]] = None,
        limit: int = 50,
    ) -> list[Event]:
        if city != City.TEL_AVIV:
            return []

        api_key = os.environ.get("TLV_API_KEY", "")
        if api_key:
            return self._fetch_api(api_key, start, end, event_types, limit)
        return self._fetch_scrape(start, end, event_types, limit)

    def _fetch_api(self, api_key: str, start: datetime, end: datetime,
                   event_types, limit: int) -> list[Event]:
        params = {
            "fromDate": start.strftime("%Y-%m-%d"),
            "toDate":   end.strftime("%Y-%m-%d"),
            "limit":    limit,
            "offset":   0,
        }
        headers = {"Ocp-Apim-Subscription-Key": api_key}
        try:
            resp = requests.get(BASE_URL, params=params, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            log.warning("TLV Municipality API error: %s — falling back to scrape", exc)
            return self._fetch_scrape(start, end, event_types, limit)

        items = data if isinstance(data, list) else data.get("results", data.get("events", []))
        return self._parse_items(items, event_types, limit)

    def _fetch_scrape(self, start: datetime, end: datetime,
                      event_types, limit: int) -> list[Event]:
        """Fallback: scrape the public TLV upcoming events page."""
        try:
            resp = requests.get(FALLBACK_URL,
                                headers={"User-Agent": "Mozilla/5.0 (compatible; ClawEvents/1.0)"},
                                timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
        except Exception as exc:
            log.warning("TLV scrape error: %s", exc)
            return []

        events: list[Event] = []
        # Try common selectors for the TLV events page
        blocks = (soup.select(".event-item, .eventItem, article.event, [class*='event']")
                  or soup.select("li[class*='event'], div[class*='event']"))

        import hashlib
        for block in blocks[:limit]:
            title_el = block.select_one("h2, h3, h4, .title, [class*='title']")
            title = title_el.get_text(strip=True) if title_el else ""
            if not title:
                continue
            link_el   = block.select_one("a[href]")
            url       = link_el["href"] if link_el else FALLBACK_URL
            if url.startswith("/"):
                url = "https://www.tel-aviv.gov.il" + url
            desc_el   = block.select_one("p, .description, [class*='desc']")
            desc      = desc_el.get_text(strip=True) if desc_el else ""
            types     = _classify_types(title, desc)
            if event_types and not any(t in types for t in event_types):
                continue
            uid = hashlib.md5(f"tlv_scrape:{title}".encode()).hexdigest()[:12]
            events.append(Event(
                id=uid, source=self.source_name, city=City.TEL_AVIV,
                title=title, description=desc, url=url,
                event_types=types, age_groups=_classify_age(title, desc),
            ))
        return events

    def _parse_items_wrapper(self, start, end, event_types, limit):
        pass  # kept for compat

        items = []  # placeholder — handled in _fetch_api

        events: list[Event] = []
        for item in items:
            title = item.get("EventName") or item.get("name") or item.get("title") or ""
            desc  = item.get("EventDescription") or item.get("description") or ""
            start_dt = _parse_dt(item.get("EventStartDate") or item.get("startDate") or item.get("start"))
            end_dt   = _parse_dt(item.get("EventEndDate")   or item.get("endDate")   or item.get("end"))

            types  = _classify_types(title, desc)
            ages   = _classify_age(title, desc)

            # Filter by requested types (if any)
            if event_types:
                if not any(t in types for t in event_types):
                    # Also let jazz pass if concert requested, etc.
                    continue

            events.append(Event(
                id          = str(item.get("EventID") or item.get("id") or hash(title + str(start_dt))),
                source      = self.source_name,
                city        = City.TEL_AVIV,
                title       = title,
                description = desc,
                url         = item.get("url") or item.get("EventURL") or "",
                image_url   = item.get("imageUrl") or item.get("EventImage") or "",
                event_types = types,
                age_groups  = ages,
                start       = start_dt,
                end         = end_dt,
                venue_name  = item.get("locationName") or item.get("venue") or "",
                address     = item.get("address") or "",
                neighborhood= item.get("neighborhood") or item.get("area") or "",
                is_free     = bool(item.get("isFree") or item.get("free")),
                ticket_url  = item.get("ticketUrl") or item.get("EventURL") or "",
            ))

        return events
