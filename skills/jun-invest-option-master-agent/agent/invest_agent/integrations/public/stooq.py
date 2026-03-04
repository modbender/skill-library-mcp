"""Public market data fallback via Stooq (free, no key).

Used only when broker data is unavailable (e.g., US ETF quote permission missing).
All outputs must include source + timestamp.
"""

from __future__ import annotations

import csv
import io
import math
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _http_get(url: str, timeout_s: float = 10.0) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "invest-agent/1.0"})
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _stooq_quote_symbol(ticker: str) -> str:
    t = (ticker or "").strip().lower()
    # Simple mapping for common US tickers.
    if t.startswith("^"):
        t = t[1:]
    # Stooq uses .us for US equities/ETFs.
    if "." not in t:
        return f"{t}.us"
    return t


def get_quote(ticker: str) -> Dict[str, Any]:
    """Get last quote snapshot (best-effort) from Stooq."""
    ts = _utc_now_iso()
    sym = _stooq_quote_symbol(ticker)
    url = f"https://stooq.com/q/l/?s={sym}&f=sd2t2ohlcv&h&e=csv"
    try:
        text = _http_get(url)
        rows = list(csv.DictReader(io.StringIO(text)))
        if not rows:
            raise RuntimeError("empty csv")
        r = rows[0]
        def fnum(x: Optional[str]) -> Optional[float]:
            try:
                return float(x) if x not in (None, "", "N/A") else None
            except Exception:
                return None
        price = fnum(r.get("Close"))
        low = fnum(r.get("Low"))
        high = fnum(r.get("High"))
        day_range = None
        if low is not None or high is not None:
            day_range = {"low": low, "high": high}
        # Stooq provides Date + Time (local exchange time); keep raw + also attach fetch timestamp.
        quote_ts = f"{r.get('Date','')}T{r.get('Time','')}".strip("T") or ts
        return {
            "ticker": ticker,
            "price": price,
            "day_range": day_range,
            "timestamp": quote_ts,
            "source": "stooq",
            "fetched_at": ts,
        }
    except Exception as exc:
        return {
            "ticker": ticker,
            "price": None,
            "day_range": None,
            "timestamp": ts,
            "source": "stooq",
            "error": f"public quote failed: {exc}",
        }


def get_daily_history(ticker: str, limit: int = 60) -> List[Tuple[str, float]]:
    """Return list of (date, close) ascending by date."""
    sym = _stooq_quote_symbol(ticker)
    url = f"https://stooq.com/q/d/l/?s={sym}&i=d"
    text = _http_get(url)
    rows = list(csv.DictReader(io.StringIO(text)))
    out: List[Tuple[str, float]] = []
    for r in rows[-limit:]:
        try:
            out.append((r["Date"], float(r["Close"])))
        except Exception:
            continue
    return out


def realized_vol_20d(ticker: str) -> Dict[str, Any]:
    ts = _utc_now_iso()
    try:
        hist = get_daily_history(ticker, limit=40)
        if len(hist) < 21:
            raise RuntimeError("insufficient history")
        closes = [c for _, c in hist]
        rets = [math.log(closes[i] / closes[i - 1]) for i in range(1, len(closes))]
        window = rets[-20:]
        mean = sum(window) / len(window)
        var = sum((x - mean) ** 2 for x in window) / (len(window) - 1)
        rv20 = math.sqrt(var) * math.sqrt(252.0)
        return {"ticker": ticker, "rv20": rv20, "timestamp": ts, "source": "stooq"}
    except Exception as exc:
        return {"ticker": ticker, "rv20": None, "timestamp": ts, "source": "stooq", "error": str(exc)}
