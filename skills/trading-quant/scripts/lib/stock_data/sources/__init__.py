"""Source adapters for stock data."""

from .baostock import BaoStockSource
from .eastmoney import EastMoneySource
from .pytdx_source import PyTdxSource
from .sina import SinaSource

__all__ = ["SinaSource", "BaoStockSource", "PyTdxSource", "EastMoneySource"]
