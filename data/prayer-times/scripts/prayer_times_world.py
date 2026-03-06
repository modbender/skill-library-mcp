#!/usr/bin/env python3
"""Global Prayer Times - Works Anywhere in the World"""

import urllib.request
import json
import sys
from urllib.parse import quote


def get_auto_location():
    """Auto-detect from IP"""
    try:
        url = "https://ipapi.co/json/"
        req = urllib.request.Request(url, headers={'User-Agent': 'GlobalPrayerTimes/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read())
        city = data.get('city', 'Unknown')
        country = data.get('country_name', '')
        location_name = f"{city}, {country}" if country else city
        return location_name, data['latitude'], data['longitude']
    except:
        return None, None, None


def geocode_location(location):
    """Find any location worldwide"""
    try:
        # Search globally - no country restriction
        url = f"https://nominatim.openstreetmap.org/search?q={quote(location)}&format=json&limit=1"
        req = urllib.request.Request(url, headers={'User-Agent': 'GlobalPrayerTimes/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read())

        if data:
            name = data[0]['display_name']
            return name, float(data[0]['lat']), float(data[0]['lon'])
    except:
        pass
    return None, None, None


def get_prayer_times(lat, lon):
    """Fetch prayer times"""
    try:
        url = f"https://api.aladhan.com/v1/timings?latitude={lat}&longitude={lon}&method=2"
        req = urllib.request.Request(url, headers={'User-Agent': 'GlobalPrayerTimes/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read())
        return data['data']['timings'], data['data']['date']['readable']
    except:
        return None, None


def format_12h(time_24):
    """Convert to 12-hour format"""
    h, m = map(int, time_24.split(':')[:2])
    period = 'AM' if h < 12 else 'PM'
    h = h if h <= 12 else h - 12
    h = 12 if h == 0 else h
    return f"{h:02d}:{m:02d} {period}"


def main():
    # Parse user input
    if len(sys.argv) > 1:
        location_input = ' '.join(sys.argv[1:])
        print(f"🔍 Looking up: {location_input}...")
        location, lat, lon = geocode_location(location_input)
        if not location:
            print(f"❌ Could not find '{location_input}'")
            print("💡 Try: Makkah, Dubai, London, New York, etc.")
            return
    else:
        print("📍 Auto-detecting location...")
        location, lat, lon = get_auto_location()
        if not location:
            print("❌ Could not detect location")
            print("💡 Try: python prayer_times.py [city name]")
            return

    # Get prayer times
    print(f"⏰ Fetching prayer times for {location}...\n")
    timings, date = get_prayer_times(lat, lon)

    if not timings:
        print("❌ Could not fetch prayer times")
        return

    # Display
    print("=" * 60)
    print(f"🕌 PRAYER TIMES - {location.upper()}")
    print(f"📅 {date}")
    print("=" * 60)
    print(f"\nFajr:    {format_12h(timings['Fajr'])}")
    print(f"Sunrise: {format_12h(timings['Sunrise'])}")
    print(f"Dhuhr:   {format_12h(timings['Dhuhr'])}")
    print(f"Asr:     {format_12h(timings['Asr'])}")
    print(f"Maghrib: {format_12h(timings['Maghrib'])}")
    print(f"Isha:    {format_12h(timings['Isha'])}")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
