#!/usr/bin/env python3
"""
Yr.no Tomorrow's Weather CLI.
Usage: python3 tomorrow.py <lat> <lon>
"""

import sys
import argparse
from datetime import datetime, timedelta
from yr_service import get_location_forecast
from utils import get_emoji, format_symbol

def format_tomorrow(data, lat, lon):
    """Format tomorrow's forecast by time of day."""
    properties = data["properties"]
    timeseries = properties["timeseries"]

    now = datetime.now()
    tomorrow = now + timedelta(days=1)
    tomorrow_date = tomorrow.strftime("%Y-%m-%d")
    tomorrow_display = tomorrow.strftime("%A, %d %B")

    tomorrow_entries = [entry for entry in timeseries if tomorrow_date in entry["time"]]

    if not tomorrow_entries:
        print(f"No data for tomorrow ({tomorrow_display})")
        sys.exit(1)

    print(f"🌤️ Tomorrow's Weather - {tomorrow_display}")
    print(f"📍 {lat:.4f}, {lon:.4f}")
    print('-' * 50)

    times_of_day = {"morning": [], "afternoon": [], "evening": [], "night": []}

    for entry in tomorrow_entries:
        time_str = entry["time"]
        try:
            time_obj = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
            hour = time_obj.hour
        except:
            continue

        data_entry = entry["data"]
        instant = data_entry["instant"]["details"]
        next_1h = data_entry.get("next_1_hours", {})
        symbol = next_1h.get("summary", {}).get("symbol_code", "cloudy")

        entry_data = {
            "hour": hour,
            "temp": instant.get("air_temperature"),
            "wind": instant.get("wind_speed"),
            "symbol": symbol
        }
        if 6 <= hour < 12:
            times_of_day["morning"].append(entry_data)
        elif 12 <= hour < 18:
            times_of_day["afternoon"].append(entry_data)
        elif 18 <= hour < 24:
            times_of_day["evening"].append(entry_data)
        else:
            times_of_day["night"].append(entry_data)

    for period, entries in times_of_day.items():
        if entries:
            mid = len(entries) // 2
            mid_entry = entries[mid]
            emoji = get_emoji(mid_entry["symbol"])
            temp = mid_entry["temp"]
            wind = mid_entry["wind"]
            print(f"\n🕐 {period.capitalize()}: {emoji} {format_symbol(mid_entry['symbol'])}")
            print(f"   {temp}°C, {wind} m/s")

    all_temps = [e["temp"] for e in tomorrow_entries if e["temp"] is not None]
    if all_temps:
        print(f"\n📊 Range: {min(all_temps):.1f}°C - {max(all_temps):.1f}°C")

def main():
    parser = argparse.ArgumentParser(description="Tomorrow's weather from Yr.no")
    parser.add_argument("lat", type=float)
    parser.add_argument("lon", type=float)
    args = parser.parse_args()

    try:
        data = get_location_forecast(args.lat, args.lon)
        format_tomorrow(data, args.lat, args.lon)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
