#!/usr/bin/env python3
"""
GA4 DEEP DIVE v2 — OWNER'S DASHBOARD
Built for Solvr by Claudius 🏴‍☠️

What an owner needs to know:
1. Am I growing? (WoW, MoM comparisons)
2. Who's using my product? (user profiles)
3. What's working? (content performance)
4. What's broken? (drop-offs, bounces)
5. Where's traffic coming from? (acquisition)
6. Are users coming back? (retention)
7. What should I fix? (actionable insights)

Usage:
    python3 deep_dive_v2.py solvr
    python3 deep_dive_v2.py solvr --days 30
    python3 deep_dive_v2.py solvr --compare  # Compare with last snapshot
    python3 deep_dive_v2.py --list
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import hashlib

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange, Dimension, Metric, RunReportRequest,
    RunRealtimeReportRequest, OrderBy, Filter, FilterExpression,
    FilterExpressionList
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

# Solvr-specific content groups
SOLVR_CONTENT_GROUPS = {
    'agents': ['/agents', '/agents/'],
    'problems': ['/problems', '/problem/'],
    'ideas': ['/ideas', '/idea/'],
    'questions': ['/questions', '/question/'],
    'feed': ['/feed'],
    'auth': ['/login', '/join', '/auth/'],
    'settings': ['/settings'],
    'api': ['/api-docs', '/api'],
    'home': ['/'],
}

# ============================================================================
# UTILITIES
# ============================================================================

def safe_int(val) -> int:
    try:
        return int(float(val))
    except:
        return 0

def safe_float(val) -> float:
    try:
        return float(val)
    except:
        return 0.0

def pct(val) -> str:
    """Format as percentage."""
    return f"{safe_float(val)*100:.1f}%"

def dur(seconds) -> str:
    """Format duration nicely."""
    s = safe_float(seconds)
    if s < 60:
        return f"{s:.0f}s"
    elif s < 3600:
        return f"{s/60:.1f}m"
    else:
        return f"{s/3600:.1f}h"

def delta(current, previous) -> str:
    """Format change with arrow."""
    if previous == 0:
        return "—"
    change = ((current - previous) / previous) * 100
    if change > 0:
        return f"↑{change:.1f}%"
    elif change < 0:
        return f"↓{abs(change):.1f}%"
    return "→0%"

def score_bar(score: int, width: int = 20) -> str:
    filled = int(score / 100 * width)
    return '█' * filled + '░' * (width - filled)

def section(title: str):
    """Print section header."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print('='*80)

def subsection(title: str):
    print(f"\n  ── {title} ──")

# ============================================================================
# AUTH
# ============================================================================

def get_credentials() -> Credentials:
    """Get or refresh OAuth credentials."""
    from google.auth.transport.requests import Request
    
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    creds = None
    
    if TOKEN_PATH.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
        except Exception as e:
            print(f"⚠️ Token load error: {e}")
            creds = None
    
    if creds and not creds.valid:
        if creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                TOKEN_PATH.write_text(creds.to_json())
            except Exception as e:
                print(f"⚠️ Token refresh failed: {e}")
                creds = None
    
    if not creds or not creds.valid:
        if not CREDENTIALS_PATH.exists():
            print(f"❌ Need credentials.json at: {CREDENTIALS_PATH}")
            sys.exit(1)
        flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
        creds = flow.run_local_server(port=0)
        TOKEN_PATH.write_text(creds.to_json())
    
    return creds

# ============================================================================
# GA4 API WRAPPER
# ============================================================================

class GA4Client:
    """Wrapper for GA4 API with conveniences."""
    
    def __init__(self, property_id: str):
        self.property_id = property_id
        self.client = BetaAnalyticsDataClient(credentials=get_credentials())
        self.property = f"properties/{property_id}"
    
    def report(self, dimensions: List[str], metrics: List[str], 
               days: int = 30, start_date: str = None, end_date: str = None,
               limit: int = 100, order_by: str = None, desc: bool = True,
               dim_filter: FilterExpression = None) -> List[Dict]:
        """Run a report and return list of dicts."""
        
        if start_date and end_date:
            date_range = DateRange(start_date=start_date, end_date=end_date)
        else:
            date_range = DateRange(start_date=f"{days}daysAgo", end_date="today")
        
        request = RunReportRequest(
            property=self.property,
            date_ranges=[date_range],
            dimensions=[Dimension(name=d) for d in dimensions] if dimensions else [],
            metrics=[Metric(name=m) for m in metrics],
            limit=limit
        )
        
        if order_by:
            request.order_bys = [OrderBy(metric=OrderBy.MetricOrderBy(metric_name=order_by), desc=desc)]
        if dim_filter:
            request.dimension_filter = dim_filter
        
        try:
            response = self.client.run_report(request)
            results = []
            for row in response.rows:
                r = {}
                for i, d in enumerate(dimensions):
                    r[d] = row.dimension_values[i].value
                for i, m in enumerate(metrics):
                    r[m] = row.metric_values[i].value
                results.append(r)
            return results
        except Exception as e:
            return [{"_error": str(e)}]
    
    def realtime(self) -> int:
        """Get realtime active users."""
        try:
            req = RunRealtimeReportRequest(
                property=self.property,
                metrics=[Metric(name="activeUsers")]
            )
            resp = self.client.run_realtime_report(req)
            return int(resp.rows[0].metric_values[0].value) if resp.rows else 0
        except:
            return 0
    
    def metrics_only(self, metrics: List[str], days: int = 30) -> Dict:
        """Get just metrics, no dimensions."""
        results = self.report([], metrics, days=days, limit=1)
        return results[0] if results else {}

# ============================================================================
# ANALYSIS MODULES
# ============================================================================

@dataclass
class Snapshot:
    """Complete analytics snapshot for storage/comparison."""
    property_id: str
    property_name: str
    generated_at: str
    period_days: int
    
    # Core metrics
    sessions: int = 0
    users: int = 0
    new_users: int = 0
    engagement_rate: float = 0.0
    bounce_rate: float = 0.0
    avg_duration: float = 0.0
    pages_per_session: float = 0.0
    page_views: int = 0
    events: int = 0
    
    # Activity metrics
    dau: int = 0
    wau: int = 0
    mau: int = 0
    
    # Traffic sources (top 5)
    top_channels: List[Dict] = None
    top_sources: List[Dict] = None
    
    # Content performance
    top_pages: List[Dict] = None
    top_landing: List[Dict] = None
    high_bounce_pages: List[Dict] = None
    
    # Geography
    top_countries: List[Dict] = None
    
    # Technology
    device_split: Dict = None
    browser_split: Dict = None
    
    # Solvr-specific
    content_groups: Dict = None
    
    # Health scores
    scores: Dict = None
    overall_score: int = 0
    
    def to_dict(self) -> Dict:
        return asdict(self)


def analyze_core_metrics(ga: GA4Client, days: int) -> Dict:
    """Core metrics with period comparison."""
    
    # Current period
    current = ga.metrics_only([
        "sessions", "totalUsers", "newUsers", "activeUsers",
        "engagedSessions", "engagementRate", "bounceRate",
        "averageSessionDuration", "screenPageViews", "eventCount"
    ], days=days)
    
    current2 = ga.metrics_only([
        "sessionsPerUser", "screenPageViewsPerSession", "eventsPerSession",
        "userEngagementDuration"
    ], days=days)
    
    # Previous period (for comparison) - use explicit dates
    today = datetime.now()
    end_prev = (today - timedelta(days=days+1)).strftime("%Y-%m-%d")
    start_prev = (today - timedelta(days=days*2)).strftime("%Y-%m-%d")
    
    previous = ga.report([], [
        "sessions", "totalUsers", "newUsers", "engagementRate", 
        "bounceRate", "averageSessionDuration", "screenPageViews"
    ], start_date=start_prev, end_date=end_prev, limit=1)
    prev = previous[0] if previous and '_error' not in previous[0] else {}
    
    return {
        'current': {**current, **current2},
        'previous': prev
    }


def analyze_acquisition(ga: GA4Client, days: int) -> Dict:
    """Full acquisition breakdown."""
    
    # Channel groups
    channels = ga.report(
        ["sessionDefaultChannelGroup"],
        ["sessions", "totalUsers", "newUsers", "engagementRate", "bounceRate", "conversions"],
        days=days, limit=15, order_by="sessions"
    )
    
    # Source/Medium detail
    sources = ga.report(
        ["sessionSource", "sessionMedium"],
        ["sessions", "totalUsers", "engagementRate", "averageSessionDuration"],
        days=days, limit=25, order_by="sessions"
    )
    
    # Referrers with URLs
    referrers = ga.report(
        ["sessionSource", "pageReferrer"],
        ["sessions", "engagementRate"],
        days=days, limit=30, order_by="sessions"
    )
    
    # First user source (how they first found us)
    first_source = ga.report(
        ["firstUserSource", "firstUserMedium"],
        ["totalUsers", "newUsers", "engagementRate"],
        days=days, limit=15, order_by="totalUsers"
    )
    
    return {
        'channels': channels,
        'sources': sources,
        'referrers': referrers,
        'first_source': first_source
    }


def analyze_content(ga: GA4Client, days: int, is_solvr: bool = False) -> Dict:
    """Content performance analysis."""
    
    # All pages - GA4 valid metrics only
    pages = ga.report(
        ["pagePath", "pageTitle"],
        ["screenPageViews", "totalUsers", "engagementRate", 
         "averageSessionDuration", "bounceRate"],
        days=days, limit=50, order_by="screenPageViews"
    )
    
    # Landing pages
    landing = ga.report(
        ["landingPage"],
        ["sessions", "totalUsers", "bounceRate", "engagementRate",
         "averageSessionDuration", "screenPageViewsPerSession"],
        days=days, limit=30, order_by="sessions"
    )
    
    # Exit pages - Note: GA4 doesn't have exits metric, use sessions instead
    exits = ga.report(
        ["pagePath"],
        ["sessions", "screenPageViews", "bounceRate"],
        days=days, limit=20, order_by="sessions"
    )
    # Use bounce rate as proxy for exit-prone pages
    for e in exits:
        if '_error' not in e:
            e['exitRate'] = safe_float(e.get('bounceRate', 0))
    
    # High bounce pages (problem areas)
    high_bounce = [p for p in pages if '_error' not in p 
                   and safe_float(p.get('bounceRate', 0)) > 0.6
                   and safe_int(p.get('screenPageViews', 0)) > 5]
    high_bounce.sort(key=lambda x: safe_float(x.get('bounceRate', 0)), reverse=True)
    
    result = {
        'pages': pages,
        'landing': landing,
        'exits': exits[:15],
        'high_bounce': high_bounce[:10]
    }
    
    # Solvr-specific content groups
    if is_solvr:
        groups = {}
        for group_name, patterns in SOLVR_CONTENT_GROUPS.items():
            group_pages = [p for p in pages if '_error' not in p 
                          and any(p.get('pagePath', '').startswith(pat) for pat in patterns)]
            if group_pages:
                groups[group_name] = {
                    'pages': len(group_pages),
                    'views': sum(safe_int(p.get('screenPageViews', 0)) for p in group_pages),
                    'users': sum(safe_int(p.get('totalUsers', 0)) for p in group_pages),
                    'avg_engagement': sum(safe_float(p.get('engagementRate', 0)) for p in group_pages) / len(group_pages)
                }
        result['content_groups'] = groups
    
    return result


def analyze_users(ga: GA4Client, days: int) -> Dict:
    """User behavior analysis."""
    
    # New vs returning
    new_vs_ret = ga.report(
        ["newVsReturning"],
        ["sessions", "totalUsers", "engagementRate", "bounceRate",
         "screenPageViewsPerSession", "averageSessionDuration"],
        days=days, limit=5
    )
    
    # User activity metrics
    activity = ga.metrics_only([
        "active1DayUsers", "active7DayUsers", "active28DayUsers",
        "dauPerMau", "dauPerWau", "wauPerMau"
    ], days=days)
    
    # Session engagement
    # Note: engagedSessions is sessions > 10s OR had conversion OR 2+ page views
    engaged = ga.metrics_only([
        "sessions", "engagedSessions", "engagementRate",
        "averageSessionDuration", "screenPageViewsPerSession"
    ], days=days)
    
    # User languages
    languages = ga.report(
        ["language"],
        ["totalUsers", "sessions", "engagementRate"],
        days=days, limit=15, order_by="totalUsers"
    )
    
    return {
        'new_vs_returning': new_vs_ret,
        'activity': activity,
        'engagement': engaged,
        'languages': languages
    }


def analyze_geography(ga: GA4Client, days: int) -> Dict:
    """Geography breakdown."""
    
    countries = ga.report(
        ["country"],
        ["sessions", "totalUsers", "newUsers", "engagementRate", "averageSessionDuration"],
        days=days, limit=20, order_by="sessions"
    )
    
    cities = ga.report(
        ["country", "city", "region"],
        ["sessions", "totalUsers", "engagementRate"],
        days=days, limit=30, order_by="sessions"
    )
    
    return {
        'countries': countries,
        'cities': cities
    }


def analyze_technology(ga: GA4Client, days: int) -> Dict:
    """Technology breakdown."""
    
    # Devices
    devices = ga.report(
        ["deviceCategory"],
        ["sessions", "totalUsers", "engagementRate", "bounceRate"],
        days=days, limit=5, order_by="sessions"
    )
    
    # Browsers
    browsers = ga.report(
        ["browser"],
        ["sessions", "totalUsers", "engagementRate", "bounceRate"],
        days=days, limit=10, order_by="sessions"
    )
    
    # OS
    os_data = ga.report(
        ["operatingSystem"],
        ["sessions", "totalUsers", "engagementRate"],
        days=days, limit=10, order_by="sessions"
    )
    
    # Screen resolutions (useful for design)
    screens = ga.report(
        ["screenResolution", "deviceCategory"],
        ["sessions", "totalUsers"],
        days=days, limit=15, order_by="sessions"
    )
    
    # Mobile models (if significant mobile traffic)
    mobile_models = ga.report(
        ["mobileDeviceModel", "operatingSystem"],
        ["sessions", "totalUsers"],
        days=days, limit=10, order_by="sessions"
    )
    
    return {
        'devices': devices,
        'browsers': browsers,
        'os': os_data,
        'screens': screens,
        'mobile_models': mobile_models
    }


def analyze_time_patterns(ga: GA4Client, days: int) -> Dict:
    """Time-based patterns."""
    
    # Hour of day
    hourly = ga.report(
        ["hour"],
        ["sessions", "totalUsers", "engagementRate"],
        days=days, limit=24
    )
    hourly = sorted([h for h in hourly if '_error' not in h], key=lambda x: int(x['hour']))
    
    # Day of week
    daily = ga.report(
        ["dayOfWeek"],
        ["sessions", "totalUsers", "engagementRate", "averageSessionDuration"],
        days=days, limit=7
    )
    daily = sorted([d for d in daily if '_error' not in d], key=lambda x: int(x['dayOfWeek']))
    
    # Daily trend
    trend = ga.report(
        ["date"],
        ["sessions", "totalUsers", "newUsers", "engagementRate", "screenPageViews"],
        days=days, limit=days+1
    )
    trend = sorted([t for t in trend if '_error' not in t], key=lambda x: x['date'])
    
    return {
        'hourly': hourly,
        'daily': daily,
        'trend': trend
    }


def analyze_events(ga: GA4Client, days: int) -> Dict:
    """Event tracking analysis."""
    
    events = ga.report(
        ["eventName"],
        ["eventCount", "totalUsers", "eventCountPerUser", "eventValue"],
        days=days, limit=30, order_by="eventCount"
    )
    
    # Key events (conversions)
    conversions = ga.report(
        ["eventName"],
        ["conversions", "totalUsers"],
        days=days, limit=20, order_by="conversions"
    )
    conversions = [c for c in conversions if '_error' not in c and safe_int(c.get('conversions', 0)) > 0]
    
    return {
        'events': events,
        'conversions': conversions
    }


def calculate_health_scores(data: Dict) -> Dict:
    """Calculate health scores based on all data."""
    
    scores = {}
    
    # 1. Engagement Score (0-100)
    core = data.get('core', {}).get('current', {})
    eng_rate = safe_float(core.get('engagementRate', 0))
    duration = safe_float(core.get('averageSessionDuration', 0))
    pps = safe_float(core.get('screenPageViewsPerSession', 0))
    
    # Engagement: 40% rate + 30% duration (target 3min) + 30% pages (target 4)
    eng_score = eng_rate * 40 + min(duration/180, 1) * 30 + min(pps/4, 1) * 30
    scores['engagement'] = int(min(100, eng_score))
    
    # 2. Traffic Diversity (0-100)
    channels = data.get('acquisition', {}).get('channels', [])
    if channels:
        total = sum(safe_int(c.get('sessions', 0)) for c in channels if '_error' not in c)
        top = safe_int(channels[0].get('sessions', 0)) if channels else 0
        diversity = 1 - (top / total) if total > 0 else 0
        scores['traffic_diversity'] = int(diversity * 100)
    else:
        scores['traffic_diversity'] = 50
    
    # 3. Mobile Readiness (0-100)
    devices = data.get('technology', {}).get('devices', [])
    if devices:
        total = sum(safe_int(d.get('sessions', 0)) for d in devices if '_error' not in d)
        mobile = sum(safe_int(d.get('sessions', 0)) for d in devices 
                    if '_error' not in d and d.get('deviceCategory') in ['mobile', 'tablet'])
        mobile_pct = mobile / total if total > 0 else 0
        # Good mobile = 30-60% of traffic
        if 0.3 <= mobile_pct <= 0.6:
            scores['mobile'] = 90
        elif mobile_pct > 0.1:
            scores['mobile'] = 70
        else:
            scores['mobile'] = 40
    else:
        scores['mobile'] = 50
    
    # 4. Content Quality (0-100)
    content = data.get('content', {})
    high_bounce = content.get('high_bounce', [])
    total_pages = len(content.get('pages', []))
    problem_ratio = len(high_bounce) / total_pages if total_pages > 0 else 0
    scores['content'] = int(max(0, 100 - problem_ratio * 200))
    
    # 5. Growth (0-100)
    core_current = data.get('core', {}).get('current', {})
    core_prev = data.get('core', {}).get('previous', {})
    curr_sessions = safe_int(core_current.get('sessions', 0))
    prev_sessions = safe_int(core_prev.get('sessions', 0))
    
    if prev_sessions > 0:
        growth = (curr_sessions - prev_sessions) / prev_sessions
        # +50% = 100, 0% = 50, -50% = 0
        scores['growth'] = int(min(100, max(0, 50 + growth * 100)))
    else:
        scores['growth'] = 75 if curr_sessions > 0 else 50
    
    # 6. Retention (0-100)
    activity = data.get('users', {}).get('activity', {})
    dau = safe_int(activity.get('active1DayUsers', 0))
    mau = safe_int(activity.get('active28DayUsers', 0))
    if mau > 0:
        stickiness = dau / mau
        # 20% stickiness = excellent for most products
        scores['retention'] = int(min(100, stickiness * 500))
    else:
        scores['retention'] = 50
    
    return scores


# ============================================================================
# OUTPUT FORMATTING
# ============================================================================

def print_report(data: Dict, property_name: str, days: int):
    """Print the full report."""
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    
    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  🔍 GA4 DEEP DIVE v2 — OWNER'S DASHBOARD                                     ║
║  Property: {property_name.upper():<20}  Period: Last {days} days                      ║
║  Generated: {now:<62}║
╚══════════════════════════════════════════════════════════════════════════════╝""")
    
    # ===== REALTIME =====
    section("🟢 RIGHT NOW")
    print(f"   Active Users: {data.get('realtime', 0)}")
    
    # ===== EXECUTIVE SUMMARY =====
    section("📊 EXECUTIVE SUMMARY")
    
    core = data.get('core', {})
    current = core.get('current', {})
    previous = core.get('previous', {})
    
    curr_sessions = safe_int(current.get('sessions', 0))
    prev_sessions = safe_int(previous.get('sessions', 0))
    curr_users = safe_int(current.get('totalUsers', 0))
    prev_users = safe_int(previous.get('totalUsers', 0))
    curr_eng = safe_float(current.get('engagementRate', 0))
    prev_eng = safe_float(previous.get('engagementRate', 0))
    
    print(f"""
   ┌─────────────────────┬──────────────┬──────────────┬────────────┐
   │ Metric              │ This Period  │ Last Period  │ Change     │
   ├─────────────────────┼──────────────┼──────────────┼────────────┤
   │ Sessions            │ {curr_sessions:>12,} │ {prev_sessions:>12,} │ {delta(curr_sessions, prev_sessions):>10} │
   │ Users               │ {curr_users:>12,} │ {prev_users:>12,} │ {delta(curr_users, prev_users):>10} │
   │ New Users           │ {safe_int(current.get('newUsers', 0)):>12,} │ {safe_int(previous.get('newUsers', 0)):>12,} │ {delta(safe_int(current.get('newUsers', 0)), safe_int(previous.get('newUsers', 0))):>10} │
   │ Engagement Rate     │ {pct(curr_eng):>12} │ {pct(prev_eng):>12} │ {delta(curr_eng, prev_eng):>10} │
   │ Bounce Rate         │ {pct(current.get('bounceRate', 0)):>12} │ {pct(previous.get('bounceRate', 0)):>12} │ — │
   │ Avg Duration        │ {dur(current.get('averageSessionDuration', 0)):>12} │ {dur(previous.get('averageSessionDuration', 0)):>12} │ — │
   │ Pages/Session       │ {safe_float(current.get('screenPageViewsPerSession', 0)):>12.2f} │ — │ — │
   │ Page Views          │ {safe_int(current.get('screenPageViews', 0)):>12,} │ {safe_int(previous.get('screenPageViews', 0)):>12,} │ {delta(safe_int(current.get('screenPageViews', 0)), safe_int(previous.get('screenPageViews', 0))):>10} │
   └─────────────────────┴──────────────┴──────────────┴────────────┘
""")
    
    # ===== HEALTH SCORES =====
    section("🏥 HEALTH SCORES")
    
    scores = data.get('scores', {})
    
    def grade(s):
        if s >= 80: return '✅'
        elif s >= 60: return '⚠️'
        else: return '❌'
    
    for name, score in scores.items():
        label = name.replace('_', ' ').title()
        print(f"   {grade(score)} {label:<20} {score_bar(score)} {score}/100")
    
    overall = int(sum(scores.values()) / len(scores)) if scores else 0
    letter = 'A' if overall >= 80 else 'B' if overall >= 65 else 'C' if overall >= 50 else 'D'
    print(f"\n   🎯 OVERALL: {overall}/100 (Grade {letter})")
    
    # ===== ACQUISITION =====
    section("🚦 WHERE USERS COME FROM")
    
    acq = data.get('acquisition', {})
    channels = acq.get('channels', [])
    
    if channels:
        total_sessions = sum(safe_int(c.get('sessions', 0)) for c in channels if '_error' not in c)
        print(f"\n   Channel Breakdown (total: {total_sessions:,} sessions)\n")
        print(f"   {'Channel':<20} {'Sessions':>8} {'Share':>8} {'Users':>7} {'Eng%':>7} {'Bnc%':>7}")
        print("   " + "─"*65)
        for c in channels[:10]:
            if '_error' in c: continue
            sess = safe_int(c.get('sessions', 0))
            share = sess / total_sessions * 100 if total_sessions > 0 else 0
            print(f"   {c.get('sessionDefaultChannelGroup', '?')[:19]:<20} {sess:>8,} {share:>7.1f}% {safe_int(c.get('totalUsers', 0)):>7,} {pct(c.get('engagementRate', 0)):>7} {pct(c.get('bounceRate', 0)):>7}")
    
    subsection("Top Referrers")
    referrers = acq.get('referrers', [])
    for r in referrers[:10]:
        if '_error' in r: continue
        ref = r.get('pageReferrer', '')[:50]
        if ref and ref != '(not set)':
            print(f"   {r.get('sessionSource', '?')[:15]:<16} {ref:<50} {safe_int(r.get('sessions', 0)):>5}")
    
    # ===== CONTENT PERFORMANCE =====
    section("📄 CONTENT PERFORMANCE")
    
    content = data.get('content', {})
    
    # Solvr content groups
    groups = content.get('content_groups', {})
    if groups:
        subsection("Content Groups (Solvr-specific)")
        print(f"   {'Group':<15} {'Pages':>6} {'Views':>8} {'Users':>7} {'Avg Eng':>8}")
        print("   " + "─"*50)
        for name, stats in sorted(groups.items(), key=lambda x: x[1].get('views', 0), reverse=True):
            if isinstance(stats, dict):
                print(f"   {name:<15} {stats.get('pages', 0):>6} {stats.get('views', 0):>8,} {stats.get('users', 0):>7,} {stats.get('avg_engagement', 0)*100:>7.1f}%")
    
    subsection("Top Pages")
    pages = content.get('pages', [])
    print(f"   {'Path':<40} {'Views':>7} {'Users':>6} {'Eng%':>6}")
    print("   " + "─"*65)
    for p in pages[:15]:
        if not p or '_error' in p: continue
        path = p.get('pagePath', '?')
        views = safe_int(p.get('screenPageViews', 0))
        users = safe_int(p.get('totalUsers', 0))
        eng = safe_float(p.get('engagementRate', 0))
        print(f"   {path[:39]:<40} {views:>7,} {users:>6,} {eng*100:>5.1f}%")
    
    subsection("🚨 Problem Pages (High Bounce)")
    high_bounce = content.get('high_bounce', [])
    if high_bounce:
        print(f"   {'Path':<45} {'Views':>7} {'Bounce':>8}")
        print("   " + "─"*65)
        for p in high_bounce[:8]:
            print(f"   {p.get('pagePath', '?')[:44]:<45} {safe_int(p.get('screenPageViews', 0)):>7,} {pct(p.get('bounceRate', 0)):>8}")
    else:
        print("   ✅ No high-bounce pages detected!")
    
    # ===== USER BEHAVIOR =====
    section("👤 USER BEHAVIOR")
    
    users = data.get('users', {})
    activity = users.get('activity', {})
    
    dau = safe_int(activity.get('active1DayUsers', 0))
    wau = safe_int(activity.get('active7DayUsers', 0))
    mau = safe_int(activity.get('active28DayUsers', 0))
    
    print(f"""
   Daily Active Users (DAU):   {dau:>8,}
   Weekly Active Users (WAU):  {wau:>8,}
   Monthly Active Users (MAU): {mau:>8,}
   
   DAU/WAU Stickiness: {dau/wau*100 if wau else 0:>6.1f}%  (how often users return weekly)
   DAU/MAU Stickiness: {dau/mau*100 if mau else 0:>6.1f}%  (how often users return monthly)
""")
    
    subsection("New vs Returning")
    nvr = users.get('new_vs_returning', [])
    for r in nvr:
        if '_error' in r: continue
        print(f"   {r.get('newVsReturning', '?'):<12}: {safe_int(r.get('sessions', 0)):>6} sessions, {pct(r.get('engagementRate', 0))} engaged, {pct(r.get('bounceRate', 0))} bounce")
    
    # ===== GEOGRAPHY =====
    section("🌍 GEOGRAPHY")
    
    geo = data.get('geography', {})
    countries = geo.get('countries', [])
    
    if countries:
        total = sum(safe_int(c.get('sessions', 0)) for c in countries if '_error' not in c)
        print(f"   {'Country':<20} {'Sessions':>8} {'Share':>7} {'Users':>7} {'Eng%':>7}")
        print("   " + "─"*55)
        for c in countries[:12]:
            if '_error' in c: continue
            sess = safe_int(c.get('sessions', 0))
            share = sess / total * 100 if total > 0 else 0
            print(f"   {c.get('country', '?')[:19]:<20} {sess:>8,} {share:>6.1f}% {safe_int(c.get('totalUsers', 0)):>7,} {pct(c.get('engagementRate', 0)):>7}")
    
    # ===== TECHNOLOGY =====
    section("💻 TECHNOLOGY")
    
    tech = data.get('technology', {})
    
    subsection("Devices")
    devices = tech.get('devices', [])
    total_dev = sum(safe_int(d.get('sessions', 0)) for d in devices if '_error' not in d)
    for d in devices:
        if '_error' in d: continue
        sess = safe_int(d.get('sessions', 0))
        share = sess / total_dev * 100 if total_dev > 0 else 0
        bar = '█' * int(share / 5)
        print(f"   {d.get('deviceCategory', '?'):<10} {bar:<20} {share:>5.1f}% ({sess:,})")
    
    subsection("Top Browsers")
    browsers = tech.get('browsers', [])
    for b in browsers[:6]:
        if '_error' in b: continue
        print(f"   {b.get('browser', '?')[:15]:<16} {safe_int(b.get('sessions', 0)):>6,} sessions, {pct(b.get('engagementRate', 0))} engaged")
    
    # ===== TIME PATTERNS =====
    section("🕐 TIME PATTERNS")
    
    time = data.get('time', {})
    
    subsection("Hour of Day (UTC)")
    hourly = time.get('hourly', [])
    if hourly:
        max_s = max(safe_int(h.get('sessions', 0)) for h in hourly)
        for h in hourly:
            sess = safe_int(h.get('sessions', 0))
            bar = '█' * int(sess / max_s * 15) if max_s > 0 else ''
            print(f"   {int(h.get('hour', 0)):02d}:00  {bar:<15} {sess:>5}")
    
    subsection("Day of Week")
    daily = time.get('daily', [])
    days_names = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    for d in daily:
        if '_error' in d: continue
        day_idx = int(d.get('dayOfWeek', 0))
        print(f"   {days_names[day_idx]:<4} {safe_int(d.get('sessions', 0)):>6} sessions, {pct(d.get('engagementRate', 0))} engaged")
    
    # ===== EVENTS =====
    section("⚡ EVENTS")
    
    events_data = data.get('events', {})
    events = events_data.get('events', [])
    
    print(f"   {'Event':<30} {'Count':>10} {'Users':>8} {'Per User':>10}")
    print("   " + "─"*65)
    for e in events[:12]:
        if '_error' in e: continue
        print(f"   {e.get('eventName', '?')[:29]:<30} {safe_int(e.get('eventCount', 0)):>10,} {safe_int(e.get('totalUsers', 0)):>8,} {safe_float(e.get('eventCountPerUser', 0)):>10.2f}")
    
    # ===== DAILY TREND =====
    section("📈 TREND (Last 14 Days)")
    
    trend = time.get('trend', [])[-14:]
    if trend:
        max_s = max(safe_int(t.get('sessions', 0)) for t in trend)
        for t in trend:
            sess = safe_int(t.get('sessions', 0))
            bar = '█' * int(sess / max_s * 20) if max_s > 0 else ''
            date = t.get('date', '')
            date_fmt = f"{date[4:6]}/{date[6:]}" if len(date) == 8 else date
            print(f"   {date_fmt}  {bar:<20} {sess:>5} ({safe_int(t.get('totalUsers', 0))} users)")
    
    # ===== RECOMMENDATIONS =====
    section("💡 ACTIONABLE INSIGHTS")
    
    insights = []
    
    # Traffic diversity
    if scores.get('traffic_diversity', 100) < 50 and channels:
        top = channels[0]
        pct_top = safe_int(top.get('sessions', 0)) / total_sessions * 100 if total_sessions > 0 else 0
        insights.append(f"⚠️  {pct_top:.0f}% of traffic from {top.get('sessionDefaultChannelGroup')} — diversify sources")
    
    # High bounce pages
    if high_bounce:
        worst = high_bounce[0]
        insights.append(f"🚨 Fix {worst.get('pagePath')} — {pct(worst.get('bounceRate'))} bounce rate")
    
    # Mobile
    if scores.get('mobile', 100) < 50:
        insights.append("📱 Low mobile traffic — check mobile UX")
    
    # Engagement
    if scores.get('engagement', 100) < 50:
        insights.append("📉 Low engagement — improve content or page speed")
    
    # Growth
    if scores.get('growth', 50) < 40:
        insights.append("📉 Traffic declining — investigate cause")
    elif scores.get('growth', 50) > 70:
        insights.append("📈 Strong growth! Keep doing what's working")
    
    # Retention
    if scores.get('retention', 50) < 30:
        insights.append("👋 Low retention — users aren't coming back")
    
    # No campaigns
    sources = acq.get('sources', [])
    has_campaigns = any(s.get('sessionMedium') in ['cpc', 'email', 'social'] for s in sources if '_error' not in s)
    if not has_campaigns:
        insights.append("📢 No tracked campaigns — consider UTM parameters")
    
    if insights:
        for insight in insights:
            print(f"   {insight}")
    else:
        print("   ✅ Looking good! No major issues detected.")
    
    print(f"\n{'='*80}")
    print("  ✅ DEEP DIVE COMPLETE")
    print(f"{'='*80}\n")


def save_snapshot(data: Dict, property_name: str, days: int):
    """Save snapshot for historical comparison."""
    
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    
    core = data.get('core', {}).get('current', {})
    activity = data.get('users', {}).get('activity', {})
    
    snapshot = Snapshot(
        property_id=PROPERTIES.get(property_name, property_name),
        property_name=property_name,
        generated_at=datetime.now().isoformat(),
        period_days=days,
        sessions=safe_int(core.get('sessions', 0)),
        users=safe_int(core.get('totalUsers', 0)),
        new_users=safe_int(core.get('newUsers', 0)),
        engagement_rate=safe_float(core.get('engagementRate', 0)),
        bounce_rate=safe_float(core.get('bounceRate', 0)),
        avg_duration=safe_float(core.get('averageSessionDuration', 0)),
        pages_per_session=safe_float(core.get('screenPageViewsPerSession', 0)),
        page_views=safe_int(core.get('screenPageViews', 0)),
        events=safe_int(core.get('eventCount', 0)),
        dau=safe_int(activity.get('active1DayUsers', 0)),
        wau=safe_int(activity.get('active7DayUsers', 0)),
        mau=safe_int(activity.get('active28DayUsers', 0)),
        top_channels=data.get('acquisition', {}).get('channels', [])[:5],
        top_pages=data.get('content', {}).get('pages', [])[:10],
        top_countries=data.get('geography', {}).get('countries', [])[:5],
        content_groups=data.get('content', {}).get('content_groups'),
        scores=data.get('scores'),
        overall_score=int(sum(data.get('scores', {}).values()) / len(data.get('scores', {}))) if data.get('scores') else 0
    )
    
    # Save with date
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{property_name}_{date_str}.json"
    filepath = SNAPSHOTS_DIR / filename
    
    with open(filepath, 'w') as f:
        json.dump(snapshot.to_dict(), f, indent=2, default=str)
    
    print(f"   💾 Snapshot saved: {filepath}")


# ============================================================================
# MAIN
# ============================================================================

def deep_dive(property_name: str, days: int = 30, compare: bool = False):
    """Run complete deep dive analysis."""
    
    property_id = PROPERTIES.get(property_name.lower(), property_name)
    is_solvr = property_name.lower() == 'solvr'
    
    print(f"\n🔄 Analyzing {property_name} (property {property_id})...")
    
    ga = GA4Client(property_id)
    
    # Collect all data
    data = {
        'realtime': ga.realtime(),
        'core': analyze_core_metrics(ga, days),
        'acquisition': analyze_acquisition(ga, days),
        'content': analyze_content(ga, days, is_solvr=is_solvr),
        'users': analyze_users(ga, days),
        'geography': analyze_geography(ga, days),
        'technology': analyze_technology(ga, days),
        'time': analyze_time_patterns(ga, days),
        'events': analyze_events(ga, days),
    }
    
    # Calculate health scores
    data['scores'] = calculate_health_scores(data)
    
    # Print report
    print_report(data, property_name, days)
    
    # Save snapshot
    save_snapshot(data, property_name, days)
    
    return data


def list_properties():
    """List known properties."""
    print("\n📋 Known Properties:\n")
    for name, prop_id in PROPERTIES.items():
        print(f"   {name:<15} → {prop_id}")
    print("\n   Usage: python3 deep_dive_v2.py <name>")


def main():
    parser = argparse.ArgumentParser(description='GA4 Deep Dive v2 — Owner Dashboard')
    parser.add_argument('property', nargs='?', help='Property name or ID')
    parser.add_argument('--days', type=int, default=30, help='Analysis period (default: 30)')
    parser.add_argument('--compare', action='store_true', help='Compare with last snapshot')
    parser.add_argument('--list', action='store_true', help='List known properties')
    
    args = parser.parse_args()
    
    if args.list:
        list_properties()
        return
    
    if not args.property:
        parser.print_help()
        return
    
    deep_dive(args.property, args.days, args.compare)


if __name__ == '__main__':
    main()
