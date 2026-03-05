#!/usr/bin/env python3
"""Entur API client — journey planning and geocoding for Norway.

Usage:
  entur.py search <query>                     Search for stops/places
  entur.py trip <from> <to> [--time ISO] [--arrive] [--modes bus,rail,...]
  entur.py departures <stop_id> [--limit N]   Departure board for a stop
  entur.py stop <stop_id>                     Stop details

All output is JSON for easy parsing by the agent.
"""

import argparse
import json
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timezone

GEOCODER_URL = "https://api.entur.io/geocoder/v1/autocomplete"
JOURNEY_URL = "https://api.entur.io/journey-planner/v3/graphql"
CLIENT_NAME = "openclaw-entur-travel"
HEADERS = {
    "ET-Client-Name": CLIENT_NAME,
    "Content-Type": "application/json",
}


def _graphql(query: str, variables: dict | None = None) -> dict:
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(JOURNEY_URL, data=body, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def _geocode(text: str, limit: int = 5) -> list:
    params = urllib.parse.urlencode({
        "text": text,
        "size": limit,
        "lang": "en",
        "layers": "venue,address",
    })
    url = f"{GEOCODER_URL}?{params}"
    req = urllib.request.Request(url, headers={"ET-Client-Name": CLIENT_NAME})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
    results = []
    for f in data.get("features", []):
        p = f.get("properties", {})
        coords = f.get("geometry", {}).get("coordinates", [None, None])
        results.append({
            "id": p.get("id"),
            "name": p.get("name"),
            "label": p.get("label"),
            "category": p.get("category", []),
            "county": p.get("county"),
            "locality": p.get("locality"),
            "coordinates": {"lon": coords[0], "lat": coords[1]} if coords[0] else None,
        })
    return results


def cmd_search(args):
    results = _geocode(args.query, limit=args.limit or 5)
    print(json.dumps(results, indent=2, ensure_ascii=False))


def cmd_trip(args):
    # Resolve from/to — if they look like stop IDs (NSR:*), use directly; otherwise geocode
    from_place = _resolve_place(args.from_place)
    to_place = _resolve_place(args.to_place)

    if not from_place or not to_place:
        print(json.dumps({"error": "Could not resolve origin or destination"}))
        sys.exit(1)

    # Build mode filter
    modes_filter = ""
    if args.modes:
        mode_list = [m.strip() for m in args.modes.split(",")]
        transport_modes = ", ".join(
            f'{{transportMode: {m}}}' for m in mode_list
        )
        modes_filter = f"modes: {{transportModes: [{transport_modes}]}}"

    time_clause = ""
    if args.time:
        time_clause = f'dateTime: "{args.time}"'
    
    arrive_clause = ""
    if args.arrive:
        arrive_clause = "arriveBy: true"

    query = f"""
    {{
      trip(
        from: {{{_place_arg(from_place)}}}
        to: {{{_place_arg(to_place)}}}
        numTripPatterns: {args.results or 3}
        {time_clause}
        {arrive_clause}
        {modes_filter}
      ) {{
        tripPatterns {{
          startTime
          endTime
          duration
          walkDistance
          legs {{
            mode
            expectedStartTime
            expectedEndTime
            fromPlace {{ name }}
            toPlace {{ name }}
            line {{
              publicCode
              name
              authority {{ name }}
            }}
            fromEstimatedCall {{
              quay {{ name publicCode }}
              aimedDepartureTime
              expectedDepartureTime
              realtime
            }}
            toEstimatedCall {{
              quay {{ name }}
              aimedArrivalTime
              expectedArrivalTime
            }}
          }}
        }}
      }}
    }}
    """

    data = _graphql(query)
    patterns = data.get("data", {}).get("trip", {}).get("tripPatterns", [])
    
    # Format for readability
    trips = []
    for p in patterns:
        legs = []
        for leg in p.get("legs", []):
            leg_info = {
                "mode": leg["mode"],
                "from": leg["fromPlace"]["name"],
                "to": leg["toPlace"]["name"],
                "depart": leg["expectedStartTime"],
                "arrive": leg["expectedEndTime"],
            }
            if leg.get("line"):
                leg_info["line"] = leg["line"]["publicCode"]
                leg_info["lineName"] = leg["line"].get("name")
                leg_info["operator"] = leg["line"].get("authority", {}).get("name")
            fc = leg.get("fromEstimatedCall")
            if fc:
                leg_info["realtime"] = fc.get("realtime", False)
                if fc.get("quay", {}).get("publicCode"):
                    leg_info["platform"] = fc["quay"]["publicCode"]
            legs.append(leg_info)
        trips.append({
            "depart": p.get("startTime"),
            "arrive": p.get("endTime"),
            "duration_sec": p.get("duration"),
            "walk_m": round(p.get("walkDistance", 0)),
            "legs": legs,
        })
    
    print(json.dumps(trips, indent=2, ensure_ascii=False))


def cmd_departures(args):
    query = f"""
    {{
      stopPlace(id: "{args.stop_id}") {{
        id
        name
        estimatedCalls(timeRange: 3600, numberOfDepartures: {args.limit or 10}) {{
          realtime
          aimedDepartureTime
          expectedDepartureTime
          destinationDisplay {{ frontText }}
          serviceJourney {{
            line {{
              publicCode
              name
              transportMode
              authority {{ name }}
            }}
          }}
          quay {{ name publicCode }}
        }}
      }}
    }}
    """
    data = _graphql(query)
    stop = data.get("data", {}).get("stopPlace")
    if not stop:
        print(json.dumps({"error": f"Stop {args.stop_id} not found"}))
        sys.exit(1)

    departures = []
    for c in stop.get("estimatedCalls", []):
        sj = c.get("serviceJourney", {})
        line = sj.get("line", {})
        departures.append({
            "line": line.get("publicCode"),
            "name": line.get("name"),
            "mode": line.get("transportMode"),
            "destination": c.get("destinationDisplay", {}).get("frontText"),
            "aimed": c.get("aimedDepartureTime"),
            "expected": c.get("expectedDepartureTime"),
            "realtime": c.get("realtime", False),
            "platform": c.get("quay", {}).get("publicCode"),
            "operator": line.get("authority", {}).get("name"),
        })

    result = {"stop": stop["name"], "id": stop["id"], "departures": departures}
    print(json.dumps(result, indent=2, ensure_ascii=False))


def cmd_stop(args):
    query = f"""
    {{
      stopPlace(id: "{args.stop_id}") {{
        id
        name
        transportMode
        description
        latitude
        longitude
        quays {{
          id
          name
          publicCode
          description
        }}
      }}
    }}
    """
    data = _graphql(query)
    print(json.dumps(data.get("data", {}).get("stopPlace"), indent=2, ensure_ascii=False))


def _resolve_place(text: str) -> dict | None:
    """Resolve a place string to {place: id} or {coordinates: {lat, lon}}."""
    if text.startswith("NSR:"):
        return {"id": text}
    # Try geocoding
    results = _geocode(text, limit=1)
    if not results:
        return None
    r = results[0]
    if r["id"] and r["id"].startswith("NSR:"):
        return {"id": r["id"], "name": r["label"]}
    elif r["coordinates"]:
        return {"coords": r["coordinates"], "name": r["label"]}
    return None


def _place_arg(place: dict) -> str:
    if "id" in place:
        s = f'place: "{place["id"]}"'
    else:
        c = place["coords"]
        s = f'coordinates: {{latitude: {c["lat"]}, longitude: {c["lon"]}}}'
    if "name" in place:
        s += f', name: "{place["name"]}"'
    return s


def main():
    parser = argparse.ArgumentParser(description="Entur public transit API client")
    sub = parser.add_subparsers(dest="command")

    s = sub.add_parser("search", help="Search for stops and places")
    s.add_argument("query")
    s.add_argument("--limit", type=int, default=5)

    t = sub.add_parser("trip", help="Plan a trip")
    t.add_argument("from_place", metavar="from")
    t.add_argument("to_place", metavar="to")
    t.add_argument("--time", help="ISO datetime for departure/arrival")
    t.add_argument("--arrive", action="store_true", help="Time is arrival (not departure)")
    t.add_argument("--modes", help="Comma-separated: bus,rail,tram,metro,water,air,coach")
    t.add_argument("--results", type=int, default=3)

    d = sub.add_parser("departures", help="Departure board")
    d.add_argument("stop_id")
    d.add_argument("--limit", type=int, default=10)

    st = sub.add_parser("stop", help="Stop details")
    st.add_argument("stop_id")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    {"search": cmd_search, "trip": cmd_trip, "departures": cmd_departures, "stop": cmd_stop}[args.command](args)


if __name__ == "__main__":
    main()
