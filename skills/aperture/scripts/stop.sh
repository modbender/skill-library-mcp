#!/usr/bin/env bash
# Stop aperture reverse proxy.
#
# Usage:
#   stop.sh            # Graceful stop
#   stop.sh --force    # SIGKILL

set -e

FORCE=false

# Parse arguments.
while [[ $# -gt 0 ]]; do
    case $1 in
        --force)
            FORCE=true
            shift
            ;;
        -h|--help)
            echo "Usage: stop.sh [--force]"
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

APERTURE_PID=$(pgrep -x aperture 2>/dev/null || true)
if [ -z "$APERTURE_PID" ]; then
    echo "aperture is not running."
    exit 0
fi

echo "Stopping aperture (PID: $APERTURE_PID)..."

if [ "$FORCE" = true ]; then
    kill -9 "$APERTURE_PID"
    echo "Sent SIGKILL."
else
    kill "$APERTURE_PID"
    echo "Sent SIGTERM."
fi

# Wait for exit.
for i in {1..10}; do
    if ! kill -0 "$APERTURE_PID" 2>/dev/null; then
        echo "aperture stopped."
        exit 0
    fi
    sleep 1
done

echo "Warning: aperture did not exit within 10 seconds." >&2
echo "Use --force to send SIGKILL." >&2
exit 1
