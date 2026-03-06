#!/usr/bin/env bash
set -euo pipefail

LOCK_DIR="/tmp/eleven-stt.lock"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
    echo "Error: Another transcription is currently running. Please wait a moment." >&2
    exit 1
fi
cleanup_lock() { rmdir "$LOCK_DIR" 2>/dev/null || true; }
trap cleanup_lock EXIT

# ElevenLabs Speech-to-Text transcription script
# Usage: transcribe.sh <audio_file> [options]

show_help() {
    cat << EOF
Usage: $(basename "$0") <audio_file> [options]

Core options:
  --diarize                 Enable speaker diarization
  --lang CODE               ISO language code (e.g., en, hu, es)
  --json                    Output full JSON response
  --events                  Tag audio events (laughter, music, etc.)
  --model MODEL             STT model (default: scribe_v2)

Async / webhook options:
  --webhook                 Enable async processing (webhook delivery)
  --webhook-id ID           Send to a specific webhook ID
  --webhook-metadata JSON   JSON string to attach to webhook callback

Advanced options:
  --timestamps MODE         none|word|character (default: word)
  --num-speakers N          Max speakers (1-32)
  --diarization-threshold X Diarization threshold (0-1)
  --use-multi-channel       Split multi-channel audio
  --entity-detection MODE   e.g. all|pii|phi|pci|offensive_language
  --keyterms "a,b,c"         Comma-separated keyterms (<=100)
  --enable-logging BOOL     true|false (default: true)
  --url HTTPS_URL           Transcribe via cloud URL instead of file

  -h, --help                Show this help

Environment:
  ELEVENLABS_API_KEY  Required API key

Examples:
  $(basename "$0") voice_note.ogg
  $(basename "$0") meeting.mp3 --diarize --lang en --json
  $(basename "$0") audio.wav --webhook --webhook-id abc123
  $(basename "$0") --url https://example.com/audio.mp3 --lang en
EOF
    exit 0
}

# Defaults
DIARIZE="false"
LANG_CODE=""
JSON_OUTPUT="false"
TAG_EVENTS="false"
MODEL_ID="scribe_v2"
TIMESTAMPS="word"
NUM_SPEAKERS=""
DIARIZATION_THRESHOLD=""
USE_MULTI_CHANNEL="false"
ENTITY_DETECTION=""
KEYTERMS=""
ENABLE_LOGGING="true"
WEBHOOK="false"
WEBHOOK_ID=""
WEBHOOK_METADATA=""
CLOUD_URL=""
FILE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help) show_help ;;
        --diarize) DIARIZE="true"; shift ;;
        --lang) LANG_CODE="$2"; shift 2 ;;
        --json) JSON_OUTPUT="true"; shift ;;
        --events) TAG_EVENTS="true"; shift ;;
        --model) MODEL_ID="$2"; shift 2 ;;
        --timestamps) TIMESTAMPS="$2"; shift 2 ;;
        --num-speakers) NUM_SPEAKERS="$2"; shift 2 ;;
        --diarization-threshold) DIARIZATION_THRESHOLD="$2"; shift 2 ;;
        --use-multi-channel) USE_MULTI_CHANNEL="true"; shift ;;
        --entity-detection) ENTITY_DETECTION="$2"; shift 2 ;;
        --keyterms) KEYTERMS="$2"; shift 2 ;;
        --enable-logging) ENABLE_LOGGING="$2"; shift 2 ;;
        --webhook) WEBHOOK="true"; shift ;;
        --webhook-id) WEBHOOK_ID="$2"; shift 2 ;;
        --webhook-metadata) WEBHOOK_METADATA="$2"; shift 2 ;;
        --url) CLOUD_URL="$2"; shift 2 ;;
        -*) echo "Unknown option: $1" >&2; exit 1 ;;
        *) FILE="$1"; shift ;;
    esac
done

# Validate inputs
if [[ -z "$FILE" && -z "$CLOUD_URL" ]]; then
    echo "Error: Provide a file path or --url" >&2
    show_help
fi

if [[ -n "$FILE" ]]; then
    if [[ ! -f "$FILE" ]]; then
        echo "Error: File not found: $FILE" >&2
        exit 1
    fi
    if [[ "${ALLOW_LOCAL_FILE:-false}" != "true" ]]; then
        echo "Error: Local file usage requires ALLOW_LOCAL_FILE=true" >&2
        exit 1
    fi
fi

if [[ -n "$CLOUD_URL" ]]; then
    if [[ ! "$CLOUD_URL" =~ ^https:// ]]; then
        echo "Error: --url must start with https://" >&2
        exit 1
    fi
    if [[ "$CLOUD_URL" =~ [[:space:]] ]]; then
        echo "Error: --url must not contain spaces" >&2
        exit 1
    fi
fi

# API key
API_KEY="${ELEVENLABS_API_KEY:-}"
if [[ -z "$API_KEY" ]]; then
    echo "Error: ELEVENLABS_API_KEY not set" >&2
    exit 1
fi

# Build curl command
CURL_ARGS=(
    -s
    -X POST
    "https://api.elevenlabs.io/v1/speech-to-text"
    -H "xi-api-key: $API_KEY"
    -F "model_id=$MODEL_ID"
    -F "diarize=$DIARIZE"
    -F "tag_audio_events=$TAG_EVENTS"
    -F "timestamps_granularity=$TIMESTAMPS"
    -F "enable_logging=$ENABLE_LOGGING"
    -F "use_multi_channel=$USE_MULTI_CHANNEL"
    -F "webhook=$WEBHOOK"
)

if [[ -n "$FILE" ]]; then
    CURL_ARGS+=(-F "file=@$FILE")
elif [[ -n "$CLOUD_URL" ]]; then
    CURL_ARGS+=(-F "cloud_storage_url=$CLOUD_URL")
fi

if [[ -n "$LANG_CODE" ]]; then
    CURL_ARGS+=(-F "language_code=$LANG_CODE")
fi

if [[ -n "$NUM_SPEAKERS" ]]; then
    CURL_ARGS+=(-F "num_speakers=$NUM_SPEAKERS")
fi

if [[ -n "$DIARIZATION_THRESHOLD" ]]; then
    CURL_ARGS+=(-F "diarization_threshold=$DIARIZATION_THRESHOLD")
fi

if [[ -n "$ENTITY_DETECTION" ]]; then
    CURL_ARGS+=(-F "entity_detection=$ENTITY_DETECTION")
fi

if [[ -n "$KEYTERMS" ]]; then
    CURL_ARGS+=(-F "keyterms=$KEYTERMS")
fi

if [[ -n "$WEBHOOK_ID" ]]; then
    CURL_ARGS+=(-F "webhook_id=$WEBHOOK_ID")
fi

if [[ -n "$WEBHOOK_METADATA" ]]; then
    if ! echo "$WEBHOOK_METADATA" | jq -e . >/dev/null 2>&1; then
        echo "Error: --webhook-metadata must be valid JSON" >&2
        exit 1
    fi
    CURL_ARGS+=(-F "webhook_metadata=$WEBHOOK_METADATA")
fi

# Make request
RESPONSE=$(curl "${CURL_ARGS[@]}")

# Check for errors
if echo "$RESPONSE" | grep -q '"detail"'; then
    echo "Error from API:" >&2
    echo "$RESPONSE" | jq -r '.detail.message // .detail' >&2
    exit 1
fi

# Output
if [[ "$JSON_OUTPUT" == "true" ]]; then
    echo "$RESPONSE" | jq .
else
    TEXT=$(echo "$RESPONSE" | jq -r '.text // empty')
    if [[ -n "$TEXT" ]]; then
        echo "$TEXT"
    else
        echo "$RESPONSE"
    fi
fi
