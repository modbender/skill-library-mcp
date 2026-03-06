#!/bin/bash
set -euo pipefail

# ai-media image generation script
# Usage: ./image.sh "prompt text" [style]

PROMPT="${1:-lady on beach at sunset}"
STYLE="${2:-realistic}"
SSH_KEY="$HOME/.ssh/${SSH_KEY_NAME:-id_ed25519_gpu}"
GPU_HOST="${GPU_USER:-user}@${GPU_HOST:-localhost}"
COMFYUI_DIR="/data/ai-stack/comfyui/ComfyUI"
OUTPUT_DIR="/data/ai-stack/output"

# Generate unique filename
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="image_${TIMESTAMP}.png"

# Determine model based on style
if [[ "$STYLE" == "realistic" ]]; then
    MODEL="juggernautXL_v9.safetensors"
    WORKFLOW="image-workflow-juggernaut.json"
else
    MODEL="juggernautXL_v9.safetensors"  # Default to Juggernaut for now
    WORKFLOW="image-workflow-juggernaut.json"
fi

echo "🎨 Generating image with prompt: '$PROMPT'"
echo "📐 Style: $STYLE"
echo "🖥️  GPU Server: $GPU_HOST"

# Check SSH connectivity
if ! ssh -i "$SSH_KEY" -o ConnectTimeout=5 "$GPU_HOST" "echo 'SSH OK'" &>/dev/null; then
    echo "❌ Cannot connect to GPU server"
    exit 1
fi

# Create output directory
ssh -i "$SSH_KEY" "$GPU_HOST" "mkdir -p $OUTPUT_DIR"

# Generate image via ComfyUI API
# For now, use a simple direct generation script on the server
ssh -i "$SSH_KEY" "$GPU_HOST" bash <<EOF
set -euo pipefail
cd $COMFYUI_DIR

# Simple Python script to generate image
python3 <<PYTHON
import sys
import os
import json
import random
sys.path.insert(0, '$COMFYUI_DIR')

# Import ComfyUI modules
import execution
import server
from nodes import NODE_CLASS_MAPPINGS

# Simple SDXL text-to-image workflow
workflow = {
    "1": {
        "class_type": "CheckpointLoaderSimple",
        "inputs": {"ckpt_name": "$MODEL"}
    },
    "2": {
        "class_type": "CLIPTextEncode",
        "inputs": {"text": "$PROMPT", "clip": ["1", 1]}
    },
    "3": {
        "class_type": "CLIPTextEncode",
        "inputs": {"text": "blurry, low quality, watermark, text", "clip": ["1", 1]}
    },
    "4": {
        "class_type": "EmptyLatentImage",
        "inputs": {"width": 1024, "height": 1024, "batch_size": 1}
    },
    "5": {
        "class_type": "KSampler",
        "inputs": {
            "seed": random.randint(0, 2**32-1),
            "steps": 30,
            "cfg": 7.5,
            "sampler_name": "euler_ancestral",
            "scheduler": "normal",
            "denoise": 1.0,
            "model": ["1", 0],
            "positive": ["2", 0],
            "negative": ["3", 0],
            "latent_image": ["4", 0]
        }
    },
    "6": {
        "class_type": "VAEDecode",
        "inputs": {"samples": ["5", 0], "vae": ["1", 2]}
    },
    "7": {
        "class_type": "SaveImage",
        "inputs": {"filename_prefix": "ai-media/$OUTPUT_FILE", "images": ["6", 0]}
    }
}

print(json.dumps(workflow, indent=2))
print("Workflow prepared. Manual execution required via ComfyUI API.")
PYTHON
EOF

echo "✅ Image generation queued"
echo "📁 Output: $OUTPUT_DIR/$OUTPUT_FILE"
echo ""
echo "⚠️  Note: Full ComfyUI API integration pending. Currently outputs workflow JSON."
echo "    Next step: Implement HTTP API calls to ComfyUI server (port 8188)"
