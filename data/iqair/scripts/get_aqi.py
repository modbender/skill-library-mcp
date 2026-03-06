#!/usr/bin/env python3
"""
Fetch air quality data from IQAir API and format it nicely.

Usage:
    python get_aqi.py Riga Latvia
    python get_aqi.py --lat 56.9496 --lon 24.1052
    python get_aqi.py --nearest

Requires IQAIR_API_KEY environment variable.
"""

import os
import sys
import json
import urllib.request
import urllib.parse
import urllib.error


def get_emoji_and_level(aqi):
    """Convert AQI value to emoji and level description."""
    if aqi <= 50:
        return "🟢", "Good"
    elif aqi <= 100:
        return "🟡", "Moderate"
    elif aqi <= 150:
        return "🟠", "Unhealthy for Sensitive Groups"
    elif aqi <= 200:
        return "🔴", "Unhealthy"
    elif aqi <= 300:
        return "🟣", "Very Unhealthy"
    else:
        return "🟤", "Hazardous"


def fetch_aqi(endpoint, params):
    """Fetch data from IQAir API."""
    api_key = os.getenv("IQAIR_API_KEY")
    if not api_key:
        print("Error: IQAIR_API_KEY environment variable not set", file=sys.stderr)
        print("Get your free key from: https://dashboard.iqair.com/personal/api-keys", file=sys.stderr)
        sys.exit(1)
    
    params["key"] = api_key
    url = f"https://api.airvisual.com/v2/{endpoint}?{urllib.parse.urlencode(params)}"
    
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            
            if data.get("status") != "success":
                print(f"Error: {data.get('data', {}).get('message', 'Unknown error')}", file=sys.stderr)
                sys.exit(1)
            
            return data["data"]
    
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("Error: Invalid API key", file=sys.stderr)
        elif e.code == 404:
            print("Error: Location not found", file=sys.stderr)
        elif e.code == 429:
            print("Error: Rate limit exceeded", file=sys.stderr)
        else:
            print(f"Error: HTTP {e.code} - {e.reason}", file=sys.stderr)
        sys.exit(1)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def format_output(data):
    """Format air quality data into a readable string."""
    city = data.get("city", "Unknown")
    state = data.get("state", "")
    country = data.get("country", "")
    
    pollution = data.get("current", {}).get("pollution", {})
    aqi = pollution.get("aqius", 0)
    
    emoji, level = get_emoji_and_level(aqi)
    
    location = f"{city}"
    if state and state != city:
        location += f", {state}"
    if country:
        location += f", {country}"
    
    return f"{emoji} {aqi} - {level}\n{location}"


def main():
    args = sys.argv[1:]
    
    if not args or args[0] in ["-h", "--help"]:
        print(__doc__)
        sys.exit(0)
    
    # Check for coordinate-based query
    if "--lat" in args and "--lon" in args:
        lat_idx = args.index("--lat")
        lon_idx = args.index("--lon")
        
        if lat_idx + 1 >= len(args) or lon_idx + 1 >= len(args):
            print("Error: --lat and --lon require values", file=sys.stderr)
            sys.exit(1)
        
        lat = args[lat_idx + 1]
        lon = args[lon_idx + 1]
        
        data = fetch_aqi("nearest_city", {"lat": lat, "lon": lon})
        print(format_output(data))
        return
    
    # Check for nearest city query
    if args[0] == "--nearest":
        data = fetch_aqi("nearest_city", {})
        print(format_output(data))
        return
    
    # City-based query
    if len(args) < 2:
        print("Error: Provide city and country (and optionally state)", file=sys.stderr)
        print("Usage: python get_aqi.py <city> <country> [state]", file=sys.stderr)
        sys.exit(1)
    
    city = args[0]
    country = args[1]
    state = args[2] if len(args) > 2 else city  # Default state to city name
    
    data = fetch_aqi("city", {"city": city, "state": state, "country": country})
    print(format_output(data))


if __name__ == "__main__":
    main()
