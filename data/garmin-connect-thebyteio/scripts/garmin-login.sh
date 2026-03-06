#!/bin/bash
# Garmin Connect authentication test
#
# Env vars (optional overrides):
#   GARMIN_1P_ITEM_NAME  - 1Password item title  (default: "Garmin Connect")
#   GARMIN_1P_VAULT      - 1Password vault        (default: "Personal")

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../venv/bin/activate"

GARMIN_1P_ITEM_NAME="${GARMIN_1P_ITEM_NAME:-Garmin Connect}"
GARMIN_1P_VAULT="${GARMIN_1P_VAULT:-Personal}"

export OP_SERVICE_ACCOUNT_TOKEN="${OP_SERVICE_ACCOUNT_TOKEN:-$(cat ~/.config/op/service-account-token 2>/dev/null)}"

EMAIL=$(op item get "$GARMIN_1P_ITEM_NAME" --vault "$GARMIN_1P_VAULT" --fields username 2>/dev/null)
PASSWORD=$(op item get "$GARMIN_1P_ITEM_NAME" --vault "$GARMIN_1P_VAULT" --fields password --reveal 2>/dev/null)

if [ -z "$EMAIL" ] || [ -z "$PASSWORD" ]; then
  echo "❌ Credentials not found: '$GARMIN_1P_ITEM_NAME' in vault '$GARMIN_1P_VAULT'"
  echo "   Set GARMIN_1P_ITEM_NAME / GARMIN_1P_VAULT if yours differ."
  exit 1
fi

mkdir -p /tmp/garmin-session

python - <<PYEOF
import sys, os
os.environ['GARMIN_EMAIL'] = "$EMAIL"
os.environ['GARMIN_PASSWORD'] = "$PASSWORD"

try:
    from garminconnect import Garmin
    client = Garmin(os.environ['GARMIN_EMAIL'], os.environ['GARMIN_PASSWORD'])
    client.login()
    client.garth.dump(dir_path='/tmp/garmin-session/')
    print(f"✅ Logged in as: {client.get_full_name()}")
except ImportError:
    print("❌ garminconnect not installed — pip install garminconnect")
    sys.exit(1)
except Exception as e:
    print(f"❌ Login failed: {e}")
    sys.exit(1)
PYEOF
