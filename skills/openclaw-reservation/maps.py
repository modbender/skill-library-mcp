"""
Google Maps Integration — Restaurant Discovery 🗺️
===================================================
Uses the GOG skill (Google API) or direct Maps URLs to:
1. Fetch Yonatan's "Saved Places" (Want to Go / Starred)
2. Search for restaurants in a city via Places API
3. Get detailed reviews + hours + photos

This is the PRIMARY recommendation source for Israel (not Michelin-indexed).
For abroad: supplements Michelin Guide and Time Out.

Auth: Uses configured Google account OAuth via gog skill.
"""
import requests
import subprocess
import json
import re

MAPS_BASE = "https://maps.googleapis.com/maps/api"
PLACES_BASE = "https://places.googleapis.com/v1"


# ---------------------------------------------------------------------------
# Saved Places (via gog CLI or Maps API)
# ---------------------------------------------------------------------------

def get_saved_places_url(list_name: str = "Want to go") -> str:
    """
    Returns the URL to view saved places. Actual data requires OAuth.
    Use the gog skill for this.
    """
    return "https://www.google.com/maps/saved/"


def search_restaurants_maps(
    city: str,
    query: str = "restaurant",
    api_key: str = None,
    min_rating: float = 4.3,
    max_results: int = 10,
) -> list[dict]:
    """
    Search Google Maps/Places for restaurants in a city.

    Requires: GOOGLE_MAPS_API_KEY env var OR the gog skill for OAuth access.
    Falls back to a search URL if no API key available.

    Returns:
        [{name, rating, address, types, maps_url, price_level}]
    """
    import os
    key = api_key or os.environ.get("GOOGLE_MAPS_API_KEY")

    if not key:
        # Fallback: return search URL for browser
        encoded = requests.utils.quote(f"best restaurants in {city}")
        return [{
            "name": f"Search: best restaurants in {city}",
            "maps_url": f"https://www.google.com/maps/search/best+restaurants+in+{city}/",
            "note": "No API key — open in browser"
        }]

    # Use Places API (New) Text Search
    r = requests.post(
        f"{PLACES_BASE}/places:searchText",
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": key,
            "X-Goog-FieldMask": "places.displayName,places.rating,places.formattedAddress,places.googleMapsUri,places.priceLevel,places.types,places.nationalPhoneNumber,places.websiteUri,places.regularOpeningHours"
        },
        json={
            "textQuery": f"best restaurants in {city}",
            "minRating": min_rating,
            "maxResultCount": max_results,
            "languageCode": "en",
        },
        timeout=10,
    )
    if not r.ok:
        return []

    places = r.json().get("places", [])
    return [{
        "name": p.get("displayName", {}).get("text"),
        "rating": p.get("rating"),
        "price_level": p.get("priceLevel"),
        "address": p.get("formattedAddress"),
        "phone": p.get("nationalPhoneNumber"),
        "website": p.get("websiteUri"),
        "maps_url": p.get("googleMapsUri"),
        "types": p.get("types", []),
        "source": "Google Maps",
    } for p in places if p.get("rating", 0) >= min_rating]


def search_via_url(city: str, query: str = "restaurant") -> str:
    """Build a Google Maps search URL (no API key needed)."""
    q = f"{query} in {city}".replace(" ", "+")
    return f"https://www.google.com/maps/search/{q}/"


# ---------------------------------------------------------------------------
# Hardcoded curated lists (from Yonatan's saved places + research)
# Pre-populate for known destinations to avoid API calls at runtime.
# ---------------------------------------------------------------------------

# Format: {city_key: [{name, cuisine, address, maps_url, notes, booking_platform, booking_id}]}
CURATED: dict[str, list[dict]] = {

    # ─── MSC Cruise Ports ───────────────────────────────────────────────────

    "marseille": [
        {
            "name": "Chez Fonfon",
            "cuisine": "Bouillabaisse / Seafood",
            "address": "140 Rue du Vallon des Auffes, 13007 Marseille",
            "maps_url": "https://goo.gl/maps/fonfon",
            "notes": "The definitive Marseille bouillabaisse. Reserve ahead.",
            "booking_platform": "thefork",
            "michelin": "Selected (Plate)",
        },
        {
            "name": "AM par Alexandre Mazzia",
            "cuisine": "Creative / Contemporary",
            "address": "9 Rue François Rocca, 13008 Marseille",
            "maps_url": "https://g.co/kgs/AM",
            "notes": "Time Out #3. Chef-driven. Unique. Not starred (yet relevant).",
            "booking_platform": "thefork",
            "michelin": None,
        },
        {
            "name": "Auffo",
            "cuisine": "Modern Cuisine",
            "address": "Marseille",
            "notes": "Michelin Selected + TheFork bookable.",
            "booking_platform": "thefork",
            "michelin": "Selected (Plate)",
        },
        {
            "name": "L'Épuisette",
            "cuisine": "Seafood / Mediterranean",
            "address": "158 Rue du Vallon des Auffes, 13007 Marseille",
            "notes": "On the water, stunning view, great fish.",
            "booking_platform": "thefork",
        },
        {
            "name": "A Moro",
            "cuisine": "Italian / Mediterranean",
            "notes": "Time Out Marseille #1.",
            "booking_platform": "thefork",
        },
    ],

    "genoa": [
        {
            "name": "Bottega del Re",
            "cuisine": "Ligurian / Contemporary",
            "notes": "Michelin Selected + TheFork bookable. Ligurian classics.",
            "booking_platform": "thefork",
            "michelin": "Selected (Plate)",
        },
        {
            "name": "20Tre",
            "cuisine": "Farm to Table / Modern",
            "notes": "Michelin Selected + TheFork bookable.",
            "booking_platform": "thefork",
            "michelin": "Selected (Plate)",
        },
        {
            "name": "Santa Teresa",
            "cuisine": "Modern / Farm to Table",
            "notes": "Michelin Selected + TheFork bookable.",
            "booking_platform": "thefork",
            "michelin": "Selected (Plate)",
        },
        {
            "name": "Ippogrifo",
            "cuisine": "Seafood / Classic",
            "notes": "Michelin Selected. Phone booking.",
            "michelin": "Selected (Plate)",
        },
    ],

    "messina": [
        {
            "name": "Trattoria Osteria del Campanile",
            "cuisine": "Sicilian / Traditional",
            "notes": "Top pick. Authentic Messina, great swordfish. Book ahead.",
            "booking_platform": "thefork",
            "kai_pick": True,
        },
        {
            "name": "Marina del Nettuno",
            "cuisine": "Creative / Contemporary",
            "notes": "Michelin Selected + TheFork bookable. In the marina.",
            "booking_platform": "thefork",
            "thefork_module_url": "https://module.thefork.com/en_GB/module/304761-aeb19/51247-42f",
            "michelin": "Selected (Plate)",
        },
        {
            "name": "Casa & Putia",
            "cuisine": "Sicilian Deli / Casual",
            "notes": "Great for a quick local lunch. Not bookable — walk-in.",
            "booking_platform": None,
        },
        {
            "name": "Casa Savoia",
            "cuisine": "Sicilian / Traditional",
            "notes": "Classic Messina restaurant. Walk-in friendly.",
            "booking_platform": None,
        },
    ],

    "valletta": [
        {
            "name": "Legligin",
            "cuisine": "Regional Maltese / Mediterranean",
            "notes": "Michelin Selected + Mozrest. Authentic Maltese food. Family-friendly.",
            "booking_platform": "mozrest",
            "michelin": "Selected (Plate)",
            "family_friendly": True,
        },
        {
            "name": "59 Republic",
            "cuisine": "Classic / International",
            "notes": "Michelin Selected + Mozrest.",
            "booking_platform": "mozrest",
            "michelin": "Selected (Plate)",
        },
        {
            "name": "Kaiseki",
            "cuisine": "Mediterranean / Asian Fusion",
            "notes": "Michelin Selected + Mozrest.",
            "booking_platform": "mozrest",
            "michelin": "Selected (Plate)",
        },
        {
            "name": "La Pira",
            "cuisine": "Traditional Maltese",
            "notes": "Michelin Selected. Local institution.",
            "michelin": "Selected (Plate)",
        },
    ],

    # ─── New York (June 2026) ────────────────────────────────────────────────

    "new_york": [
        # ── 🚩 Green Flag — also good for family (Yonatan + Louise + kids) ──────
        {
            "name": "Via Carota",
            "cuisine": "Italian / Trattoria",
            "address": "51 Grove St, West Village",
            "notes": "West Village institution. Resy (hard to get). Walk-in OK. 🚩 Green Flag.",
            "booking_platform": "resy",
            "list": "statue_of_independence",
        },
        {
            "name": "Tatiana by Kwame Onwuachi",
            "cuisine": "Afro-Caribbean / Contemporary",
            "address": "Lincoln Center, UWS",
            "notes": "Time Out NYC top pick. Beautiful space. 🚩 Green Flag.",
            "booking_platform": "resy",
            "list": "statue_of_independence",
        },
        {
            "name": "Rubirosa",
            "cuisine": "Italian-American / Pizza",
            "address": "235 Mulberry St, NoLita",
            "notes": "Legendary thin-crust pizza. 🚩 Green Flag.",
            "booking_platform": "resy",
            "list": "statue_of_independence",
        },
        {
            "name": "Café Habana",
            "cuisine": "Cuban / Mexican",
            "address": "17 Prince St, NoLita",
            "notes": "Classic. Cuban sandwich, grilled corn. 🚩 Green Flag.",
            "list": "statue_of_independence",
        },
        {
            "name": "Momofuku Noodle Bar",
            "cuisine": "Asian / Ramen",
            "address": "171 First Ave, East Village",
            "notes": "The original. 🚩 Green Flag.",
            "booking_platform": "resy",
            "list": "statue_of_independence",
        },
        {
            "name": "Momofuku Noodle Bar Uptown",
            "cuisine": "Asian / Ramen",
            "address": "UWS",
            "notes": "🚩 Green Flag.",
            "list": "statue_of_independence",
        },
        {
            "name": "Buddakan",
            "cuisine": "Asian Fusion",
            "address": "75 9th Ave, Chelsea",
            "notes": "Grand space, great for groups. 🚩 Green Flag.",
            "booking_platform": "opentable",
            "list": "statue_of_independence",
        },
        {
            "name": "Sakagura",
            "cuisine": "Japanese / Sake Bar",
            "address": "Midtown East",
            "notes": "Underground sake bar. Excellent Japanese. 🚩 Green Flag.",
            "booking_platform": "resy",
            "list": "statue_of_independence",
        },
        {
            "name": "Café China",
            "cuisine": "Sichuan",
            "address": "Midtown",
            "notes": "Michelin-level Sichuan in a retro setting. 🚩 Green Flag.",
            "booking_platform": "resy",
            "list": "statue_of_independence",
        },
        {
            "name": "RedFarm",
            "cuisine": "Chinese / Dim Sum",
            "address": "West Village + UWS",
            "notes": "Creative dim sum. 🚩 Green Flag.",
            "booking_platform": "resy",
            "list": "statue_of_independence",
        },
        {
            "name": "Jacob's Pickles",
            "cuisine": "American / Comfort",
            "address": "509 Amsterdam Ave, UWS",
            "notes": "Great brunch spot. Biscuits. 🚩 Green Flag.",
            "list": "statue_of_independence",
        },
        {
            "name": "McSorley's Old Ale House",
            "cuisine": "Irish Bar / Pub",
            "address": "15 E 7th St, East Village",
            "notes": "NYC's oldest bar (1854). Cash only. Perfect for a guys night. 🚩 Green Flag.",
            "list": "statue_of_independence",
        },
        {
            "name": "169 Bar",
            "cuisine": "Bar",
            "address": "169 E Broadway, Lower East Side",
            "notes": "Dive bar, great vibe. 🚩 Green Flag.",
            "list": "statue_of_independence",
        },
        {
            "name": "Great Jones Distilling",
            "cuisine": "Bar / Distillery",
            "address": "686 Broadway, NoHo",
            "notes": "NYC craft whiskey distillery + bar. 🚩 Green Flag.",
            "list": "statue_of_independence",
        },
        {
            "name": "The Dead Poet",
            "cuisine": "Bar",
            "address": "450 Amsterdam Ave, UWS",
            "notes": "Literary-themed bar, cozy. 🚩 Green Flag.",
            "list": "statue_of_independence",
        },
        {
            "name": "The Gin Mill",
            "cuisine": "Bar",
            "address": "442 Amsterdam Ave, UWS",
            "notes": "Sports bar vibe, cheap drinks. 🚩 Green Flag.",
            "list": "statue_of_independence",
        },
        {
            "name": "Rudy's Bar & Grill",
            "cuisine": "Bar",
            "address": "627 9th Ave, Hell's Kitchen",
            "notes": "Legendary dive bar. Free hot dogs. 🚩 Green Flag.",
            "list": "statue_of_independence",
        },
        {
            "name": "Gyu-Kaku Japanese BBQ",
            "cuisine": "Japanese BBQ",
            "address": "UWS",
            "notes": "Tabletop BBQ. Great for groups. 🚩 Green Flag.",
            "list": "statue_of_independence",
        },
        {
            "name": "Parm Upper West Side",
            "cuisine": "Italian-American",
            "address": "UWS",
            "notes": "Chicken parm sandwiches. 🚩 Green Flag.",
            "booking_platform": "resy",
            "list": "statue_of_independence",
        },
        {
            "name": "Dinosaur Bar-B-Que",
            "cuisine": "BBQ",
            "address": "Park Slope, Brooklyn",
            "notes": "Award-winning BBQ. Great for big groups. 🚩 Green Flag.",
            "list": "statue_of_independence",
        },
        {
            "name": "gertrude's",
            "cuisine": "American",
            "address": "Prospect Heights, Brooklyn",
            "notes": "🚩 Green Flag.",
            "list": "statue_of_independence",
        },
        {
            "name": "Ozakaya",
            "cuisine": "Japanese / Izakaya",
            "address": "Prospect Heights, Brooklyn",
            "notes": "🚩 Green Flag.",
            "list": "statue_of_independence",
        },
        {
            "name": "Hwa Yuan Szechuan",
            "cuisine": "Sichuan",
            "address": "Chinatown",
            "notes": "Classic Sichuan in Chinatown. 🚩 Green Flag.",
            "list": "statue_of_independence",
        },
        {
            "name": "Mission Chinese Food",
            "cuisine": "Chinese / Sichuan",
            "address": "Lower East Side",
            "notes": "🚩 Green Flag.",
            "list": "statue_of_independence",
        },
        {
            "name": "Westville",
            "cuisine": "American / Healthy",
            "address": "Multiple locations (East Village, Hell's Kitchen, Hudson)",
            "notes": "Great veggie options too. 🚩 Green Flag.",
            "list": "statue_of_independence",
        },
        {
            "name": "The Ribbon",
            "cuisine": "American",
            "address": "UWS",
            "notes": "🚩 Green Flag.",
            "list": "statue_of_independence",
        },
        {
            "name": "Sal and Carmine Pizza",
            "cuisine": "Pizza",
            "address": "2671 Broadway, UWS",
            "notes": "Old-school NY slice. 🚩 Green Flag.",
            "list": "statue_of_independence",
        },
        {
            "name": "SPIN New York",
            "cuisine": "Bar / Ping Pong",
            "address": "Midtown + Flatiron",
            "notes": "Ping pong bar. Fun for groups. 🗽 Statue of Independence.",
            "list": "statue_of_independence",
        },
        # ── 🚩 Green Flag — Brooklyn (family-friendly, confirmed by Yonatan) ──
        {
            "name": "Leland Eating and Drinking House",
            "cuisine": "American",
            "address": "Prospect Heights, Brooklyn",
            "notes": "Neighborhood gem. 🚩 Green Flag.",
            "list": "green_flag",
        },
        {
            "name": "RAS Plant Based",
            "cuisine": "Ethiopian / Plant-Based",
            "address": "Crown Heights, Brooklyn",
            "notes": "Excellent plant-based Ethiopian. 🚩 Green Flag.",
            "list": "green_flag",
        },
        {
            "name": "Casa Azul",
            "cuisine": "Mexican",
            "address": "South Slope, Brooklyn",
            "notes": "🚩 Green Flag.",
            "list": "green_flag",
        },
        {
            "name": "burger joint",
            "cuisine": "Burgers",
            "address": "Hidden in Le Parker Meridien, Midtown",
            "notes": "Secret burger spot. Cash only. 🚩 Green Flag.",
            "list": "statue_of_independence",
        },
        {
            "name": "The Halal Guys",
            "cuisine": "Middle Eastern / Street Food",
            "address": "Midtown",
            "notes": "Iconic NYC cart/restaurant. 🚩 Green Flag.",
            "list": "statue_of_independence",
        },
        {
            "name": "Golden Diner",
            "cuisine": "Diner / Asian-American",
            "address": "Two Bridges",
            "notes": "🚩 Green Flag.",
            "list": "statue_of_independence",
        },
        {
            "name": "NOL",
            "cuisine": "New Orleans / Southern",
            "address": "NoLita",
            "notes": "🚩 Green Flag.",
            "list": "statue_of_independence",
        },
        {
            "name": "Radio Bakery",
            "cuisine": "Bakery / Café",
            "address": "Prospect Heights, Brooklyn",
            "notes": "🚩 Green Flag.",
            "list": "statue_of_independence",
        },
        {
            "name": "Chavela's",
            "cuisine": "Mexican",
            "address": "Crown Heights, Brooklyn",
            "notes": "🚩 Green Flag.",
            "list": "statue_of_independence",
        },
        {
            "name": "Ramen DANBO Park Slope",
            "cuisine": "Ramen",
            "address": "Park Slope, Brooklyn",
            "notes": "🚩 Green Flag.",
            "list": "statue_of_independence",
        },
        {
            "name": "Franklin Park",
            "cuisine": "Bar",
            "address": "Crown Heights, Brooklyn",
            "notes": "Large beer garden. Great for groups. 🚩 Green Flag.",
            "list": "statue_of_independence",
        },
        # ── 🗽 Statue of Independence — guys World Cup trip only (party of 6, no kids) ──
        {
            "name": "The River Café",
            "cuisine": "American / Fine Dining",
            "address": "1 Water St, DUMBO, Brooklyn",
            "notes": "Stunning Manhattan views. Special occasion. 🗽 Statue of Independence.",
            "booking_platform": "resy",
            "list": "statue_of_independence",
        },
        {
            "name": "Doaba Deli",
            "cuisine": "Indian / Deli",
            "address": "UWS",
            "notes": "🗽 Statue of Independence.",
            "list": "statue_of_independence",
        },
        {
            "name": "Serendipity 3",
            "cuisine": "American / Desserts",
            "address": "225 E 60th St, Upper East Side",
            "notes": "Famous frozen hot chocolate. Family-friendly. 🗽 Statue of Independence.",
            "list": "statue_of_independence",
        },
        {
            "name": "Vanderbilt Market",
            "cuisine": "Food Hall",
            "address": "Midtown East",
            "notes": "🗽 Statue of Independence.",
            "list": "statue_of_independence",
        },
        # ── Previously curated (Michelin / editorial) ────────────────────────
        {
            "name": "Don Angie",
            "cuisine": "Italian-American",
            "address": "103 Greenwich Ave, West Village",
            "notes": "Resy (releases 28 days out). Lasagna is legendary.",
            "booking_platform": "resy",
        },
        {
            "name": "Adda",
            "cuisine": "Indian",
            "address": "Long Island City, Queens",
            "notes": "Time Out NYC #1. Proper Indian home-cooking.",
            "booking_platform": "resy",
        },
        {
            "name": "La Dong",
            "cuisine": "Vietnamese",
            "notes": "Michelin Bib Gourmand.",
            "booking_platform": "opentable",
            "michelin": "Bib Gourmand",
        },
        {
            "name": "Smithereens",
            "cuisine": "Seafood",
            "notes": "Michelin Selected.",
            "booking_platform": "resy",
            "michelin": "Selected (Plate)",
        },
        {
            "name": "Comal",
            "cuisine": "Mexican",
            "notes": "Michelin Selected.",
            "michelin": "Selected (Plate)",
        },
    ],

    # ─── Barcelona (pre-cruise Apr 1–3 2026) ────────────────────────────────

    "barcelona": [
        {"name": "Sartoria Panatieri", "cuisine": "Pizza / Neapolitan", "address": "Eixample", "notes": "Best pizza in Barcelona. Book ahead.", "booking_platform": "thefork"},
        {"name": "Tickets", "cuisine": "Tapas / Albert Adrià", "address": "Poble-sec", "notes": "Albert Adrià's fun tapas bar. Needs advance booking online.", "booking_platform": "thefork"},
        {"name": "Quimet & Quimet", "cuisine": "Tapas / Standing Bar", "address": "Poble-sec", "notes": "Iconic standing bar. Canned tapas + cava. No reservations, arrive early."},
        {"name": "El Xampanyet", "cuisine": "Cava Bar / Tapas", "address": "El Born", "notes": "Classic cava bar. No reservations."},
        {"name": "Can Paixano", "cuisine": "Cava + Tapas", "address": "El Born / Barceloneta", "notes": "Legendary cheap cava. Standing only. Cash."},
        {"name": "Cerveceria Catalana", "cuisine": "Tapas / Catalan", "address": "Eixample", "notes": "Always busy. Queue or arrive off-peak.", "booking_platform": "thefork"},
        {"name": "Vinitus", "cuisine": "Tapas", "address": "Eixample", "notes": "Good pintxos + tapas.", "booking_platform": "thefork"},
        {"name": "Ciutat Comtal", "cuisine": "Tapas / Catalan", "address": "Eixample", "notes": "Rambla de Catalunya terrace."},
        {"name": "La Flauta", "cuisine": "Tapas / Catalan", "address": "Eixample", "notes": "Great flautas (thin baguette sandwiches)."},
        {"name": "Elsa y Fred", "cuisine": "Mediterranean", "address": "El Born area", "notes": "Romantic bistro.", "booking_platform": "thefork"},
        {"name": "Tapas Cañota", "cuisine": "Tapas", "address": "Sant Antoni / Poble-sec", "notes": "Excellent cañotas.", "booking_platform": "thefork"},
        {"name": "La Tasqueta de Blai", "cuisine": "Pintxos", "address": "Poble-sec, Carrer de Blai", "notes": "Pintxos street. Cheap and excellent."},
        {"name": "Merendero de la Mari", "cuisine": "Seafood / Catalan", "address": "Barceloneta", "notes": "Good paella + seafood by the beach."},
        {"name": "Heliogàbal", "cuisine": "Bar / Live Music", "address": "Gràcia", "notes": "Cool neighborhood bar."},
        {"name": "Federal Cafè", "cuisine": "Brunch / Café", "address": "Sant Antoni", "notes": "Best brunch in BCN."},
        {"name": "Tantarantana", "cuisine": "Mediterranean", "address": "El Born", "notes": "From Yonatan's saved places."},
    ],

    # ─── Tel Aviv (Home) ─────────────────────────────────────────────────────

    "tel_aviv": [
        # ── Confirmed bookable via Ontopo ────────────────────────────────
        {
            "name": "Bar 51",
            "cuisine": "Bar / Mediterranean",
            "address": "59 HaYarkon St, Tel Aviv",
            "notes": "Yonatan's saved place. Ontopo postSlug: 31338736 ✅. Covered balcony available.",
            "booking_platform": "ontopo",
            "ontopo_post_slug": "31338736",
            "from_maps": True,
        },
        {
            "name": "Taizu",
            "cuisine": "Pan-Asian",
            "notes": "Yonatan's regular. Ontopo postSlug: 36960535 ✅.",
            "booking_platform": "ontopo",
            "ontopo_post_slug": "36960535",
        },
        {
            "name": "Mashya",
            "cuisine": "Modern Israeli",
            "notes": "Phone bookings only. Ontopo postSlug: 45994738.",
            "booking_platform": "phone",
            "ontopo_post_slug": "45994738",
        },
        # ── From Maps saved places (postSlug TBD — discover on demand) ──
        {
            "name": "HaBasta",
            "cuisine": "Market / Israeli",
            "address": "Hacarmel Market area, TLV",
            "notes": "Yonatan's saved place. Classic market restaurant.",
            "booking_platform": "ontopo",
            "from_maps": True,
        },
        {
            "name": "Minzar",
            "cuisine": "Bar / Israeli",
            "notes": "Yonatan's saved place. Iconic TLV bar.",
            "booking_platform": "ontopo",
            "from_maps": True,
        },
        {
            "name": "Ouzeria",
            "cuisine": "Greek / Mediterranean",
            "notes": "Relaxed, family-friendly. Yonatan's saved place.",
            "booking_platform": "tabit",
            "from_maps": True,
        },
        {
            "name": "Chacoli",
            "cuisine": "Basque / Wine Bar",
            "notes": "Yonatan's saved place. Wine-focused, intimate.",
            "from_maps": True,
        },
        {
            "name": "Magazzino",
            "cuisine": "Italian",
            "notes": "Yonatan's saved place.",
            "from_maps": True,
        },
        {
            "name": "Café Asif",
            "cuisine": "Israeli / Bakery",
            "notes": "Yonatan's saved place. Great for breakfast/brunch.",
            "from_maps": True,
        },
        {
            "name": "Par Derriere",
            "cuisine": "French / Bistro",
            "notes": "Yonatan's saved place.",
            "from_maps": True,
        },
        {
            "name": "Kalamata",
            "cuisine": "Greek",
            "notes": "Yonatan's saved place.",
            "from_maps": True,
        },
        {
            "name": "Batshon",
            "cuisine": "Israeli / Bar",
            "address": "Carlebach St 29, Tel Aviv",
            "notes": "Yonatan's saved place. Carlebach area.",
            "from_maps": True,
        },
        # Full list from Maps screenshot — postSlugs to discover on demand:
        # Santi, Thai House, A La Bar, Winona Forever, Cafe Yael, DÉ FACTO TLV,
        # Viki & King, Nilus, Taverna Romana, Abie, Kab Kem, Cafe Italia,
        # Men Tenten Ramen Bar, Cue, Naifa, Pizza Lila, Gorkha Kitchen, Big Itzik,
        # Lunel, Babagim, Mutfak, Beit Kandinof, Dilek's, Le Mala, Hanan Margilan
        # → see cache/maps_screenshots.json for full list
    ],

    # ─── Athens (visited Dec 2025 / Nov 2025) ────────────────────────────────
    "athens": [
        {"name": "Diporto", "cuisine": "Greek / Traditional", "notes": "Yonatan's saved. Classic Athens basement taverna.", "from_maps": True},
        {"name": "Vezené Athens", "cuisine": "Modern Greek", "notes": "Yonatan's saved. Ilisia area.", "from_maps": True},
        {"name": "Annie - Fine Cooking", "cuisine": "Contemporary", "notes": "Yonatan's saved.", "from_maps": True},
        {"name": "Manári Taverna", "cuisine": "Greek Taverna", "notes": "Yonatan's saved.", "from_maps": True},
        {"name": "CTC Urban Gastronomy", "cuisine": "Modern / Gazi", "notes": "Yonatan's saved. Gazi area.", "from_maps": True},
        {"name": "Cerdo Negro 1985", "cuisine": "Bar / Gazi", "notes": "Yonatan's saved.", "from_maps": True},
    ],
}


def get_curated(city: str) -> list[dict]:
    """Get pre-curated restaurant list for a known city."""
    key = city.lower().replace(" ", "_").replace("-", "_")
    return CURATED.get(key, [])


def format_curated(city: str, filter_bookable: bool = False) -> str:
    """Format the curated list for display."""
    recs = get_curated(city)
    if not recs:
        return f"No curated list for {city} yet."

    lines = [f"🗺️ *{city.title()} — Curated Picks*"]
    for r in recs:
        bk = f" | Book: {r['booking_platform']}" if r.get("booking_platform") else " | Walk-in"
        michelin = f" 🔴" if r.get("michelin") else ""
        kai = " ⭐ Kai's pick" if r.get("kai_pick") else ""
        lines.append(f"\n• *{r['name']}*{michelin}{kai}")
        lines.append(f"  {r.get('cuisine', '')} {bk}")
        if r.get("notes"):
            lines.append(f"  _{r['notes']}_")

    return "\n".join(lines)
