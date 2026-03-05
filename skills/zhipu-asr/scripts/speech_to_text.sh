#!/bin/bash
# Zhipu AI Speech-to-Text Script
# Usage: ./speech_to_text.sh <audio_file> [prompt] [hotwords]

set -e

# Configuration
API_ENDPOINT="https://open.bigmodel.cn/api/paas/v4/audio/transcriptions"

# Get API key from environment
if [ -z "$ZHIPU_API_KEY" ]; then
    echo "Error: ZHIPU_API_KEY environment variable is not set" >&2
    echo "" >&2
    echo "To fix:" >&2
    echo "1. Get a key from https://bigmodel.cn/usercenter/proj-mgmt/apikeys" >&2
    echo "2. Run: export ZHIPU_API_KEY=\"your-key\"" >&2
    exit 1
fi

# Parse arguments
AUDIO_FILE="$1"
PROMPT="$2"
HOTWORDS="$3"

# Validate audio file
if [ -z "$AUDIO_FILE" ]; then
    echo "Usage: $0 <audio_file> [prompt] [hotwords]" >&2
    echo "" >&2
    echo "Examples:" >&2
    echo "  $0 recording.wav" >&2
    echo "  $0 recording.wav \"这是之前的转录内容\"" >&2
    echo "  $0 recording.mp3 \"\" \"人名,地名,专业术语\"" >&2
    echo "" >&2
    echo "Supported formats: .wav, .mp3, .ogg, .m4a, .aac, .flac, .wma" >&2
    echo "Max file size: 25 MB" >&2
    echo "Max duration: 30 seconds" >&2
    exit 1
fi

# Check if file exists
if [ ! -f "$AUDIO_FILE" ]; then
    echo "Error: Audio file not found: $AUDIO_FILE" >&2
    exit 1
fi

# Auto-convert audio format if needed
ORIGINAL_FILE="$AUDIO_FILE"
FILE_EXT="${AUDIO_FILE##*.}"
FILE_EXT=$(echo "$FILE_EXT" | tr '[:upper:]' '[:lower:]')

# Supported formats by API: wav, mp3
# Convert other formats to mp3
if [ "$FILE_EXT" != "wav" ] && [ "$FILE_EXT" != "mp3" ]; then
    echo "Converting audio format: $FILE_EXT → mp3" >&2

    # Check if ffmpeg is available
    if ! command -v ffmpeg &> /dev/null; then
        echo "Error: ffmpeg is required for format conversion" >&2
        echo "Install with: yum install -y ffmpeg" >&2
        exit 1
    fi

    # Create temp file for converted audio
    TEMP_AUDIO=$(mktemp --suffix=.mp3)

    # Convert to mp3 with optimal settings for ASR
    ffmpeg -i "$AUDIO_FILE" \
        -acodec libmp3lame \
        -ar 16000 \
        -ac 1 \
        -b:a 64k \
        -y \
        "$TEMP_AUDIO" 2>&1 | grep -E "(Duration|size=)" || true

    # Replace AUDIO_FILE with converted file
    AUDIO_FILE="$TEMP_AUDIO"

    echo "Conversion complete: $TEMP_AUDIO" >&2
    echo "" >&2

    # Cleanup function for temp file
    cleanup() {
        if [ -f "$TEMP_AUDIO" ]; then
            rm -f "$TEMP_AUDIO"
        fi
    }
    trap cleanup EXIT
else
    # No conversion needed, no cleanup required
    cleanup() { :; }
    trap cleanup EXIT
fi

# Check file size (25 MB limit)
FILE_SIZE=$(stat -c%s "$AUDIO_FILE" 2>/dev/null || stat -f%z "$AUDIO_FILE" 2>/dev/null || echo "0")
MAX_SIZE=$((25 * 1024 * 1024))
if [ "$FILE_SIZE" -gt "$MAX_SIZE" ]; then
    echo "Error: File size exceeds 25 MB limit" >&2
    echo "Current size: $(($FILE_SIZE / 1024 / 1024)) MB" >&2
    exit 1
fi

# Build base payload
PAYLOAD=$(jq -n \
    --arg model "glm-asr-2512" \
    '{
        model: $model
    }')

# Add prompt if provided
if [ -n "$PROMPT" ]; then
    PAYLOAD=$(echo "$PAYLOAD" | jq --arg prompt "$PROMPT" '. + {prompt: $prompt}')
fi

# Add hotwords if provided
if [ -n "$HOTWORDS" ]; then
    # Convert comma-separated hotwords to JSON array
    HOTWORDS_ARRAY=$(echo "$HOTWORDS" | jq -R 'split(",") | map(trim)')
    PAYLOAD=$(echo "$PAYLOAD" | jq --argjson hotwords "$HOTWORDS_ARRAY" '. + {hotwords: $hotwords}')
fi

# Make API request
echo "Transcribing audio file: $AUDIO_FILE" >&2
if [ -n "$PROMPT" ]; then
    echo "Using context prompt: $(echo "$PROMPT" | cut -c1-50)..." >&2
fi
if [ -n "$HOTWORDS" ]; then
    echo "Hotwords: $HOTWORDS" >&2
fi
echo "" >&2

# Build curl command arguments
CURL_ARGS=()
CURL_ARGS+=(-H "Authorization: Bearer $ZHIPU_API_KEY")
CURL_ARGS+=(-F "file=@$AUDIO_FILE")
CURL_ARGS+=(-F "model=glm-asr-2512")

if [ -n "$PROMPT" ]; then
    CURL_ARGS+=(-F "prompt=$PROMPT")
fi

if [ -n "$HOTWORDS" ]; then
    # Convert comma-separated to array format for curl
    IFS=',' read -ra HW_ARRAY <<< "$HOTWORDS"
    for word in "${HW_ARRAY[@]}"; do
        word=$(echo "$word" | xargs)
        CURL_ARGS+=(-F "hotwords[]=$word")
    done
fi

RESPONSE=$(curl -s -X POST "$API_ENDPOINT" "${CURL_ARGS[@]}")

# Check for errors
if echo "$RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
    ERROR_MSG=$(echo "$RESPONSE" | jq -r '.error.message // .error')
    echo "Error: $ERROR_MSG" >&2
    exit 1
fi

# Extract and display result
echo "$RESPONSE" | jq '.'

TRANSCRIBED_TEXT=$(echo "$RESPONSE" | jq -r '.text // empty')

if [ -n "$TRANSCRIBED_TEXT" ]; then
    echo "" >&2
    echo "Transcribed text:" >&2
    echo "$TRANSCRIBED_TEXT" >&2
fi
