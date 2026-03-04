#!/usr/bin/env python3
"""PropertyGuru property listing scraper for Singapore.

Supports flexible filtering by listing type, property type, bedrooms,
bathrooms, price range, size, TOP year, MRT stations, and room type.
Outputs JSON to stdout by default when called non-interactively.

Dependencies: curl_cffi, beautifulsoup4, lxml
  pip install curl_cffi beautifulsoup4 lxml
"""

import argparse
import json
import os
import re
import sys
import urllib.parse
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional


# ─── Valid parameter values ──────────────────────────────────────────────────

VALID_LISTING_TYPES = ["rent", "sale"]
VALID_PROPERTY_TYPE_GROUPS = ["N", "L", "H"]  # N=Condo, L=Landed, H=HDB
VALID_SORTS = ["date", "price", "psf", "size"]
VALID_ORDERS = ["asc", "desc"]
VALID_ROOM_TYPES = ["master", "common", "shared"]
VALID_MRT_STATIONS = {
    # North-South Line
    "NS1", "NS2", "NS3", "NS3A", "NS4", "NS5", "NS6", "NS7", "NS8", "NS9",
    "NS10", "NS11", "NS12", "NS13", "NS14", "NS15", "NS16", "NS17", "NS18",
    "NS19", "NS20", "NS21", "NS22", "NS23", "NS24", "NS25", "NS26", "NS27", "NS28",
    # East-West Line
    "EW1", "EW2", "EW3", "EW4", "EW5", "EW6", "EW7", "EW8", "EW9", "EW10",
    "EW11", "EW12", "EW13", "EW14", "EW15", "EW16", "EW17", "EW18", "EW19", "EW20",
    "EW21", "EW22", "EW23", "EW24", "EW25", "EW26", "EW27", "EW28", "EW29", "EW30",
    "EW31", "EW32", "EW33",
    # Changi Airport Branch
    "CG1", "CG2",
    # North-East Line
    "NE1", "NE3", "NE4", "NE5", "NE6", "NE7", "NE8", "NE9", "NE10",
    "NE11", "NE12", "NE13", "NE14", "NE15", "NE16", "NE17", "NE18",
    # Circle Line
    "CC1", "CC2", "CC3", "CC4", "CC5", "CC6", "CC7", "CC8", "CC9", "CC10",
    "CC11", "CC12", "CC13", "CC14", "CC15", "CC16", "CC17", "CC19", "CC20",
    "CC21", "CC22", "CC23", "CC24", "CC25", "CC26", "CC27", "CC28", "CC29", "CC30",
    "CC31", "CC32", "CE1", "CE2",
    # Downtown Line
    "DT1", "DT2", "DT3", "DT5", "DT6", "DT7", "DT8", "DT9", "DT10",
    "DT11", "DT12", "DT13", "DT14", "DT15", "DT16", "DT17", "DT18", "DT19", "DT20",
    "DT21", "DT22", "DT23", "DT24", "DT25", "DT26", "DT27", "DT28", "DT29", "DT30",
    "DT31", "DT32", "DT33", "DT34", "DT35", "DT36", "DT37",
    # Thomson-East Coast Line
    "TE1", "TE2", "TE3", "TE4", "TE5", "TE6", "TE7", "TE8", "TE9", "TE10",
    "TE11", "TE12", "TE13", "TE14", "TE15", "TE16", "TE17", "TE18", "TE19", "TE20",
    "TE21", "TE22", "TE22A", "TE23", "TE24", "TE25", "TE26", "TE27", "TE28", "TE29",
    "TE30", "TE31",
    # Jurong Region Line
    "JS1", "JS2", "JS3", "JS4", "JS5", "JS6", "JS7", "JS8", "JS9", "JS10",
    "JS11", "JS12", "JE1", "JE2", "JE3", "JE4", "JE5", "JE6", "JE7",
    "JW1", "JW2", "JW3", "JW4", "JW5",
    # Cross Island Line
    "CR2", "CR3", "CR4", "CR5", "CR6", "CR7", "CR8", "CR9", "CR10",
    "CR11", "CR12", "CR13",
}

VALIDATIONS = {
    "listingType": VALID_LISTING_TYPES,
    "propertyTypeGroup": VALID_PROPERTY_TYPE_GROUPS,
    "sort": VALID_SORTS,
    "order": VALID_ORDERS,
    "roomType": VALID_ROOM_TYPES,
    "mrtStations": VALID_MRT_STATIONS,
}


# ─── URL construction ───────────────────────────────────────────────────────

BASE_URL = "https://www.propertyguru.com.sg"
PAGE_PATHS = {"rent": "property-for-rent", "sale": "property-for-sale"}

# Parameters that support multiple values (repeated keys in URL)
MULTI_VALUE_PARAMS = {"mrtStations", "roomType", "propertyTypeGroup"}

# Single-value filter parameters
SINGLE_VALUE_PARAMS = [
    "entireUnitOrRoom", "bedrooms", "bathrooms",
    "minPrice", "maxPrice", "minSize", "maxSize",
    "minTopYear", "maxTopYear", "distanceToMRT", "availability",
    "sort", "order",
]


def expand_mrt_range(text: str) -> Optional[List[str]]:
    """Expand 'CC:20-24' or 'CC20-24' to ['CC20','CC21','CC22','CC23','CC24']."""
    m = re.match(r"^([A-Za-z]{1,3})[:\s]?(\d+)-(\d+)$", text.strip())
    if not m:
        return None
    line, start, end = m.group(1).upper(), int(m.group(2)), int(m.group(3))
    step = 1 if start <= end else -1
    return [f"{line}{i}" for i in range(start, end + step, step)]


def expand_mrt_input(values: Any) -> List[str]:
    """Normalize various MRT station input formats to a flat list of codes.

    Supported formats:
      - String: "CC20" or range "CC20-24" / "CC:20-24"
      - List of strings: ["CC20", "EW15"]
      - List of tuples: [("CC", [20, 24])]  (line, [start, end])
      - List of dicts: [{"line": "CC", "range": [20, 24]}]
                    or [{"line": "CC", "from": 20, "to": 24}]
    """
    if values is None:
        return []
    if isinstance(values, str):
        expanded = expand_mrt_range(values)
        return expanded if expanded else [values.upper()]

    result: List[str] = []
    seen: set = set()
    items = values if isinstance(values, (list, tuple)) else [values]

    for item in items:
        codes: List[str] = []
        if isinstance(item, str):
            expanded = expand_mrt_range(item)
            codes = expanded if expanded else [item.upper()]
        elif isinstance(item, dict):
            line = (item.get("line") or item.get("prefix") or "").upper()
            if not line:
                continue
            if "range" in item and isinstance(item["range"], (list, tuple)):
                r = item["range"]
                codes = [f"{line}{i}" for i in range(r[0], r[1] + 1)]
            elif "from" in item and "to" in item:
                codes = [f"{line}{i}" for i in range(item["from"], item["to"] + 1)]
            elif "numbers" in item:
                codes = [f"{line}{n}" for n in item["numbers"]]
            else:
                codes = [line]
        elif isinstance(item, (list, tuple)) and len(item) == 2 and isinstance(item[0], str):
            line = item[0].upper()
            nums = item[1]
            if isinstance(nums, (list, tuple)) and len(nums) == 2 and all(isinstance(n, int) for n in nums):
                codes = [f"{line}{i}" for i in range(nums[0], nums[1] + 1)]
            elif isinstance(nums, (list, tuple)):
                codes = [f"{line}{n}" for n in nums]
            elif isinstance(nums, int):
                codes = [f"{line}{nums}"]
        else:
            continue

        for code in codes:
            if code not in seen:
                seen.add(code)
                result.append(code)

    return result


def validate_params(params: dict) -> None:
    """Validate parameter values against known valid values."""
    for key, valid_values in VALIDATIONS.items():
        if key not in params or params[key] is None:
            continue
        values = params[key]
        if isinstance(values, (list, tuple, set)):
            invalid = [v for v in values if v not in valid_values]
            if invalid:
                allowed = sorted(valid_values) if isinstance(valid_values, set) else valid_values
                raise ValueError(f"Invalid {key}: {invalid}. Allowed: {allowed}")
        else:
            if values not in valid_values:
                allowed = sorted(valid_values) if isinstance(valid_values, set) else valid_values
                raise ValueError(f"Invalid {key}: {values}. Allowed: {allowed}")


def build_url(params: dict, page: int = 1) -> str:
    """Build PropertyGuru search URL from filter parameters.

    Parameters use camelCase keys matching the PropertyGuru URL format:
      listingType, propertyTypeGroup, entireUnitOrRoom, roomType,
      bedrooms, bathrooms, minPrice, maxPrice, minSize, maxSize,
      minTopYear, maxTopYear, distanceToMRT, availability,
      mrtStations, sort, order, isCommercial
    """
    listing_type = params.get("listingType", "rent")
    path = PAGE_PATHS.get(listing_type, "property-for-rent")

    query: Dict[str, Any] = {}
    query["listingType"] = listing_type
    query["page"] = page
    query["isCommercial"] = params.get("isCommercial", "false")

    for key in SINGLE_VALUE_PARAMS:
        value = params.get(key)
        if value is not None and value != "":
            query[key] = value

    for key in MULTI_VALUE_PARAMS:
        values = params.get(key)
        if values:
            if isinstance(values, (list, tuple)):
                values = [v for v in values if v is not None and v != ""]
            else:
                values = [values] if values else []
            if values:
                query[key] = values

    return f"{BASE_URL}/{path}?{urllib.parse.urlencode(query, doseq=True)}"


# ─── Scraping ────────────────────────────────────────────────────────────────

# curl_cffi impersonation profile that bypasses Cloudflare
IMPERSONATE_PROFILE = "safari17_2_ios"

# HTTP headers for realistic requests
DEFAULT_HEADERS = {
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}

# CSS selectors for extracting listing card fields (using da-id attributes).
CARD_SELECTORS = {
    "name": '[da-id="listing-card-v2-title"]',
    "price": '[da-id="listing-card-v2-price"]',
    "psf": '[da-id="listing-card-v2-psf"]',
    "address": ".listing-address",
    "bedrooms": '[da-id="listing-card-v2-bedrooms"] p',
    "bathrooms": '[da-id="listing-card-v2-bathrooms"] p',
    "area": '[da-id="listing-card-v2-area"] p',
    "type": '[da-id="listing-card-v2-unit-type"] p',
    "built": '[da-id="listing-card-v2-build-year"] p',
    "availability": '[da-id="listing-card-v2-availability"] p',
    "mrt_distance": ".listing-location-value",
    "list_date": '[da-id="listing-card-v2-recency"] span.hui-typography',
    "agent": '[da-id="listing-card-v2-agent-name"]',
    "agency": '[da-id="listing-card-v2-agency-name"]',
    "headline": ".agent-description",
}


def _select_text(card, selector: str) -> str:
    """Extract stripped text from the first element matching a CSS selector."""
    el = card.select_one(selector)
    return el.get_text(strip=True) if el else ""


def _extract_card(card) -> Optional[dict]:
    """Extract property data from a BeautifulSoup listing card element."""
    listing_id = card.get("da-listing-id", "")
    if not listing_id:
        return None

    prop: Dict[str, str] = {"id": listing_id}

    # Extract all text fields via CSS selectors
    for field, selector in CARD_SELECTORS.items():
        prop[field] = _select_text(card, selector)

    # Link from card-footer anchor
    footer = card.select_one("a.card-footer")
    prop["link"] = footer.get("href", "") if footer else ""

    return prop


def _fetch_page(session, url: str, timeout: int) -> str:
    """Fetch a single page and return HTML content."""
    resp = session.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
    if resp.status_code != 200:
        raise RuntimeError(
            f"HTTP {resp.status_code} for {url}"
        )
    if "Just a moment" in resp.text[:500]:
        raise RuntimeError(
            "Blocked by Cloudflare. Try again later or check your network."
        )
    return resp.text


def fetch_all(
    params: dict,
    *,
    pages: int = 1,
    timeout: int = 30,
    verbose: bool = False,
    extra_query: Optional[Dict[str, str]] = None,
) -> List[dict]:
    """Fetch listings from one or more pages using HTTP requests."""
    try:
        from curl_cffi import requests as cffi_requests
    except ImportError:
        print(
            "Error: curl_cffi is required.\n"
            "Install with: pip install curl_cffi beautifulsoup4 lxml",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print(
            "Error: beautifulsoup4 is required.\n"
            "Install with: pip install beautifulsoup4 lxml",
            file=sys.stderr,
        )
        sys.exit(1)

    session = cffi_requests.Session(impersonate=IMPERSONATE_PROFILE)
    all_properties: List[dict] = []

    for page_num in range(1, pages + 1):
        url = build_url(params, page=page_num)
        if extra_query:
            url += "&" + urllib.parse.urlencode(extra_query)

        if verbose:
            print(f"Fetching: {url}", file=sys.stderr)

        html = _fetch_page(session, url, timeout)

        soup = BeautifulSoup(html, "lxml")
        cards = soup.select("[da-listing-id]")

        if verbose:
            print(
                f"Page {page_num}: {len(cards)} listing cards", file=sys.stderr
            )

        if not cards:
            break

        for card in cards:
            try:
                prop = _extract_card(card)
                if prop:
                    all_properties.append(prop)
            except Exception as e:
                if verbose:
                    print(f"Error extracting card: {e}", file=sys.stderr)

    return all_properties


# ─── Commute calculation ──────────────────────────────────────────────────────

ROUTES_API_URL = "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix"
SGT = timezone(timedelta(hours=8))


def _next_weekday_9am_sgt() -> datetime:
    """Return next weekday 9:00 AM SGT as an aware datetime."""
    now = datetime.now(SGT)
    target = now.replace(hour=9, minute=0, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    while target.weekday() > 4:
        target += timedelta(days=1)
    return target


def _fmt_duration(seconds_str: str) -> str:
    """Convert Routes API duration like '1500s' to '25 mins'."""
    secs = int(seconds_str.rstrip("s"))
    mins = round(secs / 60)
    if mins < 60:
        return f"{mins} mins"
    hours, remainder = divmod(mins, 60)
    return f"{hours} hr {remainder} mins" if remainder else f"{hours} hr"


def _route_matrix_request(
    session,
    origins: List[str],
    destination: str,
    travel_mode: str,
    api_key: str,
    arrival_time: Optional[str] = None,
    departure_time: Optional[str] = None,
    verbose: bool = False,
) -> dict:
    """Call Routes API computeRouteMatrix, return {originIndex: duration_str}."""
    body: Dict[str, Any] = {
        "origins": [
            {"waypoint": {"address": addr}} for addr in origins
        ],
        "destinations": [
            {"waypoint": {"address": destination}}
        ],
        "travelMode": travel_mode,
    }
    if travel_mode == "DRIVE":
        body["routingPreference"] = "TRAFFIC_AWARE"
    if departure_time:
        body["departureTime"] = departure_time
    if arrival_time:
        body["arrivalTime"] = arrival_time

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "originIndex,destinationIndex,duration,condition",
    }

    results: dict = {}
    try:
        resp = session.post(ROUTES_API_URL, json=body, headers=headers, timeout=30)
        if resp.status_code == 200:
            for entry in resp.json():
                if entry.get("condition") == "ROUTE_EXISTS" and "duration" in entry:
                    idx = entry.get("originIndex", 0)
                    results[idx] = _fmt_duration(entry["duration"])
        elif verbose:
            error_msg = ""
            try:
                error_msg = resp.json().get("error", {}).get("message", "")
            except Exception:
                pass
            print(f"Routes API HTTP {resp.status_code}: {error_msg}", file=sys.stderr)
    except Exception as e:
        if verbose:
            print(f"Routes API request failed: {e}", file=sys.stderr)

    return results


def _calculate_commute(
    properties: List[dict],
    destination: str,
    api_key: str,
    verbose: bool = False,
) -> None:
    """Add commute_driving and commute_transit fields to each property in-place."""
    try:
        from curl_cffi import requests as cffi_requests
    except ImportError:
        if verbose:
            print("curl_cffi not available, skipping commute calculation", file=sys.stderr)
        return

    arrival_dt = _next_weekday_9am_sgt()
    departure_dt = arrival_dt - timedelta(hours=1)
    arrival_rfc = arrival_dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    departure_rfc = departure_dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Build origins from addresses
    origins_list = []
    for prop in properties:
        addr = prop.get("address", "")
        if addr and not addr.lower().endswith("singapore"):
            addr += ", Singapore"
        origins_list.append(addr or "Singapore")

    session = cffi_requests.Session(impersonate=IMPERSONATE_PROFILE)

    # Process in batches of 50 (Routes API limit)
    batch_size = 50
    for batch_start in range(0, len(properties), batch_size):
        batch_end = min(batch_start + batch_size, len(properties))
        batch_origins = origins_list[batch_start:batch_end]

        if verbose:
            print(f"Commute API: batch {batch_start+1}-{batch_end}", file=sys.stderr)

        driving = _route_matrix_request(
            session, batch_origins, destination, "DRIVE", api_key,
            departure_time=departure_rfc, verbose=verbose,
        )
        transit = _route_matrix_request(
            session, batch_origins, destination, "TRANSIT", api_key,
            arrival_time=arrival_rfc, verbose=verbose,
        )

        for i in range(batch_end - batch_start):
            prop = properties[batch_start + i]
            prop["commute_driving"] = driving.get(i, "")
            prop["commute_transit"] = transit.get(i, "")


# ─── CLI ─────────────────────────────────────────────────────────────────────


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Scrape PropertyGuru.com.sg property listings.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  %(prog)s --listing-type rent --bedrooms 2 --max-price 4000
  %(prog)s --mrt-range CC:20-24 --mrt-range EW:15-20 --property-type-group N
  %(prog)s --json '{"listingType":"rent","bedrooms":2,"maxPrice":4000}'
  %(prog)s --dry-run --listing-type sale --min-size 1000
  %(prog)s --config filters.json --pages 3 --output json""",
    )

    # Input modes
    p.add_argument("--json", dest="json_input",
                   help="JSON string with filter parameters (camelCase keys)")
    p.add_argument("--config",
                   help="Path to JSON file with filter parameters")

    # Filter parameters
    f = p.add_argument_group("filters")
    f.add_argument("--listing-type", choices=VALID_LISTING_TYPES,
                   help="rent or sale")
    f.add_argument("--property-type-group", action="append",
                   choices=VALID_PROPERTY_TYPE_GROUPS,
                   help="N=Condo, L=Landed, H=HDB (repeatable)")
    f.add_argument("--entire-unit-or-room",
                   help="'ent' for entire unit only; omit for all")
    f.add_argument("--room-type", action="append", choices=VALID_ROOM_TYPES,
                   help="master/common/shared (repeatable)")
    f.add_argument("--bedrooms", type=int,
                   help="Number of bedrooms (-1=room, 0=studio, 1-5)")
    f.add_argument("--bathrooms", type=int,
                   help="Number of bathrooms")
    f.add_argument("--min-price", type=int, help="Minimum price (SGD)")
    f.add_argument("--max-price", type=int, help="Maximum price (SGD)")
    f.add_argument("--min-size", type=int, help="Minimum size (sqft)")
    f.add_argument("--max-size", type=int, help="Maximum size (sqft)")
    f.add_argument("--min-top-year", type=int, help="Minimum TOP year")
    f.add_argument("--max-top-year", type=int, help="Maximum TOP year")
    f.add_argument("--distance-to-mrt", type=float,
                   help="Max distance to MRT in km (e.g. 0.5, 0.75, 1.0)")
    f.add_argument("--availability", type=int,
                   help="Availability filter")
    f.add_argument("--mrt-station", action="append",
                   help="MRT station code, e.g. CC20 (repeatable)")
    f.add_argument("--mrt-range", action="append",
                   help="MRT range, e.g. CC:20-24 (repeatable)")
    f.add_argument("--sort", choices=VALID_SORTS,
                   help="Sort field: date, price, psf, size")
    f.add_argument("--order", choices=VALID_ORDERS,
                   help="Sort order: asc, desc")
    f.add_argument("--commute-to",
                   help="Destination address for commute time calculation (requires GOOGLE_MAPS_API_KEY)")

    # Execution options
    e = p.add_argument_group("execution")
    e.add_argument("--pages", type=int, default=1,
                   help="Number of pages to scrape (default: 1)")
    e.add_argument("--dry-run", action="store_true",
                   help="Build and print URL(s) only, skip scraping")
    e.add_argument("--no-validate", action="store_true",
                   help="Skip parameter validation")
    e.add_argument("--timeout", type=int, default=30,
                   help="HTTP request timeout in seconds (default: 30)")
    e.add_argument("--raw-param", action="append",
                   help="Extra URL query param as key=value")

    # Output options
    o = p.add_argument_group("output")
    default_output = "json" if not sys.stdout.isatty() else "text"
    o.add_argument("--output", choices=["json", "text", "none"],
                   default=default_output,
                   help=f"Output format (default: {default_output})")
    o.add_argument("--verbose", action="store_true",
                   help="Verbose logging to stderr")

    return p.parse_args(argv)


def build_params_from_args(args: argparse.Namespace) -> dict:
    """Build filter parameter dict from CLI arguments."""
    params: Dict[str, Any] = {}

    # Load from JSON string
    if args.json_input:
        params.update(json.loads(args.json_input))

    # Load from config file (overrides JSON string)
    if args.config:
        with open(args.config, "r", encoding="utf-8") as fh:
            params.update(json.load(fh))

    # CLI flags override everything
    cli_map = {
        "listing_type": "listingType",
        "property_type_group": "propertyTypeGroup",
        "entire_unit_or_room": "entireUnitOrRoom",
        "room_type": "roomType",
        "bedrooms": "bedrooms",
        "bathrooms": "bathrooms",
        "min_price": "minPrice",
        "max_price": "maxPrice",
        "min_size": "minSize",
        "max_size": "maxSize",
        "min_top_year": "minTopYear",
        "max_top_year": "maxTopYear",
        "distance_to_mrt": "distanceToMRT",
        "availability": "availability",
        "sort": "sort",
        "order": "order",
        "commute_to": "commuteTo",
    }
    for arg_name, param_name in cli_map.items():
        value = getattr(args, arg_name, None)
        if value is not None:
            params[param_name] = value

    # MRT stations from CLI
    mrt_inputs: List[str] = []
    if args.mrt_station:
        mrt_inputs.extend(args.mrt_station)
    if args.mrt_range:
        for r in args.mrt_range:
            expanded = expand_mrt_range(r)
            if expanded:
                mrt_inputs.extend(expanded)
            else:
                mrt_inputs.append(r)
    if mrt_inputs:
        existing = params.get("mrtStations", [])
        if isinstance(existing, str):
            existing = [existing]
        params["mrtStations"] = list(dict.fromkeys(
            list(existing) + mrt_inputs
        ))

    # Expand MRT stations from any input format
    if "mrtStations" in params:
        params["mrtStations"] = expand_mrt_input(params["mrtStations"])

    # Raw params (added directly to URL query)
    if args.raw_param:
        if "_raw_params" not in params:
            params["_raw_params"] = {}
        for raw in args.raw_param:
            if "=" not in raw:
                raise ValueError(f"Invalid raw param '{raw}', expected key=value")
            key, value = raw.split("=", 1)
            params["_raw_params"][key.strip()] = value.strip()

    return params


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)

    try:
        params = build_params_from_args(args)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # Extract non-URL params before validation
    commute_to = params.pop("commuteTo", None)
    raw_params = params.pop("_raw_params", {})

    if not args.no_validate:
        try:
            validate_params(params)
        except ValueError as e:
            print(f"Validation error: {e}", file=sys.stderr)
            return 1

    # Dry run: print URL(s) only
    if args.dry_run:
        for page_num in range(1, args.pages + 1):
            url = build_url(params, page=page_num)
            if raw_params:
                url += "&" + urllib.parse.urlencode(raw_params)
            print(url)
        return 0

    # Scrape
    try:
        properties = fetch_all(
            params,
            pages=args.pages,
            timeout=args.timeout,
            verbose=args.verbose,
            extra_query=raw_params or None,
        )
    except Exception as e:
        print(f"Scraping error: {e}", file=sys.stderr)
        return 1

    # Commute calculation
    if commute_to and properties:
        api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")
        if api_key:
            _calculate_commute(properties, commute_to, api_key, verbose=args.verbose)
        elif args.verbose:
            print("GOOGLE_MAPS_API_KEY not set, skipping commute calculation", file=sys.stderr)

    # Output
    if args.output == "json":
        print(json.dumps(properties, ensure_ascii=False, indent=2))
    elif args.output == "text":
        if not properties:
            print("No listings found.")
        for prop in properties:
            print(f"[{prop['id']}] {prop['name']} — {prop['price']}")
            details = []
            if prop.get("area"):
                details.append(prop["area"])
            if prop.get("bedrooms"):
                details.append(f"{prop['bedrooms']}BR")
            if prop.get("bathrooms"):
                details.append(f"{prop['bathrooms']}BA")
            if prop.get("type"):
                details.append(prop["type"])
            if details:
                print(f"  {' | '.join(details)}")
            if prop.get("address"):
                print(f"  {prop['address']}")
            if prop.get("mrt_distance"):
                print(f"  MRT: {prop['mrt_distance']}")
            commute_parts = []
            if prop.get("commute_driving"):
                commute_parts.append(f"{prop['commute_driving']} drive")
            if prop.get("commute_transit"):
                commute_parts.append(f"{prop['commute_transit']} transit")
            if commute_parts:
                print(f"  Commute: {' | '.join(commute_parts)}")
            if prop.get("availability"):
                print(f"  {prop['availability']}")
            if prop.get("link"):
                print(f"  {prop['link']}")
            print()

    return 0 if properties else 2


if __name__ == "__main__":
    sys.exit(main())
