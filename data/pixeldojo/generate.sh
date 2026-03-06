#!/bin/bash
set -euo pipefail

# PixelDojo Generation Script
# Usage: generate.sh <image|video> <prompt> <model> [options]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="${HOME}/.openclaw/workspace"
# Default output to Pictures for easy access, fallback to workspace
PICTURES_DIR="${HOME}/Pictures/AI Generated"
OUTPUT_DIR="${PICTURES_DIR}"
API_BASE="https://pixeldojo.ai/api/v1"
API_KEY="${PIXELDOJO_API_KEY:-}"

if [[ -z "$API_KEY" ]]; then
    echo "Error: PIXELDOJO_API_KEY environment variable not set"
    exit 1
fi

# Parse arguments
TYPE="${1:-}"
PROMPT="${2:-}"
MODEL="${3:-}"

if [[ -z "$TYPE" || -z "$PROMPT" || -z "$MODEL" ]]; then
    echo "Usage: generate.sh <image|video> <prompt> <model> [options]"
    echo ""
    echo "Options:"
    echo "  --aspect-ratio <ratio>   Aspect ratio (16:9, 9:16, 1:1, 4:3, 3:4)"
    echo "  --duration <seconds>     Video duration (1-10 seconds)"
    echo "  --image-url <url>        Input image for image-to-video"
    echo "  --output <path>          Custom output path"
    echo "  --poll-interval <secs>   Polling interval (default: 3)"
    echo "  --max-wait <seconds>     Maximum wait time (default: 300)"
    exit 1
fi

# Parse options
ASPECT_RATIO="1:1"
DURATION=""
IMAGE_URL=""
CUSTOM_OUTPUT=""
POLL_INTERVAL=3
MAX_WAIT=300

shift 3
while [[ $# -gt 0 ]]; do
    case $1 in
        --aspect-ratio)
            ASPECT_RATIO="$2"
            shift 2
            ;;
        --duration)
            DURATION="$2"
            shift 2
            ;;
        --image-url)
            IMAGE_URL="$2"
            shift 2
            ;;
        --output)
            CUSTOM_OUTPUT="$2"
            shift 2
            ;;
        --poll-interval)
            POLL_INTERVAL="$2"
            shift 2
            ;;
        --max-wait)
            MAX_WAIT="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Build request body using jq
build_payload() {
    local payload
    if [[ "$TYPE" == "video" ]]; then
        if [[ -n "$IMAGE_URL" && -n "$DURATION" ]]; then
            payload=$(jq -n --arg prompt "$PROMPT" --arg aspect "$ASPECT_RATIO" --arg duration "$DURATION" --arg image "$IMAGE_URL" '{prompt: $prompt, aspect_ratio: $aspect, duration: ($duration | tonumber), image_url: $image}')
        elif [[ -n "$DURATION" ]]; then
            payload=$(jq -n --arg prompt "$PROMPT" --arg aspect "$ASPECT_RATIO" --arg duration "$DURATION" '{prompt: $prompt, aspect_ratio: $aspect, duration: ($duration | tonumber)}')
        else
            payload=$(jq -n --arg prompt "$PROMPT" --arg aspect "$ASPECT_RATIO" '{prompt: $prompt, aspect_ratio: $aspect}')
        fi
    else
        payload=$(jq -n --arg prompt "$PROMPT" --arg aspect "$ASPECT_RATIO" '{prompt: $prompt, aspect_ratio: $aspect}')
    fi
    echo "$payload"
}

# Submit job
echo "Submitting $TYPE generation job..."
echo "Model: $MODEL"
echo "Prompt: $PROMPT"

SUBMIT_RESPONSE=$(curl -sS -X POST "${API_BASE}/models/${MODEL}/run" \
    -H "Authorization: Bearer ${API_KEY}" \
    -H "Content-Type: application/json" \
    -d "$(build_payload)")

JOB_ID=$(echo "$SUBMIT_RESPONSE" | jq -r '.jobId // empty')
STATUS_URL=$(echo "$SUBMIT_RESPONSE" | jq -r '.statusUrl // empty')

if [[ -z "$JOB_ID" || "$JOB_ID" == "null" ]]; then
    echo "Error: Failed to submit job"
    echo "Response: $SUBMIT_RESPONSE"
    exit 1
fi

echo "Job ID: $JOB_ID"
echo "Polling for completion..."

# Poll for completion
START_TIME=$(date +%s)
while true; do
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - START_TIME))
    
    if [[ $ELAPSED -gt $MAX_WAIT ]]; then
        echo "Error: Timeout after ${MAX_WAIT} seconds"
        echo "Job ID: $JOB_ID"
        exit 1
    fi
    
    STATUS_RESPONSE=$(curl -sS "${API_BASE}/jobs/${JOB_ID}" \
        -H "Authorization: Bearer ${API_KEY}")
    
    STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.status // "unknown"')
    
    if [[ "$STATUS" == "completed" ]]; then
        echo "✓ Generation complete!"
        break
    elif [[ "$STATUS" == "failed" ]]; then
        echo "✗ Generation failed"
        echo "Response: $STATUS_RESPONSE"
        exit 1
    fi
    
    echo -n "."
    sleep "$POLL_INTERVAL"
done

# Extract output URL (handle both single and array formats)
OUTPUT_URL=$(echo "$STATUS_RESPONSE" | jq -r '.output.image // .output.video // .output.images[0] // .output.videos[0] // empty')

if [[ -z "$OUTPUT_URL" || "$OUTPUT_URL" == "null" ]]; then
    echo "Error: No output URL in response"
    echo "Response: $STATUS_RESPONSE"
    exit 1
fi

# Determine file extension
if [[ "$TYPE" == "video" ]]; then
    EXT="mp4"
    SUBDIR="videos"
else
    EXT="png"
    SUBDIR="images"
fi

# Create output directory
mkdir -p "${OUTPUT_DIR}/${SUBDIR}"

# Generate filename
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PROMPT_SNIPPET=$(echo "$PROMPT" | tr '[:upper:]' '[:lower:]' | tr ' ' '_' | cut -c1-30 | sed 's/[^a-z0-9_]//g')
FILENAME="${TIMESTAMP}_${PROMPT_SNIPPET}.${EXT}"

if [[ -n "$CUSTOM_OUTPUT" ]]; then
    OUTPUT_PATH="$CUSTOM_OUTPUT"
else
    OUTPUT_PATH="${OUTPUT_DIR}/${SUBDIR}/${FILENAME}"
fi

# Download result
echo ""
echo "Downloading result..."
curl -sS -L "$OUTPUT_URL" -o "$OUTPUT_PATH"

if [[ -f "$OUTPUT_PATH" ]]; then
    FILE_SIZE=$(stat -f%z "$OUTPUT_PATH" 2>/dev/null || stat -c%s "$OUTPUT_PATH" 2>/dev/null || echo "unknown")
    echo "✓ Saved to: $OUTPUT_PATH"
    echo "  Size: $FILE_SIZE bytes"
else
    echo "✗ Download failed"
    exit 1
fi

# Output JSON for programmatic use
cat <<EOF
{
  "success": true,
  "jobId": "$JOB_ID",
  "type": "$TYPE",
  "model": "$MODEL",
  "outputPath": "$OUTPUT_PATH",
  "prompt": "$PROMPT"
}
EOF
