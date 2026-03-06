#!/usr/bin/env python3
"""
Weekly Training Report - Sunday summary with trends and recommendations

Security-hardened for ClawHub publication:
- No hardcoded secrets
- Input validation on all external data
- Safe error handling (no data leakage)
- Webhook URL validation
- Secure token storage path (XDG)
- Request timeouts and retry logic
"""

import os
import sys
import json
import re
import logging
import urllib.request
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, List, Any
from urllib.error import HTTPError, URLError

# ============================================================================
# SECURE CONFIGURATION
# ============================================================================

def get_config_dir() -> str:
    """Get secure config directory"""
    xdg_config = os.environ.get('XDG_CONFIG_HOME')
    if xdg_config:
        return os.path.join(xdg_config, 'strava-training-coach')
    return os.path.expanduser('~/.config/strava-training-coach')

CONFIG_DIR = get_config_dir()
TOKEN_FILE = os.path.join(CONFIG_DIR, 'strava_tokens.json')
LOG_FILE = os.path.join(CONFIG_DIR, 'report.log')

os.makedirs(CONFIG_DIR, mode=0o700, exist_ok=True)

NOTIFICATION_CHANNEL = os.environ.get('NOTIFICATION_CHANNEL', 'discord').lower()
if NOTIFICATION_CHANNEL not in ('discord', 'slack'):
    NOTIFICATION_CHANNEL = 'discord'

DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL', '')
SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL', '')

VERBOSE = os.environ.get('VERBOSE', '').lower() in ('true', '1', 'yes')

def get_env_int(name: str, default: int, min_val: int, max_val: int) -> int:
    """Get validated int from environment"""
    try:
        val = int(os.environ.get(name, default))
        return max(min_val, min(max_val, val))
    except (ValueError, TypeError):
        return default

EASY_HR_CEILING = get_env_int('MIN_EASY_RUN_HEART_RATE', 145, 100, 200)

# ============================================================================
# SECURE LOGGING
# ============================================================================

class SensitiveDataFilter(logging.Filter):
    """Filter out sensitive data from logs"""
    REDACTION_PATTERNS = [
        (re.compile(r'[a-fA-F0-9]{20,}'), '[REDACTED]'),
        (re.compile(r'Bearer\s+\S+', re.IGNORECASE), 'Bearer [REDACTED]'),
        (re.compile(r'[A-Za-z0-9_\-]{20,}'), '[REDACTED]'),
        (re.compile(r'webhooks/[0-9]+/[a-zA-Z0-9_\-]+'), 'webhooks/[REDACTED]'),
        (re.compile(r'hooks\.slack\.com/services/[A-Za-z0-9/]+'), 'hooks.slack.com/services/[REDACTED]'),
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        if record.msg and isinstance(record.msg, str):
            for pattern, replacement in self.REDACTION_PATTERNS:
                record.msg = pattern.sub(replacement, record.msg)
        return True

def setup_logging() -> logging.Logger:
    """Configure secure logging"""
    logger = logging.getLogger('weekly_report')
    logger.setLevel(logging.DEBUG if VERBOSE else logging.INFO)
    logger.handlers = []

    try:
        file_handler = logging.FileHandler(LOG_FILE, mode='a')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        file_handler.addFilter(SensitiveDataFilter())
        logger.addHandler(file_handler)
    except (IOError, OSError) as e:
        print(f"Warning: Could not create log file: {e}", file=sys.stderr)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(message)s'))
    console_handler.addFilter(SensitiveDataFilter())
    logger.addHandler(console_handler)

    return logger

logger = setup_logging()

# ============================================================================
# SECURE API CLIENT
# ============================================================================

def validate_token_data(data: Dict) -> bool:
    """Validate token data structure"""
    if not isinstance(data, dict):
        return False
    access_token = data.get('access_token')
    if not isinstance(access_token, str) or len(access_token) < 10:
        return False
    return True

def load_tokens() -> Optional[str]:
    """Load and validate Strava tokens securely"""
    try:
        with open(TOKEN_FILE, 'r') as f:
            data = json.load(f)

        if not validate_token_data(data):
            logger.error("Invalid token data structure")
            return None

        access_token = data.get('access_token')
        refresh_token = data.get('refresh_token')
        expires_at = data.get('expires_at', 0)

        if expires_at and expires_at < (datetime.now().timestamp() + 300):
            logger.info("Token expired, refreshing...")
            if refresh_token:
                return refresh_access_token(refresh_token)
            return None

        return access_token

    except FileNotFoundError:
        logger.error("Token file not found. Run auth.py first.")
        return None
    except json.JSONDecodeError:
        logger.error("Invalid token file format")
        return None
    except (IOError, OSError) as e:
        logger.error(f"Cannot read token file: {e}")
        return None

def refresh_access_token(refresh_token: str) -> Optional[str]:
    """Refresh expired access token securely"""
    import urllib.parse

    client_id = os.environ.get('STRAVA_CLIENT_ID', '').strip()
    client_secret = os.environ.get('STRAVA_CLIENT_SECRET', '').strip()

    if not client_id or not client_secret:
        logger.error("STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET required for token refresh")
        return None

    url = 'https://www.strava.com/oauth/token'
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }

    req = urllib.request.Request(
        url,
        data=urllib.parse.urlencode(data).encode(),
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        method='POST'
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            new_tokens = json.loads(response.read().decode())

            if not validate_token_data(new_tokens):
                logger.error("Invalid token response from server")
                return None

            with open(TOKEN_FILE, 'w') as f:
                json.dump(new_tokens, f, indent=2)
            os.chmod(TOKEN_FILE, 0o600)

            logger.info("Token refreshed successfully")
            return new_tokens.get('access_token')

    except HTTPError as e:
        if e.code == 401:
            logger.error("Authentication failed - credentials may be invalid")
        else:
            logger.error(f"Token refresh failed: HTTP {e.code}")
        return None
    except (URLError, TimeoutError) as e:
        logger.error(f"Network error during token refresh: {e}")
        return None
    except json.JSONDecodeError:
        logger.error("Invalid response from token server")
        return None

def validate_webhook_url(url: str) -> bool:
    """Validate webhook URL format"""
    if not url:
        return False
    allowed_patterns = [
        r'^https://discord\.com/api/webhooks/\d+/[\w-]+$',
        r'^https://hooks\.slack\.com/services/[\w/]+$'
    ]
    return any(re.match(pattern, url) for pattern in allowed_patterns)

def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert to float"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert to int"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def fetch_activities(access_token: str, days: int = 28) -> List[Dict]:
    """Fetch activities with security checks, timeouts, and retry"""
    after = int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp())
    url = f'https://www.strava.com/api/v3/athlete/activities?after={after}&per_page=100'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'User-Agent': 'TrainingCoach/2.0'
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                activities = json.loads(response.read().decode())

                if not isinstance(activities, list):
                    logger.error("Invalid API response format")
                    return []

                # Validate each activity
                validated = []
                for a in activities:
                    if not isinstance(a, dict):
                        continue
                    date_str = a.get('start_date', '')
                    if date_str and re.match(r'^\d{4}-\d{2}-\d{2}T', date_str):
                        validated.append(a)

                logger.debug(f"Fetched {len(activities)} activities, {len(validated)} valid")
                return validated

        except HTTPError as e:
            if e.code == 401:
                logger.error("Authentication expired")
                return []
            logger.warning(f"HTTP error (attempt {attempt + 1}): {e.code}")
            if attempt == max_retries - 1:
                return []
        except (URLError, TimeoutError) as e:
            logger.error(f"Network error (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                return []
        except json.JSONDecodeError:
            logger.error("Invalid JSON response from API")
            return []

    return []

# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================

def calculate_weeks(activities: List[Dict]) -> List[Dict]:
    """Calculate weekly stats for last 4 weeks with input validation"""
    weeks = []
    now = datetime.now(timezone.utc)

    for i in range(4):
        week_start = now - timedelta(days=now.weekday() + (i * 7))
        week_end = week_start + timedelta(days=7)

        week_acts = []
        for a in activities:
            try:
                date_str = a.get('start_date', '')
                if not date_str:
                    continue
                act_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                if week_start <= act_date < week_end:
                    week_acts.append(a)
            except (ValueError, TypeError):
                continue

        miles = sum(safe_float(a.get('distance'), 0) for a in week_acts) / 1609.34
        time_mins = sum(safe_float(a.get('moving_time'), 0) for a in week_acts) / 60
        runs = len([a for a in week_acts if a.get('type') == 'Run'])

        weeks.append({
            'label': f"Week {-i if i > 0 else 'This'}",
            'miles': miles,
            'time': time_mins,
            'runs': runs
        })

    return list(reversed(weeks))

def analyze_intensity_distribution(activities: List[Dict]) -> Optional[Dict]:
    """Calculate easy/moderate/hard distribution with safe type handling"""
    runs = [a for a in activities if a.get('type') == 'Run']
    if not runs:
        return None

    easy = 0
    moderate = 0
    hard = 0
    total = len(runs)

    for r in runs:
        avg_hr = safe_int(r.get('average_heartrate'), 0)
        if avg_hr <= 0:
            easy += 1  # No HR data defaults to easy
        elif avg_hr < EASY_HR_CEILING - 10:
            easy += 1
        elif avg_hr <= EASY_HR_CEILING + 10:
            moderate += 1
        else:
            hard += 1

    return {
        'easy_pct': (easy / total) * 100,
        'moderate_pct': (moderate / total) * 100,
        'hard_pct': (hard / total) * 100
    }

def calculate_acwr(weeks: List[Dict]) -> Optional[float]:
    """Calculate Acute:Chronic Workload Ratio (Gabbett, 2016).
    ACWR > 1.5 = high injury risk. 0.8-1.3 = sweet spot."""
    if not weeks:
        return None
    acute = weeks[-1]['miles']  # this week
    chronic = sum(w['miles'] for w in weeks) / len(weeks)
    if chronic <= 0:
        return None
    return acute / chronic

def get_acwr_zone(acwr: Optional[float]) -> str:
    """Interpret ACWR value based on Gabbett (2016) risk zones"""
    if acwr is None:
        return "Unknown"
    if acwr < 0.8:
        return "Undertraining"
    if acwr <= 1.3:
        return "Sweet spot"
    if acwr <= 1.5:
        return "Caution"
    return "High risk"

def generate_report(activities: List[Dict]) -> Dict:
    """Generate weekly report data with ACWR analysis"""
    weeks = calculate_weeks(activities)
    intensity = analyze_intensity_distribution(activities)

    current_week = weeks[-1] if weeks else {'miles': 0.0, 'runs': 0}
    prev_week = weeks[-2] if len(weeks) > 1 else {'miles': 0.0}

    trend = "stable"
    change_pct = 0.0
    if prev_week['miles'] > 0:
        change_pct = ((current_week['miles'] - prev_week['miles']) / prev_week['miles']) * 100
        if change_pct > 10:
            trend = "increasing"
        elif change_pct < -10:
            trend = "decreasing"

    acwr = calculate_acwr(weeks)
    acwr_zone = get_acwr_zone(acwr)

    eight_twenty_ok = intensity is not None and intensity['easy_pct'] >= 75

    return {
        'week_miles': current_week['miles'],
        'week_runs': current_week['runs'],
        'trend': trend,
        'change_pct': change_pct,
        'four_week_total': sum(w['miles'] for w in weeks),
        'four_week_avg': sum(w['miles'] for w in weeks) / len(weeks) if weeks else 0,
        'intensity': intensity,
        'eight_twenty_ok': eight_twenty_ok,
        'weekly_data': weeks,
        'acwr': acwr,
        'acwr_zone': acwr_zone
    }

# ============================================================================
# SECURE NOTIFICATIONS
# ============================================================================

def send_discord_report(report: Dict, webhook_url: str) -> bool:
    """Send weekly report to Discord with validation"""
    if not validate_webhook_url(webhook_url):
        logger.error("Invalid Discord webhook URL format")
        return False

    change_str = f" ({report['change_pct']:+.0f}%)" if report.get('change_pct') else ""
    fields = [
        {"name": "This Week", "value": f"{report['week_miles']:.1f} mi | {report['week_runs']} runs{change_str}", "inline": True},
        {"name": "Trend", "value": str(report['trend'])[:100], "inline": True},
        {"name": "4-Week Avg", "value": f"{report['four_week_avg']:.1f} mi/wk", "inline": True}
    ]

    # ACWR (Gabbett, 2016)
    acwr = report.get('acwr')
    if acwr is not None:
        zone = report.get('acwr_zone', 'Unknown')
        fields.append({
            "name": "Workload Ratio (ACWR)",
            "value": f"{acwr:.2f} — {zone}",
            "inline": True
        })

    intensity = report.get('intensity')
    if intensity:
        fields.append({
            "name": "80/20 Check (Seiler, 2010)",
            "value": f"Easy: {intensity['easy_pct']:.0f}% | Moderate: {intensity['moderate_pct']:.0f}% | Hard: {intensity['hard_pct']:.0f}%",
            "inline": False
        })

        if report['eight_twenty_ok']:
            fields.append({"name": "Status", "value": "Great polarization — this is how elite athletes train (Stoggl & Sperlich, 2014).", "inline": False})
        else:
            fields.append({"name": "Tip", "value": "Aim for 80% easy runs. Polarized training builds a stronger aerobic base than moderate-intensity training.", "inline": False})

    trend_text = " | ".join([f"{w['label']}: {w['miles']:.1f}mi" for w in report['weekly_data']])
    fields.append({"name": "4-Week Trend", "value": trend_text[:1000], "inline": False})

    embed = {
        "title": "Weekly Training Report",
        "color": 0xFC4C02 if report['eight_twenty_ok'] else 0xFFA500,
        "fields": fields,
        "footer": {"text": "Consistency > Intensity"},
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    payload = {"embeds": [embed]}

    req = urllib.request.Request(
        webhook_url,
        data=json.dumps(payload).encode(),
        headers={
            'Content-Type': 'application/json',
            'User-Agent': 'TrainingCoach/2.0'
        },
        method='POST'
    )

    try:
        with urllib.request.urlopen(req, timeout=30):
            logger.info("Weekly report sent to Discord")
            return True
    except HTTPError as e:
        logger.error(f"Discord report failed: HTTP {e.code}")
        return False
    except (URLError, TimeoutError) as e:
        logger.error(f"Discord network error: {e}")
        return False

def send_slack_report(report: Dict, webhook_url: str) -> bool:
    """Send weekly report to Slack with validation"""
    if not validate_webhook_url(webhook_url):
        logger.error("Invalid Slack webhook URL format")
        return False

    intensity = report.get('intensity')

    change_str = f" ({report['change_pct']:+.0f}%)" if report.get('change_pct') else ""
    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "Weekly Training Report"}
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*This Week*\n{report['week_miles']:.1f} mi | {report['week_runs']} runs{change_str}"},
                {"type": "mrkdwn", "text": f"*Trend*\n{report['trend']}"},
                {"type": "mrkdwn", "text": f"*4-Week Avg*\n{report['four_week_avg']:.1f} mi/wk"}
            ]
        }
    ]

    # ACWR section
    acwr = report.get('acwr')
    if acwr is not None:
        zone = report.get('acwr_zone', 'Unknown')
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Workload Ratio (ACWR):* {acwr:.2f} — {zone}\n_Gabbett (2016): 0.8-1.3 is the sweet spot, >1.5 = high injury risk_"
            }
        })

    if intensity:
        status = "Great polarization (Stoggl & Sperlich, 2014)." if report['eight_twenty_ok'] else "Aim for 80% easy runs to build aerobic base."
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*80/20 Check (Seiler, 2010):* Easy {intensity['easy_pct']:.0f}% | Moderate {intensity['moderate_pct']:.0f}% | Hard {intensity['hard_pct']:.0f}%\n{status}"
            }
        })

    trend_text = " | ".join([f"{w['label']}: {w['miles']:.1f}mi" for w in report['weekly_data']])
    blocks.append({
        "type": "context",
        "elements": [{"type": "mrkdwn", "text": f"4-Week Trend: {trend_text}"}]
    })

    payload = {"blocks": blocks}

    req = urllib.request.Request(
        webhook_url,
        data=json.dumps(payload).encode(),
        headers={
            'Content-Type': 'application/json',
            'User-Agent': 'TrainingCoach/2.0'
        },
        method='POST'
    )

    try:
        with urllib.request.urlopen(req, timeout=30):
            logger.info("Weekly report sent to Slack")
            return True
    except HTTPError as e:
        logger.error(f"Slack report failed: HTTP {e.code}")
        return False
    except (URLError, TimeoutError) as e:
        logger.error(f"Slack network error: {e}")
        return False

# ============================================================================
# MAIN
# ============================================================================

def main() -> int:
    """Main entry point"""
    logger.info(f"Generating Weekly Report - {datetime.now().strftime('%Y-%m-%d')}")
    logger.info("=" * 50)

    access_token = load_tokens()
    if not access_token:
        logger.error("No Strava tokens. Run: python3 scripts/auth.py")
        return 1

    webhook_url = SLACK_WEBHOOK_URL if NOTIFICATION_CHANNEL == 'slack' else DISCORD_WEBHOOK_URL
    if not webhook_url:
        logger.error(f"No webhook URL set. Set {'SLACK_WEBHOOK_URL' if NOTIFICATION_CHANNEL == 'slack' else 'DISCORD_WEBHOOK_URL'} environment variable.")
        return 1

    if not validate_webhook_url(webhook_url):
        logger.error("Invalid webhook URL format")
        return 1

    activities = fetch_activities(access_token)
    if not activities:
        logger.info("No activities found.")
        return 0

    logger.info(f"Found {len(activities)} activities")

    report = generate_report(activities)

    if NOTIFICATION_CHANNEL == 'slack':
        send_slack_report(report, webhook_url)
    else:
        send_discord_report(report, webhook_url)

    logger.info("=" * 50)
    return 0

if __name__ == '__main__':
    sys.exit(main())
