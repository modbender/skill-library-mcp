"""
PackageTracker — Core tracking library.
Tracks shipments via 17track API. Outputs notifications to stdout for OpenClaw messaging.
"""

import json
import os
import re
import sqlite3
from datetime import datetime, timezone

import httpx
from dotenv import load_dotenv

# ── Config ──────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

API_KEY = os.getenv("SEVENTEEN_TRACK_API_KEY", "")

API_BASE = "https://api.17track.net/track/v2.2"
DB_PATH = os.path.join(BASE_DIR, "data", "tracker.db")

# ── Status mapping ──────────────────────────────────────────────────

STATUS_MAP = {
    0: "Not Found",
    10: "In Transit",
    20: "Expired",
    30: "Pick Up",
    35: "Undelivered",
    40: "Delivered",
    50: "Alert",
}

STATUS_EMOJI = {
    "pending": "⏳",
    "Not Found": "❓",
    "In Transit": "🚚",
    "Expired": "⌛",
    "Pick Up": "📬",
    "Undelivered": "⚠️",
    "Delivered": "✅",
    "Alert": "🚨",
}

# ── Carrier detection ──────────────────────────────────────────────

CARRIER_PATTERNS = [
    # (name, 17track carrier code, regex)
    ("CTT Portugal", 2151, re.compile(r"^[A-Z]{2}\d{9}PT$", re.I)),
    ("China Post", 3011, re.compile(r"^[A-Z]{2}\d{9}CN$", re.I)),
    ("Royal Mail", 1051, re.compile(r"^[A-Z]{2}\d{9}GB$", re.I)),
    ("La Poste", 1031, re.compile(r"^[A-Z]{2}\d{9}FR$", re.I)),
    ("Deutsche Post", 1011, re.compile(r"^[A-Z]{2}\d{9}DE$", re.I)),
    ("USPS", 100001, re.compile(r"^(94|92|93|94)\d{18,22}$")),
    ("PostNL", 1071, re.compile(r"^3S[A-Z0-9]{13,15}$", re.I)),
    ("UPS", 100002, re.compile(r"^1Z[A-Z0-9]{16}$", re.I)),
    ("FedEx", 100003, re.compile(r"^\d{12}(\d{3})?(\d{5})?(\d{7})?$")),
    ("DHL", 100001, re.compile(r"^\d{10,11}$")),
]

# ── Tracking URLs ──────────────────────────────────────────────────

TRACKING_URLS = {
    "FedEx": "https://www.fedex.com/fedextrack/?trknbr={tn}",
    "UPS": "https://www.ups.com/track?tracknum={tn}",
    "DHL": "https://www.dhl.com/en/express/tracking.html?AWB={tn}",
    "CTT Portugal": "https://www.ctt.pt/feapl_2/app/open/objectSearch/objectSearch.jspx?objects={tn}",
    "USPS": "https://tools.usps.com/go/TrackConfirmAction?tLabels={tn}",
    "Royal Mail": "https://www.royalmail.com/track-your-item#/tracking-results/{tn}",
    "La Poste": "https://www.laposte.fr/outils/suivre-vos-envois?code={tn}",
    "Deutsche Post": "https://www.deutschepost.de/de/s/sendungsverfolgung.html?piececode={tn}",
    "PostNL": "https://jouw.postnl.nl/track-and-trace/{tn}",
    "China Post": "https://t.17track.net/en#nums={tn}",
}

FALLBACK_TRACKING_URL = "https://t.17track.net/en#nums={tn}"


def get_tracking_url(tracking_number: str, carrier: str | None = None) -> str:
    """Generate a clickable tracking URL for the given carrier.
    Falls back to 17track universal tracker if carrier is unknown."""
    tn = tracking_number.strip()
    if carrier:
        # Case-insensitive carrier lookup
        carrier_lower = carrier.lower()
        for name, url_tpl in TRACKING_URLS.items():
            if name.lower() == carrier_lower:
                return url_tpl.format(tn=tn)
    # Try auto-detect from tracking number pattern
    detected, _ = detect_carrier(tn)
    if detected and detected in TRACKING_URLS:
        return TRACKING_URLS[detected].format(tn=tn)
    return FALLBACK_TRACKING_URL.format(tn=tn)


def detect_carrier(tracking_number: str) -> tuple[str | None, int]:
    """Return (carrier_name, carrier_code). Code 0 = auto-detect."""
    tn = tracking_number.strip()
    for name, code, pattern in CARRIER_PATTERNS:
        if pattern.match(tn):
            return name, code
    return None, 0  # let 17track auto-detect


# ── Database ───────────────────────────────────────────────────────

def get_db() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    _init_db(conn)
    return conn


def _init_db(conn: sqlite3.Connection):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS packages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tracking_number TEXT NOT NULL UNIQUE,
            carrier TEXT,
            carrier_code INTEGER,
            description TEXT,
            status TEXT DEFAULT 'pending',
            last_event TEXT,
            last_event_date TEXT,
            last_checked TEXT,
            delivered_date TEXT,
            raw_data TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            active INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS tracking_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            package_id INTEGER REFERENCES packages(id),
            event_date TEXT,
            location TEXT,
            description TEXT,
            status_code TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS api_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            api_name TEXT,
            month TEXT,
            registrations_used INTEGER DEFAULT 0,
            UNIQUE(api_name, month)
        );
    """)
    conn.commit()


# ── 17track API ────────────────────────────────────────────────────

def _api_headers() -> dict:
    return {
        "17token": API_KEY,
        "Content-Type": "application/json",
    }


def _check_api_key():
    if not API_KEY:
        raise RuntimeError(
            "SEVENTEEN_TRACK_API_KEY is not set. "
            "Get a free API key at https://admin.17track.net and add it to .env"
        )


def _increment_registration_count(conn: sqlite3.Connection):
    """Track monthly registration usage (free tier: 100/month)."""
    month = datetime.now(timezone.utc).strftime("%Y-%m")
    conn.execute(
        """INSERT INTO api_usage (api_name, month, registrations_used)
           VALUES ('17track', ?, 1)
           ON CONFLICT(api_name, month)
           DO UPDATE SET registrations_used = registrations_used + 1""",
        (month,),
    )
    conn.commit()


def _get_registration_count(conn: sqlite3.Connection) -> int:
    month = datetime.now(timezone.utc).strftime("%Y-%m")
    row = conn.execute(
        "SELECT registrations_used FROM api_usage WHERE api_name='17track' AND month=?",
        (month,),
    ).fetchone()
    return row["registrations_used"] if row else 0


def register_tracking(tracking_number: str, carrier_code: int = 0) -> dict:
    """Register a tracking number with 17track (costs 1 registration quota).

    Free tier allows 100 registrations/month. Subsequent gettrackinfo
    calls for registered numbers are free and unlimited.
    """
    _check_api_key()
    payload = [{"number": tracking_number, "carrier": carrier_code}]
    with httpx.Client(timeout=30) as client:
        resp = client.post(
            f"{API_BASE}/register",
            headers=_api_headers(),
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()


def get_track_info(tracking_numbers: list[str]) -> dict:
    """Get tracking info for registered numbers (free, unlimited calls)."""
    _check_api_key()
    payload = [{"number": tn} for tn in tracking_numbers]
    with httpx.Client(timeout=30) as client:
        resp = client.post(
            f"{API_BASE}/gettrackinfo",
            headers=_api_headers(),
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()


def get_quota() -> dict:
    """Get current 17track API quota information."""
    _check_api_key()
    with httpx.Client(timeout=30) as client:
        resp = client.get(
            f"{API_BASE}/getquota",
            headers=_api_headers(),
        )
        resp.raise_for_status()
        return resp.json()


# ── Notifications ─────────────────────────────────────────────────

def format_notification(update_info: dict) -> str:
    """Format an update notification as plain text for OpenClaw messaging.
    
    The agent will relay this via its native message tool (Telegram, Signal,
    Discord, WhatsApp, etc.). Use emoji and clean formatting.
    """
    tn = update_info["tracking_number"]
    carrier = update_info["carrier"] or "Auto-detect"
    old_status = update_info["old_status"]
    new_status = update_info["new_status"]
    tracking_url = update_info["tracking_url"]
    description = update_info.get("description")
    latest_event = update_info.get("latest_event")
    
    emoji = "✅" if new_status == "Delivered" else "📦"
    status_change = f"{old_status} → {new_status}" if old_status != new_status else new_status
    
    lines = [
        f"{emoji} Package Update",
        f"📮 Tracking: {tn}",
        f"📦 Carrier: {carrier}",
        f"📊 Status: {status_change}",
    ]
    
    if description:
        lines.append(f"📝 Description: {description}")
    
    if latest_event:
        line = f"📍 Latest: {latest_event['description']}"
        if latest_event.get("location"):
            line += f" — {latest_event['location']}"
        if latest_event.get("date"):
            line += f" ({latest_event['date']})"
        lines.append(line)
    
    lines.append(f"🔗 Track online: {tracking_url}")
    
    return "\n".join(lines)


# ── Core functions ─────────────────────────────────────────────────

def add_package(
    tracking_number: str,
    description: str | None = None,
    carrier: str | None = None,
) -> dict:
    """Add a new package to track.

    Returns dict with 'ok' bool, plus details on success or 'error' on failure.
    """
    tracking_number = tracking_number.strip().upper()
    if not tracking_number:
        return {"ok": False, "error": "Tracking number cannot be empty"}

    conn = get_db()

    # Check if already exists
    existing = conn.execute(
        "SELECT * FROM packages WHERE tracking_number = ?",
        (tracking_number,),
    ).fetchone()
    if existing:
        if existing["active"]:
            conn.close()
            return {"ok": False, "error": f"Package {tracking_number} is already being tracked"}
        else:
            # Reactivate
            conn.execute(
                "UPDATE packages SET active=1, updated_at=datetime('now') WHERE id=?",
                (existing["id"],),
            )
            conn.commit()
            conn.close()
            return {"ok": True, "message": "Package reactivated", "id": existing["id"]}

    # Detect carrier
    detected_carrier, carrier_code = detect_carrier(tracking_number)
    if carrier:
        detected_carrier = carrier

    # Check quota warning
    used = _get_registration_count(conn)
    if used >= 95:
        print(f"⚠️  Warning: {used}/100 registrations used this month!")
    if used >= 100:
        conn.close()
        return {
            "ok": False,
            "error": f"Monthly registration limit reached ({used}/100). "
                     "Wait for next month or upgrade your 17track plan.",
        }

    # Register with 17track
    register_result = None
    registered = False
    try:
        register_result = register_tracking(tracking_number, carrier_code)
        data = register_result.get("data", {})
        accepted = data.get("accepted", [])
        rejected = data.get("rejected", [])

        if accepted:
            registered = True
            _increment_registration_count(conn)
            if accepted[0].get("carrier"):
                carrier_code = accepted[0]["carrier"]
        elif rejected:
            err = rejected[0]
            error_code = err.get("error", {}).get("code", -1)
            error_msg = err.get("error", {}).get("message", "Unknown error")
            # Code -18010012 = already registered, that's fine
            if error_code == -18010012:
                registered = True
            else:
                conn.close()
                return {"ok": False, "error": f"17track rejected: {error_msg} (code {error_code})"}
    except RuntimeError as e:
        print(f"⚠️  {e}")
        print("   Package saved locally — register with 17track after adding API key.")
    except httpx.ConnectError:
        print("⚠️  Could not connect to 17track API (network issue)")
        print("   Package saved locally — will retry on next check.")
    except Exception as e:
        print(f"⚠️  17track registration failed: {e}")
        print("   Package saved locally — will retry on next check.")

    # Save to database
    conn.execute(
        """INSERT INTO packages
           (tracking_number, carrier, carrier_code, description, raw_data)
           VALUES (?, ?, ?, ?, ?)""",
        (
            tracking_number,
            detected_carrier,
            carrier_code,
            description,
            json.dumps(register_result) if register_result else None,
        ),
    )
    conn.commit()

    pkg = conn.execute(
        "SELECT * FROM packages WHERE tracking_number = ?",
        (tracking_number,),
    ).fetchone()

    result = {
        "ok": True,
        "id": pkg["id"],
        "tracking_number": tracking_number,
        "carrier": detected_carrier or "Auto-detect",
        "registered_17track": registered,
        "tracking_url": get_tracking_url(tracking_number, detected_carrier),
    }

    if registered:
        print(f"✅ Registered with 17track (quota: {_get_registration_count(conn)}/100 this month)")

    conn.close()
    return result


def check_updates(package_id: int | None = None) -> list[dict]:
    """Check for updates on active packages.

    Returns list of update dicts for packages that had changes.
    Prints notifications to stdout for OpenClaw to relay via native messaging.
    """
    conn = get_db()

    if package_id:
        packages = conn.execute(
            "SELECT * FROM packages WHERE id = ? AND active = 1",
            (package_id,),
        ).fetchall()
    else:
        packages = conn.execute(
            "SELECT * FROM packages WHERE active = 1"
        ).fetchall()

    if not packages:
        print("📭 No active packages to check")
        conn.close()
        return []

    tracking_numbers = [p["tracking_number"] for p in packages]
    updates = []

    try:
        result = get_track_info(tracking_numbers)
    except RuntimeError as e:
        print(f"❌ API key error: {e}")
        conn.close()
        return []
    except httpx.ConnectError:
        print("❌ Could not connect to 17track API — check your network")
        conn.close()
        return []
    except httpx.HTTPStatusError as e:
        print(f"❌ 17track API returned HTTP {e.response.status_code}: {e.response.text[:200]}")
        conn.close()
        return []
    except Exception as e:
        print(f"❌ Failed to fetch tracking info: {e}")
        conn.close()
        return []

    data = result.get("data", {})
    accepted = data.get("accepted", [])

    now = datetime.now(timezone.utc).isoformat()

    for item in accepted:
        tn = item.get("number", "")
        pkg = next((p for p in packages if p["tracking_number"] == tn), None)
        if not pkg:
            continue

        track = item.get("track", {})

        # Get status
        status_code = track.get("e", 0)
        new_status = STATUS_MAP.get(status_code, f"Unknown ({status_code})")
        old_status = pkg["status"]

        # Parse events from z0 (latest tracking provider)
        events = []
        z0 = track.get("z0", {})
        raw_events = z0.get("z", [])

        for ev in raw_events:
            events.append({
                "date": ev.get("a", ""),
                "location": ev.get("z", ""),
                "description": ev.get("c", ""),
            })

        # Find new events
        existing_events = conn.execute(
            "SELECT event_date, description FROM tracking_events WHERE package_id = ?",
            (pkg["id"],),
        ).fetchall()
        existing_set = {(e["event_date"], e["description"]) for e in existing_events}

        new_events = [
            ev for ev in events
            if (ev["date"], ev["description"]) not in existing_set
        ]

        # Store new events
        for ev in new_events:
            conn.execute(
                """INSERT INTO tracking_events
                   (package_id, event_date, location, description, status_code)
                   VALUES (?, ?, ?, ?, ?)""",
                (pkg["id"], ev["date"], ev["location"], ev["description"], str(status_code)),
            )

        # Update package record
        latest_event = events[0] if events else None
        update_fields = {
            "status": new_status,
            "last_checked": now,
            "raw_data": json.dumps(item),
            "updated_at": now,
        }
        if latest_event:
            update_fields["last_event"] = latest_event["description"]
            update_fields["last_event_date"] = latest_event["date"]

        if status_code == 40:
            update_fields["delivered_date"] = now
            update_fields["active"] = 0

        set_clause = ", ".join(f"{k}=?" for k in update_fields)
        conn.execute(
            f"UPDATE packages SET {set_clause} WHERE id=?",
            (*update_fields.values(), pkg["id"]),
        )

        # Send notification if status changed or new events found
        if new_status != old_status or new_events:
            tracking_url = get_tracking_url(tn, pkg["carrier"])
            update_info = {
                "tracking_number": tn,
                "description": pkg["description"],
                "carrier": pkg["carrier"],
                "old_status": old_status,
                "new_status": new_status,
                "latest_event": latest_event,
                "new_events_count": len(new_events),
                "tracking_url": tracking_url,
            }
            updates.append(update_info)

            # Print notification to stdout for OpenClaw to relay
            print("\n" + "=" * 50)
            print(format_notification(update_info))
            print("=" * 50)

            status_emoji = STATUS_EMOJI.get(new_status, "📦")
            print(f"  {status_emoji} {tn}: {status_change}")
            if latest_event:
                print(f"     └─ {latest_event['description']}")

    conn.commit()
    conn.close()

    if not updates:
        print("📭 No new updates found")

    return updates


def list_packages(active_only: bool = True) -> list[dict]:
    """List tracked packages."""
    conn = get_db()
    if active_only:
        rows = conn.execute(
            "SELECT * FROM packages WHERE active = 1 ORDER BY created_at DESC"
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM packages ORDER BY active DESC, created_at DESC"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def remove_package(tracking_number: str) -> dict:
    """Deactivate a package (stop tracking)."""
    tracking_number = tracking_number.strip().upper()
    if not tracking_number:
        return {"ok": False, "error": "Tracking number cannot be empty"}

    conn = get_db()
    row = conn.execute(
        "SELECT * FROM packages WHERE tracking_number = ?",
        (tracking_number,),
    ).fetchone()
    if not row:
        conn.close()
        return {"ok": False, "error": f"Package {tracking_number} not found in database"}
    if not row["active"]:
        conn.close()
        return {"ok": False, "error": f"Package {tracking_number} is already inactive"}

    conn.execute(
        "UPDATE packages SET active=0, updated_at=datetime('now') WHERE id=?",
        (row["id"],),
    )
    conn.commit()
    conn.close()
    return {"ok": True, "message": f"Stopped tracking {tracking_number}"}


def get_package_details(tracking_number: str) -> dict | None:
    """Get full package details with event history and tracking URL."""
    tracking_number = tracking_number.strip().upper()
    conn = get_db()
    pkg = conn.execute(
        "SELECT * FROM packages WHERE tracking_number = ?",
        (tracking_number,),
    ).fetchone()
    if not pkg:
        conn.close()
        return None

    events = conn.execute(
        """SELECT * FROM tracking_events
           WHERE package_id = ?
           ORDER BY event_date DESC""",
        (pkg["id"],),
    ).fetchall()
    conn.close()

    pkg_dict = dict(pkg)
    pkg_dict["tracking_url"] = get_tracking_url(
        tracking_number, pkg_dict.get("carrier")
    )

    return {
        "package": pkg_dict,
        "events": [dict(e) for e in events],
    }


def get_api_quota() -> dict:
    """Get 17track quota and local usage stats."""
    result = {"local_usage": None, "api_quota": None}

    conn = get_db()
    used = _get_registration_count(conn)
    result["local_usage"] = {
        "month": datetime.now(timezone.utc).strftime("%Y-%m"),
        "registrations_used": used,
        "registrations_remaining": max(0, 100 - used),
    }
    conn.close()

    try:
        api_result = get_quota()
        result["api_quota"] = api_result
    except RuntimeError as e:
        result["api_error"] = str(e)
    except Exception as e:
        result["api_error"] = f"Failed to fetch quota: {e}"

    return result
