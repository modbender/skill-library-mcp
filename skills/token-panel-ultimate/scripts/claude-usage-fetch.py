#!/usr/bin/env python3
"""
Claude Max Usage Fetcher
Extracts OAuth token from Claude Code credentials and fetches real-time usage.
Writes to claude-usage.json for the Budget Panel widget.

Usage:
    ./claude-usage-fetch.py              # Print usage
    ./claude-usage-fetch.py --update     # Update claude-usage.json
    ./claude-usage-fetch.py --json       # Output raw JSON
"""

import json
import os
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

CREDENTIALS_PATH = Path.home() / '.claude' / '.credentials.json'
USAGE_JSON_PATH = Path.home() / '.openclaw/workspace/memory/claude-usage.json'
API_URL = 'https://api.anthropic.com/api/oauth/usage'

def get_oauth_token():
    """Extract OAuth token from Claude Code credentials."""
    if not CREDENTIALS_PATH.exists():
        raise FileNotFoundError(f"Claude Code credentials not found at {CREDENTIALS_PATH}")
    
    with open(CREDENTIALS_PATH) as f:
        creds = json.load(f)
    
    oauth = creds.get('claudeAiOauth', {})
    token = oauth.get('accessToken')
    
    if not token:
        raise ValueError("No accessToken found in credentials")
    
    return token, oauth

def fetch_usage(token):
    """Fetch usage from Anthropic OAuth API."""
    req = urllib.request.Request(
        API_URL,
        headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'claude-code/2.0.32',
            'Authorization': f'Bearer {token}',
            'anthropic-beta': 'oauth-2025-04-20'
        }
    )
    
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())

def format_reset_time(iso_str):
    """Convert ISO timestamp to human-readable local time."""
    if not iso_str:
        return None
    dt = datetime.fromisoformat(iso_str.replace('+00:00', '+00:00'))
    # Convert to local time (simple approach)
    return dt.strftime('%Y-%m-%d %H:%M UTC')

def update_usage_json(usage_data, oauth_info):
    """Update claude-usage.json with fetched data."""
    five_hour = usage_data.get('five_hour', {}) or {}
    seven_day = usage_data.get('seven_day', {}) or {}
    seven_day_sonnet = usage_data.get('seven_day_sonnet', {}) or {}
    seven_day_opus = usage_data.get('seven_day_opus', {}) or {}
    extra = usage_data.get('extra_usage', {}) or {}
    
    output = {
        "mode": "subscription",
        "plan": oauth_info.get('subscriptionType', 'unknown'),
        "rateLimitTier": oauth_info.get('rateLimitTier', 'unknown'),
        "fetchedAt": datetime.utcnow().isoformat() + 'Z',
        "limits": {
            "five_hour": {
                "utilization": five_hour.get('utilization', 0),
                "resets_at": five_hour.get('resets_at'),
                "resets_at_human": format_reset_time(five_hour.get('resets_at'))
            },
            "seven_day": {
                "utilization": seven_day.get('utilization', 0),
                "resets_at": seven_day.get('resets_at'),
                "resets_at_human": format_reset_time(seven_day.get('resets_at'))
            },
            "seven_day_sonnet": {
                "utilization": seven_day_sonnet.get('utilization', 0),
                "resets_at": seven_day_sonnet.get('resets_at')
            },
            "seven_day_opus": {
                "utilization": (seven_day_opus.get('utilization', 0) if seven_day_opus else 0),
                "resets_at": (seven_day_opus.get('resets_at') if seven_day_opus else None)
            }
        },
        "extra_usage": {
            "enabled": extra.get('is_enabled', False),
            "monthly_limit": extra.get('monthly_limit'),
            "used_credits": extra.get('used_credits'),
            "utilization": extra.get('utilization')
        }
    }
    
    USAGE_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(USAGE_JSON_PATH, 'w') as f:
        json.dump(output, f, indent=2)
    
    return output

def print_usage(usage_data):
    """Print formatted usage to terminal."""
    five_hour = usage_data.get('five_hour', {}) or {}
    seven_day = usage_data.get('seven_day', {}) or {}
    seven_day_sonnet = usage_data.get('seven_day_sonnet', {}) or {}
    
    def bar(pct):
        filled = int(pct / 5)
        return '█' * filled + '░' * (20 - filled)
    
    print("\n╔══════════════════════════════════════════╗")
    print("║       CLAUDE MAX USAGE (REAL-TIME)       ║")
    print("╠══════════════════════════════════════════╣")
    
    # 5-hour
    pct = five_hour.get('utilization', 0)
    reset = format_reset_time(five_hour.get('resets_at')) or 'N/A'
    print(f"║ 5-Hour:  {bar(pct)} {pct:5.1f}% ║")
    print(f"║          Resets: {reset:<22} ║")
    
    # 7-day
    pct = seven_day.get('utilization', 0)
    reset = format_reset_time(seven_day.get('resets_at')) or 'N/A'
    print(f"║ 7-Day:   {bar(pct)} {pct:5.1f}% ║")
    print(f"║          Resets: {reset:<22} ║")
    
    # 7-day Sonnet (if used)
    pct = seven_day_sonnet.get('utilization', 0)
    if pct > 0:
        print(f"║ Sonnet:  {bar(pct)} {pct:5.1f}% ║")
    
    print("╚══════════════════════════════════════════╝\n")

def main():
    args = sys.argv[1:]
    
    try:
        token, oauth_info = get_oauth_token()
        usage_data = fetch_usage(token)
        
        if '--json' in args:
            print(json.dumps(usage_data, indent=2))
        elif '--update' in args:
            output = update_usage_json(usage_data, oauth_info)
            print(f"✓ Updated {USAGE_JSON_PATH}")
            print(f"  5h: {output['limits']['five_hour']['utilization']}%  |  7d: {output['limits']['seven_day']['utilization']}%")
        else:
            print_usage(usage_data)
            
    except FileNotFoundError as e:
        print(f"❌ {e}", file=sys.stderr)
        print("   Install Claude Code and login first: npm install -g @anthropic-ai/claude-code", file=sys.stderr)
        sys.exit(1)
    except urllib.error.HTTPError as e:
        print(f"❌ API Error {e.code}: {e.reason}", file=sys.stderr)
        if e.code == 401:
            print("   Token expired. Run: claude /login", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
