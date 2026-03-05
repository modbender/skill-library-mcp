#!/usr/bin/env python3
"""
Search for gas prices using GasBuddy.
Usage: python3 gasbuddy_search.py --fuel "87" --lat 39.9612 --lon -82.9988 --radius 20 --output results.json
"""

import argparse
import json
import sys
from datetime import datetime

try:
    import requests
except ImportError:
    print("Error: Install required packages: pip install requests")
    sys.exit(1)

# GasBuddy API endpoints
GASBUDDY_API_BASE = "https://www.gasbuddy.com/graphql"

def search_stations(lat, lon, radius, fuel_type, api_key=None):
    """
    Search for gas stations near coordinates using GasBuddy.

    Note: GasBuddy's API requires authentication for full access.
    This script uses a workaround by scraping the public web interface.

    Parameters:
    - lat: Latitude (e.g., 39.9612 for Columbus, OH)
    - lon: Longitude (e.g., -82.9988 for Columbus, OH)
    - radius: Search radius in miles
    - fuel_type: Fuel type (87, 89, 91, diesel)
    - api_key: Optional GasBuddy API key if you have one

    Returns:
    - List of stations with prices
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'Content-Type': 'application/json',
        'Origin': 'https://www.gasbuddy.com',
        'Referer': 'https://www.gasbuddy.com/',
    }

    # Try using the public web API first
    try:
        # Search by location
        search_url = f"https://www.gasbuddy.com/home?search={lat}%2C{lon}&fuel={fuel_type}"

        response = requests.get(search_url, headers=headers, timeout=10)
        print(f"GasBuddy search status: {response.status_code}")

        if response.status_code == 200:
            # Parse HTML response (GasBuddy renders via client-side JS)
            # For now, we'll return a placeholder
            print("Note: GasBuddy requires JavaScript rendering. Consider using:")
            print("  - GasBuddy API (commercial access)")
            print("  - Playwright/Puppeteer for JS rendering")
            print("  - Alternative data sources")

        return scrape_with_playwright(lat, lon, radius, fuel_type)

    except Exception as e:
        print(f"Error searching GasBuddy: {e}")
        return []

def scrape_with_playwright(lat, lon, radius, fuel_type):
    """
    Alternative: Use Playwright for JavaScript rendering.

    This requires: pip install playwright && playwright install
    """
    try:
        from playwright.sync_api import sync_playwright

        stations = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Navigate to GasBuddy search
            url = f"https://www.gasbuddy.com/home?search={lat}%2C{lon}&fuel={fuel_type}"
            page.goto(url, wait_until="networkidle")

            # Wait for results to load
            page.wait_for_selector('[data-testid="station-row"]', timeout=10000)

            # Extract station data
            rows = page.query_selector_all('[data-testid="station-row"]')

            for row in rows:
                try:
                    station = parse_station_row(row, fuel_type)
                    if station:
                        stations.append(station)
                except Exception as e:
                    print(f"Error parsing station: {e}")
                    continue

            browser.close()

        return stations

    except ImportError:
        print("Playwright not installed. Install with: pip install playwright && playwright install")
        return []
    except Exception as e:
        print(f"Error with Playwright scraping: {e}")
        return []

def parse_station_row(row, fuel_type):
    """Parse a station row from GasBuddy."""
    try:
        # Extract station name
        name_elem = row.query_selector('[data-testid="station-name"]')
        name = name_elem.text_content(strip=True) if name_elem else "Unknown"

        # Extract address
        address_elem = row.query_selector('[data-testid="station-address"]')
        address = address_elem.text_content(strip=True) if address_elem else ""

        # Extract price
        price_elem = row.query_selector(f'[data-testid="fuel-price-{fuel_type}"]')
        price_text = price_elem.text_content(strip=True) if price_elem else ""

        # Parse price (e.g., "$2.89" -> 2.89)
        price = 0
        if price_text:
            try:
                price = float(price_text.replace('$', '').replace(',', ''))
            except ValueError:
                pass

        return {
            'source': 'gasbuddy',
            'name': name,
            'address': address,
            'price': price,
            'price_text': price_text,
            'fuel_type': fuel_type,
            'scraped_at': datetime.utcnow().isoformat()
        }

    except Exception as e:
        print(f"Error parsing row: {e}")
        return None

def save_stations(stations, output_file):
    """Save stations to JSON file."""
    with open(output_file, 'w') as f:
        json.dump(stations, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(stations)} stations to {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Search gas prices via GasBuddy')
    parser.add_argument('--lat', type=float, default=39.9612, help='Latitude (default: Columbus, OH)')
    parser.add_argument('--lon', type=float, default=-82.9988, help='Longitude (default: Columbus, OH)')
    parser.add_argument('--radius', type=float, default=20, help='Search radius in miles (default: 20)')
    parser.add_argument('--fuel', type=str, default='87', help='Fuel type: 87, 89, 91, diesel (default: 87)')
    parser.add_argument('--api-key', help='GasBuddy API key (optional)')
    parser.add_argument('--output', default='gas_prices.json', help='Output file')

    args = parser.parse_args()

    print(f"Searching for {args.fuel} octane gas near {args.lat}, {args.lon} (radius: {args.radius} miles)")

    stations = search_stations(args.lat, args.lon, args.radius, args.fuel, args.api_key)
    save_stations(stations, args.output)

    # Print top 5 cheapest
    sorted_stations = sorted([s for s in stations if s['price'] > 0], key=lambda x: x['price'])
    print(f"\nTop 5 cheapest {args.fuel} octane:")
    for i, station in enumerate(sorted_stations[:5], 1):
        print(f"{i}. {station['name']}: {station['price_text']} - {station['address']}")

if __name__ == '__main__':
    main()
