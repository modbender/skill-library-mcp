#!/bin/bash

# Seedance Video Generation Script
# Usage: ./seedance-gen.sh "prompt" [--image urls] [--duration 5] [--quality 720p] [--aspect-ratio 16:9]
# Requires: jq, curl
# API endpoint: https://api.evolink.ai (hardcoded, not configurable)

set -euo pipefail

# Constants
readonly API_BASE="https://api.evolink.ai"
readonly MAX_POLL_SECONDS=180
readonly POLL_FAST_INTERVAL=5
readonly POLL_SLOW_INTERVAL=10
readonly POLL_SLOW_AFTER=30

# Default values
DURATION=5
QUALITY="720p"
ASPECT_RATIO="16:9"
GENERATE_AUDIO="true"
IMAGE_URLS=""
PROMPT=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
error() {
    echo -e "${RED}ERROR: $1${NC}" >&2
    exit 1
}

info() {
    echo -e "${BLUE}INFO: $1${NC}"
}

success() {
    echo -e "${GREEN}SUCCESS: $1${NC}"
}

warn() {
    echo -e "${YELLOW}WARNING: $1${NC}"
}

# Check dependencies
check_dependencies() {
    if ! command -v jq &> /dev/null; then
        error "jq is required but not installed. Install it with:
  apt install jq   # Debian/Ubuntu
  brew install jq   # macOS"
    fi
    if ! command -v curl &> /dev/null; then
        error "curl is required but not installed."
    fi
}

# Check API key
check_api_key() {
    if [[ -z "${EVOLINK_API_KEY:-}" ]]; then
        error "EVOLINK_API_KEY environment variable is required.

To get started:
1. Register at: https://evolink.ai
2. Get your API key from the dashboard
3. Set the environment variable:
   export EVOLINK_API_KEY=your_key_here"
    fi
}

# Parse command line arguments
parse_args() {
    if [[ $# -eq 0 ]]; then
        error "Usage: $0 \"prompt\" [--image urls] [--duration 5] [--quality 720p] [--aspect-ratio 16:9] [--no-audio]

Examples:
  $0 \"A serene sunset over ocean waves\"
  $0 \"Dancing cat\" --duration 4 --quality 480p
  $0 \"Beach scene\" --image \"url1.jpg,url2.jpg\" --aspect-ratio 16:9"
    fi

    PROMPT="$1"
    shift

    while [[ $# -gt 0 ]]; do
        case $1 in
            --image)
                IMAGE_URLS="$2"
                shift 2
                ;;
            --duration)
                DURATION="$2"
                if [[ ! "$DURATION" =~ ^[0-9]+$ ]] || [[ "$DURATION" -lt 4 ]] || [[ "$DURATION" -gt 12 ]]; then
                    error "Duration must be between 4-12 seconds"
                fi
                shift 2
                ;;
            --quality)
                QUALITY="$2"
                if [[ ! "$QUALITY" =~ ^(480p|720p|1080p)$ ]]; then
                    error "Quality must be 480p, 720p, or 1080p"
                fi
                shift 2
                ;;
            --aspect-ratio)
                ASPECT_RATIO="$2"
                if [[ ! "$ASPECT_RATIO" =~ ^(16:9|9:16|1:1|4:3|3:4|21:9)$ ]]; then
                    error "Aspect ratio must be one of: 16:9, 9:16, 1:1, 4:3, 3:4, 21:9"
                fi
                shift 2
                ;;
            --no-audio)
                GENERATE_AUDIO="false"
                shift
                ;;
            *)
                error "Unknown parameter: $1"
                ;;
        esac
    done
}

# Build JSON payload safely using jq (no shell injection)
build_payload() {
    local json_payload
    json_payload=$(jq -n \
        --arg model "seedance-1.5-pro" \
        --arg prompt "$PROMPT" \
        --argjson duration "$DURATION" \
        --arg quality "$QUALITY" \
        --arg aspect_ratio "$ASPECT_RATIO" \
        --argjson generate_audio "$GENERATE_AUDIO" \
        '{model: $model, prompt: $prompt, duration: $duration, quality: $quality, aspect_ratio: $aspect_ratio, generate_audio: $generate_audio}')

    if [[ -n "$IMAGE_URLS" ]]; then
        # Convert comma-separated URLs to JSON array safely via jq
        local url_array="[]"
        IFS=',' read -ra URLS <<< "$IMAGE_URLS"
        for url in "${URLS[@]}"; do
            url=$(echo "$url" | xargs)  # trim whitespace
            url_array=$(echo "$url_array" | jq --arg u "$url" '. + [$u]')
        done
        json_payload=$(echo "$json_payload" | jq --argjson urls "$url_array" '. + {image_urls: $urls}')
    fi

    echo "$json_payload"
}

# Handle API errors with user-friendly messages
handle_error() {
    local status_code=$1
    local response_body=$2

    case $status_code in
        401)
            error "Invalid API key.
→ Check your key at: https://evolink.ai/dashboard"
            ;;
        402)
            error "Insufficient account balance.
→ Add credits at: https://evolink.ai/dashboard"
            ;;
        429)
            error "Rate limit exceeded. Please wait a few seconds and try again."
            ;;
        503)
            error "Service temporarily unavailable. Please try again later."
            ;;
        400)
            local error_msg
            error_msg=$(echo "$response_body" | jq -r '.error // .message // empty' 2>/dev/null || echo "")
            if echo "$error_msg" | grep -qi "face\|人脸"; then
                error "Content blocked: Realistic faces not supported.
→ Please modify your prompt to avoid human faces."
            elif echo "$error_msg" | grep -qi "file.*large\|size.*exceed"; then
                error "File size error: Images must be ≤30MB each."
            else
                error "Request error (400): ${error_msg:-$response_body}"
            fi
            ;;
        *)
            error "API error ($status_code): $response_body"
            ;;
    esac
}

# Submit generation request
submit_generation() {
    local payload
    payload=$(build_payload)

    # Minimal output — only final result matters

    local http_code response_body
    response_body=$(curl --fail-with-body --show-error --silent \
        -w "\n%{http_code}" \
        -X POST "${API_BASE}/v1/videos/generations" \
        -H "Authorization: Bearer ${EVOLINK_API_KEY}" \
        -H "Content-Type: application/json" \
        -d "$payload" 2>&1) || true

    http_code=$(echo "$response_body" | tail -n1)
    response_body=$(echo "$response_body" | sed '$d')

    if [[ "$http_code" != "200" ]]; then
        handle_error "$http_code" "$response_body"
    fi

    # Extract task_id using jq
    local task_id
    task_id=$(echo "$response_body" | jq -r '.id // .task_id // empty' 2>/dev/null)

    if [[ -z "$task_id" ]]; then
        error "Failed to extract task_id from response: $response_body"
    fi

    GLOBAL_TASK_ID="$task_id"
}

# Poll task status
poll_task() {
    local task_id=$1
    local start_time
    start_time=$(date +%s)
    local poll_interval=$POLL_FAST_INTERVAL

    # Silent polling — no output until completion or failure
    while true; do
        local current_time elapsed
        current_time=$(date +%s)
        elapsed=$((current_time - start_time))

        if [[ $elapsed -gt $MAX_POLL_SECONDS ]]; then
            warn "Generation is taking longer than expected (>${MAX_POLL_SECONDS}s). Task ${task_id} may still be processing."
            exit 1
        fi

        if [[ $elapsed -gt $POLL_SLOW_AFTER ]]; then
            poll_interval=$POLL_SLOW_INTERVAL
        fi

        sleep "$poll_interval"

        local http_code response_body
        response_body=$(curl --fail-with-body --show-error --silent \
            -w "\n%{http_code}" \
            -X GET "${API_BASE}/v1/tasks/${task_id}" \
            -H "Authorization: Bearer ${EVOLINK_API_KEY}" 2>&1) || true

        http_code=$(echo "$response_body" | tail -n1)
        response_body=$(echo "$response_body" | sed '$d')

        if [[ "$http_code" != "200" ]]; then
            handle_error "$http_code" "$response_body"
        fi

        local task_status
        task_status=$(echo "$response_body" | jq -r '.status // empty' 2>/dev/null)

        case "$task_status" in
            "completed")
                local video_url
                video_url=$(echo "$response_body" | jq -r '
                    (.results // [])[0] //
                    .video_url //
                    .url //
                    empty
                ' 2>/dev/null)

                if [[ -n "$video_url" && "$video_url" != "null" ]]; then
                    echo "VIDEO_URL=$video_url"
                    echo "ELAPSED=${elapsed}s"
                    return 0
                else
                    error "Task completed but no video URL found in response: $response_body"
                fi
                ;;
            "failed")
                local error_msg
                error_msg=$(echo "$response_body" | jq -r '.error // "Unknown error"' 2>/dev/null)
                error "Generation failed: $error_msg"
                ;;
            "processing"|"pending")
                # Silent — no output during polling
                ;;
            *)
                # Silent — no output for unknown status
                ;;
        esac
    done
}

# Main execution
main() {
    check_dependencies
    check_api_key
    parse_args "$@"

    submit_generation
    poll_task "$GLOBAL_TASK_ID"
}

main "$@"
