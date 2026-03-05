#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import os
import pathlib
import sys
import time
from urllib import error, parse, request

API_BASE = "https://swd.weatherflow.com/swd/rest"


def c_to_f(c):
    return (c * 9.0 / 5.0) + 32.0


def ms_to_mph(ms):
    return ms * 2.2369362921


def mb_to_inhg(mb):
    return mb * 0.0295299830714


def mm_to_in(mm):
    return mm * 0.03937007874


def deg_to_cardinal(deg):
    if deg is None:
        return None
    dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    idx = int((deg % 360) / 22.5 + 0.5) % 16
    return dirs[idx]


def read_version_from_skill_md():
    try:
        skill_md = pathlib.Path(__file__).resolve().parent.parent / "SKILL.md"
        text = skill_md.read_text(encoding="utf-8")
    except Exception:
        return None

    if not text.startswith("---"):
        return None

    parts = text.split("---", 2)
    if len(parts) < 3:
        return None

    frontmatter = parts[1]
    for line in frontmatter.splitlines():
        stripped = line.strip()
        if stripped.startswith("version:"):
            value = stripped.split(":", 1)[1].strip().strip('"').strip("'")
            return value or None
    return None


def detect_version():
    # Read SKILL.md frontmatter version when available
    return read_version_from_skill_md()


def build_user_agent():
    version = detect_version()
    if version:
        return f"openclaw-tempest-skill/{version}"
    return "openclaw-tempest-skill"


def get_json(url, retries=1, timeout=20):
    last_err = None
    for attempt in range(retries + 1):
        try:
            req = request.Request(url, headers={"User-Agent": build_user_agent()})
            with request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            last_err = e
            if attempt < retries:
                time.sleep(0.8)
    raise last_err


def parse_obs(obs):
    # Tempest obs index mapping (obs array)
    return {
        "timestamp_epoch": obs[0] if len(obs) > 0 else None,
        "wind_lull_mps": obs[1] if len(obs) > 1 else None,
        "wind_avg_mps": obs[2] if len(obs) > 2 else None,
        "wind_gust_mps": obs[3] if len(obs) > 3 else None,
        "wind_direction_deg": obs[4] if len(obs) > 4 else None,
        "station_pressure_mb": obs[6] if len(obs) > 6 else None,
        "air_temp_c": obs[7] if len(obs) > 7 else None,
        "relative_humidity_pct": obs[8] if len(obs) > 8 else None,
        "illuminance_lux": obs[9] if len(obs) > 9 else None,
        "uv_index": obs[10] if len(obs) > 10 else None,
        "solar_radiation_wpm2": obs[11] if len(obs) > 11 else None,
        "rain_accumulated_mm_last_interval": obs[12] if len(obs) > 12 else None,
        "precip_type": obs[13] if len(obs) > 13 else None,
        "lightning_avg_distance_km": obs[14] if len(obs) > 14 else None,
        "lightning_strike_count_last_interval": obs[15] if len(obs) > 15 else None,
        "battery_v": obs[16] if len(obs) > 16 else None,
        "report_interval_min": obs[17] if len(obs) > 17 else None,
        "local_daily_rain_mm": obs[18] if len(obs) > 18 else None,
    }


def convert_units(parsed, units):
    if units == "metric":
        out = dict(parsed)
        out["units"] = {
            "temperature": "C",
            "wind": "m/s",
            "pressure": "mb",
            "rain": "mm",
            "lightning_distance": "km",
        }
        return out

    out = dict(parsed)
    if out.get("air_temp_c") is not None:
        out["air_temp_f"] = round(c_to_f(out["air_temp_c"]), 1)
    if out.get("wind_lull_mps") is not None:
        out["wind_lull_mph"] = round(ms_to_mph(out["wind_lull_mps"]), 1)
    if out.get("wind_avg_mps") is not None:
        out["wind_avg_mph"] = round(ms_to_mph(out["wind_avg_mps"]), 1)
    if out.get("wind_gust_mps") is not None:
        out["wind_gust_mph"] = round(ms_to_mph(out["wind_gust_mps"]), 1)
    if out.get("station_pressure_mb") is not None:
        out["station_pressure_inhg"] = round(mb_to_inhg(out["station_pressure_mb"]), 3)
    if out.get("rain_accumulated_mm_last_interval") is not None:
        out["rain_accumulated_in_last_interval"] = round(mm_to_in(out["rain_accumulated_mm_last_interval"]), 3)
    if out.get("local_daily_rain_mm") is not None:
        out["local_daily_rain_in"] = round(mm_to_in(out["local_daily_rain_mm"]), 3)

    if out.get("wind_direction_deg") is not None:
        out["wind_direction_cardinal"] = deg_to_cardinal(out["wind_direction_deg"])

    out["units"] = {
        "temperature": "F",
        "wind": "mph",
        "pressure": "inHg",
        "rain": "in",
        "lightning_distance": "km",
    }
    return out


def estimate_sky_condition(data):
    """
    Approximate sky condition from station light/radiation readings.
    This is a heuristic estimate, not measured cloud cover.
    """
    ts = data.get("timestamp_epoch")
    if ts:
        hour = dt.datetime.fromtimestamp(ts).astimezone().hour
        if hour < 6 or hour > 20:
            return "Night"

    lux = data.get("illuminance_lux")
    solar = data.get("solar_radiation_wpm2")

    if lux is None and solar is None:
        return None

    score = 0.0
    if lux is not None:
        score += min(max(lux / 50000.0, 0.0), 1.0)
    if solar is not None:
        score += min(max(solar / 800.0, 0.0), 1.0)
    score /= 2.0

    if score >= 0.65:
        return "Sunny"
    if score >= 0.45:
        return "Mostly sunny"
    if score >= 0.25:
        return "Partly cloudy"
    if score >= 0.10:
        return "Mostly cloudy"
    return "Overcast"


def build_event_phrases(data, units):
    phrases = []

    rain_interval_mm = data.get("rain_accumulated_mm_last_interval")
    if rain_interval_mm is not None and rain_interval_mm > 0:
        if units == "us":
            phrases.append(f"rain now ({data.get('rain_accumulated_in_last_interval')} in/interval)")
        else:
            phrases.append(f"rain now ({rain_interval_mm} mm/interval)")

    strikes = data.get("lightning_strike_count_last_interval")
    if strikes is not None and strikes > 0:
        dist = data.get("lightning_avg_distance_km")
        if dist is not None:
            phrases.append(f"lightning activity ({strikes} strikes, avg {dist} km)")
        else:
            phrases.append(f"lightning activity ({strikes} strikes)")

    return phrases


def make_summary(data, units):
    ts = data.get("timestamp_epoch")
    local_ts = (
        dt.datetime.fromtimestamp(ts).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
        if ts
        else "unknown time"
    )

    sky = estimate_sky_condition(data)
    sky_part = f"sky est. {sky}, " if sky else ""

    if units == "us":
        t = data.get("air_temp_f")
        w = data.get("wind_avg_mph")
        g = data.get("wind_gust_mph")
        p = data.get("station_pressure_inhg")
        r = data.get("local_daily_rain_in")
        wd = data.get("wind_direction_deg")
        wc = data.get("wind_direction_cardinal")
        wind_part = f"{w} mph (gust {g}, dir {wd}° {wc})" if wd is not None and wc else f"{w} mph (gust {g})"
        base = (
            f"Tempest @ {local_ts}: "
            f"{sky_part}temp {t}°F, wind {wind_part}, "
            f"humidity {data.get('relative_humidity_pct')}%, pressure {p} inHg, "
            f"rain today {r} in"
        )
    else:
        t = data.get("air_temp_c")
        w = data.get("wind_avg_mps")
        g = data.get("wind_gust_mps")
        p = data.get("station_pressure_mb")
        r = data.get("local_daily_rain_mm")
        wd = data.get("wind_direction_deg")
        wc = data.get("wind_direction_cardinal")
        wind_part = f"{w} m/s (gust {g}, dir {wd}° {wc})" if wd is not None and wc else f"{w} m/s (gust {g})"
        base = (
            f"Tempest @ {local_ts}: "
            f"{sky_part}temp {t}°C, wind {wind_part}, "
            f"humidity {data.get('relative_humidity_pct')}%, pressure {p} mb, "
            f"rain today {r} mm"
        )

    events = build_event_phrases(data, units)
    if events:
        return base + "; " + "; ".join(events) + "."
    return base + "."


def parse_stats_row(row, units):
    parsed = {
        # 1..34 mapping provided by user (converted to zero-based indexes)
        "date_local": row[0] if len(row) > 0 else None,
        "station_pressure_avg_mb": row[1] if len(row) > 1 else None,
        "station_pressure_max_mb": row[2] if len(row) > 2 else None,
        "station_pressure_min_mb": row[3] if len(row) > 3 else None,
        "air_temp_avg_c": row[4] if len(row) > 4 else None,
        "air_temp_max_c": row[5] if len(row) > 5 else None,
        "air_temp_min_c": row[6] if len(row) > 6 else None,
        "relative_humidity_avg_pct": row[7] if len(row) > 7 else None,
        "relative_humidity_max_pct": row[8] if len(row) > 8 else None,
        "relative_humidity_min_pct": row[9] if len(row) > 9 else None,
        "brightness_avg_lux": row[10] if len(row) > 10 else None,
        "brightness_max_lux": row[11] if len(row) > 11 else None,
        "brightness_min_lux": row[12] if len(row) > 12 else None,
        "uv_index_avg": row[13] if len(row) > 13 else None,
        "uv_index_max": row[14] if len(row) > 14 else None,
        "uv_index_min": row[15] if len(row) > 15 else None,
        "solar_radiation_avg_wpm2": row[16] if len(row) > 16 else None,
        "solar_radiation_max_wpm2": row[17] if len(row) > 17 else None,
        "solar_radiation_min_wpm2": row[18] if len(row) > 18 else None,
        "wind_avg_mps": row[19] if len(row) > 19 else None,
        "wind_gust_mps": row[20] if len(row) > 20 else None,
        "wind_lull_mps": row[21] if len(row) > 21 else None,
        "wind_direction_deg": row[22] if len(row) > 22 else None,
        "wind_interval_s": row[23] if len(row) > 23 else None,
        "lightning_strike_count": row[24] if len(row) > 24 else None,
        "lightning_avg_distance_km": row[25] if len(row) > 25 else None,
        "record_count": row[26] if len(row) > 26 else None,
        "battery_v": row[27] if len(row) > 27 else None,
        "local_precip_accum_today_mm": row[28] if len(row) > 28 else None,
        "local_precip_accum_final_mm": row[29] if len(row) > 29 else None,
        "local_precip_minutes_today": row[30] if len(row) > 30 else None,
        "local_precip_minutes_final": row[31] if len(row) > 31 else None,
        "precipitation_type": row[32] if len(row) > 32 else None,
        "precipitation_analysis_type": row[33] if len(row) > 33 else None,
    }

    parsed["rain_total_mm"] = parsed.get("local_precip_accum_final_mm")
    parsed["wind_direction_cardinal"] = deg_to_cardinal(parsed.get("wind_direction_deg"))

    if units == "us":
        if parsed.get("station_pressure_avg_mb") is not None:
            parsed["station_pressure_avg_inhg"] = round(mb_to_inhg(parsed["station_pressure_avg_mb"]), 3)
        if parsed.get("station_pressure_max_mb") is not None:
            parsed["station_pressure_max_inhg"] = round(mb_to_inhg(parsed["station_pressure_max_mb"]), 3)
        if parsed.get("station_pressure_min_mb") is not None:
            parsed["station_pressure_min_inhg"] = round(mb_to_inhg(parsed["station_pressure_min_mb"]), 3)
        if parsed.get("air_temp_avg_c") is not None:
            parsed["air_temp_avg_f"] = round(c_to_f(parsed["air_temp_avg_c"]), 1)
        if parsed.get("air_temp_max_c") is not None:
            parsed["air_temp_max_f"] = round(c_to_f(parsed["air_temp_max_c"]), 1)
        if parsed.get("air_temp_min_c") is not None:
            parsed["air_temp_min_f"] = round(c_to_f(parsed["air_temp_min_c"]), 1)
        if parsed.get("local_precip_accum_final_mm") is not None:
            parsed["rain_total_in"] = round(mm_to_in(parsed["local_precip_accum_final_mm"]), 3)
        if parsed.get("lightning_avg_distance_km") is not None:
            parsed["lightning_avg_distance_mi"] = round(parsed["lightning_avg_distance_km"] * 0.621371, 1)
        if parsed.get("wind_avg_mps") is not None:
            parsed["wind_avg_mph"] = round(ms_to_mph(parsed["wind_avg_mps"]), 1)
        if parsed.get("wind_gust_mps") is not None:
            parsed["wind_gust_mph"] = round(ms_to_mph(parsed["wind_gust_mps"]), 1)
        if parsed.get("wind_lull_mps") is not None:
            parsed["wind_lull_mph"] = round(ms_to_mph(parsed["wind_lull_mps"]), 1)

    # Keep unknown/unmapped values visible for debugging and future mapping.
    if len(row) > 16:
        parsed["stats_extra_unmapped"] = row[16:]

    parsed["units"] = {
        "pressure": "inHg" if units == "us" else "mb",
        "temperature": "F" if units == "us" else "C",
        "rain": "in" if units == "us" else "mm",
        "wind": "mph" if units == "us" else "m/s",
        "humidity": "%",
        "brightness": "lux",
        "uv": "index",
        "solar_radiation": "W/m²",
        "lightning": "strikes",
    }
    return parsed


def make_historical_summary(period, matched_key, parsed, units):
    rain_duration = parsed.get("rain_duration_minutes")
    rain_total = parsed.get("rain_total_in") if units == "us" else parsed.get("rain_total_mm")
    rain_duration_part = (
        f" over {rain_duration} min"
        if (rain_duration is not None and rain_duration > 0 and rain_total is not None and rain_total > 0)
        else ""
    )

    lightning_count = parsed.get('lightning_strike_count')
    lightning_dist_km = parsed.get('lightning_avg_distance_km')
    lightning_dist_mi = parsed.get('lightning_avg_distance_mi')
    if lightning_count and lightning_count > 0:
        if units == "us" and lightning_dist_mi not in (None, 0):
            lightning_part = f"lightning strikes {lightning_count} (avg dist {lightning_dist_mi} mi)"
        elif lightning_dist_km not in (None, 0):
            lightning_part = f"lightning strikes {lightning_count} (avg dist {lightning_dist_km} km)"
        else:
            lightning_part = f"lightning strikes {lightning_count}"
    else:
        lightning_part = f"lightning strikes {lightning_count if lightning_count is not None else 0}"

    if units == "us":
        return (
            f"Tempest historical {period} stats for {matched_key}: "
            f"temp avg {parsed.get('air_temp_avg_f')}°F "
            f"(max {parsed.get('air_temp_max_f')}°F / min {parsed.get('air_temp_min_f')}°F), "
            f"wind avg {parsed.get('wind_avg_mph')} mph (high {parsed.get('wind_gust_mph')} / low {parsed.get('wind_lull_mph')}, dir {parsed.get('wind_direction_deg')}° {parsed.get('wind_direction_cardinal')}), "
            f"humidity avg {parsed.get('relative_humidity_avg_pct')}% (high {parsed.get('relative_humidity_max_pct')}% / low {parsed.get('relative_humidity_min_pct')}%), "
            f"pressure avg {parsed.get('station_pressure_avg_inhg')} inHg (high {parsed.get('station_pressure_max_inhg')} / low {parsed.get('station_pressure_min_inhg')}), "
            f"UV avg {parsed.get('uv_index_avg')} (high {parsed.get('uv_index_max')} / low {parsed.get('uv_index_min')}), "
            f"solar radiation avg {parsed.get('solar_radiation_avg_wpm2')} W/m² (high {parsed.get('solar_radiation_max_wpm2')} / low {parsed.get('solar_radiation_min_wpm2')}), "
            f"brightness avg {parsed.get('brightness_avg_lux')} lux (high {parsed.get('brightness_max_lux')} / low {parsed.get('brightness_min_lux')}), "
            f"{lightning_part}, rain {parsed.get('rain_total_in')} in{rain_duration_part}."
        )

    return (
        f"Tempest historical {period} stats for {matched_key}: "
        f"temp avg {parsed.get('air_temp_avg_c')}°C "
        f"(max {parsed.get('air_temp_max_c')}°C / min {parsed.get('air_temp_min_c')}°C), "
        f"wind avg {parsed.get('wind_avg_mps')} m/s (high {parsed.get('wind_gust_mps')} / low {parsed.get('wind_lull_mps')}, dir {parsed.get('wind_direction_deg')}° {parsed.get('wind_direction_cardinal')}), "
        f"humidity avg {parsed.get('relative_humidity_avg_pct')}% (high {parsed.get('relative_humidity_max_pct')}% / low {parsed.get('relative_humidity_min_pct')}%), "
        f"pressure avg {parsed.get('station_pressure_avg_mb')} mb (high {parsed.get('station_pressure_max_mb')} / low {parsed.get('station_pressure_min_mb')}), "
        f"UV avg {parsed.get('uv_index_avg')} (high {parsed.get('uv_index_max')} / low {parsed.get('uv_index_min')}), "
        f"solar radiation avg {parsed.get('solar_radiation_avg_wpm2')} W/m² (high {parsed.get('solar_radiation_max_wpm2')} / low {parsed.get('solar_radiation_min_wpm2')}), "
        f"brightness avg {parsed.get('brightness_avg_lux')} lux (high {parsed.get('brightness_max_lux')} / low {parsed.get('brightness_min_lux')}), "
        f"{lightning_part}, rain {parsed.get('rain_total_mm')} mm{rain_duration_part}."
    )


def build_observations_url(token, station_id=None, device_id=None):
    q = parse.urlencode({"token": token})
    if device_id:
        return f"{API_BASE}/observations/device/{device_id}?{q}"
    return f"{API_BASE}/observations/station/{station_id}?{q}"


def build_stats_url(token, station_id):
    q = parse.urlencode({"token": token})
    return f"{API_BASE}/stats/station/{station_id}?{q}"


def extract_obs_list(payload):
    return payload.get("obs") or payload.get("obs_st")


def period_date_prefix(period, when=None):
    current = when or dt.datetime.now().astimezone()
    if period == "day":
        return current.strftime("%Y-%m-%d")
    if period == "month":
        return current.strftime("%Y-%m")
    if period == "year":
        return current.strftime("%Y")
    raise ValueError(f"Unsupported period: {period}")


def normalize_date_prefix(period, date_text):
    if not date_text:
        return period_date_prefix(period)

    date_text = date_text.strip()
    if period == "day":
        return dt.datetime.strptime(date_text, "%Y-%m-%d").strftime("%Y-%m-%d")
    if period == "month":
        # Accept YYYY-MM or YYYY-MM-DD; normalize to YYYY-MM
        if len(date_text) == 7:
            return dt.datetime.strptime(date_text, "%Y-%m").strftime("%Y-%m")
        return dt.datetime.strptime(date_text, "%Y-%m-%d").strftime("%Y-%m")
    if period == "year":
        # Accept YYYY, YYYY-MM, YYYY-MM-DD; normalize to YYYY
        if len(date_text) == 4:
            return dt.datetime.strptime(date_text, "%Y").strftime("%Y")
        if len(date_text) == 7:
            return dt.datetime.strptime(date_text, "%Y-%m").strftime("%Y")
        return dt.datetime.strptime(date_text, "%Y-%m-%d").strftime("%Y")
    raise ValueError(f"Unsupported period: {period}")


def select_stats_row(payload, period, target_prefix):
    rows = payload.get(f"stats_{period}") or []
    for row in rows:
        if not row:
            continue
        key = str(row[0])
        if key.startswith(target_prefix):
            return key, row
    return None, None


def list_stats_day_rows_for_prefix(payload, target_prefix):
    rows = payload.get("stats_day") or []
    out = []
    for row in rows:
        if not row:
            continue
        key = str(row[0])
        if key.startswith(target_prefix):
            out.append(row)
    return out


def fetch_obs_rows_for_date(token, device_id, date_local):
    day_start = dt.datetime.strptime(date_local, "%Y-%m-%d").replace(tzinfo=dt.datetime.now().astimezone().tzinfo)
    day_end = day_start + dt.timedelta(days=1)
    q = parse.urlencode({
        "token": token,
        "time_start": int(day_start.timestamp()),
        "time_end": int(day_end.timestamp()),
    })
    url = f"{API_BASE}/observations/device/{device_id}?{q}"
    payload = get_json(url, retries=1)
    return extract_obs_list(payload) or []


def summarize_precip_for_day(token, device_id, date_local):
    obs_rows = fetch_obs_rows_for_date(token, device_id, date_local)
    rain_minutes = 0
    for obs in obs_rows:
        rain_mm = obs[12] if len(obs) > 12 else 0
        precip_type = obs[13] if len(obs) > 13 else 0
        interval_min = obs[17] if len(obs) > 17 else 1
        if (rain_mm and rain_mm > 0) or (precip_type and precip_type > 0):
            rain_minutes += interval_min if interval_min else 1
    return int(round(rain_minutes))


def summarize_precip_for_period(payload, period, target_prefix, token, device_id):
    if not device_id:
        return None

    if period == "day":
        return summarize_precip_for_day(token, device_id, target_prefix)

    day_rows = list_stats_day_rows_for_prefix(payload, target_prefix)
    rainy_days = [str(r[0]) for r in day_rows if len(r) > 15 and r[15] and r[15] > 0]

    # Safety cap for large ranges.
    if len(rainy_days) > 120:
        rainy_days = rainy_days[:120]

    total_rain_minutes = 0
    for day in rainy_days:
        try:
            total_rain_minutes += summarize_precip_for_day(token, device_id, day)
        except Exception:
            continue
    return int(round(total_rain_minutes))


def main():
    ap = argparse.ArgumentParser(description="Fetch current or historical weather from a Tempest station/device")
    ap.add_argument("--station-id", default=os.getenv("TEMPEST_STATION_ID"))
    ap.add_argument("--device-id", default=os.getenv("TEMPEST_DEVICE_ID"))
    ap.add_argument("--token", default=os.getenv("TEMPEST_API_TOKEN"))
    ap.add_argument("--units", default=os.getenv("TEMPEST_UNITS", "us"), choices=["us", "metric"])
    ap.add_argument(
        "--stats",
        nargs="?",
        const="day",
        choices=["day", "month", "year"],
        help="Return historical station stats for a period (defaults to day when no period is given)",
    )
    ap.add_argument(
        "--date",
        help="Target local date for --stats. day: YYYY-MM-DD, month: YYYY-MM or YYYY-MM-DD, year: YYYY|YYYY-MM|YYYY-MM-DD",
    )
    ap.add_argument("--json", action="store_true", help="Print JSON only")
    args = ap.parse_args()

    if not args.token:
        print("ERROR: Missing API token. Set TEMPEST_API_TOKEN or pass --token", file=sys.stderr)
        sys.exit(2)

    if args.stats:
        if not args.station_id:
            print(
                "ERROR: Historical stats require station id. Set TEMPEST_STATION_ID or pass --station-id",
                file=sys.stderr,
            )
            sys.exit(2)

        try:
            target_prefix = normalize_date_prefix(args.stats, args.date)
        except ValueError as e:
            print(f"ERROR: Invalid --date for stats period '{args.stats}': {e}", file=sys.stderr)
            sys.exit(2)

        url = build_stats_url(args.token, args.station_id)

        try:
            payload = get_json(url, retries=1)
        except error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else ""
            print(f"ERROR: Tempest API HTTP {e.code}. {body[:300]}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: Failed to fetch Tempest data: {e}", file=sys.stderr)
            sys.exit(1)

        matched_key, row = select_stats_row(payload, args.stats, target_prefix)
        if not row:
            print(
                f"ERROR: No stats row found for period '{args.stats}' and date prefix '{target_prefix}'",
                file=sys.stderr,
            )
            sys.exit(1)

        parsed_stats = parse_stats_row(row, args.units)

        rain_duration_min = parsed_stats.get("local_precip_minutes_final")
        if rain_duration_min is not None:
            parsed_stats["rain_duration_minutes"] = rain_duration_min
            parsed_stats["rain_duration_hours"] = round(rain_duration_min / 60.0, 2)

        result = {
            "source": "WeatherFlow Tempest REST API",
            "request_type": "station_stats",
            "station_id": str(args.station_id),
            "request_url": url.replace(args.token, "***redacted***"),
            "historical": {
                "period": args.stats,
                "requested_date_prefix": target_prefix,
                "matched_key": matched_key,
                "row_length": len(row),
                "first_ob_day_local": payload.get("first_ob_day_local"),
                "last_ob_day_local": payload.get("last_ob_day_local"),
                "parsed": parsed_stats,
                "raw_row": row,
            },
        }

        print(json.dumps(result, indent=2, sort_keys=True))
        if not args.json:
            print()
            print(make_historical_summary(args.stats, matched_key, parsed_stats, args.units))
        return

    if not args.station_id and not args.device_id:
        print(
            "ERROR: Missing station/device id. Set TEMPEST_STATION_ID or TEMPEST_DEVICE_ID (or pass --station-id/--device-id)",
            file=sys.stderr,
        )
        sys.exit(2)

    url = build_observations_url(args.token, station_id=args.station_id, device_id=args.device_id)

    try:
        payload = get_json(url, retries=1)
    except error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else ""
        print(f"ERROR: Tempest API HTTP {e.code}. {body[:300]}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to fetch Tempest data: {e}", file=sys.stderr)
        sys.exit(1)

    obs_list = extract_obs_list(payload)
    if not obs_list:
        print("ERROR: Tempest response did not include observations (obs/obs_st)", file=sys.stderr)
        print(json.dumps(payload, indent=2)[:1200], file=sys.stderr)
        sys.exit(1)

    parsed = parse_obs(obs_list[0])
    converted = convert_units(parsed, args.units)

    result = {
        "source": "WeatherFlow Tempest REST API",
        "station_id": str(args.station_id) if args.station_id else None,
        "device_id": str(args.device_id) if args.device_id else None,
        "request_type": "observations",
        "request_url": url.replace(args.token, "***redacted***"),
        "observed": converted,
    }

    print(json.dumps(result, indent=2, sort_keys=True))
    if not args.json:
        print()
        print(make_summary(converted, args.units))


if __name__ == "__main__":
    main()
