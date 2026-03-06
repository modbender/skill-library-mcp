#!/usr/bin/env python3
"""
Google Flights search via SearchAPI.io.

Usage:
    # One-way search
    python search_searchapi.py --from TLV --to LON --date 2026-03-15

    # Round-trip with auto return flight fetch for top 5 results
    python search_searchapi.py --from TLV --to BKK --date 2026-03-28 --return-date 2026-04-14 --top 5

    # Other options
    python search_searchapi.py --from TLV --to LON --date 2026-03-15 --days 3
    python search_searchapi.py --from TLV --to LON --date 2026-03-15 --currency ILS --adults 2
    python search_searchapi.py --from TLV --to LON --date 2026-03-15 --stops 1

    # Fetch return flights for a specific outbound (using departure_token)
    python search_searchapi.py --from TLV --to BKK --date 2026-03-28 --departure-token "TOKEN..."

    # Fetch booking options (real airline/OTA URLs) for a specific flight
    python search_searchapi.py --from TLV --to LON --date 2026-03-15 --booking-token "TOKEN..."

Reads SEARCHAPI_KEY from environment (loaded by openclaw via .env).
Outputs JSON flight results. For round-trips with --top N, each outbound result
includes a nested "return_flight" object with full return leg details.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import date, datetime, timedelta
from pathlib import Path


SEARCHAPI_ENDPOINT = "https://www.searchapi.io/api/v1/search"

# Logs directory: workspace-travel-agent/logs/skills/google-flights-search/
SCRIPT_DIR = Path(__file__).resolve().parent
LOG_DIR = SCRIPT_DIR.parent.parent.parent / "logs" / "skills" / "google-flights-search"

# City code -> preferred airport codes
# SearchAPI.io supports comma-separated departure_id/arrival_id,
# so we can pass multiple airports in a single request.
CITY_TO_AIRPORTS = {
    "LON": ["LHR", "LGW", "STN", "LTN"],
    "PAR": ["CDG", "ORY"],
    "NYC": ["JFK", "EWR", "LGA"],
    "MIL": ["MXP", "LIN", "BGY"],
    "ROM": ["FCO", "CIA"],
    "BER": ["BER"],
    "AMS": ["AMS"],
    "BCN": ["BCN"],
    "MAD": ["MAD"],
    "ATH": ["ATH"],
    "IST": ["IST", "SAW"],
    "TLV": ["TLV"],
}

# Map numeric stops arg to SearchAPI.io string values
STOPS_MAP = {
    0: "nonstop",
    1: "one_stop_or_fewer",
    2: "two_stops_or_fewer",
}

# Map numeric travel class arg to SearchAPI.io string values
TRAVEL_CLASS_MAP = {
    "1": "economy",
    "2": "premium_economy",
    "3": "business",
    "4": "first_class",
    # Also accept string values directly
    "economy": "economy",
    "premium_economy": "premium_economy",
    "business": "business",
    "first_class": "first_class",
}


def parse_args():
    parser = argparse.ArgumentParser(description="Search Google Flights via SearchAPI.io")
    parser.add_argument("--from", dest="origin", required=True, help="Origin airport IATA code (e.g. TLV)")
    parser.add_argument("--to", dest="destination", required=True, help="Destination airport IATA code (e.g. LON)")
    parser.add_argument("--date", required=True, help="Outbound date YYYY-MM-DD")
    parser.add_argument("--return-date", dest="return_date", default=None, help="Return date YYYY-MM-DD (makes it a round-trip search)")
    parser.add_argument("--days", type=int, default=1, choices=range(1, 4), help="Number of days to search from start date (default: 1, max: 3)")
    parser.add_argument("--currency", default="USD", help="Currency code (default: USD)")
    parser.add_argument("--adults", type=int, default=1, help="Number of adult passengers (default: 1)")
    parser.add_argument("--stops", type=int, default=None, help="Max stops: 0=direct only, 1=up to 1 stop, 2=up to 2 stops (default: any)")
    parser.add_argument("--class", dest="travel_class", default=None, help="Travel class: 1=economy, 2=premium_economy, 3=business, 4=first_class (default: economy)")
    parser.add_argument("--departure-token", dest="departure_token", default=None, help="Departure token from a previous round-trip search. Fetches return flights for that specific outbound.")
    parser.add_argument("--booking-token", dest="booking_token", default=None, help="Booking token from a previous search. Fetches booking options (URLs to airline/OTA sites).")
    parser.add_argument("--top", type=int, default=None, help="For round-trip: auto-fetch return flights for top N outbound results (default: no auto-fetch)")
    return parser.parse_args()


def get_api_key():
    key = os.environ.get("SEARCHAPI_KEY")
    if not key:
        print(json.dumps({"error": "SEARCHAPI_KEY not set in environment. Add it to your .env file."}))
        sys.exit(1)
    return key


def resolve_airports(code):
    """Return list of airport codes to search. Expands city codes to airports."""
    return CITY_TO_AIRPORTS.get(code.upper(), [code.upper()])


def _api_call(params, api_key):
    """Make an API call to SearchAPI.io. Returns (log_params, response_data)."""
    params["api_key"] = api_key
    url = f"{SEARCHAPI_ENDPOINT}?{urllib.parse.urlencode(params)}"
    log_params = {k: v for k, v in params.items() if k != "api_key"}

    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode()
        except Exception:
            pass
        data = {"error": f"HTTP {e.code}: {e.reason}", "detail": body}
    except Exception as e:
        data = {"error": str(e)}

    return log_params, data


def search_date(origin, destination_airports, outbound_date, return_date, currency, adults, stops, travel_class, api_key):
    """
    Search flights for a single date. SearchAPI.io supports comma-separated
    arrival_id, so we can query all destination airports in one request.
    Returns (request_params, response_data) tuple for logging.
    """
    flight_type = "round_trip" if return_date else "one_way"

    params = {
        "engine": "google_flights",
        "departure_id": origin,
        "arrival_id": ",".join(destination_airports),
        "outbound_date": outbound_date,
        "currency": currency,
        "adults": adults,
        "flight_type": flight_type,
        "show_cheapest_flights": True,
        "show_hidden_flights": True,
    }

    if return_date:
        params["return_date"] = return_date

    if stops is not None:
        params["stops"] = STOPS_MAP.get(stops, "any")

    if travel_class is not None:
        params["travel_class"] = TRAVEL_CLASS_MAP.get(str(travel_class), "economy")

    log_params, data = _api_call(params, api_key)
    if "error" not in data:
        data["_search_date"] = outbound_date
    else:
        data["date"] = outbound_date

    return log_params, data


def search_return_flights(departure_token, origin, destination_airports, outbound_date, return_date, currency, api_key):
    """
    Fetch return flight options for a specific outbound selection.
    Uses the departure_token from a previous round-trip search.
    The API requires all original search params alongside the token.
    Returns (request_params, response_data) tuple for logging.
    """
    params = {
        "engine": "google_flights",
        "departure_id": origin,
        "arrival_id": ",".join(destination_airports),
        "outbound_date": outbound_date,
        "return_date": return_date,
        "flight_type": "round_trip",
        "currency": currency,
        "departure_token": departure_token,
    }
    return _api_call(params, api_key)


def _parse_booking_token(token):
    """
    Decode a booking_token (base64 JSON array) to extract return_date if present.
    Round-trip tokens have 3 elements: [encoded_str, outbound_legs, return_legs].
    The return_date is the departure date of the first return leg (index [2][0][1]).
    Returns the return_date string or None.
    """
    import base64
    try:
        decoded = json.loads(base64.b64decode(token))
        if isinstance(decoded, list) and len(decoded) >= 3 and decoded[2]:
            return decoded[2][0][1]  # e.g. "2026-04-14"
    except Exception:
        pass
    return None


def search_booking_options(booking_token, origin, destination_airports, outbound_date, return_date, currency, api_key):
    """
    Fetch booking options for a specific flight using its booking_token.
    The API requires the original search params alongside the token.
    Returns (request_params, response_data) tuple for logging.
    The response contains a booking_options array with book_with, price,
    and booking_request (url + optional post_data) for each OTA/airline.
    """
    # Strip any whitespace/newlines that may have been injected by shell line-wrapping
    booking_token = booking_token.strip().replace("\n", "").replace("\r", "")

    # Auto-detect return_date from round-trip tokens when not provided via CLI
    if not return_date:
        return_date = _parse_booking_token(booking_token)

    params = {
        "engine": "google_flights",
        "departure_id": origin,
        "arrival_id": ",".join(destination_airports),
        "outbound_date": outbound_date,
        "currency": currency,
        "booking_token": booking_token,
    }
    if return_date:
        params["return_date"] = return_date
        params["flight_type"] = "round_trip"
    return _api_call(params, api_key)


def _resolve_booking_url(url, post_data):
    """
    Resolve a Google click-tracker URL to the actual airline booking URL.
    Google returns HTML with a <meta> refresh tag containing the real URL.
    Falls back to the original url if resolution fails.
    """
    import http.client
    import html
    import re
    try:
        conn = http.client.HTTPSConnection("www.google.com", timeout=10)
        conn.request("POST", "/travel/clk/f", body=post_data, headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0",
        })
        resp = conn.getresponse()
        body = resp.read().decode("utf-8", errors="replace")[:4000]
        conn.close()
        # Extract URL from <meta content="0;url='...'" />
        match = re.search(r"url='([^']+)'", body)
        if match:
            return html.unescape(match.group(1))
    except Exception:
        pass
    return url


def _normalize_legs(legs, layovers):
    """Extract common fields from a list of flight legs."""
    first_leg = legs[0]
    last_leg = legs[-1]

    stops = len(legs) - 1
    min_layover_minutes = min((lay.get("duration", 999) for lay in layovers), default=None)

    departure_airport = first_leg.get("departure_airport", {})
    arrival_airport = last_leg.get("arrival_airport", {})

    return {
        "airline": first_leg.get("airline", "Unknown"),
        "flight_number": first_leg.get("flight_number"),
        "origin": departure_airport.get("id", ""),
        "destination": arrival_airport.get("id", ""),
        "departure_time": departure_airport.get("time", ""),
        "departure_date": departure_airport.get("date", ""),
        "arrival_time": arrival_airport.get("time", ""),
        "arrival_date": arrival_airport.get("date", ""),
        "stops": stops,
        "layovers": [
            {"airport": lay.get("name"), "duration_minutes": lay.get("duration")}
            for lay in layovers
        ],
        "min_layover_minutes": min_layover_minutes,
    }


def normalize_flight(flight, search_date, include_token=False):
    """
    Flatten a SearchAPI.io flight object into a minimal dict for the agent to score.
    Only includes fields needed for scoring and presentation to reduce token bloat.
    When include_token=True, includes departure_token for round-trip return lookups.
    """
    legs = flight.get("flights", [])
    if not legs:
        return None

    layovers = flight.get("layovers", [])
    result = _normalize_legs(legs, layovers)
    result["search_date"] = search_date
    result["duration_minutes"] = flight.get("total_duration")
    result["price"] = flight.get("price")
    result["overnight"] = flight.get("overnight", False)

    if include_token and flight.get("departure_token"):
        result["departure_token"] = flight["departure_token"]

    # Always capture booking_token when available (used for real booking links)
    if flight.get("booking_token"):
        result["booking_token"] = flight["booking_token"]

    return result


def normalize_return_flight(flight):
    """
    Normalize a return flight from the departure_token lookup.
    Same structure as outbound but without departure_token.
    """
    legs = flight.get("flights", [])
    if not legs:
        return None

    layovers = flight.get("layovers", [])
    result = _normalize_legs(legs, layovers)
    result["duration_minutes"] = flight.get("total_duration")
    result["price"] = flight.get("price")
    result["overnight"] = flight.get("overnight", False)

    # Capture booking_token when available (used for real booking links)
    if flight.get("booking_token"):
        result["booking_token"] = flight["booking_token"]

    return result


def save_log(args, api_calls, output):
    """Save request/response log for this search execution."""
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{args.origin}_{args.destination}.json"
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "cli_args": {
                "origin": args.origin,
                "destination": args.destination,
                "date": args.date,
                "return_date": args.return_date,
                "days": args.days,
                "currency": args.currency,
                "adults": args.adults,
                "stops": args.stops,
                "travel_class": args.travel_class,
            },
            "api_calls": api_calls,
            "normalized_output": output,
        }
        (LOG_DIR / filename).write_text(
            json.dumps(log_entry, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except Exception:
        pass  # Never let logging break the search


def _fetch_return_for_top(outbound_flights, top_n, origin, destination_airports, return_date, currency, api_key, api_calls):
    """
    For the top N outbound flights, fetch return flight options using their
    departure_token. Returns a dict mapping outbound index to best return flight.
    """
    returns = {}
    for i, outbound in enumerate(outbound_flights[:top_n]):
        token = outbound.get("departure_token")
        if not token:
            continue

        outbound_date = outbound.get("search_date", outbound.get("departure_date", ""))

        log_params, raw = search_return_flights(
            departure_token=token,
            origin=origin,
            destination_airports=destination_airports,
            outbound_date=outbound_date,
            return_date=return_date,
            currency=currency,
            api_key=api_key,
        )
        api_calls.append({"request": log_params, "response": raw, "type": "return_lookup", "outbound_index": i})

        if "error" in raw:
            continue

        best = raw.get("best_flights", [])
        other = raw.get("other_flights", [])
        all_returns = best + other

        if all_returns:
            # Pick the best (first) return option
            normalized = normalize_return_flight(all_returns[0])
            if normalized:
                returns[i] = normalized

    return returns


def main():
    args = parse_args()
    api_key = get_api_key()

    # Mode 0: Booking token lookup (fetch booking options with real URLs)
    if args.booking_token:
        destination_airports = resolve_airports(args.destination)
        api_calls = []
        log_params, raw = search_booking_options(
            booking_token=args.booking_token,
            origin=args.origin,
            destination_airports=destination_airports,
            outbound_date=args.date,
            return_date=args.return_date,
            currency=args.currency,
            api_key=api_key,
        )
        api_calls.append({"request": log_params, "response": raw, "type": "booking_lookup"})

        booking_options = []
        if "error" not in raw:
            for opt in raw.get("booking_options", []):
                option = {
                    "book_with": opt.get("book_with"),
                    "price": opt.get("price"),
                }
                req = opt.get("booking_request", {})
                url = req.get("url", "")
                post_data = req.get("post_data", "")
                # Resolve Google click-tracker to actual airline URL
                if url and post_data:
                    option["url"] = _resolve_booking_url(url, post_data)
                elif url:
                    option["url"] = url
                booking_options.append(option)

        output = {
            "mode": "booking_lookup",
            "total_options": len(booking_options),
            "booking_options": booking_options,
        }

        save_log(args, api_calls, output)
        print(json.dumps(output, ensure_ascii=False))
        return

    # Mode 1: Single departure_token lookup (return flights for one outbound)
    if args.departure_token:
        destination_airports = resolve_airports(args.destination)
        api_calls = []
        log_params, raw = search_return_flights(
            departure_token=args.departure_token,
            origin=args.origin,
            destination_airports=destination_airports,
            outbound_date=args.date,
            return_date=args.return_date,
            currency=args.currency,
            api_key=api_key,
        )
        api_calls.append({"request": log_params, "response": raw, "type": "return_lookup"})

        results = []
        if "error" not in raw:
            best = raw.get("best_flights", [])
            other = raw.get("other_flights", [])
            for flight in best + other:
                normalized = normalize_return_flight(flight)
                if normalized:
                    results.append(normalized)

        results.sort(key=lambda f: f.get("price") or float("inf"))
        capped = results[:10]

        output = {
            "mode": "return_lookup",
            "origin": args.origin,
            "destination": args.destination,
            "total_results": len(results),
            "showing": len(capped),
            "return_flights": capped,
        }

        save_log(args, api_calls, output)
        print(json.dumps(output, ensure_ascii=False))
        return

    # Mode 2: Standard search (outbound, or round-trip outbound + auto return fetch)
    start = date.fromisoformat(args.date)
    destination_airports = resolve_airports(args.destination)
    is_round_trip = bool(args.return_date)
    all_results = []
    errors = []
    api_calls = []

    for i in range(args.days):
        search_day = start + timedelta(days=i)
        date_str = search_day.isoformat()

        log_params, raw = search_date(
            origin=args.origin,
            destination_airports=destination_airports,
            outbound_date=date_str,
            return_date=args.return_date,
            currency=args.currency,
            adults=args.adults,
            stops=args.stops,
            travel_class=args.travel_class,
            api_key=api_key,
        )

        api_calls.append({"request": log_params, "response": raw})

        if "error" in raw:
            errors.append(raw)
            continue

        best = raw.get("best_flights", [])
        other = raw.get("other_flights", [])

        for flight in best + other:
            normalized = normalize_flight(flight, date_str, include_token=is_round_trip)
            if normalized:
                all_results.append(normalized)

    # Sort by price (cheapest first) and cap at 15 results
    all_results.sort(key=lambda f: f.get("price") or float("inf"))
    capped = all_results[:15]

    # For round-trips with --top N, auto-fetch return flights for top N outbound results
    return_flights = {}
    if is_round_trip and args.top and args.top > 0:
        return_flights = _fetch_return_for_top(
            capped, args.top, args.origin, destination_airports,
            args.return_date, args.currency, api_key, api_calls,
        )
        # Attach return flight to each outbound result
        for idx, ret in return_flights.items():
            if idx < len(capped):
                capped[idx]["return_flight"] = ret
                # Remove departure_token from output (no longer needed, saves tokens)
                capped[idx].pop("departure_token", None)

    output = {
        "origin": args.origin,
        "destination": args.destination,
        "flight_type": "round_trip" if is_round_trip else "one_way",
        "date_range": {
            "from": args.date,
            "to": (start + timedelta(days=args.days - 1)).isoformat(),
            "days_searched": args.days,
        },
        "currency": args.currency,
        "total_results": len(all_results),
        "showing": len(capped),
        "flights": capped,
    }

    if is_round_trip:
        output["return_date"] = args.return_date
        if args.top:
            output["return_flights_fetched_for_top"] = min(args.top, len(capped))

    if errors:
        output["errors"] = errors

    save_log(args, api_calls, output)
    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
