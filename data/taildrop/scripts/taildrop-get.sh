#!/usr/bin/env bash
# Download files from Tailscale Taildrop inbox

set -euo pipefail

# Default settings
TARGET_DIR="$HOME/Downloads"
CONFLICT_MODE="skip"  # skip|overwrite|rename
LOOP_MODE=false

# Parse options
while [[ $# -gt 0 ]]; do
    case $1 in
        --overwrite)
            CONFLICT_MODE="overwrite"
            shift
            ;;
        --rename)
            CONFLICT_MODE="rename"
            shift
            ;;
        --loop)
            LOOP_MODE=true
            shift
            ;;
        -*)
            echo "Unknown option: $1"
            echo "Usage: $0 [target-directory] [--overwrite|--rename] [--loop]"
            exit 1
            ;;
        *)
            TARGET_DIR="$1"
            shift
            ;;
    esac
done

# Create target directory if it doesn't exist
mkdir -p "$TARGET_DIR"

# Check if tailscale is available
if ! command -v tailscale &> /dev/null; then
    echo "Error: tailscale command not found"
    exit 1
fi

# Check if we need sudo
if ! tailscale file get --help &> /dev/null 2>&1; then
    echo "Error: Cannot access Tailscale file commands"
    echo "Run once: sudo tailscale set --operator=\$USER"
    exit 1
fi

# Build command
CMD="tailscale file get --conflict=$CONFLICT_MODE"
if [ "$LOOP_MODE" = true ]; then
    CMD="$CMD --loop"
fi
CMD="$CMD \"$TARGET_DIR\""

echo "Downloading Taildrop files to: $TARGET_DIR"
echo "Conflict mode: $CONFLICT_MODE"
if [ "$LOOP_MODE" = true ]; then
    echo "Running in loop mode (Ctrl+C to stop)..."
fi

# Execute
eval $CMD

echo "✅ Download complete"
