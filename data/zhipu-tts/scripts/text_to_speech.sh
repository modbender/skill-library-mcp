#!/bin/bash
# Zhipu AI Text-to-Speech Script
# Usage: ./text_to_speech.sh "text" [voice] [speed] [output_format]

set -e

# Configuration
API_ENDPOINT="https://open.bigmodel.cn/api/paas/v4/audio/speech"

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
TEXT="$1"
VOICE="${2:-tongtong}"
SPEED="${3:-1.0}"
OUTPUT_FORMAT="${4:-wav}"
OUTPUT_FILE="${5:-output.${OUTPUT_FORMAT}}"

# Validate text
if [ -z "$TEXT" ]; then
    echo "Usage: $0 \"text\" [voice] [speed] [output_format] [output_file]" >&2
    echo "" >&2
    echo "Examples:" >&2
    echo "  $0 \"你好，今天天气怎么样\"" >&2
    echo "  $0 \"欢迎使用智能语音服务\" xiaochen 1.2 wav greeting.wav" >&2
    echo "" >&2
    echo "Voices: tongtong (default), chuichui, xiaochen, jam, kazi, douji, luodo" >&2
    echo "Speed: 0.5-2.0 (default: 1.0)" >&2
    echo "Format: wav (default), pcm" >&2
    exit 1
fi

# Build request payload
PAYLOAD=$(jq -n \
    --arg model "glm-tts" \
    --arg input "$TEXT" \
    --arg voice "$VOICE" \
    --argjson speed "$SPEED" \
    --arg response_format "$OUTPUT_FORMAT" \
    '{
        model: $model,
        input: $input,
        voice: $voice,
        speed: $speed,
        response_format: $response_format
    }')

# Make API request
echo "Converting text to speech..." >&2
echo "Voice: $VOICE, Speed: $SPEED, Format: $OUTPUT_FORMAT" >&2
echo "" >&2

RESPONSE=$(curl -s -X POST "$API_ENDPOINT" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $ZHIPU_API_KEY" \
    -d "$PAYLOAD" \
    --output "$OUTPUT_FILE" \
    -w "%{http_code}")

# Check for errors
if [ "$RESPONSE" != "200" ]; then
    echo "Error: HTTP $RESPONSE" >&2
    if [ -f "$OUTPUT_FILE" ]; then
        cat "$OUTPUT_FILE" >&2
        rm "$OUTPUT_FILE"
    fi
    exit 1
fi

echo "Audio saved to: $OUTPUT_FILE" >&2
echo "Text: $TEXT" >&2

# Get file info
if command -v file &> /dev/null; then
    FILE_INFO=$(file "$OUTPUT_FILE")
    echo "File info: $FILE_INFO" >&2
fi

if command -v ls &> /dev/null; then
    FILE_SIZE=$(ls -lh "$OUTPUT_FILE" | awk '{print $5}')
    echo "File size: $FILE_SIZE" >&2
fi

echo "$OUTPUT_FILE"
