#!/usr/bin/env python3
"""
GA4 Weekly Report with Historical Comparison
Runs every Sunday, compares with previous week, emails findings.

CONFIGURATION REQUIRED:
Set these environment variables before running:
  - GA4_REPORT_RECIPIENTS: Comma-separated list of email addresses
  - AGENTMAIL_INBOX: Your AgentMail inbox address
  - AGENTMAIL_API_KEY: Your AgentMail API key

Example:
  export GA4_REPORT_RECIPIENTS="you@example.com"
  export AGENTMAIL_INBOX="youragent@agentmail.to"
  export AGENTMAIL_API_KEY="am_your_key_here"
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange, Dimension, Metric, RunReportRequest
)
from google.oauth2.credentials import Credentials

# Config
TOKEN_PATH = Path.home() / '.config' / 'ga-deep-dive' / 'token.json'
DATA_DIR = Path(__file__).parent.parent / 'data' / 'snapshots'
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Default properties - users should edit this for their own GA4 properties
PROPERTIES = {
    # 'mysite': 'YOUR_GA4_PROPERTY_ID',
    # 'blog': 'ANOTHER_PROPERTY_ID',
}

# Metrics to track week-over-week
CORE_METRICS = [
    'sessions', 'totalUsers', 'newUsers', 'engagementRate',
    'bounceRate', 'averageSessionDuration', 'screenPageViews'
]


def get_email_config():
    """Get email configuration from environment variables."""
    recipients = os.environ.get('GA4_REPORT_RECIPIENTS', '')
    inbox = os.environ.get('AGENTMAIL_INBOX', '')
    api_key = os.environ.get('AGENTMAIL_API_KEY', '')
    
    if not all([recipients, inbox, api_key]):
        return None
    
    return {
        'recipients': [r.strip() for r in recipients.split(',') if r.strip()],
        'inbox': inbox,
        'api_key': api_key
    }


def get_client():
    """Get authenticated GA4 client."""
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH))
    return BetaAnalyticsDataClient(credentials=creds)


def fetch_weekly_data(client, property_id, property_name):
    """Fetch this week's core metrics."""
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
        metrics=[Metric(name=m) for m in CORE_METRICS],
        limit=1
    )
    
    try:
        response = client.run_report(request)
        if response.rows:
            data = {}
            for i, metric in enumerate(CORE_METRICS):
                val = response.rows[0].metric_values[i].value
                # Convert to appropriate type
                if metric in ['engagementRate', 'bounceRate']:
                    data[metric] = float(val)
                elif metric == 'averageSessionDuration':
                    data[metric] = float(val)
                else:
                    data[metric] = int(float(val))
            return data
    except Exception as e:
        print(f"Error fetching {property_name}: {e}")
    return None


def fetch_top_pages(client, property_id, limit=10):
    """Fetch top pages for the week."""
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
        dimensions=[Dimension(name="pagePath")],
        metrics=[Metric(name="screenPageViews"), Metric(name="totalUsers")],
        limit=limit
    )
    
    try:
        response = client.run_report(request)
        pages = []
        for row in response.rows:
            pages.append({
                'path': row.dimension_values[0].value,
                'views': int(float(row.metric_values[0].value)),
                'users': int(float(row.metric_values[1].value))
            })
        return pages
    except:
        return []


def fetch_top_sources(client, property_id, limit=10):
    """Fetch top traffic sources for the week."""
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
        dimensions=[Dimension(name="sessionSource")],
        metrics=[Metric(name="sessions"), Metric(name="engagementRate")],
        limit=limit
    )
    
    try:
        response = client.run_report(request)
        sources = []
        for row in response.rows:
            sources.append({
                'source': row.dimension_values[0].value,
                'sessions': int(float(row.metric_values[0].value)),
                'engagement': float(row.metric_values[1].value)
            })
        return sources
    except:
        return []


def save_snapshot(property_name, data):
    """Save weekly snapshot to JSON file."""
    today = datetime.now().strftime('%Y-%m-%d')
    filename = DATA_DIR / f"{property_name}_{today}.json"
    
    snapshot = {
        'date': today,
        'property': property_name,
        'metrics': data['metrics'],
        'top_pages': data['top_pages'],
        'top_sources': data['top_sources'],
        'generated_at': datetime.now().isoformat()
    }
    
    with open(filename, 'w') as f:
        json.dump(snapshot, f, indent=2)
    
    return filename


def load_previous_snapshot(property_name):
    """Load most recent previous snapshot."""
    files = sorted(DATA_DIR.glob(f"{property_name}_*.json"), reverse=True)
    
    # Skip today's file if it exists
    today = datetime.now().strftime('%Y-%m-%d')
    for f in files:
        if today not in f.name:
            with open(f) as fp:
                return json.load(fp)
    return None


def calculate_changes(current, previous):
    """Calculate week-over-week changes."""
    if not previous:
        return None
    
    changes = {}
    for metric in CORE_METRICS:
        curr_val = current.get(metric, 0)
        prev_val = previous.get(metric, 0)
        
        if prev_val > 0:
            pct_change = ((curr_val - prev_val) / prev_val) * 100
        else:
            pct_change = 100 if curr_val > 0 else 0
        
        changes[metric] = {
            'current': curr_val,
            'previous': prev_val,
            'change': curr_val - prev_val,
            'pct_change': pct_change
        }
    
    return changes


def format_metric(name, value):
    """Format metric value for display."""
    if name in ['engagementRate', 'bounceRate']:
        return f"{value * 100:.1f}%"
    elif name == 'averageSessionDuration':
        return f"{value:.0f}s"
    else:
        return f"{value:,}"


def generate_report(property_name, current_data, changes, top_pages, top_sources):
    """Generate email-friendly report."""
    report = []
    report.append(f"# 📊 {property_name.upper()} — Weekly GA4 Report")
    report.append(f"**Week ending:** {datetime.now().strftime('%B %d, %Y')}")
    report.append("")
    
    # Core metrics with changes
    report.append("## 📈 Core Metrics")
    report.append("")
    report.append("| Metric | This Week | Last Week | Change |")
    report.append("|--------|-----------|-----------|--------|")
    
    metric_labels = {
        'sessions': 'Sessions',
        'totalUsers': 'Total Users',
        'newUsers': 'New Users',
        'engagementRate': 'Engagement Rate',
        'bounceRate': 'Bounce Rate',
        'averageSessionDuration': 'Avg Duration',
        'screenPageViews': 'Page Views'
    }
    
    for metric in CORE_METRICS:
        label = metric_labels.get(metric, metric)
        if changes and metric in changes:
            c = changes[metric]
            curr = format_metric(metric, c['current'])
            prev = format_metric(metric, c['previous'])
            pct = c['pct_change']
            arrow = '📈' if pct > 5 else '📉' if pct < -5 else '➡️'
            change_str = f"{arrow} {pct:+.1f}%"
        else:
            curr = format_metric(metric, current_data.get(metric, 0))
            prev = "—"
            change_str = "—"
        
        report.append(f"| {label} | {curr} | {prev} | {change_str} |")
    
    report.append("")
    
    # Top pages
    report.append("## 📄 Top Pages")
    report.append("")
    for i, page in enumerate(top_pages[:5], 1):
        report.append(f"{i}. `{page['path']}` — {page['views']} views, {page['users']} users")
    report.append("")
    
    # Top sources
    report.append("## 🔗 Top Traffic Sources")
    report.append("")
    for source in top_sources[:5]:
        eng_pct = source['engagement'] * 100
        report.append(f"- **{source['source']}**: {source['sessions']} sessions ({eng_pct:.0f}% engagement)")
    report.append("")
    
    # Insights
    report.append("## 💡 Key Insights")
    report.append("")
    
    if changes:
        # Find biggest changes
        biggest_gain = max(changes.items(), key=lambda x: x[1]['pct_change'])
        biggest_drop = min(changes.items(), key=lambda x: x[1]['pct_change'])
        
        if biggest_gain[1]['pct_change'] > 10:
            report.append(f"- 🚀 **{metric_labels[biggest_gain[0]]}** up {biggest_gain[1]['pct_change']:.1f}%")
        if biggest_drop[1]['pct_change'] < -10:
            report.append(f"- ⚠️ **{metric_labels[biggest_drop[0]]}** down {abs(biggest_drop[1]['pct_change']):.1f}%")
    
    report.append("")
    report.append("---")
    report.append(f"*Generated by ga-deep-dive at {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC*")
    
    return "\n".join(report)


def send_email(config, subject, body):
    """Send email via AgentMail."""
    try:
        from agentmail import AgentMail
        
        client = AgentMail(api_key=config['api_key'])
        
        # Convert markdown to HTML (basic)
        html_body = body.replace('\n', '<br>\n')
        html_body = f"<div style='font-family: monospace; white-space: pre-wrap;'>{html_body}</div>"
        
        for recipient in config['recipients']:
            client.inboxes.messages.send(
                inbox_id=config['inbox'],
                to=recipient,
                subject=subject,
                html=html_body
            )
            print(f"✅ Email sent to {recipient}")
        return True
    except Exception as e:
        print(f"❌ Email failed: {e}")
        return False


def main():
    """Run weekly report for all properties."""
    import argparse
    parser = argparse.ArgumentParser(description="Generate weekly GA4 reports")
    parser.add_argument("--dry-run", action="store_true", help="Generate report without sending email")
    args = parser.parse_args()
    
    if not PROPERTIES:
        print("❌ No properties configured!")
        print("Edit PROPERTIES dict in this script to add your GA4 property IDs.")
        return
    
    # Check email config
    email_config = None
    if not args.dry_run:
        email_config = get_email_config()
        if not email_config:
            print("⚠️  Email not configured. Set GA4_REPORT_RECIPIENTS, AGENTMAIL_INBOX, AGENTMAIL_API_KEY")
            print("   Running in dry-run mode...")
            args.dry_run = True
    
    client = get_client()
    all_reports = []
    
    for property_name, property_id in PROPERTIES.items():
        print(f"\n{'='*50}")
        print(f"Processing {property_name}...")
        
        # Fetch current data
        metrics = fetch_weekly_data(client, property_id, property_name)
        if not metrics:
            print(f"  Skipping {property_name} - no data")
            continue
        
        top_pages = fetch_top_pages(client, property_id)
        top_sources = fetch_top_sources(client, property_id)
        
        # Load previous snapshot
        previous = load_previous_snapshot(property_name)
        prev_metrics = previous.get('metrics') if previous else None
        
        # Calculate changes
        changes = calculate_changes(metrics, prev_metrics)
        
        # Save new snapshot
        snapshot_data = {
            'metrics': metrics,
            'top_pages': top_pages,
            'top_sources': top_sources
        }
        snapshot_file = save_snapshot(property_name, snapshot_data)
        print(f"  Saved snapshot: {snapshot_file}")
        
        # Generate report
        report = generate_report(property_name, metrics, changes, top_pages, top_sources)
        all_reports.append(report)
        print(f"  Generated report for {property_name}")
    
    # Combine all reports
    full_report = "\n\n---\n\n".join(all_reports)
    
    # Print to stdout
    print("\n" + "="*60)
    print(full_report)
    
    # Send email (unless dry-run)
    if not args.dry_run and email_config:
        subject = f"📊 Weekly GA4 Report — {datetime.now().strftime('%B %d, %Y')}"
        send_email(email_config, subject, full_report)
    
    return full_report


if __name__ == '__main__':
    main()
