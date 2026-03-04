#!/usr/bin/env python3
"""
fetch_tempest.py — Fetch and normalize latest observation from a Tempest weather station.

Usage:
    python3 fetch_tempest.py --token YOUR_TOKEN --station 12345
    python3 fetch_tempest.py --token YOUR_TOKEN --station 12345 --pretty

Environment variables (alternative to flags):
    TEMPEST_TOKEN
    TEMPEST_STATION_ID
"""

import argparse
import json
import math
import os
import sys
from datetime import datetime, timezone

try:
    import requests
except ImportError:
    print(json.dumps({"error": "Missing dependency: pip install requests"}))
    sys.exit(1)

BASE_URL = "https://swd.weatherflow.com/swd/rest"


def deg_to_cardinal(deg):
    if deg is None:
        return None
    dirs = ["N","NNE","NE","ENE","E","ESE","SE","SSE",
            "S","SSW","SW","WSW","W","WNW","NW","NNW"]
    ix = round(deg / 22.5) % 16
    return dirs[ix]


def c_to_f(c):
    if c is None:
        return None
    return round((c * 9 / 5) + 32, 1)


def ms_to_mph(ms):
    if ms is None:
        return None
    return round(ms * 2.237, 1)


PRECIP_TYPES = {0: "none", 1: "rain", 2: "hail"}
PRECIP_ANALYSIS = {0: "none", 1: "rain_check_on", 2: "rain_check_off"}


def fetch_observation(token, station_id):
    url = f"{BASE_URL}/observations/station/{station_id}"
    resp = requests.get(url, params={"token": token}, timeout=10)
    
    if resp.status_code == 401:
        return {"error": "Invalid API token (401). Check your token at tempestwx.com."}
    if resp.status_code == 403:
        return {"error": f"Token does not have access to station {station_id} (403)."}
    if resp.status_code == 404:
        return {"error": f"Station {station_id} not found (404). Check your station ID."}
    
    resp.raise_for_status()
    data = resp.json()
    
    if data.get("status", {}).get("status_code") != 0:
        msg = data.get("status", {}).get("status_message", "Unknown error")
        return {"error": f"API error: {msg}"}
    
    obs_list = data.get("obs", [])
    if not obs_list:
        return {
            "error": "No recent observations available. The station may be offline.",
            "station_id": data.get("station_id"),
            "station_name": data.get("station_name")
        }
    
    obs = obs_list[0]  # Most recent observation
    
    ts = obs.get("timestamp")
    ts_iso = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat() if ts else None
    
    return {
        "station_id": data.get("station_id"),
        "station_name": data.get("station_name") or data.get("public_name"),
        "latitude": data.get("latitude"),
        "longitude": data.get("longitude"),
        "timezone": data.get("timezone"),
        "elevation_m": data.get("elevation"),
        "timestamp": ts_iso,
        "timestamp_epoch": ts,
        "conditions": {
            "temperature_c": obs.get("air_temperature"),
            "temperature_f": c_to_f(obs.get("air_temperature")),
            "humidity_pct": obs.get("relative_humidity"),
            "pressure_mb": obs.get("station_pressure"),
            "sea_level_pressure_mb": obs.get("sea_level_pressure"),
            "pressure_trend": obs.get("pressure_trend"),
            "feels_like_c": obs.get("feels_like"),
            "feels_like_f": c_to_f(obs.get("feels_like")),
            "dew_point_c": obs.get("dew_point"),
            "dew_point_f": c_to_f(obs.get("dew_point")),
            "wet_bulb_temperature_c": obs.get("wet_bulb_temperature"),
            "air_density_kgm3": obs.get("air_density"),
        },
        "wind": {
            "speed_avg_ms": obs.get("wind_avg"),
            "speed_avg_mph": ms_to_mph(obs.get("wind_avg")),
            "speed_lull_ms": obs.get("wind_lull"),
            "speed_lull_mph": ms_to_mph(obs.get("wind_lull")),
            "speed_gust_ms": obs.get("wind_gust"),
            "speed_gust_mph": ms_to_mph(obs.get("wind_gust")),
            "direction_deg": obs.get("wind_direction"),
            "direction_cardinal": deg_to_cardinal(obs.get("wind_direction")),
            "sample_interval_sec": obs.get("wind_sample_interval"),
        },
        "precipitation": {
            "rain_last_1hr_mm": obs.get("precip_accum_last_1hr"),
            "rain_daily_mm": obs.get("precip_accum_local_day"),
            "rain_yesterday_mm": obs.get("precip_accum_local_yesterday"),
            "rain_minutes_today": obs.get("precip_minutes_local_day"),
            "precip_type": PRECIP_TYPES.get(obs.get("precip_type"), "unknown"),
            "precip_analysis": PRECIP_ANALYSIS.get(obs.get("precip_analysis_type_filtered"), "unknown"),
        },
        "lightning": {
            "strike_count_interval": obs.get("lightning_strike_count"),
            "strike_count_last_1hr": obs.get("lightning_strike_count_last_1hr"),
            "strike_count_last_3hr": obs.get("lightning_strike_count_last_3hr"),
            "last_strike_epoch": obs.get("lightning_strike_last_epoch"),
            "last_strike_distance_km": obs.get("lightning_strike_last_distance"),
        },
        "solar": {
            "uv_index": obs.get("uv"),
            "solar_radiation_wm2": obs.get("solar_radiation"),
            "illuminance_lux": obs.get("illuminance"),
        },
        "battery_volts": obs.get("battery"),
        "report_interval_min": obs.get("report_interval"),
        "data_source": "tempest_rest_api"
    }


def main():
    parser = argparse.ArgumentParser(description="Fetch Tempest weather station data")
    parser.add_argument("--token", default=os.environ.get("TEMPEST_TOKEN"), help="API token")
    parser.add_argument("--station", default=os.environ.get("TEMPEST_STATION_ID"), help="Station ID")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args()

    if not args.token:
        print(json.dumps({"error": "Missing --token or TEMPEST_TOKEN env var"}))
        sys.exit(1)
    if not args.station:
        print(json.dumps({"error": "Missing --station or TEMPEST_STATION_ID env var"}))
        sys.exit(1)

    result = fetch_observation(args.token, args.station)
    indent = 2 if args.pretty else None
    print(json.dumps(result, indent=indent))


if __name__ == "__main__":
    main()
