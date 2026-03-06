#!/bin/bash
# whisper-local.sh - Local Whisper transcription using whisper-cli (HIP GPU)
# Path to model: /usr/share/whisper.cpp-model-large-v3-turbo/ggml-large-v3-turbo.bin

MODEL="/usr/share/whisper.cpp-model-large-v3-turbo/ggml-large-v3-turbo.bin"
THREADS=$(nproc)

if [ -z "$1" ]; then
    echo "Usage: $0 <audio-file> [options]"
    exit 1
fi

FILE="$1"
shift

# Default options: auto-detect language, use GPU (implicit in whisper-cli unless -ng is used), no timestamps for cleaner text
# We use flash attention (-fa) for performance as it's default true in help but good to be explicit.
whisper-cli -m "$MODEL" -f "$FILE" -t "$THREADS" -l auto -nt -fa "$@"
