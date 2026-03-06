#!/bin/bash
# Get CS2 stats by Telegram username

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check arguments
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <username>" >&2
    echo "Example: $0 jeminay" >&2
    echo "Example: $0 @jeminay" >&2
    exit 1
fi

USERNAME="$1"

# Get Steam ID using Python
STEAM_ID=$(python3 "$SCRIPT_DIR/steam_ids.py" get --username "$USERNAME" 2>/dev/null || echo "")

if [ -z "$STEAM_ID" ]; then
    echo "❌ Steam ID не найден для @$USERNAME" >&2
    exit 1
fi

# Get and format stats
python3 "$SCRIPT_DIR/profile_with_stats.py" --steam-id "$STEAM_ID" --json | python3 "$SCRIPT_DIR/format_profile.py"
