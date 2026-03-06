"""
Live test: Messina self-travel day — April 7, 2026
======================================================
Context:
  MSC World Europa arrives Messina Apr 7. We skip the excursion.
  Plan: Walk into town, eat Sicilian food, back to ship.
  Time: Lunch ~13:00, dinner possible (ship dep. ~18:00 → aim for 13:00 lunch)
  Party: Yonatan, Louise, Zoe (5.5), Lenny (1.5) — stroller, no patience for fussy

Test covers:
  1. Michelin picks for Messina
  2. Time Out picks (if any)
  3. Curated picks (from maps.py)
  4. TheFork search URL (browser handoff)
  5. Specific: Marina del Nettuno + Trattoria Osteria del Campanile
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import json
from datetime import datetime

CITY = "messina"
DATE_ISO = "2026-04-07"
DATE_YYYYMMDD = "20260407"
TIME_LOCAL = "13:00"   # Lunch
SIZE = 4


def separator(title=""):
    print(f"\n{'─'*60}")
    if title: print(f"  {title}")
    print('─'*60)


def test_michelin():
    separator("1. MICHELIN PICKS (Bib+Plate only)")
    from recommender import get_michelin
    picks = get_michelin(CITY)
    if not picks:
        print("  No Michelin picks found (expected: ~1 for Messina)")
        return picks
    for p in picks:
        print(f"  [{p['award']}] {p['name']}")
        print(f"    Cuisine: {p['cuisine']}")
        print(f"    Booking: {p.get('booking_provider', '—')} | {p.get('booking_url', '—')}")
        print(f"    URL:     {p['michelin_url']}")
    return picks


def test_timeout():
    separator("2. TIME OUT PICKS")
    from recommender import get_timeout
    picks = get_timeout(CITY)
    if not picks:
        print("  No Time Out page found for Messina (expected — small city)")
    for p in picks:
        print(f"  #{p.get('rank', '?')} {p['name']}")
    return picks


def test_curated():
    separator("3. CURATED PICKS (maps.py)")
    from maps import get_curated, format_curated
    picks = get_curated(CITY)
    print(f"  Found {len(picks)} curated picks:")
    for p in picks:
        kai = " ⭐ KAI'S PICK" if p.get("kai_pick") else ""
        michelin = f" [{p['michelin']}]" if p.get("michelin") else ""
        bk = p.get("booking_platform") or "walk-in"
        print(f"  • {p['name']}{kai}{michelin}")
        print(f"    {p.get('cuisine', '')} | {bk}")
        print(f"    {p.get('notes', '')}")
    print()
    print("  Formatted output:")
    print(format_curated(CITY))
    return picks


def test_thefork_url():
    separator("4. THEFORK BROWSER URL")
    from thefork import get_city_search_url, get_availability_url, CITY_SLUGS
    
    city_url = get_city_search_url(CITY, covers=SIZE, date=DATE_ISO, time=TIME_LOCAL)
    print(f"  City search URL: {city_url}")
    
    # Specific restaurant URLs
    for name, tf_slug in [
        ("Marina del Nettuno", "marina-del-nettuno"),
        ("Trattoria Osteria del Campanile", "trattoria-osteria-del-campanile"),
    ]:
        base_url = f"https://www.thefork.com/restaurant/{tf_slug}"
        avail_url = get_availability_url(base_url, DATE_ISO, TIME_LOCAL, SIZE)
        print(f"\n  {name}:")
        print(f"    {avail_url}")


def test_unified():
    separator("5. UNIFIED search_and_format")
    from unified import search_and_format
    report = search_and_format(
        city=CITY,
        date=DATE_YYYYMMDD,
        time=TIME_LOCAL.replace(":", ""),
        size=SIZE,
        family_mode=True,
    )
    print(report)


def run_all():
    print(f"\n{'='*60}")
    print(f"  MESSINA LIVE TEST — {DATE_ISO} {TIME_LOCAL} for {SIZE}")
    print(f"  Family: Yonatan + Louise + Zoe (5.5) + Lenny (1.5)")
    print(f"{'='*60}")
    
    m = test_michelin()
    t = test_timeout()
    c = test_curated()
    test_thefork_url()
    test_unified()

    separator("SUMMARY")
    print(f"  Michelin picks: {len(m)}")
    print(f"  Time Out picks: {len(t)}")
    print(f"  Curated picks:  {len(c)}")
    print()
    print("  ✅ RECOMMENDATION:")
    print("  1st choice: Trattoria Osteria del Campanile (authentic Sicilian, top pick)")
    print("  2nd choice: Marina del Nettuno (Michelin Selected, TheFork bookable)")
    print("  Backup: Casa & Putia (walk-in casual, no booking needed)")
    print()
    print("  BOOKING PATH:")
    print("  → TheFork browser handoff for Trattoria & Marina del Nettuno")
    print("  → Open link → Yonatan confirms party + date → done")


if __name__ == "__main__":
    run_all()
