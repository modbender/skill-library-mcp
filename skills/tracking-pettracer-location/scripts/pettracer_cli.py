#!/usr/bin/env python3
"""pettracer_cli.py — small CLI helper for PetTracer location lookups.

Designed for automation/agents:
- Reads secrets from env vars (preferred)
- Produces stable JSON for downstream tool use
- Emits structured JSON errors when --format json

Environment variables (preferred):
- PETTRACER_TOKEN              (bearer token; skips login)
- PETTRACER_USERNAME or PETTRACER_EMAIL
- PETTRACER_PASSWORD
- PETTRACER_API_BASE           (optional; default: https://portal.pettracer.com/api)

Exit codes:
- 0: success
- 1: generic error
- 2: invalid arguments / missing prerequisites
- 3: device/pet not found
- 4: authentication/authorisation error
- 5: timeout
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import socket
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_API_BASE_URL = "https://portal.pettracer.com/api"
API_BASE_URL = os.getenv("PETTRACER_API_BASE", DEFAULT_API_BASE_URL).rstrip("/")

LOGIN_ENDPOINT = "/user/login"
GET_CCS_ENDPOINT = "/map/getccs"
GET_POSITIONS_ENDPOINT = "/map/getccpositions"

DEFAULT_TIMEOUT_S = 20
DEFAULT_RETRIES = 2
USER_AGENT = "pettracer-agent-skill/0.3"


class ExitCode:
    OK = 0
    ERROR = 1
    INVALID_ARGS = 2
    NOT_FOUND = 3
    AUTH = 4
    TIMEOUT = 5


@dataclass(frozen=True)
class PetSelection:
    device_id: int
    name: str


class PetTracerApiError(RuntimeError):
    pass


class PetTracerAuthError(PetTracerApiError):
    pass


class PetTracerNotFoundError(PetTracerApiError):
    pass


# Common user-facing mode ids seen in the portal API. Values outside this map are emitted as raw ints.
MODE_NAME_BY_ID: dict[int, str] = {
    3: "Slow",
    7: "Slow+",
    2: "Normal",
    14: "Normal+",
    1: "Fast",
    8: "Fast+",
    11: "Live",  # sometimes referred to as "Search" mode
}


def _json_dumps(obj: Any, pretty: bool) -> str:
    if pretty:
        return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False)
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False)


def _parse_dt_api(s: Optional[str]) -> Optional[datetime]:
    """Parse PetTracer timestamps.

    Examples seen in the wild:
    - 2026-02-25T12:34:56.310+0000
    - 2026-02-25T12:34:56+0000
    - 2026-02-25T12:34:56Z
    """
    if not s or not isinstance(s, str):
        return None

    # Common patterns first
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass

    # Fallback to ISO 8601-ish parsing
    try:
        s2 = s.strip()
        if s2.endswith("Z"):
            s2 = s2[:-1] + "+00:00"
        # Convert +0000 to +00:00 for fromisoformat
        if len(s2) >= 5 and (s2[-5] in "+-") and s2[-2:].isdigit() and s2[-4:-2].isdigit() and s2[-3] != ":":
            s2 = s2[:-2] + ":" + s2[-2:]
        dt = datetime.fromisoformat(s2)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def _iso(dt: Optional[datetime]) -> Optional[str]:
    return dt.isoformat() if dt else None


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in metres."""
    r = 6371000.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def _battery_mv_to_percent(mv: Any) -> Optional[int]:
    """Estimate collar battery percent from millivolts.

    This is an approximation (the official API reports mV). The piecewise mapping mirrors
    public community mappings.
    """
    if mv is None:
        return None
    try:
        e = int(mv)
    except (TypeError, ValueError):
        return None

    e = max(3000, min(e, 4150))
    if e >= 4000:
        t = (e - 4000) / 150 * 17 + 83
    elif e >= 3900:
        t = (e - 3900) / 100 * 16 + 67
    elif e >= 3840:
        t = (e - 3840) / 60 * 17 + 50
    elif e >= 3760:
        t = (e - 3760) / 80 * 16 + 34
    elif e >= 3600:
        t = (e - 3600) / 160 * 17 + 17
    else:
        t = 0
    return int(round(t))


def _rssi_to_dbm(rssi: Any) -> Optional[float]:
    """Best-effort conversion of RSSI to dBm.

    Some integrations treat PetTracer's RSSI as a raw 0–255 value.
    If the value already looks like dBm (negative), return it unchanged.
    """
    if rssi is None:
        return None
    try:
        v = int(rssi)
    except (TypeError, ValueError):
        return None

    if v < 0:
        return float(v)

    # Formula used by at least one HA integration to match the portal.
    return (255 & v) / 2.0 - 130.0


def _dbm_to_percent(dbm: Optional[float]) -> Optional[int]:
    if dbm is None:
        return None
    try:
        # Formula used by at least one HA integration.
        pct = 100.0 * 1.35 * (1.0 - (dbm / -130.0))
        return int(round(max(0.0, min(100.0, pct))))
    except Exception:
        return None


def _env_first(*names: str) -> Optional[str]:
    for n in names:
        v = os.getenv(n)
        if v:
            return v
    return None


def _retry_delay_s(attempt: int, *, retry_after_s: Optional[int]) -> float:
    if retry_after_s is not None:
        return float(max(0, min(60, retry_after_s)))

    # Exponential backoff with jitter; capped to avoid long sleeps.
    base = 0.5 * (2**attempt)
    jitter = random.uniform(0.0, 0.25)
    return float(min(10.0, base + jitter))


def _request(
    method: str,
    endpoint_or_url: str,
    *,
    token: Optional[str] = None,
    json_body: Optional[Dict[str, Any]] = None,
    timeout_s: int = DEFAULT_TIMEOUT_S,
    retries: int = DEFAULT_RETRIES,
) -> Any:
    """Make a JSON request to the PetTracer REST API (stdlib-only).

    Retries are deliberately conservative (defaults to 2) and only kick in on:
    - transient HTTP errors (429, 5xx)
    - network errors / timeouts

    Auth errors (401/403) are not retried.
    """

    url = endpoint_or_url
    if endpoint_or_url.startswith("/"):
        url = f"{API_BASE_URL}{endpoint_or_url}"

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    data: Optional[bytes] = None
    if json_body is not None:
        data = json.dumps(json_body, separators=(",", ":")).encode("utf-8")
        headers["Content-Length"] = str(len(data))

    req = Request(url, data=data, headers=headers, method=method.upper())

    last_timeout: Optional[BaseException] = None
    last_err: Optional[BaseException] = None

    retries = max(0, int(retries))
    for attempt in range(retries + 1):
        try:
            with urlopen(req, timeout=timeout_s) as resp:
                raw = resp.read().decode("utf-8")
            try:
                return json.loads(raw)
            except json.JSONDecodeError as e:
                raise PetTracerApiError(f"Non-JSON response from {url}: {e}") from e

        except HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8")
            except Exception:
                pass

            if e.code in (401, 403):
                raise PetTracerAuthError(f"HTTP {e.code} {e.reason}: {body}".strip())

            # Retry on server errors / rate limiting
            if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                retry_after: Optional[int] = None
                try:
                    ra = e.headers.get("Retry-After")
                    if ra:
                        retry_after = int(float(str(ra).strip()))
                except Exception:
                    retry_after = None

                time.sleep(_retry_delay_s(attempt, retry_after_s=retry_after))
                continue

            raise PetTracerApiError(f"HTTP {e.code} {e.reason}: {body}".strip())

        except (socket.timeout, TimeoutError) as e:
            last_timeout = e
            if attempt < retries:
                time.sleep(_retry_delay_s(attempt, retry_after_s=None))
                continue
            raise TimeoutError(str(e))

        except URLError as e:
            reason = getattr(e, "reason", None)
            if isinstance(reason, (socket.timeout, TimeoutError)):
                last_timeout = e
                if attempt < retries:
                    time.sleep(_retry_delay_s(attempt, retry_after_s=None))
                    continue
                raise TimeoutError(str(e))

            last_err = e
            if attempt < retries:
                time.sleep(_retry_delay_s(attempt, retry_after_s=None))
                continue
            raise PetTracerApiError(f"Network error: {e}") from e

        except Exception as e:
            last_err = e
            if attempt < retries:
                time.sleep(_retry_delay_s(attempt, retry_after_s=None))
                continue
            raise

    # Defensive fallback (should be unreachable)
    if last_timeout is not None:
        raise TimeoutError(str(last_timeout))
    if last_err is not None:
        raise PetTracerApiError(str(last_err))
    raise PetTracerApiError("Unknown request failure")


def get_token_or_login(*, username: Optional[str], password: Optional[str], timeout_s: int, retries: int) -> str:
    """Return bearer token from env or by logging in."""
    token = _env_first("PETTRACER_TOKEN")
    if token:
        return token

    username = username or _env_first("PETTRACER_USERNAME", "PETTRACER_EMAIL")
    password = password or _env_first("PETTRACER_PASSWORD")

    if not username or not password:
        raise PetTracerAuthError(
            "Missing credentials. Set PETTRACER_TOKEN or (PETTRACER_USERNAME/PETTRACER_EMAIL + PETTRACER_PASSWORD)."
        )

    payload = {"login": username, "password": password}
    resp = _request("POST", LOGIN_ENDPOINT, json_body=payload, timeout_s=timeout_s, retries=retries)

    if not isinstance(resp, dict):
        raise PetTracerAuthError("Login response was not a JSON object.")

    token = resp.get("access_token") or resp.get("token") or resp.get("id_token")
    if not token:
        raise PetTracerAuthError("Login response did not contain an access token.")
    return str(token)


def fetch_devices(*, token: str, timeout_s: int, retries: int) -> List[Dict[str, Any]]:
    resp = _request("GET", GET_CCS_ENDPOINT, token=token, timeout_s=timeout_s, retries=retries)
    if not isinstance(resp, list):
        raise PetTracerApiError("Unexpected response from /map/getccs (expected a JSON list).")
    return resp


def _device_type(device: Dict[str, Any]) -> int:
    t = device.get("type")
    try:
        return int(t)
    except Exception:
        # Collars typically omit type or use 0; home stations use 1.
        return 0


def _device_type_name(device_type: int) -> str:
    if device_type == 1:
        return "homestation"
    return "collar"


def _device_name(device: Dict[str, Any]) -> str:
    details = device.get("details") or {}
    name = details.get("name")
    if isinstance(name, str) and name.strip():
        return name.strip()

    dev_id = device.get("id")
    if _device_type(device) == 1:
        return f"HomeStation {dev_id}"
    return f"Pet {dev_id}"


def select_device(
    devices: List[Dict[str, Any]],
    *,
    device_id: Optional[int],
    pet_name: Optional[str],
) -> PetSelection:
    """Choose a device.

    Selection rules (in order):
    1) If --device-id provided, use it.
    2) If --pet provided, match by details.name (case-insensitive). If no exact match,
       try a single substring match.
    3) If neither is provided and there is exactly one *collar* on the account, pick it.
    """

    if device_id is not None:
        for d in devices:
            try:
                if int(d.get("id", -1)) == int(device_id):
                    return PetSelection(device_id=int(device_id), name=_device_name(d))
            except Exception:
                continue
        raise PetTracerNotFoundError(
            f"No device found with id={device_id}. Available ids: {[d.get('id') for d in devices]}"
        )

    if pet_name:
        key = pet_name.casefold().strip()

        exact: List[Tuple[int, str]] = []
        for d in devices:
            name = _device_name(d)
            if name.casefold() == key:
                exact.append((int(d.get("id")), name))

        if len(exact) == 1:
            dev_id, name = exact[0]
            return PetSelection(device_id=dev_id, name=name)
        if len(exact) > 1:
            raise PetTracerNotFoundError(
                f"Multiple devices matched name={pet_name!r}. Disambiguate by id. Matches: {exact}"
            )

        # Substring match (safe only if unique)
        contains: List[Tuple[int, str]] = []
        for d in devices:
            name = _device_name(d)
            if key and key in name.casefold():
                contains.append((int(d.get("id")), name))

        if len(contains) == 1:
            dev_id, name = contains[0]
            return PetSelection(device_id=dev_id, name=name)
        if len(contains) > 1:
            raise PetTracerNotFoundError(
                f"Multiple devices partially matched name={pet_name!r}. Disambiguate by id. Matches: {contains}"
            )

        raise PetTracerNotFoundError(
            f"No device found with name={pet_name!r}. Available: {[ _device_name(d) for d in devices ]}"
        )

    collars = [d for d in devices if _device_type(d) == 0]
    if len(collars) == 1:
        d = collars[0]
        return PetSelection(device_id=int(d.get("id")), name=_device_name(d))

    if len(devices) == 1:
        d = devices[0]
        return PetSelection(device_id=int(d.get("id")), name=_device_name(d))

    raise PetTracerNotFoundError(
        "Multiple devices on this account. Provide --pet or --device-id. "
        f"Available: {[ (d.get('id'), _device_name(d)) for d in devices ]}"
    )


def _latest_position(device: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    """Return a position-like dict plus a source label.

    Collars typically store latest fix in device['lastPos'].
    Home stations may have posLat/posLong at the top level.
    """

    last_pos = device.get("lastPos")
    if isinstance(last_pos, dict):
        lat = last_pos.get("posLat")
        lon = last_pos.get("posLong")
        if lat is not None and lon is not None:
            return last_pos, "lastPos"

    lat = device.get("posLat")
    lon = device.get("posLong")
    if lat is not None and lon is not None:
        # Build a minimal position dict matching the collar shape.
        return {
            "posLat": lat,
            "posLong": lon,
            "timeMeasure": device.get("timeMeasure") or device.get("timeDb") or device.get("lastContact"),
            "timeDb": device.get("timeDb"),
            "acc": device.get("acc"),
            "horiPrec": device.get("horiPrec"),
            "sat": device.get("sat"),
            "rssi": device.get("rssi"),
        }, "top_level"

    return {}, "none"


def _summarise_device(device: Dict[str, Any], *, now: datetime) -> Dict[str, Any]:
    pos, pos_source = _latest_position(device)

    last_contact_dt = _parse_dt_api(device.get("lastContact"))
    last_fix_dt = _parse_dt_api(pos.get("timeMeasure")) or _parse_dt_api(pos.get("timeDb"))

    lat = pos.get("posLat")
    lon = pos.get("posLong")

    # Accuracy can be acc or horiPrec (HA integration uses fallback)
    accuracy = pos.get("acc") if pos.get("acc") is not None else pos.get("horiPrec")

    rssi_raw = pos.get("rssi")
    rssi_dbm = _rssi_to_dbm(rssi_raw)
    rssi_pct = _dbm_to_percent(rssi_dbm)

    mode_id = device.get("mode")
    try:
        mode_id_int = int(mode_id) if mode_id is not None else None
    except Exception:
        mode_id_int = None

    out: Dict[str, Any] = {
        "id": device.get("id"),
        "type": _device_type(device),
        "type_name": _device_type_name(_device_type(device)),
        "name": _device_name(device),
        "battery_mv": device.get("bat"),
        "battery_percent_est": _battery_mv_to_percent(device.get("bat")),
        "home": device.get("home"),
        "mode_id": mode_id_int,
        "mode_name": MODE_NAME_BY_ID.get(mode_id_int) if mode_id_int is not None else None,
        "last_contact": _iso(last_contact_dt) or device.get("lastContact"),
        "last_contact_age_s": int((now - last_contact_dt).total_seconds()) if last_contact_dt else None,
        "last_fix_time": _iso(last_fix_dt) or pos.get("timeMeasure") or pos.get("timeDb"),
        "last_fix_age_s": int((now - last_fix_dt).total_seconds()) if last_fix_dt else None,
        "position_source": pos_source,
        "last_fix": {
            "lat": float(lat) if lat is not None else None,
            "lon": float(lon) if lon is not None else None,
            "accuracy_m": accuracy,
            "sat": pos.get("sat"),
            "rssi_raw": rssi_raw,
            "rssi_dbm": rssi_dbm,
            "rssi_percent": rssi_pct,
        },
    }

    return out


def _emit(payload: Any, args: argparse.Namespace) -> None:
    if args.format == "json":
        print(_json_dumps(payload, args.pretty))
    else:
        # minimal human output
        if isinstance(payload, dict) and "devices" in payload:
            for d in payload["devices"]:
                fix = d.get("last_fix", {})
                print(
                    f"{d.get('id')}: {d.get('name')}  "
                    f"last_fix={d.get('last_fix_time')}  "
                    f"bat={d.get('battery_percent_est')}%/{d.get('battery_mv')}mV  "
                    f"lat={fix.get('lat')} lon={fix.get('lon')}"
                )
        else:
            print(payload)


def _emit_error(
    args: argparse.Namespace,
    *,
    error_type: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
) -> None:
    if getattr(args, "format", "json") == "json":
        err: Dict[str, Any] = {"error": {"type": error_type, "message": message}}
        if details:
            err["error"]["details"] = details
        print(_json_dumps(err, getattr(args, "pretty", False)))
    else:
        print(f"{error_type}: {message}", file=sys.stderr)
        if details:
            print(details, file=sys.stderr)


def cmd_list(args: argparse.Namespace) -> int:
    token = get_token_or_login(username=args.username, password=args.password, timeout_s=args.timeout_s, retries=args.retries)
    devices = fetch_devices(token=token, timeout_s=args.timeout_s, retries=args.retries)

    now = datetime.now(timezone.utc)
    payload = {"devices": [_summarise_device(d, now=now) for d in devices]}
    _emit(payload, args)
    return ExitCode.OK


def cmd_locate(args: argparse.Namespace) -> int:
    token = get_token_or_login(username=args.username, password=args.password, timeout_s=args.timeout_s, retries=args.retries)
    devices = fetch_devices(token=token, timeout_s=args.timeout_s, retries=args.retries)

    sel = select_device(devices, device_id=args.device_id, pet_name=args.pet)
    device = next(d for d in devices if int(d.get("id")) == sel.device_id)

    now = datetime.now(timezone.utc)
    summary = _summarise_device(device, now=now)

    pos = summary.get("last_fix", {})
    lat = pos.get("lat")
    lon = pos.get("lon")

    # Staleness heuristic (for “recent vs stale” answers). Defaults can be overridden.
    stale_after_s = int(float(args.stale_after_min) * 60)
    fix_age_s = summary.get("last_fix_age_s")
    is_fix_stale = (fix_age_s is not None) and (int(fix_age_s) > stale_after_s)

    if lat is None or lon is None:
        payload = {
            "pet": {"id": sel.device_id, "name": sel.name},
            "device_type": summary.get("type_name"),
            "error": "no_recent_fix",
            "last_contact": summary.get("last_contact"),
            "last_contact_age_s": summary.get("last_contact_age_s"),
            "battery_mv": summary.get("battery_mv"),
            "battery_percent_est": summary.get("battery_percent_est"),
            "mode_id": summary.get("mode_id"),
            "mode_name": summary.get("mode_name"),
            "stale_after_s": stale_after_s,
        }
        _emit(payload, args)
        return ExitCode.OK

    distance_m: Optional[float] = None
    inside_geofence: Optional[bool] = None
    if args.home_lat is not None and args.home_lon is not None:
        distance_m = _haversine_m(float(lat), float(lon), float(args.home_lat), float(args.home_lon))
        if args.geofence_radius_m is not None:
            inside_geofence = distance_m <= float(args.geofence_radius_m)

    payload = {
        "pet": {"id": sel.device_id, "name": sel.name},
        "device_type": summary.get("type_name"),
        "last_fix": {
            "lat": float(lat),
            "lon": float(lon),
            "time": summary.get("last_fix_time"),
            "accuracy_m": pos.get("accuracy_m"),
            "sat": pos.get("sat"),
            "rssi_raw": pos.get("rssi_raw"),
            "rssi_dbm": pos.get("rssi_dbm"),
            "rssi_percent": pos.get("rssi_percent"),
        },
        "last_fix_age_s": summary.get("last_fix_age_s"),
        "stale_after_s": stale_after_s,
        "is_fix_stale": is_fix_stale,
        "last_contact": summary.get("last_contact"),
        "last_contact_age_s": summary.get("last_contact_age_s"),
        "battery_mv": summary.get("battery_mv"),
        "battery_percent_est": summary.get("battery_percent_est"),
        "home": summary.get("home"),
        "mode_id": summary.get("mode_id"),
        "mode_name": summary.get("mode_name"),
        "distance_to_home_m": distance_m,
        "inside_geofence": inside_geofence,
        "position_source": summary.get("position_source"),
        "links": {
            "google_maps": f"https://www.google.com/maps?q={lat},{lon}",
            "openstreetmap": f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=18/{lat}/{lon}",
        },
    }
    _emit(payload, args)
    return ExitCode.OK


def _parse_ms(value: str) -> int:
    try:
        return int(value)
    except ValueError as e:
        raise argparse.ArgumentTypeError("must be an integer (epoch ms)") from e


def cmd_history(args: argparse.Namespace) -> int:
    token = get_token_or_login(username=args.username, password=args.password, timeout_s=args.timeout_s, retries=args.retries)
    devices = fetch_devices(token=token, timeout_s=args.timeout_s, retries=args.retries)

    sel = select_device(devices, device_id=args.device_id, pet_name=args.pet)

    # Time window
    if args.from_ms is not None and args.to_ms is not None:
        filter_ms = args.from_ms
        to_ms = args.to_ms
    else:
        now = datetime.now(timezone.utc)
        to_ms = int(now.timestamp() * 1000)
        filter_ms = int((now - timedelta(hours=float(args.hours))).timestamp() * 1000)

    body = {"devId": sel.device_id, "filterTime": filter_ms, "toTime": to_ms}
    resp = _request("POST", GET_POSITIONS_ENDPOINT, token=token, json_body=body, timeout_s=args.timeout_s, retries=args.retries)
    if not isinstance(resp, list):
        raise PetTracerApiError("Unexpected response from /map/getccpositions (expected a JSON list).")

    positions: List[Dict[str, Any]] = []
    for item in resp:
        if not isinstance(item, dict):
            continue
        t = _parse_dt_api(item.get("timeMeasure")) or _parse_dt_api(item.get("timeDb"))
        lat = item.get("posLat")
        lon = item.get("posLong")
        accuracy = item.get("acc") if item.get("acc") is not None else item.get("horiPrec")
        rssi_raw = item.get("rssi")
        rssi_dbm = _rssi_to_dbm(rssi_raw)
        rssi_pct = _dbm_to_percent(rssi_dbm)

        positions.append(
            {
                "lat": float(lat) if lat is not None else None,
                "lon": float(lon) if lon is not None else None,
                "time": _iso(t) or item.get("timeMeasure") or item.get("timeDb"),
                "accuracy_m": accuracy,
                "sat": item.get("sat"),
                "rssi_raw": rssi_raw,
                "rssi_dbm": rssi_dbm,
                "rssi_percent": rssi_pct,
            }
        )

    if args.limit is not None:
        positions = positions[: int(args.limit)]

    payload = {
        "pet": {"id": sel.device_id, "name": sel.name},
        "window": {"from_ms": filter_ms, "to_ms": to_ms},
        "count": len(positions),
        "positions": positions,
    }
    _emit(payload, args)
    return ExitCode.OK


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="pettracer_cli.py", add_help=True)

    # Global options.
    #
    # NOTE: These are intentionally duplicated on each subcommand (via common_global) so callers can
    # place flags either before or after the subcommand, e.g.:
    #   pettracer_cli.py list --format json --pretty
    #   pettracer_cli.py --format json --pretty list
    p.add_argument("--timeout-s", type=int, default=DEFAULT_TIMEOUT_S, help="Request timeout in seconds.")
    p.add_argument(
        "--retries",
        type=int,
        default=int(os.getenv("PETTRACER_RETRIES", str(DEFAULT_RETRIES))),
        help=f"Retries for transient failures (default: {DEFAULT_RETRIES}). Set 0 to disable.",
    )
    p.add_argument("--username", help="PetTracer login (prefer env var PETTRACER_USERNAME).")
    p.add_argument("--password", help="PetTracer password (prefer env var PETTRACER_PASSWORD).")
    p.add_argument("--format", choices=["json", "text"], default="json", help="Output format.")
    p.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")

    # Subcommand-shared options (duplicated here to allow flags after the command).
    common_global = argparse.ArgumentParser(add_help=False)
    common_global.add_argument("--timeout-s", type=int, default=DEFAULT_TIMEOUT_S)
    common_global.add_argument(
        "--retries",
        type=int,
        default=int(os.getenv("PETTRACER_RETRIES", str(DEFAULT_RETRIES))),
    )
    common_global.add_argument("--username")
    common_global.add_argument("--password")
    common_global.add_argument("--format", choices=["json", "text"], default="json")
    common_global.add_argument("--pretty", action="store_true")

    sub = p.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", parents=[common_global], help="List devices visible to the account.")
    p_list.set_defaults(func=cmd_list)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--device-id", type=int, help="PetTracer device id.")
    common.add_argument("--pet", help="Pet name (matches device.details.name).")

    p_loc = sub.add_parser(
        "locate",
        parents=[common_global, common],
        help="Get latest known location for a pet/device.",
    )
    p_loc.add_argument("--home-lat", type=float, help="Optional home latitude for distance/geofence.")
    p_loc.add_argument("--home-lon", type=float, help="Optional home longitude for distance/geofence.")
    p_loc.add_argument("--geofence-radius-m", type=float, help="Optional radius in metres to compute inside_geofence.")
    p_loc.add_argument(
        "--stale-after-min",
        type=float,
        default=15.0,
        help="Consider fixes older than this as stale (default: 15 minutes).",
    )
    p_loc.set_defaults(func=cmd_locate)

    p_hist = sub.add_parser("history", parents=[common_global, common], help="Get location history for a time window.")
    p_hist.add_argument("--hours", type=float, default=6.0, help="History window in hours (default: 6).")
    p_hist.add_argument("--from-ms", type=_parse_ms, help="Start time (epoch ms). Use with --to-ms.")
    p_hist.add_argument("--to-ms", type=_parse_ms, help="End time (epoch ms). Use with --from-ms.")
    p_hist.add_argument("--limit", type=int, help="Limit number of returned points (after API response).")
    p_hist.set_defaults(func=cmd_history)

    return p


def main() -> int:
    p = build_parser()
    args = p.parse_args()

    # Basic arg validation
    if args.cmd == "history" and ((args.from_ms is None) ^ (args.to_ms is None)):
        _emit_error(args, error_type="invalid_args", message="--from-ms and --to-ms must be used together")
        return ExitCode.INVALID_ARGS

    try:
        return int(args.func(args))
    except PetTracerNotFoundError as e:
        _emit_error(args, error_type="not_found", message=str(e))
        return ExitCode.NOT_FOUND
    except PetTracerAuthError as e:
        _emit_error(args, error_type="auth", message=str(e))
        return ExitCode.AUTH
    except TimeoutError as e:
        _emit_error(args, error_type="timeout", message=str(e))
        return ExitCode.TIMEOUT
    except PetTracerApiError as e:
        _emit_error(args, error_type="api_error", message=str(e))
        return ExitCode.ERROR
    except KeyboardInterrupt:
        _emit_error(args, error_type="interrupted", message="Interrupted")
        return ExitCode.ERROR


if __name__ == "__main__":
    raise SystemExit(main())
