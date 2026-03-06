#!/usr/bin/env python3
"""
Training Coach - Daily check for injury risks and training insights
Focuses on 80/20 principle and sustainable training

Security-hardened for ClawHub publication:
- No hardcoded secrets
- Input validation on all external data
- Safe error handling (no data leakage)
- Rate limiting on notifications
- Secure temp file handling
"""

import os
import sys
import json
import urllib.request
import logging
import re
import time
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, List, Any, Tuple
from urllib.error import HTTPError, URLError

# ============================================================================
# SECURE CONFIGURATION
# ============================================================================

# Paths - use XDG directories or secure temp
def get_config_dir() -> str:
    """Get secure config directory"""
    xdg_config = os.environ.get('XDG_CONFIG_HOME')
    if xdg_config:
        return os.path.join(xdg_config, 'strava-training-coach')
    return os.path.expanduser('~/.config/strava-training-coach')

CONFIG_DIR = get_config_dir()
TOKEN_FILE = os.path.join(CONFIG_DIR, 'strava_tokens.json')
STATE_FILE = os.path.join(CONFIG_DIR, 'coach_state.json')
LOG_FILE = os.path.join(CONFIG_DIR, 'coach.log')

# Create config dir if needed
os.makedirs(CONFIG_DIR, mode=0o700, exist_ok=True)

# User-configurable thresholds (with validation)
def get_env_float(name: str, default: float, min_val: float, max_val: float) -> float:
    """Get validated float from environment"""
    try:
        val = float(os.environ.get(name, default))
        return max(min_val, min(max_val, val))
    except (ValueError, TypeError):
        return default

def get_env_int(name: str, default: int, min_val: int, max_val: int) -> int:
    """Get validated int from environment"""
    try:
        val = int(os.environ.get(name, default))
        return max(min_val, min(max_val, val))
    except (ValueError, TypeError):
        return default

MAX_WEEKLY_JUMP = get_env_float('MAX_WEEKLY_MILEAGE_JUMP', 30.0, 5.0, 100.0)
MAX_HARD_PERCENT = get_env_float('MAX_HARD_DAY_PERCENTAGE', 25.0, 5.0, 100.0)
EASY_HR_CEILING = get_env_int('MIN_EASY_RUN_HEART_RATE', 145, 100, 200)
PLANNED_REST_DAYS = get_env_int('PLANNED_REST_DAYS', 2, 0, 7)

NOTIFICATION_CHANNEL = os.environ.get('NOTIFICATION_CHANNEL', 'discord').lower()
if NOTIFICATION_CHANNEL not in ('discord', 'slack'):
    NOTIFICATION_CHANNEL = 'discord'

VERBOSE = os.environ.get('VERBOSE', '').lower() in ('true', '1', 'yes')

# Oura integration (disabled by default for security)
OURA_ENABLED = os.environ.get('OURA_ENABLED', '').lower() in ('true', '1', 'yes')
OURA_SLEEP_THRESHOLD = get_env_int('OURA_SLEEP_THRESHOLD', 70, 0, 100)
OURA_READINESS_THRESHOLD = get_env_int('OURA_READINESS_THRESHOLD', 70, 0, 100)

# Webhook URL - MUST be set via environment (no defaults)
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL', '')
SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL', '')

# Rate limiting
MIN_ALERT_INTERVAL_SECONDS = 3600  # Max 1 alert per hour per type
last_alert_times: Dict[str, float] = {}

# ============================================================================
# SECURE LOGGING
# ============================================================================

class SensitiveDataFilter(logging.Filter):
    """Filter out sensitive data from logs"""
    REDACTION_PATTERNS = [
        # Hex tokens (mixed case) — covers Strava, OAuth, and most API tokens
        (re.compile(r'[a-fA-F0-9]{20,}'), '[REDACTED]'),
        # Bearer tokens in authorization headers
        (re.compile(r'Bearer\s+\S+', re.IGNORECASE), 'Bearer [REDACTED]'),
        # Base64-ish tokens (alphanumeric + common token chars, 20+ chars)
        (re.compile(r'[A-Za-z0-9_\-]{20,}'), '[REDACTED]'),
        # Discord webhook URLs
        (re.compile(r'webhooks/[0-9]+/[a-zA-Z0-9_\-]+'), 'webhooks/[REDACTED]'),
        # Slack webhook URLs
        (re.compile(r'hooks\.slack\.com/services/[A-Za-z0-9/]+'), 'hooks.slack.com/services/[REDACTED]'),
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        if record.msg and isinstance(record.msg, str):
            for pattern, replacement in self.REDACTION_PATTERNS:
                record.msg = pattern.sub(replacement, record.msg)
        return True

def setup_logging() -> logging.Logger:
    """Configure secure logging"""
    logger = logging.getLogger('training_coach')
    logger.setLevel(logging.DEBUG if VERBOSE else logging.INFO)
    
    # Clear existing handlers
    logger.handlers = []
    
    # File handler
    try:
        file_handler = logging.FileHandler(LOG_FILE, mode='a')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        file_handler.addFilter(SensitiveDataFilter())
        logger.addHandler(file_handler)
    except (IOError, OSError) as e:
        print(f"Warning: Could not create log file: {e}", file=sys.stderr)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_formatter)
    console_handler.addFilter(SensitiveDataFilter())
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logging()

# ============================================================================
# SECURE STATE MANAGEMENT
# ============================================================================

class CoachState:
    """Persist state across runs securely"""
    
    def __init__(self):
        self.last_run: Optional[str] = None
        self.last_alert_time: Optional[str] = None
        self.alert_count_24h: int = 0
        self.weekly_mileage_history: List[Dict] = []
    
    @classmethod
    def load(cls) -> 'CoachState':
        """Load state from file securely"""
        try:
            with open(STATE_FILE, 'r') as f:
                data = json.load(f)
                state = cls()
                # Only load expected fields
                state.last_run = data.get('last_run')
                state.last_alert_time = data.get('last_alert_time')
                state.alert_count_24h = int(data.get('alert_count_24h', 0))
                state.weekly_mileage_history = data.get('weekly_mileage_history', [])
                return state
        except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError):
            return cls()
    
    def save(self):
        """Save state to file securely"""
        try:
            with open(STATE_FILE, 'w') as f:
                json.dump(self.__dict__, f, indent=2, default=str)
            os.chmod(STATE_FILE, 0o600)
        except (IOError, OSError) as e:
            logger.error(f"Failed to save state: {e}")
    
    def should_alert(self, alert_type: str) -> bool:
        """Check if enough time has passed since last alert"""
        now = time.time()
        last_time = last_alert_times.get(alert_type, 0)
        if now - last_time < MIN_ALERT_INTERVAL_SECONDS:
            logger.debug(f"Rate limiting {alert_type} alert")
            return False
        last_alert_times[alert_type] = now
        return True

# ============================================================================
# SECURE API CLIENT
# ============================================================================

def validate_token_data(data: Dict) -> bool:
    """Validate token data structure"""
    if not isinstance(data, dict):
        return False
    if 'access_token' not in data or not isinstance(data['access_token'], str):
        return False
    if len(data.get('access_token', '')) < 10:
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
        
        # Check expiration with buffer
        if expires_at and expires_at < (datetime.now().timestamp() + 300):
            logger.info("Token expired, refreshing...")
            if refresh_token:
                return refresh_access_token(refresh_token)
            return None
        
        return access_token
        
    except FileNotFoundError:
        logger.error("Token file not found. Run auth.py first.")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Invalid token file: {e}")
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
        logger.error("STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET required")
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
            
            # Securely save new tokens
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


def fetch_activities(access_token: str, days: int = 14) -> List[Dict]:
    """Fetch activities with security checks"""
    url = 'https://www.strava.com/api/v3/athlete/activities?per_page=50'
    
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
                
                # Client-side filtering with validation
                cutoff = datetime.now(timezone.utc) - timedelta(days=days)
                filtered = []
                
                for a in activities:
                    if not isinstance(a, dict):
                        continue
                    try:
                        date_str = a.get('start_date', '')
                        # Validate date format
                        if not re.match(r'^\d{4}-\d{2}-\d{2}T', date_str):
                            continue
                        act_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        if act_date > cutoff:
                            filtered.append(a)
                    except (ValueError, TypeError):
                        continue
                
                logger.debug(f"Fetched {len(activities)} activities, {len(filtered)} recent")
                return filtered
                
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
# SECURE ANALYSIS FUNCTIONS
# ============================================================================

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


def calculate_acwr(activities: List[Dict]) -> Optional[float]:
    """Calculate Acute:Chronic Workload Ratio (Gabbett, 2016).
    Acute = this week's load. Chronic = 4-week rolling average.
    ACWR > 1.5 = high injury risk zone."""
    now = datetime.now(timezone.utc)
    weekly_loads = []

    for week_offset in range(4):
        week_start = now - timedelta(days=now.weekday() + (week_offset * 7))
        week_end = week_start + timedelta(days=7)
        week_miles = 0.0

        for a in activities:
            try:
                date_str = a.get('start_date', '')
                if not date_str:
                    continue
                act_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                if week_start <= act_date < week_end:
                    week_miles += safe_float(a.get('distance'), 0) / 1609.34
            except (ValueError, TypeError):
                continue

        weekly_loads.append(week_miles)

    acute = weekly_loads[0]  # this week
    chronic = sum(weekly_loads) / len(weekly_loads) if weekly_loads else 0

    if chronic <= 0:
        return None
    return acute / chronic


def analyze_weekly_load(activities: List[Dict]) -> Tuple[Optional[Dict], float]:
    """Check for dangerous mileage spikes using ACWR and week-over-week change"""
    if not activities:
        return None, 0.0

    now = datetime.now(timezone.utc)
    week_start = now - timedelta(days=now.weekday())
    last_week_start = week_start - timedelta(days=7)

    this_week: List[Dict] = []
    last_week: List[Dict] = []

    for a in activities:
        try:
            date_str = a.get('start_date', '')
            if not date_str:
                continue
            act_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            if act_date >= week_start:
                this_week.append(a)
            elif act_date >= last_week_start:
                last_week.append(a)
        except (ValueError, TypeError):
            continue

    this_miles = sum(safe_float(a.get('distance'), 0) for a in this_week) / 1609.34
    last_miles = sum(safe_float(a.get('distance'), 0) for a in last_week) / 1609.34

    logger.debug(f"This week: {this_miles:.1f} mi, Last week: {last_miles:.1f} mi")

    if last_miles == 0:
        return None, this_miles

    change_pct = ((this_miles - last_miles) / last_miles) * 100
    acwr = calculate_acwr(activities)
    acwr_str = f" ACWR: {acwr:.2f}." if acwr else ""

    if change_pct > MAX_WEEKLY_JUMP:
        severity = 'high' if change_pct > 50 or (acwr and acwr > 1.5) else 'medium'
        rec = "Consider an easy week or cut next week's mileage by 20%."
        if acwr and acwr > 1.5:
            rec = (
                "Your acute:chronic workload ratio is in the high-risk zone (>1.5). "
                "Research by Gabbett (2016) shows injury risk spikes here. "
                "Reduce next week's volume by 20-30% and prioritize easy runs."
            )
        return {
            'type': 'load_spike',
            'severity': severity,
            'message': (
                f"Weekly mileage up {change_pct:.0f}% ({last_miles:.1f} -> {this_miles:.1f} mi).{acwr_str} "
                f"Nielsen et al. (2014) found >30% weekly increases significantly raise injury risk."
            ),
            'recommendation': rec
        }, this_miles

    return None, this_miles


def analyze_intensity(activities: List[Dict]) -> Optional[Dict]:
    """Check if easy days are actually easy"""
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    
    recent = []
    for a in activities:
        try:
            date_str = a.get('start_date', '')
            if not date_str:
                continue
            act_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            if act_date > cutoff:
                recent.append(a)
        except (ValueError, TypeError):
            continue
    
    if len(recent) < 3:
        logger.debug(f"Not enough activities for intensity analysis")
        return None
    
    hard_runs = 0
    total_runs = 0
    runs_with_hr = 0
    
    for a in recent:
        if a.get('type') == 'Run':
            total_runs += 1
            avg_hr = safe_int(a.get('average_heartrate'), 0)
            if avg_hr > 0:
                runs_with_hr += 1
                if avg_hr > EASY_HR_CEILING:
                    hard_runs += 1
    
    if total_runs == 0 or runs_with_hr == 0:
        return None
    
    hard_pct = (hard_runs / runs_with_hr) * 100
    logger.debug(f"Hard runs: {hard_pct:.0f}%")
    
    if hard_pct > MAX_HARD_PERCENT:
        return {
            'type': 'intensity_imbalance',
            'severity': 'medium',
            'message': (
                f"{hard_pct:.0f}% of runs were moderate/high effort (HR >{EASY_HR_CEILING}). "
                f"Seiler (2010) found elite athletes keep ~80% of sessions below the first ventilatory threshold."
            ),
            'recommendation': (
                "Easy days should feel conversational. Stoggl & Sperlich (2014) showed "
                "polarized training (80% easy / 20% hard) produces better VO2max and "
                "lactate threshold gains than moderate-intensity training."
            )
        }

    return None


def check_recovery_gap(activities: List[Dict], state: CoachState) -> Optional[Dict]:
    """Check for too many rest days"""
    if not activities:
        return None
    
    try:
        date_str = activities[0].get('start_date', '')
        if not date_str:
            return None
        last_activity = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except (ValueError, TypeError):
        logger.error("Invalid activity date format")
        return None
    
    now = datetime.now(timezone.utc)
    days_since = (now - last_activity).days
    
    logger.debug(f"Days since last activity: {days_since}")
    
    if days_since < PLANNED_REST_DAYS:
        return None
    
    # Check for planned rest
    recent_consistency = 0
    for a in activities[:7]:
        try:
            date_str = a.get('start_date', '')
            if not date_str:
                continue
            act_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            if (now - act_date).days <= 10:
                recent_consistency += 1
        except (ValueError, TypeError):
            continue
    
    is_planned = recent_consistency >= 5 and days_since <= 5
    
    if is_planned:
        logger.debug("Gap appears to be planned rest")
        return None
    
    if days_since >= 5:
        return {
            'type': 'recovery_gap',
            'severity': 'low',
            'message': (
                f"{days_since} days since last activity. "
                f"Mujika & Padilla (2000) found VO2max begins declining after ~10 days of inactivity."
            ),
            'recommendation': (
                "A gentle 20-min walk or easy jog can maintain adaptations without adding fatigue. "
                "Nieman (2000) showed moderate exercise also supports immune function."
            )
        }
    
    return None


def check_consistency_streak(activities: List[Dict]) -> Optional[Dict]:
    """Check for streak milestones"""
    if not activities:
        return None
    
    streak = 0
    now = datetime.now(timezone.utc)
    
    for i, a in enumerate(activities):
        try:
            date_str = a.get('start_date', '')
            if not date_str:
                continue
            act_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            expected_date = now - timedelta(days=i)
            
            if abs((act_date.date() - expected_date.date()).days) <= 1:
                streak += 1
            else:
                break
        except (ValueError, TypeError):
            continue
    
    logger.debug(f"Current streak: {streak} days")
    
    milestones = [7, 14, 30, 60, 100]
    for milestone in milestones:
        if streak == milestone:
            return {
                'type': 'streak_milestone',
                'severity': 'positive',
                'message': f"🔥 {milestone}-Day Streak!",
                'recommendation': "Consistency beats intensity. Well done."
            }
    
    return None


# ============================================================================
# OURA INTEGRATION (SECURE)
# ============================================================================

def get_oura_token() -> Optional[str]:
    """Load Oura token securely"""
    oura_config_path = os.path.expanduser('~/.config/oura-cli/config.json')
    try:
        with open(oura_config_path, 'r') as f:
            config = json.load(f)
            token = config.get('access_token', '')
            if len(token) < 10:
                return None
            return token
    except (FileNotFoundError, json.JSONDecodeError, IOError, OSError):
        return None


def fetch_oura_data(endpoint: str, start_date: str, end_date: Optional[str] = None) -> Optional[List[Dict]]:
    """Fetch data from Oura API securely"""
    if not OURA_ENABLED:
        return None
    
    access_token = get_oura_token()
    if not access_token:
        logger.debug("Oura token not available")
        return None
    
    url = f'https://api.ouraring.com/v2/usercollection/{endpoint}'
    params = [f'start_date={start_date}']
    if end_date:
        params.append(f'end_date={end_date}')
    full_url = f"{url}?{'&'.join(params)}"
    
    req = urllib.request.Request(
        full_url,
        headers={
            'Authorization': f'Bearer {access_token}',
            'User-Agent': 'TrainingCoach/2.0'
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())
            result = data.get('data', [])
            return result if isinstance(result, list) else None
    except HTTPError as e:
        if e.code == 401:
            logger.warning("Oura authentication expired")
        else:
            logger.debug(f"Oura API error: {e.code}")
        return None
    except (URLError, TimeoutError, json.JSONDecodeError) as e:
        logger.debug(f"Oura request failed: {e}")
        return None


def check_oura_sleep(date: str, state: CoachState) -> Optional[Dict]:
    """Check sleep score from Oura"""
    if not state.should_alert('sleep'):
        return None
    
    sleep_data = fetch_oura_data('sleep', date, date)
    if not sleep_data:
        return None
    
    try:
        latest = sleep_data[0]
        score = safe_int(latest.get('score'), 0)
        
        if 0 < score < OURA_SLEEP_THRESHOLD:
            return {
                'type': 'poor_sleep',
                'severity': 'medium',
                'message': f"😴 Poor sleep last night (score: {score}/100).",
                'recommendation': "Consider an easy day or extra rest. Poor sleep increases injury risk."
            }
    except (IndexError, TypeError):
        pass
    
    return None


def check_oura_readiness(date: str, state: CoachState) -> Optional[Dict]:
    """Check readiness score from Oura"""
    if not state.should_alert('readiness'):
        return None
    
    readiness_data = fetch_oura_data('readiness', date, date)
    if not readiness_data:
        return None
    
    try:
        latest = readiness_data[0]
        score = safe_int(latest.get('score'), 0)
        
        if 0 < score < OURA_READINESS_THRESHOLD:
            return {
                'type': 'low_readiness',
                'severity': 'medium',
                'message': f"📉 Low readiness this morning (score: {score}/100).",
                'recommendation': "Your body needs recovery. Skip hard workouts today."
            }
    except (IndexError, TypeError):
        pass
    
    return None


# ============================================================================
# SECURE NOTIFICATIONS
# ============================================================================

def validate_webhook_url(url: str) -> bool:
    """Validate webhook URL format"""
    if not url:
        return False
    # Only allow Discord/Slack webhook patterns
    allowed_patterns = [
        r'^https://discord\.com/api/webhooks/\d+/[\w-]+$',
        r'^https://hooks\.slack\.com/services/[\w/]+$'
    ]
    for pattern in allowed_patterns:
        if re.match(pattern, url):
            return True
    return False


def send_discord_alert(alert: Dict, webhook_url: str) -> bool:
    """Send alert to Discord securely"""
    if not validate_webhook_url(webhook_url):
        logger.error("Invalid Discord webhook URL format")
        return False
    
    colors = {
        'high': 0xFF4444,
        'medium': 0xFFA500,
        'low': 0xFFFF00,
        'positive': 0x44FF44
    }
    
    # Sanitize message content
    message = str(alert.get('message', ''))[:1000]
    recommendation = str(alert.get('recommendation', ''))[:1000]
    
    title = "🎉 Achievement" if alert.get('severity') == 'positive' else "🏃 Training Coach Alert"
    
    embed = {
        "title": title,
        "color": colors.get(alert.get('severity'), 0x888888),
        "fields": [
            {"name": "Issue", "value": message, "inline": False},
            {"name": "Recommendation", "value": recommendation, "inline": False}
        ],
        "footer": {"text": "Strava + Oura | 80/20 Rule"},
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
            logger.info(f"Discord alert sent: {alert.get('type')}")
            return True
    except HTTPError as e:
        logger.error(f"Discord alert failed: HTTP {e.code}")
        return False
    except (URLError, TimeoutError) as e:
        logger.error(f"Discord network error: {e}")
        return False


def send_slack_alert(alert: Dict, webhook_url: str) -> bool:
    """Send alert to Slack securely"""
    if not validate_webhook_url(webhook_url):
        logger.error("Invalid Slack webhook URL format")
        return False
    
    emoji = {'high': '🚨', 'medium': '⚠️', 'low': '💡', 'positive': '🎉'}
    
    message = str(alert.get('message', ''))[:3000]
    recommendation = str(alert.get('recommendation', ''))[:3000]
    
    payload = {
        "text": f"{emoji.get(alert.get('severity'), 'ℹ️')} *Training Coach*",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{message}*\n\n{recommendation}"
                }
            },
            {
                "type": "context",
                "elements": [
                    {"type": "mrkdwn", "text": "Strava + Oura | 80/20 Rule"}
                ]
            }
        ]
    }
    
    req = urllib.request.Request(
        webhook_url,
        data=json.dumps(payload).encode(),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30):
            logger.info(f"Slack alert sent: {alert.get('type')}")
            return True
    except HTTPError as e:
        logger.error(f"Slack alert failed: HTTP {e.code}")
        return False
    except (URLError, TimeoutError) as e:
        logger.error(f"Slack network error: {e}")
        return False


# ============================================================================
# MAIN
# ============================================================================

def main() -> int:
    """Main entry point"""
    logger.info(f"🏃 Training Coach Check - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    logger.info("=" * 50)
    
    # Load state
    state = CoachState.load()
    state.last_run = datetime.now(timezone.utc).isoformat()
    
    # Load tokens
    access_token = load_tokens()
    if not access_token:
        logger.error("❌ No Strava tokens. Run: python3 scripts/auth.py")
        return 1
    
    # Get webhook
    webhook_url = DISCORD_WEBHOOK_URL if NOTIFICATION_CHANNEL == 'discord' else SLACK_WEBHOOK_URL
    if not webhook_url:
        logger.error(f"❌ No webhook URL set. Set {'DISCORD_WEBHOOK_URL' if NOTIFICATION_CHANNEL == 'discord' else 'SLACK_WEBHOOK_URL'} environment variable.")
        return 1
    
    if not validate_webhook_url(webhook_url):
        logger.error("❌ Invalid webhook URL format")
        return 1
    
    # Fetch activities
    activities = fetch_activities(access_token)
    if not activities:
        logger.info("No recent activities found.")
        state.save()
        return 0
    
    logger.info(f"Found {len(activities)} recent activities\n")
    
    # Run checks
    alerts = []
    
    # Weekly load
    load_alert, weekly_miles = analyze_weekly_load(activities)
    if load_alert and state.should_alert('load'):
        alerts.append(load_alert)
        logger.info(f"⚠️  Load spike: {weekly_miles:.1f} mi")
    else:
        logger.info(f"✅ Weekly load: {weekly_miles:.1f} mi")
    
    # Intensity
    intensity_alert = analyze_intensity(activities)
    if intensity_alert and state.should_alert('intensity'):
        alerts.append(intensity_alert)
        logger.info(f"⚠️  Intensity imbalance")
    else:
        logger.info("✅ Intensity OK")
    
    # Recovery gap
    recovery_alert = check_recovery_gap(activities, state)
    if recovery_alert and state.should_alert('recovery'):
        alerts.append(recovery_alert)
        logger.info(f"💡 Recovery gap")
    
    # Streak
    streak_alert = check_consistency_streak(activities)
    if streak_alert and state.should_alert('streak'):
        alerts.append(streak_alert)
        logger.info(f"🎉 Streak milestone")
    
    # Oura checks
    if OURA_ENABLED:
        logger.info("\n📊 Oura checks...")
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        
        sleep_alert = check_oura_sleep(today, state)
        if sleep_alert:
            alerts.append(sleep_alert)
            logger.info(f"😴 Sleep alert")
        
        readiness_alert = check_oura_readiness(today, state)
        if readiness_alert:
            alerts.append(readiness_alert)
            logger.info(f"📉 Readiness alert")
    
    # Send alerts
    if alerts:
        logger.info(f"\n📤 Sending {len(alerts)} alert(s)...")
        for alert in alerts:
            if NOTIFICATION_CHANNEL == 'slack':
                send_slack_alert(alert, webhook_url)
            else:
                send_discord_alert(alert, webhook_url)
        state.last_alert_time = datetime.now(timezone.utc).isoformat()
    else:
        logger.info("\n✅ All checks passed. No alerts.")
    
    state.save()
    logger.info(f"\n{'=' * 50}\n")
    return 0


if __name__ == '__main__':
    sys.exit(main())
