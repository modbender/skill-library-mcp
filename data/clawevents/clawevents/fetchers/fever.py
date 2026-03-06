"""Fever scraper — Barcelona (and other cities).

Requires: pip install playwright && playwright install chromium
Site: https://feverup.com/en/barcelona

Fever is strong for: experiences, immersive events, concerts, theatre, exhibitions.
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

_CITY_URLS: dict[City, str] = {
    City.BARCELONA: "https://feverup.com/en/barcelona",
    City.NEW_YORK:  "https://feverup.com/en/new-york",
}

_TYPE_KEYWORDS: dict[EventType, list[str]] = {
    EventType.CONCERT:   ["concert", "music", "live", "show"],
    EventType.JAZZ:      ["jazz"],
    EventType.THEATRE:   ["theatre", "theater", "show", "performance"],
    EventType.ART:       ["art", "exhibition", "immersive", "museum"],
    EventType.COMEDY:    ["comedy", "stand up"],
    EventType.FAMILY:    ["family", "kids"],
    EventType.FESTIVAL:  ["festival"],
    EventType.NIGHTLIFE: ["club", "night", "party", "dj"],
}


def _classify(title: str, desc: str) -> list[EventType]:
    text = (title + " " + desc).lower()
    found = [t for t, kws in _TYPE_KEYWORDS.items() if any(k in text for k in kws)]
    return found or [EventType.OTHER]


def _parse_price(text: str) -> tuple[Optional[float], Optional[float], str]:
    nums = re.findall(r"[\d,.]+", text.replace(",", ""))
    floats = []
    for n in nums:
        try:
            floats.append(float(n))
        except ValueError:
            pass
    if not floats:
        return None, None, ""
    currency = "€" if "€" in text else ("$" if "$" in text else "")
    return min(floats), max(floats), currency


class FeverFetcher(BaseFetcher):
    source_name = "fever"
    supported_cities = [City.BARCELONA, City.NEW_YORK]

    def fetch(
        self,
        city: City,
        start: datetime,
        end: datetime,
        event_types: Optional[list[EventType]] = None,
        limit: int = 50,
    ) -> list[Event]:
        url = _CITY_URLS.get(city)
        if not url:
            return []

        html = fetch_page_html(url, wait_selector="[class*='plan'], [class*='card'], article")
        if not html:
            return []

        return self._parse(html, city, event_types, limit)

    def _parse(self, html: str, city: City, event_types, limit: int) -> list[Event]:
        soup = BeautifulSoup(html, "html.parser")
        events: list[Event] = []

        # Fever renders event cards — try multiple selectors
        cards = (
            soup.select("[class*='plan-card'], [class*='PlanCard'], [class*='experience']")
            or soup.select("article, [class*='card'], [class*='event']")
        )[:limit * 2]

        for card in cards:
            title_el = card.select_one("h2, h3, [class*='title'], [class*='name']")
            title = title_el.get_text(strip=True) if title_el else ""
            if not title or len(title) < 3:
                continue

            link_el = card.select_one("a[href]")
            url = link_el["href"] if link_el else ""
            if url and not url.startswith("http"):
                url = "https://feverup.com" + url

            desc_el = card.select_one("p, [class*='desc'], [class*='subtitle']")
            desc = desc_el.get_text(strip=True) if desc_el else ""

            price_el = card.select_one("[class*='price'], [class*='Price']")
            price_text = price_el.get_text(strip=True) if price_el else ""
            is_free = "free" in price_text.lower()
            price_min, price_max, currency = _parse_price(price_text) if not is_free else (None, None, "")

            img_el = card.select_one("img[src]")
            image_url = img_el.get("src", "") if img_el else ""

            types = _classify(title, desc)
            if event_types and not any(t in types for t in event_types):
                continue

            uid = hashlib.md5(f"fever:{city.value}:{title}".encode()).hexdigest()[:12]
            events.append(Event(
                id          = uid,
                source      = self.source_name,
                city        = city,
                title       = title,
                description = desc[:300],
                url         = url,
                image_url   = image_url,
                event_types = types,
                age_groups  = [AgeGroup.FAMILY] if EventType.FAMILY in types else [AgeGroup.ADULTS],
                is_free     = is_free,
                price_min   = price_min,
                price_max   = price_max,
                currency    = currency,
                ticket_url  = url,
            ))

        return events[:limit]
