#!/usr/bin/env python3
"""
Build a monitoring snapshot using Yahoo Finance quotes plus optional
Questrade-exported CSV data.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import math
import sys
import urllib.request
from pathlib import Path
from typing import Dict, Iterable, List, Optional


YAHOO_CHART_URL = "https://query2.finance.yahoo.com/v8/finance/chart/{symbol}"


def parse_symbols(symbols_text: str) -> List[str]:
    symbols = []
    for part in symbols_text.split(","):
        symbol = part.strip().upper()
        if symbol:
            symbols.append(symbol)
    if not symbols:
        raise ValueError("At least one symbol is required.")
    return sorted(set(symbols))


def to_float(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return float(text.replace(",", ""))
    except ValueError:
        return None


def to_int(value: Optional[str]) -> Optional[int]:
    number = to_float(value)
    if number is None:
        return None
    return int(number)


def find_latest(values: Iterable[Optional[float]]) -> Optional[float]:
    for value in reversed(list(values)):
        if value is not None:
            return float(value)
    return None


def fetch_yahoo_chart_quote(symbol: str) -> Optional[dict]:
    url = YAHOO_CHART_URL.format(symbol=symbol)
    url += "?range=1d&interval=1m&includePrePost=true&events=div,split"
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            )
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        payload = json.loads(response.read().decode("utf-8"))

    chart = payload.get("chart", {})
    if chart.get("error"):
        return None
    results = chart.get("result") or []
    if not results:
        return None

    result = results[0]
    meta = result.get("meta", {})
    quote = (result.get("indicators", {}).get("quote") or [{}])[0]
    latest_close = find_latest(quote.get("close") or [])
    latest_volume = find_latest(quote.get("volume") or [])

    market_time = meta.get("regularMarketTime")
    market_ts = None
    if isinstance(market_time, (int, float)):
        market_ts = dt.datetime.fromtimestamp(
            int(market_time), tz=dt.timezone.utc
        ).isoformat()

    market_price = meta.get("regularMarketPrice")
    if market_price is None:
        market_price = latest_close

    market_volume = meta.get("regularMarketVolume")
    if market_volume is None:
        market_volume = latest_volume

    return {
        "symbol": symbol,
        "price": market_price,
        "bid": None,
        "ask": None,
        "volume": market_volume,
        "currency": meta.get("currency"),
        "exchange": meta.get("fullExchangeName") or meta.get("exchangeName"),
        "market_state": "unknown",
        "market_time_utc": market_ts,
    }


def fetch_yahoo_quotes(symbols: Iterable[str]) -> Dict[str, dict]:
    quotes: Dict[str, dict] = {}
    for symbol in symbols:
        try:
            quote = fetch_yahoo_chart_quote(symbol)
            if quote is not None:
                quotes[symbol] = quote
        except Exception as exc:
            print(f"Warning: Yahoo request failed for {symbol}: {exc}", file=sys.stderr)
    return quotes


def lower_map(row: dict) -> Dict[str, str]:
    return {str(key).strip().lower(): value for key, value in row.items()}


def first_value(row: Dict[str, str], keys: Iterable[str]) -> Optional[str]:
    for key in keys:
        if key in row and str(row[key]).strip():
            return str(row[key]).strip()
    return None


def load_questrade_csv(path: Path) -> Dict[str, dict]:
    if not path.exists():
        raise FileNotFoundError(f"Questrade CSV not found: {path}")

    quotes: Dict[str, dict] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("Questrade CSV has no header row.")

        for raw_row in reader:
            row = lower_map(raw_row)
            symbol = first_value(row, ("symbol", "ticker", "security", "instrument"))
            if not symbol:
                continue
            symbol = symbol.upper()
            quotes[symbol] = {
                "symbol": symbol,
                "last": to_float(
                    first_value(row, ("last", "lastprice", "price", "mark"))
                ),
                "bid": to_float(first_value(row, ("bid", "bidprice"))),
                "ask": to_float(first_value(row, ("ask", "askprice"))),
                "volume": to_int(first_value(row, ("volume", "vol"))),
                "timestamp": first_value(
                    row,
                    (
                        "timestamp",
                        "time",
                        "updatedat",
                        "quote_time",
                        "quote time",
                    ),
                ),
            }
    return quotes


def diff_pct(a: Optional[float], b: Optional[float]) -> Optional[float]:
    if a is None or b is None:
        return None
    if b == 0:
        return None
    return ((a - b) / b) * 100.0


def build_snapshot(
    symbols: List[str], yahoo_quotes: Dict[str, dict], questrade_quotes: Dict[str, dict]
) -> dict:
    now = dt.datetime.now(tz=dt.timezone.utc).isoformat()
    rows = []
    for symbol in symbols:
        y = yahoo_quotes.get(symbol, {})
        q = questrade_quotes.get(symbol, {})

        y_price = to_float(y.get("price"))
        q_last = to_float(q.get("last"))
        price_delta = None
        if q_last is not None and y_price is not None:
            price_delta = q_last - y_price

        row = {
            "symbol": symbol,
            "snapshot_time_utc": now,
            "yahoo_price": y_price,
            "yahoo_bid": to_float(y.get("bid")),
            "yahoo_ask": to_float(y.get("ask")),
            "yahoo_volume": to_int(y.get("volume")),
            "yahoo_market_state": y.get("market_state"),
            "yahoo_exchange": y.get("exchange"),
            "yahoo_market_time_utc": y.get("market_time_utc"),
            "questrade_last": q_last,
            "questrade_bid": to_float(q.get("bid")),
            "questrade_ask": to_float(q.get("ask")),
            "questrade_volume": to_int(q.get("volume")),
            "questrade_timestamp": q.get("timestamp"),
            "price_delta_qt_minus_yahoo": price_delta,
            "price_delta_pct": diff_pct(q_last, y_price),
            "symbol_status": "ok",
        }
        if not y and not q:
            row["symbol_status"] = "missing_all_sources"
        elif not y:
            row["symbol_status"] = "missing_yahoo"
        elif not q:
            row["symbol_status"] = "missing_questrade"

        rows.append(row)

    return {"generated_at_utc": now, "count": len(rows), "rows": rows}


def write_csv(path: Path, rows: List[dict]) -> None:
    fieldnames = [
        "symbol",
        "snapshot_time_utc",
        "symbol_status",
        "yahoo_price",
        "yahoo_bid",
        "yahoo_ask",
        "yahoo_volume",
        "yahoo_market_state",
        "yahoo_exchange",
        "yahoo_market_time_utc",
        "questrade_last",
        "questrade_bid",
        "questrade_ask",
        "questrade_volume",
        "questrade_timestamp",
        "price_delta_qt_minus_yahoo",
        "price_delta_pct",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            cleaned = {}
            for key in fieldnames:
                value = row.get(key)
                if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
                    cleaned[key] = ""
                else:
                    cleaned[key] = value
            writer.writerow(cleaned)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create a monitoring snapshot by combining Yahoo quotes with "
            "optional Questrade CSV quote exports."
        )
    )
    parser.add_argument(
        "--symbols",
        required=True,
        help="Comma-separated symbols (example: AAPL,MSFT,TSLA).",
    )
    parser.add_argument(
        "--questrade-csv",
        default="",
        help="Path to Questrade CSV export with symbol and quote columns.",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Output file path.",
    )
    parser.add_argument(
        "--format",
        choices=("json", "csv"),
        default="json",
        help="Output format. Default: json.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        symbols = parse_symbols(args.symbols)
        yahoo_quotes = fetch_yahoo_quotes(symbols)
        questrade_quotes = {}
        if args.questrade_csv:
            questrade_quotes = load_questrade_csv(Path(args.questrade_csv))
        snapshot = build_snapshot(symbols, yahoo_quotes, questrade_quotes)
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if args.format == "json":
            out_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
        else:
            write_csv(out_path, snapshot["rows"])
        print(f"Wrote {snapshot['count']} symbols to {out_path}")
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
