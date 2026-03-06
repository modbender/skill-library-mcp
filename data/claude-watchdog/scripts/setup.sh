#!/usr/bin/env bash
set -euo pipefail

# setup.sh — Interactive setup for Claude Watchdog skill

SKILL_DATA_DIR="$HOME/.openclaw/skills/claude-watchdog"
ENV_FILE="$SKILL_DATA_DIR/claude-watchdog.env"
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# (#5) Validate python3 exists before doing anything
PYTHON3="$(command -v python3 || true)"
if [[ -z "$PYTHON3" ]]; then
    echo "ERROR: python3 not found. Please install Python 3.10+ first." >&2
    exit 1
fi

# ── uninstall ─────────────────────────────────────────────────────────────────

if [[ "${1:-}" == "--uninstall" ]]; then
    echo "=== Claude Watchdog — Uninstall ==="
    echo ""

    # Remove cron jobs
    if crontab -l 2>/dev/null | grep -q 'claude-watchdog'; then
        crontab -l 2>/dev/null | grep -v 'claude-watchdog' | crontab -
        echo "✓ Cron jobs removed."
    else
        echo "No cron jobs found."
    fi

    # Optionally remove config/state
    if [[ -d "$SKILL_DATA_DIR" ]]; then
        echo ""
        read -rp "Also remove config and state files in $SKILL_DATA_DIR? [y/N]: " remove_data
        if [[ "${remove_data,,}" == "y" ]]; then
            rm -rf "$SKILL_DATA_DIR"
            echo "✓ Config and state files removed."
        else
            echo "Config and state files kept."
        fi
    fi

    echo ""
    echo "=== Uninstall complete ==="
    exit 0
fi

# ── setup ─────────────────────────────────────────────────────────────────────

echo "=== Claude Watchdog — Setup 🐕 ==="
echo ""

# (#4) Warn if config already exists
if [[ -f "$ENV_FILE" ]]; then
    echo "⚠️  Existing config found at $ENV_FILE"
    read -rp "Overwrite? [y/N]: " overwrite
    if [[ "${overwrite,,}" != "y" ]]; then
        echo "Setup cancelled. Edit $ENV_FILE directly to change settings."
        exit 0
    fi
    echo ""
fi

# 1. Telegram Bot Token
echo "Telegram Bot Token (get one from @BotFather on Telegram):"
read -rsp "> " bot_token
echo ""
if [[ -z "$bot_token" ]]; then
    echo "ERROR: Bot token is required." >&2
    exit 1
fi

# 2. Telegram Chat ID
echo ""
echo "Telegram Chat ID — to find yours:"
echo "  1. Send any message to your bot"
echo "  2. Visit https://api.telegram.org/bot<TOKEN>/getUpdates"
echo "  3. Look for \"chat\":{\"id\":YOUR_ID}"
echo "  (Or message @userinfobot on Telegram for your personal chat ID)"
read -rp "> " chat_id
if [[ -z "$chat_id" ]]; then
    echo "ERROR: Chat ID is required." >&2
    exit 1
fi
# (#8) Validate chat_id is numeric (may be negative for groups)
if ! [[ "$chat_id" =~ ^-?[0-9]+$ ]]; then
    echo "ERROR: Chat ID must be a number (e.g. 123456789 or -1001234567890)." >&2
    exit 1
fi

# 3. Telegram Topic ID (optional, for forum groups)
echo ""
echo "Telegram Topic ID (optional — for forum/topic groups only)."
echo "If you're not using forum groups, just press Enter to skip."
echo "To find your topic ID: right-click a topic → Copy Link → the number after the last '/'."
read -rp "> " topic_id
# (#8) Validate topic_id is numeric if provided
if [[ -n "$topic_id" ]] && ! [[ "$topic_id" =~ ^[0-9]+$ ]]; then
    echo "ERROR: Topic ID must be a number." >&2
    exit 1
fi

# 4. OpenClaw Gateway Token
echo ""
echo "OpenClaw Gateway Token (find with: openclaw gateway status, or run:"
echo "  python3 -c \"from pathlib import Path; import json; print(json.load(open(Path.home() / '.openclaw/openclaw.json'))['gateway']['auth']['token'])\""
echo "):"
read -rsp "> " gw_token
echo ""
if [[ -z "$gw_token" ]]; then
    echo "ERROR: Gateway token is required." >&2
    exit 1
fi

# 5. Gateway port (default 18789)
echo ""
read -rp "OpenClaw Gateway Port [18789]: " gw_port
gw_port="${gw_port:-18789}"
# (#8) Validate port is numeric
if ! [[ "$gw_port" =~ ^[0-9]+$ ]] || (( gw_port < 1 || gw_port > 65535 )); then
    echo "ERROR: Port must be a number between 1 and 65535." >&2
    exit 1
fi

# 6. Monitor model (default sonnet)
echo ""
read -rp "Model name to track in status incidents [sonnet]: " monitor_model
monitor_model="${monitor_model:-sonnet}"

# 7. Probe model (default openclaw)
echo ""
echo "Probe model — the model alias sent to the OpenClaw gateway for latency"
echo "probes. 'openclaw' uses the gateway's default routing."
read -rp "Probe model [openclaw]: " probe_model
probe_model="${probe_model:-openclaw}"

# 8. Probe agent ID (default main)
echo ""
read -rp "Probe agent ID (x-openclaw-agent-id header) [main]: " probe_agent_id
probe_agent_id="${probe_agent_id:-main}"

# Write env file
mkdir -p "$SKILL_DATA_DIR"
cat > "$ENV_FILE" <<EOF
TELEGRAM_BOT_TOKEN=$bot_token
TELEGRAM_CHAT_ID=$chat_id
TELEGRAM_TOPIC_ID=${topic_id:-}
OPENCLAW_GATEWAY_TOKEN=$gw_token
OPENCLAW_GATEWAY_PORT=$gw_port
MONITOR_MODEL=$monitor_model
PROBE_MODEL=$probe_model
PROBE_AGENT_ID=$probe_agent_id
EOF
chmod 600 "$ENV_FILE"
echo ""
echo "✓ Config written to $ENV_FILE (permissions: 600)"

# (#6/#2) Send a test alert to verify Telegram works
echo ""
echo "Sending test alert to verify Telegram setup..."
TEST_MSG="🐕 <b>Claude Watchdog — Setup Complete!</b>

Your monitoring is now active. You'll receive alerts here when:
• Anthropic reports an API incident
• API latency spikes above baseline
• Services recover after an incident

Status checks run every 15 minutes."

TEST_PAYLOAD="{\"chat_id\": $chat_id, \"text\": \"$TEST_MSG\", \"parse_mode\": \"HTML\""
if [[ -n "${topic_id:-}" ]]; then
    TEST_PAYLOAD="$TEST_PAYLOAD, \"message_thread_id\": $topic_id"
fi
TEST_PAYLOAD="$TEST_PAYLOAD}"

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST "https://api.telegram.org/bot${bot_token}/sendMessage" \
    -H "Content-Type: application/json" \
    -d "$TEST_PAYLOAD" 2>/dev/null || echo "000")

if [[ "$HTTP_CODE" == "200" ]]; then
    echo "✓ Test alert sent! Check your Telegram chat."
else
    echo "✗ Test alert failed (HTTP $HTTP_CODE)." >&2
    echo "  Check your bot token, chat ID, and topic ID." >&2
    echo "  Config was saved — you can fix values in $ENV_FILE and retry." >&2
    echo "  Continuing setup anyway (cron jobs will retry on next run)." >&2
fi

# Install cron jobs
STATUS_SCRIPT="$SKILL_DIR/scripts/status-check.py"
LATENCY_SCRIPT="$SKILL_DIR/scripts/latency-probe.py"

# Remove old entries if any
crontab -l 2>/dev/null | grep -v 'claude-watchdog' | grep -v 'status-check\.py' | grep -v 'latency-probe\.py' > /tmp/crontab-clean || true
{
    cat /tmp/crontab-clean
    echo "*/15 * * * * $PYTHON3 $STATUS_SCRIPT >> /dev/null 2>&1 # claude-watchdog"
    echo "*/15 * * * * $PYTHON3 $LATENCY_SCRIPT >> /dev/null 2>&1 # claude-watchdog"
} | crontab -
rm -f /tmp/crontab-clean

echo "✓ Cron jobs installed (every 15 minutes)."

# Run initial status check
echo ""
echo "Running initial status check..."
if "$PYTHON3" "$STATUS_SCRIPT"; then
    echo "✓ Status check passed."
else
    echo "✗ Status check failed — check config." >&2
    exit 1
fi

echo ""
echo "=== Setup complete! 🐕 ==="
echo ""
echo "Alerts: Telegram chat $chat_id"
echo "Config: $ENV_FILE"
echo "Logs:   $SKILL_DATA_DIR/"
echo ""
echo "To reconfigure: re-run this script or edit $ENV_FILE directly."
echo "To uninstall:   bash $0 --uninstall"
