#!/bin/bash
#
# send-voice-memo.sh
# Convert text to native iMessage voice bubble via BlueBubbles
#
# Usage: ./send-voice-memo.sh "Your message here" [recipient_phone]
#
# Requirements:
#   - ELEVENLABS_API_KEY in ~/.openclaw/.env
#   - BLUEBUBBLES_PASSWORD in ~/.openclaw/.env
#   - afconvert (macOS built-in)
#   - BlueBubbles running locally with Private API enabled
#
# Working formula discovered 2026-02-19:
#   - Opus CAF @ 24kHz (pre-converted, not BlueBubbles converted)
#   - chatGuid: any;-;+PHONE (NOT iMessage;-;)
#   - method: private-api (REQUIRED for native bubble)
#   - isAudioMessage: true

set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

# Load environment variables
if [[ -f ~/.openclaw/.env ]]; then
    source ~/.openclaw/.env
else
    echo "❌ Error: ~/.openclaw/.env not found"
    exit 1
fi

# ElevenLabs settings
ELEVENLABS_API_KEY="${ELEVENLABS_API_KEY:-}"
VOICE_ID="${ELEVENLABS_VOICE_ID:-21m00Tcm4TlvDq8ikWAM}"  # Rachel voice ID
MODEL_ID="${ELEVENLABS_MODEL_ID:-eleven_turbo_v2_5}"

# BlueBubbles settings
BLUEBUBBLES_URL="${BLUEBUBBLES_URL:-http://127.0.0.1:1234}"
BLUEBUBBLES_PASSWORD="${BLUEBUBBLES_PASSWORD:-}"

# Default recipient
DEFAULT_RECIPIENT="${IMESSAGE_RECIPIENT:-+14169060839}"

# Output directory
OUTPUT_DIR="${VOICE_MEMO_OUTPUT_DIR:-$HOME/.openclaw/workspace/skills/voice-memo-imessage/tmp}"
mkdir -p "$OUTPUT_DIR"

TIMESTAMP=$(date +%s)
MP3_FILE="$OUTPUT_DIR/tts_${TIMESTAMP}.mp3"
CAF_FILE="$OUTPUT_DIR/voice_${TIMESTAMP}.caf"

# ============================================================================
# Validate inputs
# ============================================================================

if [[ -z "${1:-}" ]]; then
    echo "Usage: $0 \"Your message here\" [recipient_phone]"
    echo ""
    echo "Example: $0 \"Hey, just checking in!\" +14169060839"
    exit 1
fi

TEXT="$1"
RECIPIENT="${2:-$DEFAULT_RECIPIENT}"

if [[ -z "$RECIPIENT" ]]; then
    echo "❌ Error: No recipient specified"
    exit 1
fi

if [[ -z "$ELEVENLABS_API_KEY" ]]; then
    echo "❌ Error: ELEVENLABS_API_KEY not found in .env"
    exit 1
fi

if [[ -z "$BLUEBUBBLES_PASSWORD" ]]; then
    echo "❌ Error: BLUEBUBBLES_PASSWORD not found in .env"
    exit 1
fi

# ============================================================================
# Step 1: Generate TTS audio (ElevenLabs)
# ============================================================================

echo "🎤 Generating voice memo..."

# Escape text for JSON
TEXT_ESCAPED=$(echo "$TEXT" | sed 's/"/\\"/g' | sed "s/'/\\'/g")

curl -X POST "https://api.elevenlabs.io/v1/text-to-speech/$VOICE_ID" \
    -H "xi-api-key: $ELEVENLABS_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{
        \"text\": \"$TEXT_ESCAPED\",
        \"model_id\": \"$MODEL_ID\",
        \"voice_settings\": {
            \"stability\": 0.5,
            \"similarity_boost\": 0.75
        }
    }" \
    --output "$MP3_FILE" \
    --silent \
    --show-error

if [[ ! -f "$MP3_FILE" ]] || [[ ! -s "$MP3_FILE" ]]; then
    echo "❌ Error: TTS generation failed"
    exit 1
fi

MP3_SIZE=$(stat -f%z "$MP3_FILE" 2>/dev/null || stat -c%s "$MP3_FILE")
echo "✅ TTS: ${MP3_SIZE} bytes"

# ============================================================================
# Step 2: Convert to Opus CAF @ 24kHz (REQUIRED for native voice bubbles)
# ============================================================================

echo "🔄 Converting to Opus CAF..."

# This is the EXACT format iMessage expects for voice memos:
# - Opus codec (not PCM, not AAC)
# - 24000 Hz sample rate
# - Mono channel
# - CAF container
afconvert "$MP3_FILE" "$CAF_FILE" -f caff -d opus@24000 -c 1

if [[ ! -f "$CAF_FILE" ]] || [[ ! -s "$CAF_FILE" ]]; then
    echo "❌ Error: Conversion failed"
    exit 1
fi

CAF_SIZE=$(stat -f%z "$CAF_FILE" 2>/dev/null || stat -c%s "$CAF_FILE")
echo "✅ CAF: ${CAF_SIZE} bytes"

# ============================================================================
# Step 3: Send via BlueBubbles (working formula from 2026-02-19)
# ============================================================================

echo "📱 Sending to $RECIPIENT..."

# CRITICAL: chatGuid format is "any;-;+PHONE" NOT "iMessage;-;+PHONE"
# The "any" prefix works; "iMessage" causes issues
CHAT_GUID="any;-;$RECIPIENT"

# Send via BlueBubbles API with the WORKING formula:
# - method=private-api (REQUIRED for native voice bubble)
# - isAudioMessage=true (REQUIRED)
# - type=audio/x-caf on attachment
# - Pre-converted Opus CAF (don't let BlueBubbles convert)
RESPONSE=$(curl -X POST "$BLUEBUBBLES_URL/api/v1/message/attachment" \
    -H "Authorization: Bearer $BLUEBUBBLES_PASSWORD" \
    -F "attachment=@$CAF_FILE;type=audio/x-caf" \
    --form-string "chatGuid=$CHAT_GUID" \
    -F "name=voice.caf" \
    -F "tempGuid=temp-$TIMESTAMP" \
    -F "isAudioMessage=true" \
    -F "method=private-api" \
    --silent \
    --max-time 60)

# Check response
if echo "$RESPONSE" | grep -q '"isAudioMessage":true'; then
    echo "✅ Native voice bubble sent!"
    echo "📊 MP3: ${MP3_SIZE}B → CAF: ${CAF_SIZE}B"
    
    # Clean up both MP3 and CAF after successful send
    rm -f "$MP3_FILE" "$CAF_FILE"
    
    exit 0
elif echo "$RESPONSE" | grep -q '"status":200'; then
    echo "⚠️  Sent, but may not be native bubble (isAudioMessage not confirmed)"
    echo "Response: $RESPONSE"
    rm -f "$MP3_FILE" "$CAF_FILE"
    exit 0
else
    echo "❌ Error: Send failed"
    echo "Response: $RESPONSE"
    rm -f "$MP3_FILE" "$CAF_FILE"
    exit 1
fi
