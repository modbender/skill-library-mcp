#!/usr/bin/env bash
# find_available_plots.sh - Scan the grid for available plot positions
#
# Usage: ./find_available_plots.sh <width> <height> [--limit N]
#
# Width and height must be multiples of 16 (e.g., 16, 32, 64, 128)
# Default limit is 10 results.
#
# Output: JSON with available_plots array, count, and plot_size

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

if [ "$#" -lt 2 ]; then
    echo "Usage: $0 <width> <height> [--limit N]" >&2
    echo "  Example: $0 32 32 --limit 5" >&2
    exit 1
fi

WIDTH="$1"
HEIGHT="$2"
shift 2

# Parse optional args
LIMIT=10
while [ "$#" -gt 0 ]; do
    case "$1" in
        --limit)
            LIMIT="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

# Validate dimensions
if (( WIDTH % GRID_UNIT != 0 )); then
    echo "Error: Width ($WIDTH) must be a multiple of $GRID_UNIT" >&2
    exit 1
fi
if (( HEIGHT % GRID_UNIT != 0 )); then
    echo "Error: Height ($HEIGHT) must be a multiple of $GRID_UNIT" >&2
    exit 1
fi
if (( WIDTH < GRID_UNIT || HEIGHT < GRID_UNIT )); then
    echo "Error: Minimum size is ${GRID_UNIT}x${GRID_UNIT}" >&2
    exit 1
fi
if (( WIDTH > CANVAS_SIZE || HEIGHT > CANVAS_SIZE )); then
    echo "Error: Maximum size is ${CANVAS_SIZE}x${CANVAS_SIZE}" >&2
    exit 1
fi

# Use the Node.js helper for efficient batch RPC scanning
node "$HELPERS_DIR/find_plots.js" "$WIDTH" "$HEIGHT" --limit "$LIMIT"
