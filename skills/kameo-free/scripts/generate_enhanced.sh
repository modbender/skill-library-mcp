#!/bin/bash
# One-command workflow: Enhance prompt + Generate video

IMAGE_PATH="$1"
DIALOGUE="$2"
OUTPUT_FILE="${3:-kameo-output.mp4}"
ASPECT_RATIO="${4:-9:16}"

if [ -z "$IMAGE_PATH" ] || [ -z "$DIALOGUE" ]; then
    echo "Usage: $0 <image> <dialogue> [output] [aspect_ratio]"
    echo ""
    echo "Example:"
    echo "  $0 photo.jpg \"Hello world\" video.mp4 9:16"
    echo ""
    echo "This automatically:"
    echo "  1. Analyzes image with Gemini vision"
    echo "  2. Generates enhanced cinematic prompt"
    echo "  3. Sends to Kameo for video generation"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🎬 Kameo Enhanced Video Generation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 1: Enhance prompt
echo "📝 Step 1: Enhancing prompt with Gemini..."
ENHANCED_PROMPT=$("$SCRIPT_DIR/enhance_prompt.sh" "$IMAGE_PATH" "$DIALOGUE")

if [ $? -ne 0 ]; then
    echo "❌ Prompt enhancement failed"
    exit 1
fi

echo "✅ Enhanced prompt ready"
echo ""

# Step 2: Generate video
echo "🚀 Step 2: Generating video with Kameo..."
"$SCRIPT_DIR/generate_video.sh" "$IMAGE_PATH" "$ENHANCED_PROMPT" "$OUTPUT_FILE" "$ASPECT_RATIO"
