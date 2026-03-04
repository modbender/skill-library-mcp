#!/usr/bin/env python3
"""Build dashboard-style market panels with source fallback and cache.

Primary source:
- Yahoo chart API

Fallback sources:
- Stooq daily CSV (where available)
- FRED proxy series for selected macro symbols
- Local cache from previous successful runs
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import random
import time
import urllib.error
import urllib.parse
import urllib.request
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

USER_AGENT = "Mozilla/5.0 (OpenClaw stanley-druckenmiller-workflow/1.1)"

SYMBOLS = {
    "rates": ["^IRX", "^FVX", "^TNX", "^TYX"],
    "fx": ["DX-Y.NYB", "AUDJPY=X"],
    "equities": ["^GSPC", "^IXIC", "^RUT", "^VIX", "SPY", "IWM"],
    "credit": ["HYG", "LQD"],
    "internals": ["XHB", "ITB", "IYT", "XRT", "SMH", "KRE", "XLY", "XLP"],
    "commodities": ["CL=F", "GC=F", "HG=F"],
}

FRED_SERIES = [
    "WALCL",
    "RRPONTSYD",
    "WTREGEN",
    "M2SL",
    "GDP",
    "DGS2",
    "DGS10",
    "T10Y2Y",
    "BAMLH0A0HYM2",
]

# Proxy map used when Yahoo/Stooq are unavailable.
FRED_PROXY_MAP = {
    "^IRX": "DGS3MO",
    "^FVX": "DGS5",
    "^TNX": "DGS10",
    "^TYX": "DGS30",
    "^VIX": "VIXCLS",
    "DX-Y.NYB": "DTWEXBGS",
    "CL=F": "DCOILWTICO",
    "GC=F": "GOLDAMGBD228NLBM",
    "HG=F": "PCOPPUSDM",
}

STOOQ_MAP = {
    "SPY": "spy.us",
    "IWM": "iwm.us",
    "HYG": "hyg.us",
    "LQD": "lqd.us",
    "XHB": "xhb.us",
    "ITB": "itb.us",
    "IYT": "iyt.us",
    "XRT": "xrt.us",
    "SMH": "smh.us",
    "KRE": "kre.us",
    "XLY": "xly.us",
    "XLP": "xlp.us",
    "^GSPC": "^spx",
    "^IXIC": "^ndq",
    "AUDJPY=X": "audjpy",
}

BREADTH_PROXY_UNIVERSE = [
    "SPY",
    "IWM",
    "XHB",
    "ITB",
    "IYT",
    "XRT",
    "SMH",
    "KRE",
    "XLY",
    "XLP",
    "HYG",
    "LQD",
]

WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
CACHE_PATH = WORKSPACE_ROOT / "memory" / "market-snapshots" / "market-panels-cache.json"
CACHE_FRESH_HOURS = 96
CACHE_STALE_HOURS = 336


class HttpError(RuntimeError):
    pass


def http_get(url: str, timeout: int = 20, retries: int = 5, backoff: float = 0.6) -> str:
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            last_err = exc
            retryable = exc.code in (429, 500, 502, 503, 504)
            if not retryable or attempt == retries - 1:
                break
            sleep_s = backoff * (2**attempt) + random.uniform(0.05, 0.25)
            time.sleep(sleep_s)
        except (urllib.error.URLError, TimeoutError) as exc:
            last_err = exc
            if attempt == retries - 1:
                break
            sleep_s = backoff * (2**attempt) + random.uniform(0.05, 0.25)
            time.sleep(sleep_s)
    raise HttpError(str(last_err))


def compute_changes(points: list[tuple[int, float]]) -> tuple[float | None, float | None, float | None]:
    vals = [v for _, v in points]
    latest = vals[-1]

    def pct(old: float | None) -> float | None:
        if old in (None, 0):
            return None
        return ((latest - old) / old) * 100.0

    chg_1d = pct(vals[-2]) if len(vals) >= 2 else None
    chg_5d = pct(vals[-6]) if len(vals) >= 6 else None
    chg_20d = pct(vals[-21]) if len(vals) >= 21 else None
    return chg_1d, chg_5d, chg_20d


def yahoo_series(symbol: str, range_: str = "1y", interval: str = "1d") -> dict:
    encoded = urllib.parse.quote(symbol, safe="")
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{encoded}"
        f"?range={range_}&interval={interval}&includePrePost=false"
    )
    try:
        payload = json.loads(http_get(url))
        result = payload["chart"]["result"][0]
        ts = result.get("timestamp", [])
        close = result["indicators"]["quote"][0].get("close", [])
        points = [(int(t), float(v)) for t, v in zip(ts, close) if v is not None]
        if len(points) < 2:
            return {"ok": False, "symbol": symbol, "url": url, "error": "insufficient data"}

        latest_ts, latest = points[-1]
        chg_1d, chg_5d, chg_20d = compute_changes(points)
        return {
            "ok": True,
            "symbol": symbol,
            "url": url,
            "source": "yahoo",
            "asof_utc": datetime.fromtimestamp(latest_ts, tz=timezone.utc).isoformat(),
            "latest": latest,
            "chg_1d_pct": chg_1d,
            "chg_5d_pct": chg_5d,
            "chg_20d_pct": chg_20d,
            "series_close": [v for _, v in points],
        }
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "symbol": symbol, "url": url, "error": str(exc)}


def stooq_series(symbol: str) -> dict:
    stooq_symbol = STOOQ_MAP.get(symbol)
    if not stooq_symbol:
        return {"ok": False, "symbol": symbol, "error": "stooq mapping unavailable"}

    url = f"https://stooq.com/q/d/l/?s={stooq_symbol}&i=d"
    try:
        text = http_get(url)
        reader = csv.DictReader(io.StringIO(text))
        points: list[tuple[int, float]] = []
        for row in reader:
            raw_date = (row.get("Date") or "").strip()
            raw_close = (row.get("Close") or "").strip()
            if not raw_date or not raw_close:
                continue
            try:
                dt = datetime.fromisoformat(raw_date).replace(tzinfo=timezone.utc)
                close_val = float(raw_close)
            except ValueError:
                continue
            points.append((int(dt.timestamp()), close_val))

        if len(points) < 2:
            return {"ok": False, "symbol": symbol, "url": url, "error": "insufficient stooq data"}

        latest_ts, latest = points[-1]
        chg_1d, chg_5d, chg_20d = compute_changes(points)
        return {
            "ok": True,
            "symbol": symbol,
            "url": url,
            "source": "stooq",
            "asof_utc": datetime.fromtimestamp(latest_ts, tz=timezone.utc).isoformat(),
            "latest": latest,
            "chg_1d_pct": chg_1d,
            "chg_5d_pct": chg_5d,
            "chg_20d_pct": chg_20d,
            "series_close": [v for _, v in points],
            "stooq_symbol": stooq_symbol,
        }
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "symbol": symbol, "url": url, "error": str(exc)}


def fred_points(series_id: str) -> list[tuple[int, float]]:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    text = http_get(url)
    reader = csv.DictReader(io.StringIO(text))
    fields = reader.fieldnames or []
    if len(fields) < 2:
        return []

    date_key = fields[0]
    value_key = fields[1]

    out: list[tuple[int, float]] = []
    for row in reader:
        raw_date = (row.get(date_key) or "").strip()
        raw_val = (row.get(value_key) or "").strip()
        if not raw_date or not raw_val or raw_val == ".":
            continue
        try:
            dt = datetime.fromisoformat(raw_date).replace(tzinfo=timezone.utc)
            val = float(raw_val)
        except ValueError:
            continue
        out.append((int(dt.timestamp()), val))
    return out


def fred_proxy_series(symbol: str) -> dict:
    # Derived AUDJPY from FRED pairs when possible.
    if symbol == "AUDJPY=X":
        try:
            # DEXJPUS: JPY per USD, DEXUSAL: USD per AUD.
            jpy = fred_points("DEXJPUS")
            aud = fred_points("DEXUSAL")
            if len(jpy) < 2 or len(aud) < 2:
                return {"ok": False, "symbol": symbol, "error": "insufficient FRED FX points"}
            aud_map = {ts: val for ts, val in aud}
            points: list[tuple[int, float]] = []
            for ts, jpy_per_usd in jpy:
                usd_per_aud = aud_map.get(ts)
                if usd_per_aud is None:
                    continue
                points.append((ts, jpy_per_usd * usd_per_aud))
            if len(points) < 2:
                return {"ok": False, "symbol": symbol, "error": "no aligned FRED FX dates"}
            latest_ts, latest = points[-1]
            chg_1d, chg_5d, chg_20d = compute_changes(points)
            return {
                "ok": True,
                "symbol": symbol,
                "url": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DEXJPUS",
                "source": "fred-proxy",
                "asof_utc": datetime.fromtimestamp(latest_ts, tz=timezone.utc).isoformat(),
                "latest": latest,
                "chg_1d_pct": chg_1d,
                "chg_5d_pct": chg_5d,
                "chg_20d_pct": chg_20d,
                "series_close": [v for _, v in points],
                "proxy_series": ["DEXJPUS", "DEXUSAL"],
            }
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "symbol": symbol, "error": str(exc)}

    series_id = FRED_PROXY_MAP.get(symbol)
    if not series_id:
        return {"ok": False, "symbol": symbol, "error": "fred proxy mapping unavailable"}

    try:
        points = fred_points(series_id)
        if len(points) < 2:
            return {"ok": False, "symbol": symbol, "error": "insufficient FRED proxy data"}

        latest_ts, latest = points[-1]
        chg_1d, chg_5d, chg_20d = compute_changes(points)
        return {
            "ok": True,
            "symbol": symbol,
            "url": f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}",
            "source": "fred-proxy",
            "asof_utc": datetime.fromtimestamp(latest_ts, tz=timezone.utc).isoformat(),
            "latest": latest,
            "chg_1d_pct": chg_1d,
            "chg_5d_pct": chg_5d,
            "chg_20d_pct": chg_20d,
            "series_close": [v for _, v in points],
            "proxy_series": [series_id],
        }
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "symbol": symbol, "error": str(exc)}


def load_cache() -> dict[str, dict]:
    if not CACHE_PATH.exists():
        return {}
    try:
        payload = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        symbols = payload.get("symbols")
        if isinstance(symbols, dict):
            return symbols
    except Exception:
        return {}
    return {}


def _cache_age_hours(asof_utc: str) -> float | None:
    try:
        ts = datetime.fromisoformat(asof_utc.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        return (now - ts.astimezone(timezone.utc)).total_seconds() / 3600.0
    except Exception:
        return None


def cache_series(symbol: str, cache: dict[str, dict]) -> dict:
    item = deepcopy(cache.get(symbol) or {})
    if not item:
        return {"ok": False, "symbol": symbol, "error": "cache miss"}

    asof = item.get("asof_utc")
    if not asof:
        return {"ok": False, "symbol": symbol, "error": "cache missing asof_utc"}

    age_h = _cache_age_hours(asof)
    if age_h is None or age_h > CACHE_STALE_HOURS:
        return {"ok": False, "symbol": symbol, "error": "cache too old"}

    item["ok"] = True
    item["symbol"] = symbol
    item["source"] = f"cache:{item.get('source', 'unknown')}"
    item["cache_age_hours"] = round(age_h, 2)
    item["stale"] = age_h > CACHE_FRESH_HOURS
    return item


def save_cache(flat: dict[str, dict]) -> None:
    symbols: dict[str, dict] = {}
    for sym, item in flat.items():
        if not item.get("ok"):
            continue
        if not item.get("series_close"):
            continue
        symbols[sym] = deepcopy(item)

    if not symbols:
        return

    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "symbols": symbols,
    }
    CACHE_PATH.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def fetch_symbol_with_fallback(symbol: str, cache: dict[str, dict]) -> dict:
    attempts: list[str] = []

    primary = yahoo_series(symbol)
    if primary.get("ok"):
        return primary
    attempts.append(f"yahoo:{primary.get('error', 'unknown')}" )

    alt_stooq = stooq_series(symbol)
    if alt_stooq.get("ok"):
        alt_stooq["fallback_chain"] = attempts
        return alt_stooq
    attempts.append(f"stooq:{alt_stooq.get('error', 'unknown')}" )

    alt_fred = fred_proxy_series(symbol)
    if alt_fred.get("ok"):
        alt_fred["fallback_chain"] = attempts
        return alt_fred
    attempts.append(f"fred-proxy:{alt_fred.get('error', 'unknown')}" )

    cached = cache_series(symbol, cache)
    if cached.get("ok"):
        cached["fallback_chain"] = attempts
        return cached
    attempts.append(f"cache:{cached.get('error', 'unknown')}" )

    return {
        "ok": False,
        "symbol": symbol,
        "url": primary.get("url"),
        "error": "all sources failed",
        "fallback_chain": attempts,
    }


def fred_latest(series_id: str) -> dict:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    try:
        points = fred_points(series_id)
        if not points:
            return {"ok": False, "series": series_id, "url": url, "error": "no numeric value"}
        latest_ts, latest = points[-1]
        date_val = datetime.fromtimestamp(latest_ts, tz=timezone.utc).date().isoformat()
        return {
            "ok": True,
            "series": series_id,
            "date": date_val,
            "value": latest,
            "url": url,
        }
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "series": series_id, "url": url, "error": str(exc)}


def safe_latest(data: dict, symbol: str) -> float | None:
    item = data.get(symbol)
    if not item or not item.get("ok"):
        return None
    return item.get("latest")


def calc_breadth_proxy(flat: dict[str, dict]) -> dict:
    available = []
    for sym in BREADTH_PROXY_UNIVERSE:
        item = flat.get(sym)
        if not item or not item.get("ok"):
            continue
        closes = item.get("series_close") or []
        if len(closes) < 210:
            continue
        available.append((sym, closes))

    if not available:
        return {
            "ok": False,
            "error": "insufficient proxy breadth history",
            "universe": BREADTH_PROXY_UNIVERSE,
        }

    advancers = 0
    decliners = 0
    above_200d = 0
    new_highs_20d = 0
    new_lows_20d = 0

    for _, closes in available:
        latest = closes[-1]
        prev = closes[-2]
        ma200 = sum(closes[-200:]) / 200.0

        if latest > prev:
            advancers += 1
        elif latest < prev:
            decliners += 1

        if latest > ma200:
            above_200d += 1

        if latest >= max(closes[-20:]):
            new_highs_20d += 1
        if latest <= min(closes[-20:]):
            new_lows_20d += 1

    total = len(available)
    return {
        "ok": True,
        "method": "proxy-universe",
        "universe": [sym for sym, _ in available],
        "advancers_1d": advancers,
        "decliners_1d": decliners,
        "ad_line_1d": advancers - decliners,
        "pct_above_200d": (above_200d / total) * 100.0,
        "new_highs_20d": new_highs_20d,
        "new_lows_20d": new_lows_20d,
        "sample_size": total,
    }


def build_snapshot(pause_s: float = 0.25) -> dict:
    out: dict = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": {
            "primary": "yahoo_chart_api_public",
            "fallbacks": ["stooq_csv_public", "fred_proxy_public", "local_cache"],
            "fred": "fredgraph_csv_public",
            "cache_path": str(CACHE_PATH),
        },
        "panels": {},
        "ratios": {},
        "fred": {},
        "derived": {},
    }

    cache = load_cache()
    flat: dict[str, dict] = {}

    for panel, symbols in SYMBOLS.items():
        bucket = {}
        for sym in symbols:
            bucket[sym] = fetch_symbol_with_fallback(sym, cache)
            flat[sym] = bucket[sym]
            time.sleep(pause_s)
        out["panels"][panel] = bucket

    ratio_defs = [
        ("IWM_SPY", "IWM", "SPY"),
        ("XLY_XLP", "XLY", "XLP"),
        ("XHB_SPY", "XHB", "SPY"),
        ("SMH_SPY", "SMH", "SPY"),
        ("KRE_SPY", "KRE", "SPY"),
        ("COPPER_GOLD", "HG=F", "GC=F"),
    ]

    for name, a, b in ratio_defs:
        va = safe_latest(flat, a)
        vb = safe_latest(flat, b)
        if va is None or vb in (None, 0):
            out["ratios"][name] = {"ok": False, "a": a, "b": b}
        else:
            out["ratios"][name] = {"ok": True, "a": a, "b": b, "value": va / vb}

    out["panels"]["breadth_proxy"] = calc_breadth_proxy(flat)

    # Persist successful series for future fallback before stripping output payload.
    save_cache(flat)

    # Remove raw close arrays from output payload to keep output compact.
    for item in flat.values():
        if isinstance(item, dict):
            item.pop("series_close", None)

    for sid in FRED_SERIES:
        out["fred"][sid] = fred_latest(sid)
        time.sleep(0.1)

    f = out["fred"]
    if f.get("WALCL", {}).get("ok") and f.get("RRPONTSYD", {}).get("ok") and f.get("WTREGEN", {}).get("ok"):
        out["derived"]["net_liquidity_proxy_WALCL_minus_RRP_minus_TGA_mn_usd"] = (
            f["WALCL"]["value"] - f["RRPONTSYD"]["value"] - f["WTREGEN"]["value"]
        )

    if f.get("DGS10", {}).get("ok") and f.get("DGS2", {}).get("ok"):
        out["derived"]["curve_10y_minus_2y_pct_pts"] = f["DGS10"]["value"] - f["DGS2"]["value"]

    if f.get("M2SL", {}).get("ok") and f.get("GDP", {}).get("ok") and f["GDP"]["value"] != 0:
        out["derived"]["m2_to_gdp_ratio"] = f["M2SL"]["value"] / f["GDP"]["value"]

    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Stanley workflow panel snapshot")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    parser.add_argument("--output", help="Write output JSON to file path")
    parser.add_argument("--pause", type=float, default=0.25, help="Pause seconds between symbol calls")
    args = parser.parse_args()

    data = build_snapshot(pause_s=args.pause)
    text = json.dumps(data, ensure_ascii=False, indent=2 if args.pretty else None)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text + ("\n" if not text.endswith("\n") else ""), encoding="utf-8")

    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
