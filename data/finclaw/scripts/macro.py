#!/usr/bin/env python3
"""Macro economics data from FRED API."""

import sys, os, json, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.config import get_api_key
from lib.rate_limiter import wait_if_needed
import requests

SERIES = {
    "gdp": ("GDP", "US GDP (Quarterly)", "$B"), "inflation": ("CPIAUCSL", "CPI", "Index"),
    "unemployment": ("UNRATE", "Unemployment Rate", "%"), "fed_rate": ("FEDFUNDS", "Fed Funds Rate", "%"),
    "10y_yield": ("DGS10", "10-Year Treasury", "%"), "2y_yield": ("DGS2", "2-Year Treasury", "%"),
    "m2": ("M2SL", "M2 Money Supply", "$B"), "housing": ("HOUST", "Housing Starts", "K"),
    "retail": ("RSAFS", "Retail Sales", "$M"), "vix": ("VIXCLS", "VIX", "Index"),
}


def get_fred_series(series_id, limit=10):
    api_key = get_api_key("fredApiKey")
    if not api_key: return {"error": "FRED API key not configured. Add FRED_API_KEY to finclaw env config."}
    wait_if_needed("fred")
    data = requests.get("https://api.stlouisfed.org/fred/series/observations",
        params={"series_id": series_id, "api_key": api_key, "file_type": "json",
                "sort_order": "desc", "limit": limit}, timeout=10).json()
    return {"series_id": series_id,
            "observations": [{"date": o["date"], "value": float(o["value"])} for o in data.get("observations", []) if o["value"] != "."]}


def main():
    parser = argparse.ArgumentParser(description="Macro economics data")
    parser.add_argument("action", choices=["indicator", "dashboard", "series", "list"])
    parser.add_argument("--name", "-n"); parser.add_argument("--series-id")
    parser.add_argument("--limit", type=int, default=5); parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.action == "list":
        print("**Available Macro Indicators**\n")
        for k, (sid, name, unit) in SERIES.items(): print(f"  `{k}` — {name} ({sid})")
    elif args.action == "dashboard":
        api_key = get_api_key("fredApiKey")
        if not api_key: print("Error: FRED API key not configured"); sys.exit(1)
        print("**Macro Dashboard**\n")
        for name in ["fed_rate", "10y_yield", "unemployment", "inflation", "vix"]:
            sid, label, unit = SERIES[name]
            try:
                d = get_fred_series(sid, 1)
                if d.get("observations"): print(f"  {label}: {d['observations'][0]['value']}{unit} ({d['observations'][0]['date']})")
            except: print(f"  {label}: _error_")
    elif args.action == "indicator":
        if not args.name: print("Error: --name required"); sys.exit(1)
        if args.name not in SERIES: print(f"Unknown: {args.name}. Use: {', '.join(SERIES.keys())}"); sys.exit(1)
        sid, label, unit = SERIES[args.name]
        d = get_fred_series(sid, args.limit)
        if args.json: print(json.dumps(d, indent=2))
        elif "error" in d: print(f"Error: {d['error']}")
        else:
            print(f"**{label}** ({sid})\n")
            for o in d["observations"]: print(f"  {o['date']}: {o['value']} {unit}")
    elif args.action == "series":
        if not args.series_id: print("Error: --series-id required"); sys.exit(1)
        d = get_fred_series(args.series_id, args.limit)
        if args.json: print(json.dumps(d, indent=2))
        elif "error" in d: print(f"Error: {d['error']}")
        else:
            print(f"**{d['series_id']}**\n")
            for o in d["observations"]: print(f"  {o['date']}: {o['value']}")


if __name__ == "__main__":
    main()
