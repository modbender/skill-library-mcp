#!/bin/bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🚨 ORef Alerts - OpenClaw Native - Installer
# Israeli Home Front Command real-time alerts
# via WhatsApp + 3CX call - no Home Assistant needed
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"
LOG_FILE="/var/log/oref_native.log"

echo "🚨 ORef Alerts - OpenClaw Native Installer"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ── 1. בדוק דרישות ───────────────────────────────
echo "📦 Checking dependencies..."
command -v python3 >/dev/null || { echo "❌ python3 required"; exit 1; }
command -v openclaw >/dev/null || { echo "❌ openclaw required"; exit 1; }
pip3 install requests gtts 2>/dev/null | tail -1
echo "✅ Dependencies OK"

# ── 2. הגדרת oref-alerts Docker proxy ────────────
echo ""
echo "🐳 Starting oref-alerts API proxy..."
if ! docker ps | grep -q oref-alerts; then
    docker run -d \
        --name oref-alerts \
        --restart unless-stopped \
        -p 49000:9001 \
        -e TZ="Asia/Jerusalem" \
        dmatik/oref-alerts:latest
    echo "✅ oref-alerts started on port 49000"
else
    echo "✅ oref-alerts already running"
fi

# ── 3. קובץ הגדרות ──────────────────────────────
if [ ! -f "$ENV_FILE" ]; then
    echo ""
    echo "⚙️  Configuration Setup"
    echo "━━━━━━━━━━━━━━━━━━━━━━"

    read -p "📍 Monitored areas (comma separated, e.g. הרצליה,תל אביב): " AREAS
    read -p "📱 WhatsApp group JID (e.g. 120363...@g.us): " WA_GROUP
    read -p "📞 3CX extension to call on alert (e.g. 12610, leave empty to disable): " CX3_EXT
    read -p "🔑 Home Assistant URL (leave empty to disable): " HA_URL
    read -p "🔑 Home Assistant Token (leave empty to disable): " HA_TOKEN

    CX3_ENABLED="false"
    [ -n "$CX3_EXT" ] && CX3_ENABLED="true"

    cat > "$ENV_FILE" << EOF
OREF_API_URL=http://localhost:49000/current
OREF_POLL_INTERVAL=5
OREF_COOLDOWN=60
MONITORED_AREAS=$AREAS
WHATSAPP_GROUP_JID=$WA_GROUP
CX3_API=http://localhost:3000/api/outbound-call
CX3_EXTENSION=$CX3_EXT
CX3_ENABLED=$CX3_ENABLED
HASS_SERVER=$HA_URL
HASS_TOKEN=$HA_TOKEN
HA_TTS_SPEAKER=media_player.home_assistant_voice_09a069_media_player
EOF
    echo "✅ Config saved to $ENV_FILE"
else
    echo "✅ Using existing config: $ENV_FILE"
fi

# ── 4. הפעלה ─────────────────────────────────────
echo ""
echo "🚀 Starting ORef monitor..."
pkill -f oref_native.py 2>/dev/null || true
sleep 1

source "$ENV_FILE"
export $(cat "$ENV_FILE" | grep -v "^#" | xargs)

nohup python3 "$SCRIPT_DIR/oref_native.py" >> "$LOG_FILE" 2>&1 &
PID=$!
sleep 2

if ps -p $PID > /dev/null 2>&1; then
    echo "✅ Monitor running (PID: $PID)"
else
    echo "❌ Monitor failed to start. Check: tail -20 $LOG_FILE"
    exit 1
fi

# ── 5. crontab ────────────────────────────────────
ENV_EXPORTS=$(cat "$ENV_FILE" | grep -v "^#" | tr '\n' ' ')
CRON_CMD="@reboot $ENV_EXPORTS python3 $SCRIPT_DIR/oref_native.py >> $LOG_FILE 2>&1 &"
(crontab -l 2>/dev/null | grep -v oref_native; echo "$CRON_CMD") | crontab -
echo "✅ Added to crontab (auto-start on reboot)"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Installation complete!"
echo ""
echo "📋 Commands:"
echo "  tail -f $LOG_FILE     # live logs"
echo "  pkill -f oref_native  # stop monitor"
echo "  bash $SCRIPT_DIR/install.sh  # restart"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
