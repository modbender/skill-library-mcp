#!/bin/bash
# Wrapper for video-audio-replace skill

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/replace.py" "$@"
