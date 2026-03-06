#!/usr/bin/env python3
"""
GolfNow Tee Time Search — Batch query multiple courses via reverse-engineered API.

Usage:
  python3 golfnow-search.py --date "Feb 16 2026" --players 2 --lat 26.1224 --lng -80.1373
  python3 golfnow-search.py --date "Feb 16 2026" --players 2 --facilities 5744,10239,4482
  python3 golfnow-search.py --date "Feb 16 2026" --players 2 --area example

Areas: example, miami, westpalmbeach (predefined facility lists)
"""

import json, subprocess, sys, math, argparse
from collections import defaultdict

# ═══════════════════════════════════════════
# KNOWN FACILITY DATABASE — Your Area
# ═══════════════════════════════════════════

FACILITIES = {
    # Add your local courses here
    # Format: "cityname": [(facility_id, "Course Name"), ...]
    # Find facility IDs by searching on golfnow.com and checking the URL
    "example": [
        (1234, "Example Golf Club"),
        (5678, "Sample Country Club"),
    ],
}

# Default: Your City home base
DEFAULT_LAT = 26.1224
DEFAULT_LNG = -80.1373


def haversine(lat1, lng1, lat2, lng2):
    """Distance in miles between two lat/lng points."""
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
    return 3959 * 2 * math.asin(math.sqrt(a))


def fetch_facility(fid, date, players, lat, lng):
    """Fetch tee times for a single facility."""
    payload = json.dumps({
        "Radius": 50, "Latitude": lat, "Longitude": lng,
        "PageSize": 50, "PageNumber": 0, "SearchType": 1,
        "SortBy": "Date", "SortDirection": 0, "Date": date,
        "BestDealsOnly": False, "PriceMin": "0", "PriceMax": "10000",
        "Players": str(players), "Holes": "3", "FacilityType": 0,
        "RateType": "all", "TimeMin": "10", "TimeMax": "42",
        "FacilityId": fid, "SortByRollup": "Date.MinDate", "View": "Grouping",
        "ExcludeFeaturedFacilities": True, "TeeTimeCount": 50,
        "PromotedCampaignsOnly": "false",
        "CurrentClientDate": f"{date.split()[-1]}-01-01T05:00:00.000Z"
    })

    try:
        r = subprocess.run([
            'curl', '-s', '-X', 'POST',
            'https://www.golfnow.com/api/tee-times/tee-time-results',
            '-H', 'Content-Type: application/json',
            '-H', 'Accept: application/json',
            '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            '-H', 'Origin: https://www.golfnow.com',
            '-d', payload
        ], capture_output=True, text=True, timeout=15)
        return json.loads(r.stdout)
    except:
        return None


def parse_results(data, home_lat, home_lng):
    """Parse API response into structured course data."""
    times = data.get('ttResults', {}).get('teeTimes', [])
    if not times:
        return None

    fac = times[0]['facility']
    dist = haversine(home_lat, home_lng, fac.get('latitude', 0), fac.get('longitude', 0))

    slots = []
    has_hot = has_trade = False
    for t in times:
        hot = any(r.get('isHotDeal', False) for r in t.get('teeTimeRates', []))
        trade = any(r.get('isTradeOffer', False) for r in t.get('teeTimeRates', []))
        if hot: has_hot = True
        if trade: has_trade = True
        slots.append({
            'time': f"{t.get('formattedTime', '?')} {t.get('formattedTimeMeridian', '')}",
            'price': t.get('displayRate', 0),
            'fee': t.get('maxPriceTransactionFee', 0),
            'holes': t.get('multipleHolesRate', 18),
            'rate': t.get('teeTimeRates', [{}])[0].get('rateName', ''),
            'cart': any(r.get('isCartIncluded', False) for r in t.get('teeTimeRates', [])),
            'hot': hot, 'trade': trade,
        })

    return {
        'name': fac['name'],
        'city': fac.get('address', {}).get('city', '?'),
        'rating': fac.get('averageRating', 0),
        'reviews': fac.get('reviewCount', 0),
        'seo': fac.get('seoFriendlyName', ''),
        'dist': dist,
        'slots': slots,
        'has_hot': has_hot, 'has_trade': has_trade,
    }


def format_telegram(courses, date, players):
    """Format results for Telegram output."""
    lines = [f"🏌️ *Tee Times · {date} · {players} Players*\n"]
    lines.append("⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n")

    # Deals first
    deals = [c for c in courses if c['has_hot'] or c['has_trade']]
    if deals:
        for c in deals:
            flag = "🔥" if c['has_hot'] else "💳"
            url = f"https://www.golfnow.com/tee-times/facility/{c['seo']}/search"
            lines.append(f"{flag} *[{c['name']}]({url})*")
            lines.append(f"{c['city']} · {c['dist']:.1f} mi · ⭐ {c['rating']:.1f} · {c['reviews']} reviews")
            for s in c['slots']:
                if s['hot'] or s['trade']:
                    sf = " 🔥" if s['hot'] else " 💳"
                    lines.append(f"▸ {s['time']} · *${s['price']:.0f}* · {s['holes']} holes{sf}")
            lines.append("")
        lines.append("⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n")

    # All courses
    for c in courses:
        url = f"https://www.golfnow.com/tee-times/facility/{c['seo']}/search"
        lines.append(f"*[{c['name']}]({url})*")
        lines.append(f"{c['city']} · {c['dist']:.1f} mi · ⭐ {c['rating']:.1f} · {c['reviews']} reviews")

        by_price = defaultdict(list)
        for s in c['slots']:
            by_price[s['price']].append(s)

        for price, pslots in sorted(by_price.items()):
            ts = [s['time'] for s in pslots]
            if len(ts) > 4:
                summary = f"{ts[0]} – {ts[-1]} ({len(ts)} slots)"
            else:
                summary = ' / '.join(ts)
            note = f" {pslots[0]['rate']}" if 'twilight' in pslots[0]['rate'].lower() else ""
            lines.append(f"▸ {summary} · ${price:.0f}{note}")
        lines.append("")

    lines.append("⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯")
    lines.append("_All prices per player · cart included · via GolfNow_")
    return '\n'.join(lines)


def format_plain(courses):
    """Format results as plain text."""
    for c in courses:
        url = f"https://www.golfnow.com/tee-times/facility/{c['seo']}/search"
        flags = []
        if c['has_hot']: flags.append("🔥HOT")
        if c['has_trade']: flags.append("💳CREDIT")
        print(f"\n⛳ {c['name']} ({c['city']}) — {c['dist']:.1f} mi — ⭐{c['rating']:.1f} ({c['reviews']} reviews) {' '.join(flags)}")
        print(f"   {url}")
        for s in c['slots']:
            f = " 🔥" if s['hot'] else (" 💳" if s['trade'] else "")
            print(f"   {s['time']:>10} | ${s['price']:<5.0f} | {s['holes']}h | {s['rate']}{f}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='GolfNow Tee Time Search')
    parser.add_argument('--date', required=True, help='Date like "Feb 16 2026"')
    parser.add_argument('--players', type=int, default=2)
    parser.add_argument('--lat', type=float, default=DEFAULT_LAT)
    parser.add_argument('--lng', type=float, default=DEFAULT_LNG)
    parser.add_argument('--facilities', help='Comma-separated facility IDs')
    parser.add_argument('--area', default='example', help='Predefined area name')
    parser.add_argument('--format', choices=['plain', 'telegram', 'json'], default='plain')
    args = parser.parse_args()

    if args.facilities:
        fac_list = [(int(f.strip()), f"Facility {f.strip()}") for f in args.facilities.split(',')]
    else:
        fac_list = FACILITIES.get(args.area, FACILITIES['example'])

    courses = []
    no_avail = []
    for fid, label in fac_list:
        data = fetch_facility(fid, args.date, args.players, args.lat, args.lng)
        if data:
            result = parse_results(data, args.lat, args.lng)
            if result:
                courses.append(result)
                continue
        no_avail.append(label)

    courses.sort(key=lambda x: x['dist'])

    if args.format == 'telegram':
        print(format_telegram(courses, args.date, args.players))
    elif args.format == 'json':
        print(json.dumps(courses, indent=2, default=str))
    else:
        format_plain(courses)

    if no_avail:
        print(f"\n❌ No availability: {', '.join(no_avail)}")
