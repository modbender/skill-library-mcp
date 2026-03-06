#!/usr/bin/env python3
"""
Fetch today's prayer times for Rabat, Morocco
Using AlAdhan API (https://aladhan.com/prayer-times-api)
Endpoint: GET /timings/{date}
"""
import requests
import json
from datetime import datetime, timedelta

MOROCCO_UTC_OFFSET = 1

def get_morocco_time():
    """Get current time in Morocco (GMT+1)"""
    utc_now = datetime.utcnow()
    return utc_now + timedelta(hours=MOROCCO_UTC_OFFSET)

def fetch_prayer_times_aladhan(city=None, country=None, latitude=None, longitude=None):
    """
    Fetch from AlAdhan API
    API docs: https://aladhan.com/prayer-times-api#get-/timings/-date-
    
    Args:
        city: City name
        country: Country name
        latitude: Latitude coordinate
        longitude: Longitude coordinate
    """
    try:
        local_time = get_morocco_time()
        date_str = local_time.strftime('%d-%m-%Y')
        
        # Determine method based on country
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
        
        method = method_map.get(country, 2)  # Default to Muslim World League
        
        # AlAdhan API endpoint
        if latitude and longitude:
            url = f"https://api.aladhan.com/v1/timings/{date_str}"
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "method": method
            }
            location = f"Lat: {latitude}, Lon: {longitude}"
        elif city and country:
            url = f"https://api.aladhan.com/v1/timingsByCity/{date_str}"
            params = {
                "city": city,
                "country": country,
                "method": method
            }
            location = f"{city}, {country}"
        else:
            print("❌ Must provide either city/country or coordinates")
            return None
        
        print(f"🔄 Calling: {url}")
        print(f"   Location: {location}")
        print(f"   Method: {method}")
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('code') == 200:
            timings = data['data']['timings']
            date_info = data['data']['date']
            
            return {
                "source": "api.aladhan.com",
                "location": location,
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
            print(f"❌ API returned code: {data.get('code')}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ AlAdhan API timeout (10s)")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"❌ AlAdhan API connection error: {e}")
        return None
    except Exception as e:
        print(f"❌ AlAdhan API error: {e}")
        return None

def get_today_prayer_times(city="Rabat", country="Morocco", latitude=None, longitude=None):
    """
    Fetch today's prayer times using AlAdhan API
    
    Args:
        city: City name (default: Rabat)
        country: Country name (default: Morocco)
        latitude: Optional latitude coordinate
        longitude: Optional longitude coordinate
    """
    print("=" * 60)
    if latitude and longitude:
        print(f"Fetching today's prayer times for coordinates: {latitude}, {longitude}")
    else:
        print(f"Fetching today's prayer times for {city}, {country}")
    
    local_time = get_morocco_time()
    print(f"Current time: {local_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    # Try AlAdhan API
    print("🔄 Fetching from AlAdhan API...")
    result = fetch_prayer_times_aladhan(city, country, latitude, longitude)
    
    if result:
        print(f"✅ Success with {result['source']}")
        return result
    
    print()
    print("❌ Failed to fetch prayer times - check network connectivity")
    print("💡 Tip: You may need Cloudflare WARP VPN if running on a VPS")
    return None

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Fetch today\'s Islamic prayer times')
    parser.add_argument('--city', help='City name (e.g., Rabat)')
    parser.add_argument('--country', help='Country name (e.g., Morocco)')
    parser.add_argument('--lat', type=float, help='Latitude')
    parser.add_argument('--lon', type=float, help='Longitude')
    parser.add_argument('--output', default='today_prayer_times.json', help='Output JSON file')
    
    args = parser.parse_args()
    
    # Validate input
    if not (args.city and args.country) and not (args.lat and args.lon):
        print("❌ Error: Must provide either --city and --country, or --lat and --lon")
        print("\nExamples:")
        print("  python3 fetch_prayer_times.py --city Rabat --country Morocco")
        print("  python3 fetch_prayer_times.py --lat 34.0209 --lon -6.8416")
        exit(1)
    
    # Fetch prayer times
    times = get_today_prayer_times(
        city=args.city,
        country=args.country,
        latitude=args.lat,
        longitude=args.lon
    )
    
    if times:
        print()
        print("=" * 60)
        print("📅 TODAY'S PRAYER TIMES")
        print("=" * 60)
        print(f"📍 Location: {times.get('location', 'N/A')}")
        print(f"📡 Source: {times['source']}")
        print(f"📆 Date: {times.get('date', 'N/A')}")
        if 'hijri' in times:
            print(f"🌙 Hijri: {times['hijri']}")
        if 'method' in times:
            print(f"🔢 Method: {times['method']}")
        print()
        
        for prayer, time in times['prayers'].items():
            emoji = "🌅" if prayer == "Sunrise" else "🕌"
            print(f"{emoji} {prayer:8s} {time}")
        
        print("=" * 60)
        
        # Save for use by check script
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(times, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Saved to {args.output}")
    
    else:
        exit(1)
