#!/usr/bin/env python3
"""
CLI helper for the Linz Linien EFA API.

Endpoints used:
- GET /efa/XML_STOPFINDER_REQUEST
- GET /efa/XML_DM_REQUEST
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

DEFAULT_BASE_URL = "http://www.linzag.at/linz2"


def build_url(base_url: str, path: str) -> str:
    base = base_url.rstrip("/")
    return f"{base}/{path.lstrip('/')}"


def http_get_json(url: str, timeout: int) -> Any:
    req = urllib.request.Request(url=url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)
    except urllib.error.HTTPError as err:
        raise RuntimeError(f"HTTP {err.code} for {url}") from err
    except urllib.error.URLError as err:
        raise RuntimeError(f"Network error for {url}: {err.reason}") from err
    except json.JSONDecodeError as err:
        raise RuntimeError(f"Invalid JSON from {url}: {err}") from err


def query_efa(base_url: str, endpoint: str, params: dict[str, Any], timeout: int) -> dict[str, Any]:
    query = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    url = build_url(base_url, f"/efa/{endpoint}?{query}")
    payload = http_get_json(url, timeout)
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object from {endpoint}")
    return payload


def parse_message_code(message: Any) -> str | None:
    if not isinstance(message, list):
        return None
    for item in message:
        if isinstance(item, dict) and item.get("name") == "code":
            value = item.get("value")
            if value is None:
                return None
            return str(value)
    return None


def normalize_points(points: Any) -> list[dict[str, Any]]:
    if isinstance(points, list):
        return [x for x in points if isinstance(x, dict)]
    if isinstance(points, dict):
        point = points.get("point")
        if isinstance(point, list):
            return [x for x in point if isinstance(x, dict)]
        if isinstance(point, dict):
            return [point]
        return [points]
    return []


def reduce_stop(point: dict[str, Any]) -> dict[str, Any]:
    ref = point.get("ref")
    if not isinstance(ref, dict):
        ref = {}
    stop_id = point.get("stateless") or ref.get("id")
    return {
        "id": str(stop_id) if stop_id is not None else None,
        "name": point.get("name"),
        "type": point.get("anyType") or point.get("type"),
        "best": point.get("best"),
        "quality": point.get("quality"),
        "place": ref.get("place"),
        "coords": ref.get("coords"),
    }


def get_stops(base_url: str, name: str, timeout: int) -> list[dict[str, Any]]:
    payload = query_efa(
        base_url=base_url,
        endpoint="XML_STOPFINDER_REQUEST",
        params={
            "locationServerActive": 1,
            "outputFormat": "JSON",
            "type_sf": "any",
            "name_sf": name,
        },
        timeout=timeout,
    )
    stop_finder = payload.get("stopFinder")
    if not isinstance(stop_finder, dict):
        raise RuntimeError("Missing stopFinder in response")

    message_code = parse_message_code(stop_finder.get("message"))
    points = normalize_points(stop_finder.get("points"))
    reduced = [reduce_stop(p) for p in points]
    reduced = [s for s in reduced if s.get("id") and s.get("type") == "stop"]

    if not reduced and message_code == "-8020":
        return []
    return reduced


def normalize_departures(departure_list: Any) -> list[dict[str, Any]]:
    if isinstance(departure_list, list):
        items = departure_list
    elif isinstance(departure_list, dict):
        dep = departure_list.get("departure")
        if isinstance(dep, list):
            items = dep
        elif isinstance(dep, dict):
            items = [dep]
        else:
            items = []
    else:
        items = []
    return [x for x in items if isinstance(x, dict)]


def to_iso_time(date_time: Any) -> str | None:
    if not isinstance(date_time, dict):
        return None
    year = date_time.get("year")
    month = date_time.get("month")
    day = date_time.get("day")
    hour = date_time.get("hour")
    minute = date_time.get("minute")
    fields = [year, month, day, hour, minute]
    if any(v is None for v in fields):
        return None
    try:
        return f"{int(year):04d}-{int(month):02d}-{int(day):02d}T{int(hour):02d}:{int(minute):02d}:00"
    except (TypeError, ValueError):
        return None


def normalize_countdown(value: Any) -> int | None:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return None


def get_departures(base_url: str, stop_id: str, limit: int, timeout: int) -> list[dict[str, Any]]:
    payload = query_efa(
        base_url=base_url,
        endpoint="XML_DM_REQUEST",
        params={
            "locationServerActive": 1,
            "stateless": 1,
            "outputFormat": "JSON",
            "type_dm": "any",
            "name_dm": stop_id,
            "mode": "direct",
            "limit": limit,
        },
        timeout=timeout,
    )

    dm = payload.get("dm")
    if isinstance(dm, dict):
        message_code = parse_message_code(dm.get("message"))
        if message_code == "-8020":
            raise RuntimeError(f"Stop id '{stop_id}' not found")

    raw_departures = normalize_departures(payload.get("departureList"))
    result = []
    for item in raw_departures:
        serving_line = item.get("servingLine")
        if not isinstance(serving_line, dict):
            serving_line = {}

        planned = to_iso_time(item.get("dateTime"))
        realtime = to_iso_time(item.get("realDateTime"))
        countdown = normalize_countdown(item.get("countdown"))
        result.append(
            {
                "countdownInMinutes": countdown,
                "time": realtime or planned,
                "line": {
                    "number": serving_line.get("number"),
                    "direction": serving_line.get("direction"),
                    "initialOriginStopName": serving_line.get("directionFrom"),
                    "type": serving_line.get("motType"),
                },
                "platform": item.get("platform"),
                "stopName": item.get("stopName"),
                "realtimeTripStatus": item.get("realtimeTripStatus"),
            }
        )
    return result


def stop_name_candidates(name: Any) -> list[str]:
    if not isinstance(name, str):
        return []
    parts = [x.strip() for x in name.split(",") if x.strip()]
    short = parts[-1] if parts else name
    return [name.strip(), short.strip()]


def is_exact_stop_match(stop_name: Any, query: str) -> bool:
    q = query.casefold().strip()
    for candidate in stop_name_candidates(stop_name):
        if candidate.casefold() == q:
            return True
    return False


def is_prefix_stop_match(stop_name: Any, query: str) -> bool:
    q = query.casefold().strip()
    for candidate in stop_name_candidates(stop_name):
        if candidate.casefold().startswith(q):
            return True
    return False


def pick_stop(stops: list[dict[str, Any]], name: str, pick_first: bool) -> dict[str, Any]:
    if not stops:
        raise RuntimeError(f"No stops found for '{name}'")

    exact = []
    prefix = []
    for stop in stops:
        stop_name = stop.get("name")
        if is_exact_stop_match(stop_name, name):
            exact.append(stop)
        elif is_prefix_stop_match(stop_name, name):
            prefix.append(stop)

    if len(exact) == 1:
        return exact[0]
    if len(exact) > 1 and not pick_first:
        raise RuntimeError(
            "Multiple exact stop matches found. Re-run with --pick-first or pick stopId explicitly."
        )

    if len(prefix) == 1:
        return prefix[0]

    if len(stops) > 1 and not pick_first and not exact and not prefix:
        raise RuntimeError(
            "Multiple stop matches found. Re-run with --pick-first or use departures with --stop-id."
        )

    if exact:
        return exact[0]
    if prefix:
        return prefix[0]
    return stops[0]


def cmd_stops(args: argparse.Namespace) -> dict[str, Any]:
    stops = get_stops(args.base_url, args.name, args.timeout)
    return {"query": args.name, "count": len(stops), "stops": stops}


def cmd_departures(args: argparse.Namespace) -> dict[str, Any]:
    departures = get_departures(args.base_url, args.stop_id, args.limit, args.timeout)
    departures.sort(key=lambda d: (d.get("countdownInMinutes") is None, d.get("countdownInMinutes")))
    return {"stopId": args.stop_id, "count": len(departures), "departures": departures}


def cmd_next(args: argparse.Namespace) -> dict[str, Any]:
    stops = get_stops(args.base_url, args.name, args.timeout)
    selected = pick_stop(stops, args.name, args.pick_first)
    stop_id = str(selected.get("id", ""))
    if not stop_id:
        raise RuntimeError("Selected stop has no id")

    departures = get_departures(args.base_url, stop_id, args.limit, args.timeout)
    departures.sort(key=lambda d: (d.get("countdownInMinutes") is None, d.get("countdownInMinutes")))

    return {
        "query": args.name,
        "selectedStop": {"id": stop_id, "name": selected.get("name")},
        "count": len(departures),
        "departures": departures,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Linz Linien EFA API CLI helper.")
    parser.add_argument(
        "--base-url",
        default=os.environ.get("LINZ_TRANSPORT_API_BASE_URL", DEFAULT_BASE_URL),
        help=(
            "API base URL. Defaults to LINZ_TRANSPORT_API_BASE_URL or "
            f"{DEFAULT_BASE_URL}."
        ),
    )
    parser.add_argument("--timeout", type=int, default=15, help="HTTP timeout in seconds (default: 15).")

    sub = parser.add_subparsers(dest="command", required=True)

    stops_p = sub.add_parser("stops", help="Search stops by name.")
    stops_p.add_argument("name", help="Stop name token to search.")
    stops_p.set_defaults(handler=cmd_stops)

    dep_p = sub.add_parser("departures", help="Fetch departures for a stop id.")
    dep_p.add_argument("--stop-id", required=True, help="Stop id.")
    dep_p.add_argument("--limit", type=int, default=10, help="Max departures to return (default: 10).")
    dep_p.set_defaults(handler=cmd_departures)

    next_p = sub.add_parser("next", help="Resolve stop by name and fetch departures.")
    next_p.add_argument("name", help="Stop name token.")
    next_p.add_argument("--limit", type=int, default=10, help="Max departures to return (default: 10).")
    next_p.add_argument(
        "--pick-first",
        action="store_true",
        help="Pick first stop match when multiple matches exist.",
    )
    next_p.set_defaults(handler=cmd_next)

    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    try:
        args = parse_args(argv)
        result = args.handler(args)
        print(json.dumps(result, ensure_ascii=True, indent=2))
        return 0
    except RuntimeError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
