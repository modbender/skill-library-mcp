"""
Ontopo.com API client — Israel 🇮🇱
====================================
Reverse-engineered from serviceSdk.417f1a81.js + index.faa0fd78.js
All findings confirmed via live testing (March 2026).

Base:      https://ontopo.com/api
Auth:      POST /loginAnonymously → jwt_token; use as header: token: <jwt>
           (NOT Authorization: Bearer — wrong header returns 401)
Date fmt:  YYYYMMDD (e.g. "20260407")   ← CRITICAL: wrong format = sparse response
Time fmt:  HHMM (e.g. "1930")           ← CRITICAL: wrong format = no slots returned
Size:      string not int (e.g. "2")    ← CRITICAL: int returns no slots

Known Bib Gourmand or Plate restaurants bookable via Ontopo in Israel:
  (Israel is not yet in the Michelin index — use Maps/TimeOut for recommendations)
"""
import requests
import re
import time as _time

BASE = "https://ontopo.com/api"
DISTRIBUTOR = "15171493"       # Ontopo IL distributor slug
DISTRIBUTOR_VERSION = "7850"

_cached_token: str | None = None
_token_ts: float = 0
TOKEN_TTL = 3600  # assume 1hr validity (conservative)


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def get_token(force_refresh: bool = False) -> str:
    """Get anonymous JWT. Re-fetches if stale (>1hr). Short-lived per session."""
    global _cached_token, _token_ts
    if not force_refresh and _cached_token and (_time.time() - _token_ts) < TOKEN_TTL:
        return _cached_token
    r = requests.post(f"{BASE}/loginAnonymously", timeout=10)
    r.raise_for_status()
    _cached_token = r.json()["jwt_token"]
    _token_ts = _time.time()
    return _cached_token


def _auth_headers(token: str = None) -> dict:
    return {
        "token": token or get_token(),
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
    }


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def search_venue(name: str, token: str = None) -> list[dict]:
    """
    Search for a restaurant by name on Ontopo.
    Returns list of {slug (INTERNAL), title, address, ...}

    ⚠️  The 'slug' from this endpoint is the INTERNAL slug, not the postSlug.
        Use get_post_slug() to convert URL slug → postSlug for availability_search.
    """
    r = requests.get(
        f"{BASE}/venue_search",
        headers=_auth_headers(token),
        params={
            "slug": DISTRIBUTOR,
            "version": DISTRIBUTOR_VERSION,
            "terms": name,
            "locale": "en",
        },
        timeout=10,
    )
    return r.json() if r.ok else []


def get_post_slug(url_slug: str) -> str | None:
    """
    Resolve a restaurant's URL slug → postSlug (numeric string).
    Fetches the Ontopo SSR page and extracts postSlug from JSON-LD.

    Example:
        get_post_slug("taizu")  → "36960535"
        get_post_slug("mashya") → "45994738"
    """
    r = requests.get(
        f"https://ontopo.com/he/il/page/{url_slug}",
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=10,
    )
    m = re.search(r'"postSlug"\s*:\s*"(\d+)"', r.text)
    return m.group(1) if m else None


# ---------------------------------------------------------------------------
# Availability
# ---------------------------------------------------------------------------

def check_availability(
    post_slug: str,
    date: str,         # YYYYMMDD e.g. "20260407"
    time: str,         # HHMM    e.g. "1930"
    size: int,
    token: str = None,
) -> dict:
    """
    Check available time slots for a restaurant.

    Returns:
        {
          "available": bool,
          "method": "seat"|"standby"|"phone"|"disabled",
          "slots": [{"area", "time" (HHMM), "method"}],
          "confirmed_slots": [...],   # method == "seat"
          "standby_slots": [...],     # method == "standby"
          "availability_id": str,     # needed for book_slot()
          "alt_dates": [str],         # suggested alternative dates if fully booked
          "raw": dict,
        }
    """
    r = requests.post(
        f"{BASE}/availability_search",
        headers=_auth_headers(token),
        json={
            "slug": post_slug,
            "locale": "en",
            "criteria": {
                "size": str(size),    # ← must be string
                "date": date,         # ← YYYYMMDD
                "time": time,         # ← HHMM
            },
        },
        timeout=10,
    )
    d = r.json()

    # Sparse response = wrong date/time format
    areas = d.get("areas", [])
    if not areas:
        return {
            "available": False,
            "method": d.get("method", "unknown"),
            "slots": [],
            "confirmed_slots": [],
            "standby_slots": [],
            "alt_dates": d.get("dates", []),
            "alt_venues": d.get("venues", []),
            "availability_id": d.get("availability_id"),
            "raw": d,
        }

    slots = []
    for area in areas:
        for opt in area.get("options", []):
            slots.append({
                "area": area.get("name", ""),
                "time": opt.get("time", ""),   # HHMM
                "method": opt.get("method", ""),
            })

    confirmed = [s for s in slots if s["method"] == "seat"]
    standby = [s for s in slots if s["method"] == "standby"]

    return {
        "available": bool(confirmed),
        "method": d.get("method"),
        "slots": slots,
        "confirmed_slots": confirmed,
        "standby_slots": standby,
        "availability_id": d.get("availability_id"),
        "alt_dates": d.get("dates", []),
        "raw": d,
    }


# ---------------------------------------------------------------------------
# Booking
# ---------------------------------------------------------------------------

def initiate_booking(
    post_slug: str,
    availability_id: str,
    date: str,          # YYYYMMDD
    time: str,          # HHMM — the specific chosen slot
    size: int,
    token: str = None,
) -> dict:
    """
    Step 2 of booking: call /availability_search again WITH availability_id.
    Returns {"checkout_id": str} → redirect to checkout page for CC + confirmation.

    CONFIRMED flow (March 2026 live test):
      Step 1: POST /availability_search (no availability_id) → get availability_id
      Step 2: POST /availability_search (WITH availability_id) → get checkout_id
      Step 3: Open https://www.ontopo.co.il/en/checkout/<checkout_id>
              User enters name, phone, email, CREDIT CARD → confirms booking

    CC IS required at the checkout page (Taizu confirmed).
    Use browser co-pilot: open checkout URL, user fills in details.

    ⚠️ ALWAYS confirm with user before calling this.
    """
    r = requests.post(
        f"{BASE}/availability_search",
        headers=_auth_headers(token),
        json={
            "slug": post_slug,
            "locale": "en",
            "criteria": {
                "size": str(size),
                "date": date,
                "time": time,
            },
            "availability_id": availability_id,
        },
        timeout=10,
    )
    return r.json()


def get_checkout_url(checkout_id: str) -> str:
    """Returns the checkout page URL. User fills CC + personal details here."""
    return f"https://www.ontopo.co.il/en/checkout/{checkout_id}"


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def format_hhmm(hhmm: str) -> str:
    """'1930' → '19:30'"""
    return f"{hhmm[:2]}:{hhmm[2:]}" if len(hhmm) == 4 else hhmm


def format_availability(result: dict, name: str) -> str:
    """Human-readable availability summary for Telegram/chat output."""
    if not result["available"]:
        method = result.get("method", "unknown")
        label = {
            "phone": f"📞 {name} — phone bookings only (no online).",
            "disabled": f"❌ {name} — fully booked.",
            "unknown": f"⚠️ {name} — no availability.",
        }.get(method, f"⚠️ {name} — {method}.")

        alt = result.get("alt_dates", [])
        if alt:
            label += f"\n  📅 Next available: {', '.join(alt[:3])}"
        return label

    lines = [f"✅ *{name}* — available slots:"]
    seen = set()
    for s in result["confirmed_slots"]:
        key = (s["time"], s["area"])
        if key not in seen:
            seen.add(key)
            lines.append(f"  • {format_hhmm(s['time'])} — {s['area']}")

    if result["standby_slots"] and not result["confirmed_slots"]:
        lines = [f"⏳ *{name}* — waitlist only:"]
        seen = set()
        for s in result["standby_slots"][:4]:
            key = (s["time"], s["area"])
            if key not in seen:
                seen.add(key)
                lines.append(f"  • {format_hhmm(s['time'])} — {s['area']} (standby)")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Known venues (add as discovered)
# ---------------------------------------------------------------------------

KNOWN_SLUGS: dict[str, str] = {
    # name_key: postSlug
    "taizu": "36960535",
    "bar_51": "31338736",  # 59 HaYarkon St, TLV
    "mashya": "45994738",   # phone-only
}

# URL slugs (for get_post_slug)
KNOWN_URL_SLUGS: dict[str, str] = {
    "taizu": "taizu",
    "mashya": "mashya",
}


def discover_post_slug(internal_slug: str, restaurant_name: str) -> str | None:
    """
    Discover postSlug for a venue when the URL slug is unknown.
    Strategy: DuckDuckGo search for 'ontopo.com/en/il/page/<id>' pattern.
    Falls back to None if not found.
    """
    import subprocess
    query = f"site:ontopo.com {restaurant_name} tel aviv page"
    result = subprocess.run(
        ["curl", "-s", f"https://duckduckgo.com/html/?q={requests.utils.quote(query)}",
         "-H", "User-Agent: Mozilla/5.0"],
        capture_output=True, text=True, timeout=15
    )
    # Find page URLs
    matches = re.findall(r'ontopo\.com/(?:en|he)/il/page/(\d+)', result.stdout)
    for candidate in matches:
        # Verify it's the right venue
        r = requests.get(f"https://ontopo.com/en/il/page/{candidate}",
                         headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if restaurant_name.lower().replace(" ", "").replace("-", "") in r.text.lower().replace(" ", ""):
            return candidate
    return None
