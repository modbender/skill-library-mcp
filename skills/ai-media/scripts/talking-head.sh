#!/bin/bash
set -euo pipefail

# ai-media talking head generation script
# Usage: ./talking-head.sh "speech text" [voice_style] [avatar_image]

TEXT="${1:-Hello, I am Alex Chen}"
VOICE_STYLE="${2:-gentle}"
AVATAR="${3:-}"
SSH_KEY="$HOME/.ssh/${SSH_KEY_NAME:-id_ed25519_gpu}"
GPU_HOST="${GPU_USER:-user}@${GPU_HOST:-localhost}"
SADTALKER_DIR="/data/ai-stack/sadtalker"
OUTPUT_DIR="/data/ai-stack/output"

# Generate unique filename
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
AUDIO_FILE="audio_${TIMESTAMP}.wav"
OUTPUT_FILE="talking_${TIMESTAMP}.mp4"

echo "🗣️  Generating talking head"
echo "💬 Text: '$TEXT'"
echo "🎤 Voice: $VOICE_STYLE"
echo "🖥️  GPU Server: $GPU_HOST"

# Check SSH connectivity
if ! ssh -i "$SSH_KEY" -o ConnectTimeout=5 "$GPU_HOST" "echo 'SSH OK'" &>/dev/null; then
    echo "❌ Cannot connect to GPU server"
    exit 1
fi

# Create output directory
ssh -i "$SSH_KEY" "$GPU_HOST" "mkdir -p $OUTPUT_DIR"

# Generate audio first (using gTTS in .venv)
echo "🎵 Generating audio..."
ssh -i "$SSH_KEY" "$GPU_HOST" bash <<EOF
set -euo pipefail
cd $SADTALKER_DIR
source .venv/bin/activate

python3 <<PYTHON
from gtts import gTTS
import os

text = "$TEXT"
output_path = "$OUTPUT_DIR/$AUDIO_FILE"

# Generate audio
tts = gTTS(text=text, lang='en', slow=False)
tts.save(output_path)
print(f"✅ Audio saved: {output_path}")
PYTHON
EOF

# Determine avatar image
if [[ -z "$AVATAR" ]]; then
    # Use default avatar
    AVATAR_PATH="$SADTALKER_DIR/examples/source_image/full_body_1.png"
    echo "📸 Using default avatar"
else
    # Copy user-provided avatar to GPU server
    AVATAR_FILENAME=$(basename "$AVATAR")
    echo "📸 Uploading avatar: $AVATAR"
    scp -i "$SSH_KEY" "$AVATAR" "$GPU_HOST:$OUTPUT_DIR/$AVATAR_FILENAME"
    AVATAR_PATH="$OUTPUT_DIR/$AVATAR_FILENAME"
fi

# Generate talking head video
echo "🎬 Generating talking head video..."
ssh -i "$SSH_KEY" "$GPU_HOST" bash <<EOF
set -euo pipefail
cd $SADTALKER_DIR
source .venv/bin/activate

# Run SadTalker
python3 inference.py \\
    --driven_audio "$OUTPUT_DIR/$AUDIO_FILE" \\
    --source_image "$AVATAR_PATH" \\
    --result_dir "$OUTPUT_DIR" \\
    --enhancer gfpgan \\
    --preprocess full

# Find the generated video (SadTalker creates timestamped output)
LATEST_VIDEO=\$(ls -t $OUTPUT_DIR/*.mp4 | head -1)

# Convert to H.264 for Telegram compatibility
ffmpeg -y -i "\$LATEST_VIDEO" \\
    -c:v libx264 -profile:v baseline -level 3.0 \\
    -pix_fmt yuv420p -c:a aac -b:a 128k \\
    -movflags +faststart \\
    "$OUTPUT_DIR/$OUTPUT_FILE"

echo "✅ Video saved: $OUTPUT_DIR/$OUTPUT_FILE"

# Get file size
ls -lh "$OUTPUT_DIR/$OUTPUT_FILE" | awk '{print "📦 Size:", \$5}'
EOF

echo ""
echo "✅ Talking head generation complete!"
echo "📁 Output: $OUTPUT_DIR/$OUTPUT_FILE"
echo ""
echo "To download:"
echo "  scp -i $SSH_KEY $GPU_HOST:$OUTPUT_DIR/$OUTPUT_FILE ."
