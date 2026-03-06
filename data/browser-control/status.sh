#!/bin/bash
# Browser Control - Status Check

SKILL_DIR=~/.openclaw/skills/browser-control

# Check VNC (Linux only)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if pgrep -f "Xtightvnc.*:1" > /dev/null; then
        VNC_STATUS="running"
    else
        VNC_STATUS="stopped"
    fi
else
    # Mac uses Screen Sharing
    if pgrep -x "screensharingd" > /dev/null; then
        VNC_STATUS="running"
    else
        VNC_STATUS="stopped"
    fi
fi

# Check noVNC
if pgrep -f "websockify.*6080" > /dev/null; then
    NOVNC_STATUS="running"
else
    NOVNC_STATUS="stopped"
fi

# Check ngrok
if pgrep -f "ngrok.*http" > /dev/null; then
    TUNNEL_STATUS="running"
else
    TUNNEL_STATUS="stopped"
fi

# Get URL if available
if [ -f "$SKILL_DIR/config.json" ]; then
    URL=$(jq -r '.novncUrl' "$SKILL_DIR/config.json" 2>/dev/null)
    EMAIL=$(jq -r '.allowedEmail' "$SKILL_DIR/config.json" 2>/dev/null)
else
    URL=""
    EMAIL=""
fi

# Output JSON
cat << EOF
{
  "vnc": "$VNC_STATUS",
  "novnc": "$NOVNC_STATUS",
  "tunnel": "$TUNNEL_STATUS",
  "ready": $([ "$VNC_STATUS" = "running" ] && [ "$NOVNC_STATUS" = "running" ] && [ "$TUNNEL_STATUS" = "running" ] && echo "true" || echo "false"),
  "url": "$URL",
  "allowedEmail": "$EMAIL"
}
EOF
