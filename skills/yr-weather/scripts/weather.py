#!/usr/bin/env python3
"""
Yr.no Weather CLI - Current weather and short-term forecast.
Usage: python3 weather.py <lat> <lon> [altitude]
"""

import sys
import argparse
from datetime import datetime
from yr_service import get_location_forecast
from utils import get_emoji, format_symbol

def format_weather(data):
    """Format weather data into human-readable output."""
    properties = data["properties"]
    timeseries = properties["timeseries"]
    meta = properties.get("meta", {})

    if not timeseries:
        print("No weather data available")
        sys.exit(1)

    print("🌤️ Weather Forecast for MET Norway")
    print(f"Updated: {meta.get('updated_at', 'N/A')}")
    print('-' * 50)

    # Current conditions
    current = timeseries[0]
    current_data = current["data"]
    current_instant = current_data["instant"]["details"]

    temp = current_instant.get("air_temperature", "N/A")
    wind = current_instant.get("wind_speed", "N/A")
    humidity = current_instant.get("relative_humidity", "N/A")

    print("\n📍 Current Conditions:")
    print(f"   Temperature: {temp}°C")
    print(f"   Wind: {wind} m/s")
    print(f"   Humidity: {humidity}%")

    next_1h = current_data.get("next_1_hours", {})
    symbol = next_1h.get("summary", {}).get("symbol_code", "unknown")
    print(f"   Conditions: {get_emoji(symbol)} {format_symbol(symbol)}")

    # Next few hours
    print("\n📅 Next 12 Hours:")

    shown = 0
    for entry in timeseries[1:]:
        if shown >= 6:
            break

        time_str = entry["time"]
        try:
            time_obj = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
            time_display = time_obj.strftime("%H:%M")
        except:
            time_display = time_str[:16].replace("T", " ")

        data = entry["data"]
        instant = data["instant"]["details"]

        next_1h_entry = data.get("next_1_hours", {})
        symbol_entry = next_1h_entry.get("summary", {}).get("symbol_code", "unknown")

        temp_val = instant.get("air_temperature", "N/A")
        wind_val = instant.get("wind_speed", "N/A")

        print(f"   {time_display}: {get_emoji(symbol_entry)} {temp_val}°C, {wind_val} m/s")
        shown += 1

def main():
    parser = argparse.ArgumentParser(description="Get current weather and forecast from Yr.no")
    parser.add_argument("lat", type=float, help="Latitude")
    parser.add_argument("lon", type=float, help="Longitude")
    parser.add_argument("altitude", type=str, nargs='?', default=None, help="Altitude (e.g., '100' or '100m')")
    args = parser.parse_args()

    try:
        data = get_location_forecast(args.lat, args.lon, args.altitude)
        format_weather(data)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
