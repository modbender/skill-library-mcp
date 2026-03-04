#!/bin/bash
# clawra-selfie-enhanced.sh
# Generate images with Grok Imagine (fal.ai) or MiniMax and send via OpenClaw
#
# Usage: ./clawra-selfie-enhanced.sh "<prompt>" "<channel>" ["<caption>"] ["<provider>"]
#
# Environment variables:
#   FAL_KEY      - fal.ai API key (for fal.ai provider)
#   MINIMAX_API_KEY - MiniMax API key (for minimax provider)
#
# Example:
#   FAL_KEY=xxx ./clawra-selfie-enhanced.sh "A coffee shop" "telegram" "My coffee"
#   MINIMAX_API_KEY=xxx ./clawra-selfie-enhanced.sh "A coffee shop" "telegram" "My coffee" "minimax"

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_debug() { echo -e "${BLUE}[DEBUG]${NC} $1"; }

# Check for jq
if ! command -v jq &> /dev/null; then
    log_error "jq is required"
    exit 1
fi

# Check for curl
if ! command -v curl &> /dev/null; then
    log_error "curl is required"
    exit 1
fi

# Parse arguments
PROMPT="${1:-}"
CHANNEL="${2:-}"
CAPTION="${3:-Generated with AI}"
PROVIDER="${4:-auto}"  # auto, fal, minimax

if [ -z "$PROMPT" ] || [ -z "$CHANNEL" ]; then
    echo "Usage: $0 <prompt> <channel> [caption] [provider]"
    echo ""
    echo "Arguments:"
    echo "  prompt   - Image description (required)"
    echo "  channel  - Target channel (required)"
    echo "  caption  - Message caption (default: 'Generated with AI')"
    echo "  provider - 'fal', 'minimax', or 'auto' (default: auto)"
    echo ""
    echo "Environment variables:"
    echo "  FAL_KEY        - fal.ai API key"
    echo "  MINIMAX_API_KEY - MiniMax API key"
    echo ""
    echo "Examples:"
    echo "  FAL_KEY=xxx $ shop\" \"t0 \"A coffeeelegram\""
    echo "  MINIMAX_API_KEY=xxx $0 \"A coffee shop\" \"telegram\" \"minimax\""
    exit 1
fi

# Detect provider automatically
detect_provider() {
    if [ "$PROVIDER" != "auto" ]; then
        echo "$PROVIDER"
        return
    fi
    
    # Priority: MiniMax > fal.ai (because fal.ai might be out of credits)
    if [ -n "${MINIMAX_API_KEY:-}" ]; then
        echo "minimax"
    elif [ -n "${FAL_KEY:-}" ]; then
        echo "fal"
    else
        log_error "No API key found. Set MINIMAX_API_KEY or FAL_KEY"
        exit 1
    fi
}

# Get aspect ratio mapping for MiniMax
map_aspect_ratio() {
    local ratio="$1"
    case "$ratio" in
        "2:1"|"21:9") echo "21:9" ;;
        "16:9") echo "16:9" ;;
        "4:3") echo "4:3" ;;
        "1:1") echo "1:1" ;;
        "3:4") echo "3:4" ;;
        "9:16") echo "9:16" ;;
        *) echo "1:1" ;;
    esac
}

# Generate image with MiniMax
generate_minimax() {
    log_info "Generating image with MiniMax..."
    log_info "Prompt: $PROMPT"
    
    local aspect=$(map_aspect_ratio "$ASPECT_RATIO")
    
    RESPONSE=$(curl -s -X POST "https://api.minimaxi.com/v1/image_generation" \
        -H "Authorization: Bearer $MINIMAX_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{
            \"model\": \"image-01\",
            \"prompt\": \"$PROMPT\",
            \"aspect_ratio\": \"$aspect\",
            \"response_format\": \"base64\"
        }")
    
    # Check for errors
    if echo "$RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
        ERROR_MSG=$(echo "$RESPONSE" | jq -r '.error // "Unknown error"')
        log_error "MiniMax API error: $ERROR_MSG"
        exit 1
    fi
    
    # Extract base64 image
    IMAGE_BASE64=$(echo "$RESPONSE" | jq -r '.data.image_base64[0] // empty')
    
    if [ -z "$IMAGE_BASE64" ]; then
        log_error "Failed to extract image from MiniMax response"
        echo "Response: $RESPONSE"
        exit 1
    fi
    
    log_info "Image generated successfully!"
    
    # For MiniMax, save to temp file and encode
    TEMP_FILE=$(mktemp --suffix=.jpeg)
    echo "$IMAGE_BASE64" | base64 -d > "$TEMP_FILE" 2>/dev/null || echo "$IMAGE_BASE64" | base64 -d -o "$TEMP_FILE"
    
    log_info "Image saved to: $TEMP_FILE"
}

# Generate image with fal.ai
generate_fal() {
    log_info "Generating image with fal.ai (Grok Imagine)..."
    log_info "Prompt: $PROMPT"
    
    RESPONSE=$(curl -s -X POST "https://fal.run/xai/grok-imagine-image" \
        -H "Authorization: Key $FAL_KEY" \
        -H "Content-Type: application/json" \
        -d "{
            \"prompt\": $(echo "$PROMPT" | jq -Rs .),
            \"num_images\": 1,
            \"aspect_ratio\": \"$ASPECT_RATIO\",
            \"output_format\": \"jpeg\"
        }")
    
    # Check for errors
    if echo "$RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
        ERROR_MSG=$(echo "$RESPONSE" | jq -r '.error // .detail // "Unknown error"')
        log_error "fal.ai error: $ERROR_MSG"
        exit 1
    fi
    
    # Extract URL
    IMAGE_URL=$(echo "$RESPONSE" | jq -r '.images[0].url // empty')
    
    if [ -z "$IMAGE_URL" ]; then
        log_error "Failed to extract URL from fal.ai response"
        echo "Response: $RESPONSE"
        exit 1
    fi
    
    log_info "Image generated: $IMAGE_URL"
}

# Send image via OpenClaw
send_image() {
    log_info "Sending to channel: $CHANNEL"
    
    if command -v openclaw &> /dev/null; then
        # Try with file path first (if we have a temp file)
        if [ -n "${TEMP_FILE:-}" ] && [ -f "$TEMP_FILE" ]; then
            openclaw message send \
                --target "$CHANNEL" \
                --message "$CAPTION" \
                --media "$TEMP_FILE"
        else
            openclaw message send \
                --target "$CHANNEL" \
                --message "$CAPTION" \
                --media "$IMAGE_URL"
        fi
    else
        # Direct API call
        GATEWAY_URL="${OPENCLAW_GATEWAY_URL:-http://localhost:18789}"
        GATEWAY_TOKEN="${OPENCLAW_GATEWAY_TOKEN:-}"
        
        curl -s -X POST "$GATEWAY_URL/message" \
            -H "Content-Type: application/json" \
            ${GATEWAY_TOKEN:+-H "Authorization: Bearer $GATEWAY_TOKEN"} \
            -d "{
                \"action\": \"send\",
                \"channel\": \"$CHANNEL\",
                \"message\": \"$CAPTION\",
                \"media\": \"$IMAGE_URL\"
            }"
    fi
    
    log_info "Done! Image sent to $CHANNEL"
    
    # Cleanup temp file
    if [ -n "${TEMP_FILE:-}" ] && [ -f "$TEMP_FILE" ]; then
        rm -f "$TEMP_FILE"
    fi
}

# Main
ASPECT_RATIO="${5:-1:1}"
PROVIDER=$(detect_provider)

case "$PROVIDER" in
    "minimax")
        generate_minimax
        ;;
    "fal"|"fal.ai")
        generate_fal
        ;;
    *)
        log_error "Unknown provider: $PROVIDER"
        exit 1
        ;;
esac

send_image

# Output JSON result
echo ""
echo "--- Result ---"
jq -n \
    --arg url "$IMAGE_URL" \
    --arg channel "$CHANNEL" \
    --arg prompt "$PROMPT" \
    --arg provider "$PROVIDER" \
    --arg tempFile "${TEMP_FILE:-}" \
    '{
        success: true,
        image_url: $url,
        channel: $channel,
        prompt: $prompt,
        provider: $provider,
        temp_file: $tempFile
    }'
