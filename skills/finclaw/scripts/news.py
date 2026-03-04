#!/usr/bin/env python3
"""Financial news from Finnhub."""

import sys, os, json, argparse
from datetime import datetime, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.config import get_api_key
from lib.rate_limiter import wait_if_needed
import requests


def get_company_news(symbol, days=7):
    api_key = get_api_key("finnhubApiKey")
    if not api_key:
        return [{"error": "Finnhub API key not configured. Add FINNHUB_API_KEY to finclaw env config."}]
    end = datetime.now()
    start = end - timedelta(days=days)
    wait_if_needed("finnhub")
    articles = requests.get("https://finnhub.io/api/v1/company-news",
        params={"symbol": symbol.upper(), "from": start.strftime("%Y-%m-%d"),
                "to": end.strftime("%Y-%m-%d"), "token": api_key}, timeout=10).json()
    return [{"headline": a.get("headline", ""), "summary": a.get("summary", ""),
             "source": a.get("source", ""), "url": a.get("url", ""),
             "datetime": datetime.fromtimestamp(a["datetime"]).strftime("%Y-%m-%d %H:%M") if a.get("datetime") else ""}
            for a in articles[:20]]


def get_market_news(category="general"):
    api_key = get_api_key("finnhubApiKey")
    if not api_key:
        return [{"error": "Finnhub API key not configured"}]
    wait_if_needed("finnhub")
    articles = requests.get("https://finnhub.io/api/v1/news",
        params={"category": category, "token": api_key}, timeout=10).json()
    return [{"headline": a.get("headline", ""), "source": a.get("source", ""),
             "url": a.get("url", ""),
             "datetime": datetime.fromtimestamp(a["datetime"]).strftime("%Y-%m-%d %H:%M") if a.get("datetime") else ""}
            for a in articles[:15]]


def format_news(articles, title="News"):
    if not articles: return "No news found."
    if articles[0].get("error"): return f"Error: {articles[0]['error']}"
    lines = [f"**{title}**\n"]
    for i, a in enumerate(articles, 1):
        lines.append(f"{i}. **{a['headline']}**")
        if a.get("summary"):
            lines.append(f"   {a['summary'][:200]}...")
        meta = [x for x in [a.get("source"), a.get("datetime")] if x]
        if meta: lines.append(f"   _{'  |  '.join(meta)}_")
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Financial news")
    parser.add_argument("action", choices=["company", "market"])
    parser.add_argument("--symbol", "-s")
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--category", default="general")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.action == "company":
        if not args.symbol: print("Error: --symbol required"); sys.exit(1)
        articles = get_company_news(args.symbol, args.days)
        title = f"{args.symbol.upper()} News"
    else:
        articles = get_market_news(args.category)
        title = f"Market News ({args.category})"
    print(json.dumps(articles, indent=2) if args.json else format_news(articles, title))


if __name__ == "__main__":
    main()
