#!/usr/bin/env python3
"""BirdWeather CLI — query station data from the BirdWeather API.

No API key required. All data is publicly accessible.
Station IDs can be found at https://app.birdweather.com/

Usage:
    birdweather.py station <station_id>
    birdweather.py species <station_id> [--period day|week|month] [--from YYYY-MM-DD] [--to YYYY-MM-DD] [--limit N]
    birdweather.py detections <station_id> [--species <id>] [--limit N]
    birdweather.py top <station_id> [--period day|week|month] [--limit N]
    birdweather.py compare <station_id> --this <period> --last <period>
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
from datetime import datetime, timedelta

API_BASE = "https://app.birdweather.com/api/v1"
TIMEOUT = 15


def _get(path, params=None):
    """GET request to BirdWeather API."""
    url = f"{API_BASE}{path}"
    if params:
        qs = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
        if qs:
            url += f"?{qs}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"API error: HTTP {e.code}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Request failed: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_station(args):
    """Show station info."""
    data = _get(f"/stations/{args.station_id}")
    print(f"Station: {data.get('name', '?')} (ID: {data.get('id')})")
    print(f"Type: {data.get('type', '?')}")
    print(f"Live: {data.get('live', '?')}")
    coords = data.get("coords", {})
    if coords:
        print(f"Location: {coords.get('lat', '?')}, {coords.get('lon', '?')}")
    latest = data.get("latestDetectionAt")
    if latest:
        print(f"Latest detection: {latest}")


def cmd_species(args):
    """List species detected at a station."""
    params = {"limit": str(args.limit)}
    if args.period:
        params["period"] = args.period
    if args.from_date:
        params["from"] = args.from_date
    if args.to_date:
        params["to"] = args.to_date

    data = _get(f"/stations/{args.station_id}/species", params)
    species = data.get("species", [])

    if not species:
        print("No species detected for this period.")
        return

    if args.json:
        print(json.dumps(species, indent=2))
        return

    for s in species:
        name = s.get("commonName", "?")
        sci = s.get("scientificName", "")
        det = s.get("detections", 0)
        if isinstance(det, dict):
            det = det.get("total", 0)
        print(f"  {det:>5}  {name} ({sci})")

    print(f"\n  {len(species)} species, {sum(s.get('detections', 0) if not isinstance(s.get('detections'), dict) else s['detections'].get('total', 0) for s in species)} total detections")


def cmd_top(args):
    """Show top species for a period (compact output)."""
    params = {"limit": str(args.limit)}
    if args.period:
        params["period"] = args.period

    data = _get(f"/stations/{args.station_id}/species", params)
    species = data.get("species", [])

    if not species:
        print("No detections.")
        return

    total = sum(
        s.get("detections", 0) if not isinstance(s.get("detections"), dict)
        else s["detections"].get("total", 0)
        for s in species
    )
    print(f"{len(species)} species, {total} detections\n")
    for i, s in enumerate(species[:args.limit], 1):
        name = s.get("commonName", "?")
        det = s.get("detections", 0)
        if isinstance(det, dict):
            det = det.get("total", 0)
        print(f"  {i:>2}. {name} ({det})")


def cmd_detections(args):
    """List recent detections."""
    params = {"limit": str(args.limit)}
    if args.species_id:
        params["speciesId"] = args.species_id

    data = _get(f"/stations/{args.station_id}/detections", params)
    detections = data.get("detections", [])

    if not detections:
        print("No recent detections.")
        return

    if args.json:
        print(json.dumps(detections, indent=2))
        return

    for d in detections:
        ts = d.get("timestamp", "?")
        sp = d.get("species", {})
        name = sp.get("commonName", "?")
        conf = d.get("confidence", d.get("score", "?"))
        print(f"  {ts}  {name}  (confidence: {conf})")


def cmd_compare(args):
    """Compare two periods for trend analysis."""
    data_this = _get(f"/stations/{args.station_id}/species", {"period": args.this_period, "limit": "50"})
    data_last = _get(f"/stations/{args.station_id}/species", {"period": args.last_period, "limit": "50"})

    this_sp = {
        s["commonName"]: s.get("detections", 0) if not isinstance(s.get("detections"), dict) else s["detections"].get("total", 0)
        for s in data_this.get("species", [])
    }
    last_sp = {
        s["commonName"]: s.get("detections", 0) if not isinstance(s.get("detections"), dict) else s["detections"].get("total", 0)
        for s in data_last.get("species", [])
    }

    if args.json:
        print(json.dumps({"this_period": this_sp, "last_period": last_sp}, indent=2))
        return

    all_species = sorted(set(list(this_sp.keys()) + list(last_sp.keys())))

    new = [s for s in all_species if s in this_sp and s not in last_sp]
    gone = [s for s in all_species if s not in this_sp and s in last_sp]
    increased = [(s, this_sp[s], last_sp[s]) for s in all_species if s in this_sp and s in last_sp and this_sp[s] > last_sp[s] * 1.5]
    decreased = [(s, this_sp[s], last_sp[s]) for s in all_species if s in this_sp and s in last_sp and this_sp[s] < last_sp[s] * 0.5]

    total_this = sum(this_sp.values())
    total_last = sum(last_sp.values())

    print(f"This period: {len(this_sp)} species, {total_this} detections")
    print(f"Last period: {len(last_sp)} species, {total_last} detections")
    if total_last > 0:
        pct = ((total_this - total_last) / total_last) * 100
        print(f"Change: {pct:+.0f}%")

    if new:
        print(f"\nNew arrivals: {', '.join(new)}")
    if gone:
        print(f"\nNot seen: {', '.join(gone)}")
    if increased:
        print(f"\nIncreasing:")
        for name, now, prev in sorted(increased, key=lambda x: -x[1]):
            print(f"  {name}: {prev} → {now}")
    if decreased:
        print(f"\nDecreasing:")
        for name, now, prev in sorted(decreased, key=lambda x: x[1]):
            print(f"  {name}: {prev} → {now}")


def main():
    parser = argparse.ArgumentParser(description="BirdWeather station data CLI")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    sub = parser.add_subparsers(dest="command", required=True)

    # station
    p = sub.add_parser("station", help="Show station info")
    p.add_argument("station_id", help="BirdWeather station ID")

    # species
    p = sub.add_parser("species", help="List species detected")
    p.add_argument("station_id")
    p.add_argument("--period", choices=["day", "week", "month"], default="day")
    p.add_argument("--from", dest="from_date")
    p.add_argument("--to", dest="to_date")
    p.add_argument("--limit", type=int, default=50)

    # top
    p = sub.add_parser("top", help="Top species (compact)")
    p.add_argument("station_id")
    p.add_argument("--period", choices=["day", "week", "month"], default="week")
    p.add_argument("--limit", type=int, default=10)

    # detections
    p = sub.add_parser("detections", help="Recent detections")
    p.add_argument("station_id")
    p.add_argument("--species", dest="species_id")
    p.add_argument("--limit", type=int, default=20)

    # compare
    p = sub.add_parser("compare", help="Compare two periods")
    p.add_argument("station_id")
    p.add_argument("--this", dest="this_period", default="week", help="Current period")
    p.add_argument("--last", dest="last_period", default="month", help="Previous period")

    args = parser.parse_args()

    commands = {
        "station": cmd_station,
        "species": cmd_species,
        "top": cmd_top,
        "detections": cmd_detections,
        "compare": cmd_compare,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
