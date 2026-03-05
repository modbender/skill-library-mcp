#!/bin/bash
# Test script to debug ComfyUI history API response

set -euo pipefail

COMFYUI_HOST="${COMFYUI_HOST:-localhost}"
COMFYUI_PORT="${COMFYUI_PORT:-8188}"
COMFYUI_URL="http://${COMFYUI_HOST}:${COMFYUI_PORT}"

echo "Testing ComfyUI connection..."
if ! curl -s "${COMFYUI_URL}/system_stats" > /dev/null 2>&1; then
    echo "Error: Cannot connect to ComfyUI at ${COMFYUI_URL}"
    exit 1
fi
echo "✅ ComfyUI is reachable"
echo ""

# Submit a simple test job
echo "Submitting test TTS job..."
CLIENT_ID="test_$(date +%s)"
SEED=$((RANDOM % 1000000000 + 1000000000))

WORKFLOW=$(cat <<EOF
{
  "10": {
    "inputs": {
      "character": "Girl",
      "style": "Emotional",
      "custom_instruct": ""
    },
    "class_type": "AILab_Qwen3TTSVoiceInstruct"
  },
  "11": {
    "inputs": {
      "filename_prefix": "audio/test",
      "audioUI": "",
      "audio": ["15", 0]
    },
    "class_type": "SaveAudio"
  },
  "15": {
    "inputs": {
      "text": "测试",
      "instruct": ["10", 0],
      "model_size": "1.7B",
      "device": "auto",
      "precision": "bf16",
      "language": "Auto",
      "max_new_tokens": 2048,
      "do_sample": false,
      "top_p": 0.9,
      "top_k": 50,
      "temperature": 0.9,
      "repetition_penalty": 1,
      "attention": "auto",
      "unload_models": true,
      "seed": ${SEED}
    },
    "class_type": "AILab_Qwen3TTSVoiceDesign_Advanced"
  }
}
EOF
)

PAYLOAD=$(cat <<EOF
{
  "prompt": ${WORKFLOW},
  "client_id": "${CLIENT_ID}"
}
EOF
)

RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD" \
    "${COMFYUI_URL}/prompt")

PROMPT_ID=$(echo "$RESPONSE" | jq -r '.prompt_id // empty')
if [ -z "$PROMPT_ID" ]; then
    echo "Error: Failed to get prompt_id"
    echo "Response: $RESPONSE"
    exit 1
fi

echo "Job submitted: ${PROMPT_ID}"
echo ""

# Poll and show history response
echo "Polling history (press Ctrl+C to stop)..."
echo "======================================"

COUNT=0
while [ $COUNT -lt 60 ]; do
    sleep 2
    COUNT=$((COUNT + 1))
    
    HISTORY=$(curl -s "${COMFYUI_URL}/history/${PROMPT_ID}")
    
    echo ""
    echo "--- Poll #${COUNT} ---"
    
    if [ -z "$HISTORY" ] || [ "$HISTORY" = "null" ] || [ "$HISTORY" = "{}" ]; then
        echo "History is empty/null"
        continue
    fi
    
    # Show full response
    echo "Full response:"
    echo "$HISTORY" | jq .
    
    # Extract and show status
    PROMPT_DATA=$(echo "$HISTORY" | jq -r ".[\"${PROMPT_ID}\"] // empty")
    if [ -n "$PROMPT_DATA" ] && [ "$PROMPT_DATA" != "null" ]; then
        echo ""
        echo "Status analysis:"
        echo "  .status: $(echo "$PROMPT_DATA" | jq -r '.status // "null"')"
        echo "  .status.status: $(echo "$PROMPT_DATA" | jq -r '.status.status // "null"')"
        echo "  .outputs count: $(echo "$PROMPT_DATA" | jq -r '(.outputs // {}) | length')"
        
        # Check if completed
        HAS_OUTPUTS=$(echo "$PROMPT_DATA" | jq -r '(.outputs // {}) | length')
        if [ "$HAS_OUTPUTS" -gt 0 ]; then
            echo ""
            echo "✅ Job has outputs - completed!"
            break
        fi
    fi
done

echo ""
echo "======================================"
echo "Test complete"
