#!/bin/bash
# Compare two players by their Telegram usernames

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <username1> <username2>" >&2
    echo "Example: $0 jeminay kokojambovin" >&2
    exit 1
fi

USERNAME1="$1"
USERNAME2="$2"

# Get Steam IDs for both players
STEAM_ID_1=$(python3 "$SCRIPT_DIR/steam_ids.py" get --username "$USERNAME1" 2>/dev/null || echo "")
STEAM_ID_2=$(python3 "$SCRIPT_DIR/steam_ids.py" get --username "$USERNAME2" 2>/dev/null || echo "")

if [ -z "$STEAM_ID_1" ]; then
    echo "❌ Steam ID не найден для @$USERNAME1" >&2
    exit 1
fi

if [ -z "$STEAM_ID_2" ]; then
    echo "❌ Steam ID не найден для @$USERNAME2" >&2
    exit 1
fi

# Get stats for both players
PLAYER1_DATA=$(python3 "$SCRIPT_DIR/profile_with_stats.py" --steam-id "$STEAM_ID_1" --json)
PLAYER2_DATA=$(python3 "$SCRIPT_DIR/profile_with_stats.py" --steam-id "$STEAM_ID_2" --json)

# Combine into array and pass to compare script
echo "[$PLAYER1_DATA,$PLAYER2_DATA]" | python3 "$SCRIPT_DIR/compare_players.py"
