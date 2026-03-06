"""Lev Cinema scraper — Tel Aviv boutique cinema chain.

Website: lev.co.il
No public API; scrapes the schedule pages.
TLV branches: Cinema City Dizengoff (Lev), Lev Herzliya, etc.
"""

from __future__ import annotations
import hashlib
import logging
import re
from datetime import datetime, timedelta
from typing import Optional

import requests
from bs4 import BeautifulSoup

from ..models import AgeGroup, City, Event, EventType
from .base import BaseFetcher

log = logging.getLogger(__name__)

SCHEDULE_URL = "https://www.lev.co.il/en/schedule/"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ClawEvents/1.0)"}


def _parse_lev_date(date_str: str, time_str: str) -> Optional[datetime]:
    """Parse Lev's date/time strings."""
    for fmt in ["%d/%m/%Y %H:%M", "%Y-%m-%d %H:%M", "%d.%m.%Y %H:%M"]:
        try:
            return datetime.strptime(f"{date_str.strip()} {time_str.strip()}", fmt)
        except ValueError:
            continue
    return None


class LevCinemaFetcher(BaseFetcher):
    source_name = "lev_cinema"
    supported_cities = [City.TEL_AVIV]

    def fetch(
        self,
        city: City,
        start: datetime,
        end: datetime,
        event_types: Optional[list[EventType]] = None,
        limit: int = 50,
    ) -> list[Event]:
        # Only run if cinema type requested or no type filter
        if event_types and EventType.CINEMA not in event_types:
            return []
        if city != City.TEL_AVIV:
            return []

        try:
            resp = requests.get(SCHEDULE_URL, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
        except Exception as exc:
            log.warning("Lev Cinema scrape error: %s", exc)
            return []

        events: list[Event] = []
        # Lev's site structure varies; try common selectors
        film_blocks = (
            soup.select(".movie-item, .film-item, .schedule-item, article.movie")
            or soup.select("[class*='movie'], [class*='film'], [class*='schedule']")
        )

        for block in film_blocks[:limit]:
            title_el = block.select_one("h2, h3, .title, .movie-title, .film-name")
            title = title_el.get_text(strip=True) if title_el else ""
            if not title:
                continue

            link_el  = block.select_one("a[href]")
            url      = "https://www.lev.co.il" + link_el["href"] if link_el and link_el.get("href", "").startswith("/") else (link_el["href"] if link_el else SCHEDULE_URL)

            img_el   = block.select_one("img[src]")
            image_url = img_el["src"] if img_el else ""

            # Extract showtimes
            time_els = block.select(".showtime, .time, [class*='time'], [class*='hour']")
            date_el  = block.select_one(".date, [class*='date']")
            date_str = date_el.get_text(strip=True) if date_el else ""

            showtimes: list[Optional[datetime]] = []
            for t_el in time_els:
                t_str = t_el.get_text(strip=True)
                if re.match(r"\d{1,2}:\d{2}", t_str):
                    dt = _parse_lev_date(date_str or start.strftime("%d/%m/%Y"), t_str)
                    showtimes.append(dt)

            # If no showtimes parsed, create a single event without time
            if not showtimes:
                showtimes = [None]

            for st in showtimes:
                if st and not (start <= st <= end):
                    continue
                uid = hashlib.md5(f"lev:{title}:{st}".encode()).hexdigest()[:12]
                events.append(Event(
                    id          = uid,
                    source      = self.source_name,
                    city        = City.TEL_AVIV,
                    title       = title,
                    url         = url,
                    image_url   = image_url,
                    event_types = [EventType.CINEMA],
                    age_groups  = [AgeGroup.ADULTS],
                    start       = st,
                    end         = (st + timedelta(hours=2)) if st else None,
                    venue_name  = "Lev Cinema",
                    address     = "Dizengoff Center, Tel Aviv",
                    neighborhood= "Dizengoff",
                    is_free     = False,
                    ticket_url  = url,
                ))

        return events
