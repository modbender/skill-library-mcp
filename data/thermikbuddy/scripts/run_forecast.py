#!/usr/bin/env python3
"""
run_forecast.py – Segelflug-Thermikvorhersage Hauptscript
Verwendung:
  python3 run_forecast.py --list-regions
  python3 run_forecast.py --region werdenfels [--days 3] [--no-dhv]
  python3 run_forecast.py --lat 47.5 --lon 11.1 --name "Mein Platz" [--days 3]

Gibt JSON auf stdout aus. Logs/Fehler auf stderr.
"""

import argparse
import json
import sys
import os
import math
from datetime import datetime, timedelta

# Füge scripts/ zum Pfad hinzu wenn nötig
sys.path.insert(0, os.path.dirname(__file__))

from fetcher import REGIONS, list_regions, fetch_forecast, fetch_daily_precip_yesterday
from scorer import HourlyData, score_hour, score_day


def parse_args():
    p = argparse.ArgumentParser(description="Segelflug-Thermikvorhersage")
    p.add_argument("--list-regions", action="store_true")
    p.add_argument("--region", type=str, help="Region-ID (siehe --list-regions)")
    p.add_argument("--lat", type=float)
    p.add_argument("--lon", type=float)
    p.add_argument("--name", type=str, default="Eigener Standort")
    p.add_argument("--days", type=int, default=3, choices=range(1, 8))
    p.add_argument("--no-dhv", action="store_true")
    return p.parse_args()


def get_value(hourly: dict, key: str, idx: int, default=0.0) -> float:
    vals = hourly.get(key, [])
    if not vals:
        return default
    if idx < len(vals) and vals[idx] is not None:
        return float(vals[idx])
    return default


def _calculate_uv(speed_kmh, direction_deg):
    """Berechnet U/V Komponenten in m/s aus Speed (km/h) und Direction."""
    if speed_kmh is None or direction_deg is None:
        return 0.0, 0.0
    
    # Umrechnung km/h -> m/s
    speed_ms = speed_kmh / 3.6
    
    # Meteorologische Richtung (woher) in mathematische (wohin) umrechnen
    # Mathe: 0° = Ost, 90° = Nord. Meteo: 0° = Nord, 90° = Ost (im Uhrzeigersinn).
    # U (West-Ost): -sin(dir) * speed
    # V (Süd-Nord): -cos(dir) * speed
    rad = math.radians(direction_deg)
    u = -speed_ms * math.sin(rad)
    v = -speed_ms * math.cos(rad)
    return u, v


def build_hourly_data(hourly: dict, idx: int) -> HourlyData:
    """Erstellt HourlyData aus Open-Meteo Antwort-Index."""
    time_str = hourly["time"][idx]
    hour = int(time_str[11:13])

    # Windwerte holen
    w_speed_10m = get_value(hourly, "wind_speed_10m", idx)
    w_dir_10m = get_value(hourly, "wind_direction_10m", idx)
    w_speed_850 = get_value(hourly, "wind_speed_850hPa", idx)
    w_dir_850 = get_value(hourly, "wind_direction_850hPa", idx)

    # U/V berechnen
    u_10m, v_10m = _calculate_uv(w_speed_10m, w_dir_10m)
    u_850, v_850 = _calculate_uv(w_speed_850, w_dir_850)

    return HourlyData(
        hour=hour,
        temp_2m=get_value(hourly, "temperature_2m", idx),
        dewpoint_2m=get_value(hourly, "dewpoint_2m", idx),
        precip=get_value(hourly, "precipitation", idx),
        
        cloudcover=get_value(hourly, "cloud_cover", idx),
        cloudcover_low=get_value(hourly, "cloud_cover_low", idx),
        cloudcover_mid=get_value(hourly, "cloud_cover_mid", idx),
        
        direct_radiation=get_value(hourly, "direct_radiation", idx),
        
        wind_speed_10m=w_speed_10m,
        wind_dir_10m=w_dir_10m,
        wind_speed_850hpa=w_speed_850,
        wind_dir_850hpa=w_dir_850,
        
        wind_u_10m=u_10m,
        wind_v_10m=v_10m,
        wind_u_850hpa=u_850,
        wind_v_850hpa=v_850,
        
        rh_700hpa=get_value(hourly, "relative_humidity_700hPa", idx, default=40.0),
        rh_850hpa=get_value(hourly, "relative_humidity_850hPa", idx, default=50.0),
        
        cape=get_value(hourly, "cape", idx),
        lifted_index=get_value(hourly, "lifted_index", idx, default=2.0),
        cin=get_value(hourly, "convective_inhibition", idx, default=0.0),
        
        blh=get_value(hourly, "boundary_layer_height", idx),
        soil_moisture=get_value(hourly, "soil_moisture_0_to_1cm", idx, default=0.25),
        
        temp_850hpa=get_value(hourly, "temperature_850hPa", idx),
        temp_700hpa=get_value(hourly, "temperature_700hPa", idx),
    )


def _weekday_de(date_str: str) -> str:
    d = datetime.strptime(date_str, "%Y-%m-%d")
    names = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
    return names[d.weekday()]


def process_forecast(raw: dict, region_cfg: dict, prev_precip: float, days: int) -> list:
    """Verarbeitet Open-Meteo Rohdaten zu tageweisen DailyScore-Dicts."""
    hourly = raw.get("hourly", {})
    times = hourly.get("time", [])

    # Gruppiere nach Datum
    from collections import defaultdict
    by_date = defaultdict(list)
    for i, t in enumerate(times):
        date = t[:10]
        by_date[date].append(i)

    results = []
    # Key 'type' existiert in fetcher.REGIONS, 'terrain_bearing' auch.
    terrain_bearing = region_cfg.get("terrain_bearing", 270)
    region_type = region_cfg.get("type", "alpine")

    for date, indices in sorted(by_date.items()):
        if len(results) >= days:
            break
        hourly_scores = []
        for idx in indices:
            h = build_hourly_data(hourly, idx)
            # Scorer Aufruf
            hr = score_hour(h, prev_precip, terrain_bearing, region_type)
            hourly_scores.append(hr)

        day = score_day(date, hourly_scores, prev_precip)

        results.append({
            "date": day.date,
            "weekday": _weekday_de(day.date),
            "score": day.score,
            "label": day.label,
            "emoji": day.emoji,
            "thermik": {
                "climb_rate_avg": day.avg_climb_rate,
                "cloud_base_msl": day.cloud_base_msl,
                "blh_max": day.blh_max,
                "cape_max": day.cape_max,
            },
            "wind": {
                "avg_kmh": day.wind_avg,
                "shear_avg_kmh": day.wind_shear_avg,
            },
            "warnings": day.warnings,
            "foehn": day.foehn_detected,
            "overdevelopment": day.overdevelopment_risk,
            "ridge_lift_bonus": day.ridge_lift_bonus,
            "phases": day.phases,
        })

    return results


def main():
    args = parse_args()

    if args.list_regions:
        # Hier importieren wir list_regions aus fetcher, das muss klappen
        print(json.dumps(list_regions(), ensure_ascii=False, indent=2))
        return

    # Region auflösen
    region_cfg = None
    lat, lon, name = 0.0, 0.0, ""

    if args.region:
        if args.region not in REGIONS:
            print(json.dumps({"error": f"Unbekannte Region: {args.region}"}))
            sys.exit(1)
        region_cfg = REGIONS[args.region]
        lat, lon = region_cfg["lat"], region_cfg["lon"]
        name = region_cfg["name"]
    elif args.lat and args.lon:
        region_cfg = {
            "name": args.name,
            "type": "alpine",
            "terrain_bearing": 270,
            "elevation_m": 700,
        }
        lat, lon, name = args.lat, args.lon, args.name
    else:
        print(json.dumps({"error": "Bitte --region oder --lat/--lon angeben"}))
        sys.exit(1)

    print(f"[INFO] Rufe Vorhersage ab für {name} ({lat}, {lon})...", file=sys.stderr)

    # Vortages-Niederschlag
    prev_precip = fetch_daily_precip_yesterday(lat, lon)
    print(f"[INFO] Vortages-Niederschlag: {prev_precip} mm", file=sys.stderr)

    # Forecast abrufen
    raw = fetch_forecast(lat, lon, args.days)

    # Verarbeiten
    try:
        days_data = process_forecast(raw, region_cfg, prev_precip, args.days)
    except Exception as e:
        import traceback
        traceback.print_exc(file=sys.stderr)
        print(json.dumps({"error": f"Verarbeitungsfehler: {str(e)}"}), file=sys.stderr)
        sys.exit(1)

    output = {
        "region": name,
        "lat": lat,
        "lon": lon,
        "generated_at": datetime.now().isoformat(),
        # hourly_units existiert in der Antwort evtl nicht mehr exakt so wie früher, checken?
        # OpenMeteo liefert 'hourly_units' meist mit.
        "model": raw.get("hourly_units", {}).get("model", "ICON-D2"), 
        "days": days_data,
        "dhv_available": not args.no_dhv,
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
