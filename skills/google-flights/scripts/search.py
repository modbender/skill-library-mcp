#!/usr/bin/env python3
"""
Flight search CLI using fast-flights (Google Flights scraper).
Quick mode: Returns prices and price trends fast.
"""

import argparse
import json
import sys
import warnings
from datetime import datetime, timedelta

# Suppress date parsing warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Add venv to path
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
venv_site = os.path.join(script_dir, '..', '.venv', 'lib')
if os.path.exists(venv_site):
    for d in os.listdir(venv_site):
        if d.startswith('python'):
            sys.path.insert(0, os.path.join(venv_site, d, 'site-packages'))
            break

from fast_flights import FlightData, Passengers, get_flights


def parse_date(date_str: str) -> str:
    """Parse flexible date input to YYYY-MM-DD format."""
    date_str = date_str.lower().strip()
    today = datetime.now()
    
    if date_str == "today":
        return today.strftime("%Y-%m-%d")
    elif date_str == "tomorrow":
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")
    elif date_str.startswith("in ") and "day" in date_str:
        days = int(''.join(filter(str.isdigit, date_str)))
        return (today + timedelta(days=days)).strftime("%Y-%m-%d")
    elif date_str.startswith("next "):
        weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for i, day in enumerate(weekdays):
            if day in date_str:
                days_ahead = i - today.weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        if "week" in date_str:
            return (today + timedelta(days=7)).strftime("%Y-%m-%d")
    
    # Try to parse with year first to avoid ambiguity
    if len(date_str) >= 8 and date_str[4] == '-':
        return date_str  # Already YYYY-MM-DD
    
    for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%B %d, %Y", "%b %d, %Y"]:
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    
    # For formats without year, assume current/next year
    for fmt in ["%m/%d", "%d %b", "%b %d", "%B %d"]:
        try:
            parsed = datetime.strptime(date_str, fmt)
            parsed = parsed.replace(year=today.year)
            if parsed.date() < today.date():
                parsed = parsed.replace(year=today.year + 1)
            return parsed.strftime("%Y-%m-%d")
        except ValueError:
            continue
    
    return date_str


def build_google_flights_url(from_apt: str, to_apt: str, dep_date: str, ret_date: str = None) -> str:
    """Build a direct Google Flights search URL."""
    if ret_date:
        return f"https://www.google.com/travel/flights?q=Flights%20from%20{from_apt}%20to%20{to_apt}%20on%20{dep_date}%20returning%20{ret_date}&hl=en"
    else:
        return f"https://www.google.com/travel/flights?q=Flights%20from%20{from_apt}%20to%20{to_apt}%20on%20{dep_date}%20one%20way&hl=en"


def extract_prices(flights) -> list:
    """Extract unique prices from flights, sorted low to high."""
    prices = []
    seen = set()
    for f in flights:
        if f.price and f.price not in seen:
            seen.add(f.price)
            numeric = ''.join(c for c in f.price if c.isdigit())
            prices.append((int(numeric) if numeric else 0, f.price, f.is_best))
    prices.sort(key=lambda x: x[0])
    return prices[:10]


def main():
    parser = argparse.ArgumentParser(description="Search Google Flights (quick mode)")
    parser.add_argument("from_airport", help="Departure airport code (e.g., LAX, YYC)")
    parser.add_argument("to_airport", help="Arrival airport code (e.g., JFK, LHR)")
    parser.add_argument("date", help="Departure date (YYYY-MM-DD, 'tomorrow', 'next monday', etc.)")
    parser.add_argument("--return", "-r", dest="return_date", help="Return date for round-trip")
    parser.add_argument("--adults", "-a", type=int, default=1, help="Number of adults (default: 1)")
    parser.add_argument("--children", "-c", type=int, default=0, help="Number of children")
    parser.add_argument("--seat", "-s", choices=["economy", "premium-economy", "business", "first"], 
                        default="economy", help="Seat class")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    dep_date = parse_date(args.date)
    ret_date = parse_date(args.return_date) if args.return_date else None
    
    flight_data = [
        FlightData(
            date=dep_date,
            from_airport=args.from_airport.upper(),
            to_airport=args.to_airport.upper()
        )
    ]
    
    trip = "one-way"
    if ret_date:
        trip = "round-trip"
        flight_data.append(
            FlightData(
                date=ret_date,
                from_airport=args.to_airport.upper(),
                to_airport=args.from_airport.upper()
            )
        )
    
    # Suppress the "Impersonate" warning from primp
    import io
    from contextlib import redirect_stderr
    
    try:
        with redirect_stderr(io.StringIO()):
            result = get_flights(
                flight_data=flight_data,
                trip=trip,
                seat=args.seat,
                passengers=Passengers(
                    adults=args.adults,
                    children=args.children,
                    infants_in_seat=0,
                    infants_on_lap=0
                ),
                fetch_mode="fallback"
            )
    except Exception as e:
        print(f"Error fetching flights: {e}", file=sys.stderr)
        sys.exit(1)
    
    prices = extract_prices(result.flights)
    google_url = build_google_flights_url(
        args.from_airport.upper(), 
        args.to_airport.upper(),
        dep_date, 
        ret_date
    )
    
    if args.json:
        output = {
            "query": {
                "from": args.from_airport.upper(),
                "to": args.to_airport.upper(),
                "date": dep_date,
                "return_date": ret_date,
                "trip": trip,
                "seat": args.seat,
                "passengers": {"adults": args.adults, "children": args.children}
            },
            "price_trend": result.current_price,
            "prices": [{"price": p[1], "is_best": p[2]} for p in prices],
            "total_options": len(result.flights),
            "google_flights_url": google_url
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"✈️  {args.from_airport.upper()} → {args.to_airport.upper()}")
        print(f"📅 {dep_date}" + (f" ↔ {ret_date}" if ret_date else " (one-way)"))
        print(f"👥 {args.adults} adult(s)" + (f", {args.children} child(ren)" if args.children else ""))
        print(f"💺 {args.seat.replace('-', ' ').title()}")
        print()
        print(f"📊 Prices currently: {result.current_price.upper()}")
        print(f"🔢 {len(result.flights)} flight options found")
        print()
        
        if prices:
            print("💰 Price range:")
            for i, (_, price, is_best) in enumerate(prices[:5]):
                marker = "⭐" if is_best else "  "
                print(f"   {marker} {price}")
            if len(prices) > 5:
                print(f"   ... and {len(prices) - 5} more price points")
        
        print()
        print(f"🔗 {google_url}")


if __name__ == "__main__":
    main()
