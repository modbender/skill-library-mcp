#!/bin/bash
# ============================================================
# NOT USED BY DEFAULT SETUP — THIS IS AN OPTIONAL HELPER ONLY
# setup.sh does NOT call this script. Most users don't need it.
# Use this ONLY if you want clawhub.ai to provide your Google
# OAuth credentials.json instead of downloading it yourself from
# Google Cloud Console.
# ============================================================
#
# Proactive Claw — OPT-IN clawhub.ai OAuth credential provisioning
#
# WHAT THIS DOES:
#   Downloads your Google OAuth credentials.json from clawhub.ai using a
#   clawhub_token you have set in config.json.
#
# WHAT IS FETCHED:
#   Only the Google OAuth client definition (credentials.json) — the same file
#   you would download from Google Cloud Console. This is NOT your token.json,
#   NOT your calendar data, and NOT any personal information.
#
# WHAT IS NOT FETCHED:
#   - token.json (your Google access token — generated locally, never leaves your machine)
#   - Any calendar events or personal data
#
# HOW TO VERIFY:
#   After running this script, inspect the downloaded file:
#     cat ~/.openclaw/workspace/skills/proactive-claw/credentials.json
#   It should contain only: {"installed": {"client_id": "...", "client_secret": "...", ...}}
#   No personal data. You can revoke the OAuth client at any time in Google Cloud Console.
#
# HOW TO OPT IN:
#   1. Set clawhub_token in your config.json (from clawhub.ai/settings/integrations)
#   2. Run: bash scripts/setup_clawhub_oauth.sh
#   3. Then run: bash scripts/setup.sh (for the rest of setup)
#
# This script is NOT called by setup.sh. It is a separate, explicit opt-in.

set -e

SKILL_DIR="$HOME/.openclaw/workspace/skills/proactive-claw"
CONFIG="$SKILL_DIR/config.json"
CREDS="$SKILL_DIR/credentials.json"

echo "🔑 Proactive Claw — clawhub OAuth credential provisioning"
echo "=========================================================="
echo ""
echo "This will download credentials.json from clawhub.ai."
echo "Only the OAuth client definition is fetched — never your token or calendar data."
echo ""

if [ ! -f "$CONFIG" ]; then
  echo "❌ config.json not found. Run scripts/setup.sh first to create it."
  exit 1
fi

if [ -f "$CREDS" ]; then
  echo "ℹ️  credentials.json already exists at $CREDS"
  echo "   Delete it first if you want to re-download."
  exit 0
fi

python3 - << 'PYEOF'
import json, urllib.request, sys
from pathlib import Path

SKILL_DIR = Path.home() / ".openclaw/workspace/skills/proactive-claw"
CONFIG_FILE = SKILL_DIR / "config.json"
CREDS_FILE = SKILL_DIR / "credentials.json"

with open(CONFIG_FILE) as f:
    config = json.load(f)

token = config.get("clawhub_token", "").strip()
if not token:
    print("❌ clawhub_token not set in config.json")
    print("   Get your token at: https://clawhub.ai/settings/integrations")
    sys.exit(1)

print(f"🌐 Contacting clawhub.ai to fetch Google OAuth client definition...")
print(f"   Endpoint: https://clawhub.ai/api/oauth/google-calendar-credentials")
print(f"   Method: GET (read-only)")
print()

try:
    req = urllib.request.Request(
        "https://clawhub.ai/api/oauth/google-calendar-credentials",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"}
    )
    resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
    creds_data = resp.get("credentials")
    if not creds_data:
        print("❌ No credentials returned from clawhub.")
        print("   Connect Google Calendar at https://clawhub.ai/settings/integrations first.")
        sys.exit(1)
    with open(CREDS_FILE, "w") as f:
        json.dump(creds_data, f, indent=2)
    print(f"✅ credentials.json downloaded to {CREDS_FILE}")
    print()
    print("To verify the downloaded file contains only the OAuth client definition:")
    print(f"  cat {CREDS_FILE}")
    print()
    print("Next step: run bash scripts/setup.sh to complete setup.")
except Exception as e:
    print(f"❌ Failed to fetch credentials: {e}")
    print("   Alternative: download credentials.json manually from Google Cloud Console")
    print("   (see SKILL.md Setup section, Option B)")
    sys.exit(1)
PYEOF
