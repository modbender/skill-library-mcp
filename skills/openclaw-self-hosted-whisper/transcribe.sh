#!/usr/bin/env bash
# Whisper ASR transcription via onerahmet/openai-whisper-asr-webservice
# Endpoint: http://whisper-asr.whisper-asr.svc.cluster.local:9000/asr
set -euo pipefail

BASE_URL="http://whisper-asr.whisper-asr.svc.cluster.local:9000"

# --- Parse arguments ---
INPUT_FILE=""
OUT_FILE=""
LANGUAGE=""
PROMPT=""
OUTPUT_FORMAT="txt"
TASK="transcribe"
VAD_FILTER=""
WORD_TIMESTAMPS=""

usage() {
  cat <<EOF
Usage: $(basename "$0") <audio_file> [options]

Options:
  --out <path>                Output file path (default: <input>.<format>)
  --language <code>           ISO language code (e.g., en, de, fr)
  --prompt <text>             Initial prompt/context for the transcription
  --output <fmt>              Output format: txt|json|vtt|srt|tsv (default: txt)
  --json                      Shorthand for --output json
  --task <task>               Task: transcribe (default) or translate
  --translate                 Shorthand for --task translate
  --vad-filter                Enable voice activity detection filtering
  --word-timestamps           Enable word-level timestamps (json output)
  -h, --help                  Show this help message

Examples:
  $(basename "$0") meeting.m4a
  $(basename "$0") interview.ogg --language en --output txt
  $(basename "$0") podcast.mp3 --json --out transcript.json
  $(basename "$0") call.wav --translate
  $(basename "$0") lecture.m4a --output srt --out subtitles.srt
  $(basename "$0") audio.m4a --vad-filter --word-timestamps --json
EOF
  exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --out)              OUT_FILE="$2"; shift 2 ;;
    --language)         LANGUAGE="$2"; shift 2 ;;
    --prompt)           PROMPT="$2"; shift 2 ;;
    --output)           OUTPUT_FORMAT="$2"; shift 2 ;;
    --json)             OUTPUT_FORMAT="json"; shift ;;
    --task)             TASK="$2"; shift 2 ;;
    --translate)        TASK="translate"; shift ;;
    --vad-filter)       VAD_FILTER="true"; shift ;;
    --word-timestamps)  WORD_TIMESTAMPS="true"; shift ;;
    -h|--help)          usage ;;
    -*)                 echo "Unknown option: $1" >&2; exit 1 ;;
    *)
      if [[ -z "$INPUT_FILE" ]]; then
        INPUT_FILE="$1"
      else
        echo "Unexpected argument: $1" >&2; exit 1
      fi
      shift
      ;;
  esac
done

# --- Validate ---
if [[ -z "$INPUT_FILE" ]]; then
  echo "Error: No audio file specified." >&2
  usage
fi

if [[ ! -f "$INPUT_FILE" ]]; then
  echo "Error: File not found: $INPUT_FILE" >&2
  exit 1
fi

# --- Determine output file ---
if [[ -z "$OUT_FILE" ]]; then
  OUT_FILE="${INPUT_FILE}.${OUTPUT_FORMAT}"
fi

# --- Build query string ---
QUERY="task=${TASK}&output=${OUTPUT_FORMAT}"
[[ -n "$LANGUAGE" ]]        && QUERY="${QUERY}&language=${LANGUAGE}"
[[ -n "$PROMPT" ]]          && QUERY="${QUERY}&initial_prompt=$(python3 -c "import urllib.parse; print(urllib.parse.quote('${PROMPT}'))" 2>/dev/null || echo "${PROMPT}")"
[[ -n "$VAD_FILTER" ]]      && QUERY="${QUERY}&vad_filter=true"
[[ -n "$WORD_TIMESTAMPS" ]] && QUERY="${QUERY}&word_timestamps=true"

# --- Execute ---
echo "Transcribing: ${INPUT_FILE}" >&2
echo "  Endpoint: ${BASE_URL}/asr" >&2
echo "  Task: ${TASK}" >&2
echo "  Format: ${OUTPUT_FORMAT}" >&2
[[ -n "$LANGUAGE" ]] && echo "  Language: ${LANGUAGE}" >&2

RESPONSE=$(curl \
  --silent \
  --show-error \
  --fail \
  --request POST \
  --header "content-type: multipart/form-data" \
  --form "audio_file=@${INPUT_FILE}" \
  "${BASE_URL}/asr?${QUERY}")

echo "$RESPONSE" > "$OUT_FILE"
echo "Transcript saved to: ${OUT_FILE}" >&2
