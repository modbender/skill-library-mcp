#!/usr/bin/env python3
"""
Live test script for the reservation skill.
Run manually to verify each platform works.

Usage:
    cd /home/openclaw/.openclaw/workspace/skills
    python -m reservation.test_live

Tests:
    1. Ontopo: anonymous auth + search + availability
    2. Tabit: connectivity check
    3. TheFork: URL generation
    4. OpenTable: URL generation + widget
    5. Recommender: Michelin + TimeOut scraping
"""

import sys
import json

sys.path.insert(0, "/home/openclaw/.openclaw/workspace/skills")


def test_ontopo():
    print("\n=== TEST: Ontopo ===")
    from reservation.ontopo import get_token, search_venue, check_availability

    # Test 1: Anonymous auth
    try:
        token = get_token()
        print(f"✅ Anonymous auth: OK (token: {token[:20]}...)")
    except Exception as e:
        print(f"❌ Anonymous auth failed: {e}")
        return False

    # Test 2: Venue search
    try:
        results = search_venue("Taizu", token)
        print(f"✅ Venue search 'Taizu': {len(results)} results")
        if results:
            print(f"   First result: {results[0]}")
    except Exception as e:
        print(f"❌ Venue search failed: {e}")

    print("\nTo test availability_search, you need a postSlug.")
    print("Run: curl -s 'https://ontopo.com/he/il/page/taizu' | grep -o 'postSlug[^,]*'")
    
    return True


def test_tabit():
    print("\n=== TEST: Tabit ===")
    import requests
    
    TABIT_API = "https://ros.tabit.cloud"
    TABIT_APP = "https://tabitisrael.co.il"
    
    # Test: API responds (401 expected)
    try:
        r = requests.get(f"{TABIT_API}/online-shopper/organizations", 
                        params={"publicUrlLabel": "messa"},
                        timeout=5)
        if r.status_code == 401:
            print(f"✅ Tabit API reachable (auth required, expected): 401")
        elif r.status_code == 200:
            print(f"✅ Tabit API returned 200 (unexpected - anonymous access works!)")
            print(f"   Data: {r.text[:200]}")
        else:
            print(f"⚠️  Tabit API returned: {r.status_code}")
    except Exception as e:
        print(f"❌ Tabit API unreachable: {e}")

    # Test: App URL works
    try:
        r = requests.get(f"{TABIT_APP}/messa", timeout=5)
        if r.status_code == 200 and "tabit" in r.text.lower():
            print(f"✅ Tabit app URL works: {TABIT_APP}/messa")
        else:
            print(f"⚠️  Tabit app returned: {r.status_code}")
    except Exception as e:
        print(f"❌ Tabit app unreachable: {e}")
    
    print(f"📎 Manual booking URL: {TABIT_APP}/messa")


def test_thefork():
    print("\n=== TEST: TheFork ===")
    import requests
    from reservation.thefork import TheForkBrowserClient, BlockedByDataDome

    # Test: Direct API (expected to be blocked)
    try:
        r = requests.get("https://www.thefork.com/api/graphql", timeout=5)
        if "captcha" in r.text.lower() or r.status_code in (403, 429):
            print(f"✅ TheFork API blocked by DataDome (expected): {r.status_code}")
        else:
            print(f"⚠️  Unexpected TheFork response: {r.status_code}")
    except Exception as e:
        print(f"⚠️  TheFork connection: {e}")

    # Test: URL generation
    url = TheForkBrowserClient.get_search_url("marseille", "2026-06-15", "20:00", 2)
    print(f"✅ TheFork Marseille search URL: {url}")
    
    url = TheForkBrowserClient.get_search_url("genoa", "2026-06-17", "13:00", 4)
    print(f"✅ TheFork Genoa search URL: {url}")

    print("📎 To actually search, use: TheForkBrowserClient.search_with_playwright()")


def test_opentable():
    print("\n=== TEST: OpenTable ===")
    import requests
    from reservation.opentable import OpenTableBrowserClient, get_search_url

    # Test: Direct API (expected 403)
    try:
        r = requests.post("https://www.opentable.com/dapi/fe/gql",
                         json={"query": "{__typename}"},
                         headers={"Content-Type": "application/json",
                                 "User-Agent": "Mozilla/5.0"},
                         timeout=5)
        print(f"✅ OpenTable GQL response: {r.status_code} (403 = expected, needs auth)")
    except Exception as e:
        print(f"⚠️  OpenTable GQL: {e}")

    # Test: URL generation
    url = get_search_url("New York", "2026-03-15", "19:00", 2)
    print(f"✅ OpenTable NY search URL: {url}")
    
    # Test: Widget URL for Le Bernardin
    widget = OpenTableBrowserClient.get_widget_url(55800, "2026-03-15", "19:00", 2)
    print(f"✅ Le Bernardin widget URL: {widget}")
    
    booking = OpenTableBrowserClient.get_booking_url(55800, "2026-03-15", "19:00", 2)
    print(f"✅ Le Bernardin booking URL: {booking}")


def test_recommender():
    print("\n=== TEST: Recommender ===")
    from reservation.recommender import MichelinScraper, TimeOutScraper, get_recommendations

    # Test: Michelin (may be blocked)
    print("Testing Michelin scraper for Tel Aviv...")
    try:
        results = MichelinScraper.scrape_city("tel aviv")
        if results:
            print(f"✅ Michelin Tel Aviv: {len(results)} restaurants")
            for r in results[:3]:
                print(f"   - {r.name} ({r.michelin_category})")
        else:
            print("⚠️  Michelin returned 0 results (CloudFront block or empty page)")
    except Exception as e:
        print(f"❌ Michelin error: {e}")

    # Test: TimeOut (should work)
    print("\nTesting TimeOut scraper for Tel Aviv...")
    try:
        results = TimeOutScraper.scrape_city("tel aviv")
        if results:
            print(f"✅ TimeOut Tel Aviv: {len(results)} restaurants")
            for r in results[:3]:
                print(f"   - {r.name}")
        else:
            print("⚠️  TimeOut returned 0 results")
    except Exception as e:
        print(f"❌ TimeOut error: {e}")

    # Test: Pre-cached recommendations
    from reservation.recommender import CACHED_RECOMMENDATIONS
    marseille = CACHED_RECOMMENDATIONS.get("marseille", [])
    print(f"\n✅ Pre-cached Marseille recommendations: {len(marseille)}")
    for r in marseille:
        print(f"   - {r.name} ({r.michelin_category}) [{', '.join(r.sources)}]")


def test_unified():
    print("\n=== TEST: Unified Search ===")
    from reservation.unified import search, format_results_for_kai

    print("Testing unified search for Tel Aviv...")
    try:
        results = search(
            city="tel aviv",
            date="2026-04-15",
            time="20:00",
            size=2,
            include_recommendations=True,
        )
        print(f"✅ Search complete")
        print(f"   Availability results: {len(results['availability'])}")
        print(f"   Recommendations: {len(results['recommendations'])}")
        print(f"   Platform status: {results['platform_status']}")
        print(f"\n--- Formatted output ---")
        print(format_results_for_kai(results, "tel aviv", "2026-04-15", 2))
    except Exception as e:
        print(f"❌ Unified search error: {e}")


def test_ontopo_booking_discovery():
    """
    INTERACTIVE TEST: Discover the Ontopo booking endpoint.
    Requires: a restaurant with free cancellation and your phone number.
    
    Instructions:
    1. Find a restaurant on Ontopo that allows free cancellation
    2. Get its postSlug
    3. Run this test and observe the network calls
    """
    print("\n=== TEST: Ontopo Booking Discovery (INTERACTIVE) ===")
    print("This test requires manual setup. See comments in test_live.py")
    print()
    print("To discover the booking endpoint:")
    print("1. Open Chrome DevTools → Network tab")
    print("2. Go to ontopo.com and try to make a reservation")
    print("3. Look for POST calls after selecting a time slot")
    print("4. Document the endpoint, payload, and response")
    print()
    print("Suspected endpoint: POST /api/reserve_request")
    print("Suspected payload: {availability_id, personal_details: {first_name, last_name, phone, email}}")


if __name__ == "__main__":
    print("🍽️  Reservation Skill - Live Tests")
    print("=" * 50)
    
    tests = {
        "ontopo": test_ontopo,
        "tabit": test_tabit,
        "thefork": test_thefork,
        "opentable": test_opentable,
        "recommender": test_recommender,
        "unified": test_unified,
        "booking_discovery": test_ontopo_booking_discovery,
    }
    
    # Run specific test or all
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        if test_name in tests:
            tests[test_name]()
        else:
            print(f"Unknown test: {test_name}")
            print(f"Available: {', '.join(tests.keys())}")
    else:
        # Run all non-interactive tests
        for name, fn in tests.items():
            if name != "booking_discovery":
                try:
                    fn()
                except Exception as e:
                    print(f"❌ Test {name} crashed: {e}")
        
        print("\n" + "=" * 50)
        print("✅ Test run complete")
        print("Run 'python -m reservation.test_live booking_discovery' for booking endpoint discovery")
