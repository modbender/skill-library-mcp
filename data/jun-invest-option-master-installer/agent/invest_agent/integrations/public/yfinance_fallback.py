"""Public market data fallback using yfinance (Yahoo Finance).

This is the preferred public fallback when broker data is unavailable.
All outputs include source + timestamp.

Note: Implemented as a lightweight adapter around the mature yfinance library.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import yfinance as yf


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_quote(ticker: str) -> Dict[str, Any]:
    ts = _utc_now_iso()
    t = yf.Ticker(ticker)
    try:
        fi = t.fast_info or {}
        price = fi.get("last_price") or fi.get("lastPrice")
        low = fi.get("day_low") or fi.get("dayLow")
        high = fi.get("day_high") or fi.get("dayHigh")
        day_range = None
        if low is not None or high is not None:
            day_range = {"low": float(low) if low is not None else None, "high": float(high) if high is not None else None}
        return {
            "ticker": ticker,
            "price": float(price) if price is not None else None,
            "day_range": day_range,
            "timestamp": ts,
            "source": "yfinance",
        }
    except Exception as exc:
        return {"ticker": ticker, "price": None, "day_range": None, "timestamp": ts, "source": "yfinance", "error": str(exc)}


def realized_vol_20d(ticker: str) -> Dict[str, Any]:
    ts = _utc_now_iso()
    try:
        hist = yf.download(ticker, period="3mo", interval="1d", progress=False, auto_adjust=False, threads=False)
        if hist is None or hist.empty or len(hist) < 21:
            raise RuntimeError("insufficient history")
        # yfinance may return MultiIndex columns when downloading multiple tickers; normalize.
        if hasattr(hist.columns, "nlevels") and hist.columns.nlevels > 1:
            # try ('Close', ticker)
            try:
                close_series = hist[("Close", ticker)]
            except Exception:
                close_series = hist.xs("Close", axis=1, level=0).iloc[:, 0]
        else:
            close_series = hist["Close"]
        closes = close_series.dropna().astype(float).tolist()
        if len(closes) < 21:
            raise RuntimeError("insufficient closes")
        rets = [math.log(closes[i] / closes[i - 1]) for i in range(1, len(closes))]
        window = rets[-20:]
        mean = sum(window) / len(window)
        var = sum((x - mean) ** 2 for x in window) / (len(window) - 1)
        rv20 = math.sqrt(var) * math.sqrt(252.0)
        return {"ticker": ticker, "rv20": rv20, "timestamp": ts, "source": "yfinance"}
    except Exception as exc:
        return {"ticker": ticker, "rv20": None, "timestamp": ts, "source": "yfinance", "error": str(exc)}


def get_options_chain_summary(ticker: str, dte_min: int = 30, dte_max: int = 45) -> Dict[str, Any]:
    """Best-effort options chain summary using yfinance.

    Returns fields aligned with Data.snapshot.options_chain_summary entry.
    """
    ts = _utc_now_iso()
    t = yf.Ticker(ticker)
    try:
        exps = list(t.options or [])
        if not exps:
            raise RuntimeError("no expirations")
        # Pick the first expiration within range if possible.
        from datetime import date

        def dte(exp: str) -> int:
            y, m, d = exp.split("-")
            dt = date(int(y), int(m), int(d))
            return (dt - date.today()).days

        exp_pick = None
        for e in exps:
            dd = dte(e)
            if dte_min <= dd <= dte_max:
                exp_pick = e
                break
        if exp_pick is None:
            exp_pick = exps[0]
        chain = t.option_chain(exp_pick)
        calls = chain.calls
        puts = chain.puts

        # Typical spread: median(ask-bid) across near-the-money strikes.
        def median_spread(df) -> Optional[float]:
            if df is None or df.empty:
                return None
            df2 = df.copy()
            df2["spread"] = (df2["ask"] - df2["bid"]).astype(float)
            df2 = df2[df2["spread"].notna()]
            if df2.empty:
                return None
            return float(df2["spread"].median())

        spread = median_spread(calls)

        oi_note = None
        if calls is not None and not calls.empty:
            oi_note = f"calls OI sum={int(calls['openInterest'].fillna(0).sum())}"

        return {
            "ticker": ticker,
            "dte": exp_pick,
            "atm_iv": None,
            "put_skew_note": "unknown (not computed)",
            "bid_ask_spread_typical": spread,
            "oi_volume_note": oi_note,
            "source": "yfinance",
            "timestamp": ts,
        }
    except Exception as exc:
        return {
            "ticker": ticker,
            "dte": {"min": int(dte_min), "max": int(dte_max)},
            "atm_iv": None,
            "put_skew_note": "unknown (not computed)",
            "bid_ask_spread_typical": None,
            "oi_volume_note": None,
            "source": "yfinance",
            "timestamp": ts,
            "error": str(exc),
        }
