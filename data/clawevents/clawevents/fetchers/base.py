"""Base fetcher interface."""

from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from ..models import City, Event, EventType


class BaseFetcher(ABC):
    """All fetchers return List[Event]. Failures are logged, never raised."""

    source_name: str = "unknown"
    supported_cities: list[City] = []

    @abstractmethod
    def fetch(
        self,
        city: City,
        start: datetime,
        end: datetime,
        event_types: Optional[list[EventType]] = None,
        limit: int = 50,
    ) -> list[Event]:
        ...

    def supports(self, city: City) -> bool:
        return city in self.supported_cities
