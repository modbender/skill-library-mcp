#!/bin/bash
# ComfyUI Qwen-TTS Script
# Usage: tts.sh "text to speak" [options]

set -euo pipefail

# Default configuration
COMFYUI_HOST="${COMFYUI_HOST:-localhost}"
COMFYUI_PORT="${COMFYUI_PORT:-8188}"
COMFYUI_URL="http://${COMFYUI_HOST}:${COMFYUI_PORT}"

# Default TTS parameters
CHARACTER="${TTS_CHARACTER:-Girl}"
STYLE="${TTS_STYLE:-Emotional}"
MODEL_SIZE="${TTS_MODEL:-1.7B}"
TEMPERATURE="${TTS_TEMPERATURE:-0.9}"
TOP_P="${TTS_TOP_P:-0.9}"
TOP_K="${TTS_TOP_K:-50}"
OUTPUT_FILE=""

# Parse arguments
TEXT=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --character)
            CHARACTER="$2"
            shift 2
            ;;
        --style)
            STYLE="$2"
            shift 2
            ;;
        --model)
            MODEL_SIZE="$2"
            shift 2
            ;;
        --temperature)
            TEMPERATURE="$2"
            shift 2
            ;;
        --top-p)
            TOP_P="$2"
            shift 2
            ;;
        --top-k)
            TOP_K="$2"
            shift 2
            ;;
        --output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: tts.sh \"text to speak\" [options]"
            echo ""
            echo "Options:"
            echo "  --character    Voice character (default: Girl)"
            echo "  --style        Speaking style (default: Emotional)"
            echo "  --model        Model size: 0.5B, 1.7B, 3B (default: 1.7B)"
            echo "  --temperature  Generation temperature (default: 0.9)"
            echo "  --top-p        Top-p sampling (default: 0.9)"
            echo "  --top-k        Top-k sampling (default: 50)"
            echo "  --output       Output file path (default: auto-generated)"
            echo "  --help         Show this help message"
            echo ""
            echo "Environment variables:"
            echo "  COMFYUI_HOST   ComfyUI server host (default: localhost)"
            echo "  COMFYUI_PORT   ComfyUI server port (default: 8188)"
            exit 0
            ;;
        -*)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
        *)
            if [ -z "$TEXT" ]; then
                TEXT="$1"
            else
                TEXT="$TEXT $1"
            fi
            shift
            ;;
    esac
done

# Validate required parameters
if [ -z "$TEXT" ]; then
    echo "Error: No text provided"
    echo "Usage: tts.sh \"text to speak\""
    exit 1
fi

# Check dependencies
if ! command -v curl &> /dev/null; then
    echo "Error: curl is required but not installed"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed"
    exit 1
fi

# Check ComfyUI connectivity
echo "🔍 Checking ComfyUI connection at ${COMFYUI_URL}..."
if ! curl -s "${COMFYUI_URL}/system_stats" > /dev/null 2>&1; then
    echo "Error: Cannot connect to ComfyUI at ${COMFYUI_URL}"
    echo "Please ensure ComfyUI is running and COMFYUI_HOST/COMFYUI_PORT are set correctly"
    exit 1
fi
echo "✅ ComfyUI is reachable"

# Generate unique client ID
CLIENT_ID="openclaw_$(date +%s)_$$"

# Generate random seed
SEED=$((RANDOM % 1000000000 + 1000000000))

# Create timestamp for filename
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Build the workflow JSON
WORKFLOW=$(cat <<EOF
{
  "10": {
    "inputs": {
      "character": "${CHARACTER}",
      "style": "${STYLE}",
      "custom_instruct": ""
    },
    "class_type": "AILab_Qwen3TTSVoiceInstruct",
    "_meta": {
      "title": "Voice Instruct (QwenTTS)"
    }
  },
  "11": {
    "inputs": {
      "filename_prefix": "audio/ComfyUI",
      "audioUI": "",
      "audio": [
        "15",
        0
      ]
    },
    "class_type": "SaveAudio",
    "_meta": {
      "title": "保存音频"
    }
  },
  "12": {
    "inputs": {
      "audioUI": "",
      "audio": [
        "15",
        0
      ]
    },
    "class_type": "PreviewAudio",
    "_meta": {
      "title": "预览音频"
    }
  },
  "14": {
    "inputs": {
      "preview": "",
      "previewMode": null,
      "source": [
        "10",
        0
      ]
    },
    "class_type": "PreviewAny",
    "_meta": {
      "title": "预览任意"
    }
  },
  "15": {
    "inputs": {
      "text": $(echo "$TEXT" | jq -R .),
      "instruct": [
        "10",
        0
      ],
      "model_size": "${MODEL_SIZE}",
      "device": "auto",
      "precision": "bf16",
      "language": "Auto",
      "max_new_tokens": 2048,
      "do_sample": false,
      "top_p": ${TOP_P},
      "top_k": ${TOP_K},
      "temperature": ${TEMPERATURE},
      "repetition_penalty": 1,
      "attention": "auto",
      "unload_models": true,
      "seed": ${SEED}
    },
    "class_type": "AILab_Qwen3TTSVoiceDesign_Advanced",
    "_meta": {
      "title": "Voice Design (QwenTTS) Advanced"
    }
  }
}
EOF
)

# Submit the prompt
echo "🎯 Submitting TTS job..."
echo "   Text: ${TEXT}"
echo "   Character: ${CHARACTER}"
echo "   Style: ${STYLE}"
echo "   Model: ${MODEL_SIZE}"

PAYLOAD=$(cat <<EOF
{
  "prompt": ${WORKFLOW},
  "client_id": "${CLIENT_ID}"
}
EOF
)

# Submit and get prompt ID
RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD" \
    "${COMFYUI_URL}/prompt")

if [ -z "$RESPONSE" ] || [ "$RESPONSE" = "null" ]; then
    echo "Error: Failed to submit prompt to ComfyUI"
    exit 1
fi

PROMPT_ID=$(echo "$RESPONSE" | jq -r '.prompt_id // empty')
if [ -z "$PROMPT_ID" ] || [ "$PROMPT_ID" = "null" ]; then
    echo "Error: No prompt_id received from ComfyUI"
    echo "Response: $RESPONSE"
    exit 1
fi

echo "📋 Job ID: ${PROMPT_ID}"

# Poll for completion
echo "⏳ Waiting for generation to complete..."
MAX_RETRIES=300
RETRY_COUNT=0
COMPLETED=false
LAST_STATUS=""

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    sleep 2
    
    HISTORY=$(curl -s "${COMFYUI_URL}/history/${PROMPT_ID}")
    
    # If history is empty or null, job might be done (ComfyUI removes completed jobs quickly)
    if [ -z "$HISTORY" ] || [ "$HISTORY" = "null" ] || [ "$HISTORY" = "{}" ]; then
        # Check if job was previously seen - if yes, it might have completed
        if [ -n "$LAST_STATUS" ]; then
            echo "   Job completed (removed from history)"
            COMPLETED=true
            break
        fi
        RETRY_COUNT=$((RETRY_COUNT + 1))
        continue
    fi
    
    # Check prompt exists in history
    PROMPT_DATA=$(echo "$HISTORY" | jq -r ".[\"${PROMPT_ID}\"] // empty")
    if [ -z "$PROMPT_DATA" ] || [ "$PROMPT_DATA" = "null" ]; then
        # Job not in history yet, still pending
        RETRY_COUNT=$((RETRY_COUNT + 1))
        continue
    fi
    
    # Check status - ComfyUI uses .status.status_str
    STATUS=$(echo "$PROMPT_DATA" | jq -r '.status.status_str // empty')
    LAST_STATUS="$STATUS"
    
    if [ "$STATUS" = "success" ]; then
        COMPLETED=true
        break
    elif [ "$STATUS" = "error" ]; then
        ERROR_MSG=$(echo "$PROMPT_DATA" | jq -r '.status.messages[] | select(.[0] == "execution_error") | .[1].error // "Unknown error"')
        echo "❌ Error during generation: ${ERROR_MSG}"
        exit 1
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    
    if [ $((RETRY_COUNT % 10)) -eq 0 ]; then
        echo "   Still processing... (${RETRY_COUNT}s) [status: ${STATUS:-unknown}]"
    fi
done

if [ "$COMPLETED" = false ]; then
    echo "❌ Timeout waiting for generation to complete"
    exit 1
fi

echo "✅ Generation complete!"

# If job was removed from history, try to fetch it one more time
if [ -z "$HISTORY" ] || [ "$HISTORY" = "null" ] || [ "$HISTORY" = "{}" ]; then
    sleep 1
    HISTORY=$(curl -s "${COMFYUI_URL}/history/${PROMPT_ID}")
fi

# Extract output file information
OUTPUTS=$(echo "$HISTORY" | jq -r ".[\"${PROMPT_ID}\"].outputs // {}")

# Find the audio output from node 11 (SaveAudio) or node 15 (TTS node)
AUDIO_FILES=$(echo "$OUTPUTS" | jq -r '
    to_entries[] | 
    select(.value.audio?) | 
    .value.audio[] | 
    select(.filename | test("\\.(wav|mp3|flac|ogg|m4a)$"; "i"))
')

if [ -z "$AUDIO_FILES" ]; then
    # Try alternative path
    AUDIO_FILES=$(echo "$OUTPUTS" | jq -r '
        to_entries[] | 
        select(.value.files?) | 
        .value.files[] | 
        select(.filename | test("\\.(wav|mp3|flac|ogg|m4a)$"; "i"))
    ')
fi

if [ -z "$AUDIO_FILES" ]; then
    echo "⚠️  Warning: Could not find audio file in outputs"
    echo "   Full output: $OUTPUTS"
    exit 1
fi

# Get the filename
FILENAME=$(echo "$AUDIO_FILES" | jq -r '.filename // empty' | head -1)
SUBFOLDER=$(echo "$AUDIO_FILES" | jq -r '.subfolder // empty' | head -1)
TYPE=$(echo "$AUDIO_FILES" | jq -r '.type // "output"' | head -1)

if [ -z "$FILENAME" ]; then
    echo "⚠️  Warning: Could not extract filename"
    exit 1
fi

# Construct full path
if [ -n "$SUBFOLDER" ]; then
    FULL_PATH="${SUBFOLDER}/${FILENAME}"
else
    FULL_PATH="${FILENAME}"
fi

# Get the view URL
VIEW_URL="${COMFYUI_URL}/view?filename=${FILENAME}"
if [ -n "$SUBFOLDER" ]; then
    VIEW_URL="${VIEW_URL}&subfolder=${SUBFOLDER}"
fi
VIEW_URL="${VIEW_URL}&type=${TYPE}"

echo ""
echo "🎵 Audio generated successfully!"
echo "   Filename: ${FILENAME}"
echo "   View URL: ${VIEW_URL}"

# If output file specified, download it
if [ -n "$OUTPUT_FILE" ]; then
    echo "📥 Downloading to: ${OUTPUT_FILE}"
    
    # Create directory if needed
    OUTPUT_DIR=$(dirname "$OUTPUT_FILE")
    if [ ! -d "$OUTPUT_DIR" ]; then
        mkdir -p "$OUTPUT_DIR"
    fi
    
    if curl -s -o "$OUTPUT_FILE" "$VIEW_URL"; then
        echo "✅ Saved to: ${OUTPUT_FILE}"
    else
        echo "⚠️  Warning: Failed to download file"
    fi
fi

echo ""
echo "Done!"
