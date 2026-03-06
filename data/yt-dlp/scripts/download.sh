#!/usr/bin/env bash
set -e

# yt-dlp wrapper script
# Usage: ./download <url> [options]

# Path to local venv binary
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(dirname "$BASE_DIR")"
YT_DLP="$SKILL_ROOT/.venv/bin/yt-dlp"

# Check if yt-dlp is installed locally, if not, try system or fail
if [ ! -f "$YT_DLP" ]; then
    if command -v yt-dlp &> /dev/null; then
        YT_DLP="yt-dlp"
    else
        echo "Error: yt-dlp is not installed. Run 'scripts/setup' first."
        exit 1
    fi
fi

# Default options (can be overridden by arguments, but applied first)
# - Best video + best audio merged (if not overridden by -f)
# - Embed metadata, thumbnail, subs
# - Output template: Title [ID].ext
# Note: We append user args ($@) at the end so they can override defaults if needed
# OR we simply pass common flags if the user didn't specify format.

# Simple logic: If user provides NO arguments, show help.
if [ -z "$1" ]; then
    "$YT_DLP" --help
    exit 0
fi

# Run yt-dlp with standard "archival" defaults unless specific flags are likely present
# For flexibility, we just prepend some useful defaults for metadata.
# We DO NOT enforce format here because the user might want -F or specific audio.

# Defaults for metadata embedding
DEFAULTS="--embed-metadata --embed-thumbnail --embed-subs --sub-langs all --merge-output-format mp4"

# If the user supplied format flags, don't force merge format blindly if it conflicts (though yt-dlp handles it well)
# We just run it. The user has full CLI power.
"$YT_DLP" $DEFAULTS "$@"
