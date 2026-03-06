#!/bin/bash
# Proactive Claw — One-time setup
# Supports: Google Calendar API | Nextcloud CalDAV
#
# SECURITY NOTE: This script does NOT contact any remote server by default.
# - All packages are installed from PyPI via uv pip install (pip3 fallback).
# - If you have set clawhub_token in config.json, run scripts/optional/setup_clawhub_oauth.sh
#   separately (opt-in only) to fetch Google credentials via clawhub.ai.
# - No curl/wget. No eval of remote code. No sudo. No root.

set -e

SKILL_DIR="$HOME/.openclaw/workspace/skills/proactive-claw"
CONFIG="$SKILL_DIR/config.json"
CREDS="$SKILL_DIR/credentials.json"

echo "🦞 Proactive Claw Setup"
echo "========================"

# Check Python 3.8+
if ! command -v python3 &>/dev/null; then
  echo "❌ Python 3 not found. Please install Python 3.8+ first."
  exit 1
fi
PYTHON_VER=$(python3 -c "import sys; print(sys.version_info >= (3,8))")
if [ "$PYTHON_VER" != "True" ]; then
  echo "❌ Python 3.8+ required."
  exit 1
fi
echo "✅ Python 3 found"

# Detect backend from config
BACKEND="google"
if [ -f "$CONFIG" ]; then
  BACKEND=$(python3 -c "import json; d=json.load(open('$CONFIG')); print(d.get('calendar_backend','google'))" 2>/dev/null || echo "google")
fi
echo "📅 Calendar backend: $BACKEND"

# ── clawhub OAuth is OPT-IN ONLY ──────────────────────────────────────────────
# Remote credential provisioning is NOT part of the default flow.
# If you want to use clawhub.ai to obtain your Google credentials.json,
# run this separately AFTER reviewing it:
#   bash scripts/optional/setup_clawhub_oauth.sh
# This script does NOT contact clawhub.ai. All setup is local.

# Initialize config.json if missing
if [ ! -f "$CONFIG" ]; then
  echo ""
  echo "📝 Creating default config.json (safe defaults — all features OFF)..."
  cat > "$CONFIG" << 'EOF'
{
  "calendar_backend": "google",
  "max_autonomy_level": "confirm",
  "daemon_enabled": false,
  "proactivity_mode": "balanced",
  "pre_checkin_offset_default": "1 day",
  "pre_checkin_offset_same_day": "1 hour",
  "post_checkin_offset": "30 minutes",
  "conversation_threshold": 5,
  "calendar_threshold": 6,
  "feature_conversation": false,
  "feature_calendar": false,
  "feature_daemon": false,
  "feature_memory": false,
  "feature_conflicts": false,
  "feature_rules": false,
  "feature_intelligence_loop": false,
  "feature_policy_engine": false,
  "feature_orchestrator": false,
  "feature_energy": false,
  "feature_cal_editor": false,
  "feature_relationship": false,
  "feature_adaptive_notifications": false,
  "feature_proactivity_engine": false,
  "feature_interrupt_controller": false,
  "feature_explainability": false,
  "feature_health_check": false,
  "feature_simulation": false,
  "feature_export": false,
  "feature_behaviour_report": false,
  "feature_config_wizard": false,
  "feature_policy_conflict_detection": false,
  "feature_cross_skill": false,
  "feature_voice": false,
  "feature_team_awareness": false,
  "feature_llm_rater": false,
  "feature_telegram_notifications": false,
  "default_user_calendar": "",
  "timezone": "UTC",
  "user_email": "",
  "notes_destination": "local",
  "notes_path": "~/.openclaw/workspace/skills/proactive-claw/outcomes/",
  "scan_days_ahead": 7,
  "scan_cache_ttl_minutes": 30,
  "openclaw_cal_id": "",
  "action_cleanup_days": 30,
  "memory_decay_half_life_days": 90,
  "max_nudges_per_day": 12,
  "quiet_hours": {
    "weekdays": "22:00-07:00",
    "weekends": "21:00-09:00"
  },
  "clawhub_token": "",
  "nextcloud": {
    "url": "",
    "username": "",
    "password": "",
    "openclaw_calendar_url": ""
  }
}
EOF
  echo "✅ config.json created with safe defaults (all features OFF, max_autonomy_level: confirm)"
  echo "   → Edit config.json to set your timezone and user_email before continuing."
fi

mkdir -p "$SKILL_DIR/outcomes"

if [ "$BACKEND" = "nextcloud" ]; then
  echo ""
  echo "📦 Installing Nextcloud dependencies..."
  if command -v uv &>/dev/null; then
    uv pip install -q --upgrade caldav icalendar
  else
    pip3 install -q --upgrade caldav icalendar
  fi
  echo "✅ caldav + icalendar installed"
  echo ""
  echo "🔧 Nextcloud setup — editing config.json"
  echo "   Set: nextcloud.url, nextcloud.username, nextcloud.password"
  echo "   ⚠️  Use an app-specific password (not your account password)."
  echo "      Generate one at: your-nextcloud.com/settings/personal/security"
  echo "   Example URL: https://your-nextcloud.com"
  echo ""
  python3 - << 'PYEOF'
import json, sys
from pathlib import Path

SKILL_DIR = Path.home() / ".openclaw/workspace/skills/proactive-claw"
CONFIG_FILE = SKILL_DIR / "config.json"

with open(CONFIG_FILE) as f:
    config = json.load(f)

nc = config.get("nextcloud", {})
url = nc.get("url", "").strip()
username = nc.get("username", "").strip()
password = nc.get("password", "").strip()

if not all([url, username, password]):
    print("❌ Nextcloud credentials not set in config.json.")
    print("   Set nextcloud.url, nextcloud.username, nextcloud.password")
    sys.exit(1)

try:
    import caldav
    client = caldav.DAVClient(
        url=f"{url.rstrip('/')}/remote.php/dav",
        username=username,
        password=password,
    )
    principal = client.principal()
    calendars = principal.calendars()
    print(f"✅ Connected to Nextcloud. Found {len(calendars)} calendar(s).")

    # Find or create Action Calendar (check both old and new name for migration)
    openclaw_url = None
    for cal in calendars:
        if cal.name in ("Proactive Claw \u2014 Actions", "OpenClaw"):
            openclaw_url = str(cal.url)
            print(f"\u2705 Action Calendar exists: {openclaw_url}")
            break

    if not openclaw_url:
        new_cal = principal.make_calendar(name="Proactive Claw \u2014 Actions")
        openclaw_url = str(new_cal.url)
        print(f"\u2705 Action Calendar created: {openclaw_url}")

    config["openclaw_cal_id"] = openclaw_url
    config["nextcloud"]["openclaw_calendar_url"] = openclaw_url

    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    print("✅ openclaw_cal_id saved to config.json")
    print("\n🦞 Nextcloud setup complete!")

except Exception as e:
    print(f"❌ Nextcloud connection failed: {e}")
    sys.exit(1)
PYEOF

else
  # Google Calendar setup
  echo ""
  if [ ! -f "$CREDS" ]; then
    echo "❌ credentials.json not found at $CREDS"
    echo ""
    echo "To create it:"
    echo "  1. Go to https://console.cloud.google.com"
    echo "  2. Create project 'OpenClaw' → Enable Google Calendar API"
    echo "  3. Create OAuth 2.0 credentials (Desktop app)"
    echo "  4. Download and move: mv ~/Downloads/credentials.json $CREDS"
    echo ""
    exit 1
  fi
  echo "✅ credentials.json found"

  echo ""
  echo "📦 Installing Google Calendar dependencies..."
  if command -v uv &>/dev/null; then
    uv pip install -q --upgrade google-api-python-client google-auth-oauthlib google-auth-httplib2
  else
    pip3 install -q --upgrade google-api-python-client google-auth-oauthlib google-auth-httplib2
  fi
  echo "✅ Dependencies installed"

  echo ""
  echo "🔐 Authenticating with Google Calendar (browser will open)..."
  python3 - << 'PYEOF'
import json, sys
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SKILL_DIR = Path.home() / ".openclaw/workspace/skills/proactive-claw"
CREDS_FILE = SKILL_DIR / "credentials.json"
TOKEN_FILE = SKILL_DIR / "token.json"
CONFIG_FILE = SKILL_DIR / "config.json"
SCOPES = ["https://www.googleapis.com/auth/calendar"]

creds = None
if TOKEN_FILE.exists():
    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception:
            creds = None
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_FILE), SCOPES)
        creds = flow.run_local_server(port=0)
    with open(TOKEN_FILE, "w") as f:
        f.write(creds.to_json())

service = build("calendar", "v3", credentials=creds)

# Check if Action Calendar already exists (check both old and new name for migration)
calendars = service.calendarList().list().execute().get("items", [])
openclaw_id = None
for cal in calendars:
    if cal.get("summary") in ("Proactive Claw \u2014 Actions", "OpenClaw"):
        openclaw_id = cal["id"]
        print(f"\u2705 Action Calendar exists (id: {openclaw_id})")
        break

if not openclaw_id:
    cal = service.calendars().insert(body={"summary": "Proactive Claw \u2014 Actions"}).execute()
    openclaw_id = cal["id"]
    print(f"\u2705 Action Calendar created (id: {openclaw_id})")

# Save to config
with open(CONFIG_FILE) as f:
    config = json.load(f)
config["openclaw_cal_id"] = openclaw_id

# Try to get user email
try:
    profile = service.calendars().get(calendarId="primary").execute()
    email = profile.get("id", "")
    if email and not config.get("user_email"):
        config["user_email"] = email
        print(f"✅ user_email set to: {email}")
except Exception:
    pass

with open(CONFIG_FILE, "w") as f:
    json.dump(config, f, indent=2)
print("✅ OPENCLAW_CAL_ID saved to config.json")

# Verify by listing events
try:
    service.events().list(calendarId="primary", maxResults=1).execute()
    print("✅ Calendar API read verified")
except Exception as e:
    print(f"⚠️  Could not read primary calendar: {e}")

print("\n🦞 Google Calendar setup complete!")
PYEOF
fi

echo ""
echo "========================"
echo "✅ Setup complete."
echo ""
echo "Next steps:"
echo "  1. Test calendar access:  python3 scripts/scan_calendar.py"
echo "  2. Enable features:       python3 scripts/config_wizard.py"
echo "  3. Install background daemon (optional):"
echo "     bash scripts/install_daemon.sh"
echo ""
echo "All features default OFF — enable only what you need in config.json."
