"""
OpenTable / Resy client — USA (NYC focus) 🇺🇸
===============================================
Direct API returns 403. Browser co-pilot is the only path.

OpenTable: General USA restaurants, worldwide
Resy:      Dominant in NYC for top-tier restaurants (Don Angie, Lilia, Via Carota, etc.)

Both are browser-handoff only. We construct pre-filled URLs.
"""
import requests

OT_BASE = "https://www.opentable.com"
RESY_BASE = "https://resy.com"


def get_restaurant_search_url(city: str, query: str = "", covers: int = 2,
                               date: str = "", time: str = "") -> str:
    """OpenTable search URL for a city."""
    url = f"{OT_BASE}/s?term={requests.utils.quote(query or 'restaurant')}&metroId=4"
    if covers:
        url += f"&covers={covers}"
    if date:
        url += f"&dateTime={date}T{time or '20:00'}:00"
    return url


def get_resy_url(venue_slug: str, city_slug: str, date: str, covers: int = 2) -> str:
    """Resy restaurant booking URL."""
    return f"{RESY_BASE}/cities/{city_slug}/venues/{venue_slug}?date={date}&party_size={covers}"


def get_booking_url(restaurant_key: str, date: str, time: str, covers: int) -> dict:
    """
    Get booking URL for a known NYC restaurant.
    Returns {"platform": str, "url": str}
    """
    info = NYC_KNOWN.get(restaurant_key)
    if not info:
        return {
            "platform": "opentable",
            "url": f"{OT_BASE}/s?term={requests.utils.quote(restaurant_key)}"
        }

    if info["platform"] == "resy":
        return {
            "platform": "resy",
            "url": get_resy_url(info["slug"], info.get("city_slug", "new-york"), date, covers),
        }
    elif info["platform"] == "opentable":
        ot_id = info.get("id", "")
        url = (f"{OT_BASE}/restref/booking/start?restref={ot_id}"
               f"&covers={covers}&dateTime={date}T{time}:00")
        return {"platform": "opentable", "url": url}

    return {"platform": "unknown", "url": ""}


# ── Known NYC restaurants ─────────────────────────────────────────────────────
NYC_KNOWN = {
    # Resy (most top-tier NYC spots)
    "adda":         {"platform": "resy",       "slug": "adda",         "city_slug": "new-york"},
    "tatiana":      {"platform": "resy",       "slug": "tatiana",      "city_slug": "new-york"},
    "don_angie":    {"platform": "resy",       "slug": "don-angie",    "city_slug": "new-york"},
    "lilia":        {"platform": "resy",       "slug": "lilia",        "city_slug": "new-york"},
    "via_carota":   {"platform": "resy",       "slug": "via-carota",   "city_slug": "new-york"},
    "carbone":      {"platform": "resy",       "slug": "carbone",      "city_slug": "new-york"},
    "joe_beef":     {"platform": "resy",       "slug": "joe-beef",     "city_slug": "new-york"},
    "smithereens":  {"platform": "resy",       "slug": "smithereens",  "city_slug": "new-york"},
    "borgo":        {"platform": "resy",       "slug": "borgo",        "city_slug": "new-york"},
    "theodora":     {"platform": "resy",       "slug": "theodora",     "city_slug": "new-york"},
    "roscioli_nyc": {"platform": "resy",       "slug": "roscioli-nyc", "city_slug": "new-york"},
    # OpenTable
    "la_dong":      {"platform": "opentable",  "id": 0, "note": "Look up OT ID"},
    "le_bernardin": {"platform": "opentable",  "id": 3735},
    "daniel":       {"platform": "opentable",  "id": 2027},
    "sushi_nakazawa":{"platform": "opentable", "id": 0, "note": "Look up OT ID"},
}
