#!/usr/bin/env python3
"""UK Prayer Times - Simple & Fast"""

import urllib.request
import json
import sys
from urllib.parse import quote


def get_auto_location():
    """Auto-detect from IP"""
    try:
        url = "https://ipapi.co/json/"
        req = urllib.request.Request(url, headers={'User-Agent': 'UKPrayerTimes/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read())
        return data['city'], data['latitude'], data['longitude']
    except:
        return None, None, None


def geocode_location(location):
    """Find any UK location"""
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={quote(location)},UK&format=json&limit=1"
        req = urllib.request.Request(url, headers={'User-Agent': 'UKPrayerTimes/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read())

        if data:
            name = data[0]['display_name'].split(',')[0]
            return name, float(data[0]['lat']), float(data[0]['lon'])
    except:
        pass
    return None, None, None


def get_prayer_times(lat, lon):
    """Fetch prayer times"""
    try:
        url = f"https://api.aladhan.com/v1/timings?latitude={lat}&longitude={lon}&method=2"
        req = urllib.request.Request(url, headers={'User-Agent': 'UKPrayerTimes/1.0'})
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
        city, lat, lon = geocode_location(location_input)
        if not city:
            print(f"❌ Could not find '{location_input}'")
            print("💡 Try: Birmingham, London, Woolwich, Leicester, etc.")
            return
    else:
        print("📍 Auto-detecting location...")
        city, lat, lon = get_auto_location()
        if not city:
            print("❌ Could not detect location")
            print("💡 Try: python uk_prayer_times.py Birmingham")
            return

    # Get prayer times
    print(f"⏰ Fetching prayer times for {city}...\n")
    timings, date = get_prayer_times(lat, lon)

    if not timings:
        print("❌ Could not fetch prayer times")
        return

    # Display
    print("=" * 50)
    print(f"🕌 PRAYER TIMES - {city.upper()}")
    print(f"📅 {date}")
    print("=" * 50)
    print(f"\nFajr:    {format_12h(timings['Fajr'])}")
    print(f"Sunrise: {format_12h(timings['Sunrise'])}")
    print(f"Dhuhr:   {format_12h(timings['Dhuhr'])}")
    print(f"Asr:     {format_12h(timings['Asr'])}")
    print(f"Maghrib: {format_12h(timings['Maghrib'])}")
    print(f"Isha:    {format_12h(timings['Isha'])}")
    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()