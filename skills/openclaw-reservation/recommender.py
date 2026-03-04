"""
Restaurant Recommendation Engine 🌟
=====================================
Sources (in priority order):
1. Michelin Guide — Algolia API (BIB_GOURMAND + selected/Plate only, NEVER stars)
2. Time Out — scraping "Best of" lists
3. Condé Nast Traveler — scraping gallery pages
4. Maps Curated — hand-curated + Google Maps saved places (maps.py)

Michelin Algolia Config (reverse-engineered March 2026):
  App:    8NVHRD7ONV
  Key:    3222e669cf890dc73fa5f38241117ba5  (public read-only)
  Index:  prod-restaurants-en
  Awards: BIB_GOURMAND | selected (=Plate) | ONE_STAR | TWO_STARS | THREE_STARS
  ⚠️ Israel is NOT in the Michelin index as of 2026. Use Maps/TimeOut for TLV.

Per Yonatan's explicit preference:
  ✅ BIB_GOURMAND  — great food, great value, no fuss
  ✅ selected      — Plate / Recommended / "good cooking"
  ❌ ONE_STAR and above — too fancy, not the vibe
"""
import requests
import re

# ── Michelin (Algolia) ──────────────────────────────────────────────────────

ALGOLIA_APP = "8NVHRD7ONV"
ALGOLIA_KEY = "3222e669cf890dc73fa5f38241117ba5"
ALGOLIA_IDX = "prod-restaurants-en"
ALGOLIA_HEADERS = {
    "X-Algolia-Application-Id": ALGOLIA_APP,
    "X-Algolia-API-Key": ALGOLIA_KEY,
    "Content-Type": "application/json",
    "Referer": "https://guide.michelin.com/",
    "Origin": "https://guide.michelin.com",
}

# City slug mappings for Michelin Algolia (must match their city_slug field)
MICHELIN_CITY_SLUGS = {
    "marseille":  "marseille",
    "genoa":      "genova",
    "genova":     "genova",
    "messina":    "messina",
    "valletta":   "valletta",
    "new york":   "new-york",
    "new_york":   "new-york",
    "nyc":        "new-york",
    "paris":      "paris",
    "rome":       "rome",
    "barcelona":  "barcelona",
    "milan":      "milan",
    "tel aviv":   None,   # NOT in Michelin index — use Maps
    "tel_aviv":   None,
}


def get_michelin(city: str, bib_only: bool = False, limit: int = 20) -> list[dict]:
    """
    Fetch Michelin recommendations (Bib Gourmand + Plate only — no stars ever).

    Args:
        city: city name (mapped to Michelin slug internally)
        bib_only: if True, only return Bib Gourmand (skip Plate)
        limit: max results per query

    Returns: [{name, award, cuisine, booking_provider, booking_url, michelin_url}]
    """
    slug = MICHELIN_CITY_SLUGS.get(city.lower().replace(" ", "_"))
    if slug is None:
        return []  # city not in Michelin index

    award_filter = "michelin_award:BIB_GOURMAND" if bib_only else \
                   "(michelin_award:BIB_GOURMAND OR michelin_award:selected)"

    payload = {
        "query": "",
        "filters": f"city_slug:{slug} AND {award_filter}",
        "hitsPerPage": limit,
        "attributesToRetrieve": [
            "name", "michelin_award", "cuisines", "booking_provider",
            "booking_url", "phone", "url", "price_category", "city",
            "michelin_star",
        ],
    }

    try:
        r = requests.post(
            f"https://{ALGOLIA_APP}-dsn.algolia.net/1/indexes/{ALGOLIA_IDX}/query",
            headers=ALGOLIA_HEADERS,
            json=payload,
            timeout=10,
        )
        hits = r.json().get("hits", []) if r.ok else []
    except Exception:
        return []

    results = []
    for h in hits:
        award = h.get("michelin_award", "")
        # Double-check: never return starred restaurants
        if award in ("ONE_STAR", "TWO_STARS", "THREE_STARS"):
            continue
        cuisines = ", ".join(c.get("label", "") for c in (h.get("cuisines") or []))
        results.append({
            "name": h.get("name"),
            "source": "Michelin Guide",
            "award": "Bib Gourmand 🍺" if award == "BIB_GOURMAND" else "Plate 🍽️",
            "cuisine": cuisines,
            "price": (h.get("price_category") or {}).get("label", ""),
            "booking_provider": h.get("booking_provider"),
            "booking_url": h.get("booking_url"),
            "phone": h.get("phone"),
            "michelin_url": f"https://guide.michelin.com{h.get('url', '')}",
        })
    return results


# ── Time Out ─────────────────────────────────────────────────────────────────

TIMEOUT_PATHS = {
    "new york":   "newyork/restaurants/100-best-new-york-restaurants",
    "new_york":   "newyork/restaurants/100-best-new-york-restaurants",
    "nyc":        "newyork/restaurants/100-best-new-york-restaurants",
    "marseille":  "marseille/en/restaurants/best-restaurants-in-marseille",
    "london":     "london/restaurants/best-restaurants-in-london",
    "paris":      "paris/en/restaurants/best-restaurants-in-paris",
    "rome":       "rome/en/restaurants/best-restaurants-in-rome",
    "barcelona":  "barcelona/en/restaurants/best-restaurants-in-barcelona",
    "milan":      "milan/en/restaurants/best-restaurants-in-milan",
    "tel aviv":   "israel/restaurants",   # closest TLV page
    "tel_aviv":   "israel/restaurants",
}


def get_timeout(city: str, limit: int = 15) -> list[dict]:
    """
    Scrape Time Out 'Best Restaurants' list for a city.
    Returns [{name, rank, source, url}]
    """
    path = TIMEOUT_PATHS.get(city.lower().replace(" ", "_"))
    if not path:
        return []

    url = f"https://www.timeout.com/{path}"
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if not r.ok:
            return []

        # Time Out numbers their best lists with h3 tags: "1.&nbsp;Restaurant Name"
        h3s = re.findall(r"<h3[^>]*>(.*?)</h3>", r.text, re.DOTALL)
        results = []
        for h in h3s:
            clean = re.sub(r"<[^>]+>", "", h).replace("&nbsp;", " ").strip()
            match = re.match(r"(\d+)\.\s*(.+)", clean)
            if match:
                results.append({
                    "name": match.group(2).strip(),
                    "rank": int(match.group(1)),
                    "source": "Time Out",
                    "url": url,
                })
            elif 3 < len(clean) < 80 and "Time Out" not in clean and not clean.startswith("http"):
                results.append({"name": clean, "source": "Time Out", "url": url})

        return results[:limit]
    except Exception:
        return []


# ── Condé Nast Traveler ───────────────────────────────────────────────────────
# CNT GraphQL needs auth tokens; fallback to scraping their gallery pages.
# Works for some cities, not all. Silently returns [] if no page found.

CNT_PATHS = {
    "new york":  ["/gallery/best-new-restaurants-nyc", "/gallery/best-italian-restaurants-in-new-york"],
    "new_york":  ["/gallery/best-new-restaurants-nyc"],
    "marseille": ["/story/best-restaurants-marseille"],
    "paris":     ["/gallery/best-restaurants-in-paris"],
    "london":    ["/gallery/best-restaurants-in-london"],
    "rome":      ["/gallery/best-restaurants-in-rome"],
    "barcelona": ["/gallery/best-restaurants-in-barcelona"],
}


def get_cnt(city: str, limit: int = 10) -> list[dict]:
    """
    Scrape Condé Nast Traveler restaurant picks for a city.
    Returns [{name, source, url}]
    """
    paths = CNT_PATHS.get(city.lower().replace(" ", "_"), [])
    for path in paths:
        url = f"https://www.cntraveler.com{path}"
        try:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            if not r.ok:
                continue
            # CNT uses h2 for gallery slide titles
            names = re.findall(r"<h2[^>]*>(.*?)</h2>", r.text, re.DOTALL)
            results = []
            for n in names:
                clean = re.sub(r"<[^>]+>", "", n).strip()
                if 3 < len(clean) < 80 and not any(
                    kw in clean.lower() for kw in ["newsletter", "privacy", "follow", "condé", "conde"]
                ):
                    results.append({"name": clean, "source": "Condé Nast Traveler", "url": url})
            if results:
                return results[:limit]
        except Exception:
            continue
    return []


# ── Unified ───────────────────────────────────────────────────────────────────

def get_recommendations(city: str, include_michelin: bool = True,
                        include_timeout: bool = True,
                        include_cnt: bool = True,
                        include_maps: bool = True) -> dict:
    """
    Fetch all recommendations for a city, organized by source.

    Returns:
        {
          "michelin": [...],
          "timeout": [...],
          "cnt": [...],
          "maps_curated": [...],
          "all": [...],   # merged, deduped by name
        }
    """
    from .maps import get_curated

    result = {
        "michelin": get_michelin(city) if include_michelin else [],
        "timeout":  get_timeout(city)  if include_timeout  else [],
        "cnt":      get_cnt(city)      if include_cnt      else [],
        "maps_curated": get_curated(city) if include_maps else [],
    }

    # Merge and deduplicate by lowercased name
    seen = set()
    merged = []
    for source in ("maps_curated", "michelin", "timeout", "cnt"):
        for item in result[source]:
            key = (item.get("name") or "").lower().strip()
            if key and key not in seen:
                seen.add(key)
                merged.append({**item, "source": item.get("source", source)})
    result["all"] = merged

    return result


def format_recommendations(city: str, recs: dict = None) -> str:
    """Format recommendations for Telegram display."""
    if recs is None:
        recs = get_recommendations(city)

    lines = [f"🌟 *Recommendations — {city.title()}*\n"]

    # Maps curated picks first (highest signal, hand-curated)
    curated = recs.get("maps_curated", [])
    if curated:
        lines.append("*🗺️ Curated Picks:*")
        for r in curated[:5]:
            kai = " ⭐" if r.get("kai_pick") else ""
            michelin = f" [{r['michelin']}]" if r.get("michelin") else ""
            bk = f" — Book: _{r['booking_platform']}_" if r.get("booking_platform") else ""
            lines.append(f"• *{r['name']}*{kai}{michelin} | {r.get('cuisine','')}{bk}")
            if r.get("notes"):
                lines.append(f"  _{r['notes']}_")

    # Michelin
    michelin = recs.get("michelin", [])
    if michelin:
        lines.append("\n*🔴 Michelin (Bib + Plate only):*")
        for r in michelin[:6]:
            bk = f" | Book: _{r.get('booking_provider','?')}_" if r.get("booking_provider") else ""
            lines.append(f"• *{r['name']}* {r.get('award','')} | {r.get('cuisine','')}{bk}")

    # Time Out
    timeout = recs.get("timeout", [])
    if timeout:
        lines.append("\n*⏰ Time Out picks:*")
        for r in timeout[:5]:
            rank = f"#{r['rank']} " if r.get("rank") else ""
            lines.append(f"• {rank}*{r['name']}*")

    # CNT
    cnt = recs.get("cnt", [])
    if cnt:
        lines.append("\n*✈️ Condé Nast Traveler:*")
        for r in cnt[:4]:
            lines.append(f"• *{r['name']}*")

    return "\n".join(lines)


# ── Cache for known destinations ──────────────────────────────────────────────
# Pre-loaded so we don't hammer APIs mid-conversation.
# Refresh manually or via heartbeat once a month.

CACHED_RECOMMENDATIONS: dict[str, dict] = {}
