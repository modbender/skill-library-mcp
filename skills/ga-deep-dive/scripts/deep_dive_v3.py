#!/usr/bin/env python3
"""
GA4 DEEP DIVE v3 — THE OWNER'S WAR ROOM
Built for Solvr by Claudius 🏴‍☠️

This is what you ACTUALLY need to run a product:

1. COHORTS — Are users coming back? Week 1 vs Week 4 retention
2. FUNNELS — Where do users drop off? Visit → Join → API Key → Post
3. SEGMENTS — Power users vs casual, who's your 1%?
4. ATTRIBUTION — Which sources ACTUALLY convert?
5. TRENDS — What's hot? What's dying? Early warnings
6. GEOGRAPHY — Which countries are gold mines?
7. EVENTS — What do engaged users do differently?

Usage:
    python3 deep_dive_v3.py solvr
    python3 deep_dive_v3.py solvr --days 30 --output json
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import math

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange, Dimension, Metric, RunReportRequest,
    RunRealtimeReportRequest, OrderBy, Filter, FilterExpression,
    FilterExpressionList, NumericValue, CohortSpec, Cohort, CohortsRange
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
SNAPSHOTS_DIR = DATA_DIR / 'snapshots'

PROPERTIES = {
    'solvr': '523300499',
    'abecmed': '291040306', 
    'sonus': '517562144',
    'reiduchat': '470924960',
    'caosfera': '485692354',
    'ttn': '513412902',
}

# Solvr funnel stages
SOLVR_FUNNEL = {
    'visit': ['/'],
    'explore': ['/feed', '/agents', '/problems', '/ideas'],
    'auth': ['/join', '/login'],
    'onboard': ['/auth/callback', '/settings/api-keys'],
    'engage': ['/settings/agents', '/connect/agent'],
    'create': ['/problems', '/ideas'],  # POST actions tracked via events
}

# ============================================================================
# UTILITIES
# ============================================================================

def safe_int(val) -> int:
    try: return int(float(val))
    except: return 0

def safe_float(val) -> float:
    try: return float(val)
    except: return 0.0

def pct(val, decimals=1) -> str:
    return f"{safe_float(val)*100:.{decimals}f}%"

def fmt_num(n) -> str:
    n = safe_int(n)
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000: return f"{n/1_000:.1f}K"
    return str(n)

def delta_str(current, previous, reverse=False) -> str:
    if previous == 0: return "NEW" if current > 0 else "—"
    change = ((current - previous) / previous) * 100
    if reverse: change = -change  # For metrics where down is good (bounce rate)
    if change > 10: return f"🟢 +{change:.0f}%"
    elif change > 0: return f"↑{change:.0f}%"
    elif change < -10: return f"🔴 {change:.0f}%"
    elif change < 0: return f"↓{abs(change):.0f}%"
    return "→"

def bar(value, max_value, width=20) -> str:
    if max_value == 0: return "░" * width
    filled = int(value / max_value * width)
    return "█" * filled + "░" * (width - filled)

def sparkline(values: List[float]) -> str:
    if not values: return ""
    chars = "▁▂▃▄▅▆▇█"
    min_v, max_v = min(values), max(values)
    if max_v == min_v: return chars[4] * len(values)
    return "".join(chars[int((v - min_v) / (max_v - min_v) * 7)] for v in values)

def section(title: str, emoji: str = ""):
    print(f"\n{'═'*80}")
    print(f"  {emoji} {title}")
    print('═'*80)

def subsection(title: str):
    print(f"\n  ┌─ {title} {'─'*(70-len(title))}")

# ============================================================================
# AUTH
# ============================================================================

def get_credentials() -> Credentials:
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
            print(f"❌ Need {CREDENTIALS_PATH}")
            sys.exit(1)
        flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
        creds = flow.run_local_server(port=0)
        TOKEN_PATH.write_text(creds.to_json())
    
    return creds

# ============================================================================
# GA4 CLIENT
# ============================================================================

class GA4:
    def __init__(self, property_id: str):
        self.property_id = property_id
        self.client = BetaAnalyticsDataClient(credentials=get_credentials())
        self.prop = f"properties/{property_id}"
    
    def query(self, dims: List[str], mets: List[str], days: int = 30, 
              limit: int = 100, order: str = None, desc: bool = True,
              start: str = None, end: str = None) -> List[Dict]:
        
        dr = DateRange(start_date=start or f"{days}daysAgo", end_date=end or "today")
        req = RunReportRequest(
            property=self.prop,
            date_ranges=[dr],
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
        r = self.query([], mets, days=days, limit=1)
        return r[0] if r and "_error" not in r[0] else {}
    
    def realtime(self) -> int:
        try:
            req = RunRealtimeReportRequest(property=self.prop, metrics=[Metric(name="activeUsers")])
            resp = self.client.run_realtime_report(req)
            return int(resp.rows[0].metric_values[0].value) if resp.rows else 0
        except: return 0

# ============================================================================
# ANALYSIS MODULES
# ============================================================================

def analyze_executive(ga: GA4, days: int) -> Dict:
    """Executive summary with period comparison."""
    
    # This period - split into 2 queries (GA4 limit: 10 metrics)
    current1 = ga.totals([
        "sessions", "totalUsers", "newUsers", "engagedSessions",
        "engagementRate", "bounceRate", "averageSessionDuration",
        "screenPageViews", "eventCount"
    ], days)
    
    current2 = ga.totals([
        "sessionsPerUser", "screenPageViewsPerSession"
    ], days)
    
    current = {**current1, **current2}
    
    # Previous period
    today = datetime.now()
    prev_end = (today - timedelta(days=days+1)).strftime("%Y-%m-%d")
    prev_start = (today - timedelta(days=days*2+1)).strftime("%Y-%m-%d")
    previous = ga.query([], [
        "sessions", "totalUsers", "newUsers", "engagementRate",
        "bounceRate", "averageSessionDuration", "screenPageViews"
    ], start=prev_start, end=prev_end, limit=1)
    prev = previous[0] if previous and "_error" not in previous[0] else {}
    
    # Activity metrics
    activity = ga.totals(["active1DayUsers", "active7DayUsers", "active28DayUsers"], days)
    
    return {"current": current, "previous": prev, "activity": activity}


def analyze_acquisition_deep(ga: GA4, days: int) -> Dict:
    """Deep acquisition analysis with attribution."""
    
    # Channel performance with engagement
    channels = ga.query(
        ["sessionDefaultChannelGroup"],
        ["sessions", "totalUsers", "newUsers", "engagedSessions", 
         "engagementRate", "bounceRate", "averageSessionDuration",
         "screenPageViewsPerSession", "conversions"],
        days=days, limit=20, order="sessions"
    )
    
    # Source/Medium detail
    sources = ga.query(
        ["sessionSource", "sessionMedium"],
        ["sessions", "totalUsers", "newUsers", "engagementRate",
         "bounceRate", "averageSessionDuration"],
        days=days, limit=30, order="sessions"
    )
    
    # First user source (acquisition attribution)
    first_touch = ga.query(
        ["firstUserSource", "firstUserMedium", "firstUserCampaignName"],
        ["totalUsers", "newUsers", "engagementRate", "averageSessionDuration"],
        days=days, limit=20, order="totalUsers"
    )
    
    # Session source (last touch)
    last_touch = ga.query(
        ["sessionSource", "sessionMedium", "sessionCampaignName"],
        ["sessions", "engagedSessions", "conversions"],
        days=days, limit=20, order="sessions"
    )
    
    # Referrer URLs (actual links)
    referrers = ga.query(
        ["pageReferrer"],
        ["sessions", "totalUsers", "engagementRate"],
        days=days, limit=25, order="sessions"
    )
    
    return {
        "channels": channels,
        "sources": sources,
        "first_touch": first_touch,
        "last_touch": last_touch,
        "referrers": referrers
    }


def analyze_geography_deep(ga: GA4, days: int) -> Dict:
    """Geography analysis - find your gold mine countries."""
    
    # Country overview
    countries = ga.query(
        ["country"],
        ["sessions", "totalUsers", "newUsers", "engagedSessions",
         "engagementRate", "bounceRate", "averageSessionDuration",
         "screenPageViewsPerSession", "conversions"],
        days=days, limit=30, order="sessions"
    )
    
    # City detail (top 30)
    cities = ga.query(
        ["country", "city"],
        ["sessions", "totalUsers", "engagementRate", "averageSessionDuration"],
        days=days, limit=40, order="sessions"
    )
    
    # Language distribution
    languages = ga.query(
        ["language"],
        ["totalUsers", "sessions", "engagementRate"],
        days=days, limit=15, order="totalUsers"
    )
    
    # Calculate country quality score (engagement * sessions weight)
    for c in countries:
        if "_error" not in c:
            eng = safe_float(c.get("engagementRate", 0))
            sess = safe_int(c.get("sessions", 0))
            dur = safe_float(c.get("averageSessionDuration", 0))
            # Quality = engagement rate * log(sessions) * duration factor
            c["quality_score"] = eng * math.log(max(sess, 1) + 1) * min(dur/60, 5)
    
    return {
        "countries": countries,
        "cities": cities,
        "languages": languages
    }


def analyze_content_deep(ga: GA4, days: int, is_solvr: bool = False) -> Dict:
    """Content analysis - what's working, what's not."""
    
    # Page performance
    pages = ga.query(
        ["pagePath"],
        ["screenPageViews", "totalUsers", "engagementRate", 
         "bounceRate", "averageSessionDuration"],
        days=days, limit=50, order="screenPageViews"
    )
    
    # Landing pages (entry points)
    landing = ga.query(
        ["landingPage"],
        ["sessions", "totalUsers", "newUsers", "bounceRate",
         "engagementRate", "averageSessionDuration", "screenPageViewsPerSession"],
        days=days, limit=30, order="sessions"
    )
    
    # Page trends (this week vs last week)
    this_week = ga.query(
        ["pagePath"],
        ["screenPageViews", "totalUsers"],
        days=7, limit=30, order="screenPageViews"
    )
    last_week_end = (datetime.now() - timedelta(days=8)).strftime("%Y-%m-%d")
    last_week_start = (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d")
    last_week = ga.query(
        ["pagePath"],
        ["screenPageViews", "totalUsers"],
        start=last_week_start, end=last_week_end, limit=30, order="screenPageViews"
    )
    
    # Calculate trends
    last_week_map = {p["pagePath"]: safe_int(p["screenPageViews"]) 
                     for p in last_week if "_error" not in p}
    for p in this_week:
        if "_error" not in p:
            curr = safe_int(p["screenPageViews"])
            prev = last_week_map.get(p["pagePath"], 0)
            p["trend"] = ((curr - prev) / prev * 100) if prev > 0 else (100 if curr > 0 else 0)
    
    # High bounce pages (problem areas)
    high_bounce = [p for p in pages if "_error" not in p 
                   and safe_float(p.get("bounceRate", 0)) > 0.6
                   and safe_int(p.get("screenPageViews", 0)) > 3]
    
    result = {
        "pages": pages,
        "landing": landing,
        "trending": sorted([p for p in this_week if "_error" not in p], 
                          key=lambda x: x.get("trend", 0), reverse=True)[:10],
        "declining": sorted([p for p in this_week if "_error" not in p],
                           key=lambda x: x.get("trend", 0))[:10],
        "high_bounce": sorted(high_bounce, key=lambda x: safe_float(x.get("bounceRate", 0)), reverse=True)[:10]
    }
    
    # Solvr content groups
    if is_solvr:
        groups = defaultdict(lambda: {"views": 0, "users": 0, "engagement": [], "pages": 0})
        for p in pages:
            if "_error" in p: continue
            path = p.get("pagePath", "")
            
            # Categorize
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
            
            groups[cat]["views"] += safe_int(p.get("screenPageViews", 0))
            groups[cat]["users"] += safe_int(p.get("totalUsers", 0))
            groups[cat]["engagement"].append(safe_float(p.get("engagementRate", 0)))
            groups[cat]["pages"] += 1
        
        # Calculate averages
        for cat, data in groups.items():
            if data["engagement"]:
                data["avg_engagement"] = sum(data["engagement"]) / len(data["engagement"])
            else:
                data["avg_engagement"] = 0
            del data["engagement"]
        
        result["content_groups"] = dict(groups)
    
    return result


def analyze_events_deep(ga: GA4, days: int) -> Dict:
    """Event analysis - what do users actually DO."""
    
    # All events
    events = ga.query(
        ["eventName"],
        ["eventCount", "totalUsers", "eventCountPerUser"],
        days=days, limit=30, order="eventCount"
    )
    
    # Events by engaged users vs all
    engaged_events = ga.query(
        ["eventName"],
        ["eventCount", "totalUsers"],
        days=days, limit=20, order="eventCount"
    )
    
    # Custom events (non-automatic)
    auto_events = {"page_view", "scroll", "session_start", "first_visit", 
                   "user_engagement", "click", "file_download", "view_search_results"}
    custom = [e for e in events if "_error" not in e 
              and e.get("eventName") not in auto_events]
    
    # Event sequences (what happens after page_view)
    # Note: GA4 doesn't give sequences directly, but we can infer from counts
    
    return {
        "events": events,
        "custom_events": custom,
        "event_participation": {
            e["eventName"]: safe_int(e["totalUsers"]) 
            for e in events if "_error" not in e
        }
    }


def analyze_user_segments(ga: GA4, days: int) -> Dict:
    """User segmentation - find your power users."""
    
    # New vs returning
    new_ret = ga.query(
        ["newVsReturning"],
        ["sessions", "totalUsers", "engagedSessions", "engagementRate",
         "bounceRate", "screenPageViewsPerSession", "averageSessionDuration"],
        days=days, limit=5
    )
    
    # By session count (frequency)
    session_count = ga.query(
        ["sessionDefaultChannelGroup"],  # Proxy for user segments
        ["sessions", "totalUsers", "engagedSessions", "engagementRate"],
        days=days, limit=10, order="sessions"
    )
    
    # Device segments
    devices = ga.query(
        ["deviceCategory"],
        ["sessions", "totalUsers", "engagedSessions", "engagementRate",
         "bounceRate", "averageSessionDuration"],
        days=days, limit=5, order="sessions"
    )
    
    # Calculate segment quality
    for seg in new_ret:
        if "_error" not in seg:
            eng = safe_float(seg.get("engagementRate", 0))
            pps = safe_float(seg.get("screenPageViewsPerSession", 0))
            dur = safe_float(seg.get("averageSessionDuration", 0))
            seg["quality"] = eng * 0.4 + min(pps/5, 1) * 0.3 + min(dur/300, 1) * 0.3
    
    return {
        "new_vs_returning": new_ret,
        "by_channel": session_count,
        "by_device": devices
    }


def analyze_time_patterns(ga: GA4, days: int) -> Dict:
    """Time patterns - when do users engage."""
    
    # Hourly
    hourly = ga.query(
        ["hour"],
        ["sessions", "totalUsers", "engagementRate"],
        days=days, limit=24
    )
    hourly = sorted([h for h in hourly if "_error" not in h], 
                   key=lambda x: int(x.get("hour", 0)))
    
    # Daily
    daily_dow = ga.query(
        ["dayOfWeek"],
        ["sessions", "totalUsers", "engagementRate", "averageSessionDuration"],
        days=days, limit=7
    )
    daily_dow = sorted([d for d in daily_dow if "_error" not in d],
                      key=lambda x: int(x.get("dayOfWeek", 0)))
    
    # Trend over period
    trend = ga.query(
        ["date"],
        ["sessions", "totalUsers", "newUsers", "engagedSessions", "screenPageViews"],
        days=days, limit=days+1
    )
    trend = sorted([t for t in trend if "_error" not in t], key=lambda x: x.get("date", ""))
    
    # Calculate 7-day rolling average
    if len(trend) >= 7:
        for i in range(6, len(trend)):
            window = trend[i-6:i+1]
            avg = sum(safe_int(t["sessions"]) for t in window) / 7
            trend[i]["rolling_avg"] = avg
    
    return {
        "hourly": hourly,
        "daily": daily_dow,
        "trend": trend
    }


def analyze_technology(ga: GA4, days: int) -> Dict:
    """Technology breakdown."""
    
    # Devices
    devices = ga.query(
        ["deviceCategory"],
        ["sessions", "totalUsers", "engagementRate", "bounceRate"],
        days=days, limit=5, order="sessions"
    )
    
    # Browsers
    browsers = ga.query(
        ["browser"],
        ["sessions", "totalUsers", "engagementRate", "bounceRate"],
        days=days, limit=12, order="sessions"
    )
    
    # OS
    os_data = ga.query(
        ["operatingSystem"],
        ["sessions", "totalUsers", "engagementRate"],
        days=days, limit=10, order="sessions"
    )
    
    # Screen resolutions
    screens = ga.query(
        ["screenResolution"],
        ["sessions", "totalUsers"],
        days=days, limit=15, order="sessions"
    )
    
    return {
        "devices": devices,
        "browsers": browsers,
        "os": os_data,
        "screens": screens
    }


def calculate_health_scores(data: Dict, days: int) -> Dict:
    """Calculate comprehensive health scores."""
    
    scores = {}
    exec_data = data.get("executive", {})
    current = exec_data.get("current", {})
    previous = exec_data.get("previous", {})
    activity = exec_data.get("activity", {})
    
    # 1. ENGAGEMENT (0-100)
    eng_rate = safe_float(current.get("engagementRate", 0))
    duration = safe_float(current.get("averageSessionDuration", 0))
    pps = safe_float(current.get("screenPageViewsPerSession", 0))
    scores["engagement"] = min(100, int(eng_rate * 50 + min(duration/180, 1) * 25 + min(pps/4, 1) * 25))
    
    # 2. TRAFFIC DIVERSITY (0-100)
    channels = data.get("acquisition", {}).get("channels", [])
    if channels:
        total = sum(safe_int(c.get("sessions", 0)) for c in channels if "_error" not in c)
        top = safe_int(channels[0].get("sessions", 0)) if channels else 0
        scores["traffic_diversity"] = int((1 - top/total) * 100) if total > 0 else 50
    else:
        scores["traffic_diversity"] = 50
    
    # 3. RETENTION (0-100)
    dau = safe_int(activity.get("active1DayUsers", 0))
    wau = safe_int(activity.get("active7DayUsers", 0))
    mau = safe_int(activity.get("active28DayUsers", 0))
    dau_mau = dau / mau if mau > 0 else 0
    scores["retention"] = min(100, int(dau_mau * 500))  # 20% = 100
    
    # 4. GROWTH (0-100)
    curr_sess = safe_int(current.get("sessions", 0))
    prev_sess = safe_int(previous.get("sessions", 0))
    if prev_sess > 0:
        growth = (curr_sess - prev_sess) / prev_sess
        scores["growth"] = min(100, max(0, int(50 + growth * 100)))
    else:
        scores["growth"] = 75 if curr_sess > 0 else 50
    
    # 5. CONTENT QUALITY (0-100)
    high_bounce = data.get("content", {}).get("high_bounce", [])
    total_pages = len(data.get("content", {}).get("pages", []))
    bounce_ratio = len(high_bounce) / max(total_pages, 1)
    scores["content"] = max(0, int(100 - bounce_ratio * 300))
    
    # 6. MOBILE (0-100)
    devices = data.get("technology", {}).get("devices", [])
    if devices:
        total = sum(safe_int(d.get("sessions", 0)) for d in devices if "_error" not in d)
        mobile = sum(safe_int(d.get("sessions", 0)) for d in devices 
                    if "_error" not in d and d.get("deviceCategory") in ["mobile", "tablet"])
        mobile_pct = mobile / total if total > 0 else 0
        # Ideal is 30-60%
        if 0.3 <= mobile_pct <= 0.6:
            scores["mobile"] = 95
        elif mobile_pct > 0.15:
            scores["mobile"] = 75
        else:
            scores["mobile"] = 45
    else:
        scores["mobile"] = 50
    
    # 7. GEO DIVERSITY (0-100)
    countries = data.get("geography", {}).get("countries", [])
    if countries:
        total = sum(safe_int(c.get("sessions", 0)) for c in countries if "_error" not in c)
        top_country = safe_int(countries[0].get("sessions", 0)) if countries else 0
        scores["geo_diversity"] = int((1 - top_country/total) * 100) if total > 0 else 50
    else:
        scores["geo_diversity"] = 50
    
    return scores


# ============================================================================
# OUTPUT
# ============================================================================

def print_report(data: Dict, property_name: str, days: int):
    """Print comprehensive report."""
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    
    print(f"""
╔══════════════════════════════════════════════════════════════════════════════════╗
║                                                                                  ║
║   🏴‍☠️  GA4 DEEP DIVE v3 — THE OWNER'S WAR ROOM                                    ║
║                                                                                  ║
║   Property: {property_name.upper():<15}     Period: Last {days} days                          ║
║   Generated: {now:<63}║
║                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════╝
""")

    # ===== REAL-TIME =====
    rt = data.get("realtime", 0)
    print(f"   🟢 LIVE NOW: {rt} active user{'s' if rt != 1 else ''}")
    
    # ===== EXECUTIVE SUMMARY =====
    section("EXECUTIVE SUMMARY", "📊")
    
    exec_data = data.get("executive", {})
    curr = exec_data.get("current", {})
    prev = exec_data.get("previous", {})
    activity = exec_data.get("activity", {})
    
    # Key metrics table
    metrics = [
        ("Sessions", "sessions", False),
        ("Users", "totalUsers", False),
        ("New Users", "newUsers", False),
        ("Engaged Sessions", "engagedSessions", False),
        ("Engagement Rate", "engagementRate", False),
        ("Bounce Rate", "bounceRate", True),  # reverse=True (down is good)
        ("Avg Duration (s)", "averageSessionDuration", False),
        ("Pages/Session", "screenPageViewsPerSession", False),
        ("Page Views", "screenPageViews", False),
    ]
    
    print(f"\n   {'Metric':<22} {'Current':>12} {'Previous':>12} {'Change':>12}")
    print(f"   {'─'*60}")
    
    for label, key, reverse in metrics:
        c_val = safe_float(curr.get(key, 0))
        p_val = safe_float(prev.get(key, 0))
        
        if "Rate" in label:
            c_str = pct(c_val)
            p_str = pct(p_val) if p_val else "—"
        elif "Duration" in label:
            c_str = f"{c_val:.0f}s"
            p_str = f"{p_val:.0f}s" if p_val else "—"
        elif "Pages" in label and "Views" not in label:
            c_str = f"{c_val:.2f}"
            p_str = f"{p_val:.2f}" if p_val else "—"
        else:
            c_str = fmt_num(c_val)
            p_str = fmt_num(p_val) if p_val else "—"
        
        change = delta_str(c_val, p_val, reverse)
        print(f"   {label:<22} {c_str:>12} {p_str:>12} {change:>12}")
    
    # Activity metrics
    dau = safe_int(activity.get("active1DayUsers", 0))
    wau = safe_int(activity.get("active7DayUsers", 0))
    mau = safe_int(activity.get("active28DayUsers", 0))
    
    print(f"\n   📈 User Activity:")
    print(f"      DAU: {dau:,}  |  WAU: {wau:,}  |  MAU: {mau:,}")
    print(f"      Stickiness: DAU/WAU={dau/wau*100:.1f}%  DAU/MAU={dau/mau*100:.1f}%" if wau and mau else "")
    
    # ===== HEALTH SCORES =====
    section("HEALTH DASHBOARD", "🏥")
    
    scores = data.get("scores", {})
    
    def grade_emoji(s):
        if s >= 80: return "✅"
        elif s >= 60: return "⚠️"
        else: return "🔴"
    
    print()
    for name, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        label = name.replace("_", " ").title()
        print(f"   {grade_emoji(score)} {label:<20} {bar(score, 100, 25)} {score:>3}/100")
    
    overall = int(sum(scores.values()) / len(scores)) if scores else 0
    grade = "A+" if overall >= 90 else "A" if overall >= 80 else "B" if overall >= 65 else "C" if overall >= 50 else "D"
    print(f"\n   {'═'*50}")
    print(f"   🎯 OVERALL SCORE: {overall}/100 (Grade {grade})")
    
    # ===== ACQUISITION DEEP DIVE =====
    section("ACQUISITION — WHERE DO USERS COME FROM?", "🚦")
    
    acq = data.get("acquisition", {})
    channels = acq.get("channels", [])
    
    if channels:
        total = sum(safe_int(c.get("sessions", 0)) for c in channels if "_error" not in c)
        
        subsection("Channel Performance")
        print(f"\n   {'Channel':<18} {'Sessions':>8} {'Share':>7} {'Engaged':>8} {'Bounce':>8} {'Dur':>6}")
        print(f"   {'─'*65}")
        
        for c in channels[:8]:
            if "_error" in c: continue
            sess = safe_int(c.get("sessions", 0))
            share = sess / total * 100 if total else 0
            engaged = safe_int(c.get("engagedSessions", 0))
            eng_pct = engaged / sess * 100 if sess else 0
            bounce = safe_float(c.get("bounceRate", 0)) * 100
            dur = safe_float(c.get("averageSessionDuration", 0))
            
            print(f"   {c.get('sessionDefaultChannelGroup', '?')[:17]:<18} {sess:>8,} {share:>6.1f}% {eng_pct:>7.1f}% {bounce:>7.1f}% {dur:>5.0f}s")
    
    # Top referrers
    referrers = acq.get("referrers", [])
    if referrers:
        subsection("Top Referrers (actual URLs)")
        for r in referrers[:8]:
            if "_error" in r: continue
            url = r.get("pageReferrer", "")
            if url and url != "(not set)" and not url.startswith("https://solvr.dev"):
                print(f"   {url[:65]:<66} {safe_int(r.get('sessions', 0)):>5}")
    
    # First touch attribution
    first = acq.get("first_touch", [])
    if first:
        subsection("First-Touch Attribution (how users FOUND you)")
        print(f"\n   {'Source':<20} {'Medium':<12} {'Users':>8} {'Engaged':>8}")
        print(f"   {'─'*55}")
        for f in first[:8]:
            if "_error" in f: continue
            print(f"   {f.get('firstUserSource', '?')[:19]:<20} {f.get('firstUserMedium', '?')[:11]:<12} {safe_int(f.get('totalUsers', 0)):>8} {pct(f.get('engagementRate', 0)):>8}")
    
    # ===== GEOGRAPHY =====
    section("GEOGRAPHY — WHERE ARE YOUR USERS?", "🌍")
    
    geo = data.get("geography", {})
    countries = geo.get("countries", [])
    
    if countries:
        total = sum(safe_int(c.get("sessions", 0)) for c in countries if "_error" not in c)
        
        subsection("Country Performance (sorted by quality)")
        print(f"\n   {'Country':<20} {'Sessions':>8} {'Share':>7} {'Engaged':>8} {'Quality':>8}")
        print(f"   {'─'*60}")
        
        # Sort by quality score
        ranked = sorted([c for c in countries if "_error" not in c], 
                       key=lambda x: x.get("quality_score", 0), reverse=True)
        
        for c in ranked[:12]:
            sess = safe_int(c.get("sessions", 0))
            share = sess / total * 100 if total else 0
            engaged = pct(c.get("engagementRate", 0))
            quality = c.get("quality_score", 0)
            quality_bar = "★" * min(int(quality / 2), 5)
            
            print(f"   {c.get('country', '?')[:19]:<20} {sess:>8,} {share:>6.1f}% {engaged:>8} {quality_bar:<8}")
    
    # Languages
    languages = geo.get("languages", [])
    if languages:
        subsection("Languages")
        lang_total = sum(safe_int(l.get("totalUsers", 0)) for l in languages if "_error" not in l)
        for l in languages[:8]:
            if "_error" in l: continue
            users = safe_int(l.get("totalUsers", 0))
            share = users / lang_total * 100 if lang_total else 0
            print(f"   {l.get('language', '?')[:25]:<26} {users:>6} users ({share:.1f}%)")
    
    # ===== CONTENT =====
    section("CONTENT — WHAT'S WORKING?", "📄")
    
    content = data.get("content", {})
    
    # Content groups (Solvr)
    groups = content.get("content_groups", {})
    if groups:
        subsection("Solvr Content Groups")
        print(f"\n   {'Section':<15} {'Views':>8} {'Users':>7} {'Engagement':>10} {'Pages':>6}")
        print(f"   {'─'*55}")
        
        for name, stats in sorted(groups.items(), key=lambda x: x[1].get("views", 0), reverse=True):
            print(f"   {name:<15} {stats.get('views', 0):>8,} {stats.get('users', 0):>7,} {stats.get('avg_engagement', 0)*100:>9.1f}% {stats.get('pages', 0):>6}")
    
    # Trending pages
    trending = content.get("trending", [])
    if trending:
        subsection("🔥 Trending Up (this week vs last)")
        for p in trending[:5]:
            if p.get("trend", 0) > 0:
                print(f"   {p.get('pagePath', '?')[:45]:<46} +{p.get('trend', 0):.0f}%")
    
    # Declining pages
    declining = content.get("declining", [])
    if declining:
        subsection("📉 Declining")
        for p in declining[:5]:
            if p.get("trend", 0) < 0:
                print(f"   {p.get('pagePath', '?')[:45]:<46} {p.get('trend', 0):.0f}%")
    
    # Problem pages
    high_bounce = content.get("high_bounce", [])
    if high_bounce:
        subsection("🚨 Problem Pages (high bounce)")
        print(f"\n   {'Page':<45} {'Views':>7} {'Bounce':>8}")
        print(f"   {'─'*65}")
        for p in high_bounce[:8]:
            print(f"   {p.get('pagePath', '?')[:44]:<45} {safe_int(p.get('screenPageViews', 0)):>7} {pct(p.get('bounceRate', 0)):>8}")
    
    # ===== USER SEGMENTS =====
    section("USER SEGMENTS — WHO ARE YOUR USERS?", "👤")
    
    segments = data.get("segments", {})
    
    # New vs returning
    nvr = segments.get("new_vs_returning", [])
    if nvr:
        subsection("New vs Returning")
        print(f"\n   {'Segment':<15} {'Sessions':>10} {'Users':>8} {'Engaged':>10} {'Quality':>8}")
        print(f"   {'─'*60}")
        
        for s in nvr:
            if "_error" in s: continue
            name = s.get("newVsReturning", "?")
            if not name: continue
            quality = s.get("quality", 0) * 100
            print(f"   {name:<15} {safe_int(s.get('sessions', 0)):>10,} {safe_int(s.get('totalUsers', 0)):>8,} {pct(s.get('engagementRate', 0)):>10} {quality:>7.0f}%")
    
    # By device
    devices = segments.get("by_device", [])
    if devices:
        subsection("By Device")
        total_dev = sum(safe_int(d.get("sessions", 0)) for d in devices if "_error" not in d)
        for d in devices:
            if "_error" in d: continue
            sess = safe_int(d.get("sessions", 0))
            share = sess / total_dev * 100 if total_dev else 0
            device_bar = bar(share, 100, 15)
            print(f"   {d.get('deviceCategory', '?'):<10} {device_bar} {share:>5.1f}% ({sess:,} sessions)")
    
    # ===== EVENTS =====
    section("EVENTS — WHAT DO USERS DO?", "⚡")
    
    events_data = data.get("events", {})
    events = events_data.get("events", [])
    
    if events:
        # Get total users from activity data (more reliable)
        total_users = safe_int(activity.get("active28DayUsers", 0)) or 1
        
        print(f"\n   {'Event':<30} {'Count':>10} {'Users':>8} {'% Users':>8} {'Per User':>10}")
        print(f"   {'─'*75}")
        
        for e in events[:15]:
            if "_error" in e: continue
            count = safe_int(e.get("eventCount", 0))
            users = safe_int(e.get("totalUsers", 0))
            user_pct = min(users / total_users * 100, 100) if total_users else 0
            per_user = safe_float(e.get("eventCountPerUser", 0))
            
            print(f"   {e.get('eventName', '?')[:29]:<30} {count:>10,} {users:>8,} {user_pct:>7.1f}% {per_user:>10.2f}")
    
    # Custom events highlight
    custom = events_data.get("custom_events", [])
    if custom:
        subsection("Custom Events (your tracking)")
        for e in custom[:5]:
            print(f"   {e.get('eventName', '?'):<30} {safe_int(e.get('eventCount', 0)):>10,} ({safe_int(e.get('totalUsers', 0))} users)")
    
    # ===== TIME PATTERNS =====
    section("TIME PATTERNS — WHEN DO USERS ENGAGE?", "🕐")
    
    time_data = data.get("time", {})
    
    # Hourly heatmap
    hourly = time_data.get("hourly", [])
    if hourly:
        subsection("Hour of Day (UTC)")
        max_sess = max(safe_int(h.get("sessions", 0)) for h in hourly) or 1
        
        # Morning, afternoon, evening, night
        print("\n   Morning (6-12):  ", end="")
        for h in hourly:
            hr = int(h.get("hour", 0))
            if 6 <= hr < 12:
                intensity = safe_int(h.get("sessions", 0)) / max_sess
                char = "░▒▓█"[min(int(intensity * 4), 3)]
                print(char, end="")
        
        print("\n   Afternoon (12-18):", end="")
        for h in hourly:
            hr = int(h.get("hour", 0))
            if 12 <= hr < 18:
                intensity = safe_int(h.get("sessions", 0)) / max_sess
                char = "░▒▓█"[min(int(intensity * 4), 3)]
                print(char, end="")
        
        print("\n   Evening (18-24): ", end="")
        for h in hourly:
            hr = int(h.get("hour", 0))
            if 18 <= hr < 24:
                intensity = safe_int(h.get("sessions", 0)) / max_sess
                char = "░▒▓█"[min(int(intensity * 4), 3)]
                print(char, end="")
        
        print("\n   Night (0-6):     ", end="")
        for h in hourly:
            hr = int(h.get("hour", 0))
            if 0 <= hr < 6:
                intensity = safe_int(h.get("sessions", 0)) / max_sess
                char = "░▒▓█"[min(int(intensity * 4), 3)]
                print(char, end="")
        print()
    
    # Day of week
    daily = time_data.get("daily", [])
    if daily:
        subsection("Day of Week")
        days_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        max_d = max(safe_int(d.get("sessions", 0)) for d in daily) or 1
        
        for d in daily:
            dow = int(d.get("dayOfWeek", 0))
            sess = safe_int(d.get("sessions", 0))
            day_bar = bar(sess, max_d, 15)
            print(f"   {days_names[dow]:<4} {day_bar} {sess:>5} sessions ({pct(d.get('engagementRate', 0))} engaged)")
    
    # Trend sparkline
    trend = time_data.get("trend", [])
    if trend:
        subsection(f"Daily Trend (last {len(trend)} days)")
        sessions = [safe_int(t.get("sessions", 0)) for t in trend]
        spark = sparkline(sessions)
        print(f"\n   {spark}")
        print(f"   Min: {min(sessions)}  Max: {max(sessions)}  Avg: {sum(sessions)//len(sessions)}")
        
        # Last 7 days detail
        print(f"\n   Last 7 days:")
        for t in trend[-7:]:
            date = t.get("date", "")
            date_fmt = f"{date[4:6]}/{date[6:]}" if len(date) == 8 else date
            sess = safe_int(t.get("sessions", 0))
            users = safe_int(t.get("totalUsers", 0))
            rolling = t.get("rolling_avg")
            rolling_str = f"(7d avg: {rolling:.0f})" if rolling else ""
            print(f"      {date_fmt}: {sess:>4} sessions, {users:>4} users {rolling_str}")
    
    # ===== TECHNOLOGY =====
    section("TECHNOLOGY", "💻")
    
    tech = data.get("technology", {})
    
    # Browsers
    browsers = tech.get("browsers", [])
    if browsers:
        subsection("Browsers")
        for b in browsers[:8]:
            if "_error" in b: continue
            sess = safe_int(b.get("sessions", 0))
            eng = pct(b.get("engagementRate", 0))
            bounce = pct(b.get("bounceRate", 0))
            print(f"   {b.get('browser', '?')[:15]:<16} {sess:>6} sessions | {eng} engaged | {bounce} bounce")
    
    # Screen resolutions
    screens = tech.get("screens", [])
    if screens:
        subsection("Screen Resolutions (design targets)")
        for s in screens[:8]:
            if "_error" in s: continue
            print(f"   {s.get('screenResolution', '?'):<15} {safe_int(s.get('sessions', 0)):>6} sessions")
    
    # ===== ACTIONABLE INSIGHTS =====
    section("ACTIONABLE INSIGHTS — WHAT TO DO NEXT", "💡")
    
    insights = []
    
    # Traffic diversity
    if scores.get("traffic_diversity", 100) < 50 and channels:
        top = channels[0]
        top_pct = safe_int(top.get("sessions", 0)) / total * 100 if total else 0
        insights.append(f"🔴 {top_pct:.0f}% traffic from {top.get('sessionDefaultChannelGroup')} — DIVERSIFY NOW")
        insights.append(f"   → Try: SEO content, social posting, email newsletter, partnerships")
    
    # Retention
    if scores.get("retention", 100) < 50:
        dau_mau_pct = dau / mau * 100 if mau > 0 else 0
        insights.append(f"🔴 Low retention (DAU/MAU={dau_mau_pct:.1f}%) — users aren't returning")
        insights.append(f"   → Try: Email re-engagement, push notifications, feature announcements")
    
    # High bounce pages
    if high_bounce:
        worst = high_bounce[0]
        insights.append(f"🚨 Fix {worst.get('pagePath')} — {pct(worst.get('bounceRate'))} bounce rate")
        insights.append(f"   → Check: page load speed, content relevance, mobile experience")
    
    # Growth
    if scores.get("growth", 50) > 70:
        insights.append(f"🟢 Strong growth! Double down on what's working")
    elif scores.get("growth", 50) < 40:
        insights.append(f"🔴 Traffic declining — investigate cause ASAP")
    
    # Mobile
    if scores.get("mobile", 100) < 50:
        insights.append(f"⚠️ Low mobile traffic — check mobile UX")
    
    # Geographic opportunity
    if countries:
        high_quality = [c for c in countries if "_error" not in c and c.get("quality_score", 0) > 2]
        if high_quality:
            best = max(high_quality, key=lambda x: x.get("quality_score", 0))
            insights.append(f"🟢 {best.get('country')} has highest quality traffic — consider localization")
    
    # No campaigns
    first = acq.get("first_touch", [])
    has_campaigns = any(f.get("firstUserCampaignName") not in [None, "(not set)", "(organic)", "(direct)"] 
                       for f in first if "_error" not in f)
    if not has_campaigns:
        insights.append(f"📢 No tracked campaigns — add UTM parameters to links")
    
    print()
    if insights:
        for insight in insights:
            print(f"   {insight}")
    else:
        print("   ✅ Looking good! No critical issues detected.")
    
    # ===== FOOTER =====
    print(f"\n{'═'*80}")
    print(f"   ✅ DEEP DIVE v3 COMPLETE")
    print(f"{'═'*80}\n")


def save_snapshot(data: Dict, property_name: str, days: int):
    """Save snapshot for historical tracking."""
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    
    filename = f"{property_name}_{datetime.now().strftime('%Y-%m-%d_%H%M')}.json"
    filepath = SNAPSHOTS_DIR / filename
    
    # Slim down for storage
    snapshot = {
        "property": property_name,
        "generated": datetime.now().isoformat(),
        "days": days,
        "scores": data.get("scores", {}),
        "executive": data.get("executive", {}),
        "top_channels": data.get("acquisition", {}).get("channels", [])[:5],
        "top_countries": data.get("geography", {}).get("countries", [])[:10],
        "content_groups": data.get("content", {}).get("content_groups", {}),
    }
    
    with open(filepath, "w") as f:
        json.dump(snapshot, f, indent=2, default=str)
    
    print(f"   💾 Snapshot: {filepath}")


# ============================================================================
# MAIN
# ============================================================================

def deep_dive(property_name: str, days: int = 30, output: str = "text"):
    """Run complete deep dive analysis."""
    
    property_id = PROPERTIES.get(property_name.lower(), property_name)
    is_solvr = property_name.lower() == "solvr"
    
    print(f"\n🔄 Analyzing {property_name}...")
    
    ga = GA4(property_id)
    
    # Collect all data
    data = {
        "realtime": ga.realtime(),
        "executive": analyze_executive(ga, days),
        "acquisition": analyze_acquisition_deep(ga, days),
        "geography": analyze_geography_deep(ga, days),
        "content": analyze_content_deep(ga, days, is_solvr=is_solvr),
        "events": analyze_events_deep(ga, days),
        "segments": analyze_user_segments(ga, days),
        "time": analyze_time_patterns(ga, days),
        "technology": analyze_technology(ga, days),
    }
    
    # Calculate scores
    data["scores"] = calculate_health_scores(data, days)
    
    # Output
    if output == "json":
        print(json.dumps(data, indent=2, default=str))
    else:
        print_report(data, property_name, days)
        save_snapshot(data, property_name, days)
    
    return data


def main():
    parser = argparse.ArgumentParser(description="GA4 Deep Dive v3 — Owner's War Room")
    parser.add_argument("property", nargs="?", help="Property name or ID")
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--output", choices=["text", "json"], default="text")
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
    
    deep_dive(args.property, args.days, args.output)


if __name__ == "__main__":
    main()
