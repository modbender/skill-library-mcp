"""
Tabit reservation API — Israel 🇮🇱
=====================================
Reverse-engineered from tabitisrael.co.il JS bundles v5.3.0.

KEY DISCOVERY: The public GUID E3AE3D44-6FE4-4264-AD3A-54D44119F802 is the
global TG-Authorization key. Works for reading config and CHECKING availability,
but actual booking requires OTP-authenticated session.

Availability check via temp-reservations creates a real ~10-15 minute table hold.
Always DELETE it if the user decides not to book (delete_temp_reservation).

Auth:
  Check/Config: TG-Authorization: <GUID> + Origin: https://tabitisrael.co.il
  Booking:      OTP to user's phone → phone-verified Bearer token
"""
import requests
import time as _time
from datetime import datetime, timezone, timedelta

BRIDGE = "https://bridge.tabit.cloud"
TGM = "https://tgm-api.tabit.cloud"
TG_GUID = "E3AE3D44-6FE4-4264-AD3A-54D44119F802"
ORIGIN = "https://tabitisrael.co.il"

# Israel UTC offset (approximation — DST not handled; TODO)
# Winter (Oct–Mar): UTC+2   Summer (Mar–Oct): UTC+3
# For Apr (cruise): UTC+3
ISRAEL_UTC_OFFSET = 3   # change to 2 in winter


def _h(with_auth: bool = True, referer_slug: str = None) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Content-Type": "application/json",
        "Origin": ORIGIN,
    }
    if with_auth:
        headers["TG-Authorization"] = TG_GUID
    if referer_slug:
        headers["Referer"] = f"{ORIGIN}/online-reservations/{referer_slug}"
    return headers


def _to_utc_iso(date: str, time_str: str) -> str:
    """Convert 'YYYY-MM-DD', 'HH:MM' (Israel local) → UTC ISO string."""
    dt = datetime.strptime(f"{date} {time_str}", "%Y-%m-%d %H:%M")
    dt_utc = dt - timedelta(hours=ISRAEL_UTC_OFFSET)
    return dt_utc.strftime("%Y-%m-%dT%H:%M:%S.000Z")


# ---------------------------------------------------------------------------
# Restaurant Search
# ---------------------------------------------------------------------------

def search_venue(name: str) -> list[dict]:
    """
    Search Tabit restaurant directory by name.
    Returns list of {_id, name, reservation_method, address, url}
    reservation_method: "onlineBooking" | "phone" | "none"
    """
    r = requests.get(
        f"{BRIDGE}/organizations/search",
        params={"searchTerm": name},
        headers={
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json",
        },
        timeout=10,
    )
    if not r.ok:
        return []

    orgs = r.json().get("organizations", [])
    return [
        {
            "_id": o.get("_id"),
            "name": o.get("name"),
            "reservation_method": o.get("reservation", {}).get("method", "none"),
            "address": o.get("address"),
            "url": f"{ORIGIN}/online-reservations/{o.get('_id')}",
        }
        for o in orgs
    ]


def get_booking_config(org_id: str) -> dict:
    """
    Get booking configuration for a restaurant.
    Contains: default_group_size, max_group_size, future_reservation settings, etc.
    """
    r = requests.get(
        f"{TGM}/rsv/booking/configuration",
        params={"organization": org_id},
        headers=_h(),
        timeout=10,
    )
    return r.json() if r.ok else {}


# ---------------------------------------------------------------------------
# Availability (Temp Reservation)
# ---------------------------------------------------------------------------

def check_availability(
    org_id: str,
    date: str,          # "YYYY-MM-DD" in Israel local time
    time_str: str,      # "HH:MM" in Israel local time (e.g. "20:00")
    covers: int,
    standby: bool = False,
) -> dict:
    """
    Check availability by creating a temporary reservation.

    ⚠️  SIDE EFFECT: This creates a real hold (~15 min) on the restaurant's system.
        Call delete_temp_reservation() if the user does NOT proceed.

    Returns:
        {
          "available": bool,
          "temp_id": str | None,       # delete this if user cancels
          "org_id": str,               # pass to delete_temp_reservation
          "area": str,
          "reserved_from": str,        # ISO timestamp from Tabit
          "error_type": str | None,    # "no_availability" | "auth_error" | ...
        }
    """
    date_utc = _to_utc_iso(date, time_str)
    payload = {
        "organization": org_id,
        "type": "future_reservation",
        "standby_reservation": standby,
        "timestamp": int(_time.time() * 1000),
        "reservation_details": {
            "date": date_utc,
            "seats_count": covers,
            "preference": "first_available",
            "notes": "",
            "customer": {
                "first_name": "", "last_name": "",
                "email": "", "phone": "",
            },
        },
    }
    r = requests.post(
        f"{TGM}/rsv/booking/temp-reservations",
        json=payload,
        headers=_h(referer_slug=org_id),
        timeout=15,
    )
    d = r.json()
    temp_id = d.get("_id")
    desc = d.get("description_string", "")

    return {
        "available": bool(temp_id),
        "temp_id": temp_id,
        "org_id": org_id,
        "area": d.get("reservation_details", {}).get("table_area", ""),
        "reserved_from": d.get("reservation_details", {}).get("reserved_from", ""),
        "description_string": desc,
        "error_type": _classify_error(desc) if not temp_id else None,
        "raw": d,
    }


def _classify_error(desc: str) -> str:
    m = {
        "call_restaurant_error": "no_availability",
        "no_results": "auth_error",
        "fully_booked": "fully_booked",
    }
    for k, v in m.items():
        if k in desc:
            return v
    return "unknown"


def delete_temp_reservation(temp_id: str, org_id: str) -> bool:
    """
    Release a temp reservation. CALL THIS if the user does NOT confirm.
    """
    r = requests.delete(
        f"{TGM}/rsv/management/{temp_id}/customer_cancelled",
        params={"organization": org_id},
        headers=_h(),
        timeout=10,
    )
    return r.ok


# ---------------------------------------------------------------------------
# Booking (OTP-protected)
# ---------------------------------------------------------------------------

def request_otp(phone: str) -> bool:
    """Send OTP to user's phone. Returns True on success."""
    r = requests.post(
        f"{TGM}/users/otp",
        json={"phone": phone},
        headers=_h(),
        timeout=10,
    )
    return r.ok


def verify_otp(phone: str, otp_code: str) -> str | None:
    """Verify OTP and return Bearer token, or None on failure."""
    r = requests.post(
        f"{TGM}/users/verify-otp",
        json={"phone": phone, "code": otp_code},
        headers=_h(),
        timeout=10,
    )
    if r.ok:
        return r.json().get("token")
    return None


def confirm_booking(
    temp_id: str,
    org_id: str,
    first_name: str,
    last_name: str,
    phone: str,
    email: str,
    bearer_token: str,
    notes: str = "",
) -> dict:
    """
    Confirm a temp reservation with customer details.
    Requires OTP-verified bearer_token from verify_otp().

    Full booking flow:
    1. check_availability() → temp_id (table held)
    2. request_otp(phone)   → OTP sent
    3. verify_otp(phone, code) → bearer_token
    4. confirm_booking(temp_id, ..., bearer_token) → confirmed
    """
    auth_headers = {**_h(referer_slug=org_id), "Authorization": f"Bearer {bearer_token}"}
    payload = {
        "reservation_details": {
            "notes": notes,
            "customer": {
                "first_name": first_name,
                "last_name": last_name,
                "phone": phone,
                "email": email,
            },
            "send_notification": {"event_type": "online_booking_created"},
        }
    }
    r = requests.put(
        f"{TGM}/rsv/booking/temp-reservations/{temp_id}",
        json=payload,
        params={"organization": org_id},
        headers=auth_headers,
        timeout=10,
    )
    return r.json()


def get_copilot_url(org_id: str) -> str:
    """Get the browser URL for manual booking co-pilot."""
    return f"{ORIGIN}/online-reservations/{org_id}"


# ---------------------------------------------------------------------------
# Known organizations (add as discovered)
# ---------------------------------------------------------------------------

KNOWN_ORGS: dict[str, str] = {
    # RSV system (tgm-api.tabit.cloud) — table reservations
    "molam":              "67dc03b26adf5bfd252aff30",
    "thai_har_sinai":     "5bcc2b0ebfee100100dcac1d",
    "rothschild_48":      "62efaedc2edea179d043b73e",
    "cote":               "63c68a50c5406f71ae8c8a02",
    # NOTE: To discover org IDs, visit tabitisrael.co.il/site/<name>
    # and check the og:image URL for the ID fragment, OR look at network
    # calls to /rsv/booking/configuration?organization=<id>
}

# Tabit ORDER system org IDs (ros-tad.tabit.cloud) — takeout/delivery only, NOT reservations
# These come from tabitisrael.co.il/site/<name> pages
KNOWN_ORDER_ORGS: dict[str, str] = {
    "ha_achim":           "74fbd8341c4c375fe6fced6f",  # Ibn Gabirol 26 TLV — order/delivery only
}
