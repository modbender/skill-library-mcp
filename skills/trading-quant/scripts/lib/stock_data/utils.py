"""Utility helpers for symbol normalization and DataFrame standardization."""

from __future__ import annotations

from typing import Optional

import pandas as pd

STANDARD_COLUMNS = [
    "date",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "amount",
    "code",
    "source",
    "frequency",
    "adjust",
]


def normalize_code(code: str) -> str:
    """Normalize a symbol into internal 6-digit numeric code."""
    raw = str(code).strip().lower()
    for prefix in ("sh.", "sz.", "sh", "sz"):
        if raw.startswith(prefix):
            raw = raw[len(prefix) :]
            break
    raw = "".join(ch for ch in raw if ch.isdigit())
    if len(raw) != 6:
        raise ValueError(f"invalid stock code: {code}")
    return raw


def _market_from_code(n: str) -> str:
    """Infer CN market prefix from 6-digit code.

    Common rules:
    - SH: 5xx/6xx/9xx (ETF, A-share, B-share)
    - SZ: others like 0xx/1xx/2xx/3xx
    """
    return "sh" if n.startswith(("5", "6", "9")) else "sz"


def to_sina_symbol(code: str) -> str:
    """Convert internal code to sina/akshare market style: sh600519/sz002202."""
    n = normalize_code(code)
    return f"{_market_from_code(n)}{n}"


def to_baostock_symbol(code: str) -> str:
    """Convert internal code to baostock style: sh.600519/sz.002202."""
    n = normalize_code(code)
    return f"{_market_from_code(n)}.{n}"


def _find_col(df: pd.DataFrame, names: list[str]) -> Optional[str]:
    lower_map = {str(c).strip().lower(): c for c in df.columns}
    for name in names:
        if name.lower() in lower_map:
            return lower_map[name.lower()]
    return None


def normalize_kline_df(
    df: pd.DataFrame,
    code: str,
    source: str,
    frequency: str,
    adjust: str,
) -> pd.DataFrame:
    """Convert source-specific kline columns into the standard schema."""
    if df is None or df.empty:
        return pd.DataFrame(columns=STANDARD_COLUMNS)

    date_col = _find_col(df, ["date", "datetime", "time", "day", "日期", "时间"])
    open_col = _find_col(df, ["open", "开盘"])
    high_col = _find_col(df, ["high", "最高"])
    low_col = _find_col(df, ["low", "最低"])
    close_col = _find_col(df, ["close", "收盘"])
    vol_col = _find_col(df, ["volume", "vol", "成交量"])
    amt_col = _find_col(df, ["amount", "成交额", "turnover"])

    required = [date_col, open_col, high_col, low_col, close_col, vol_col]
    if any(col is None for col in required):
        raise ValueError(f"missing required columns from source={source}: {list(df.columns)}")

    out = pd.DataFrame(
        {
            "date": pd.to_datetime(df[date_col], errors="coerce"),
            "open": pd.to_numeric(df[open_col], errors="coerce"),
            "high": pd.to_numeric(df[high_col], errors="coerce"),
            "low": pd.to_numeric(df[low_col], errors="coerce"),
            "close": pd.to_numeric(df[close_col], errors="coerce"),
            "volume": pd.to_numeric(df[vol_col], errors="coerce"),
            "amount": pd.to_numeric(df[amt_col], errors="coerce") if amt_col else pd.NA,
        }
    )
    out = out.dropna(subset=["date", "open", "high", "low", "close"]).copy()
    out["date"] = out["date"].dt.strftime("%Y-%m-%d %H:%M:%S")
    out["code"] = normalize_code(code)
    out["source"] = source
    out["frequency"] = frequency
    out["adjust"] = adjust
    return out[STANDARD_COLUMNS].sort_values("date").reset_index(drop=True)
