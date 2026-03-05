#!/usr/bin/env python3
"""Deutsche Bahn / European transit API client via v6.db.transport.rest.

Covers Germany + international trains (ICE, IC, EC, regional, S-Bahn, buses, ferries, trams).

Usage:
  db-travel.py search <query>                       Search for stops/stations
  db-travel.py trip <from> <to> [--time ISO] [--arrive] [--results N]
  db-travel.py departures <stop_id> [--duration M]  Departure board
  db-travel.py arrivals <stop_id> [--duration M]    Arrival board
  db-travel.py stop <stop_id>                       Stop details

All output is JSON.
"""

import argparse
import json
import sys
import urllib.request
import urllib.parse

BASE = "https://v6.db.transport.rest"


def _get(path: str, params: dict | None = None) -> dict | list:
    url = f"{BASE}{path}"
    if params:
        # Filter None values
        params = {k: v for k, v in params.items() if v is not None}
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def cmd_search(args):
    results = _get("/locations", {"query": args.query, "results": args.limit or 5})
    out = []
    for r in results:
        loc = r.get("location", {})
        out.append({
            "id": r.get("id"),
            "name": r.get("name"),
            "type": r.get("type"),
            "lat": loc.get("latitude"),
            "lon": loc.get("longitude"),
        })
    print(json.dumps(out, indent=2, ensure_ascii=False))


def cmd_trip(args):
    from_loc = _resolve(args.from_place)
    to_loc = _resolve(args.to_place)

    if not from_loc or not to_loc:
        print(json.dumps({"error": "Could not resolve origin or destination"}))
        sys.exit(1)

    params = {
        "from": from_loc["id"] if "id" in from_loc else None,
        "from.latitude": from_loc.get("lat"),
        "from.longitude": from_loc.get("lon"),
        "from.name": from_loc.get("name"),
        "to": to_loc["id"] if "id" in to_loc else None,
        "to.latitude": to_loc.get("lat"),
        "to.longitude": to_loc.get("lon"),
        "to.name": to_loc.get("name"),
        "results": args.results or 3,
        "stopovers": "false",
        "language": "en",
    }

    if args.time:
        if args.arrive:
            params["arrival"] = args.time
        else:
            params["departure"] = args.time

    data = _get("/journeys", params)
    journeys = data.get("journeys", [])

    trips = []
    for j in journeys:
        legs = []
        for leg in j.get("legs", []):
            leg_info = {
                "mode": leg.get("line", {}).get("mode") or leg.get("walking") and "walk" or "transfer",
                "from": leg.get("origin", {}).get("name"),
                "to": leg.get("destination", {}).get("name"),
                "depart": leg.get("departure"),
                "arrive": leg.get("arrival"),
            }
            if leg.get("line"):
                leg_info["line"] = leg["line"].get("name")
                leg_info["product"] = leg["line"].get("product")
                leg_info["operator"] = leg["line"].get("operator", {}).get("name") if leg["line"].get("operator") else None
            if leg.get("departurePlatform"):
                leg_info["platform"] = leg["departurePlatform"]
            if leg.get("departureDelay") and leg["departureDelay"] != 0:
                leg_info["delay_min"] = leg["departureDelay"] // 60
            if leg.get("walking"):
                leg_info["mode"] = "walk"
                if leg.get("distance"):
                    leg_info["distance_m"] = leg["distance"]
            legs.append(leg_info)

        trips.append({
            "legs": legs,
        })

    print(json.dumps(trips, indent=2, ensure_ascii=False))


def cmd_departures(args):
    params = {
        "duration": args.duration or 30,
        "results": args.limit or 10,
        "language": "en",
    }
    data = _get(f"/stops/{args.stop_id}/departures", params)
    
    deps = []
    for d in data.get("departures", data) if isinstance(data, dict) else data:
        line = d.get("line", {})
        deps.append({
            "line": line.get("name"),
            "product": line.get("product"),
            "direction": d.get("direction"),
            "planned": d.get("plannedWhen"),
            "expected": d.get("when"),
            "delay_min": (d.get("delay") or 0) // 60 if d.get("delay") else 0,
            "platform": d.get("platform"),
            "operator": line.get("operator", {}).get("name") if line.get("operator") else None,
        })

    print(json.dumps(deps, indent=2, ensure_ascii=False))


def cmd_arrivals(args):
    params = {
        "duration": args.duration or 30,
        "results": args.limit or 10,
        "language": "en",
    }
    data = _get(f"/stops/{args.stop_id}/arrivals", params)

    arrs = []
    for a in data.get("arrivals", data) if isinstance(data, dict) else data:
        line = a.get("line", {})
        arrs.append({
            "line": line.get("name"),
            "product": line.get("product"),
            "origin": a.get("provenance") or a.get("origin", {}).get("name"),
            "planned": a.get("plannedWhen"),
            "expected": a.get("when"),
            "delay_min": (a.get("delay") or 0) // 60 if a.get("delay") else 0,
            "platform": a.get("platform"),
        })

    print(json.dumps(arrs, indent=2, ensure_ascii=False))


def cmd_stop(args):
    data = _get(f"/stops/{args.stop_id}", {"language": "en"})
    print(json.dumps(data, indent=2, ensure_ascii=False))


def _resolve(text: str) -> dict | None:
    """Resolve a place string to {id, name} or {lat, lon, name}."""
    # If it's a numeric ID, use directly
    if text.isdigit():
        return {"id": text}
    # Geocode
    results = _get("/locations", {"query": text, "results": 1})
    if not results:
        return None
    r = results[0]
    loc = r.get("location", {})
    if r.get("id"):
        return {"id": r["id"], "name": r.get("name")}
    elif loc.get("latitude"):
        return {"lat": loc["latitude"], "lon": loc["longitude"], "name": r.get("name")}
    return None


def main():
    parser = argparse.ArgumentParser(description="Deutsche Bahn / European transit API client")
    sub = parser.add_subparsers(dest="command")

    s = sub.add_parser("search", help="Search for stops/stations")
    s.add_argument("query")
    s.add_argument("--limit", type=int, default=5)

    t = sub.add_parser("trip", help="Plan a journey")
    t.add_argument("from_place", metavar="from")
    t.add_argument("to_place", metavar="to")
    t.add_argument("--time", help="ISO datetime for departure/arrival")
    t.add_argument("--arrive", action="store_true", help="Time is arrival time")
    t.add_argument("--results", type=int, default=3)

    d = sub.add_parser("departures", help="Departure board")
    d.add_argument("stop_id")
    d.add_argument("--duration", type=int, default=30, help="Minutes to look ahead")
    d.add_argument("--limit", type=int, default=10)

    a = sub.add_parser("arrivals", help="Arrival board")
    a.add_argument("stop_id")
    a.add_argument("--duration", type=int, default=30)
    a.add_argument("--limit", type=int, default=10)

    st = sub.add_parser("stop", help="Stop details")
    st.add_argument("stop_id")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    cmds = {"search": cmd_search, "trip": cmd_trip, "departures": cmd_departures, "arrivals": cmd_arrivals, "stop": cmd_stop}
    cmds[args.command](args)


if __name__ == "__main__":
    main()
