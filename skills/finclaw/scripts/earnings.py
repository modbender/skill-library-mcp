#!/usr/bin/env python3
"""Earnings calendar from Finnhub."""

import sys, os, json, argparse
from datetime import datetime, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.config import get_api_key
from lib.rate_limiter import wait_if_needed
import requests


def get_earnings_calendar(from_date=None, to_date=None):
    api_key = get_api_key("finnhubApiKey")
    if not api_key: return [{"error": "Finnhub API key not configured"}]
    if not from_date: from_date = datetime.now().strftime("%Y-%m-%d")
    if not to_date: to_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
    wait_if_needed("finnhub")
    data = requests.get("https://finnhub.io/api/v1/calendar/earnings",
        params={"from": from_date, "to": to_date, "token": api_key}, timeout=10).json()
    return [{"symbol": e.get("symbol", ""), "date": e.get("date", ""), "hour": e.get("hour", ""),
             "eps_estimate": e.get("epsEstimate")} for e in data.get("earningsCalendar", [])[:50]]


def get_earnings_for_symbol(symbol):
    api_key = get_api_key("finnhubApiKey")
    if not api_key: return [{"error": "Finnhub API key not configured"}]
    wait_if_needed("finnhub")
    return requests.get("https://finnhub.io/api/v1/stock/earnings",
        params={"symbol": symbol.upper(), "token": api_key}, timeout=10).json()[:10]


def main():
    parser = argparse.ArgumentParser(description="Earnings calendar")
    parser.add_argument("action", choices=["calendar", "symbol"])
    parser.add_argument("--symbol", "-s"); parser.add_argument("--from-date"); parser.add_argument("--to-date")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.action == "calendar":
        data = get_earnings_calendar(args.from_date, args.to_date)
        if args.json: print(json.dumps(data, indent=2)); return
        if data and data[0].get("error"): print(f"Error: {data[0]['error']}"); return
        print("**Upcoming Earnings**\n")
        cur = ""
        for e in data:
            if e["date"] != cur: cur = e["date"]; print(f"\n**{cur}**")
            hour = {"bmo": "Before Open", "amc": "After Close"}.get(e.get("hour", ""), "")
            eps = f" (est: {e['eps_estimate']})" if e.get("eps_estimate") else ""
            print(f"  {e['symbol']} {hour}{eps}")
    elif args.action == "symbol":
        if not args.symbol: print("Error: --symbol required"); sys.exit(1)
        data = get_earnings_for_symbol(args.symbol)
        if args.json: print(json.dumps(data, indent=2)); return
        print(f"**Earnings History: {args.symbol.upper()}**\n")
        for e in data:
            print(f"  {e.get('period','?')}: EPS {e.get('actual','N/A')} (est: {e.get('estimate','N/A')}, surprise: {e.get('surprisePercent','N/A')}%)")


if __name__ == "__main__":
    main()
