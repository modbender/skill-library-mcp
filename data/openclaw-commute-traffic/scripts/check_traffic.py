#!/usr/bin/env python3
"""
Check real-time traffic between two locations using TomTom APIs.

Uses only Python stdlib (urllib + json) — no pip install required.
Handles geocoding (place name → coordinates) and routing (travel time with live traffic)
via the same TomTom API key.

Usage:
    python3 check_traffic.py --origin "Basel, Switzerland" --destination "Zurich, Switzerland"
    python3 check_traffic.py --origin "Basel SBB" --destination "Paradeplatz, Zürich"
    python3 check_traffic.py --origin "47.5596,7.5886" --destination "47.3769,8.5417"

Requires TOMTOM_API_KEY environment variable (free at developer.tomtom.com).
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

TOMTOM_BASE = "https://api.tomtom.com"
REQUEST_TIMEOUT = 30  # seconds per API call
MAX_ALTERNATIVES = 2  # number of alternative routes to request


def parse_args():
    parser = argparse.ArgumentParser(
        description="Check live traffic between two locations via TomTom"
    )
    parser.add_argument(
        "--origin", required=True,
        help="Starting location (address, place name, or lat,lng)",
    )
    parser.add_argument(
        "--destination", required=True,
        help="Destination (address, place name, or lat,lng)",
    )
    return parser.parse_args()


def is_coordinates(text: str) -> tuple:
    """Check if text is already lat,lng coordinates. Returns (lat, lng) or None."""
    match = re.match(
        r"^\s*(-?\d+\.?\d*)\s*[,\s]\s*(-?\d+\.?\d*)\s*$", text.strip()
    )
    if match:
        lat, lng = float(match.group(1)), float(match.group(2))
        if -90 <= lat <= 90 and -180 <= lng <= 180:
            return (lat, lng)
    return None


def tomtom_request(url: str) -> dict:
    """Make a GET request to a TomTom API endpoint."""
    req = urllib.request.Request(url, method="GET", headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = ""
        try:
            detail = e.read().decode("utf-8")
        except Exception:
            pass
        return {"error": True, "message": f"HTTP {e.code}: {e.reason}", "detail": detail}
    except urllib.error.URLError as e:
        return {"error": True, "message": f"Connection failed: {e.reason}"}
    except Exception as e:
        return {"error": True, "message": f"Unexpected error: {e}"}


def geocode(location: str, api_key: str) -> dict:
    """
    Resolve a location string to lat/lng using TomTom Geocoding API.
    If the input is already coordinates, skip the API call.
    Returns {"lat": float, "lng": float, "address": str} or {"error": ...}.
    """
    coords = is_coordinates(location)
    if coords:
        return {"lat": coords[0], "lng": coords[1], "address": location}

    encoded = urllib.parse.quote(location)
    url = (
        f"{TOMTOM_BASE}/search/2/geocode/{encoded}.json"
        f"?key={api_key}"
        f"&countrySet=CH"  # Bias to Switzerland
        f"&limit=1"
    )

    data = tomtom_request(url)
    if data.get("error"):
        return {"error": True, "message": f"Geocoding failed for '{location}': {data['message']}"}

    results = data.get("results", [])
    if not results:
        return {"error": True, "message": f"No coordinates found for '{location}'. Try a more specific address."}

    pos = results[0].get("position", {})
    addr = results[0].get("address", {}).get("freeformAddress", location)

    return {"lat": pos.get("lat"), "lng": pos.get("lon"), "address": addr}


def calculate_route(origin_lat: float, origin_lng: float,
                    dest_lat: float, dest_lng: float,
                    api_key: str) -> dict:
    """
    Calculate route with live traffic using TomTom Routing API.
    Returns the raw TomTom response or an error dict.
    """
    url = (
        f"{TOMTOM_BASE}/routing/1/calculateRoute"
        f"/{origin_lat},{origin_lng}:{dest_lat},{dest_lng}/json"
        f"?key={api_key}"
        f"&traffic=true"
        f"&travelMode=car"
        f"&routeType=fastest"
        f"&computeTravelTimeFor=all"
        f"&maxAlternatives={MAX_ALTERNATIVES}"
        f"&routeRepresentation=summaryOnly"
    )

    return tomtom_request(url)


def process_response(raw: dict, origin_addr: str, dest_addr: str,
                     origin_query: str, dest_query: str) -> dict:
    """Parse TomTom routing response into clean structured output."""

    if raw.get("error"):
        return {
            "status": "error",
            "origin_query": origin_query,
            "destination_query": dest_query,
            "message": raw.get("message", "Unknown routing error"),
        }

    routes = raw.get("routes", [])
    if not routes:
        return {
            "status": "no_data",
            "origin_query": origin_query,
            "destination_query": dest_query,
            "message": "No routes found. Try more specific locations.",
        }

    output = {
        "status": "success",
        "origin_query": origin_query,
        "origin_resolved": origin_addr,
        "destination_query": dest_query,
        "destination_resolved": dest_addr,
        "route_count": len(routes),
        "routes": [],
    }

    for i, route in enumerate(routes):
        summary = route.get("summary", {})

        travel_time_s = summary.get("travelTimeInSeconds", 0)
        no_traffic_s = summary.get("noTrafficTravelTimeInSeconds", 0)
        historic_s = summary.get("historicTrafficTravelTimeInSeconds", 0)
        live_s = summary.get("liveTrafficIncidentsTravelTimeInSeconds", 0)
        delay_s = summary.get("trafficDelayInSeconds", 0)
        length_m = summary.get("lengthInMeters", 0)

        # Derive congestion from delay relative to free-flow time
        if no_traffic_s > 0:
            delay_pct = (delay_s / no_traffic_s) * 100
        else:
            delay_pct = 0

        if delay_pct < 20:
            congestion = "light"
        elif delay_pct < 50:
            congestion = "moderate"
        else:
            congestion = "heavy"

        output["routes"].append({
            "route_number": i + 1,
            "distance_km": round(length_m / 1000, 1),
            "travel_time_min": round(travel_time_s / 60, 1),
            "no_traffic_time_min": round(no_traffic_s / 60, 1),
            "historic_traffic_time_min": round(historic_s / 60, 1),
            "live_traffic_time_min": round(live_s / 60, 1),
            "traffic_delay_min": round(delay_s / 60, 1),
            "traffic_delay_pct": round(delay_pct, 1),
            "congestion": congestion,
            "departure_time": summary.get("departureTime", ""),
            "arrival_time": summary.get("arrivalTime", ""),
        })

    # Sort by travel time — fastest first
    output["routes"].sort(key=lambda r: r["travel_time_min"])

    return output


def main():
    args = parse_args()

    api_key = os.environ.get("TOMTOM_API_KEY", "").strip()
    if not api_key:
        print(json.dumps({
            "status": "error",
            "message": "TOMTOM_API_KEY environment variable is not set. "
                       "Get a free key at https://developer.tomtom.com and configure it in "
                       "~/.openclaw/openclaw.json under skills.entries.commute-traffic.env.TOMTOM_API_KEY"
        }, indent=2))
        sys.exit(1)

    # Step 1: Geocode origin
    origin = geocode(args.origin, api_key)
    if origin.get("error"):
        print(json.dumps({"status": "error", "step": "geocode_origin", **origin}, indent=2))
        sys.exit(1)

    # Step 2: Geocode destination
    dest = geocode(args.destination, api_key)
    if dest.get("error"):
        print(json.dumps({"status": "error", "step": "geocode_destination", **dest}, indent=2))
        sys.exit(1)

    # Step 3: Calculate route with live traffic
    raw = calculate_route(origin["lat"], origin["lng"], dest["lat"], dest["lng"], api_key)

    # Step 4: Process and output
    result = process_response(raw, origin["address"], dest["address"], args.origin, args.destination)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    if result.get("status") == "error":
        sys.exit(1)


if __name__ == "__main__":
    main()
