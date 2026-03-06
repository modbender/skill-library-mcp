"""Time Out Israel scraper — TLV jazz, concerts, nightlife, theatre.

Requires: pip install playwright && playwright install chromium
Site: https://www.timeout.com/israel

Sections:
  /israel/music           → concerts + live music
  /israel/nightlife       → clubs, bars
  /israel/things-to-do    → general events
  /israel/theatre         → theatre
  /israel/film            → cinema (general editorial, not listings)
"""

from __future__ import annotations
import hashlib
import logging
import re
from datetime import datetime
from typing import Optional

from bs4 import BeautifulSoup

from ..models import AgeGroup, City, Event, EventType
from .base import BaseFetcher
from .playwright_base import fetch_page_html

log = logging.getLogger(__name__)

BASE = "https://www.timeout.com"

_SECTION_TYPES: dict[str, list[EventType]] = {
    "/israel/music":        [EventType.CONCERT],
    "/israel/nightlife":    [EventType.NIGHTLIFE],
    "/israel/theatre":      [EventType.THEATRE],
    "/israel/things-to-do": [EventType.OTHER],
}

_JAZZ_KEYWORDS = ["jazz", "ג'אז", "bebop", "swing", "blues"]

_TYPE_KEYWORDS: dict[EventType, list[str]] = {
    EventType.JAZZ:      _JAZZ_KEYWORDS,
    EventType.CONCERT:   ["concert", "live", "gig", "band", "perform"],
    EventType.COMEDY:    ["comedy", "stand up"],
    EventType.THEATRE:   ["theatre", "theater", "play"],
    EventType.FAMILY:    ["family", "kids", "children"],
    EventType.ART:       ["art", "exhibition", "gallery"],
}


def _classify(title: str, desc: str) -> list[EventType]:
    text = (title + " " + desc).lower()
    found = [t for t, kws in _TYPE_KEYWORDS.items() if any(k in text for k in kws)]
    return found or [EventType.OTHER]


class TimeOutILFetcher(BaseFetcher):
    source_name = "timeout_il"
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

        # Determine which sections to scrape based on requested types
        sections = list(_SECTION_TYPES.keys())
        if event_types:
            sections = []
            if any(t in event_types for t in [EventType.CONCERT, EventType.JAZZ]):
                sections.append("/israel/music")
            if EventType.NIGHTLIFE in event_types:
                sections.append("/israel/nightlife")
            if EventType.THEATRE in event_types:
                sections.append("/israel/theatre")
            if not sections:
                sections = ["/israel/things-to-do"]

        events: list[Event] = []
        for section in sections:
            url = BASE + section
            html = fetch_page_html(url, wait_selector="article, .tile, [class*='card']")
            if not html:
                continue
            events.extend(self._parse(html, url, event_types, limit - len(events)))
            if len(events) >= limit:
                break

        return events[:limit]

    def _parse(self, html: str, section_url: str, event_types, limit: int) -> list[Event]:
        soup = BeautifulSoup(html, "html.parser")
        events: list[Event] = []

        # Time Out uses article tiles with class containing 'tile' or 'card'
        articles = (
            soup.select("article._article_a9slj_1, article.tile, [class*='_article_']")
            or soup.select("article, [class*='tile'], [class*='card']")
        )[:limit * 2]

        for art in articles:
            title_el = art.select_one("h3, h2, [class*='title'], [class*='heading']")
            title = title_el.get_text(strip=True) if title_el else ""
            if not title or len(title) < 3:
                continue

            link_el = art.select_one("a[href]")
            url = link_el["href"] if link_el else section_url
            if url.startswith("/"):
                url = BASE + url

            desc_el = art.select_one("p, [class*='desc'], [class*='summary']")
            desc = desc_el.get_text(strip=True) if desc_el else ""

            img_el = art.select_one("img[src]")
            image_url = img_el.get("src", "") if img_el else ""

            types = _classify(title, desc)
            if event_types and not any(t in types for t in event_types):
                # Still include if it's a jazz keyword regardless of section
                if not any(kw in (title + desc).lower() for kw in _JAZZ_KEYWORDS):
                    continue

            uid = hashlib.md5(f"timeout_il:{title}".encode()).hexdigest()[:12]
            events.append(Event(
                id          = uid,
                source      = self.source_name,
                city        = City.TEL_AVIV,
                title       = title,
                description = desc[:300],
                url         = url,
                image_url   = image_url,
                event_types = types,
                age_groups  = [AgeGroup.ADULTS],
                venue_name  = "Tel Aviv",
            ))

        return events
