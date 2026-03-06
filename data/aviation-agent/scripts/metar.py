#!/usr/bin/env python3
"""Aviation weather data fetcher - queries METAR, TAF, and PIREP from aviationweather.gov."""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE_URL = "https://aviationweather.gov/api/data"
ALLOWED_DOMAINS = ("aviationweather.gov",)
ICAO_PATTERN = re.compile(r"^[A-Z]{4}$")

# Weather phenomena decode table
WX_CODES = {
    # Intensity
    "-": "Light", "+": "Heavy",
    # Descriptor
    "MI": "Shallow", "PR": "Partial", "BC": "Patches", "DR": "Low Drifting",
    "BL": "Blowing", "SH": "Showers", "TS": "Thunderstorm", "FZ": "Freezing",
    # Precipitation
    "RA": "Rain", "DZ": "Drizzle", "SN": "Snow", "SG": "Snow Grains",
    "IC": "Ice Crystals", "PL": "Ice Pellets", "GR": "Hail",
    "GS": "Small Hail", "UP": "Unknown Precip",
    # Obscuration
    "FG": "Fog", "BR": "Mist", "HZ": "Haze", "SA": "Sand",
    "DU": "Dust", "FU": "Smoke", "VA": "Volcanic Ash", "PY": "Spray",
    # Other
    "SQ": "Squall", "FC": "Funnel Cloud", "SS": "Sandstorm", "DS": "Duststorm",
    "PO": "Dust Whirls",
}

CLOUD_COVER = {
    "SKC": "Sky Clear", "CLR": "Clear", "FEW": "Few (1-2 oktas)",
    "SCT": "Scattered (3-4 oktas)", "BKN": "Broken (5-7 oktas)",
    "OVC": "Overcast (8 oktas)", "VV": "Vertical Visibility",
}


def validate_icao(code):
    """Validate ICAO airport code format."""
    code = code.upper().strip()
    if not ICAO_PATTERN.match(code):
        raise argparse.ArgumentTypeError(
            f"Invalid ICAO code '{code}'. Must be exactly 4 uppercase letters (e.g., KLAX)."
        )
    return code


def fetch_json(endpoint, params):
    """Fetch JSON from aviationweather.gov API."""
    url = f"{BASE_URL}/{endpoint}?{urlencode(params)}"
    # Verify domain is whitelisted
    if not any(domain in url for domain in ALLOWED_DOMAINS):
        print(f"Error: URL domain not in whitelist: {url}", file=sys.stderr)
        sys.exit(1)

    req = Request(url, headers={"User-Agent": "aviation-agent-skill/0.1.0"})
    try:
        with urlopen(req, timeout=15) as resp:
            data = resp.read().decode("utf-8")
            if not data.strip():
                return []
            return json.loads(data)
    except HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason} for {endpoint}", file=sys.stderr)
        sys.exit(1)
    except URLError as e:
        print(f"Network error: {e.reason}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        return []


def classify_flight_category(visib, ceiling_ft):
    """Determine flight category based on visibility and ceiling.

    Categories per FAA:
      LIFR: vis < 1 SM or ceiling < 500 ft
      IFR:  vis 1-<3 SM or ceiling 500-<1000 ft
      MVFR: vis 3-5 SM or ceiling 1000-3000 ft
      VFR:  vis > 5 SM and ceiling > 3000 ft
    """
    # Parse visibility
    vis = 99
    if visib is not None:
        if isinstance(visib, str):
            visib = visib.replace("+", "")
            try:
                vis = float(visib)
            except ValueError:
                vis = 99
        else:
            vis = float(visib)

    ceil = ceiling_ft if ceiling_ft is not None else 99999

    if vis < 1 or ceil < 500:
        return "LIFR"
    if vis < 3 or ceil < 1000:
        return "IFR"
    if vis <= 5 or ceil <= 3000:
        return "MVFR"
    return "VFR"


def get_ceiling(clouds):
    """Extract ceiling from cloud layers. Ceiling = lowest BKN or OVC layer."""
    if not clouds:
        return None
    for layer in sorted(clouds, key=lambda c: c.get("base", 99999) or 99999):
        cover = layer.get("cover", "")
        if cover in ("BKN", "OVC", "VV"):
            return layer.get("base")
    return None


def decode_wx(wx_string):
    """Decode weather phenomena string like +TSRA or -FZFG."""
    if not wx_string:
        return ""
    parts = []
    for token in wx_string.split():
        decoded = []
        i = 0
        while i < len(token):
            if token[i] in ("-", "+"):
                decoded.append(WX_CODES.get(token[i], token[i]))
                i += 1
            elif i + 2 <= len(token) and token[i:i+2] in WX_CODES:
                decoded.append(WX_CODES[token[i:i+2]])
                i += 2
            else:
                decoded.append(token[i:])
                break
        parts.append(" ".join(decoded))
    return ", ".join(parts)


def format_wind(wdir, wspd, wgst=None):
    """Format wind information."""
    if wdir is None and wspd is None:
        return "Calm"
    direction = "VRB" if wdir == "VRB" or wdir is None else f"{wdir:03d}" if isinstance(wdir, int) else str(wdir)
    gust = f" gusting {wgst} kt" if wgst else ""
    return f"{direction}° at {wspd} kt{gust}"


def format_clouds(clouds):
    """Format cloud layers for display."""
    if not clouds:
        return "Clear"
    parts = []
    for layer in clouds:
        cover = layer.get("cover", "???")
        base = layer.get("base")
        label = CLOUD_COVER.get(cover, cover)
        cloud_type = layer.get("type", "")
        type_str = f" ({cloud_type})" if cloud_type else ""
        if base is not None:
            parts.append(f"  {label} at {base:,} ft AGL{type_str}")
        else:
            parts.append(f"  {label}{type_str}")
    return "\n".join(parts)


def format_timestamp(epoch):
    """Format epoch timestamp to readable UTC string."""
    if epoch is None:
        return "N/A"
    try:
        dt = datetime.fromtimestamp(epoch, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%MZ")
    except (OSError, ValueError):
        return "N/A"


def print_metar(data):
    """Print formatted METAR report."""
    if not data:
        print("  No METAR data available.")
        return
    for obs in data:
        icao = obs.get("icaoId", "????")
        name = obs.get("name", "")
        flt_cat_api = obs.get("fltCat", "")

        ceiling = get_ceiling(obs.get("clouds", []))
        flt_cat = classify_flight_category(obs.get("visib"), ceiling)

        cat_display = flt_cat_api if flt_cat_api else flt_cat
        cat_marker = {"VFR": "✅", "MVFR": "🟡", "IFR": "🔴", "LIFR": "⛔"}.get(cat_display, "❓")

        print(f"\n{'='*60}")
        print(f"  METAR: {icao} - {name}")
        print(f"  Flight Category: {cat_marker} {cat_display}")
        print(f"{'='*60}")
        print(f"  Raw: {obs.get('rawOb', 'N/A')}")
        print(f"  Observed: {format_timestamp(obs.get('obsTime'))}")
        print(f"  Temperature: {obs.get('temp', 'N/A')}°C / Dewpoint: {obs.get('dewp', 'N/A')}°C")
        print(f"  Wind: {format_wind(obs.get('wdir'), obs.get('wspd'), obs.get('wgst'))}")

        visib = obs.get("visib", "N/A")
        print(f"  Visibility: {visib} SM")
        print(f"  Altimeter: {obs.get('altim', 'N/A')} hPa ({round(obs.get('altim', 0) * 0.02953, 2):.2f} inHg)")

        wx = obs.get("wxString", "")
        if wx:
            print(f"  Weather: {wx} ({decode_wx(wx)})")

        print(f"  Clouds:")
        print(format_clouds(obs.get("clouds", [])))
        if ceiling is not None:
            print(f"  Ceiling: {ceiling:,} ft AGL")
        print()


def print_taf(data):
    """Print formatted TAF report."""
    if not data:
        print("  No TAF data available.")
        return
    for taf in data:
        icao = taf.get("icaoId", "????")
        name = taf.get("name", "")
        print(f"\n{'='*60}")
        print(f"  TAF: {icao} - {name}")
        print(f"{'='*60}")
        print(f"  Raw: {taf.get('rawTAF', 'N/A')}")
        print(f"  Issued: {format_timestamp(taf.get('issueTime'))}")
        print(f"  Valid: {format_timestamp(taf.get('validTimeFrom'))} to {format_timestamp(taf.get('validTimeTo'))}")
        print()

        for i, fcst in enumerate(taf.get("fcsts", [])):
            change = fcst.get("fcstChange", "INITIAL") or "INITIAL"
            prob = fcst.get("probability")
            prob_str = f" (PROB{prob})" if prob else ""

            time_from = format_timestamp(fcst.get("timeFrom"))
            time_to = format_timestamp(fcst.get("timeTo"))

            ceiling = get_ceiling(fcst.get("clouds", []))
            flt_cat = classify_flight_category(fcst.get("visib"), ceiling)
            cat_marker = {"VFR": "✅", "MVFR": "🟡", "IFR": "🔴", "LIFR": "⛔"}.get(flt_cat, "❓")

            print(f"  --- {change}{prob_str}: {time_from} to {time_to} [{cat_marker} {flt_cat}] ---")
            print(f"    Wind: {format_wind(fcst.get('wdir'), fcst.get('wspd'), fcst.get('wgst'))}")

            visib = fcst.get("visib", "N/A")
            print(f"    Visibility: {visib} SM")

            wx = fcst.get("wxString", "")
            if wx:
                print(f"    Weather: {wx} ({decode_wx(wx)})")

            print(f"    Clouds:")
            for line in format_clouds(fcst.get("clouds", [])).split("\n"):
                print(f"  {line}")
            print()


def print_pirep(data):
    """Print formatted PIREP reports."""
    if not data:
        print("  No PIREP data available in the specified area/timeframe.")
        return
    for i, pirep in enumerate(data):
        print(f"\n  --- PIREP #{i+1} ---")
        print(f"  Raw: {pirep.get('rawOb', 'N/A')}")
        print(f"  Time: {format_timestamp(pirep.get('obsTime'))}")
        print(f"  Location: {pirep.get('lat', 'N/A')}, {pirep.get('lon', 'N/A')}")
        print(f"  Altitude: {pirep.get('fltlvl', 'N/A')} FL")
        print(f"  Aircraft: {pirep.get('acType', 'N/A')}")

        tp = pirep.get("turbType", "")
        if tp:
            print(f"  Turbulence: {pirep.get('turbInten', 'N/A')} (base FL{pirep.get('turbBLo', '?')} - top FL{pirep.get('turbBHi', '?')})")

        ic = pirep.get("icgType", "")
        if ic:
            print(f"  Icing: {pirep.get('icgInten', 'N/A')} {ic} (base FL{pirep.get('icgBLo', '?')} - top FL{pirep.get('icgBHi', '?')})")

        wx = pirep.get("wxString", "")
        if wx:
            print(f"  Weather: {wx}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Fetch aviation weather data (METAR/TAF/PIREP) from aviationweather.gov",
        epilog="Examples:\n"
               "  %(prog)s --metar KLAX KJFK\n"
               "  %(prog)s --taf KORD --hours 12\n"
               "  %(prog)s --pirep KSFO --hours 3\n"
               "  %(prog)s --metar KLAX --taf KLAX",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--metar", nargs="+", type=validate_icao, metavar="ICAO",
                        help="Fetch METAR for one or more ICAO airport codes")
    parser.add_argument("--taf", nargs="+", type=validate_icao, metavar="ICAO",
                        help="Fetch TAF for one or more ICAO airport codes")
    parser.add_argument("--pirep", type=validate_icao, metavar="ICAO",
                        help="Fetch PIREPs near an ICAO airport (200nm radius)")
    parser.add_argument("--hours", type=int, default=2, choices=range(1, 25),
                        metavar="N", help="Hours of data to fetch (1-24, default: 2)")

    args = parser.parse_args()

    if not any([args.metar, args.taf, args.pirep]):
        parser.print_help()
        sys.exit(1)

    if args.metar:
        ids = ",".join(args.metar)
        print(f"\n📡 Fetching METAR for: {ids}")
        data = fetch_json("metar", {"ids": ids, "format": "json", "hours": args.hours})
        if isinstance(data, dict) and "error" in data:
            print(f"  API Error: {data['error']}", file=sys.stderr)
        else:
            print_metar(data)

    if args.taf:
        ids = ",".join(args.taf)
        print(f"\n📡 Fetching TAF for: {ids}")
        data = fetch_json("taf", {"ids": ids, "format": "json"})
        if isinstance(data, dict) and "error" in data:
            print(f"  API Error: {data['error']}", file=sys.stderr)
        else:
            print_taf(data)

    if args.pirep:
        print(f"\n📡 Fetching PIREPs near: {args.pirep} (200nm radius, last {args.hours}h)")
        data = fetch_json("pirep", {
            "id": args.pirep, "format": "json",
            "dist": 200, "age": args.hours,
        })
        if isinstance(data, dict) and "error" in data:
            print(f"  API Error: {data['error']}", file=sys.stderr)
        else:
            print_pirep(data)


if __name__ == "__main__":
    main()
