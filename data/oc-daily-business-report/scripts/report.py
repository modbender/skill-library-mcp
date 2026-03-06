#!/usr/bin/env python3
"""
daily-business-report: Generate daily business briefings from free public APIs.
Aggregates weather, crypto, news, quotes, and system health.
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

CONFIG_DIR = Path(os.environ.get("REPORT_CONFIG_DIR", Path.home() / ".daily-report"))
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "city": "Brussels",
    "crypto": ["bitcoin", "ethereum"],
    "crypto_currency": "usd",
    "news_country": "us",
    "news_api_key": "",
    "sections": ["date", "weather", "crypto", "news", "quote", "system"],
}


def load_config() -> dict:
    if CONFIG_FILE.exists():
        cfg = json.loads(CONFIG_FILE.read_text())
        merged = {**DEFAULT_CONFIG, **cfg}
        return merged
    return DEFAULT_CONFIG.copy()


def save_config(cfg: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))


def api_get(url: str, timeout: int = 10) -> str | None:
    """Safe API GET request."""
    try:
        req = Request(url, headers={"User-Agent": "daily-business-report/1.0"})
        with urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except (HTTPError, URLError, TimeoutError):
        return None


# ─── Data Sources ────────────────────────────────────────────

def fetch_date() -> dict:
    now = datetime.now(timezone.utc)
    return {
        "section": "date",
        "date": now.strftime("%A, %d %B %Y"),
        "time_utc": now.strftime("%H:%M UTC"),
    }


def fetch_weather(city: str) -> dict:
    """Weather from wttr.in (free, no API key)."""
    data = api_get(f"https://wttr.in/{city}?format=j1")
    if not data:
        return {"section": "weather", "error": "Could not fetch weather"}

    try:
        j = json.loads(data)
        current = j["current_condition"][0]
        return {
            "section": "weather",
            "city": city,
            "temp_c": current["temp_C"],
            "feels_like_c": current["FeelsLikeC"],
            "description": current["weatherDesc"][0]["value"],
            "humidity": current["humidity"],
            "wind_kmh": current["windspeedKmph"],
        }
    except (KeyError, json.JSONDecodeError):
        return {"section": "weather", "error": "Failed to parse weather data"}


def fetch_crypto(coins: list, currency: str = "usd") -> dict:
    """Crypto prices from CoinGecko (free, no API key)."""
    ids = ",".join(coins)
    data = api_get(f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies={currency}&include_24hr_change=true")
    if not data:
        return {"section": "crypto", "error": "Could not fetch crypto prices"}

    try:
        j = json.loads(data)
        prices = []
        for coin in coins:
            if coin in j:
                prices.append({
                    "coin": coin,
                    "price": j[coin].get(currency, 0),
                    "change_24h": round(j[coin].get(f"{currency}_24h_change", 0), 2),
                })
        return {"section": "crypto", "currency": currency, "prices": prices}
    except (KeyError, json.JSONDecodeError):
        return {"section": "crypto", "error": "Failed to parse crypto data"}


def fetch_news(country: str = "us", api_key: str = "") -> dict:
    """News headlines. Uses NewsData.io if API key provided, else a fallback."""
    if api_key:
        data = api_get(f"https://newsdata.io/api/1/latest?apikey={api_key}&country={country}&language=en&size=5")
        if data:
            try:
                j = json.loads(data)
                headlines = [{"title": a["title"], "source": a.get("source_name", "")} for a in j.get("results", [])[:5]]
                return {"section": "news", "headlines": headlines}
            except (KeyError, json.JSONDecodeError):
                pass

    # Fallback: wttr.in doesn't do news, so return a helpful message
    return {
        "section": "news",
        "headlines": [],
        "note": "Set a NewsData.io API key (free tier) for news headlines: report.py config --news-key YOUR_KEY",
    }


def fetch_quote() -> dict:
    """Inspirational quote from Quotable API."""
    data = api_get("https://api.quotable.io/quotes/random?limit=1")
    if data:
        try:
            j = json.loads(data)
            if j and len(j) > 0:
                return {
                    "section": "quote",
                    "text": j[0]["content"],
                    "author": j[0]["author"],
                }
        except (KeyError, json.JSONDecodeError, IndexError):
            pass

    return {"section": "quote", "text": "The best way to predict the future is to create it.", "author": "Peter Drucker"}


def fetch_system() -> dict:
    """Local system health."""
    result = {"section": "system"}

    # Disk usage
    try:
        total, used, free = shutil.disk_usage("/")
        result["disk_total_gb"] = round(total / (1024**3), 1)
        result["disk_used_gb"] = round(used / (1024**3), 1)
        result["disk_percent"] = round(used / total * 100, 1)
    except OSError:
        result["disk_error"] = "Could not read disk info"

    # Memory (Linux only)
    try:
        with open("/proc/meminfo") as f:
            mem = {}
            for line in f:
                parts = line.split()
                if len(parts) >= 2:
                    mem[parts[0].rstrip(":")] = int(parts[1])
            total_mb = mem.get("MemTotal", 0) / 1024
            avail_mb = mem.get("MemAvailable", 0) / 1024
            used_mb = total_mb - avail_mb
            result["ram_total_mb"] = round(total_mb)
            result["ram_used_mb"] = round(used_mb)
            result["ram_percent"] = round(used_mb / max(total_mb, 1) * 100, 1)
    except (FileNotFoundError, KeyError):
        pass  # Not Linux or no /proc

    return result


FETCHERS = {
    "date": lambda cfg: fetch_date(),
    "weather": lambda cfg: fetch_weather(cfg["city"]),
    "crypto": lambda cfg: fetch_crypto(cfg["crypto"], cfg["crypto_currency"]),
    "news": lambda cfg: fetch_news(cfg["news_country"], cfg.get("news_api_key", "")),
    "quote": lambda cfg: fetch_quote(),
    "system": lambda cfg: fetch_system(),
}


# ─── Formatting ──────────────────────────────────────────────

def format_text(sections: list[dict]) -> str:
    """Format report as styled text."""
    lines = []
    lines.append("╔" + "═" * 54 + "╗")

    for s in sections:
        sec = s.get("section", "")

        if sec == "date":
            lines.append(f"║  DAILY BUSINESS REPORT — {s['date']:<28}║")
            lines.append("╠" + "═" * 54 + "╣")

        elif sec == "weather":
            if "error" in s:
                lines.append(f"║  🌤 Weather: {s['error']:<40}║")
            else:
                w = f"{s['city']} — {s['temp_c']}°C, {s['description']}"
                lines.append(f"║  🌤 {w:<49}║")

        elif sec == "crypto":
            if "error" in s:
                lines.append(f"║  📈 Crypto: {s['error']:<41}║")
            else:
                parts = []
                for p in s.get("prices", []):
                    sign = "+" if p["change_24h"] >= 0 else ""
                    name = p["coin"][:3].upper()
                    parts.append(f"{name}: ${p['price']:,.0f} ({sign}{p['change_24h']}%)")
                crypto_str = " | ".join(parts)
                lines.append(f"║  📈 {crypto_str:<49}║")

        elif sec == "news":
            headlines = s.get("headlines", [])
            if headlines:
                lines.append(f"║  📰 Top News:{' ':40}║")
                for i, h in enumerate(headlines[:3], 1):
                    title = h["title"][:45]
                    lines.append(f"║     {i}. {title:<47}║")
            elif s.get("note"):
                lines.append(f"║  📰 News: (configure API key for headlines){' ':9}║")

        elif sec == "quote":
            text = s.get("text", "")
            author = s.get("author", "")
            if len(text) > 45:
                lines.append(f"║  💬 \"{text[:44]}\"  ║")
                lines.append(f"║     — {author:<47}║")
            else:
                lines.append(f"║  💬 \"{text}\" — {author:<10}║")

        elif sec == "system":
            parts = []
            if "disk_percent" in s:
                parts.append(f"Disk: {s['disk_percent']}%")
            if "ram_percent" in s:
                parts.append(f"RAM: {s['ram_percent']}%")
            if parts:
                sys_str = " | ".join(parts)
                lines.append(f"║  💾 {sys_str:<49}║")

    lines.append("╚" + "═" * 54 + "╝")
    return "\n".join(lines)


def format_markdown(sections: list[dict]) -> str:
    """Format report as markdown."""
    lines = []

    for s in sections:
        sec = s.get("section", "")

        if sec == "date":
            lines.append(f"# Daily Report — {s['date']}")
            lines.append(f"*Generated at {s['time_utc']}*")
            lines.append("")

        elif sec == "weather":
            lines.append("## Weather")
            if "error" in s:
                lines.append(f"*{s['error']}*")
            else:
                lines.append(f"**{s['city']}**: {s['temp_c']}°C (feels like {s['feels_like_c']}°C)")
                lines.append(f"{s['description']}, humidity {s['humidity']}%, wind {s['wind_kmh']} km/h")
            lines.append("")

        elif sec == "crypto":
            lines.append("## Crypto")
            if "error" in s:
                lines.append(f"*{s['error']}*")
            else:
                for p in s.get("prices", []):
                    sign = "+" if p["change_24h"] >= 0 else ""
                    lines.append(f"- **{p['coin'].title()}**: ${p['price']:,.2f} ({sign}{p['change_24h']}%)")
            lines.append("")

        elif sec == "news":
            lines.append("## News")
            for h in s.get("headlines", []):
                lines.append(f"- {h['title']} *({h.get('source', '')})*")
            if not s.get("headlines"):
                lines.append(f"*{s.get('note', 'No headlines available')}*")
            lines.append("")

        elif sec == "quote":
            lines.append("## Quote of the Day")
            lines.append(f"> {s.get('text', '')}")
            lines.append(f"> — *{s.get('author', '')}*")
            lines.append("")

        elif sec == "system":
            lines.append("## System Health")
            if "disk_percent" in s:
                lines.append(f"- Disk: {s['disk_used_gb']}/{s['disk_total_gb']} GB ({s['disk_percent']}%)")
            if "ram_percent" in s:
                lines.append(f"- RAM: {s['ram_used_mb']}/{s['ram_total_mb']} MB ({s['ram_percent']}%)")
            lines.append("")

    return "\n".join(lines)


# ─── Commands ────────────────────────────────────────────────

def cmd_generate(sections_filter: list = None, fmt: str = "text", output: str = None):
    cfg = load_config()
    active_sections = sections_filter or cfg.get("sections", DEFAULT_CONFIG["sections"])

    results = []
    for sec in active_sections:
        if sec in FETCHERS:
            print(f"  Fetching {sec}...", file=sys.stderr)
            results.append(FETCHERS[sec](cfg))

    if fmt == "json":
        text = json.dumps(results, indent=2, ensure_ascii=False)
    elif fmt == "md":
        text = format_markdown(results)
    else:
        text = format_text(results)

    if output:
        Path(output).write_text(text, encoding="utf-8")
        print(f"Report saved to {output}", file=sys.stderr)
    else:
        print(text)


def cmd_config(city=None, crypto=None, news_country=None, news_key=None, show=False):
    cfg = load_config()

    if show:
        print(json.dumps(cfg, indent=2))
        return

    if city:
        cfg["city"] = city
    if crypto:
        cfg["crypto"] = [c.strip().lower() for c in crypto.split(",")]
    if news_country:
        cfg["news_country"] = news_country
    if news_key:
        cfg["news_api_key"] = news_key

    save_config(cfg)
    print("Configuration updated.")
    print(json.dumps(cfg, indent=2))


def cmd_test(source: str):
    cfg = load_config()
    if source not in FETCHERS:
        print(f"Unknown source: {source}. Available: {', '.join(FETCHERS.keys())}", file=sys.stderr)
        sys.exit(1)

    result = FETCHERS[source](cfg)
    print(json.dumps(result, indent=2, ensure_ascii=False))


# ─── CLI ─────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Daily Business Report Generator")
    sub = parser.add_subparsers(dest="command", required=True)

    p_gen = sub.add_parser("generate", help="Generate report")
    p_gen.add_argument("--sections", help="Comma-separated sections")
    p_gen.add_argument("-f", "--format", default="text", choices=["text", "json", "md"])
    p_gen.add_argument("-o", "--output", help="Output file")

    p_cfg = sub.add_parser("config", help="Configure preferences")
    p_cfg.add_argument("--city", help="City for weather")
    p_cfg.add_argument("--crypto", help="Comma-separated coin IDs (e.g. bitcoin,ethereum)")
    p_cfg.add_argument("--news-country", help="2-letter country code")
    p_cfg.add_argument("--news-key", help="NewsData.io API key")
    p_cfg.add_argument("--show", action="store_true", help="Show current config")

    p_test = sub.add_parser("test", help="Test a data source")
    p_test.add_argument("source", help="Source to test")

    args = parser.parse_args()

    if args.command == "generate":
        sections = [s.strip() for s in args.sections.split(",")] if args.sections else None
        cmd_generate(sections, args.format, args.output)
    elif args.command == "config":
        cmd_config(args.city, args.crypto, args.news_country, args.news_key, args.show)
    elif args.command == "test":
        cmd_test(args.source)


if __name__ == "__main__":
    main()
