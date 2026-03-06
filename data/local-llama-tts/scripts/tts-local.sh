#!/bin/bash

# Configuration
MODEL="/data/public/machine-learning/models/text-to-speach/OuteTTS-1.0-0.6B-Q4_K_M.gguf"
VOCODER="/data/public/machine-learning/models/text-to-speach/WavTokenizer-Large-75-Q4_0.gguf"

# Default sampling parameters for OuteTTS 1.0
TEMP=0.4
REP_PENALTY=1.1
REP_LAST_N=64
TOP_K=40
TOP_P=0.9
MIN_P=0.05

# Usage
usage() {
    echo "Usage: $0 [options] <text>"
    echo "Options:"
    echo "  -o, --output <file>    Output WAV file (default: output.wav)"
    echo "  -s, --speaker <file>   Speaker reference file (optional)"
    echo "  -t, --temp <value>     Temperature (default: $TEMP)"
    exit 1
}

OUTPUT="output.wav"
SPEAKER_PARAM=""

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -o|--output) OUTPUT="$2"; shift ;;
        -s|--speaker) SPEAKER_PARAM="--tts-speaker-file $2"; shift ;;
        -t|--temp) TEMP="$2"; shift ;;
        -h|--help) usage ;;
        *) TEXT="$1" ;;
    esac
    shift
done

if [ -z "$TEXT" ]; then
    usage
fi

# Run llama-tts
llama-tts \
    -m "$MODEL" \
    -mv "$VOCODER" \
    -p "$TEXT" \
    -o "$OUTPUT" \
    --temp "$TEMP" \
    --repeat-penalty "$REP_PENALTY" \
    --repeat-last-n "$REP_LAST_N" \
    --top-k "$TOP_K" \
    --top-p "$TOP_P" \
    --min-p "$MIN_P" \
    $SPEAKER_PARAM
