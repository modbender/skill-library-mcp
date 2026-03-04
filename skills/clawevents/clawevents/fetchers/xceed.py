"""Xceed scraper — Barcelona clubs and nightlife.

Requires: pip install playwright && playwright install chromium
Site: https://xceed.me/en/barcelona/events

Xceed is the dominant platform for Barcelona clubbing: Pacha, Razzmatazz, Sala Apolo, etc.
Also covers electronic music events in NYC.
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
    City.BARCELONA: "https://xceed.me/en/barcelona/events",
    City.NEW_YORK:  "https://xceed.me/en/new-york/events",
}

_TYPE_KEYWORDS: dict[EventType, list[str]] = {
    EventType.NIGHTLIFE: ["club", "dj", "techno", "house", "electronic", "night", "party"],
    EventType.CONCERT:   ["concert", "live", "band", "rock", "pop"],
    EventType.JAZZ:      ["jazz"],
    EventType.FESTIVAL:  ["festival"],
}


def _classify(title: str, desc: str) -> list[EventType]:
    text = (title + " " + desc).lower()
    found = [t for t, kws in _TYPE_KEYWORDS.items() if any(k in text for k in kws)]
    return found or [EventType.NIGHTLIFE]  # Xceed default is nightlife


def _parse_price(text: str) -> tuple[Optional[float], Optional[float], str]:
    nums = re.findall(r"[\d,.]+", text.replace(",", ""))
    floats = []
    for n in nums:
        try:
            floats.append(float(n))
        except ValueError:
            pass
    currency = "€" if "€" in text else ("$" if "$" in text else "")
    if not floats:
        return None, None, currency
    return min(floats), max(floats), currency


def _parse_dt_xceed(text: str) -> Optional[datetime]:
    """Parse Xceed date strings like 'Fri, 21 Mar' or 'Mar 21, 2026 23:00'."""
    text = text.strip()
    for fmt in ["%a, %d %b %Y %H:%M", "%b %d, %Y %H:%M", "%d %b %Y", "%a, %d %b"]:
        try:
            dt = datetime.strptime(text, fmt)
            if dt.year == 1900:
                dt = dt.replace(year=datetime.now().year)
            return dt
        except ValueError:
            continue
    return None


class XceedFetcher(BaseFetcher):
    source_name = "xceed"
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

        # Skip if types are requested that Xceed doesn't cover
        if event_types and not any(
            t in event_types for t in [EventType.NIGHTLIFE, EventType.CONCERT,
                                        EventType.JAZZ, EventType.FESTIVAL, EventType.OTHER]
        ):
            return []

        html = fetch_page_html(url, wait_selector="[class*='event'], [class*='Event'], article")
        if not html:
            return []

        return self._parse(html, city, event_types, limit)

    def _parse(self, html: str, city: City, event_types, limit: int) -> list[Event]:
        soup = BeautifulSoup(html, "html.parser")
        events: list[Event] = []

        # Xceed uses Next.js RSC — event cards have multiple selectors
        cards = (
            soup.select("[class*='eventCard'], [class*='EventCard']")
            or soup.select("article, [class*='event-item'], [class*='plan']")
        )[:limit * 2]

        for card in cards:
            title_el = card.select_one("h2, h3, h4, [class*='title'], [class*='name']")
            title = title_el.get_text(strip=True) if title_el else ""
            if not title or len(title) < 3:
                continue

            link_el = card.select_one("a[href]")
            url = link_el["href"] if link_el else ""
            if url and not url.startswith("http"):
                url = "https://xceed.me" + url

            # Date
            date_el = card.select_one("[class*='date'], [class*='Date'], time")
            date_text = date_el.get_text(strip=True) if date_el else ""
            start_dt = _parse_dt_xceed(date_text)

            # Venue
            venue_el = card.select_one("[class*='venue'], [class*='location']")
            venue = venue_el.get_text(strip=True) if venue_el else ""

            # Price
            price_el = card.select_one("[class*='price'], [class*='Price']")
            price_text = price_el.get_text(strip=True) if price_el else ""
            is_free = "free" in price_text.lower()
            price_min, price_max, currency = _parse_price(price_text) if not is_free else (None, None, "")

            img_el = card.select_one("img[src]")
            image_url = img_el.get("src", "") if img_el else ""

            types = _classify(title, "")
            if event_types and not any(t in types for t in event_types):
                continue

            # Filter by date
            if start_dt and not (start <= start_dt <= end):
                continue

            uid = hashlib.md5(f"xceed:{city.value}:{title}:{date_text}".encode()).hexdigest()[:12]
            events.append(Event(
                id          = uid,
                source      = self.source_name,
                city        = city,
                title       = title,
                url         = url,
                image_url   = image_url,
                event_types = types,
                age_groups  = [AgeGroup.ADULTS],
                start       = start_dt,
                venue_name  = venue,
                is_free     = is_free,
                price_min   = price_min,
                price_max   = price_max,
                currency    = currency,
                ticket_url  = url,
            ))

        return events[:limit]
