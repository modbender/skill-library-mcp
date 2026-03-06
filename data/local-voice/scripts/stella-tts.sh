#!/bin/bash
# Stella TTS - Local text-to-speech via FluidAudio Kokoro (af_sky voice)
# Usage: stella-tts.sh "Text to speak" [output.wav|output.mp3]
#
# The TTS daemon must be running (com.stella.tts launchd service)
# Returns WAV audio to stdout or specified file (auto-converts to MP3 if .mp3 extension)

set -e

TEXT="$1"
OUTPUT="${2:--}"  # Default to stdout

if [ -z "$TEXT" ]; then
    echo "Usage: stella-tts.sh \"Text to speak\" [output.wav|output.mp3]" >&2
    exit 1
fi

# Check if daemon is running
if ! curl -s http://127.0.0.1:18790/health > /dev/null 2>&1; then
    echo "Error: StellaTTS daemon not running" >&2
    echo "Start it with: launchctl load ~/Library/LaunchAgents/com.stella.tts.plist" >&2
    exit 1
fi

if [ "$OUTPUT" = "-" ]; then
    curl -s -X POST http://127.0.0.1:18790/synthesize -d "$TEXT"
else
    # Check if output should be MP3
    if [[ "$OUTPUT" == *.mp3 ]]; then
        # Generate WAV first, then convert to MP3
        TMPWAV=$(mktemp /tmp/stella-tts-XXXXXX.wav)
        curl -s -X POST http://127.0.0.1:18790/synthesize -d "$TEXT" -o "$TMPWAV"
        ffmpeg -i "$TMPWAV" -b:a 128k "$OUTPUT" -y -loglevel error 2>/dev/null
        rm -f "$TMPWAV"
    else
        curl -s -X POST http://127.0.0.1:18790/synthesize -d "$TEXT" -o "$OUTPUT"
    fi
    echo "$OUTPUT"
fi
