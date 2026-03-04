"""Unified Event model for ClawEvents — city-agnostic."""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class City(str, Enum):
    TEL_AVIV  = "tel-aviv"
    BARCELONA = "barcelona"
    NEW_YORK  = "new-york"


class EventType(str, Enum):
    CONCERT   = "concert"
    JAZZ      = "jazz"
    CINEMA    = "cinema"
    THEATRE   = "theatre"
    NIGHTLIFE = "nightlife"
    FAMILY    = "family"
    COMEDY    = "comedy"
    ART       = "art"
    SPORT     = "sport"
    FESTIVAL  = "festival"
    COMMUNITY = "community"
    OTHER     = "other"


class AgeGroup(str, Enum):
    KIDS   = "kids"      # under 12
    FAMILY = "family"    # all ages welcome
    ADULTS = "adults"    # 18+


class TimeOfDay(str, Enum):
    MORNING    = "morning"     # 06:00–12:00
    AFTERNOON  = "afternoon"   # 12:00–17:00
    EVENING    = "evening"     # 17:00–22:00
    LATE_NIGHT = "late-night"  # 22:00+


def time_of_day(dt: Optional[datetime]) -> Optional[TimeOfDay]:
    if dt is None:
        return None
    h = dt.hour
    if 6 <= h < 12:
        return TimeOfDay.MORNING
    if 12 <= h < 17:
        return TimeOfDay.AFTERNOON
    if 17 <= h < 22:
        return TimeOfDay.EVENING
    return TimeOfDay.LATE_NIGHT


@dataclass
class Event:
    # Identity
    id: str
    source: str                          # "ticketmaster" | "tlv_municipality" | "eventbrite" | ...
    city: City

    # Core info
    title: str
    description: str = ""
    url: str = ""
    image_url: str = ""

    # Classification
    event_types: list[EventType] = field(default_factory=list)
    age_groups: list[AgeGroup]   = field(default_factory=list)

    # Time
    start: Optional[datetime] = None
    end:   Optional[datetime] = None

    # Location
    venue_name: str = ""
    address: str = ""
    neighborhood: str = ""

    # Ticketing
    is_free: bool = False
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    currency: str = ""
    ticket_url: str = ""

    # Derived (computed on post-init)
    time_of_day: Optional[TimeOfDay] = field(default=None, init=False)

    def __post_init__(self):
        self.time_of_day = time_of_day(self.start)

    @property
    def price_display(self) -> str:
        if self.is_free:
            return "Free"
        if self.price_min is not None:
            s = f"{self.currency}{self.price_min:.0f}"
            if self.price_max and self.price_max != self.price_min:
                s += f"–{self.currency}{self.price_max:.0f}"
            return s
        return ""

    def to_dict(self) -> dict:
        return {
            "id":           self.id,
            "source":       self.source,
            "city":         self.city.value,
            "title":        self.title,
            "description":  self.description[:200] if self.description else "",
            "url":          self.url,
            "image_url":    self.image_url,
            "types":        [t.value for t in self.event_types],
            "age_groups":   [a.value for a in self.age_groups],
            "start":        self.start.isoformat() if self.start else None,
            "end":          self.end.isoformat()   if self.end   else None,
            "time_of_day":  self.time_of_day.value if self.time_of_day else None,
            "venue":        self.venue_name,
            "address":      self.address,
            "neighborhood": self.neighborhood,
            "free":         self.is_free,
            "price":        self.price_display,
            "ticket_url":   self.ticket_url,
        }
