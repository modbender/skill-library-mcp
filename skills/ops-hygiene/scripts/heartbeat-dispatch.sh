#!/bin/bash
# Heartbeat Dispatcher — triage checks locally, escalate only when needed
# Usage: bash heartbeat-dispatch.sh
# 
# Flow:
#   1. Run health-check.sh (no LLM needed)
#   2. Check state file for what's overdue
#   3. Run overdue checks
#   4. Triage results through Reef (local LLM, $0)
#   5. Only output alert if something needs cloud agent attention
#   6. Otherwise → HEARTBEAT_OK
#
# Output: JSON with action needed or "HEARTBEAT_OK"

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE="${HOME}/.openclaw/workspace"
STATE_FILE="${WORKSPACE}/memory/heartbeat-state.json"
REEF_URL="http://localhost:3030"
NOW=$(date +%s)
ALERTS=""

# ── Helpers ───────────────────────────────────────────────────────────────────

add_alert() {
    if [ -z "$ALERTS" ]; then
        ALERTS="$1"
    else
        ALERTS="${ALERTS}\n$1"
    fi
}

get_last_check() {
    local key="$1"
    if [ -f "$STATE_FILE" ]; then
        python3 -c "
import json
with open('$STATE_FILE') as f:
    d = json.load(f)
v = d.get('lastChecks', {}).get('$key', 0)
print(v if isinstance(v, (int, float)) and v is not None else 0)
" 2>/dev/null || echo "0"
    else
        echo "0"
    fi
}

update_state() {
    local key="$1"
    python3 -c "
import json, os
path = '$STATE_FILE'
os.makedirs(os.path.dirname(path), exist_ok=True)
try:
    with open(path) as f:
        d = json.load(f)
except:
    d = {'lastChecks': {}}
d.setdefault('lastChecks', {})['$key'] = $NOW
with open(path, 'w') as f:
    json.dump(d, f, indent=2)
" 2>/dev/null
}

hours_since() {
    local last="$1"
    echo $(( (NOW - last) / 3600 ))
}

reef_triage() {
    local prompt="$1"
    local response
    response=$(curl -s --max-time 10 -X POST "${REEF_URL}/api/delegate" \
        -H "Content-Type: application/json" \
        -d "{\"prompt\": \"$prompt\"}" 2>/dev/null)
    
    if [ $? -eq 0 ] && [ -n "$response" ]; then
        echo "$response" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(d.get('response', 'error')[:500])
" 2>/dev/null || echo "reef_error"
    else
        echo "reef_unavailable"
    fi
}

# ── Check: Is it quiet hours? ────────────────────────────────────────────────

HOUR=$(date +%H)
if [ "$HOUR" -ge 7 ] && [ "$HOUR" -lt 23 ]; then
    QUIET_HOURS=false
else
    QUIET_HOURS=true
fi

# ── Check 1: System Health (every heartbeat, no LLM) ─────────────────────────

HEALTH=$(bash "${SCRIPT_DIR}/health-check.sh" 2>/dev/null || echo '{"error": true}')

# Parse critical values
DISK_USED=$(echo "$HEALTH" | python3 -c "import sys,json; print(json.load(sys.stdin).get('disk',{}).get('usedPercent', 0))" 2>/dev/null || echo 0)
RAM_FREE=$(echo "$HEALTH" | python3 -c "import sys,json; print(json.load(sys.stdin).get('memory',{}).get('freeGB', '99'))" 2>/dev/null || echo 99)
UNCOMMITTED=$(echo "$HEALTH" | python3 -c "import sys,json; print(json.load(sys.stdin).get('git',{}).get('uncommitted', 0))" 2>/dev/null || echo 0)
OLLAMA_UP=$(echo "$HEALTH" | python3 -c "import sys,json; print(json.load(sys.stdin).get('ollama',{}).get('running', False))" 2>/dev/null || echo False)

# Threshold alerts (no LLM needed)
if [ "$DISK_USED" -gt 80 ]; then
    add_alert "🔴 Disk usage at ${DISK_USED}%"
fi

RAM_FREE_INT=$(echo "$RAM_FREE" | cut -d. -f1)
if [ "$RAM_FREE_INT" -lt 2 ]; then
    add_alert "🔴 RAM critically low: ${RAM_FREE}GB free"
fi

if [ "$OLLAMA_UP" = "False" ]; then
    add_alert "🟡 Ollama is not running"
fi

if [ "$UNCOMMITTED" -gt 20 ]; then
    add_alert "🟡 ${UNCOMMITTED} uncommitted files in workspace"
fi

update_state "health"

# ── Check 2: Secret Scan (every 24h) ─────────────────────────────────────────

LAST_SECRET=$(get_last_check "secretScan")
HOURS_SINCE_SECRET=$(hours_since "$LAST_SECRET")

if [ "$HOURS_SINCE_SECRET" -ge 24 ]; then
    if ! bash "${SCRIPT_DIR}/secret-scan.sh" "$WORKSPACE" > /dev/null 2>&1; then
        add_alert "🔴 Secret scan found exposed credentials — run security-audit.sh"
    fi
    update_state "secretScan"
fi

# ── Check 3: Email Triage (every 4h, uses Reef for summary) ──────────────────

LAST_EMAIL=$(get_last_check "email")
HOURS_SINCE_EMAIL=$(hours_since "$LAST_EMAIL")

if [ "$HOURS_SINCE_EMAIL" -ge 4 ]; then
    # Check if we can reach AgentMail
    EMAIL_COUNT=$(python3 -c "
import warnings; warnings.filterwarnings('ignore')
try:
    from agentmail import AgentMail
    client = AgentMail(api_key='$(grep -o "am_[a-f0-9]*" "$WORKSPACE/.secrets" 2>/dev/null || echo "none")')
    msgs = client.inboxes.messages.list(inbox_id='celeste.ai@agentmail.to')
    # Count unread/recent (last 4 hours)
    print(len(msgs.messages) if hasattr(msgs, 'messages') else 0)
except Exception as e:
    print(0)
" 2>/dev/null || echo "0")

    if [ "$EMAIL_COUNT" -gt 0 ]; then
        # Use Reef to triage — is any email urgent?
        TRIAGE=$(reef_triage "You are an email triage bot. There are $EMAIL_COUNT emails in the inbox. Reply with only: URGENT, CHECK, or SKIP. If count is 0, say SKIP.")
        if echo "$TRIAGE" | grep -qi "URGENT"; then
            add_alert "📧 Urgent email detected — $EMAIL_COUNT message(s) in inbox"
        fi
    fi
    update_state "email"
fi

# ── Check 4: Git Commit Reminder (every 8h) ──────────────────────────────────

LAST_GIT=$(get_last_check "gitCommit")
HOURS_SINCE_GIT=$(hours_since "$LAST_GIT")

if [ "$HOURS_SINCE_GIT" -ge 8 ] && [ "$UNCOMMITTED" -gt 5 ]; then
    add_alert "📝 ${UNCOMMITTED} uncommitted files — consider committing"
    update_state "gitCommit"
fi

# ── Check 5: Memory Maintenance (every 48h) ──────────────────────────────────

LAST_MEMORY=$(get_last_check "memoryMaintenance")
HOURS_SINCE_MEMORY=$(hours_since "$LAST_MEMORY")

if [ "$HOURS_SINCE_MEMORY" -ge 48 ]; then
    add_alert "🧠 Memory maintenance overdue — review daily logs, update MEMORY.md"
    update_state "memoryMaintenance"
fi

# ── Check 6: Prompt Guard Update (every 168h / weekly) ────────────────────────

LAST_PG=$(get_last_check "promptGuardUpdate")
HOURS_SINCE_PG=$(hours_since "$LAST_PG")

if [ "$HOURS_SINCE_PG" -ge 168 ]; then
    add_alert "🛡️ Prompt-guard patterns review overdue (weekly)"
    update_state "promptGuardUpdate"
fi

# ── Output ────────────────────────────────────────────────────────────────────

if [ -n "$ALERTS" ] && [ "$QUIET_HOURS" = false ]; then
    echo "{"
    echo "  \"status\": \"attention_needed\","
    echo "  \"alerts\": ["
    echo -e "$ALERTS" | while IFS= read -r alert; do
        echo "    \"$alert\","
    done
    echo "    \"\"" # trailing element to avoid comma issues
    echo "  ],"
    echo "  \"health\": $HEALTH,"
    echo "  \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\""
    echo "}"
    exit 2
elif [ -n "$ALERTS" ] && [ "$QUIET_HOURS" = true ]; then
    # Log but don't escalate during quiet hours
    echo "HEARTBEAT_OK"
    exit 0
else
    echo "HEARTBEAT_OK"
    exit 0
fi
