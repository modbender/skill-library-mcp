"""Base data source adapter for US snapshots."""

from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class DataSource(ABC):
    """Abstract source adapter."""

    name: str = "base"
    supports_snapshot: bool = False

    @abstractmethod
    def get_snapshots(self, symbols: list[str]) -> pd.DataFrame:
        raise NotImplementedError
