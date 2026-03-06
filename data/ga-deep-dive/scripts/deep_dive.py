#!/usr/bin/env python3
"""
GA4 Deep Dive Analysis Tool — COMPREHENSIVE VERSION
Full property analysis with 374 dimensions and 95 metrics available.

Usage:
    python3 deep_dive.py <property_name_or_id> [--days N]
    python3 deep_dive.py --list
    python3 deep_dive.py solvr --days 30

Features:
    - Core metrics breakdown (sessions, users, engagement, bounce, duration)
    - Full acquisition analysis (channel, source, medium)
    - Referrer URLs detail
    - Landing pages with engagement metrics
    - All pages performance
    - Complete event tracking
    - Technology breakdown (browser, OS, device, resolution)
    - Geography with cities and regions
    - Time patterns (hour of day, day of week)
    - New vs returning user analysis
    - User languages
    - Daily session trends
    - Content-specific pages (agents, ideas, problems)
    - High bounce page analysis
    - Health scores with recommendations
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange, Dimension, Metric, RunReportRequest,
    RunRealtimeReportRequest, OrderBy, Filter, FilterExpression
)
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Config
SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
TOKEN_PATH = Path.home() / '.config' / 'ga-deep-dive' / 'token.json'
CREDENTIALS_PATH = Path.home() / '.config' / 'ga-deep-dive' / 'credentials.json'

# Known properties (name -> property_id mapping)
PROPERTIES = {
    'solvr': '523300499',
    'abecmed': '291040306',
    'sonus': '517562144',
    'reiduchat': '470924960',
    'caosfera': '485692354',
    'ttn': '513412902',
    # Add more as needed
}


def get_credentials():
    """Get or refresh OAuth credentials."""
    from google.auth.transport.requests import Request
    
    creds = None
    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    if TOKEN_PATH.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
        except Exception as e:
            print(f"⚠️  Token load error: {e}")
            creds = None
    
    if creds:
        if not creds.valid:
            if creds.expired and creds.refresh_token:
                try:
                    print("   🔄 Refreshing token...")
                    creds.refresh(Request())
                    with open(TOKEN_PATH, 'w') as f:
                        f.write(creds.to_json())
                    print("   ✅ Token refreshed")
                except Exception as e:
                    print(f"⚠️  Token refresh failed: {e}")
                    creds = None
    
    if not creds or not creds.valid:
        if not CREDENTIALS_PATH.exists():
            print(f"❌ No valid credentials.")
            print(f"   Need credentials.json from Google Cloud Console")
            print(f"   Place at: {CREDENTIALS_PATH}")
            sys.exit(1)
        
        flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
        creds = flow.run_local_server(port=0)
        
        with open(TOKEN_PATH, 'w') as f:
            f.write(creds.to_json())
        print("   ✅ New token saved")
    
    return creds


def run_report(client, property_id, dimensions, metrics, days=30, limit=20, order_by=None, dim_filter=None):
    """Run a GA4 report with given dimensions and metrics."""
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
        dimensions=[Dimension(name=d) for d in dimensions],
        metrics=[Metric(name=m) for m in metrics],
        limit=limit
    )
    if order_by:
        request.order_bys = [OrderBy(metric=OrderBy.MetricOrderBy(metric_name=order_by), desc=True)]
    if dim_filter:
        request.dimension_filter = dim_filter
    
    try:
        response = client.run_report(request)
        results = []
        for row in response.rows:
            r = {}
            for i, dim in enumerate(dimensions):
                r[dim] = row.dimension_values[i].value
            for i, met in enumerate(metrics):
                r[met] = row.metric_values[i].value
            results.append(r)
        return results
    except Exception as e:
        return [{"error": str(e)}]


def section(title):
    """Print section header."""
    print(f"\n{'='*75}")
    print(f"  {title}")
    print('='*75)


def safe_int(val):
    try:
        return int(float(val))
    except:
        return 0


def safe_float(val):
    try:
        return float(val)
    except:
        return 0.0


def deep_dive(property_id, days=30):
    """Run comprehensive deep dive analysis."""
    creds = get_credentials()
    client = BetaAnalyticsDataClient(credentials=creds)
    
    print(f"\n🔍 GA4 DEEP DIVE ANALYSIS — COMPREHENSIVE")
    print(f"   Property: {property_id}")
    print(f"   Period: Last {days} days")
    print(f"   Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # ========== REAL-TIME ==========
    section("🟢 REAL-TIME")
    try:
        rt_request = RunRealtimeReportRequest(
            property=f"properties/{property_id}",
            metrics=[Metric(name="activeUsers")]
        )
        rt_response = client.run_realtime_report(rt_request)
        active = rt_response.rows[0].metric_values[0].value if rt_response.rows else "0"
        print(f"   Active Users Now: {active}")
    except Exception as e:
        print(f"   Active Users Now: Error: {e}")
    
    # ========== CORE METRICS ==========
    # Note: GA4 API limits to 10 metrics per request, so we split into two calls
    section("📊 CORE METRICS BREAKDOWN")
    data1 = run_report(client, property_id, [], [
        "sessions", "totalUsers", "newUsers", "activeUsers",
        "engagedSessions", "engagementRate", "averageSessionDuration",
        "bounceRate", "screenPageViews", "eventCount"
    ], days=days, limit=1)
    data2 = run_report(client, property_id, [], [
        "sessionsPerUser", "screenPageViewsPerSession", "eventsPerSession",
        "conversions", "userEngagementDuration"
    ], days=days, limit=1)
    
    if data1 and 'error' not in data1[0]:
        d = data1[0]
        d2 = data2[0] if data2 and 'error' not in data2[0] else {}
        print(f"""
   Sessions:              {safe_int(d.get('sessions', 0)):,}
   Total Users:           {safe_int(d.get('totalUsers', 0)):,}
   New Users:             {safe_int(d.get('newUsers', 0)):,}
   Active Users:          {safe_int(d.get('activeUsers', 0)):,}
   
   Engaged Sessions:      {safe_int(d.get('engagedSessions', 0)):,}
   Engagement Rate:       {safe_float(d.get('engagementRate', 0))*100:.1f}%
   Bounce Rate:           {safe_float(d.get('bounceRate', 0))*100:.1f}%
   
   Avg Session Duration:  {safe_float(d.get('averageSessionDuration', 0)):.0f}s
   Sessions/User:         {safe_float(d2.get('sessionsPerUser', 0)):.2f}
   Pages/Session:         {safe_float(d2.get('screenPageViewsPerSession', 0)):.2f}
   Events/Session:        {safe_float(d2.get('eventsPerSession', 0)):.2f}
   
   Total Page Views:      {safe_int(d.get('screenPageViews', 0)):,}
   Total Events:          {safe_int(d.get('eventCount', 0)):,}
   Conversions:           {safe_int(d2.get('conversions', 0)):,}
   User Engagement:       {safe_float(d2.get('userEngagementDuration', 0))/60:.1f} min
""")
    
    # ========== USER ACQUISITION ==========
    section("🚦 USER ACQUISITION — FULL BREAKDOWN")
    data = run_report(client, property_id,
        ["sessionDefaultChannelGroup", "sessionSource", "sessionMedium"],
        ["sessions", "totalUsers", "newUsers", "engagementRate", "averageSessionDuration", "bounceRate"],
        days=days, limit=25, order_by="sessions"
    )
    print(f"   {'Channel':<18} {'Source':<22} {'Medium':<10} {'Sess':>6} {'Users':>5} {'New':>4} {'Eng%':>5} {'Bnc%':>5}")
    print("   " + "-"*85)
    for r in data:
        if 'error' in r:
            continue
        print(f"   {r['sessionDefaultChannelGroup'][:17]:<18} {r['sessionSource'][:21]:<22} {r['sessionMedium'][:9]:<10} {safe_int(r['sessions']):>6} {safe_int(r['totalUsers']):>5} {safe_int(r['newUsers']):>4} {safe_float(r['engagementRate'])*100:>4.0f}% {safe_float(r['bounceRate'])*100:>4.0f}%")
    
    # ========== REFERRERS ==========
    section("🔗 REFERRERS — WHERE TRAFFIC COMES FROM")
    data = run_report(client, property_id,
        ["sessionSource", "pageReferrer"],
        ["sessions", "engagementRate"],
        days=days, limit=25, order_by="sessions"
    )
    print(f"   {'Source':<22} {'Referrer URL':<45} {'Sess':>6}")
    print("   " + "-"*80)
    for r in data:
        if 'error' in r:
            continue
        ref = r['pageReferrer'][:44] if r['pageReferrer'] != '(not set)' else '-'
        print(f"   {r['sessionSource'][:21]:<22} {ref:<45} {safe_int(r['sessions']):>6}")
    
    # ========== LANDING PAGES ==========
    section("🚪 LANDING PAGES — ENTRY POINTS")
    data = run_report(client, property_id,
        ["landingPage", "sessionDefaultChannelGroup"],
        ["sessions", "totalUsers", "bounceRate", "averageSessionDuration", "screenPageViewsPerSession"],
        days=days, limit=30, order_by="sessions"
    )
    print(f"   {'Landing Page':<40} {'Channel':<12} {'Sess':>5} {'Bnc%':>5} {'Dur':>6} {'Pgs':>4}")
    print("   " + "-"*80)
    for r in data:
        if 'error' in r:
            continue
        dur = f"{safe_float(r['averageSessionDuration']):.0f}s"
        print(f"   {r['landingPage'][:39]:<40} {r['sessionDefaultChannelGroup'][:11]:<12} {safe_int(r['sessions']):>5} {safe_float(r['bounceRate'])*100:>4.0f}% {dur:>6} {safe_float(r['screenPageViewsPerSession']):>4.1f}")
    
    # ========== ALL PAGES ==========
    section("📄 ALL PAGES — DETAILED PERFORMANCE")
    data = run_report(client, property_id,
        ["pagePath", "pageTitle"],
        ["screenPageViews", "totalUsers", "averageSessionDuration", "engagementRate"],
        days=days, limit=35, order_by="screenPageViews"
    )
    print(f"   {'Path':<38} {'Title':<25} {'Views':>6} {'Users':>5} {'Eng%':>5}")
    print("   " + "-"*85)
    for r in data:
        if 'error' in r:
            continue
        title = r['pageTitle'][:24] if r['pageTitle'] != '(not set)' else '-'
        print(f"   {r['pagePath'][:37]:<38} {title:<25} {safe_int(r['screenPageViews']):>6} {safe_int(r['totalUsers']):>5} {safe_float(r['engagementRate'])*100:>4.0f}%")
    
    # ========== EVENTS ==========
    section("⚡ ALL EVENTS — COMPLETE LIST")
    data = run_report(client, property_id,
        ["eventName"],
        ["eventCount", "totalUsers", "eventCountPerUser", "eventValue"],
        days=days, limit=30, order_by="eventCount"
    )
    print(f"   {'Event Name':<35} {'Count':>10} {'Users':>7} {'Per User':>9} {'Value':>10}")
    print("   " + "-"*80)
    for r in data:
        if 'error' in r:
            continue
        val = f"${safe_float(r['eventValue']):,.0f}" if safe_float(r['eventValue']) > 0 else "-"
        print(f"   {r['eventName']:<35} {safe_int(r['eventCount']):>10,} {safe_int(r['totalUsers']):>7} {safe_float(r['eventCountPerUser']):>9.2f} {val:>10}")
    
    # ========== TECHNOLOGY ==========
    section("💻 TECHNOLOGY — BROWSERS & OS")
    data = run_report(client, property_id,
        ["browser", "operatingSystem", "deviceCategory"],
        ["sessions", "totalUsers", "engagementRate", "bounceRate"],
        days=days, limit=20, order_by="sessions"
    )
    print(f"   {'Browser':<18} {'OS':<14} {'Device':<8} {'Sess':>6} {'Users':>5} {'Eng%':>5} {'Bnc%':>5}")
    print("   " + "-"*75)
    for r in data:
        if 'error' in r:
            continue
        print(f"   {r['browser'][:17]:<18} {r['operatingSystem'][:13]:<14} {r['deviceCategory']:<8} {safe_int(r['sessions']):>6} {safe_int(r['totalUsers']):>5} {safe_float(r['engagementRate'])*100:>4.0f}% {safe_float(r['bounceRate'])*100:>4.0f}%")
    
    # ========== SCREEN RESOLUTION ==========
    section("📱 SCREEN RESOLUTIONS")
    data = run_report(client, property_id,
        ["screenResolution", "deviceCategory"],
        ["sessions", "totalUsers", "engagementRate"],
        days=days, limit=15, order_by="sessions"
    )
    print(f"   {'Resolution':<18} {'Device':<10} {'Sessions':>8} {'Users':>6} {'Eng%':>6}")
    print("   " + "-"*55)
    for r in data:
        if 'error' in r:
            continue
        print(f"   {r['screenResolution']:<18} {r['deviceCategory']:<10} {safe_int(r['sessions']):>8} {safe_int(r['totalUsers']):>6} {safe_float(r['engagementRate'])*100:>5.1f}%")
    
    # ========== GEOGRAPHY ==========
    section("🌍 GEOGRAPHY — COUNTRIES & CITIES")
    data = run_report(client, property_id,
        ["country", "city", "region"],
        ["sessions", "totalUsers", "engagementRate", "averageSessionDuration"],
        days=days, limit=30, order_by="sessions"
    )
    print(f"   {'Country':<18} {'City':<18} {'Region':<14} {'Sess':>5} {'Users':>5} {'Eng%':>5} {'Dur':>5}")
    print("   " + "-"*85)
    for r in data:
        if 'error' in r:
            continue
        city = r['city'][:17] if r['city'] != '(not set)' else '-'
        region = r['region'][:13] if r['region'] != '(not set)' else '-'
        dur = f"{safe_float(r['averageSessionDuration']):.0f}s"
        print(f"   {r['country'][:17]:<18} {city:<18} {region:<14} {safe_int(r['sessions']):>5} {safe_int(r['totalUsers']):>5} {safe_float(r['engagementRate'])*100:>4.0f}% {dur:>5}")
    
    # ========== TIME PATTERNS - HOUR ==========
    section("🕐 TIME PATTERNS — HOUR OF DAY (UTC)")
    data = run_report(client, property_id,
        ["hour"],
        ["sessions", "totalUsers", "engagementRate"],
        days=days, limit=24
    )
    data_sorted = sorted([r for r in data if 'error' not in r], key=lambda x: int(x['hour']))
    print(f"   Hour    Sessions  Users  Eng%   Visual")
    print("   " + "-"*55)
    max_s = max(safe_int(r['sessions']) for r in data_sorted) if data_sorted else 1
    for r in data_sorted:
        sessions = safe_int(r['sessions'])
        bar = '█' * int(sessions / max_s * 25)
        print(f"   {r['hour']:>5}:00  {sessions:>6}   {safe_int(r['totalUsers']):>5}  {safe_float(r['engagementRate'])*100:>4.0f}%  {bar}")
    
    # ========== TIME PATTERNS - DAY OF WEEK ==========
    section("📅 TIME PATTERNS — DAY OF WEEK")
    data = run_report(client, property_id,
        ["dayOfWeek"],
        ["sessions", "totalUsers", "engagementRate", "averageSessionDuration"],
        days=days, limit=7
    )
    days_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    print(f"   {'Day':<12} {'Sessions':>10} {'Users':>8} {'Eng%':>8} {'Avg Dur':>10}")
    print("   " + "-"*55)
    for r in sorted([r for r in data if 'error' not in r], key=lambda x: int(x['dayOfWeek'])):
        day_name = days_names[int(r['dayOfWeek'])]
        print(f"   {day_name:<12} {safe_int(r['sessions']):>10} {safe_int(r['totalUsers']):>8} {safe_float(r['engagementRate'])*100:>7.1f}% {safe_float(r['averageSessionDuration']):>9.0f}s")
    
    # ========== NEW VS RETURNING ==========
    section("👤 NEW VS RETURNING USERS")
    data = run_report(client, property_id,
        ["newVsReturning"],
        ["sessions", "totalUsers", "engagementRate", "screenPageViewsPerSession", "bounceRate"],
        days=days, limit=5
    )
    print(f"   {'Type':<15} {'Sessions':>10} {'Users':>8} {'Eng%':>8} {'Pgs/Sess':>10} {'Bounce':>8}")
    print("   " + "-"*65)
    for r in [r for r in data if 'error' not in r]:
        print(f"   {r['newVsReturning']:<15} {safe_int(r['sessions']):>10} {safe_int(r['totalUsers']):>8} {safe_float(r['engagementRate'])*100:>7.1f}% {safe_float(r['screenPageViewsPerSession']):>10.2f} {safe_float(r['bounceRate'])*100:>7.1f}%")
    
    # ========== LANGUAGES ==========
    section("🌐 USER LANGUAGES")
    data = run_report(client, property_id,
        ["language"],
        ["sessions", "totalUsers", "engagementRate"],
        days=days, limit=12, order_by="sessions"
    )
    print(f"   {'Language':<30} {'Sessions':>10} {'Users':>8} {'Eng%':>8}")
    print("   " + "-"*60)
    for r in [r for r in data if 'error' not in r]:
        print(f"   {r['language'][:29]:<30} {safe_int(r['sessions']):>10} {safe_int(r['totalUsers']):>8} {safe_float(r['engagementRate'])*100:>7.1f}%")
    
    # ========== DAILY TREND ==========
    section(f"📈 DAILY SESSIONS TREND (Last {days} days)")
    data = run_report(client, property_id,
        ["date"],
        ["sessions", "totalUsers", "engagementRate", "screenPageViews"],
        days=days, limit=days+1
    )
    data_sorted = sorted([r for r in data if 'error' not in r], key=lambda x: x['date'])
    print(f"   {'Date':<10} {'Sess':>6} {'Users':>5} {'Views':>6} {'Eng%':>5}  Trend")
    print("   " + "-"*60)
    max_s = max(safe_int(r['sessions']) for r in data_sorted) if data_sorted else 1
    for r in data_sorted[-14:]:  # Last 14 days
        s = safe_int(r['sessions'])
        bar = '█' * int(s / max_s * 18)
        date_fmt = f"{r['date'][4:6]}/{r['date'][6:]}"
        print(f"   {date_fmt:<10} {s:>6} {safe_int(r['totalUsers']):>5} {safe_int(r['screenPageViews']):>6} {safe_float(r['engagementRate'])*100:>4.0f}%  {bar}")
    
    # ========== CAMPAIGNS / UTM ==========
    section("📢 CAMPAIGNS & UTM TRACKING")
    data = run_report(client, property_id,
        ["sessionCampaign", "sessionSource", "sessionMedium"],
        ["sessions", "totalUsers", "engagementRate", "conversions"],
        days=days, limit=15, order_by="sessions"
    )
    campaigns = [r for r in data if 'error' not in r and r['sessionCampaign'] not in ['(not set)', '(organic)', '(direct)', '(referral)']]
    if campaigns:
        print(f"   {'Campaign':<30} {'Source':<15} {'Sess':>6} {'Conv':>5} {'Eng%':>6}")
        print("   " + "-"*70)
        for r in campaigns[:10]:
            print(f"   {r['sessionCampaign'][:29]:<30} {r['sessionSource'][:14]:<15} {safe_int(r['sessions']):>6} {safe_int(r['conversions']):>5} {safe_float(r['engagementRate'])*100:>5.1f}%")
    else:
        print("   No campaign data (consider adding UTM parameters to your links)")
    
    # ========== KEY EVENTS / CONVERSIONS ==========
    section("🎯 KEY EVENTS (CONVERSIONS)")
    data = run_report(client, property_id,
        ["eventName"],
        ["conversions", "totalUsers"],
        days=days, limit=20, order_by="conversions"
    )
    conversions = [r for r in data if 'error' not in r and safe_int(r['conversions']) > 0]
    if conversions:
        print(f"   {'Event Name':<40} {'Conversions':>12} {'Users':>8}")
        print("   " + "-"*65)
        for r in conversions:
            print(f"   {r['eventName']:<40} {safe_int(r['conversions']):>12} {safe_int(r['totalUsers']):>8}")
    else:
        print("   No key events configured (mark events as conversions in GA4 Admin)")
    
    # ========== HIGH BOUNCE PAGES ==========
    section("🚪 HIGH BOUNCE PAGES (WHERE USERS LEAVE)")
    data = run_report(client, property_id,
        ["pagePath"],
        ["sessions", "bounceRate", "engagementRate"],
        days=days, limit=30, order_by="sessions"
    )
    print(f"   {'Page':<42} {'Sessions':>8} {'Bounce':>8} {'Eng%':>8}")
    print("   " + "-"*70)
    high_bounce = [r for r in data if 'error' not in r and safe_float(r['bounceRate']) > 0.5 and safe_int(r['sessions']) > 2]
    for r in sorted(high_bounce, key=lambda x: safe_float(x['bounceRate']), reverse=True)[:12]:
        print(f"   {r['pagePath'][:41]:<42} {safe_int(r['sessions']):>8} {safe_float(r['bounceRate'])*100:>7.1f}% {safe_float(r['engagementRate'])*100:>7.1f}%")
    
    # ========== USER ACTIVITY METRICS ==========
    section("📈 USER ACTIVITY METRICS")
    data = run_report(client, property_id, [], [
        "active1DayUsers", "active7DayUsers", "active28DayUsers"
    ], days=days, limit=1)
    if data and 'error' not in data[0]:
        d = data[0]
        dau = safe_int(d.get('active1DayUsers', 0))
        wau = safe_int(d.get('active7DayUsers', 0))
        mau = safe_int(d.get('active28DayUsers', 0))
        # Calculate ratios properly (they should be <1)
        dau_wau = (dau / wau * 100) if wau > 0 else 0
        dau_mau = (dau / mau * 100) if mau > 0 else 0
        print(f"""
   Active Users (1 day):    {dau:,}
   Active Users (7 day):    {wau:,}
   Active Users (28 day):   {mau:,}
   
   DAU/WAU Stickiness:      {dau_wau:.1f}%  (how often users return weekly)
   DAU/MAU Stickiness:      {dau_mau:.1f}%  (how often users return monthly)
""")
    
    # ========== HEALTH SCORES ==========
    section("🏥 HEALTH SCORES")
    
    # Get data for scoring
    core = run_report(client, property_id, [], ["engagementRate", "bounceRate", "averageSessionDuration", "screenPageViewsPerSession"], days=days, limit=1)
    channels = run_report(client, property_id, ["sessionDefaultChannelGroup"], ["sessions"], days=days, limit=10, order_by="sessions")
    devices = run_report(client, property_id, ["deviceCategory"], ["sessions", "engagementRate"], days=days, limit=5, order_by="sessions")
    
    scores = {}
    
    # Engagement score (engagement rate + session duration)
    if core and 'error' not in core[0]:
        eng_rate = safe_float(core[0].get('engagementRate', 0))
        duration = safe_float(core[0].get('averageSessionDuration', 0))
        scores['engagement'] = min(100, int(eng_rate * 100 * 0.7 + min(duration / 3, 30)))
    else:
        scores['engagement'] = 50
    
    # Traffic diversity (not too reliant on one channel)
    if channels:
        total = sum(safe_int(r['sessions']) for r in channels if 'error' not in r)
        top = safe_int(channels[0]['sessions']) if channels else 0
        diversity = 1 - (top / total) if total > 0 else 0
        scores['traffic_diversity'] = int(diversity * 100)
    else:
        scores['traffic_diversity'] = 50
    
    # Mobile ready
    if devices:
        total = sum(safe_int(r['sessions']) for r in devices if 'error' not in r)
        mobile = sum(safe_int(r['sessions']) for r in devices if 'error' not in r and r['deviceCategory'] in ['mobile', 'tablet'])
        mobile_pct = mobile / total if total > 0 else 0
        scores['mobile'] = min(100, int(mobile_pct * 100 + 30))  # Bonus for having mobile traffic
    else:
        scores['mobile'] = 50
    
    # Content (pages per session)
    if core and 'error' not in core[0]:
        pps = safe_float(core[0].get('screenPageViewsPerSession', 0))
        scores['content'] = min(100, int(pps * 20))
    else:
        scores['content'] = 50
    
    # Growth (week-over-week comparison)
    this_week = run_report(client, property_id, [], ["sessions"], days=7, limit=1)
    last_week = run_report(client, property_id, [], ["sessions"], days=14, limit=1)  # Will subtract
    
    if this_week and last_week and 'error' not in this_week[0] and 'error' not in last_week[0]:
        tw_sessions = safe_int(this_week[0].get('sessions', 0))
        total_14d = safe_int(last_week[0].get('sessions', 0))
        lw_sessions = total_14d - tw_sessions  # Last week = 14 days total minus this week
        
        if lw_sessions > 0:
            growth_pct = ((tw_sessions - lw_sessions) / lw_sessions) * 100
            # Score: 50 = flat, 100 = +100% growth, 0 = -50% decline
            scores['growth'] = min(100, max(0, int(50 + growth_pct)))
        else:
            scores['growth'] = 75 if tw_sessions > 0 else 50  # New site bonus
    else:
        scores['growth'] = 50
    
    def score_bar(score):
        filled = int(score / 5)
        empty = 20 - filled
        return '█' * filled + '░' * empty
    
    def score_icon(score):
        if score >= 70:
            return '✅'
        elif score >= 50:
            return '⚠️'
        else:
            return '❌'
    
    print(f"   {score_icon(scores['engagement'])} Engagement           {score_bar(scores['engagement'])} {scores['engagement']}/100")
    print(f"   {score_icon(scores['traffic_diversity'])} Traffic Diversity    {score_bar(scores['traffic_diversity'])} {scores['traffic_diversity']}/100")
    print(f"   {score_icon(scores['mobile'])} Mobile Ready         {score_bar(scores['mobile'])} {scores['mobile']}/100")
    print(f"   {score_icon(scores['content'])} Content              {score_bar(scores['content'])} {scores['content']}/100")
    print(f"   {score_icon(scores['growth'])} Growth               {score_bar(scores['growth'])} {scores['growth']}/100")
    
    overall = int(sum(scores.values()) / len(scores))
    grade = 'A' if overall >= 80 else 'B' if overall >= 65 else 'C' if overall >= 50 else 'D'
    print(f"\n   ========================================")
    print(f"   🎯 OVERALL SCORE: {overall}/100 (Grade: {grade})")
    
    # ========== RECOMMENDATIONS ==========
    section("💡 RECOMMENDATIONS")
    
    if scores['traffic_diversity'] < 50:
        if channels:
            top_channel = channels[0]['sessionDefaultChannelGroup']
            top_pct = safe_int(channels[0]['sessions']) / sum(safe_int(r['sessions']) for r in channels if 'error' not in r) * 100
            print(f"   ⚠️  {top_pct:.0f}% from {top_channel} — diversify traffic sources")
    
    if scores['engagement'] < 50:
        print(f"   ⚠️  Low engagement — improve content quality or page load speed")
    
    if scores['mobile'] < 50:
        print(f"   ⚠️  Low mobile traffic — check mobile UX and responsiveness")
    
    if scores['content'] < 50:
        print(f"   ⚠️  Low pages/session — improve internal linking and navigation")
    
    print("\n" + "="*75)
    print("  ✅ DEEP DIVE COMPLETE")
    print("="*75)


def list_properties():
    """List known properties."""
    print("\n📋 Known Properties:\n")
    for name, prop_id in PROPERTIES.items():
        print(f"   {name:<20} → {prop_id}")
    print(f"\n   Usage: python3 deep_dive.py <name_or_id>")


def main():
    parser = argparse.ArgumentParser(description='GA4 Deep Dive Analysis')
    parser.add_argument('property', nargs='?', help='Property name or ID')
    parser.add_argument('--days', type=int, default=30, help='Analysis period in days')
    parser.add_argument('--list', action='store_true', help='List known properties')
    
    args = parser.parse_args()
    
    if args.list:
        list_properties()
        return
    
    if not args.property:
        parser.print_help()
        return
    
    # Resolve property ID
    property_id = PROPERTIES.get(args.property.lower(), args.property)
    
    deep_dive(property_id, args.days)


if __name__ == '__main__':
    main()
