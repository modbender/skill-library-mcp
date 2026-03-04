#!/usr/bin/env python3
"""News sentiment via Alpha Vantage."""

import sys, os, json, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.config import get_api_key
from lib.rate_limiter import wait_if_needed
import requests


def get_sentiment(symbol=None, topics=None):
    api_key = get_api_key("alphaVantageApiKey")
    if not api_key: return {"error": "Alpha Vantage API key not configured. Add ALPHA_VANTAGE_API_KEY to finclaw env config."}
    params = {"function": "NEWS_SENTIMENT", "apikey": api_key, "limit": 20}
    if symbol: params["tickers"] = symbol.upper()
    if topics: params["topics"] = topics
    wait_if_needed("alpha_vantage")
    data = requests.get("https://www.alphavantage.co/query", params=params, timeout=15).json()
    if "feed" not in data: return {"error": data.get("Note", "No data")}
    articles = [{"title": a.get("title", ""), "source": a.get("source", ""),
                 "score": float(a.get("overall_sentiment_score", 0)),
                 "label": a.get("overall_sentiment_label", "")} for a in data["feed"][:15]]
    avg = sum(a["score"] for a in articles) / len(articles) if articles else 0
    label = "Bullish" if avg > 0.35 else "Somewhat Bullish" if avg > 0.15 else "Neutral" if avg > -0.15 else "Somewhat Bearish" if avg > -0.35 else "Bearish"
    return {"query": symbol or topics or "general", "count": len(articles), "avg_sentiment": round(avg, 4),
            "label": label, "articles": articles}


def main():
    parser = argparse.ArgumentParser(description="News sentiment")
    parser.add_argument("--symbol", "-s"); parser.add_argument("--topics"); parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    d = get_sentiment(args.symbol, args.topics)
    if args.json: print(json.dumps(d, indent=2)); return
    if "error" in d: print(f"Error: {d['error']}"); return
    e = {"Bullish": "🟢", "Somewhat Bullish": "🟡", "Neutral": "⚪", "Somewhat Bearish": "🟡", "Bearish": "🔴"}.get(d["label"], "⚪")
    print(f"**Sentiment: {d['query']}**\n\n{e} {d['label']} ({d['avg_sentiment']:.4f}) — {d['count']} articles\n")
    for a in d["articles"][:10]:
        ae = "🟢" if a["score"] > 0.15 else "🔴" if a["score"] < -0.15 else "⚪"
        print(f"{ae} {a['title']}\n   _{a['source']} | {a['label']}_")


if __name__ == "__main__":
    main()
