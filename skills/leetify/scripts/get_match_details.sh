#!/bin/bash
# Get details for a specific match

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <username> [match_index]"
    echo "Example: $0 jeminay 0 (last match)"
    exit 1
fi

USERNAME="$1"
INDEX="${2:-0}"

python3 "$SCRIPT_DIR/match_details.py" --username "$USERNAME" --index "$INDEX"
