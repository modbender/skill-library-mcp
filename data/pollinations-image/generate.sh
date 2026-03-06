#!/bin/sh
# Pollinations Image Generation - Main Script
# Modular, user-friendly image generation with model selection

set -e

# Get script directory
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
LIB_DIR="$SCRIPT_DIR/lib"

# Load model registry
. "$LIB_DIR/models.sh"

# Check for first-time setup
FIRST_RUN=false
if [ ! -f "$SCRIPT_DIR/.env" ] && [ ! -f "$SCRIPT_DIR/.user.conf" ]; then
    FIRST_RUN=true
fi

# Load user config if exists
USER_CONF="$SCRIPT_DIR/.user.conf"
[ -f "$USER_CONF" ] && . "$USER_CONF"

# Welcome message for first-time users
show_welcome() {
    echo ""
    echo "🎉 Welcome to Pollinations Image Generator!"
    echo "═══════════════════════════════════════════════════"
    echo ""
    echo "First time? Here's how to get started:"
    echo ""
    echo "1️⃣  See available models:"
    echo "   ./generate.sh models"
    echo ""
    echo "2️⃣  Set your default model:"
    echo "   ./generate.sh set-model flux"
    echo ""
    echo "3️⃣  Generate your first image:"
    echo "   ./generate.sh 'a cute cat'"
    echo ""
    echo "📖 Full documentation: ./SKILL.md"
    echo ""
    echo "═══════════════════════════════════════════════════"
    echo ""
    # Create a marker file so we don't show this every time
    touch "$SCRIPT_DIR/.first-run-complete"
}

if [ "$FIRST_RUN" = "true" ] && [ ! -f "$SCRIPT_DIR/.first-run-complete" ]; then
    show_welcome
fi

# Load environment
load_env_file() {
    env_path=$1
    [ -f "$env_path" ] || return 0
    while IFS= read -r line || [ -n "$line" ]; do
        case "$line" in ''|\#*) continue ;; esac
        case "$line" in *=*) ;; *) continue ;; esac
        key=${line%%=*}
        value=${line#*=}
        key=$(printf '%s' "$key" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')
        value=$(printf '%s' "$value" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')
        case "$value" in
            "*") value=${value#\"}; value=${value%\"} ;;
            '*') value=${value#\'}; value=${value%\'} ;;
        esac
        eval "is_set=\${$key+x}"
        [ -z "$is_set" ] && export "$key=$value"
    done < "$env_path"
}

load_env_file "$SCRIPT_DIR/../.env"
load_env_file "$PWD/.env"

# Config
API_KEY=${POLLINATIONS_API_KEY:-}
BASE_URL="https://gen.pollinations.ai"
OUTPUT_DIR="${OUTPUT_DIR:-$HOME/.openclaw/workspace/outputs/pollinations-image}"

# Helper functions
url_encode() {
    if command -v python3 >/dev/null 2>&1; then
        printf '%s' "$1" | python3 -c "import sys,urllib.parse; print(urllib.parse.quote(sys.stdin.read(), safe=''))"
    else
        printf '%s' "$1" | sed 's/ /%20/g'
    fi
}

slugify() {
    slug=$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9 _-]/ /g; s/[ _-]\+/-/g; s/^-//; s/-$//')
    [ -z "$slug" ] && slug="image"
    printf '%.40s' "$slug"
}

# Commands

print_help() {
    cat <<'EOF'
🎨 Pollinations Image Generator

USAGE:
  generate.sh COMMAND [OPTIONS]

COMMANDS:
  generate, g    Generate an image (default)
  models, m      List all available models
  model NAME     Show details for a specific model
  set-model NAME Set default model for future generations
  config         Show current configuration
  help           Show this help message

GENERATE OPTIONS:
  --prompt TEXT       Image description (required)
  --model MODEL       Override model for this generation
  --width N           Image width (64-2048, default: 1024)
  --height N          Image height (64-2048, default: 1024)
  --seed N            Seed for reproducibility
  --filename NAME     Custom output filename
  --nologo            Remove Pollinations watermark
  --enhance           Let AI improve your prompt

EXAMPLES:
  # List all models
  ./generate.sh models

  # Set default model to zimage (fast)
  ./generate.sh set-model zimage

  # Generate with current default model
  ./generate.sh generate --prompt "a cute cat"
  
  # Quick generation (shortcut)
  ./generate.sh g -p "a cute cat"

  # Use specific model once
  ./generate.sh g -p "artwork" --model klein-large

CONFIGURATION:
  Default model: 
EOF
    echo "    ${DEFAULT_IMAGE_MODEL:-flux}"
    echo ""
    echo "  To change: ./generate.sh set-model MODEL_NAME"
    echo ""
}

cmd_models() {
    print_models_table
}

cmd_model() {
    if [ -z "$1" ]; then
        echo "Usage: $0 model MODEL_NAME"
        echo ""
        echo "Available models:"
        get_model_ids | tr '\n' ' '
        echo ""
        exit 1
    fi
    print_model_details "$1"
}

cmd_set_model() {
    if [ -z "$1" ]; then
        echo "Usage: $0 set-model MODEL_NAME"
        echo ""
        echo "Available models:"
        get_model_ids | tr '\n' ' '
        echo ""
        exit 1
    fi
    
    if ! is_valid_model "$1"; then
        echo "❌ Error: Unknown model '$1'" >&2
        echo "Available models:" >&2
        get_model_ids | tr '\n' ' ' >&2
        echo "" >&2
        exit 1
    fi
    
    # Save to user config
    echo "# User Preferences" > "$USER_CONF"
    echo "DEFAULT_IMAGE_MODEL=$1" >> "$USER_CONF"
    
    model_info=$(get_model_info "$1" display_name)
    type=$(get_model_info "$1" type)
    
    echo "✅ Default model set to: $1 ($model_info)"
    if [ "$type" = "paid" ]; then
        echo "   ⚠️  This is a PAID model (requires pollen credits)"
    else
        echo "   🎁 This is a FREE model"
    fi
}

cmd_config() {
    echo ""
    echo "🔧 Current Configuration"
    echo "═══════════════════════════════════════"
    echo "Default model: ${DEFAULT_IMAGE_MODEL:-flux}"
    echo "Output dir:    $OUTPUT_DIR"
    echo "API Key:       ${API_KEY:+✅ configured}${API_KEY:-❌ not set}"
    echo ""
    echo "📋 Model Details:"
    print_model_details "${DEFAULT_IMAGE_MODEL:-flux}" 2>/dev/null || echo "  (unknown model)"
}

cmd_generate() {
    # Parse arguments
    prompt=""
    model="${DEFAULT_IMAGE_MODEL:-flux}"
    width="1024"
    height="1024"
    seed=""
    filename=""
    nologo="false"
    enhance="false"
    
    while [ $# -gt 0 ]; do
        case "$1" in
            -p|--prompt) shift; prompt=$1 ;;
            -m|--model) shift; model=$1 ;;
            -w|--width) shift; width=$1 ;;
            -h|--height) shift; height=$1 ;;
            -s|--seed) shift; seed=$1 ;;
            -f|--filename) shift; filename=$1 ;;
            --nologo) nologo="true" ;;
            --enhance) enhance="true" ;;
            *) 
                # If no flag and prompt is empty, treat as prompt
                if [ -z "$prompt" ] && [ "${1#-}" = "$1" ]; then
                    prompt=$1
                fi
                ;;
        esac
        shift
    done
    
    # Validate
    if [ -z "$prompt" ]; then
        echo "❌ Error: Prompt is required." >&2
        echo "Usage: $0 generate --prompt 'your description'" >&2
        exit 1
    fi
    
    if ! is_valid_model "$model"; then
        echo "❌ Error: Unknown model '$model'" >&2
        echo "Run '$0 models' to see available models." >&2
        exit 1
    fi
    
    # Validate dimensions
    if [ "$width" -gt 2048 ] || [ "$height" -gt 2048 ]; then
        echo "❌ Error: Max dimension is 2048x2048" >&2
        exit 1
    fi
    if [ "$width" -lt 64 ] || [ "$height" -lt 64 ]; then
        echo "❌ Error: Min dimension is 64x64" >&2
        exit 1
    fi
    
    # Generate filename
    if [ -z "$filename" ]; then
        timestamp=$(date +"%Y-%m-%d-%H-%M-%S")
        slug=$(slugify "$prompt")
        filename="${timestamp}-${slug}.png"
    fi
    
    # Setup output
    mkdir -p "$OUTPUT_DIR"
    output_path="$OUTPUT_DIR/$(basename "$filename")"
    
    # Build URL
    encoded_prompt=$(url_encode "$prompt")
    api_url="${BASE_URL}/image/${encoded_prompt}?width=${width}&height=${height}&model=${model}"
    [ -n "$seed" ] && api_url="${api_url}&seed=${seed}"
    [ "$nologo" = "true" ] && api_url="${api_url}&nologo=true"
    [ "$enhance" = "true" ] && api_url="${api_url}&enhance=true"
    
    # Get model info for display
    model_name=$(get_model_info "$model" display_name)
    model_type=$(get_model_info "$model" type)
    
    echo ""
    echo "🎨 Generating Image"
    echo "═══════════════════════════════════════"
    printf "  Model:  %s (%s)\n" "$model_name" "$model"
    printf "  Type:   %s\n" "$([ "$model_type" = "free" ] && echo "🎁 FREE" || echo "💰 PAID")"
    printf "  Size:   %sx%s\n" "$width" "$height"
    printf "  Prompt: %s\n" "$prompt"
    echo ""
    
    # Download
    curl_cmd="curl -sS -L -o \"$output_path\" --max-time 120"
    [ -n "$API_KEY" ] && curl_cmd="$curl_cmd -H \"Authorization: Bearer $API_KEY\""
    curl_cmd="$curl_cmd \"$api_url\""
    
    if ! eval "$curl_cmd"; then
        echo "❌ Error: Failed to generate image" >&2
        exit 1
    fi
    
    # Verify
    if ! file "$output_path" | grep -qE "PNG|JPEG|JPG|image data"; then
        echo "❌ Error: Invalid image received" >&2
        cat "$output_path" 2>/dev/null | head -c 500 >&2
        rm -f "$output_path"
        exit 1
    fi
    
    file_size=$(stat -c%s "$output_path" 2>/dev/null || stat -f%z "$output_path" 2>/dev/null || echo "?")
    
    echo "✅ Image generated successfully!"
    echo ""
    echo "📁 File: $(basename "$output_path")"
    echo "📊 Size: ${file_size} bytes"
    echo "📂 Path: $(realpath "$output_path")"
    echo ""
}

# Main entry point

COMMAND=${1:-generate}
shift || true

case "$COMMAND" in
    generate|g)
        cmd_generate "$@"
        ;;
    models|m|list)
        cmd_models
        ;;
    model)
        cmd_model "$@"
        ;;
    set-model|set)
        cmd_set_model "$@"
        ;;
    config|cfg)
        cmd_config
        ;;
    help|--help|-h)
        print_help
        ;;
    *)
        # If first arg doesn't look like a command, treat as generate with prompt
        if [ -n "$COMMAND" ] && [ "${COMMAND#-}" = "$COMMAND" ]; then
            cmd_generate --prompt "$COMMAND" "$@"
        else
            echo "Unknown command: $COMMAND" >&2
            echo "Run '$0 help' for usage." >&2
            exit 1
        fi
        ;;
esac
