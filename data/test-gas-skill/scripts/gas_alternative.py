#!/usr/bin/env python3
"""
Alternative gas price search using free APIs and public data sources.
Usage: python3 gas_alternative.py --city "Columbus" --state "OH" --radius 20 --output results.json
"""

import argparse
import json
import math
import sys
from datetime import datetime, timezone

try:
    import requests
    from geopy.geocoders import Nominatim
    from geopy.distance import geodesic
except ImportError:
    print("Error: Install required packages: pip install requests geopy")
    sys.exit(1)

# Coordinates for downtown Columbus, OH
DOWNTOWN_COLUMBUS = (39.9612, -82.9988)

def get_distance(lat, lon, reference=DOWNTOWN_COLUMBUS):
    """Calculate distance from reference point in miles."""
    station_coords = (lat, lon)
    return geodesic(reference, station_coords).miles

def search_costco_locations(lat, lon, radius):
    """
    Search for Costco gas stations (Costco typically has cheap gas).

    Costco locations are available via various APIs, but for this example,
    we'll use a known list of Columbus area Costco locations.
    """
    # Known Costco locations in Columbus, OH area
    costco_stations = [
        {
            'name': 'Costco Gas',
            'address': '5000 Morse Rd, Columbus, OH 43213',
            'lat': 39.9667,
            'lon': -82.8500
        },
        {
            'name': 'Costco Gas',
            'address': '1350 Hilliard Rome Rd, Columbus, OH 43228',
            'lat': 39.9400,
            'lon': -83.1500
        },
        {
            'name': 'Costco Gas',
            'address': '8570 S Old State Rd, Lewis Center, OH 43035',
            'lat': 40.1800,
            'lon': -83.0000
        }
    ]

    # Filter by radius
    nearby = []
    for station in costco_stations:
        distance = geodesic((lat, lon), (station['lat'], station['lon'])).miles
        if distance <= radius:
            station['distance'] = distance
            nearby.append(station)

    return nearby

def search_gas_stations(lat, lon, radius, fuel_type='87'):
    """
    Search for gas stations using various free APIs.

    This uses the OpenStreetMap/Overpass API to find gas stations.
    """
    # Overpass API query for gas stations
    overpass_url = "http://overpass-api.de/api/interpreter"

    # Calculate bounding box
    # Approximate: 1 degree ≈ 69 miles
    delta_lat = radius / 69
    delta_lon = radius / (69 * math.cos(math.radians(lat)))

    bbox = f"{lat-delta_lat},{lon-delta_lon},{lat+delta_lat},{lon+delta_lon}"

    query = f"""
    [out:json][timeout:25];
    (
      node["amenity"="fuel"]({bbox});
      way["amenity"="fuel"]({bbox});
      relation["amenity"="fuel"]({bbox});
    );
    out body center;
    """

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.post(overpass_url, data=query, headers=headers, timeout=30)
        response.raise_for_status()

        data = response.json()

        stations = []
        for element in data.get('elements', []):
            if 'lat' in element and 'lon' in element:
                tags = element.get('tags', {})

                # Calculate distance from downtown
                distance = get_distance(element['lat'], element['lon'])

                if distance <= radius:
                    station = {
                        'source': 'osm',
                        'name': tags.get('name', tags.get('brand', 'Unknown Station')),
                        'brand': tags.get('brand', 'Unknown'),
                        'address': tags.get('addr:full', ''),
                        'lat': element['lat'],
                        'lon': element['lon'],
                        'distance': round(distance, 2),
                        'fuel_type': fuel_type,
                        'price': 0,  # OSM doesn't have real-time prices
                        'price_text': 'N/A',
                        'scraped_at': datetime.now(timezone.utc).isoformat()
                    }
                    stations.append(station)

        print(f"Found {len(stations)} gas stations within {radius} miles")
        return stations

    except Exception as e:
        print(f"Error searching gas stations: {e}")
        return []

def estimate_costco_prices(stations, base_price=2.89):
    """
    Estimate Costco gas prices (typically $0.10-0.30 below average).

    In real usage, this would fetch actual prices from GasBuddy or similar.
    """
    for station in stations:
        if 'costco' in station['name'].lower():
            # Costco typically $0.15-0.25 below market average
            discount = 0.20
            estimated_price = round(base_price - discount, 2)
            station['price'] = estimated_price
            station['price_text'] = f"${estimated_price:.2f} (est.)"
            station['is_costco'] = True
        else:
            station['is_costco'] = False

    return stations

def generate_summary(stations, fuel_type='87'):
    """Generate a summary of gas prices."""
    if not stations:
        return "No gas stations found."

    # Sort by distance
    by_distance = sorted(stations, key=lambda x: x.get('distance', float('inf')))

    # Find Costco stations (typically cheapest)
    costco_stations = [s for s in stations if s.get('is_costco', False)]

    # Find stations with prices
    stations_with_prices = [s for s in stations if s.get('price', 0) > 0]
    by_price = sorted(stations_with_prices, key=lambda x: x.get('price', float('inf')))

    summary = f"⛽ Gas Prices ({fuel_type} Octane) - Columbus, OH"

    # Show cheapest available prices (Costco + others with prices)
    if by_price:
        summary += f"\n\n💰 **Best Prices Available** ({len(by_price)} with prices)\n"
        for station in by_price[:5]:
            summary += f"• {station['name']} ({station.get('brand', 'N/A')})\n"
            summary += f"  💰 {station.get('price_text', 'Check site')}\n"
            summary += f"  📍 {station['address']} ({station.get('distance', 0):.1f} miles)\n"
            if station.get('is_costco'):
                summary += f"  ⭐ Costco!\n"
            summary += "\n"
    elif costco_stations:
        # No prices except Costco estimates
        summary += f"\n\n💰 **Estimated Prices**\n"
        for station in costco_stations[:3]:
            summary += f"• {station['name']}\n"
            summary += f"  💰 {station.get('price_text', 'Check site')}\n"
            summary += f"  📍 {station['address']} ({station.get('distance', 0):.1f} miles)\n\n"

    # Show nearest stations
    summary += f"\n📍 **Nearest Stations** (Top 10 by distance)\n"
    for i, station in enumerate(by_distance[:10], 1):
        summary += f"{i}. {station['name']} ({station.get('brand', 'N/A')})\n"
        summary += f"   📍 {station['address'] or 'Address unknown'} ({station.get('distance', 0):.1f} miles)\n"
        summary += f"   💰 {station.get('price_text', 'Check for price')}\n"
        if station.get('is_costco'):
            summary += f"   ⭐ Costco!\n"
        summary += "\n"

    summary += f"... and {len(by_distance) - 10} more stations within 20 miles\n"

    summary += "\n💡 **Tips:**\n"
    summary += "• Costco typically has gas $0.15-0.25 below market average\n"
    summary += "• For exact prices, check GasBuddy.com or station's app\n"
    summary += f"• Total stations found: {len(by_distance)}"

    return summary

def save_stations(stations, output_file):
    """Save stations to JSON file."""
    with open(output_file, 'w') as f:
        json.dump(stations, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(stations)} stations to {output_file}")

def geocode_zip(zip_code, city='Columbus', state='OH'):
    """Geocode ZIP code to lat/lon."""
    try:
        from geopy.geocoders import Nominatim
        geolocator = Nominatim(user_agent='openclaw-gasfinder')
        location = geolocator.geocode(f'{zip_code}, {city}, {state}', timeout=10)
        if location:
            return location.latitude, location.longitude
        else:
            print(f"Warning: Could not geocode ZIP {zip_code}. Using default location.")
            return 39.9612, -82.9988
    except Exception as e:
        print(f"Warning: Geocoding error: {e}. Using default location.")
        return 39.9612, -82.9988

def main():
    parser = argparse.ArgumentParser(description='Search gas prices using alternative methods')
    parser.add_argument('--city', type=str, default='Columbus', help='City name')
    parser.add_argument('--state', type=str, default='OH', help='State abbreviation')
    parser.add_argument('--zip', type=str, help='ZIP code (overrides lat/lon)')
    parser.add_argument('--lat', type=float, default=39.9612, help='Latitude (default: Columbus, OH)')
    parser.add_argument('--lon', type=float, default=-82.9988, help='Longitude (default: Columbus, OH)')
    parser.add_argument('--radius', type=float, default=20, help='Search radius in miles (default: 20)')
    parser.add_argument('--fuel', type=str, default='87', help='Fuel type (default: 87)')
    parser.add_argument('--base-price', type=float, default=2.89, help='Base price for estimation (default: 2.89)')
    parser.add_argument('--output', default='gas_prices.json', help='Output file')
    parser.add_argument('--summary', action='store_true', help='Print summary to stdout')

    args = parser.parse_args()

    # Geocode ZIP if provided
    if args.zip:
        print(f"Geocoding ZIP {args.zip}...")
        lat, lon = geocode_zip(args.zip, args.city, args.state)
        print(f"ZIP {args.zip} -> {lat}, {lon}")
    else:
        lat, lon = args.lat, args.lon

    print(f"Searching for gas stations near {lat}, {lon} (radius: {args.radius} miles)")

    # Search for all stations
    stations = search_gas_stations(lat, lon, args.radius, args.fuel)

    # Search for Costco specifically
    costco_stations = search_costco_locations(lat, lon, args.radius)

    # Add Costco to main list
    costco_with_prices = estimate_costco_prices(costco_stations, args.base_price)
    stations.extend(costco_with_prices)

    # Remove duplicates (by location - lat/lon within 0.0001 degrees)
    seen_locations = set()
    unique_stations = []
    for station in stations:
        lat = station.get('lat', 0)
        lon = station.get('lon', 0)
        # Round coordinates to avoid near-duplicates
        loc_key = (round(lat, 4), round(lon, 4))
        if loc_key not in seen_locations:
            seen_locations.add(loc_key)
            unique_stations.append(station)

    save_stations(unique_stations, args.output)

    # Generate and print summary
    if args.summary:
        summary = generate_summary(unique_stations, args.fuel)
        print("\n" + summary)

if __name__ == '__main__':
    main()
