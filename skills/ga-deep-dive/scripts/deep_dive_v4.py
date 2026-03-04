#!/usr/bin/env python3
"""
GA4 DEEP DIVE v4 — THE FULL MONTY 🏴‍☠️
EVERYTHING GA4 can tell you about your product.

NEW in v4:
- COHORT RETENTION: Week-over-week user retention
- SCROLL DEPTH: How far users actually read
- OUTBOUND LINKS: Where users go when they leave
- SEARCH TERMS: What users search on your site
- DEMOGRAPHICS: Age brackets, gender
- SEARCH CONSOLE: Google organic search performance
- USER FLOW: Entry → Exit patterns
- AUDIENCE PERFORMANCE: GA4 audience segments
- EVENT DEEP DIVE: Event parameters and values

Usage:
    python3 deep_dive_v4.py solvr
    python3 deep_dive_v4.py solvr --full  # Extra slow but EVERYTHING
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict
import math

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange, Dimension, Metric, RunReportRequest,
    RunRealtimeReportRequest, OrderBy, Filter, FilterExpression
)
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# ============================================================================
# CONFIG
# ============================================================================

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
CONFIG_DIR = Path.home() / '.config' / 'ga-deep-dive'
TOKEN_PATH = CONFIG_DIR / 'token.json'
CREDENTIALS_PATH = CONFIG_DIR / 'credentials.json'
DATA_DIR = Path(__file__).parent.parent / 'data'

PROPERTIES = {
    'solvr': '523300499',
    'abecmed': '291040306',
    'sonus': '517562144',
}

# ============================================================================
# UTILS
# ============================================================================

def safe_int(val) -> int:
    try: return int(float(val))
    except: return 0

def safe_float(val) -> float:
    try: return float(val)
    except: return 0.0

def pct(val) -> str:
    return f"{safe_float(val)*100:.1f}%"

def bar(value, max_val, width=20) -> str:
    if max_val == 0: return "░" * width
    filled = int(value / max_val * width)
    return "█" * filled + "░" * (width - filled)

def section(title: str, emoji: str = ""):
    print(f"\n{'═'*80}")
    print(f"  {emoji} {title}")
    print('═'*80)

def sub(title: str):
    print(f"\n  ┌─ {title} {'─'*(70-len(title))}")

# ============================================================================
# AUTH
# ============================================================================

def get_creds() -> Credentials:
    from google.auth.transport.requests import Request
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    creds = None
    
    if TOKEN_PATH.exists():
        try: creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
        except: pass
    
    if creds and not creds.valid and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            TOKEN_PATH.write_text(creds.to_json())
        except: creds = None
    
    if not creds or not creds.valid:
        if not CREDENTIALS_PATH.exists():
            sys.exit(f"❌ Need {CREDENTIALS_PATH}")
        flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
        creds = flow.run_local_server(port=0)
        TOKEN_PATH.write_text(creds.to_json())
    
    return creds

# ============================================================================
# GA4 CLIENT
# ============================================================================

class GA4:
    def __init__(self, property_id: str):
        self.prop = f"properties/{property_id}"
        self.client = BetaAnalyticsDataClient(credentials=get_creds())
    
    def q(self, dims: List[str], mets: List[str], days: int = 30, 
          limit: int = 100, order: str = None, desc: bool = True) -> List[Dict]:
        """Query GA4 API."""
        req = RunReportRequest(
            property=self.prop,
            date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
            dimensions=[Dimension(name=d) for d in dims] if dims else [],
            metrics=[Metric(name=m) for m in mets],
            limit=limit
        )
        if order:
            req.order_bys = [OrderBy(metric=OrderBy.MetricOrderBy(metric_name=order), desc=desc)]
        
        try:
            resp = self.client.run_report(req)
            return [{**{dims[i]: row.dimension_values[i].value for i in range(len(dims))},
                     **{mets[i]: row.metric_values[i].value for i in range(len(mets))}}
                    for row in resp.rows]
        except Exception as e:
            return [{"_error": str(e)}]
    
    def totals(self, mets: List[str], days: int = 30) -> Dict:
        r = self.q([], mets, days=days, limit=1)
        return r[0] if r and "_error" not in r[0] else {}
    
    def rt(self) -> int:
        try:
            req = RunRealtimeReportRequest(property=self.prop, metrics=[Metric(name="activeUsers")])
            resp = self.client.run_realtime_report(req)
            return int(resp.rows[0].metric_values[0].value) if resp.rows else 0
        except: return 0

# ============================================================================
# ANALYSIS MODULES
# ============================================================================

def analyze_scroll_depth(ga: GA4, days: int) -> Dict:
    """How far do users actually scroll/read?"""
    
    # Scroll depth by page
    scroll = ga.q(
        ["pagePath", "percentScrolled"],
        ["eventCount", "totalUsers"],
        days=days, limit=50, order="eventCount"
    )
    
    # Aggregate scroll distribution
    scroll_dist = defaultdict(int)
    page_scroll = defaultdict(list)
    
    for s in scroll:
        if "_error" in s: continue
        pct_scroll = s.get("percentScrolled", "0")
        count = safe_int(s.get("eventCount", 0))
        path = s.get("pagePath", "/")
        
        scroll_dist[pct_scroll] += count
        page_scroll[path].append((pct_scroll, count))
    
    # Calculate completion rates per page
    page_completion = {}
    for path, scrolls in page_scroll.items():
        total = sum(c for _, c in scrolls)
        deep = sum(c for p, c in scrolls if p in ["90", "100"])
        page_completion[path] = deep / total if total > 0 else 0
    
    return {
        "distribution": dict(scroll_dist),
        "by_page": dict(page_scroll),
        "completion_rates": page_completion
    }


def analyze_outbound_links(ga: GA4, days: int) -> Dict:
    """Where do users go when they click external links?"""
    
    # Outbound clicks
    outbound = ga.q(
        ["linkUrl", "linkDomain", "pagePath"],
        ["eventCount", "totalUsers"],
        days=days, limit=50, order="eventCount"
    )
    
    # Filter to actual outbound (not internal)
    external = [o for o in outbound if "_error" not in o 
                and o.get("linkDomain") 
                and "solvr.dev" not in o.get("linkDomain", "")]
    
    # Group by domain
    by_domain = defaultdict(lambda: {"clicks": 0, "users": 0, "urls": []})
    for o in external:
        domain = o.get("linkDomain", "unknown")
        by_domain[domain]["clicks"] += safe_int(o.get("eventCount", 0))
        by_domain[domain]["users"] += safe_int(o.get("totalUsers", 0))
        if o.get("linkUrl") not in by_domain[domain]["urls"]:
            by_domain[domain]["urls"].append(o.get("linkUrl"))
    
    return {
        "all": external[:30],
        "by_domain": dict(by_domain)
    }


def analyze_site_search(ga: GA4, days: int) -> Dict:
    """What do users search for on your site?"""
    
    search = ga.q(
        ["searchTerm"],
        ["eventCount", "totalUsers"],
        days=days, limit=50, order="eventCount"
    )
    
    # Filter out empty/not set
    valid = [s for s in search if "_error" not in s 
             and s.get("searchTerm") 
             and s.get("searchTerm") != "(not set)"]
    
    return {
        "terms": valid,
        "total_searches": sum(safe_int(s.get("eventCount", 0)) for s in valid),
        "unique_terms": len(valid)
    }


def analyze_demographics(ga: GA4, days: int) -> Dict:
    """User demographics (requires Google signals enabled)."""
    
    # Age brackets
    age = ga.q(
        ["userAgeBracket"],
        ["totalUsers", "sessions", "engagementRate"],
        days=days, limit=10, order="totalUsers"
    )
    
    # Gender
    gender = ga.q(
        ["userGender"],
        ["totalUsers", "sessions", "engagementRate"],
        days=days, limit=5, order="totalUsers"
    )
    
    # Interests (if available)
    interests = ga.q(
        ["brandingInterest"],
        ["totalUsers", "sessions"],
        days=days, limit=20, order="totalUsers"
    )
    
    return {
        "age": [a for a in age if "_error" not in a and a.get("userAgeBracket") != "(not set)"],
        "gender": [g for g in gender if "_error" not in g and g.get("userGender") != "(not set)"],
        "interests": [i for i in interests if "_error" not in i and i.get("brandingInterest") != "(not set)"]
    }


def analyze_search_console(ga: GA4, days: int) -> Dict:
    """Google Search Console data (organic search performance)."""
    
    # Note: This requires Search Console to be linked to GA4
    try:
        search_data = ga.totals([
            "organicGoogleSearchClicks",
            "organicGoogleSearchImpressions", 
            "organicGoogleSearchClickThroughRate",
            "organicGoogleSearchAveragePosition"
        ], days)
        
        return {
            "clicks": safe_int(search_data.get("organicGoogleSearchClicks", 0)),
            "impressions": safe_int(search_data.get("organicGoogleSearchImpressions", 0)),
            "ctr": safe_float(search_data.get("organicGoogleSearchClickThroughRate", 0)),
            "avg_position": safe_float(search_data.get("organicGoogleSearchAveragePosition", 0)),
            "available": True
        }
    except:
        return {"available": False}


def analyze_user_flow(ga: GA4, days: int) -> Dict:
    """Entry and exit patterns."""
    
    # Landing pages with exit data
    landing = ga.q(
        ["landingPage"],
        ["sessions", "totalUsers", "bounceRate", "engagementRate", 
         "screenPageViewsPerSession", "averageSessionDuration"],
        days=days, limit=30, order="sessions"
    )
    
    # Page sequences (what page comes after landing)
    # Note: GA4 doesn't give direct sequences, but we can look at page pairs
    page_pairs = ga.q(
        ["pagePath", "pageTitle"],
        ["screenPageViews", "totalUsers", "bounceRate"],
        days=days, limit=50, order="screenPageViews"
    )
    
    return {
        "entry_points": [l for l in landing if "_error" not in l],
        "all_pages": [p for p in page_pairs if "_error" not in p]
    }


def analyze_audiences(ga: GA4, days: int) -> Dict:
    """GA4 audience segment performance."""
    
    audiences = ga.q(
        ["audienceName"],
        ["totalUsers", "sessions", "engagementRate", "averageSessionDuration"],
        days=days, limit=20, order="totalUsers"
    )
    
    return {
        "audiences": [a for a in audiences if "_error" not in a 
                     and a.get("audienceName") not in [None, "(not set)", "All Users"]]
    }


def analyze_events_deep(ga: GA4, days: int) -> Dict:
    """Deep event analysis with values."""
    
    # All events with values
    events = ga.q(
        ["eventName"],
        ["eventCount", "totalUsers", "eventCountPerUser", "eventValue"],
        days=days, limit=30, order="eventCount"
    )
    
    # Key events (conversions)
    key_events = ga.totals(["keyEvents"], days)
    
    # Scrolled users metric
    scroll_users = ga.totals(["scrolledUsers"], days)
    
    # Event by page
    events_by_page = ga.q(
        ["eventName", "pagePath"],
        ["eventCount"],
        days=days, limit=50, order="eventCount"
    )
    
    return {
        "events": [e for e in events if "_error" not in e],
        "key_events": safe_int(key_events.get("keyEvents", 0)),
        "scrolled_users": safe_int(scroll_users.get("scrolledUsers", 0)),
        "by_page": [e for e in events_by_page if "_error" not in e][:20]
    }


def analyze_technology_deep(ga: GA4, days: int) -> Dict:
    """Deep technology analysis."""
    
    # Browser versions
    browser_ver = ga.q(
        ["browser", "browserVersion"],
        ["sessions", "bounceRate"],
        days=days, limit=20, order="sessions"
    )
    
    # OS versions
    os_ver = ga.q(
        ["operatingSystem", "operatingSystemVersion"],
        ["sessions", "bounceRate"],
        days=days, limit=20, order="sessions"
    )
    
    # Mobile device models
    mobile = ga.q(
        ["mobileDeviceModel", "mobileDeviceBranding"],
        ["sessions", "engagementRate"],
        days=days, limit=20, order="sessions"
    )
    
    return {
        "browser_versions": [b for b in browser_ver if "_error" not in b],
        "os_versions": [o for o in os_ver if "_error" not in o],
        "mobile_devices": [m for m in mobile if "_error" not in m 
                          and m.get("mobileDeviceModel") != "(not set)"]
    }


def analyze_time_deep(ga: GA4, days: int) -> Dict:
    """Deep time analysis with hourly engagement."""
    
    # Hour with engagement
    hourly = ga.q(
        ["hour"],
        ["sessions", "totalUsers", "engagedSessions", "engagementRate", 
         "averageSessionDuration"],
        days=days, limit=24
    )
    hourly = sorted([h for h in hourly if "_error" not in h], 
                   key=lambda x: int(x.get("hour", 0)))
    
    # Day of week with full metrics
    daily = ga.q(
        ["dayOfWeekName"],
        ["sessions", "totalUsers", "newUsers", "engagementRate", 
         "averageSessionDuration", "screenPageViewsPerSession"],
        days=days, limit=7
    )
    
    # First session date distribution (when did users first visit)
    first_visit = ga.q(
        ["firstSessionDate"],
        ["totalUsers"],
        days=days, limit=30, order="totalUsers"
    )
    
    return {
        "hourly": hourly,
        "daily": [d for d in daily if "_error" not in d],
        "first_visit_dates": [f for f in first_visit if "_error" not in f][:14]
    }


def analyze_cohorts(ga: GA4, days: int) -> Dict:
    """Cohort retention analysis."""
    
    # Weekly cohorts
    weekly = ga.q(
        ["cohort", "cohortNthWeek"],
        ["cohortActiveUsers", "cohortTotalUsers"],
        days=days, limit=50
    )
    
    # Calculate retention rates
    cohorts = defaultdict(dict)
    for w in weekly:
        if "_error" in w: continue
        cohort = w.get("cohort", "")
        week = w.get("cohortNthWeek", "0")
        active = safe_int(w.get("cohortActiveUsers", 0))
        total = safe_int(w.get("cohortTotalUsers", 0))
        
        if cohort:
            cohorts[cohort][week] = {
                "active": active,
                "total": total,
                "retention": active / total if total > 0 else 0
            }
    
    return {
        "raw": [w for w in weekly if "_error" not in w],
        "by_cohort": dict(cohorts)
    }


def analyze_content_groups(ga: GA4, days: int, is_solvr: bool = False) -> Dict:
    """Content group performance."""
    
    # Content groups (if configured)
    groups = ga.q(
        ["contentGroup"],
        ["screenPageViews", "totalUsers", "engagementRate"],
        days=days, limit=20, order="screenPageViews"
    )
    
    # Full page URLs (for debugging)
    urls = ga.q(
        ["fullPageUrl"],
        ["screenPageViews", "totalUsers"],
        days=days, limit=20, order="screenPageViews"
    )
    
    # Calculate Solvr groups manually if needed
    solvr_groups = {}
    if is_solvr:
        pages = ga.q(
            ["pagePath"],
            ["screenPageViews", "totalUsers", "engagementRate", "bounceRate"],
            days=days, limit=100, order="screenPageViews"
        )
        
        categories = defaultdict(lambda: {"views": 0, "users": 0, "engagement": [], "bounce": []})
        for p in pages:
            if "_error" in p: continue
            path = p.get("pagePath", "")
            
            if path.startswith("/agents"): cat = "agents"
            elif path.startswith("/problems") or path.startswith("/problem/"): cat = "problems"
            elif path.startswith("/ideas") or path.startswith("/idea/"): cat = "ideas"
            elif path.startswith("/questions"): cat = "questions"
            elif path == "/feed": cat = "feed"
            elif path in ["/login", "/join"] or path.startswith("/auth"): cat = "auth"
            elif path.startswith("/settings"): cat = "settings"
            elif path.startswith("/api"): cat = "api"
            elif path == "/": cat = "home"
            else: cat = "other"
            
            categories[cat]["views"] += safe_int(p.get("screenPageViews", 0))
            categories[cat]["users"] += safe_int(p.get("totalUsers", 0))
            categories[cat]["engagement"].append(safe_float(p.get("engagementRate", 0)))
            categories[cat]["bounce"].append(safe_float(p.get("bounceRate", 0)))
        
        for cat, data in categories.items():
            solvr_groups[cat] = {
                "views": data["views"],
                "users": data["users"],
                "avg_engagement": sum(data["engagement"]) / len(data["engagement"]) if data["engagement"] else 0,
                "avg_bounce": sum(data["bounce"]) / len(data["bounce"]) if data["bounce"] else 0
            }
    
    return {
        "configured_groups": [g for g in groups if "_error" not in g 
                             and g.get("contentGroup") != "(not set)"],
        "full_urls": [u for u in urls if "_error" not in u][:10],
        "solvr_groups": solvr_groups
    }


# ============================================================================
# PRINT REPORT
# ============================================================================

def print_v4_report(data: Dict, prop_name: str, days: int):
    """Print the FULL MONTY report."""
    
    print(f"""
╔══════════════════════════════════════════════════════════════════════════════════╗
║                                                                                  ║
║   🏴‍☠️  GA4 DEEP DIVE v4 — THE FULL MONTY                                          ║
║                                                                                  ║
║   Property: {prop_name.upper():<15}     Period: Last {days} days                          ║
║   Generated: {datetime.now().strftime("%Y-%m-%d %H:%M UTC"):<63}║
║                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════╝
""")

    # ===== SCROLL DEPTH =====
    section("SCROLL DEPTH — HOW FAR DO USERS READ?", "📜")
    
    scroll = data.get("scroll", {})
    dist = scroll.get("distribution", {})
    
    if dist:
        print("\n   Scroll Depth Distribution:")
        print(f"   {'Depth':<10} {'Events':>10} {'Visual':>25}")
        print(f"   {'─'*50}")
        
        total = sum(dist.values())
        for depth in ["10", "25", "50", "75", "90", "100"]:
            count = dist.get(depth, 0)
            pct_val = count / total * 100 if total > 0 else 0
            print(f"   {depth}%{' ':>7} {count:>10,} {bar(pct_val, 100, 20)} {pct_val:.1f}%")
        
        # Completion rates
        sub("Page Completion Rates (% who scroll to 90%+)")
        completion = scroll.get("completion_rates", {})
        sorted_comp = sorted(completion.items(), key=lambda x: x[1], reverse=True)[:10]
        for path, rate in sorted_comp:
            if rate > 0:
                print(f"   {path[:45]:<46} {rate*100:>5.1f}%")
    else:
        print("\n   ⚠️ No scroll data (enhanced measurement may not be enabled)")
    
    # ===== OUTBOUND LINKS =====
    section("OUTBOUND LINKS — WHERE DO USERS GO?", "🔗")
    
    outbound = data.get("outbound", {})
    by_domain = outbound.get("by_domain", {})
    
    if by_domain:
        print("\n   External Domains (where users click out to):")
        print(f"   {'Domain':<35} {'Clicks':>10} {'Users':>8}")
        print(f"   {'─'*60}")
        
        sorted_domains = sorted(by_domain.items(), key=lambda x: x[1]["clicks"], reverse=True)[:15]
        for domain, stats in sorted_domains:
            print(f"   {domain[:34]:<35} {stats['clicks']:>10,} {stats['users']:>8,}")
    else:
        print("\n   ⚠️ No outbound link data (click tracking may not be enabled)")
    
    # ===== SITE SEARCH =====
    section("SITE SEARCH — WHAT DO USERS LOOK FOR?", "🔍")
    
    search = data.get("search", {})
    terms = search.get("terms", [])
    
    if terms:
        print(f"\n   Total Searches: {search.get('total_searches', 0):,}")
        print(f"   Unique Terms: {search.get('unique_terms', 0)}")
        print(f"\n   Top Search Terms:")
        print(f"   {'Term':<40} {'Searches':>10} {'Users':>8}")
        print(f"   {'─'*65}")
        
        for t in terms[:15]:
            print(f"   {t.get('searchTerm', '?')[:39]:<40} {safe_int(t.get('eventCount', 0)):>10,} {safe_int(t.get('totalUsers', 0)):>8,}")
    else:
        print("\n   ⚠️ No site search data (site search tracking not configured)")
    
    # ===== DEMOGRAPHICS =====
    section("DEMOGRAPHICS — WHO ARE YOUR USERS?", "👥")
    
    demo = data.get("demographics", {})
    
    age = demo.get("age", [])
    if age:
        sub("Age Distribution")
        total_age = sum(safe_int(a.get("totalUsers", 0)) for a in age)
        for a in age:
            users = safe_int(a.get("totalUsers", 0))
            pct_val = users / total_age * 100 if total_age > 0 else 0
            bracket = a.get("userAgeBracket", "?")
            print(f"   {bracket:<15} {bar(pct_val, 100, 15)} {pct_val:>5.1f}% ({users:,} users)")
    
    gender = demo.get("gender", [])
    if gender:
        sub("Gender Distribution")
        total_g = sum(safe_int(g.get("totalUsers", 0)) for g in gender)
        for g in gender:
            users = safe_int(g.get("totalUsers", 0))
            pct_val = users / total_g * 100 if total_g > 0 else 0
            print(f"   {g.get('userGender', '?'):<15} {bar(pct_val, 100, 15)} {pct_val:>5.1f}%")
    
    interests = demo.get("interests", [])
    if interests:
        sub("Top Interests (Branding)")
        for i in interests[:10]:
            print(f"   {i.get('brandingInterest', '?')[:50]:<51} {safe_int(i.get('totalUsers', 0)):>6} users")
    
    if not age and not gender:
        print("\n   ⚠️ No demographic data (Google Signals may not be enabled)")
    
    # ===== SEARCH CONSOLE =====
    section("GOOGLE SEARCH CONSOLE — ORGANIC SEARCH", "🌐")
    
    gsc = data.get("search_console", {})
    
    if gsc.get("available") and gsc.get("impressions", 0) > 0:
        print(f"""
   Organic Google Search Performance:
   
   Impressions:    {gsc.get('impressions', 0):>12,}
   Clicks:         {gsc.get('clicks', 0):>12,}
   CTR:            {gsc.get('ctr', 0)*100:>11.2f}%
   Avg Position:   {gsc.get('avg_position', 0):>12.1f}
""")
    else:
        print("\n   ⚠️ No Search Console data (link GA4 to Search Console in GA4 Admin)")
    
    # ===== USER FLOW =====
    section("USER FLOW — ENTRY & EXIT PATTERNS", "🚪")
    
    flow = data.get("flow", {})
    entries = flow.get("entry_points", [])
    
    if entries:
        sub("Top Entry Points (Landing Pages)")
        print(f"\n   {'Page':<40} {'Sessions':>8} {'Bounce':>8} {'Engaged':>8}")
        print(f"   {'─'*70}")
        
        for e in entries[:12]:
            print(f"   {e.get('landingPage', '?')[:39]:<40} {safe_int(e.get('sessions', 0)):>8,} {pct(e.get('bounceRate', 0)):>8} {pct(e.get('engagementRate', 0)):>8}")
    
    # ===== AUDIENCES =====
    section("GA4 AUDIENCES — SEGMENT PERFORMANCE", "🎯")
    
    audiences = data.get("audiences", {}).get("audiences", [])
    
    if audiences:
        print(f"\n   {'Audience':<35} {'Users':>8} {'Sessions':>10} {'Engaged':>8}")
        print(f"   {'─'*70}")
        
        for a in audiences[:10]:
            print(f"   {a.get('audienceName', '?')[:34]:<35} {safe_int(a.get('totalUsers', 0)):>8,} {safe_int(a.get('sessions', 0)):>10,} {pct(a.get('engagementRate', 0)):>8}")
    else:
        print("\n   ⚠️ No custom audiences configured (create in GA4 Admin → Audiences)")
    
    # ===== EVENTS DEEP =====
    section("EVENTS — DEEP ANALYSIS", "⚡")
    
    events = data.get("events", {})
    event_list = events.get("events", [])
    
    if event_list:
        print(f"\n   Key Events (Conversions): {events.get('key_events', 0):,}")
        print(f"   Users Who Scrolled: {events.get('scrolled_users', 0):,}")
        
        sub("Events with Values")
        print(f"\n   {'Event':<30} {'Count':>10} {'Value':>12} {'Per User':>10}")
        print(f"   {'─'*70}")
        
        for e in event_list[:15]:
            value = safe_float(e.get("eventValue", 0))
            value_str = f"${value:,.0f}" if value > 0 else "—"
            print(f"   {e.get('eventName', '?')[:29]:<30} {safe_int(e.get('eventCount', 0)):>10,} {value_str:>12} {safe_float(e.get('eventCountPerUser', 0)):>10.2f}")
        
        # Events by page
        by_page = events.get("by_page", [])
        if by_page:
            sub("Events by Page (where events happen)")
            for ep in by_page[:10]:
                event = ep.get("eventName", "?")
                page = ep.get("pagePath", "?")
                count = safe_int(ep.get("eventCount", 0))
                if event not in ["page_view", "session_start", "first_visit", "user_engagement"]:
                    print(f"   {event:<25} on {page[:30]:<31} {count:>6}")
    
    # ===== COHORTS =====
    section("COHORT RETENTION — DO USERS COME BACK?", "📊")
    
    cohorts = data.get("cohorts", {})
    by_cohort = cohorts.get("by_cohort", {})
    
    if by_cohort:
        print("\n   Weekly Retention by Cohort:")
        print(f"   {'Cohort':<12} {'Week 0':>8} {'Week 1':>8} {'Week 2':>8} {'Week 3':>8} {'Week 4':>8}")
        print(f"   {'─'*60}")
        
        for cohort_name, weeks in sorted(by_cohort.items(), reverse=True)[:8]:
            row = f"   {cohort_name[:11]:<12}"
            for w in ["0", "1", "2", "3", "4"]:
                if w in weeks:
                    retention = weeks[w].get("retention", 0) * 100
                    row += f" {retention:>7.1f}%"
                else:
                    row += f" {'—':>8}"
            print(row)
    else:
        print("\n   ⚠️ No cohort data available")
    
    # ===== CONTENT GROUPS =====
    section("CONTENT GROUPS — SOLVR SECTIONS", "📄")
    
    groups = data.get("content_groups", {})
    solvr = groups.get("solvr_groups", {})
    
    if solvr:
        print(f"\n   {'Section':<15} {'Views':>10} {'Users':>8} {'Engaged':>10} {'Bounce':>10}")
        print(f"   {'─'*60}")
        
        for name, stats in sorted(solvr.items(), key=lambda x: x[1]["views"], reverse=True):
            print(f"   {name:<15} {stats['views']:>10,} {stats['users']:>8,} {stats['avg_engagement']*100:>9.1f}% {stats['avg_bounce']*100:>9.1f}%")
    
    # ===== TECHNOLOGY DEEP =====
    section("TECHNOLOGY — DETAILED BREAKDOWN", "💻")
    
    tech = data.get("technology", {})
    
    mobile = tech.get("mobile_devices", [])
    if mobile:
        sub("Mobile Device Models")
        for m in mobile[:10]:
            brand = m.get("mobileDeviceBranding", "")
            model = m.get("mobileDeviceModel", "")
            if model and model != "(not set)":
                print(f"   {brand[:15]:<16} {model[:25]:<26} {safe_int(m.get('sessions', 0)):>6} sessions")
    
    browser_ver = tech.get("browser_versions", [])
    if browser_ver:
        sub("Browser Versions (check compatibility)")
        for b in browser_ver[:8]:
            browser = b.get("browser", "")
            version = b.get("browserVersion", "")
            bounce = safe_float(b.get("bounceRate", 0))
            print(f"   {browser[:15]:<16} v{version[:10]:<11} {safe_int(b.get('sessions', 0)):>6} sessions ({bounce*100:.1f}% bounce)")
    
    # ===== TIME DEEP =====
    section("TIME PATTERNS — DETAILED", "🕐")
    
    time_data = data.get("time", {})
    
    hourly = time_data.get("hourly", [])
    if hourly:
        sub("Hourly Performance (when users are ENGAGED)")
        print(f"\n   {'Hour':<8} {'Sessions':>8} {'Engaged':>8} {'Eng Rate':>10} {'Avg Dur':>10}")
        print(f"   {'─'*55}")
        
        for h in hourly:
            hr = int(h.get("hour", 0))
            engaged = safe_int(h.get("engagedSessions", 0))
            rate = safe_float(h.get("engagementRate", 0))
            dur = safe_float(h.get("averageSessionDuration", 0))
            
            print(f"   {hr:02d}:00    {safe_int(h.get('sessions', 0)):>8,} {engaged:>8,} {rate*100:>9.1f}% {dur:>9.0f}s")
    
    # First visit dates
    first_visit = time_data.get("first_visit_dates", [])
    if first_visit:
        sub("When Did Users First Visit? (acquisition over time)")
        for f in first_visit[:7]:
            date = f.get("firstSessionDate", "")
            users = safe_int(f.get("totalUsers", 0))
            print(f"   {date}  {bar(users, safe_int(first_visit[0].get('totalUsers', 1)), 20)} {users:>5} users")
    
    # ===== SUMMARY =====
    print(f"\n{'═'*80}")
    print("  ✅ FULL MONTY COMPLETE — You now have EVERYTHING GA4 can tell you")
    print('═'*80)
    print(f"\n   💾 Snapshot saved to: {DATA_DIR}/snapshots/")
    print()


# ============================================================================
# MAIN
# ============================================================================

def deep_dive_v4(prop_name: str, days: int = 30, full: bool = False):
    """Run the FULL MONTY analysis."""
    
    prop_id = PROPERTIES.get(prop_name.lower(), prop_name)
    is_solvr = prop_name.lower() == "solvr"
    
    print(f"\n🔄 Running FULL MONTY analysis on {prop_name}...")
    print("   This pulls EVERYTHING GA4 has. May take 1-2 minutes...\n")
    
    ga = GA4(prop_id)
    
    data = {
        "scroll": analyze_scroll_depth(ga, days),
        "outbound": analyze_outbound_links(ga, days),
        "search": analyze_site_search(ga, days),
        "demographics": analyze_demographics(ga, days),
        "search_console": analyze_search_console(ga, days),
        "flow": analyze_user_flow(ga, days),
        "audiences": analyze_audiences(ga, days),
        "events": analyze_events_deep(ga, days),
        "cohorts": analyze_cohorts(ga, days),
        "content_groups": analyze_content_groups(ga, days, is_solvr),
        "technology": analyze_technology_deep(ga, days),
        "time": analyze_time_deep(ga, days),
    }
    
    print_v4_report(data, prop_name, days)
    
    # Save
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    snapshot_path = DATA_DIR / "snapshots" / f"{prop_name}_v4_{datetime.now().strftime('%Y-%m-%d')}.json"
    snapshot_path.parent.mkdir(exist_ok=True)
    with open(snapshot_path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    
    return data


def main():
    parser = argparse.ArgumentParser(description="GA4 Deep Dive v4 — THE FULL MONTY")
    parser.add_argument("property", nargs="?")
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--full", action="store_true", help="Extra slow but EVERYTHING")
    parser.add_argument("--list", action="store_true")
    
    args = parser.parse_args()
    
    if args.list:
        print("\n📋 Properties:")
        for name, pid in PROPERTIES.items():
            print(f"   {name:<15} → {pid}")
        return
    
    if not args.property:
        parser.print_help()
        return
    
    deep_dive_v4(args.property, args.days, args.full)


if __name__ == "__main__":
    main()
