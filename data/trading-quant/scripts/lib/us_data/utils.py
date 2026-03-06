"""Utility helpers for US symbol normalization and snapshot shaping."""

from __future__ import annotations

from datetime import datetime

import pandas as pd

SNAPSHOT_COLUMNS = ["symbol", "last", "prev", "pct", "quote_time", "source", "status"]


def normalize_us_symbol(symbol: str) -> str:
    raw = str(symbol).strip().upper()
    if not raw:
        raise ValueError("empty symbol")
    return raw


def utc_now_str() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def normalize_snapshot_df(df: pd.DataFrame, source: str) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=SNAPSHOT_COLUMNS)

    out = pd.DataFrame()
    out["symbol"] = df.get("symbol", pd.Series(dtype=object)).astype(str).str.strip().str.upper()
    out["last"] = pd.to_numeric(df.get("last"), errors="coerce")
    out["prev"] = pd.to_numeric(df.get("prev"), errors="coerce")
    out["pct"] = pd.to_numeric(df.get("pct"), errors="coerce")
    out["quote_time"] = pd.to_datetime(df.get("quote_time"), errors="coerce").dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    out["quote_time"] = out["quote_time"].fillna(utc_now_str())
    out["source"] = source
    out["status"] = df.get("status", "ok").astype(str).str.lower()

    out = out[out["symbol"] != ""].copy()
    out = out.drop_duplicates(subset=["symbol"], keep="last")
    return out[SNAPSHOT_COLUMNS].reset_index(drop=True)
