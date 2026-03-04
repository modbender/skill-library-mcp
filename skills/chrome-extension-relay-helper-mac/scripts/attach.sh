#!/usr/bin/env bash
# chrome-relay/scripts/attach.sh
# Attach the OpenClaw Browser Relay to a live Chrome tab using Peekaboo.
# Finds the extension icon by accessibility description — no hardcoded coordinates.
#
# Prerequisites:
#   - peekaboo installed: brew install steipete/tap/peekaboo
#   - node Accessibility permission granted in System Settings
#   - openclaw.json: browser.profiles.chrome = { driver: extension, cdpUrl: http://127.0.0.1:18792 }
#
# Outputs: ATTACHED | ALREADY_ATTACHED | FAILED: <reason>
set -euo pipefail

ANCHOR_URL="https://info.cern.ch/"  # world's first website — static HTML, no anti-bot, always works
MEDIA_DIR="$HOME/.openclaw/media"
mkdir -p "$MEDIA_DIR"

# ── Helpers ───────────────────────────────────────────────────────────────────

# Check attachment state via Peekaboo accessibility tree
relay_state() {
    peekaboo see --app "Google Chrome" --json 2>/dev/null | python3 -c "
import sys, json
data = json.load(sys.stdin)
for e in data.get('data', {}).get('ui_elements', []):
    desc = str(e.get('description', '') or '')
    role = str(e.get('role_description', '') or '')
    if desc.startswith('OpenClaw Browser Relay') and role == 'pop-up button' and e.get('is_actionable'):
        if 'click to detach' in desc.lower():
            print('attached:' + e['id'])
        else:
            print('detached:' + e['id'])
        break
" 2>/dev/null || true
}

# ── 0. Already running? ───────────────────────────────────────────────────────
if pgrep -f "Google Chrome" > /dev/null 2>&1; then
    STATE=$(relay_state)
    if [[ "$STATE" == attached:* ]]; then
        echo "ALREADY_ATTACHED"
        exit 0
    fi
fi

# ── 1. Kill Chrome & patch prefs ─────────────────────────────────────────────
pkill -9 -f "Google Chrome" 2>/dev/null || true
sleep 2

python3 - <<'PYEOF'
import json, os
p = os.path.expanduser("~/Library/Application Support/Google/Chrome/Default/Preferences")
try:
    with open(p) as f:
        prefs = json.load(f)
    prefs.setdefault("session", {})["restore_on_startup"] = 1
    prefs.setdefault("profile", {})["exit_type"] = "Normal"
    prefs["profile"]["exited_cleanly"] = True
    with open(p, "w") as f:
        json.dump(prefs, f)
except:
    pass
PYEOF

# ── 2. Open + maximize Chrome ─────────────────────────────────────────────────
open -a "Google Chrome" "$ANCHOR_URL"
sleep 5
peekaboo window maximize --app "Google Chrome" 2>/dev/null || true
sleep 3   # wait for toolbar to fully render after maximize

# ── 3. Find the OpenClaw icon (retry up to 8x, 2s apart = 16s max) ───────────
echo "Scanning for OpenClaw Browser Relay icon..."
ELEM_ID=""
for attempt in $(seq 1 8); do
    STATE=$(relay_state)
    if [[ "$STATE" == attached:* ]]; then
        echo "ALREADY_ATTACHED"
        exit 0
    elif [[ "$STATE" == detached:* ]]; then
        ELEM_ID="${STATE#detached:}"
        echo "Found (attempt $attempt): $ELEM_ID"
        break
    fi
    echo "  Attempt $attempt: not visible yet..."
    sleep 2
done

if [ -z "$ELEM_ID" ]; then
    /usr/sbin/screencapture -x "$MEDIA_DIR/relay-attach-fail.png"
    echo "FAILED: icon not found after 8 attempts"
    exit 1
fi

# ── 4. Click to attach ────────────────────────────────────────────────────────
peekaboo click --on "$ELEM_ID" --app "Google Chrome" --no-auto-focus
sleep 4

# ── 5. Verify ─────────────────────────────────────────────────────────────────
for check in 1 2 3; do
    STATE=$(relay_state)
    if [[ "$STATE" == attached:* ]]; then
        echo "ATTACHED"
        exit 0
    fi
    sleep 2
done

/usr/sbin/screencapture -x "$MEDIA_DIR/relay-attach-fail.png"
echo "FAILED: clicked but state did not change to attached"
exit 1
