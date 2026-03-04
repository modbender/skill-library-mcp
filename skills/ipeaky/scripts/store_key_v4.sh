#!/usr/bin/env bash
# ipeaky v4 — "Single Paste, Zero Exposure"
# One popup. Paste everything. Regex parses. One save. One restart.
# Keys never touch: chat, API calls, logs, shell history.
#
# Usage: bash store_key_v4.sh <SERVICE_NAME> <config_prefix>
# Example: bash store_key_v4.sh "X API (Main)" "skills.entries.x-twitter.env"
#
# User pastes any format:
#   consumer key: abc123
#   secret: xyz789
#   bearer token: AAAA...
#
# Or structured:
#   CONSUMER_KEY=abc123
#   SECRET=xyz789
#   BEARER=AAAA...
#
# The script auto-detects keys, confirms with the user, stores all at once.

set -euo pipefail

SERVICE_NAME="${1:?Usage: store_key_v4.sh <SERVICE_NAME> <config_prefix>}"
CONFIG_PREFIX="${2:?Usage: store_key_v4.sh <SERVICE_NAME> <config_prefix>}"

# --- 1. Single popup — paste everything ---
RAW_INPUT=$(osascript <<EOF
set dialogResult to display dialog "Paste all your ${SERVICE_NAME} keys below.

Any format works:
  consumer key: xxx
  secret: yyy
  bearer: zzz" with title "ipeaky v4 🔑" default answer "" buttons {"Cancel", "Store All"} default button "Store All"
return text returned of dialogResult
EOF
) || { echo "CANCELLED"; exit 2; }

if [ -z "$RAW_INPUT" ]; then
  echo "ERROR: Empty input"
  exit 1
fi

# --- 2. Parse with Python (local, no network, no AI) ---
export IPEAKY_RAW="$RAW_INPUT"
PARSE_RESULT=$(python3 -c '
import re, json, os

raw = os.environ.get("IPEAKY_RAW", "")
if not raw.strip():
    print(json.dumps({"error": "empty input"}))
    exit(0)

keys = {}

for line in raw.strip().split("\n"):
    line = line.strip()
    if not line:
        continue
    
    m = re.match(r"^[\s\u2022\-]*([A-Za-z][A-Za-z0-9_ ]*?)\s*[:=]\s*(.+)$", line)
    if m:
        label = m.group(1).strip()
        value = m.group(2).strip().strip("\"").strip("'\''")
        if len(value) > 8:
            norm = re.sub(r"[^A-Za-z0-9]+", "_", label).upper().strip("_")
            keys[norm] = value
            continue
    
    if re.match(r"^[A-Za-z0-9\-_]{20,}$", line):
        idx = len(keys)
        labels = ["CONSUMER_KEY", "CONSUMER_SECRET", "BEARER_TOKEN"]
        label = labels[idx] if idx < len(labels) else f"KEY_{idx+1}"
        keys[label] = line

if not keys:
    tokens = re.findall(r"[A-Za-z0-9\-_]{16,}", raw)
    labels = ["CONSUMER_KEY", "CONSUMER_SECRET", "BEARER_TOKEN"]
    for i, token in enumerate(tokens):
        label = labels[i] if i < len(labels) else f"KEY_{i+1}"
        keys[label] = token

print(json.dumps({"keys": keys}))
')
unset IPEAKY_RAW

# --- 3. Extract parsed keys ---
KEY_COUNT=$(echo "$PARSE_RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('keys',{})))")
KEY_NAMES=$(echo "$PARSE_RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(', '.join(d.get('keys',{}).keys()))")

if [ "$KEY_COUNT" -eq 0 ]; then
  echo "ERROR: Could not parse any keys from input. Try format: key_name: value"
  RAW_INPUT=""
  exit 1
fi

# --- 4. Confirm with user ---
osascript -e "display dialog \"Found ${KEY_COUNT} keys:\n${KEY_NAMES}\n\nStore all to ${CONFIG_PREFIX}?\" with title \"ipeaky v4 🔑 Confirm\" buttons {\"Cancel\", \"Store All\"} default button \"Store All\"" 2>/dev/null || { echo "CANCELLED"; RAW_INPUT=""; exit 2; }

# --- 5. Store all keys in one batch ---
STORED=0
FAILED=0

while IFS= read -r line; do
  KEY_NAME=$(echo "$line" | cut -d'|' -f1)
  KEY_VAL=$(echo "$line" | cut -d'|' -f2)
  CONFIG_PATH="${CONFIG_PREFIX}.${KEY_NAME}"
  
  if openclaw config set "$CONFIG_PATH" "$KEY_VAL" 2>/dev/null; then
    STORED=$((STORED + 1))
  else
    FAILED=$((FAILED + 1))
    echo "WARN: Failed to set ${CONFIG_PATH}"
  fi
done < <(echo "$PARSE_RESULT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
for k, v in d.get('keys', {}).items():
    print(f'{k}|{v}')
")

# --- 6. Clear sensitive data ---
RAW_INPUT=""
PARSE_RESULT=""
KEY_VAL=""

# --- 7. ONE restart ---
if [ "$STORED" -gt 0 ]; then
  openclaw gateway restart 2>/dev/null &
fi

# --- 8. Report ---
if [ "$FAILED" -eq 0 ]; then
  echo "OK: ${STORED} ${SERVICE_NAME} keys stored. Gateway restarting."
else
  echo "PARTIAL: ${STORED} stored, ${FAILED} failed."
  exit 1
fi
