"""
Unified Reservation Interface 🍽️
==================================
Single entry point for Kai and agent callers.

Quick usage:
    from skills.reservation import unified

    # Recommend + show availability for a specific request
    unified.handle("Book somewhere good in Messina for April 7, dinner for 4")

    # Or structured:
    report = unified.search_and_format(
        city="messina", date="20260407", time="1930", size=4
    )

⚠️ POLICIES (non-negotiable):
  1. Never auto-book. Always present options and wait for explicit user choice.
  2. Never store or transmit raw CC data.
  3. For OTP flows: prompt user for code, never assume.

Default credentials (from USER.md / MEMORY.md):
  name:  Yonatan Hyatt
  phone: configured per USER.md
  email: os.environ.get("RESERVATION_EMAIL", "your@email.com")
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import ontopo
import tabit
import recommender
import maps
from thefork import get_city_search_url as thefork_search_url, get_availability_url as thefork_avail_url
from opentable import get_restaurant_search_url as ot_search_url, get_booking_url as ot_booking_url, NYC_KNOWN

# ── Default user credentials ──────────────────────────────────────────────────
DEFAULT_USER = {
    "first_name": "Yonatan",
    "last_name": "Hyatt",
    "email": "os.environ.get("RESERVATION_EMAIL", "your@email.com")",
    "phone": os.environ.get("RESERVATION_PHONE", "+972500000000"),
    "name": "Yonatan Hyatt",
}

# ── Platform routing ──────────────────────────────────────────────────────────
# city (lowercase) → primary platforms in priority order
CITY_ROUTING = {
    "tel aviv":   ["ontopo", "tabit"],
    "tel-aviv":   ["ontopo", "tabit"],
    "jerusalem":  ["ontopo", "tabit"],
    "haifa":      ["ontopo", "tabit"],
    "eilat":      ["ontopo"],
    "herzliya":   ["ontopo", "tabit"],

    "marseille":  ["thefork"],
    "genoa":      ["thefork"],
    "genova":     ["thefork"],
    "messina":    ["thefork"],
    "valletta":   ["thefork"],
    "rome":       ["thefork"],
    "barcelona":  ["thefork"],
    "paris":      ["thefork"],
    "milan":      ["thefork"],
    "nice":       ["thefork"],

    "new york":   ["resy", "opentable"],
    "nyc":        ["resy", "opentable"],
    "new-york":   ["resy", "opentable"],
    "los angeles":["opentable"],
    "chicago":    ["opentable"],
}


def _get_platforms(city: str) -> list[str]:
    return CITY_ROUTING.get(city.lower(), ["thefork", "opentable"])


# ── Search & Recommend ────────────────────────────────────────────────────────

def search_and_format(
    city: str,
    date: str,       # Ontopo: YYYYMMDD | Tabit/others: YYYY-MM-DD — auto-converted
    time: str,       # HH:MM (Israel local) or HHMM — auto-normalized
    size: int,
    query: str = None,       # specific restaurant name (optional)
    family_mode: bool = False,  # surface family-friendly flags
) -> str:
    """
    Main entry point. Returns a formatted Telegram-ready string with:
    - Curated picks + Michelin/TimeOut recommendations
    - Live availability where possible (Ontopo for Israel)
    - Booking URLs for browser-handoff platforms (TheFork, Resy, etc.)
    """
    city_lower = city.lower()
    platforms = _get_platforms(city_lower)

    # Normalize date / time
    date_yyyymmdd = date.replace("-", "") if "-" in date else date  # for Ontopo
    date_iso = f"{date[:4]}-{date[4:6]}-{date[6:]}" if len(date) == 8 else date  # for Tabit
    time_hhmm = time.replace(":", "") if ":" in time else time  # for Ontopo
    time_hh_mm = f"{time[:2]}:{time[2:]}" if ":" not in time else time  # for Tabit/display

    lines = [f"🍽️ *{city.title()} — {date_iso} {time_hh_mm} for {size}*\n"]

    # ── Curated Picks ────────────────────────────────────────────────────────
    curated = maps.get_curated(city_lower)
    if curated:
        lines.append("*📍 Curated picks:*")
        for r in curated[:5]:
            kai = " ⭐" if r.get("kai_pick") else ""
            michelin_tag = f" [{r['michelin']}]" if r.get("michelin") else ""
            lines.append(f"• *{r['name']}*{kai}{michelin_tag} — {r.get('cuisine', '')}")
            if r.get("notes"):
                lines.append(f"  _{r['notes']}_")
            bk = r.get("booking_platform")
            if bk:
                url = _get_booking_url(r, city_lower, date_iso, time_hh_mm, size)
                lines.append(f"  🔗 {url}")
        lines.append("")

    # ── Live Availability (Israel / Ontopo) ──────────────────────────────────
    if "ontopo" in platforms and query:
        lines.append("*🇮🇱 Ontopo availability:*")
        venues = ontopo.search_venue(query)
        for v in venues[:3]:
            url_slug = (v.get("url") or "").rstrip("/").split("/")[-1]
            post_slug = ontopo.get_post_slug(url_slug)
            if post_slug:
                avail = ontopo.check_availability(post_slug, date_yyyymmdd, time_hhmm, size)
                lines.append(ontopo.format_availability(avail, v.get("title", query)))
            else:
                lines.append(f"• {v.get('title', query)} — could not resolve slug")
        lines.append("")

    # ── TheFork (Europe) ─────────────────────────────────────────────────────
    if "thefork" in platforms:
        lines.append("*🇪🇺 TheFork (browser booking):*")
        city_url = thefork_search_url(city_lower, covers=size, date=date_iso, time=time_hh_mm)
        lines.append(f"🔗 {city_url}")

        # Also surface any Michelin picks that have TheFork booking
        michelin = recommender.get_michelin(city_lower)
        fork_picks = [m for m in michelin if (m.get("booking_provider") or "").lower() == "thefork"]
        if fork_picks:
            lines.append("  _Michelin picks bookable via TheFork:_")
            for m in fork_picks[:4]:
                lines.append(f"  • *{m['name']}* {m['award']} — {m['cuisine']}")
                if m.get("booking_url"):
                    lines.append(f"    🔗 {m['booking_url']}")
        lines.append("")

    # ── OpenTable / Resy (USA) ────────────────────────────────────────────────
    if "opentable" in platforms or "resy" in platforms:
        lines.append("*🇺🇸 NYC — Resy / OpenTable:*")
        url = ot_search_url(city.replace(" ", "-").lower(), covers=size, date=date_iso, time=time_hh_mm)
        lines.append(f"🔗 OpenTable: {url}")
        lines.append(f"🔗 Resy: https://resy.com/cities/new-york?date={date_iso}&party_size={size}")
        lines.append("")

    # ── Michelin Summary ─────────────────────────────────────────────────────
    michelin = recommender.get_michelin(city_lower)
    if michelin:
        lines.append(f"*🔴 Michelin (no stars) — {len(michelin)} picks:*")
        for m in michelin[:5]:
            bk = f" | _{m.get('booking_provider', '—')}_" if m.get("booking_provider") else ""
            lines.append(f"• *{m['name']}* {m['award']} — {m['cuisine']}{bk}")
        lines.append("")

    # ── Time Out ─────────────────────────────────────────────────────────────
    timeout = recommender.get_timeout(city_lower)
    if timeout:
        lines.append("*⏰ Time Out top 5:*")
        for r in timeout[:5]:
            rank = f"#{r.get('rank', '?')} " if r.get("rank") else ""
            lines.append(f"• {rank}*{r['name']}*")

    return "\n".join(lines)


def _get_booking_url(restaurant: dict, city: str, date: str, time: str, size: int) -> str:
    """Resolve a booking URL for a curated restaurant entry."""
    platform = restaurant.get("booking_platform", "")
    if platform == "ontopo":
        slug = restaurant.get("ontopo_post_slug")
        return f"https://ontopo.com/en/il/page/{slug}" if slug else "https://ontopo.com"
    if platform == "tabit":
        org_id = restaurant.get("tabit_org_id", "")
        return f"https://tabitisrael.co.il/online-reservations/{org_id}" if org_id else "https://tabitisrael.co.il"
    if platform == "thefork":
        return thefork_search_url(city, covers=size, date=date, time=time)
    if platform == "resy":
        slug = restaurant.get("resy_slug") or restaurant["name"].lower().replace(" ", "-")
        return f"https://resy.com/cities/new-york/venues/{slug}?date={date}&party_size={size}"
    if platform == "opentable":
        restaurant_key = restaurant.get("opentable_key") or restaurant["name"].lower().replace(" ", "_")
        bk = ot_booking_url(restaurant_key, date, time, size)
        return bk.get("url", f"https://www.opentable.com/s?term={restaurant['name']}")
    if platform == "mozrest":
        return f"https://www.mozrest.com/search?q={restaurant['name']}&city={city}"
    return ""


# ── Booking flow ──────────────────────────────────────────────────────────────

def initiate_ontopo_booking(
    post_slug: str,
    availability_id: str,
    date: str,          # YYYYMMDD
    time: str,          # HHMM (chosen slot)
    size: int,
    user: dict = None,
    notes: str = "",
) -> dict:
    """
    Start an Ontopo booking. Returns checkout_id + checkout URL.
    ⚠️ Always confirm with user before calling.
    """
    u = {**DEFAULT_USER, **(user or {})}
    result = ontopo.initiate_booking(
        post_slug=post_slug,
        availability_id=availability_id,
        date=date,
        time=time,
        size=size,
        name=u["name"],
        phone=u["phone"],
        email=u["email"],
        notes=notes,
    )
    checkout_id = result.get("checkout_id")
    return {
        "checkout_id": checkout_id,
        "checkout_url": ontopo.get_checkout_url(checkout_id) if checkout_id else None,
        "raw": result,
    }


def initiate_tabit_availability(
    org_id: str,
    date: str,       # YYYY-MM-DD
    time: str,       # HH:MM
    size: int,
) -> dict:
    """
    Check Tabit availability.
    ⚠️ Creates a ~15 min table hold. Call delete_temp_reservation if user cancels.
    """
    return tabit.check_availability(org_id, date, time, size)


def confirm_tabit_booking(temp_id: str, org_id: str, bearer_token: str,
                          user: dict = None, notes: str = "") -> dict:
    """Confirm Tabit booking after OTP verified."""
    u = {**DEFAULT_USER, **(user or {})}
    return tabit.confirm_booking(
        temp_id=temp_id,
        org_id=org_id,
        first_name=u["first_name"],
        last_name=u["last_name"],
        phone=u["phone"],
        email=u["email"],
        bearer_token=bearer_token,
        notes=notes,
    )


def get_browser_handoff_url(platform: str, city: str = "", restaurant_url: str = "",
                             date: str = "", time: str = "", size: int = 2) -> str:
    """
    Get a pre-filled booking URL for browser co-pilot handoff.
    Used when platform requires human interaction (CC entry, OTP, CAPTCHA).
    """
    if platform == "thefork":
        if restaurant_url:
            return thefork_avail_url(restaurant_url, date, time, size)
        return thefork_search_url(city, covers=size, date=date, time=time)
    if platform in ("opentable", "resy"):
        url = ot_search_url(city.replace(" ", "-").lower(), covers=size, date=date, time=time)
        return url
    if platform == "tabit":
        return tabit.get_copilot_url("")
    return ""
