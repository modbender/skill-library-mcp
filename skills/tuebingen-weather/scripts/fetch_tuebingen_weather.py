#!/usr/bin/env python3
"""Fetch current + daily weather summary for Tübingen via Open-Meteo."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from textwrap import dedent
from urllib import request

API_URL = (
    "https://api.open-meteo.com/v1/forecast?latitude=48.5216&longitude=9.0576"
    "&current_weather=true"
    "&hourly=temperature_2m,precipitation_probability"
    "&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max"
    "&timezone=Europe/Berlin"
)

WEATHER_CODES = {
    0: "Klar",
    1: "Überwiegend klar",
    2: "Teilweise bewölkt",
    3: "Bewölkt",
    45: "Nebel",
    48: "Nebel mit Reifansatz",
    51: "Leichter Nieselregen",
    53: "Mäßiger Nieselregen",
    55: "Starker Nieselregen",
    56: "Leichter gefrierender Niesel",
    57: "Starker gefrierender Niesel",
    61: "Leichter Regen",
    63: "Mäßiger Regen",
    65: "Starker Regen",
    66: "Leichter gefrierender Regen",
    67: "Starker gefrierender Regen",
    71: "Leichter Schneefall",
    73: "Mäßiger Schneefall",
    75: "Starker Schneefall",
    80: "Leichte Regenschauer",
    81: "Mäßige Regenschauer",
    82: "Heftige Regenschauer",
    85: "Leichte Schneeschauer",
    86: "Heftige Schneeschauer",
    95: "Gewitter",
    96: "Gewitter mit leichtem Hagel",
    99: "Gewitter mit starkem Hagel",
}


def fetch() -> dict:
    with request.urlopen(API_URL, timeout=15) as resp:  # noqa: S310
        return json.load(resp)


def describe(code: int) -> str:
    return WEATHER_CODES.get(code, f"Wettercode {code}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Tübingen-Wetter zusammenfassen")
    parser.add_argument(
        "--output",
        type=Path,
        help="Optionaler Speicherpfad für die erzeugte Textzusammenfassung",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        data = fetch()
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    current = data["current_weather"]
    daily = data["daily"]
    today_idx = 0
    today_max = daily["temperature_2m_max"][today_idx]
    today_min = daily["temperature_2m_min"][today_idx]
    today_rain = daily["precipitation_probability_max"][today_idx]

    now = dt.datetime.fromisoformat(current["time"]).strftime("%d.%m.%Y %H:%M")
    summary = dedent(
        f"""
        Tübingen Wetter ({now}):
        • Aktuell: {current['temperature']}°C, Wind {current['windspeed']} km/h aus {current['winddirection']}°, {describe(current['weathercode'])}
        • Heute: {today_min:.1f}°C bis {today_max:.1f}°C, max. Regenwahrscheinlichkeit {today_rain}%
        • Hinweis: Wetterdaten via open-meteo.com
        """
    ).strip()

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(summary + "\n", encoding="utf-8")

    print(summary)


if __name__ == "__main__":
    main()
