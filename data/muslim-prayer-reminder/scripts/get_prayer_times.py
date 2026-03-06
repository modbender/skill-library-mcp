#!/usr/bin/env python3
"""
Get prayer times for any location using AlAdhan API
Supports multiple calculation methods for different regions
"""
import requests
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

def get_prayer_times(city=None, country=None, latitude=None, longitude=None, method=None, date=None):
    """
    Fetch prayer times from AlAdhan API
    
    Args:
        city: City name (e.g., "Rabat")
        country: Country name (e.g., "Morocco")
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        method: Calculation method ID (defaults based on location)
        date: Date string in DD-MM-YYYY format (defaults to today)
    
    Returns:
        dict with prayer times or None if failed
    """
    
    # Default method selection based on country
    method_map = {
        "Morocco": 21,
        "Saudi Arabia": 4,
        "Egypt": 5,
        "Turkey": 13,
        "Jordan": 24,
        "Algeria": 19,
        "Tunisia": 18,
        "UAE": 16,
        "Kuwait": 9,
        "Qatar": 10,
    }
    
    if method is None and country in method_map:
        method = method_map[country]
    elif method is None:
        method = 2  # Default to Muslim World League
    
    # Get date
    if date is None:
        date = datetime.now().strftime('%d-%m-%Y')
    
    try:
        # Use city/country or coordinates
        if city and country:
            url = f"https://api.aladhan.com/v1/timingsByCity/{date}"
            params = {
                "city": city,
                "country": country,
                "method": method
            }
        elif latitude and longitude:
            url = f"https://api.aladhan.com/v1/timings/{date}"
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "method": method
            }
        else:
            print("Error: Must provide either city/country or coordinates", file=sys.stderr)
            return None
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('code') == 200:
            timings = data['data']['timings']
            date_info = data['data']['date']
            
            return {
                "source": "api.aladhan.com",
                "location": f"{city}, {country}" if city else f"Lat: {latitude}, Lon: {longitude}",
                "date": date_info['readable'],
                "hijri": date_info['hijri']['date'],
                "gregorian": date_info['gregorian']['date'],
                "method": method,
                "prayers": {
                    "Fajr": timings['Fajr'],
                    "Sunrise": timings['Sunrise'],
                    "Dhuhr": timings['Dhuhr'],
                    "Asr": timings['Asr'],
                    "Maghrib": timings['Maghrib'],
                    "Isha": timings['Isha']
                }
            }
        else:
            print(f"API error: {data.get('code')}", file=sys.stderr)
            return None
            
    except requests.exceptions.Timeout:
        print("Error: API request timed out", file=sys.stderr)
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"Error: Connection failed - {e}", file=sys.stderr)
        print("Tip: Check if api.aladhan.com is reachable or if VPN is needed", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return None

def get_next_prayer(prayers_data, timezone_offset=0):
    """
    Find the next prayer time
    
    Args:
        prayers_data: Dict with 'prayers' key containing prayer times
        timezone_offset: Hours offset from UTC (e.g., +1 for Morocco)
    
    Returns:
        dict with next prayer info or None if all prayers passed
    """
    utc_now = datetime.utcnow()
    local_now = utc_now + timedelta(hours=timezone_offset)
    
    prayers = prayers_data['prayers']
    prayer_order = ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']
    
    for prayer_name in prayer_order:
        if prayer_name in prayers:
            time_str = prayers[prayer_name]
            hour, minute = map(int, time_str.split(':'))
            prayer_time = local_now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            diff_minutes = (prayer_time - local_now).total_seconds() / 60
            
            if diff_minutes > 0:
                hours = int(diff_minutes // 60)
                minutes = int(diff_minutes % 60)
                
                return {
                    "name": prayer_name,
                    "time": time_str,
                    "hours_until": hours,
                    "minutes_until": minutes,
                    "total_minutes": int(diff_minutes)
                }
    
    # All prayers passed, return tomorrow's Fajr
    return {
        "name": "Fajr",
        "time": prayers.get('Fajr', 'N/A'),
        "tomorrow": True
    }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Get Islamic prayer times')
    parser.add_argument('--city', help='City name')
    parser.add_argument('--country', help='Country name')
    parser.add_argument('--lat', type=float, help='Latitude')
    parser.add_argument('--lon', type=float, help='Longitude')
    parser.add_argument('--method', type=int, help='Calculation method ID (1-24)')
    parser.add_argument('--date', help='Date in DD-MM-YYYY format')
    parser.add_argument('--timezone', type=int, default=0, help='Timezone offset from UTC')
    parser.add_argument('--next', action='store_true', help='Show next prayer time')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    # Get prayer times
    result = get_prayer_times(
        city=args.city,
        country=args.country,
        latitude=args.lat,
        longitude=args.lon,
        method=args.method,
        date=args.date
    )
    
    if not result:
        sys.exit(1)
    
    # Output format
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"📍 {result['location']}")
        print(f"📆 {result['date']}")
        print(f"🌙 {result['hijri']}")
        print(f"🔢 Method: {result['method']}")
        print()
        for prayer, time in result['prayers'].items():
            emoji = "🌅" if prayer == "Sunrise" else "🕌"
            print(f"{emoji} {prayer:8s} {time}")
        
        if args.next:
            next_info = get_next_prayer(result, args.timezone)
            print()
            if next_info.get('tomorrow'):
                print(f"⏳ All prayers passed. Next: Fajr tomorrow at {next_info['time']}")
            else:
                if next_info['hours_until'] > 0:
                    print(f"⏳ Next: {next_info['name']} at {next_info['time']} (in {next_info['hours_until']}h {next_info['minutes_until']}m)")
                else:
                    print(f"⏳ Next: {next_info['name']} at {next_info['time']} (in {next_info['minutes_until']} minutes)")
