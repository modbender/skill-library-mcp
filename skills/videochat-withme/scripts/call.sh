#!/bin/bash
# Incoming call notification — triggers macOS dialog, opens browser on accept
set -e

PORT=${PORT:-8766}
PROTO=${PROTO:-https}
AGENT_NAME=${AGENT_NAME:-"AI Assistant"}

# Pop up incoming call dialog
RESULT=$(osascript -e "
display dialog \"📞 ${AGENT_NAME} incoming call...\" buttons {\"Decline\", \"Accept\"} default button \"Accept\" with title \"Incoming Call\" with icon caution giving up after 30
" 2>&1) || true

if echo "$RESULT" | grep -q "Accept"; then
  open "${PROTO}://localhost:${PORT}"
  echo "ACCEPTED"
else
  echo "DECLINED"
fi
