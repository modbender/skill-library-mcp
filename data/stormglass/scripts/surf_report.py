#!/usr/bin/env python3
"""
Stormglass surf report CLI.

Purpose:
- Fetch surf-relevant conditions from Stormglass for now and forecast horizons.
- Support both spot-name lookup (Google Geocoding) and direct coordinates.
- Emit stable JSON for cron/downstream-agent pipelines.

Usage examples:
  python scripts/surf_report.py --location "Highcliffe Beach" --horizon 72h --output json
  python scripts/surf_report.py --lat 50.735 --lon -1.705 --horizon 24h --output json
  python scripts/surf_report.py --location "Highcliffe Beach" --horizon now --mock --output pretty

Environment:
  STORMGLASS_API_KEY         Required unless --mock.
  GOOGLE_GEOCODING_API_KEY   Required when --location unless --mock.

Exit codes:
  0 success
  2 invalid CLI usage
  3 missing configuration/API keys
  4 external API failure
  5 parsing/normalization failure
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

WEATHER_ENDPOINT = "https://api.stormglass.io/v2/weather/point"
TIDE_ENDPOINTS = [
    "https://api.stormglass.io/v2/tide/extremes/point",
    "https://api.stormglass.io/v2/tide/extremes",
]
GEOCODE_ENDPOINT = "https://maps.googleapis.com/maps/api/geocode/json"
OSM_GEOCODE_ENDPOINT = "https://nominatim.openstreetmap.org/search"

DEFAULT_SOURCE_ORDER = ["sg", "icon", "gfs", "ecmwf", "dwd", "noaa"]

METRIC_MAP = {
    "waveHeight": "waveHeightM",
    "swellHeight": "swellHeightM",
    "swellPeriod": "swellPeriodS",
    "swellDirection": "swellDirectionDeg",
    "windSpeed": "windSpeedMps",
    "windDirection": "windDirectionDeg",
    "gust": "windGustMps",
    "waterTemperature": "waterTemperatureC",
}

HORIZON_HOURS = {"now": 1, "24h": 24, "48h": 48, "72h": 72}


class ApiError(RuntimeError):
    """Raised for external API errors."""


class ConfigError(RuntimeError):
    """Raised for missing local configuration such as API keys."""


def now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def iso_z(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_time(value: str) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value).astimezone(timezone.utc)


def to_unix_seconds(dt: datetime) -> int:
    return int(dt.astimezone(timezone.utc).timestamp())


def http_get_any_json(url: str, headers: Optional[Dict[str, str]], timeout: int) -> Any:
    req = urllib.request.Request(url=url, headers=headers or {}, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ApiError(f"HTTP {exc.code} for {url}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise ApiError(f"Network error for {url}: {exc}") from exc

    try:
        parsed = json.loads(body)
    except json.JSONDecodeError as exc:
        raise ApiError(f"Invalid JSON from {url}: {exc}") from exc
    return parsed


def http_get_json(url: str, headers: Optional[Dict[str, str]], timeout: int) -> Dict[str, Any]:
    parsed = http_get_any_json(url=url, headers=headers, timeout=timeout)
    if not isinstance(parsed, dict):
        raise ApiError(f"Unexpected payload from {url}; expected JSON object")
    return parsed


def parse_sources(value: Optional[str]) -> List[str]:
    if not value:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


def select_metric_value(raw: Any, source_order: List[str]) -> Optional[float]:
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    if not isinstance(raw, dict):
        return None

    ordered = source_order + [src for src in DEFAULT_SOURCE_ORDER if src not in source_order]
    for key in ordered:
        if key in raw and raw[key] is not None:
            try:
                return float(raw[key])
            except (TypeError, ValueError):
                continue
    for val in raw.values():
        if val is not None:
            try:
                return float(val)
            except (TypeError, ValueError):
                continue
    return None


def geocode_location(address: str, api_key: str, timeout: int) -> Tuple[Dict[str, Any], List[str]]:
    query = urllib.parse.urlencode({"address": address, "key": api_key})
    payload = http_get_json(f"{GEOCODE_ENDPOINT}?{query}", headers=None, timeout=timeout)

    status = payload.get("status")
    if status != "OK":
        err = payload.get("error_message", status)
        raise ApiError(f"Geocoding failed: {err}")

    results = payload.get("results", [])
    if not results:
        raise ApiError("Geocoding returned no results")

    top = results[0]
    geometry = top.get("geometry", {}).get("location", {})
    lat = geometry.get("lat")
    lon = geometry.get("lng")
    if lat is None or lon is None:
        raise ApiError("Geocoding response missing coordinates")

    warnings: List[str] = []
    if len(results) > 1:
        warnings.append("Location query returned multiple matches; top result used.")

    location = {
        "query": address,
        "resolvedName": top.get("formatted_address", address),
        "lat": float(lat),
        "lon": float(lon),
        "googlePlaceId": top.get("place_id"),
    }
    return location, warnings


def geocode_location_osm(address: str, timeout: int) -> Tuple[Dict[str, Any], List[str]]:
    query = urllib.parse.urlencode(
        {
            "q": address,
            "format": "jsonv2",
            "limit": "5",
            "addressdetails": "0",
        }
    )
    payload = http_get_any_json(
        f"{OSM_GEOCODE_ENDPOINT}?{query}",
        headers={"User-Agent": "stormglass-surf-skill/1.0 (+openclaw-cron)"},
        timeout=timeout,
    )
    # Nominatim returns a top-level array; use direct request path here.
    if isinstance(payload, dict):
        # Defensive compatibility if proxy/wrapper returns object.
        results = payload.get("results", [])
    else:
        results = payload
    if not isinstance(results, list) or not results:
        raise ApiError("OSM geocoding returned no results")

    top = results[0]
    try:
        lat = float(top.get("lat"))
        lon = float(top.get("lon"))
    except (TypeError, ValueError) as exc:
        raise ApiError("OSM geocoding response missing valid coordinates") from exc

    warnings: List[str] = [
        "GOOGLE_GEOCODING_API_KEY not set; used OpenStreetMap Nominatim fallback geocoding."
    ]
    if len(results) > 1:
        warnings.append("Location query returned multiple matches; top result used.")

    location = {
        "query": address,
        "resolvedName": top.get("display_name", address),
        "lat": lat,
        "lon": lon,
        "googlePlaceId": None,
    }
    return location, warnings


def fetch_weather(
    lat: float,
    lon: float,
    stormglass_key: str,
    start: datetime,
    end: datetime,
    sources: List[str],
    timeout: int,
) -> List[Dict[str, Any]]:
    params = ",".join(METRIC_MAP.keys())
    query_data = {
        "lat": lat,
        "lng": lon,
        "params": params,
        "start": str(to_unix_seconds(start)),
        "end": str(to_unix_seconds(end)),
    }
    if sources:
        query_data["source"] = ",".join(sources)
    query = urllib.parse.urlencode(query_data)

    payload = http_get_json(
        f"{WEATHER_ENDPOINT}?{query}",
        headers={"Authorization": stormglass_key},
        timeout=timeout,
    )
    hours = payload.get("hours", [])
    if not isinstance(hours, list):
        raise ApiError("Weather response missing hours array")
    return hours


def fetch_tides(
    lat: float,
    lon: float,
    stormglass_key: str,
    start: datetime,
    end: datetime,
    timeout: int,
) -> List[Dict[str, Any]]:
    query = urllib.parse.urlencode(
        {
            "lat": lat,
            "lng": lon,
            "start": start.date().isoformat(),
            "end": end.date().isoformat(),
        }
    )
    last_error: Optional[ApiError] = None
    for endpoint in TIDE_ENDPOINTS:
        try:
            payload = http_get_json(
                f"{endpoint}?{query}",
                headers={"Authorization": stormglass_key},
                timeout=timeout,
            )
            data = payload.get("data", [])
            if isinstance(data, list):
                return data
            raise ApiError("Tide response missing data array")
        except ApiError as exc:
            last_error = exc
    if last_error:
        raise last_error
    return []


def normalize_hour(hour: Dict[str, Any], source_order: List[str]) -> Dict[str, Any]:
    out: Dict[str, Any] = {"time": hour.get("time")}
    for raw_key, out_key in METRIC_MAP.items():
        out[out_key] = select_metric_value(hour.get(raw_key), source_order)
    return out


def nearest_hour(hours: List[Dict[str, Any]], anchor: datetime) -> Dict[str, Any]:
    def distance(hour: Dict[str, Any]) -> float:
        return abs((parse_time(str(hour["time"])) - anchor).total_seconds())

    valid = [h for h in hours if "time" in h]
    if not valid:
        raise ApiError("No weather hours with time field")
    return min(valid, key=distance)


def score_hour(hour: Dict[str, Any]) -> float:
    wave = hour.get("waveHeightM")
    period = hour.get("swellPeriodS")
    wind = hour.get("windSpeedMps")
    gust = hour.get("windGustMps")

    score = 0.0
    if wave is not None:
        score += max(0.0, 1.2 - abs(wave - 1.2))
    if period is not None:
        score += min(2.0, period / 6.0)
    if wind is not None:
        score += max(0.0, 2.0 - wind / 3.0)
    if gust is not None:
        score += max(0.0, 1.5 - gust / 4.0)
    return round(score, 4)


def build_windows(
    normalized_hours: List[Dict[str, Any]],
    anchor: datetime,
    horizon: str,
) -> Dict[str, Any]:
    requested = HORIZON_HOURS[horizon]
    windows: Dict[str, Any] = {}
    for label, hours in [("24h", 24), ("48h", 48), ("72h", 72)]:
        if hours > requested or horizon == "now":
            continue
        end = anchor + timedelta(hours=hours)
        in_window = []
        for h in normalized_hours:
            t = parse_time(str(h["time"]))
            if anchor <= t <= end:
                entry = dict(h)
                entry["score"] = score_hour(h)
                in_window.append(entry)
        top = sorted(in_window, key=lambda x: x["score"], reverse=True)[:3]
        windows[label] = {
            "start": iso_z(anchor),
            "end": iso_z(end),
            "bestHours": top,
        }
    return windows


def normalize_tides(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for item in data:
        t = item.get("time")
        if not t:
            continue
        item_type = item.get("type")
        height = item.get("height")
        try:
            height_value = float(height) if height is not None else None
        except (TypeError, ValueError):
            height_value = None
        out.append({"time": t, "type": item_type, "heightM": height_value})
    out.sort(key=lambda x: x["time"])
    return out


def tide_trend_now(extremes: List[Dict[str, Any]], anchor: datetime) -> str:
    parsed: List[Tuple[datetime, str]] = []
    for e in extremes:
        try:
            parsed.append((parse_time(str(e["time"])), str(e.get("type", "")).lower()))
        except Exception:
            continue
    if not parsed:
        return "unknown"
    prev_item = None
    next_item = None
    for dt, kind in parsed:
        if dt <= anchor:
            prev_item = (dt, kind)
        elif dt > anchor and next_item is None:
            next_item = (dt, kind)
    if prev_item and next_item:
        prev_kind = prev_item[1]
        next_kind = next_item[1]
        if prev_kind == "low" and next_kind == "high":
            return "rising"
        if prev_kind == "high" and next_kind == "low":
            return "falling"
    return "unknown"


def tides_by_day(extremes: List[Dict[str, Any]]) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    out: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
    for e in extremes:
        try:
            day = parse_time(str(e["time"])).date().isoformat()
        except Exception:
            continue
        out.setdefault(day, {"high": [], "low": []})
        kind = str(e.get("type", "")).lower()
        if kind not in ("high", "low"):
            continue
        out[day][kind].append({"time": e["time"], "heightM": e.get("heightM")})
    return out


def mock_payload(
    anchor: datetime, horizon: str, location_mode: str, lat: float, lon: float, location_query: Optional[str]
) -> Dict[str, Any]:
    hours = HORIZON_HOURS[horizon] if horizon != "now" else 24
    normalized_hours: List[Dict[str, Any]] = []
    for i in range(hours + 1):
        t = anchor + timedelta(hours=i)
        normalized_hours.append(
            {
                "time": iso_z(t),
                "waveHeightM": round(0.9 + 0.5 * math.sin(i / 6.0), 2),
                "swellHeightM": round(0.7 + 0.3 * math.cos(i / 7.0), 2),
                "swellPeriodS": round(8.0 + 2.0 * math.sin(i / 8.0), 2),
                "swellDirectionDeg": round(240 + 15 * math.cos(i / 12.0), 1),
                "windSpeedMps": round(4.0 + 2.0 * math.sin(i / 5.0), 2),
                "windDirectionDeg": round(210 + 25 * math.cos(i / 9.0), 1),
                "windGustMps": round(6.0 + 2.5 * math.sin(i / 5.0), 2),
                "waterTemperatureC": round(10.5 + 0.8 * math.sin(i / 24.0), 2),
            }
        )

    extremes: List[Dict[str, Any]] = []
    ext_count = max(6, int((HORIZON_HOURS.get(horizon, 72) / 6) + 2))
    kind = "low"
    for i in range(ext_count):
        t = anchor + timedelta(hours=i * 6)
        kind = "high" if kind == "low" else "low"
        extremes.append(
            {
                "time": iso_z(t),
                "type": kind,
                "heightM": round(1.0 + (0.8 if kind == "high" else -0.3), 2),
            }
        )

    nearest = nearest_hour(normalized_hours, anchor)
    return {
        "meta": {
            "generatedAt": iso_z(anchor),
            "horizon": horizon,
            "inputMode": location_mode,
            "sourcesRequested": [],
            "warnings": ["Mock mode enabled: no external API calls were made."],
        },
        "location": {
            "query": location_query,
            "resolvedName": location_query if location_query else f"{lat},{lon}",
            "lat": lat,
            "lon": lon,
            "googlePlaceId": None,
        },
        "now": nearest,
        "forecast": {"windows": build_windows(normalized_hours, anchor, horizon)},
        "tides": {
            "trendNow": tide_trend_now(extremes, anchor),
            "extremes": extremes,
            "byDay": tides_by_day(extremes),
        },
    }


def build_report(args: argparse.Namespace) -> Dict[str, Any]:
    anchor = now_utc()
    sources = parse_sources(args.source)
    warnings: List[str] = []

    if args.location:
        mode = "location"
        location_query = args.location
    else:
        mode = "coordinates"
        location_query = None

    lat: float
    lon: float
    location: Dict[str, Any]

    if args.mock:
        lat = args.lat if args.lat is not None else 50.735
        lon = args.lon if args.lon is not None else -1.705
        return mock_payload(anchor, args.horizon, mode, lat, lon, location_query)

    stormglass_key = os.environ.get("STORMGLASS_API_KEY")
    if not stormglass_key:
        raise ConfigError("Missing STORMGLASS_API_KEY environment variable.")

    if args.location:
        geocode_key = os.environ.get("GOOGLE_GEOCODING_API_KEY")
        if geocode_key:
            location, geo_warnings = geocode_location(args.location, geocode_key, args.timeout)
        else:
            location, geo_warnings = geocode_location_osm(args.location, args.timeout)
        warnings.extend(geo_warnings)
        lat = location["lat"]
        lon = location["lon"]
    else:
        lat = float(args.lat)
        lon = float(args.lon)
        location = {
            "query": None,
            "resolvedName": f"{lat},{lon}",
            "lat": lat,
            "lon": lon,
            "googlePlaceId": None,
        }

    end = anchor + timedelta(hours=HORIZON_HOURS[args.horizon])
    weather_hours = fetch_weather(lat, lon, stormglass_key, anchor, end, sources, args.timeout)
    tide_data = fetch_tides(lat, lon, stormglass_key, anchor, end + timedelta(days=1), args.timeout)

    source_order = sources[:] if sources else []
    normalized = [normalize_hour(hour, source_order) for hour in weather_hours if "time" in hour]
    if not normalized:
        raise ApiError("No weather data points returned")

    current = nearest_hour(normalized, anchor)
    extremes = normalize_tides(tide_data)

    return {
        "meta": {
            "generatedAt": iso_z(anchor),
            "horizon": args.horizon,
            "inputMode": mode,
            "sourcesRequested": sources,
            "warnings": warnings,
        },
        "location": location,
        "now": current,
        "forecast": {"windows": build_windows(normalized, anchor, args.horizon)},
        "tides": {
            "trendNow": tide_trend_now(extremes, anchor),
            "extremes": extremes,
            "byDay": tides_by_day(extremes),
        },
    }


def to_pretty(report: Dict[str, Any]) -> str:
    now = report.get("now", {})
    location = report.get("location", {})
    lines = [
        f"Surf report for: {location.get('resolvedName')}",
        f"Generated: {report.get('meta', {}).get('generatedAt')}",
        "",
        "Now:",
        f"  Wave: {now.get('waveHeightM')} m",
        f"  Swell: {now.get('swellHeightM')} m @ {now.get('swellPeriodS')} s ({now.get('swellDirectionDeg')} deg)",
        f"  Wind: {now.get('windSpeedMps')} m/s gust {now.get('windGustMps')} m/s ({now.get('windDirectionDeg')} deg)",
        f"  Water temp: {now.get('waterTemperatureC')} C",
        f"  Tide trend: {report.get('tides', {}).get('trendNow')}",
    ]
    windows = report.get("forecast", {}).get("windows", {})
    if windows:
        lines.append("")
        lines.append("Best windows:")
        for label, data in windows.items():
            best = data.get("bestHours", [])
            if not best:
                continue
            top = best[0]
            lines.append(
                f"  {label}: {top.get('time')} (score {top.get('score')}, "
                f"wave {top.get('waveHeightM')} m, period {top.get('swellPeriodS')} s)"
            )
    return "\n".join(lines)


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch surf-relevant Stormglass data by location or coordinates.")
    parser.add_argument("--location", help="Surf spot/place name for geocoding lookup.")
    parser.add_argument("--lat", type=float, help="Latitude for direct coordinate mode.")
    parser.add_argument("--lon", type=float, help="Longitude for direct coordinate mode.")
    parser.add_argument("--horizon", choices=["now", "24h", "48h", "72h"], default="72h")
    parser.add_argument("--output", choices=["json", "pretty"], default="json")
    parser.add_argument("--source", help="Optional comma-separated Stormglass sources.")
    parser.add_argument("--timeout", type=int, default=20, help="HTTP timeout seconds.")
    parser.add_argument("--mock", action="store_true", help="Use deterministic offline mock data.")

    args = parser.parse_args(argv)

    has_location = bool(args.location)
    has_coords = args.lat is not None or args.lon is not None
    if has_location and has_coords:
        parser.error("Use either --location or --lat/--lon, not both.")
    if not has_location and not has_coords:
        parser.error("Provide --location or both --lat and --lon.")
    if has_coords and (args.lat is None or args.lon is None):
        parser.error("Both --lat and --lon are required for coordinate mode.")
    return args


def main(argv: List[str]) -> int:
    try:
        args = parse_args(argv)
        report = build_report(args)
        if args.output == "json":
            print(json.dumps(report, ensure_ascii=True, sort_keys=True))
        else:
            print(to_pretty(report))
        return 0
    except SystemExit as exc:
        if isinstance(exc.code, int):
            if exc.code in (0, 2, 3):
                return exc.code
            return 2
        return 2
    except ApiError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 4
    except ConfigError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 3
    except Exception as exc:  # pragma: no cover - safety catch for cron robustness
        print(f"ERROR: {exc}", file=sys.stderr)
        return 5


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
