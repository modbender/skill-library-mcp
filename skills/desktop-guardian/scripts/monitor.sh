#!/usr/bin/env bash
# Desktop Guardian v2 — Monitor Script
# Called by LaunchAgent every 60 seconds.
# NEVER interpolates shell variables into hs -c strings.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HELPERS="$SCRIPT_DIR/helpers.py"
CONFIG_DIR="$HOME/.openclaw/skills/desktop-guardian"
KILL_SWITCH="$CONFIG_DIR/KILL_SWITCH"
LOG_DIR="$HOME/Library/Logs/desktop-guardian"
SWIFT_FALLBACK="$SCRIPT_DIR/desktop-query"

# Ensure directories exist
mkdir -p "$CONFIG_DIR" && chmod 700 "$CONFIG_DIR" || true
mkdir -p "$LOG_DIR" && chmod 700 "$LOG_DIR" || true

# Always exit 0 — LaunchAgent should never see failures
trap 'exit 0' ERR

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

# 1. Kill switch check
if [[ -f "$KILL_SWITCH" ]]; then
    log "Kill switch active, aborting"
    exit 0
fi

# 2. Check quiet hours
if ! python3 "$HELPERS" check_quiet 2>/dev/null; then
    log "Quiet hours active, skipping"
    exit 0
fi

# 3. Determine mode: full (Hammerspoon) or degraded (Swift fallback)
MODE="degraded"
SNAPSHOT=""

if command -v hs &>/dev/null; then
    # Test if Hammerspoon is responsive
    ACC=$(hs -c 'spoon.DesktopGuardian.accessibilityState()' 2>/dev/null || echo '{"accessible":false}')
    if echo "$ACC" | python3 -c "import sys,json; d=json.load(sys.stdin); sys.exit(0 if d.get('accessible') else 1)" 2>/dev/null; then
        MODE="full"
    fi
fi

# 4. Query desktop state
if [[ "$MODE" == "full" ]]; then
    SNAPSHOT=$(hs -c 'spoon.DesktopGuardian.queryAll()' 2>/dev/null || echo '{}')
elif [[ -x "$SWIFT_FALLBACK" ]]; then
    SNAPSHOT=$("$SWIFT_FALLBACK" 2>/dev/null || echo '{}')
    log "WARNING: Running in degraded mode (no Hammerspoon). Cleanup disabled."
else
    log "ERROR: Neither Hammerspoon nor Swift fallback available"
    exit 0
fi

# 5. Validate snapshot
if [[ -z "$SNAPSHOT" || "$SNAPSHOT" == "{}" ]]; then
    log "ERROR: Empty snapshot"
    exit 0
fi

# 6. Evaluate snapshot against policy
EVAL_RESULT=$(python3 "$HELPERS" evaluate_snapshot "$SNAPSHOT" 2>/dev/null || echo '{"violations":[],"actions":[]}')

# Parse violations and actions
VIOLATION_COUNT=$(echo "$EVAL_RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('violations',[])))" 2>/dev/null || echo "0")
ACTION_COUNT=$(echo "$EVAL_RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('actions',[])))" 2>/dev/null || echo "0")

if [[ "$VIOLATION_COUNT" == "0" ]]; then
    exit 0
fi

log "Found $VIOLATION_COUNT violations, $ACTION_COUNT actions to take"

# 7. Execute actions (only in full mode)
ACTIONS_TAKEN=()
ASK_MESSAGES=()

if [[ "$MODE" == "full" && "$ACTION_COUNT" -gt "0" ]]; then
    # Extract and execute each action
    # Use Python to iterate actions safely — NO shell interpolation into hs -c
    while IFS= read -r action_line; do
        ACTION_TYPE=$(echo "$action_line" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('type',''))" 2>/dev/null)
        
        case "$ACTION_TYPE" in
            close_window|close_app|force_close_app|close_tab|dismiss_dialog|dismiss_dialog_escape)
                # Get the pre-built safe hs command from helpers.py
                HS_CMD=$(echo "$action_line" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('hs_command',''))" 2>/dev/null)
                if [[ -n "$HS_CMD" ]]; then
                    DESC=$(echo "$action_line" | python3 -c "
import sys,json
d=json.load(sys.stdin)
t=d.get('type','')
if t=='close_window': print(f\"Closed window {d.get('title','')} of {d.get('app','')}\")
elif t=='close_app': print(f\"Closed app {d.get('app','')}\")
elif t=='force_close_app': print(f\"Force closed app {d.get('app','')}\")
elif t=='close_tab': print(f\"Closed Chrome tab {d.get('title','')}\")
elif t.startswith('dismiss_dialog'): print(f\"Dismissed dialog from {d.get('app','')}\")
else: print(t)
" 2>/dev/null)
                    log "Executing: $DESC"
                    # Execute the pre-built command
                    eval "$HS_CMD" 2>/dev/null || log "WARNING: Action failed: $DESC"
                    ACTIONS_TAKEN+=("$DESC")
                    # Log the action
                    python3 "$HELPERS" log_violation "action_taken" "$DESC" 2>/dev/null || true
                fi
                ;;
            ask_user)
                MSG=$(echo "$action_line" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('message',''))" 2>/dev/null)
                ASK_MESSAGES+=("$MSG")
                ;;
        esac
    done < <(echo "$EVAL_RESULT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
for a in d.get('actions', []):
    print(json.dumps(a))
" 2>/dev/null)
fi

# 8. Log violations
while IFS= read -r viol_line; do
    VTYPE=$(echo "$viol_line" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('type',''))" 2>/dev/null)
    VDETAIL=$(echo "$viol_line" | python3 -c "import sys,json; print(json.dumps(json.load(sys.stdin)))" 2>/dev/null)
    python3 "$HELPERS" log_violation "$VTYPE" "$VDETAIL" 2>/dev/null || true
done < <(echo "$EVAL_RESULT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
for v in d.get('violations', []):
    print(json.dumps(v))
" 2>/dev/null)

# 9. Send notifications
NOTIFY_ON_ACTIONS=$(python3 -c "
import sys; sys.path.insert(0, '$SCRIPT_DIR')
from helpers import load_config
cfg = load_config()
print('true' if cfg.get('alerts',{}).get('notify_on_actions', True) else 'false')
" 2>/dev/null || echo "true")

# Build alert message
ALERT_MSG=""

# Notify about auto-actions taken
if [[ "$NOTIFY_ON_ACTIONS" == "true" && ${#ACTIONS_TAKEN[@]} -gt 0 ]]; then
    ALERT_MSG="🧹 Desktop Guardian auto-cleaned:\n"
    for act in "${ACTIONS_TAKEN[@]}"; do
        ALERT_MSG+="  • $act\n"
    done
fi

# Add items needing user attention
if [[ ${#ASK_MESSAGES[@]} -gt 0 ]]; then
    ALERT_MSG+="⚠️ Desktop Guardian — needs your input:\n"
    for msg in "${ASK_MESSAGES[@]}"; do
        ALERT_MSG+="  $msg\n"
    done
fi

# Add degraded mode note
if [[ "$MODE" == "degraded" && "$VIOLATION_COUNT" -gt "0" ]]; then
    ALERT_MSG+="ℹ️ Running in monitor-only mode (no Hammerspoon). Install Hammerspoon for auto-cleanup.\n"
fi

# Send alert if there's something to say
if [[ -n "$ALERT_MSG" ]]; then
    # Check cooldown
    if python3 "$HELPERS" check_cooldown "combined" 2>/dev/null; then
        # Try openclaw_wake first
        if command -v openclaw &>/dev/null; then
            echo -e "$ALERT_MSG" | openclaw wake --message "$(echo -e "$ALERT_MSG")" 2>/dev/null || true
        fi
        # Update cooldown state
        python3 "$HELPERS" update_state "combined" 2>/dev/null || true
    fi
fi

log "Monitor cycle complete. Violations: $VIOLATION_COUNT, Actions: ${#ACTIONS_TAKEN[@]}"
exit 0
