#!/usr/bin/env bash
# generate_and_send.sh — Full pipeline: Mermaid content → PNG → Telegram
#
# This is the main entry point the OpenClaw agent calls.
# It chains render + send into a single command.
#
# Usage: ./generate_and_send.sh <chat_id> [caption]
#
# Reads Mermaid mindmap syntax from STDIN.
#
# Example:
#   echo "mindmap
#     root((Today))
#       (Tasks)
#         Do the thing
#   " | ./generate_and_send.sh 123456789 "Here's your day!"
#
# Dependencies:
#   - Node.js v18+
#   - @mermaid-js/mermaid-cli
#   - curl
#   - TELEGRAM_BOT_TOKEN env var

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHAT_ID="${1:?Usage: echo '<mermaid>' | generate_and_send.sh <chat_id> [caption]}"
CAPTION="${2:-🗺️ Here's your mindmap}"

# Generate unique temp filenames
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
INPUT_FILE="/tmp/mindmap_${TIMESTAMP}.mmd"
OUTPUT_FILE="/tmp/mindmap_${TIMESTAMP}.png"

# Read mermaid content from STDIN
if [[ -t 0 ]]; then
    echo "Error: No input provided. Pipe Mermaid mindmap syntax via STDIN." >&2
    echo "Example: echo 'mindmap\n  root((Topic))' | $0 $CHAT_ID" >&2
    exit 1
fi

cat > "$INPUT_FILE"

# Validate we got content
if [[ ! -s "$INPUT_FILE" ]]; then
    echo "Error: Empty input received" >&2
    exit 1
fi

echo "📝 Step 1/3: Received mindmap content ($(wc -l < "$INPUT_FILE" | tr -d ' ') lines)"

# Step 1: Render to PNG
echo "🎨 Step 2/3: Rendering mindmap to PNG..."
"$SCRIPT_DIR/render_mindmap.sh" "$INPUT_FILE" "$OUTPUT_FILE"

if [[ $? -ne 0 || ! -f "$OUTPUT_FILE" ]]; then
    echo "Error: Rendering failed. Sending text fallback to Telegram..." >&2

    # Fallback: send the raw content as a text message
    TEXT_CONTENT=$(cat "$INPUT_FILE")
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
        -F "chat_id=$CHAT_ID" \
        -F "text=⚠️ Couldn't render the mindmap as an image. Here's the structure:\n\n$TEXT_CONTENT" \
        -F "parse_mode=HTML" \
        > /dev/null 2>&1

    rm -f "$INPUT_FILE"
    exit 1
fi

# Step 2: Send to Telegram
echo "📱 Step 3/3: Sending to Telegram..."
"$SCRIPT_DIR/send_telegram_photo.sh" "$OUTPUT_FILE" "$CAPTION" "$CHAT_ID"

# Cleanup temp files
rm -f "$INPUT_FILE" "$OUTPUT_FILE"

echo "🎉 Done! Mindmap delivered to Telegram."
