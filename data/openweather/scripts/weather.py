#!/usr/bin/env python3
"""
OpenWeather One Call API 3.0 — CLI helper for OpenClaw

Usage:
  weather.py current [city] [--units imperial|metric|standard]
  weather.py forecast [city] [--days N] [--units imperial|metric|standard]
  weather.py hourly [city] [--hours N] [--units imperial|metric|standard]

If [city] is omitted, the script will use OPENWEATHER_DEFAULT_LOCATION (if set).
Example:
  OPENWEATHER_DEFAULT_LOCATION="Johnstown, PA, US" weather.py current
"""

import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timezone

API_KEY = os.environ.get("OPENWEATHER_API_KEY", "").strip()
DEFAULT_LOCATION = os.environ.get("OPENWEATHER_DEFAULT_LOCATION", "").strip()

ALLOWED_UNITS = {"imperial", "metric", "standard"}
DEFAULT_TIMEOUT_SECS = 12
USER_AGENT = "openclaw-openweather-skill/1.0 (+https://openweathermap.org/)"


def err(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def fetch(url: str):
    # Only allow OpenWeather endpoints (HTTPS only).
    if not (url.startswith("https://api.openweathermap.org/") or url.startswith("https://openweathermap.org/")):
        err("Refusing to request non-OpenWeather URL")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT_SECS) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            msg = json.loads(body).get("message", body)
        except Exception:
            msg = body
        err(f"API error {e.code}: {msg}")
    except Exception as e:
        err(f"Request failed: {e}")


def geocode(city: str):
    encoded = urllib.parse.quote(city)
    url = f"https://api.openweathermap.org/geo/1.0/direct?q={encoded}&limit=1&appid={API_KEY}"
    results = fetch(url)
    if not results:
        err(f"Location not found: '{city}'. Try a more specific name e.g. 'Springfield, IL, US'")
    r = results[0]
    return r["lat"], r["lon"], r.get("name", city), r.get("country", "")


def onecall(lat, lon, units, exclude: str):
    url = (
        f"https://api.openweathermap.org/data/3.0/onecall"
        f"?lat={lat}&lon={lon}&units={units}&exclude={exclude}&appid={API_KEY}"
    )
    return fetch(url)


def wind_dir(deg):
    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    return dirs[round(deg / 45) % 8]


def fmt_time(ts, offset=0):
    dt = datetime.fromtimestamp(ts + offset, tz=timezone.utc)
    hour = int(dt.strftime("%I"))
    ampm = dt.strftime("%p")
    return dt.strftime(f"%a %b {dt.day}, {hour}:{dt.strftime('%M')} {ampm}")


def fmt_date(ts, offset=0):
    dt = datetime.fromtimestamp(ts + offset, tz=timezone.utc)
    return dt.strftime(f"%A, %b {dt.day}")


def unit_labels(units):
    temp = {"imperial": "°F", "metric": "°C", "standard": "K"}.get(units, "°F")
    speed = {"imperial": "mph", "metric": "m/s", "standard": "m/s"}.get(units, "mph")
    return temp, speed


def cmd_current(city, units):
    temp_label, speed_label = unit_labels(units)
    lat, lon, name, country = geocode(city)
    data = onecall(lat, lon, units, exclude="minutely,hourly,daily,alerts")
    c = data["current"]
    offset = data.get("timezone_offset", 0)

    print(f"\n🌤️  Current Weather — {name}, {country}")
    print(f"   As of: {fmt_time(c['dt'], offset)}")
    print(f"   {c['weather'][0]['description'].title()}")
    print(f"   Temperature: {c['temp']:.0f}{temp_label}  (feels like {c['feels_like']:.0f}{temp_label})")
    print(f"   Humidity: {c['humidity']}%")
    print(f"   Wind: {c['wind_speed']:.0f} {speed_label} {wind_dir(c.get('wind_deg', 0))}")
    uvi = c.get("uvi")
    if uvi is not None:
        print(f"   UV Index: {uvi:.0f}")
    if "visibility" in c:
        vis = c["visibility"]
        print(f"   Visibility: {vis/1000:.0f} km" if units == "metric" else f"   Visibility: {vis/1609:.0f} mi")
    print()


def cmd_forecast(city, units, days=7):
    temp_label, _ = unit_labels(units)
    lat, lon, name, country = geocode(city)
    data = onecall(lat, lon, units, exclude="minutely,hourly,alerts")
    offset = data.get("timezone_offset", 0)
    daily = data["daily"][: min(max(days, 1), 8)]

    print(f"\n📅  {len(daily)}-Day Forecast — {name}, {country}\n")
    for d in daily:
        date = fmt_date(d["dt"], offset)
        desc = d["weather"][0]["description"].title()
        hi = d["temp"]["max"]
        lo = d["temp"]["min"]
        pop = int(d.get("pop", 0) * 100)
        rain_str = f"  💧{pop}% chance of rain" if pop >= 20 else ""
        summary = d.get("summary", "")
        print(f"  {date}")
        print(f"    {desc} — High {hi:.0f}{temp_label} / Low {lo:.0f}{temp_label}{rain_str}")
        if summary:
            print(f"    {summary}")
        print()


def cmd_hourly(city, units, hours=12):
    temp_label, _ = unit_labels(units)
    lat, lon, name, country = geocode(city)
    data = onecall(lat, lon, units, exclude="minutely,daily,alerts")
    offset = data.get("timezone_offset", 0)
    hourly = data["hourly"][: min(max(hours, 1), 48)]

    print(f"\n⏰  Next {len(hourly)} Hours — {name}, {country}\n")
    for h in hourly:
        time = fmt_time(h["dt"], offset)
        temp = h["temp"]
        desc = h["weather"][0]["description"].title()
        pop = int(h.get("pop", 0) * 100)
        rain_str = f"  💧{pop}%" if pop >= 20 else ""
        print(f"  {time:<26}  {temp:.0f}{temp_label}  {desc}{rain_str}")
    print()


def parse_args():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)

    cmd = args[0]
    city_parts = []
    flags = {}
    i = 1
    while i < len(args):
        if args[i].startswith("--"):
            if i + 1 < len(args):
                flags[args[i]] = args[i + 1]
                i += 2
            else:
                i += 1
        else:
            city_parts.append(args[i])
            i += 1

    city = " ".join(city_parts).strip() if city_parts else ""
    if not city:
        if DEFAULT_LOCATION:
            city = DEFAULT_LOCATION
        else:
            err(
                "No city provided and OPENWEATHER_DEFAULT_LOCATION is not set.\n"
                "Examples:\n"
                '  weather.py current "New York, NY, US"\n'
                '  export OPENWEATHER_DEFAULT_LOCATION="Johnstown, PA, US"'
            )

    units = flags.get("--units", os.environ.get("OPENWEATHER_UNITS", "imperial")).strip().lower()
    if units not in ALLOWED_UNITS:
        err(f"Invalid units: '{units}'. Use: imperial, metric, or standard")

    days = int(flags.get("--days", 7))
    hours = int(flags.get("--hours", 12))
    return cmd, city, units, days, hours


def main():
    if not API_KEY:
        err(
            "OPENWEATHER_API_KEY is not set.\n"
            "Get a key at https://openweathermap.org/api\n"
            "Then set it in your OpenClaw skill config or as an environment variable."
        )

    cmd, city, units, days, hours = parse_args()

    if cmd == "current":
        cmd_current(city, units)
    elif cmd == "forecast":
        cmd_forecast(city, units, days)
    elif cmd == "hourly":
        cmd_hourly(city, units, hours)
    else:
        err(f"Unknown command: '{cmd}'. Valid commands: current, forecast, hourly")


if __name__ == "__main__":
    main()
