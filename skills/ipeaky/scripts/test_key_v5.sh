#!/usr/bin/env bash
# ipeaky v5 — test_key_v5.sh
# Usage: bash test_key_v5.sh <SERVICE_NAME>
# Tests the stored key for a service. Key never appears in stdout, logs, or ps.

set -euo pipefail

SERVICE="${1:?Usage: test_key_v5.sh <SERVICE_NAME>}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KEY_PATHS_DIR="$HOME/.ipeaky/key-paths"
STATUS_FILE="$HOME/.ipeaky/status.json"

# ── 1. Load test config ────────────────────────────────────────────────
CONFIG_JSON=$(bash "$SCRIPT_DIR/detect_test_config.sh" "$SERVICE")
URL=$(echo "$CONFIG_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('url',''))")
METHOD=$(echo "$CONFIG_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('method','GET'))")
EXPECTED=$(echo "$CONFIG_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('expected_status',200))")

if [ -z "$URL" ]; then
  echo "⚠️  No test URL configured for $SERVICE."
  echo "   Run: bash $SCRIPT_DIR/config_test.sh $SERVICE"
  exit 0
fi

# ── 2. Get openclaw config path ────────────────────────────────────────
KEY_PATH_FILE="$KEY_PATHS_DIR/${SERVICE}.txt"
if [ ! -f "$KEY_PATH_FILE" ]; then
  echo "❌  Key path not registered for $SERVICE."
  echo "   Was this key stored with ipeaky? (store scripts call register_key_path.sh)"
  exit 1
fi
CONFIG_PATH=$(cat "$KEY_PATH_FILE" | tr -d '[:space:]')

# ── 3. Read key from openclaw config ──────────────────────────────────
# Key is captured into a variable — never passed as CLI arg to external tools
KEY=$(openclaw config get "$CONFIG_PATH" 2>/dev/null | tr -d '[:space:]')
if [ -z "$KEY" ]; then
  echo "❌  Could not read key at config path: $CONFIG_PATH"
  exit 1
fi
MASKED="${KEY:0:4}****"

# ── 4. Build secure temp header file ──────────────────────────────────
HFILE=$(mktemp)
chmod 600 "$HFILE"

# Replace {{KEY}} in each header line and write to temp file
_PYEOF_HDR=$(mktemp /tmp/ipeaky_hdr_XXXXXX.py)
cat > "$_PYEOF_HDR" <<'PYEOF'
import sys, json

config_file = sys.argv[1]
key = sys.argv[2]

config = json.load(sys.stdin)
headers = config.get("headers", [])

with open(config_file, "w") as f:
    for h in headers:
        f.write(h.replace("{{KEY}}", key) + "\n")
PYEOF
echo "$CONFIG_JSON" | python3 "$_PYEOF_HDR" "$HFILE" "$KEY"
rm -f "$_PYEOF_HDR"

# ── 5. Run curl ────────────────────────────────────────────────────────
RESP_FILE=$(mktemp)
START_MS=$(python3 -c "import time; print(int(time.time() * 1000))")

BODY=$(echo "$CONFIG_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('body') or '')")

if [ -n "$BODY" ] && [ "$BODY" != "None" ] && [ "$BODY" != "null" ]; then
  HTTP_CODE=$(curl -s -o "$RESP_FILE" -w "%{http_code}" \
    -X "$METHOD" \
    -H @"$HFILE" \
    -d "$BODY" \
    "$URL" 2>/dev/null || echo "000")
else
  HTTP_CODE=$(curl -s -o "$RESP_FILE" -w "%{http_code}" \
    -X "$METHOD" \
    -H @"$HFILE" \
    "$URL" 2>/dev/null || echo "000")
fi

END_MS=$(python3 -c "import time; print(int(time.time() * 1000))")
LATENCY=$((END_MS - START_MS))

# ── 6. Cleanup header file immediately ────────────────────────────────
rm -f "$HFILE"
rm -f "$RESP_FILE"

# ── 7. Evaluate result ─────────────────────────────────────────────────
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
if [ "$HTTP_CODE" = "$EXPECTED" ]; then
  STATUS="OK"
  echo "✅ $SERVICE ($MASKED) → HTTP $HTTP_CODE — ${LATENCY}ms"
else
  STATUS="FAIL"
  echo "❌ $SERVICE ($MASKED) → HTTP $HTTP_CODE (expected $EXPECTED) — ${LATENCY}ms"
fi

# ── 8. Update status.json atomically ──────────────────────────────────
mkdir -p "$HOME/.ipeaky"
_PYEOF_STATUS=$(mktemp /tmp/ipeaky_status_XXXXXX.py)
cat > "$_PYEOF_STATUS" <<'PYEOF'
import sys, json, os, tempfile

status_file = sys.argv[1]
service     = sys.argv[2]
status      = sys.argv[3]
http_code   = sys.argv[4]
latency_ms  = int(sys.argv[5])
masked      = sys.argv[6]
timestamp   = sys.argv[7]

# Load existing or create fresh
if os.path.exists(status_file):
    with open(status_file) as f:
        data = json.load(f)
else:
    data = {"updated": timestamp, "keys": {}}

data["updated"] = timestamp
data["keys"][service] = {
    "status":      status,
    "http_code":   int(http_code) if http_code.isdigit() else http_code,
    "latency_ms":  latency_ms,
    "masked":      masked,
    "last_checked": timestamp,
    "error":       None if status == "OK" else f"HTTP {http_code}"
}

# Atomic write
tmp = status_file + ".tmp"
with open(tmp, "w") as f:
    json.dump(data, f, indent=2)
os.replace(tmp, status_file)
PYEOF
python3 "$_PYEOF_STATUS" "$STATUS_FILE" "$SERVICE" "$STATUS" "$HTTP_CODE" "$LATENCY" "$MASKED" "$TIMESTAMP"
rm -f "$_PYEOF_STATUS"
