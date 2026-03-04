#!/bin/bash
# Slack Thread Reader
# Fetches thread replies using a Slack link or channel ID + timestamp.
#
# Usage:
#   ./slack-thread.sh https://your-workspace.slack.com/archives/C0123456789/p1234567890123456
#   ./slack-thread.sh C0123456789 1234567890.123456
#   ./slack-thread.sh C0123456789 1234567890.123456 50    # with limit
#
# Output: [timestamp] username: message text (one per line)

set -euo pipefail

CONFIG_FILE="$HOME/.openclaw/openclaw.json"

exec python3 "$(dirname "$0")/slack-thread.py" "$@"
