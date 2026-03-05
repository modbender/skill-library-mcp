"""Base data source adapter."""

from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class DataSource(ABC):
    """Abstract source adapter."""

    name: str = "base"
    supports_daily: bool = False
    supports_minute: bool = False

    @abstractmethod
    def get_daily(self, code: str, start: str, end: str, adjust: str = "") -> pd.DataFrame:
        raise NotImplementedError

    @abstractmethod
    def get_minute(self, code: str, period: str = "5", adjust: str = "") -> pd.DataFrame:
        raise NotImplementedError
