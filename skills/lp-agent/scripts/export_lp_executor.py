#!/usr/bin/env python3
"""
Export a single LP executor to CSV by executor ID.

Fetches from the Hummingbot REST API — no SQLite database required.

Usage:
    python scripts/export_lp_executor.py --id <executor_id>
    python scripts/export_lp_executor.py --id <executor_id> --output exports/my_run.csv
    python scripts/export_lp_executor.py --id <executor_id> --print

CSV columns (LP executor schema):
  Identity:   id, account_name, controller_id, connector_name, trading_pair
  State:      status, close_type, is_active, is_trading, error_count
  Timing:     created_at, closed_at, close_timestamp, duration_seconds
  PnL:        net_pnl_quote, net_pnl_pct, cum_fees_quote, filled_amount_quote
  Config:     pool_address, lower_price, upper_price, base_amount_config,
              quote_amount_config, side, position_offset_pct,
              auto_close_above_range_seconds, auto_close_below_range_seconds,
              keep_position
  Live/Final: state, position_address, current_price, lower_price_actual,
              upper_price_actual, base_amount_current, quote_amount_current,
              base_fee, quote_fee, fees_earned_quote, total_value_quote,
              unrealized_pnl_quote, position_rent, position_rent_refunded,
              tx_fee, out_of_range_seconds, max_retries_reached,
              initial_base_amount, initial_quote_amount
"""

import argparse
import base64
import csv
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime


# ---------------------------------------------------------------------------
# Auth / config  (HUMMINGBOT_API_URL / API_USER / API_PASS — same as other lp-agent scripts)
# ---------------------------------------------------------------------------

def load_env():
    """Load environment from .env files (first found wins)."""
    for path in [".env", os.path.expanduser("~/.hummingbot/.env"), os.path.expanduser("~/.env")]:
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
            break


def get_api_config():
    """Get API configuration from environment."""
    load_env()
    return {
        "url":      os.environ.get("HUMMINGBOT_API_URL", "http://localhost:8000"),
        "user":     os.environ.get("API_USER", "admin"),
        "password": os.environ.get("API_PASS", "admin"),
    }


def make_auth_header(cfg):
    creds = base64.b64encode(f"{cfg['user']}:{cfg['password']}".encode()).decode()
    return f"Basic {creds}"


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------

def api_get(url, headers, timeout=30):
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read().decode(errors='replace')}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Connection error: {e.reason}") from e


def fetch_executor(base_url, hdrs, executor_id):
    """GET /executors/{id} — returns the executor dict."""
    raw = api_get(f"{base_url}/executors/{executor_id}", hdrs)
    # Unwrap {"data": [...]} or {"data": {...}}
    if isinstance(raw, dict) and "data" in raw:
        data = raw["data"]
        if isinstance(data, list):
            return data[0] if data else None
        return data
    return raw


# ---------------------------------------------------------------------------
# Schema helpers
# ---------------------------------------------------------------------------

def _f(v, d=None):
    if v is None or v == "":
        return d
    try:
        return float(v)
    except (ValueError, TypeError):
        return d


def _s(v):
    return str(v) if v is not None else ""


def _b(v):
    if v is None:
        return ""
    return "true" if v else "false"


def parse_ts(s):
    if not s:
        return None
    try:
        clean = str(s).replace("+00:00", "").replace("Z", "")
        if "." in clean:
            p = clean.split(".")
            clean = p[0] + "." + p[1][:6]
        import calendar
        dt = datetime.fromisoformat(clean)
        return calendar.timegm(dt.timetuple()) + dt.microsecond / 1e6
    except Exception:
        return None


def to_row(ex):
    cfg = ex.get("config") or {}
    ci = ex.get("custom_info") or {}

    created_ts = parse_ts(ex.get("created_at"))
    close_ts = _f(ex.get("close_timestamp")) or parse_ts(ex.get("closed_at"))
    closed_at = _s(ex.get("closed_at"))
    if not closed_at and close_ts:
        closed_at = datetime.utcfromtimestamp(close_ts).strftime("%Y-%m-%dT%H:%M:%S.%f+00:00")

    duration = None
    if created_ts and close_ts and close_ts > created_ts:
        duration = round(close_ts - created_ts, 1)

    return {
        "id":                              _s(ex.get("executor_id") or ex.get("id")),
        "account_name":                    _s(ex.get("account_name")),
        "controller_id":                   _s(ex.get("controller_id")),
        "connector_name":                  _s(ex.get("connector_name")),
        "trading_pair":                    _s(ex.get("trading_pair")),
        "status":                          _s(ex.get("status")),
        "close_type":                      _s(ex.get("close_type")),
        "is_active":                       _b(ex.get("is_active")),
        "is_trading":                      _b(ex.get("is_trading")),
        "error_count":                     ex.get("error_count", 0),
        "created_at":                      _s(ex.get("created_at")),
        "closed_at":                       closed_at,
        "close_timestamp":                 close_ts,
        "duration_seconds":                duration,
        "net_pnl_quote":                   _f(ex.get("net_pnl_quote")),
        "net_pnl_pct":                     _f(ex.get("net_pnl_pct")),
        "cum_fees_quote":                  _f(ex.get("cum_fees_quote")),
        "filled_amount_quote":             _f(ex.get("filled_amount_quote")),
        # config
        "pool_address":                    _s(cfg.get("pool_address")),
        "lower_price":                     _f(cfg.get("lower_price")),
        "upper_price":                     _f(cfg.get("upper_price")),
        "base_amount_config":              _f(cfg.get("base_amount")),
        "quote_amount_config":             _f(cfg.get("quote_amount")),
        "side":                            cfg.get("side"),
        "position_offset_pct":             _f(cfg.get("position_offset_pct")),
        "auto_close_above_range_seconds":  cfg.get("auto_close_above_range_seconds"),
        "auto_close_below_range_seconds":  cfg.get("auto_close_below_range_seconds"),
        "keep_position":                   _b(cfg.get("keep_position")),
        # custom_info
        "state":                           _s(ci.get("state")),
        "position_address":                _s(ci.get("position_address")),
        "current_price":                   _f(ci.get("current_price")),
        "lower_price_actual":              _f(ci.get("lower_price")),
        "upper_price_actual":              _f(ci.get("upper_price")),
        "base_amount_current":             _f(ci.get("base_amount")),
        "quote_amount_current":            _f(ci.get("quote_amount")),
        "base_fee":                        _f(ci.get("base_fee")),
        "quote_fee":                       _f(ci.get("quote_fee")),
        "fees_earned_quote":               _f(ci.get("fees_earned_quote")),
        "total_value_quote":               _f(ci.get("total_value_quote")),
        "unrealized_pnl_quote":            _f(ci.get("unrealized_pnl_quote")),
        "position_rent":                   _f(ci.get("position_rent")),
        "position_rent_refunded":          _f(ci.get("position_rent_refunded")),
        "tx_fee":                          _f(ci.get("tx_fee")),
        "out_of_range_seconds":            _f(ci.get("out_of_range_seconds")),
        "max_retries_reached":             _b(ci.get("max_retries_reached")),
        "initial_base_amount":             _f(ci.get("initial_base_amount")),
        "initial_quote_amount":            _f(ci.get("initial_quote_amount")),
    }


CSV_COLUMNS = [
    "id", "account_name", "controller_id", "connector_name", "trading_pair",
    "status", "close_type", "is_active", "is_trading", "error_count",
    "created_at", "closed_at", "close_timestamp", "duration_seconds",
    "net_pnl_quote", "net_pnl_pct", "cum_fees_quote", "filled_amount_quote",
    "pool_address", "lower_price", "upper_price",
    "base_amount_config", "quote_amount_config", "side",
    "position_offset_pct",
    "auto_close_above_range_seconds", "auto_close_below_range_seconds", "keep_position",
    "state", "position_address", "current_price",
    "lower_price_actual", "upper_price_actual",
    "base_amount_current", "quote_amount_current",
    "base_fee", "quote_fee", "fees_earned_quote",
    "total_value_quote", "unrealized_pnl_quote",
    "position_rent", "position_rent_refunded", "tx_fee",
    "out_of_range_seconds", "max_retries_reached",
    "initial_base_amount", "initial_quote_amount",
]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Export a single LP executor to CSV by ID",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--id", dest="executor_id", required=True,
                        help="Executor ID to export")
    parser.add_argument("--output", "-o",
                        help="Output CSV path (default: data/lp_executor_<id[:10]>_<ts>.csv)")
    parser.add_argument("--print", dest="print_only", action="store_true",
                        help="Print row as JSON instead of writing CSV")
    args = parser.parse_args()

    cfg = get_api_config()
    hdrs = {"Authorization": make_auth_header(cfg)}

    print(f"Fetching executor {args.executor_id} from {cfg['url']} ...")
    try:
        ex = fetch_executor(cfg["url"], hdrs, args.executor_id)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if not ex:
        print("Executor not found.", file=sys.stderr)
        return 1

    row = to_row(ex)

    if args.print_only:
        print(json.dumps(row, indent=2, default=str))
        return 0

    output_path = args.output
    if not output_path:
        os.makedirs("data", exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"data/lp_executor_{args.executor_id[:10]}_{ts}.csv"

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerow(row)

    print(f"Exported to: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
