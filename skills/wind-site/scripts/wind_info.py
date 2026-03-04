#!/usr/bin/env python3
"""
Get current or recent wind conditions at a location (speed and direction).
Uses Open-Meteo API (no API key required).
"""
import argparse
import sys
from datetime import datetime, timedelta

try:
    import requests
except ImportError:
    print("Error: requests is required. pip install requests", file=sys.stderr)
    sys.exit(1)


def fetch_wind(lat: float, lon: float, days_back: int = 0):
    """Fetch wind from Open-Meteo. If days_back=0, use forecast; else use archive."""
    if days_back > 0:
        end = datetime.utcnow()
        start = end - timedelta(days=days_back)
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start.strftime("%Y-%m-%d"),
            "end_date": end.strftime("%Y-%m-%d"),
            "hourly": "wind_speed_10m,wind_direction_10m",
            "timezone": "UTC",
        }
    else:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "wind_speed_10m,wind_direction_10m",
            "timezone": "UTC",
            "forecast_days": 1,
        }
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    return r.json()


def main():
    parser = argparse.ArgumentParser(description="Get wind speed and direction at a location.")
    parser.add_argument("--lat", type=float, required=True, help="Latitude")
    parser.add_argument("--lon", type=float, required=True, help="Longitude")
    parser.add_argument("--days", type=int, default=0, help="0=current (forecast); >0=last N days (archive)")
    args = parser.parse_args()
    try:
        data = fetch_wind(args.lat, args.lon, args.days)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    h = data.get("hourly", {})
    times = h.get("time", [])
    speeds = h.get("wind_speed_10m", [])
    dirs = h.get("wind_direction_10m", [])
    if not times:
        print("No wind data returned.")
        return 0
    # Latest
    print(f"Location: {args.lat}, {args.lon}")
    print(f"Latest: {times[-1]} UTC  |  Wind speed: {speeds[-1]} m/s  |  Direction: {dirs[-1]}°")
    if len(speeds) > 1:
        avg_speed = sum(speeds) / len(speeds)
        print(f"Period mean speed: {avg_speed:.2f} m/s")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
