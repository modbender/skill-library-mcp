#!/usr/bin/env python3
"""
ha_bridge.py - Home Assistant REST API bridge for OpenClaw.

A lightweight CLI that lets the OpenClaw agent read energy data and call
services on a local Home Assistant instance. Zero external dependencies;
uses only Python stdlib.

Usage:
    python3 ha_bridge.py <command> [options]

Commands:
    status          Get the state of a specific entity
    discover        Find all energy-related entities
    energy-summary  One-shot energy dashboard snapshot
    call-service    Call a Home Assistant service
    history         Fetch recent state history for an entity

Environment:
    HA_URL    Base URL of Home Assistant (e.g. http://homeassistant.local:8123)
    HA_TOKEN  Long-Lived Access Token for authentication

Exit codes:
    0  Success
    1  API / network error
    2  Configuration error (missing HA_URL or HA_TOKEN)
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone


# ---------------------------------------------------------------------------
#  Configuration
# ---------------------------------------------------------------------------


def load_config() -> dict:
    """
    Read HA_URL and HA_TOKEN from the environment.

    Returns a config dict or exits with code 2 if not set.
    """
    ha_url = os.environ.get("HA_URL", "").rstrip("/")
    ha_token = os.environ.get("HA_TOKEN", "")

    errors = []
    if not ha_url:
        errors.append("HA_URL is not set")
    if not ha_token:
        errors.append("HA_TOKEN is not set")

    if errors:
        _error(
            "Configuration error: " + "; ".join(errors) + ". "
            "Set these environment variables.",
            exit_code=2,
        )

    return {"url": ha_url, "token": ha_token}


# ---------------------------------------------------------------------------
#  HA REST API Client
# ---------------------------------------------------------------------------


def ha_request(method: str, endpoint: str, config: dict, payload: dict = None) -> dict:
    """
    Make an authenticated HTTP request to the Home Assistant REST API.

    Args:
        method:   HTTP method (GET or POST)
        endpoint: API path, e.g. "/api/states/sensor.electricity_price"
        config:   Dict with 'url' and 'token' keys
        payload:  Optional JSON body for POST requests

    Returns:
        Parsed JSON response (dict or list).

    Raises SystemExit on network / API errors (exit code 1).
    """
    url = f"{config['url']}{endpoint}"
    headers = {
        "Authorization": f"Bearer {config['token']}",
        "Content-Type": "application/json",
    }

    data = json.dumps(payload).encode("utf-8") if payload else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        detail = ""
        try:
            detail = exc.read().decode("utf-8")
        except Exception:
            pass
        _error(f"HA API returned HTTP {exc.code} for {method} {endpoint}: {detail}")
    except urllib.error.URLError as exc:
        _error(f"Cannot reach Home Assistant at {config['url']}: {exc.reason}")
    except Exception as exc:
        _error(f"Unexpected error talking to HA: {exc}")


# ---------------------------------------------------------------------------
#  Read Commands
# ---------------------------------------------------------------------------


# Energy-related device_class values used for auto-discovery.
ENERGY_DEVICE_CLASSES = {
    "energy",       # kWh sensors (grid import, export, device consumption)
    "power",        # W/kW instantaneous power draw
    "monetary",     # Cost / price sensors
    "battery",      # Battery state-of-charge
    "gas",          # Gas consumption
    "voltage",      # Grid voltage
    "current",      # Amperage
}


def get_entity_state(entity_id: str, config: dict) -> dict:
    """
    Fetch the full state object for a single entity.

    Returns dict with: entity_id, state, attributes, last_changed, last_updated.
    """
    result = ha_request("GET", f"/api/states/{entity_id}", config)
    return _format_state(result)


def discover_energy_entities(config: dict) -> list:
    """
    Scan all HA entities and return those relevant to energy management.

    Filters by device_class (energy, power, monetary, battery, gas) and also
    catches entities whose entity_id contains energy-related keywords.
    """
    all_states = ha_request("GET", "/api/states", config)

    # Keywords to match in entity_id for entities that may lack device_class
    ENERGY_KEYWORDS = {
        "energy", "power", "electricity", "solar", "battery", "grid",
        "consumption", "production", "tariff", "price", "cost", "kwh",
        "charger", "ev_charger", "inverter", "soc",
    }

    results = []
    for entity in all_states:
        attrs = entity.get("attributes", {})
        device_class = attrs.get("device_class", "")
        eid = entity.get("entity_id", "")

        # Match by device_class
        if device_class in ENERGY_DEVICE_CLASSES:
            results.append(_format_state(entity))
            continue

        # Match by keyword in entity_id
        eid_lower = eid.lower()
        if any(kw in eid_lower for kw in ENERGY_KEYWORDS):
            results.append(_format_state(entity))

    return results


def build_energy_summary(config: dict) -> dict:
    """
    Build a one-shot energy dashboard snapshot.

    Groups discovered energy entities into categories:
      - pricing:     Electricity price / cost sensors
      - consumption: Grid import, device energy usage
      - production:  Solar / wind generation
      - storage:     Battery SOC and power
      - devices:     Controllable switches and high-draw appliances

    This gives the agent everything it needs to reason about load shifting
    in a single call.
    """
    entities = discover_energy_entities(config)

    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pricing": [],
        "consumption": [],
        "production": [],
        "storage": [],
        "devices": [],
        "other_energy": [],
    }

    for ent in entities:
        eid = ent["entity_id"].lower()
        dc = ent.get("attributes", {}).get("device_class", "")

        if dc == "monetary" or _matches_any(eid, ["price", "cost", "tariff", "rate"]):
            summary["pricing"].append(ent)
        elif dc == "battery" or _matches_any(eid, ["battery", "soc", "storage"]):
            summary["storage"].append(ent)
        elif _matches_any(eid, ["solar", "pv", "production", "generation", "inverter"]):
            summary["production"].append(ent)
        elif _matches_any(eid, ["grid", "consumption", "import", "usage", "demand"]):
            summary["consumption"].append(ent)
        elif eid.startswith("switch.") or _matches_any(eid, ["charger", "ev", "dishwasher", "washer", "dryer", "pool", "pump", "heater"]):
            summary["devices"].append(ent)
        else:
            summary["other_energy"].append(ent)

    # Add counts for quick scanning
    summary["entity_counts"] = {
        cat: len(items) for cat, items in summary.items()
        if isinstance(items, list)
    }

    return summary


def get_entity_history(entity_id: str, hours: float, config: dict) -> list:
    """
    Fetch the state history for an entity over the last N hours.

    Uses GET /api/history/period/<timestamp>?filter_entity_id=<id>
    Returns a flat list of state change objects.
    """
    start = datetime.now(timezone.utc) - timedelta(hours=hours)
    ts = start.strftime("%Y-%m-%dT%H:%M:%S")
    endpoint = f"/api/history/period/{ts}?filter_entity_id={entity_id}&minimal_response&no_attributes"
    result = ha_request("GET", endpoint, config)

    # API returns [[state1, state2, ...]] - a list of lists grouped by entity
    if result and isinstance(result, list) and len(result) > 0:
        return result[0]
    return []


# ---------------------------------------------------------------------------
#  Write Commands
# ---------------------------------------------------------------------------


# Service domains allowed for call-service. Restricted to energy-related
# domains to prevent misuse (e.g. lock/unlock, alarm_control_panel).
ALLOWED_SERVICE_DOMAINS = {
    "switch",          # Toggle devices (EV charger, pool pump, water heater)
    "automation",      # Trigger energy automations
    "script",          # Run energy management scripts
    "climate",         # HVAC pre-conditioning setpoints
    "water_heater",    # Water heater scheduling
    "input_boolean",   # Toggle helper entities
    "input_number",    # Set numeric helpers (e.g. setpoint overrides)
    "number",          # Device number controls (e.g. charge current limit)
}


def call_service(domain: str, service: str, data: dict, config: dict) -> dict:
    """
    Call a Home Assistant service (energy-related domains only).

    Args:
        domain:  Service domain (e.g. "switch", "automation", "script")
        service: Service name (e.g. "turn_on", "trigger")
        data:    Service data dict (typically includes "entity_id")
        config:  HA connection config

    Example:
        call_service("switch", "turn_on", {"entity_id": "switch.ev_charger"}, cfg)

    Returns the API response (list of affected states).

    Raises SystemExit (code 2) if the domain is not in the allowlist.
    """
    if domain not in ALLOWED_SERVICE_DOMAINS:
        _error(
            f"Domain '{domain}' is not allowed. "
            f"Permitted domains: {', '.join(sorted(ALLOWED_SERVICE_DOMAINS))}. "
            "This skill is restricted to energy-related services.",
            exit_code=2,
        )
    endpoint = f"/api/services/{domain}/{service}"
    return ha_request("POST", endpoint, config, payload=data)


# ---------------------------------------------------------------------------
#  Helpers
# ---------------------------------------------------------------------------


def _format_state(raw: dict) -> dict:
    """Normalize an HA state object to a clean, flat-ish dict."""
    return {
        "entity_id": raw.get("entity_id", ""),
        "state": raw.get("state", ""),
        "attributes": raw.get("attributes", {}),
        "last_changed": raw.get("last_changed", ""),
        "last_updated": raw.get("last_updated", ""),
    }


def _matches_any(text: str, keywords: list) -> bool:
    """Return True if any keyword appears in text."""
    return any(kw in text for kw in keywords)


def _output(data) -> None:
    """Print JSON to stdout (agent-facing output)."""
    print(json.dumps(data, indent=2, default=str))


def _error(message: str, exit_code: int = 1) -> None:
    """Print error to stderr and exit."""
    print(json.dumps({"error": message}), file=sys.stderr)
    sys.exit(exit_code)


# ---------------------------------------------------------------------------
#  CLI Argument Parsing
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog="ha_bridge.py",
        description=(
            "Home Assistant energy bridge for OpenClaw. "
            "Read energy data and call services via the HA REST API."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- status ---
    p_status = subparsers.add_parser(
        "status",
        help="Get the state of a specific entity",
    )
    p_status.add_argument(
        "entity_id",
        help="Entity ID to query (e.g. sensor.electricity_price)",
    )

    # --- discover ---
    subparsers.add_parser(
        "discover",
        help="Find all energy-related entities in Home Assistant",
    )

    # --- energy-summary ---
    subparsers.add_parser(
        "energy-summary",
        help="One-shot energy dashboard snapshot (prices, consumption, solar, batteries)",
    )

    # --- call-service ---
    p_call = subparsers.add_parser(
        "call-service",
        help="Call a Home Assistant service (e.g. switch/turn_on)",
    )
    p_call.add_argument(
        "service_target",
        help="Service as domain/service (e.g. switch/turn_on, automation/trigger)",
    )
    p_call.add_argument(
        "--entity-id",
        required=True,
        help="Target entity ID (e.g. switch.ev_charger)",
    )
    p_call.add_argument(
        "--data",
        default="{}",
        help='Additional service data as JSON string (e.g. \'{"brightness": 100}\')',
    )

    # --- history ---
    p_hist = subparsers.add_parser(
        "history",
        help="Fetch recent state history for an entity",
    )
    p_hist.add_argument(
        "entity_id",
        help="Entity ID to query history for",
    )
    p_hist.add_argument(
        "--hours",
        type=float,
        default=24,
        help="How many hours of history to fetch (default: 24)",
    )

    return parser


# ---------------------------------------------------------------------------
#  Main
# ---------------------------------------------------------------------------


def main():
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()
    config = load_config()

    if args.command == "status":
        result = get_entity_state(args.entity_id, config)
        _output(result)

    elif args.command == "discover":
        results = discover_energy_entities(config)
        _output({"count": len(results), "entities": results})

    elif args.command == "energy-summary":
        summary = build_energy_summary(config)
        _output(summary)

    elif args.command == "call-service":
        # Parse "domain/service" format
        parts = args.service_target.split("/", 1)
        if len(parts) != 2:
            _error(
                f"Invalid service format '{args.service_target}'. "
                "Use domain/service (e.g. switch/turn_on)",
                exit_code=2,
            )
        domain, service = parts

        # Build service data
        try:
            extra_data = json.loads(args.data)
        except json.JSONDecodeError as exc:
            _error(f"Invalid JSON in --data: {exc}", exit_code=2)

        service_data = {"entity_id": args.entity_id, **extra_data}
        result = call_service(domain, service, service_data, config)
        _output({"service": f"{domain}.{service}", "result": result})

    elif args.command == "history":
        results = get_entity_history(args.entity_id, args.hours, config)
        _output({"entity_id": args.entity_id, "hours": args.hours, "states": results})


if __name__ == "__main__":
    main()
