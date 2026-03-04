#!/usr/bin/env python3
"""
Aerobase CLI - Flight search and jetlag scoring tool
"""
import argparse
import json
import os
import sys
from typing import Any, Optional

import requests

BASE_URL = "https://aerobase.app/api"


def get_api_key() -> str:
    """Get API key from environment or prompt."""
    api_key = os.environ.get("AEROBASE_API_KEY")
    if not api_key:
        print("Error: AEROBASE_API_KEY not set", file=sys.stderr)
        print("Get your API key from https://aerobase.app/connect", file=sys.stderr)
        sys.exit(1)
    return api_key


def get_headers() -> dict:
    """Get common headers for API requests."""
    return {
        "Authorization": f"Bearer {get_api_key()}",
        "Content-Type": "application/json",
    }


def search_flights(
    origin: str,
    destination: str,
    date: str,
    return_date: Optional[str] = None,
    cabin: str = "economy",
    sort: str = "jetlag",
    limit: int = 10,
) -> dict:
    """Search flights with jetlag scoring."""
    payload = {
        "from": origin,
        "to": destination,
        "date": date,
        "cabin": cabin,
        "sort": sort,
        "limit": limit,
    }
    if return_date:
        payload["returnDate"] = return_date

    response = requests.post(
        f"{BASE_URL}/v1/flights/search",
        headers=get_headers(),
        json=payload,
    )
    response.raise_for_status()
    return response.json()


def score_flight(
    origin: str,
    destination: str,
    departure: str,
    arrival: str,
    cabin: str = "economy",
    chronotype: Optional[str] = None,
) -> dict:
    """Score a flight for jetlag impact."""
    payload = {
        "from": origin,
        "to": destination,
        "departure": departure,
        "arrival": arrival,
        "cabin": cabin,
    }
    if chronotype:
        payload["chronotype"] = chronotype

    response = requests.post(
        f"{BASE_URL}/v1/flights/score",
        headers=get_headers(),
        json=payload,
    )
    response.raise_for_status()
    return response.json()


def compare_flights(flights: list, labels: Optional[list] = None) -> dict:
    """Compare multiple flights."""
    if labels:
        flights = [
            {**flight, "label": label}
            for flight, label in zip(flights, labels)
        ]

    response = requests.post(
        f"{BASE_URL}/v1/flights/compare",
        headers=get_headers(),
        json={"flights": flights},
    )
    response.raise_for_status()
    return response.json()


def get_deals(
    departure: Optional[str] = None,
    destination: Optional[str] = None,
    max_price: Optional[int] = None,
    sort: str = "jetlag_score",
    limit: int = 10,
) -> dict:
    """Get travel deals with jetlag scores."""
    params = {"sort": sort, "limit": limit}
    if departure:
        params["departure"] = departure
    if destination:
        params["destination"] = destination
    if max_price:
        params["max_price"] = max_price

    response = requests.get(
        f"{BASE_URL}/v1/deals",
        headers=get_headers(),
        params=params,
    )
    response.raise_for_status()
    return response.json()


def get_recovery_plan(
    origin: str,
    destination: str,
    departure: str,
    arrival: str,
    cabin: str = "economy",
    commitments: Optional[list] = None,
) -> dict:
    """Generate a recovery plan."""
    payload = {
        "from": origin,
        "to": destination,
        "departure": departure,
        "arrival": arrival,
        "cabin": cabin,
    }
    if commitments:
        payload["arrival_commitments"] = commitments

    response = requests.post(
        f"{BASE_URL}/v1/recovery/plan",
        headers=get_headers(),
        json=payload,
    )
    response.raise_for_status()
    return response.json()


def get_airport(code: str) -> dict:
    """Get airport information."""
    response = requests.get(
        f"{BASE_URL}/v1/airports/{code}",
        headers=get_headers(),
    )
    response.raise_for_status()
    return response.json()


def get_hotels(airport: str, jetlag_friendly: bool = False, limit: int = 10) -> dict:
    """Search hotels near airport."""
    params = {"airport": airport, "limit": limit}
    if jetlag_friendly:
        params["jetlagFriendly"] = "true"

    response = requests.get(
        f"{BASE_URL}/v1/hotels",
        headers=get_headers(),
        params=params,
    )
    response.raise_for_status()
    return response.json()


def get_lounges(airport: str, limit: int = 10) -> dict:
    """Search airport lounges."""
    response = requests.get(
        f"{BASE_URL}/v1/lounges",
        headers=get_headers(),
        params={"airport": airport, "limit": limit},
    )
    response.raise_for_status()
    return response.json()


def analyze_itinerary(legs: list) -> dict:
    """Analyze multi-leg itinerary."""
    response = requests.post(
        f"{BASE_URL}/v1/itinerary/analyze",
        headers=get_headers(),
        json={"legs": legs},
    )
    response.raise_for_status()
    return response.json()


def format_flight_result(data: dict) -> str:
    """Format flight search results for display."""
    if "error" in data.get("data", {}):
        return f"Error: {data['data']['error']['message']}"

    flights = data.get("data", {}).get("flights", [])
    if not flights:
        return "No flights found."

    lines = []
    for f in flights:
        score = f.get("jetlag_score", "N/A")
        recovery = f.get("recovery_days", "?")
        lines.append(
            f"✈️ {f.get('airline', 'Unknown')} {f.get('flight_number', '')} "
            f"{f.get('origin', '')} → {f.get('destination', '')}"
        )
        lines.append(f"   Score: {score}/100 | Recovery: {recovery} days")
        lines.append(f"   {f.get('departure_time', '')} → {f.get('arrival_time', '')}")
        if f.get("price"):
            lines.append(f"   💰 ${f['price']}")
        lines.append("")

    return "\n".join(lines)


def format_score_result(data: dict) -> str:
    """Format flight score result for display."""
    if "error" in data.get("data", {}):
        return f"Error: {data['data']['error']['message']}"

    score_data = data.get("data", {})
    score = score_data.get("score", 0)
    tier = score_data.get("tier", "unknown")
    recovery = score_data.get("recovery_days", "?")
    direction = score_data.get("direction", "none")
    shift = score_data.get("timezone_shift_hours", 0)

    lines = [
        f"🛫 Jetlag Score: {score}/100 ({tier})",
        f"📅 Recovery: {recovery} days",
        f"🧭 Direction: {direction} ({shift} hours)",
    ]

    insight = score_data.get("insight")
    if insight:
        lines.append(f"\n💡 {insight}")

    strategies = score_data.get("strategies", {})
    if strategies:
        lines.append("\n📋 Strategies:")
        for key, value in strategies.items():
            lines.append(f"  • {key}: {value}")

    return "\n".join(lines)


def format_deals_result(data: dict) -> str:
    """Format deals result for display."""
    if "error" in data.get("data", {}):
        return f"Error: {data['data']['error']['message']}"

    deals = data.get("data", {}).get("deals", [])
    if not deals:
        return "No deals found."

    lines = []
    for d in deals:
        score = d.get("jetlag", {}).get("score", "N/A")
        price = d.get("price_usd", 0)
        origin = d.get("origin", {}).get("iata", "")
        dest = d.get("destination", {}).get("iata", "")
        lines.append(f"✈️ {origin} → {dest} | ${price} | Score: {score}/100")
        lines.append(f"   {d.get('title', '')}")
        if d.get("booking_deadline"):
            lines.append(f"   ⏰ Book by: {d['booking_deadline'][:10]}")
        lines.append("")

    return "\n".join(lines)


def format_recovery_result(data: dict) -> str:
    """Format recovery plan for display."""
    if "error" in data.get("data", {}):
        return f"Error: {data['data']['error']['message']}"

    plan = data.get("data", {}).get("recovery_plan", {})
    score_data = data.get("data", {}).get("score", {})

    lines = [
        f"🛫 Jetlag Score: {score_data.get('score', 0)}/100 ({score_data.get('tier', '')})",
        f"📅 Estimated Recovery: {score_data.get('recovery_days', '?')} days",
        f"🧭 Direction: {score_data.get('direction', '')}",
    ]

    pre_flight = plan.get("pre_flight_schedule", [])
    if pre_flight:
        lines.append("\n📅 Pre-Flight Schedule:")
        for item in pre_flight[:5]:
            lines.append(f"  Day {item.get('day')}: {item.get('title')}")

    post_arrival = plan.get("post_arrival_schedule", [])
    if post_arrival:
        lines.append("\n📅 Post-Arrival:")
        for item in post_arrival[:5]:
            lines.append(f"  Day {item.get('day')}: {item.get('title')}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Aerobase Flight CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search flights")
    search_parser.add_argument("--from", dest="origin", required=True, help="Origin IATA")
    search_parser.add_argument("--to", dest="destination", required=True, help="Destination IATA")
    search_parser.add_argument("--date", required=True, help="Departure date (YYYY-MM-DD)")
    search_parser.add_argument("--return", dest="return_date", help="Return date")
    search_parser.add_argument("--cabin", default="economy", help="Cabin class")
    search_parser.add_argument("--sort", default="jetlag", help="Sort by")
    search_parser.add_argument("--limit", type=int, default=10, help="Max results")

    # Score command
    score_parser = subparsers.add_parser("score", help="Score a flight")
    score_parser.add_argument("--from", dest="origin", required=True)
    score_parser.add_argument("--to", dest="destination", required=True)
    score_parser.add_argument("--departure", required=True, help="ISO 8601 datetime")
    score_parser.add_argument("--arrival", required=True, help="ISO 8601 datetime")
    score_parser.add_argument("--cabin", default="economy")
    score_parser.add_argument("--chronotype")

    # Compare command
    compare_parser = subparsers.add_parser("compare", help="Compare flights")
    compare_parser.add_argument("--flights", nargs="+", required=True, help="Flight JSON")

    # Deals command
    deals_parser = subparsers.add_parser("deals", help="Get travel deals")
    deals_parser.add_argument("--from", dest="departure", help="Origin")
    deals_parser.add_argument("--to", dest="destination", help="Destination")
    deals_parser.add_argument("--max-price", type=int, help="Max price")
    deals_parser.add_argument("--sort", default="jetlag_score")
    deals_parser.add_argument("--limit", type=int, default=10)

    # Recovery command
    recovery_parser = subparsers.add_parser("recovery", help="Get recovery plan")
    recovery_parser.add_argument("--from", dest="origin", required=True)
    recovery_parser.add_argument("--to", dest="destination", required=True)
    recovery_parser.add_argument("--departure", required=True)
    recovery_parser.add_argument("--arrival", required=True)
    recovery_parser.add_argument("--cabin", default="economy")

    # Airport command
    airport_parser = subparsers.add_parser("airport", help="Get airport info")
    airport_parser.add_argument("code", help="Airport IATA code")

    # Hotels command
    hotels_parser = subparsers.add_parser("hotels", help="Search hotels")
    hotels_parser.add_argument("--airport", required=True)
    hotels_parser.add_argument("--jetlag-friendly", action="store_true")
    hotels_parser.add_argument("--limit", type=int, default=10)

    # Lounges command
    lounges_parser = subparsers.add_parser("lounges", help="Search lounges")
    lounges_parser.add_argument("--airport", required=True)
    lounges_parser.add_argument("--limit", type=int, default=10)

    # Itinerary command
    itinerary_parser = subparsers.add_parser("itinerary", help="Analyze itinerary")
    itinerary_parser.add_argument("--legs", nargs="+", required=True, help="Leg JSON")

    # Output format
    parser.add_argument("--json", action="store_true", help="Output JSON")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        result = None

        if args.command == "search":
            result = search_flights(
                args.origin, args.destination, args.date,
                args.return_date, args.cabin, args.sort, args.limit
            )
            output = format_flight_result(result) if not args.json else json.dumps(result, indent=2)

        elif args.command == "score":
            result = score_flight(
                args.origin, args.destination,
                args.departure, args.arrival,
                args.cabin, args.chronotype
            )
            output = format_score_result(result) if not args.json else json.dumps(result, indent=2)

        elif args.command == "compare":
            flights = [json.loads(f) for f in args.flights]
            result = compare_flights(flights)
            output = json.dumps(result, indent=2) if args.json else result

        elif args.command == "deals":
            result = get_deals(args.departure, args.destination, args.max_price, args.sort, args.limit)
            output = format_deals_result(result) if not args.json else json.dumps(result, indent=2)

        elif args.command == "recovery":
            result = get_recovery_plan(
                args.origin, args.destination,
                args.departure, args.arrival,
                args.cabin
            )
            output = format_recovery_result(result) if not args.json else json.dumps(result, indent=2)

        elif args.command == "airport":
            result = get_airport(args.code)
            output = json.dumps(result, indent=2) if args.json else result

        elif args.command == "hotels":
            result = get_hotels(args.airport, args.jetlag_friendly, args.limit)
            output = json.dumps(result, indent=2) if args.json else result

        elif args.command == "lounges":
            result = get_lounges(args.airport, args.limit)
            output = json.dumps(result, indent=2) if args.json else result

        elif args.command == "itinerary":
            legs = [json.loads(l) for l in args.legs]
            result = analyze_itinerary(legs)
            output = json.dumps(result, indent=2) if args.json else result

        print(output)

    except requests.exceptions.HTTPError as e:
        if e.response:
            error_data = e.response.json()
            print(f"Error: {error_data.get('error', {}).get('message', str(e))}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
