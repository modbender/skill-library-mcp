#!/bin/bash
#
# Send Daily Briefing via iMessage
# Generates and sends the morning briefing to a specified recipient.
#
# Usage: ./send-briefing.sh <recipient>
# Example: ./send-briefing.sh paulkingham@mac.com
#

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RECIPIENT="${1:-paulkingham@mac.com}"

# Check if imsg is available
if ! command -v imsg &> /dev/null; then
    echo "Error: imsg not found. Install with: brew install steipete/tap/imsg" >&2
    exit 1
fi

# Generate the briefing
echo "Generating briefing..." >&2
briefing=$("${SCRIPT_DIR}/generate-briefing.sh")

# Send via iMessage
echo "Sending to $RECIPIENT..." >&2
imsg send --to "$RECIPIENT" --text "$briefing"

# Record the send
echo "$(date -Iseconds) - Briefing sent to $RECIPIENT" >> "$(dirname "$SCRIPT_DIR")/.last-run"

echo "Briefing sent successfully!" >&2
