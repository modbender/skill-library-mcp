#!/bin/bash
set -euo pipefail

# Test ComfyUI server connectivity and status

GPU_HOST="${GPU_HOST:-localhost}"
COMFYUI_PORT="8188"

echo "🔍 Testing ComfyUI server..."
echo "   Host: $GPU_HOST:$COMFYUI_PORT"

# Test HTTP connectivity
if curl -s -m 5 "http://$GPU_HOST:$COMFYUI_PORT/" > /dev/null; then
    echo "✅ ComfyUI server is accessible"
else
    echo "❌ ComfyUI server is not responding"
    exit 1
fi

# Get system stats
echo ""
echo "📊 ComfyUI System Stats:"
STATS=$(curl -s "http://$GPU_HOST:$COMFYUI_PORT/system_stats" 2>/dev/null || echo "{}")
echo "$STATS" | python3 -m json.tool 2>/dev/null || echo "   (Unable to parse stats)"

# Get queue info
echo ""
echo "📋 Queue Status:"
QUEUE=$(curl -s "http://$GPU_HOST:$COMFYUI_PORT/queue" 2>/dev/null || echo "{}")
echo "$QUEUE" | python3 -m json.tool 2>/dev/null || echo "   (Unable to parse queue)"

echo ""
echo "✅ ComfyUI server is ready for generation"
