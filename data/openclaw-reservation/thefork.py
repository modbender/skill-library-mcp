"""
TheFork client — Mediterranean Europe 🇪🇺
==========================================
DataDome protected. No direct API access possible via requests.
Strategy: Browser co-pilot (user opens link, Kai reads snapshot).

Coverage: France, Italy, Spain, Malta, Belgium, Portugal, Netherlands, etc.
Relevant for MSC cruise: Marseille (Apr 4), Genoa (Apr 5), Messina (Apr 7), Valletta (Apr 8 - Mozrest)

Note on Valletta: TheFork doesn't cover Malta well. Use Mozrest or direct booking.
"""
import requests

BASE = "https://www.thefork.com"

# TheFork city slugs (from their search URL structure)
CITY_SLUGS = {
    "marseille":  "marseille-415144",
    "genoa":      "genoa-genova-413974",
    "genova":     "genoa-genova-413974",
    "messina":    "messina-415005",
    "rome":       "rome-roma-413906",
    "paris":      "paris-415080",
    "milan":      "milan-milano-413966",
    "barcelona":  "barcelona-414809",
    "nice":       "nice-415124",
    "florence":   "florence-firenze-413934",
    "naples":     "naples-napoli-413984",
    "palermo":    "palermo-414996",
}


def get_city_search_url(city: str, covers: int = 2, date: str = "", time: str = "") -> str:
    """Build TheFork search URL for a city with pre-filled party/date/time."""
    slug = CITY_SLUGS.get(city.lower(), city.lower())
    url = f"{BASE}/search?citySlug={slug}&covers={covers}"
    if date:
        url += f"&date={date}"
    if time:
        url += f"&time={time.replace(':', '%3A')}"
    return url


def get_availability_url(restaurant_url: str, date: str, time: str, covers: int) -> str:
    """Pre-fill availability on a specific TheFork restaurant page."""
    params = f"?date={date}&time={time.replace(':', '%3A')}&covers={covers}"
    return f"{restaurant_url.rstrip('/')}{params}"


def get_restaurant_url(restaurant_name: str, city: str) -> str:
    """
    Build a TheFork direct restaurant search URL.
    For known restaurants we'd store the slug; otherwise fallback to city search.
    """
    slug = CITY_SLUGS.get(city.lower(), city.lower())
    return f"{BASE}/search?citySlug={slug}&q={requests.utils.quote(restaurant_name)}&covers=2"
