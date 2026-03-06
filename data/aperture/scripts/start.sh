#!/usr/bin/env bash
# Start aperture reverse proxy.
#
# Usage:
#   start.sh                           # Background, default config
#   start.sh --foreground              # Foreground mode
#   start.sh --config /path/to/yaml    # Custom config

set -e

APERTURE_DIR="$HOME/.aperture"
CONFIG_FILE="$APERTURE_DIR/aperture.yaml"
FOREGROUND=false

# Parse arguments.
while [[ $# -gt 0 ]]; do
    case $1 in
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        --foreground)
            FOREGROUND=true
            shift
            ;;
        -h|--help)
            echo "Usage: start.sh [--foreground] [--config PATH]"
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

# Verify aperture is installed.
if ! command -v aperture &>/dev/null; then
    echo "Error: aperture not found. Run install.sh first." >&2
    exit 1
fi

# Verify config exists.
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Config not found at $CONFIG_FILE" >&2
    echo "Run setup.sh first to generate config." >&2
    exit 1
fi

# Check if aperture is already running.
if pgrep -x aperture &>/dev/null; then
    echo "aperture is already running (PID: $(pgrep -x aperture))."
    echo "Use stop.sh to stop it first."
    exit 1
fi

echo "=== Starting Aperture ==="
echo "Config: $CONFIG_FILE"
echo ""

LOG_FILE="$APERTURE_DIR/aperture-start.log"

if [ "$FOREGROUND" = true ]; then
    exec aperture --configfile="$CONFIG_FILE"
else
    nohup aperture --configfile="$CONFIG_FILE" \
        > "$LOG_FILE" 2>&1 &
    APERTURE_PID=$!
    echo "aperture started in background (PID: $APERTURE_PID)"
    echo "Log file: $LOG_FILE"

    # Wait briefly and verify it's running.
    sleep 2
    if kill -0 "$APERTURE_PID" 2>/dev/null; then
        echo "aperture is running."
    else
        echo "Error: aperture exited immediately. Check $LOG_FILE" >&2
        tail -20 "$LOG_FILE" 2>/dev/null
        exit 1
    fi
fi
