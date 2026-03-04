#!/usr/bin/env python3
"""Generate a Weather Intelligence Digest using NOAA / NWS data."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import List

import requests

USER_AGENT = "WeatherDigestSkill/1.0 (openclaw)"

HTML_THEMES = {
    "midnight": {
        "bg": "#0f172a",
        "card": "#fff",
        "text": "#0f172a",
        "accent": "#db2777",
        "subhead": "#475569",
        "alert_bg": "#fce7f3",
        "alert_text": "#7f1d1d",
    },
    "daybreak": {
        "bg": "#f7fafc",
        "card": "#ffffff",
        "text": "#1a202c",
        "accent": "#2b6cb0",
        "subhead": "#4a5568",
        "alert_bg": "#ebf8ff",
        "alert_text": "#1a365d",
    },
    "citrus": {
        "bg": "#fff7ed",
        "card": "#ffffff",
        "text": "#1f2933",
        "accent": "#f97316",
        "subhead": "#7b8794",
        "alert_bg": "#fff1c1",
        "alert_text": "#92400e",
    },
}


def fetch_json(url: str) -> dict:
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=20)
    resp.raise_for_status()
    return resp.json()


def get_point_metadata(lat: float, lon: float) -> dict:
    url = f"https://api.weather.gov/points/{lat},{lon}"
    data = fetch_json(url)
    return data["properties"]


def get_forecast(lat: float, lon: float) -> dict:
    meta = get_point_metadata(lat, lon)
    forecast_url = meta["forecast"]
    forecast = fetch_json(forecast_url)["properties"]["periods"]
    return {
        "city": meta.get("relativeLocation", {}).get("properties", {}).get("city"),
        "state": meta.get("relativeLocation", {}).get("properties", {}).get("state"),
        "forecast": forecast,
    }


def summarize_forecast(periods: list) -> List[str]:
    today = periods[:2]
    bullets = []
    for period in today:
        name = period["name"]
        temp = period["temperature"]
        unit = period["temperatureUnit"]
        short = period["shortForecast"]
        wind = period.get("windSpeed") or "calm"
        direction = period.get("windDirection") or ""
        bullets.append(f"**{name}**: {temp}°{unit}, {short} (winds {wind} {direction})")
    return bullets


def get_alerts(lat: float, lon: float) -> list:
    url = f"https://api.weather.gov/alerts/active?point={lat},{lon}"
    data = fetch_json(url)
    features = data.get("features", [])
    alerts = []
    for feature in features:
        props = feature.get("properties", {})
        alerts.append(
            {
                "event": props.get("event"),
                "headline": props.get("headline"),
                "severity": props.get("severity"),
                "instructions": props.get("instruction"),
                "expires": props.get("expires"),
            }
        )
    return alerts


def _format_expiration(expires: str | None) -> str:
    if not expires:
        return ""
    expires_dt = dt.datetime.fromisoformat(expires.replace("Z", "+00:00")).astimezone()
    return expires_dt.strftime("%b %d • %I:%M %p %Z")


def _trim_text(text: str | None, limit: int = 160) -> str:
    if not text:
        return ""
    clean = " ".join(text.split())
    if len(clean) <= limit:
        return clean
    return clean[: limit - 1].rstrip() + "…"


def _strip_md(text: str) -> str:
    return text.replace("**", "")


def format_alerts_md(alerts: list) -> str:
    if not alerts:
        return "- No active alerts"
    lines = []
    for alert in alerts:
        event = alert.get("event") or "Alert"
        severity = alert.get("severity") or "Unknown"
        expiry = _format_expiration(alert.get("expires"))
        headline = alert.get("headline") or "Details forthcoming"
        summary = _trim_text(alert.get("instructions"))
        expires_copy = f" — expires {expiry}" if expiry else ""
        lines.append(f"- **{event}** ({severity}){expires_copy}: {headline}")
        if summary:
            lines.append(f"  - {summary}")
    return "\n".join(lines)


def format_alerts_html(alerts: list) -> str:
    if not alerts:
        return "<div class=\"no-alerts\">No active alerts</div>"
    blocks = []
    for alert in alerts:
        event = alert.get("event") or "Alert"
        severity = alert.get("severity") or "Unknown"
        expiry = _format_expiration(alert.get("expires"))
        headline = alert.get("headline") or "Details forthcoming"
        instructions = _trim_text(alert.get("instructions"), limit=220)
        expiry_html = f"<div class=\"expires\">Expires {expiry}</div>" if expiry else ""
        instructions_html = (
            f"<div class=\"instructions\">{instructions}</div>" if instructions else ""
        )
        blocks.append(
            f"<div class=\"alert\"><div class=\"alert-title\"><strong>{event}</strong>"
            f"<span class=\"pill\">{severity}</span></div>{expiry_html}"
            f"<div class=\"headline\">{headline}</div>{instructions_html}</div>"
        )
    return "".join(blocks)


def gather_reports(locations: list[dict]) -> list[dict]:
    reports = []
    for loc in locations:
        name = loc.get("name") or f"{loc['lat']}, {loc['lon']}"
        forecast_data = get_forecast(loc["lat"], loc["lon"])
        alerts = get_alerts(loc["lat"], loc["lon"])
        reports.append(
            {
                "display_name": name,
                "city": forecast_data.get("city"),
                "state": forecast_data.get("state"),
                "summary_lines": summarize_forecast(forecast_data["forecast"]),
                "alerts": alerts,
            }
        )
    return reports


def build_markdown(reports: list[dict]) -> str:
    today = dt.datetime.now().strftime("%A, %B %d %Y")
    sections = [f"# Weather Intelligence Digest\n*Generated {today}*\n"]
    for report in reports:
        sections.append(f"## {report['display_name']}")
        if report.get("city") and report.get("state"):
            sections.append(f"**Nearest location:** {report['city']}, {report['state']}")
        sections.append("### Outlook")
        sections.extend([f"- {line}" if not line.startswith("-") else line for line in report["summary_lines"]])
        sections.append("\n### Active Alerts")
        sections.append(format_alerts_md(report["alerts"]))
        sections.append("\n")
    return "\n".join(sections)


def build_theme_css(theme: str) -> str:
    palette = HTML_THEMES.get(theme, HTML_THEMES["midnight"])
    return f"""
body{{font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;background:{palette['bg']};color:{palette['text']};margin:0;padding:32px;}}
main{{max-width:960px;margin:auto;}}
header{{color:{palette['subhead']};margin-bottom:24px;}}
.card{{background:{palette['card']};border-radius:14px;padding:20px;margin-bottom:20px;box-shadow:0 10px 30px rgba(15,23,42,.12);color:{palette['text']};}}
.subhead{{color:{palette['subhead']};margin-bottom:10px;}}
h2{{margin:0 0 8px 0;}}
h3{{margin-top:16px;}}
ul{{padding-left:20px;}}
.alert{{background:{palette['alert_bg']};border-left:4px solid {palette['accent']};padding:12px;margin-bottom:12px;border-radius:12px;}}
.alert-title{{display:flex;align-items:center;gap:8px;font-size:1.05rem;}}
.pill{{background:{palette['accent']};color:#fff;border-radius:999px;padding:2px 10px;font-size:.75rem;text-transform:uppercase;letter-spacing:.05em;}}
.expires{{color:{palette['alert_text']};font-size:.85rem;margin-top:4px;}}
.headline{{margin-top:6px;font-weight:500;}}
.instructions{{margin-top:4px;color:{palette['alert_text']};font-size:.9rem;}}
.no-alerts{{color:{palette['subhead']};font-style:italic;}}
"""


def build_html(reports: list[dict], theme: str = "midnight") -> str:
    today = dt.datetime.now().strftime("%A, %B %d %Y")
    cards = []
    for report in reports:
        city_meta = ""
        if report.get("city") and report.get("state"):
            city_meta = f"<div class=\"subhead\">Nearest location: {report['city']}, {report['state']}</div>"
        summary_li = "".join(
            f"<li>{line.replace('**', '')}</li>" for line in report["summary_lines"]
        )
        alerts_html = format_alerts_html(report["alerts"])
        cards.append(
            f"<section class=\"card\"><h2>{report['display_name']}</h2>{city_meta}"
            f"<h3>Outlook</h3><ul>{summary_li}</ul><h3>Active Alerts</h3>{alerts_html}</section>"
        )
    theme_css = build_theme_css(theme)
    html = f"""
<!doctype html>
<html>
<head>
<meta charset=\"utf-8\">
<title>Weather Intelligence Digest</title>
<style>
{theme_css}
</style>
</head>
<body>
<main>
<header>
<h1>Weather Intelligence Digest</h1>
<div>Generated {today}</div>
</header>
{''.join(cards)}
</main>
</body>
</html>
"""
    return html


def build_json_document(reports: list[dict]) -> dict:
    payload = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "reports": [],
    }
    for report in reports:
        payload["reports"].append(
            {
                "display_name": report["display_name"],
                "nearest_location": {
                    "city": report.get("city"),
                    "state": report.get("state"),
                },
                "outlook": [_strip_md(line) for line in report["summary_lines"]],
                "alerts": report["alerts"],
            }
        )
    return payload


def parse_args():
    parser = argparse.ArgumentParser(description="Generate a weather digest for configured locations")
    parser.add_argument("--config", default="config.json", help="Path to config JSON with locations list")
    parser.add_argument("--output", default="digest.md", help="Where to write the markdown digest")
    parser.add_argument("--html", dest="html_path", help="Optional HTML output path")
    parser.add_argument("--json", dest="json_path", help="Optional JSON export path")
    parser.add_argument(
        "--theme",
        choices=sorted(HTML_THEMES.keys()),
        default="midnight",
        help="HTML color theme",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    config_path = Path(args.config)
    if not config_path.exists():
        sys.exit(f"Config file not found: {config_path}")
    config = json.loads(config_path.read_text())
    locations = config.get("locations")
    if not locations:
        sys.exit("Config must include a 'locations' list with name/lat/lon")
    reports = gather_reports(locations)
    markdown = build_markdown(reports)
    output_path = Path(args.output)
    output_path.write_text(markdown)
    print(f"Markdown digest written to {output_path}")
    if args.html_path:
        html = build_html(reports, theme=args.theme)
        html_path = Path(args.html_path)
        html_path.write_text(html)
        print(f"HTML digest written to {html_path} (theme: {args.theme})")
    if args.json_path:
        json_payload = build_json_document(reports)
        json_path = Path(args.json_path)
        json_path.write_text(json.dumps(json_payload, indent=2))
        print(f"JSON digest written to {json_path}")


if __name__ == "__main__":
    main()
