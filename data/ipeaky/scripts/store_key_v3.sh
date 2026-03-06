#!/usr/bin/env bash
# ipeaky v3 — Zero-exposure key storage
# The agent NEVER sees the key. This script:
# 1. Shows a macOS popup for secure input (hidden answer)
# 2. Writes the key directly into openclaw.json via Python (never in argv/process list)
# 3. Restarts the gateway to pick up new config
# 4. Returns only OK/ERROR to the agent — key never appears in output
#
# Usage: bash store_key_v3.sh <SERVICE_NAME> <config_path1> [config_path2] ...
# Example: bash store_key_v3.sh "Brave Search" "tools.web.search.apiKey"
# Example: bash store_key_v3.sh "ElevenLabs" "skills.entries.sag.apiKey" "talk.apiKey"

set -euo pipefail

SERVICE_NAME="${1:?Usage: store_key_v3.sh <SERVICE_NAME> <config_path> [config_path2] ...}"
shift
CONFIG_PATHS=("$@")

if [ ${#CONFIG_PATHS[@]} -eq 0 ]; then
  echo "ERROR: No config paths provided"
  exit 1
fi

# --- Sanitize SERVICE_NAME to prevent shell injection in osascript dialog ---
# Remove quotes, backticks, dollar signs, semicolons, and other dangerous chars
SAFE_SERVICE_NAME=$(echo "$SERVICE_NAME" | sed 's/["`$;\\|&<>(){}]/_/g' | tr -s '_')

# --- 1. Secure input via macOS popup (hidden answer — key not visible on screen) ---
KEY_VALUE=$(osascript <<EOF
set dialogResult to display dialog "Enter your ${SAFE_SERVICE_NAME} API key:" with title "ipeaky 🔑" default answer "" with hidden answer buttons {"Cancel", "Store"} default button "Store"
return text returned of dialogResult
EOF
) || { echo "CANCELLED"; exit 2; }

if [ -z "$KEY_VALUE" ]; then
  echo "ERROR: Empty key"
  exit 1
fi

# --- 2. Write key to secure temp file (0600 — no other users can read) ---
TEMP_KEY_FILE=$(mktemp)
chmod 600 "$TEMP_KEY_FILE"
echo -n "$KEY_VALUE" > "$TEMP_KEY_FILE"
KEY_VALUE=""  # Clear from shell memory immediately

# Locate openclaw config file
OPENCLAW_CONFIG="${HOME}/.openclaw/openclaw.json"
if [ ! -f "$OPENCLAW_CONFIG" ]; then
  echo "ERROR: openclaw.json not found at $OPENCLAW_CONFIG"
  rm -f "$TEMP_KEY_FILE"
  exit 1
fi

# --- 3. Write each config path directly into openclaw.json via Python ---
# Key is read from file inside Python — never passed as argv (no process list exposure)
STORED=0
FAILED=0

for CONFIG_PATH in "${CONFIG_PATHS[@]}"; do
  RESULT=$(python3 - "$CONFIG_PATH" "$TEMP_KEY_FILE" "$OPENCLAW_CONFIG" <<'PYEOF'
import json, sys, os, shutil

config_path = sys.argv[1]
key_file    = sys.argv[2]
config_file = sys.argv[3]

try:
    with open(key_file, 'r') as f:
        key_value = f.read()

    with open(config_file, 'r') as f:
        config = json.load(f)

    # Walk / create nested path
    parts = config_path.split('.')
    obj = config
    for part in parts[:-1]:
        if part not in obj or not isinstance(obj[part], dict):
            obj[part] = {}
        obj = obj[part]
    obj[parts[-1]] = key_value

    # Atomic-ish write: backup then overwrite
    shutil.copy2(config_file, config_file + '.bak.ipeaky')
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

    print("OK")
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
PYEOF
  ) 2>/dev/null

  if [ "$RESULT" = "OK" ]; then
    STORED=$((STORED + 1))
  else
    FAILED=$((FAILED + 1))
    echo "WARN: Failed to set ${CONFIG_PATH}"
  fi
done

# --- 4. Secure cleanup: overwrite temp file with random data before deletion ---
dd if=/dev/urandom of="$TEMP_KEY_FILE" bs=1024 count=1 2>/dev/null || true
rm -f "$TEMP_KEY_FILE"

# --- 5. Restart gateway to pick up new config ---
if [ "$STORED" -gt 0 ]; then
  openclaw gateway restart 2>/dev/null || true
fi

# --- 6. Report result — key never appears in output ---
if [ "$FAILED" -eq 0 ]; then
  echo "OK: ${SERVICE_NAME} key stored in ${STORED} config path(s). Gateway restarting."
else
  echo "PARTIAL: ${STORED} stored, ${FAILED} failed. Check openclaw logs."
  exit 1
fi
