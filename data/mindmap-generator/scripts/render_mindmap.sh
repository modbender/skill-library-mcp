#!/usr/bin/env bash
# render_mindmap.sh — Renders Mermaid mindmap syntax to PNG image
#
# Usage: ./render_mindmap.sh <input.mmd> <output.png> [width] [height]
#
# Dependencies:
#   - Node.js v18+
#   - @mermaid-js/mermaid-cli (installed globally or via npx)
#
# The output PNG is optimized for Telegram viewing:
#   - Default 1200x800 for good readability on mobile
#   - White background (no transparency — looks clean in Telegram dark mode too)
#   - Scale factor 2x for retina displays

set -euo pipefail

INPUT_FILE="${1:?Usage: render_mindmap.sh <input.mmd> <output.png> [width] [height]}"
OUTPUT_FILE="${2:?Usage: render_mindmap.sh <input.mmd> <output.png> [width] [height]}"
WIDTH="${3:-1200}"
HEIGHT="${4:-800}"

# Validate input file exists
if [[ ! -f "$INPUT_FILE" ]]; then
    echo "Error: Input file not found: $INPUT_FILE" >&2
    exit 1
fi

# Validate input contains mindmap syntax
if ! grep -q "^mindmap" "$INPUT_FILE" 2>/dev/null; then
    echo "Warning: Input file may not contain valid Mermaid mindmap syntax" >&2
fi

# Create a Puppeteer config for mermaid-cli
# This ensures clean rendering with proper fonts
PUPPETEER_CONFIG=$(mktemp /tmp/mmdc-puppeteer-XXXXXX.json)
cat > "$PUPPETEER_CONFIG" <<'EOF'
{
    "headless": true,
    "args": [
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage"
    ]
}
EOF

# Create mermaid config for styling
# Optimized for: readable on mobile, clean white background, good contrast
MERMAID_CONFIG=$(mktemp /tmp/mmdc-config-XXXXXX.json)
cat > "$MERMAID_CONFIG" <<EOF
{
    "theme": "default",
    "themeVariables": {
        "fontSize": "16px",
        "fontFamily": "arial, sans-serif"
    },
    "mindmap": {
        "padding": 20,
        "useMaxWidth": false
    }
}
EOF

# Render using mermaid-cli (mmdc)
# Priority: global install > local node_modules > npx auto-install
if command -v mmdc &> /dev/null; then
    MMDC_CMD="mmdc"
elif [[ -x "./node_modules/.bin/mmdc" ]]; then
    MMDC_CMD="./node_modules/.bin/mmdc"
elif [[ -d "/tmp/mmdc-test/node_modules" ]]; then
    # Use the local install we set up for testing
    MMDC_CMD="/tmp/mmdc-test/node_modules/.bin/mmdc"
else
    # Auto-install via npx as last resort
    MMDC_CMD="npx -y @mermaid-js/mermaid-cli"
fi

echo "Rendering mindmap: $INPUT_FILE → $OUTPUT_FILE"

$MMDC_CMD \
    -i "$INPUT_FILE" \
    -o "$OUTPUT_FILE" \
    -w "$WIDTH" \
    -H "$HEIGHT" \
    -s 2 \
    -b white \
    -c "$MERMAID_CONFIG" \
    -p "$PUPPETEER_CONFIG" \
    2>&1

RENDER_EXIT=$?

# Cleanup temp configs
rm -f "$PUPPETEER_CONFIG" "$MERMAID_CONFIG"

if [[ $RENDER_EXIT -ne 0 ]]; then
    echo "Error: Mermaid rendering failed with exit code $RENDER_EXIT" >&2
    exit $RENDER_EXIT
fi

# Verify output was created
if [[ ! -f "$OUTPUT_FILE" ]]; then
    echo "Error: Output file was not created: $OUTPUT_FILE" >&2
    exit 1
fi

FILE_SIZE=$(wc -c < "$OUTPUT_FILE" | tr -d ' ')
echo "✅ Mindmap rendered successfully: $OUTPUT_FILE ($FILE_SIZE bytes)"

# Telegram has a 10MB photo limit — warn if close
if [[ "$FILE_SIZE" -gt 9000000 ]]; then
    echo "⚠️  Warning: File is close to Telegram's 10MB photo limit" >&2
fi
