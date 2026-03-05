#!/bin/bash
# Long Audio Transcription Script for Whisper (RAM-friendly)
# Splits audio into chunks, transcribes with base model, merges output

set -e

AUDIO_FILE="$1"
OUTPUT_DIR="${2:-.}"
CHUNK_LENGTH=600  # 10 minutes in seconds
MODEL="${WHISPER_MODEL:-base}"  # default to 'base' (less RAM)
LANG="${WHISPER_LANG:-en}"  # default English

if [[ -z "$AUDIO_FILE" ]]; then
  echo "Usage: $0 <audio-file> [output-dir]"
  echo ""
  echo "Environment vars:"
  echo "  WHISPER_MODEL=tiny|base|small|medium|turbo  (default: base)"
  echo "  WHISPER_LANG=de|en|...  (default: de)"
  exit 1
fi

if [[ ! -f "$AUDIO_FILE" ]]; then
  echo "Error: File not found: $AUDIO_FILE"
  exit 1
fi

# Check if ffmpeg and whisper are installed
command -v ffmpeg >/dev/null 2>&1 || { echo "Error: ffmpeg not installed"; exit 1; }
command -v whisper >/dev/null 2>&1 || { echo "Error: whisper not installed"; exit 1; }

# Create temp directory
TEMP_DIR=$(mktemp -d -t transcribe-XXXXXX)
trap "rm -rf $TEMP_DIR" EXIT

echo "🎙️  Transcribing: $AUDIO_FILE"
echo "📁  Output dir: $OUTPUT_DIR"
echo "🤖  Model: $MODEL"
echo "🌍  Language: $LANG"
echo ""

# Get audio duration
DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$AUDIO_FILE")
DURATION_INT=${DURATION%.*}

echo "⏱️  Audio duration: ${DURATION_INT}s ($(($DURATION_INT / 60)) min)"

if (( DURATION_INT <= CHUNK_LENGTH )); then
  echo "✅ Audio is short, no splitting needed"
  whisper "$AUDIO_FILE" \
    --model "$MODEL" \
    --language "$LANG" \
    --output_format txt \
    --output_dir "$OUTPUT_DIR"
  echo "✅ Done!"
  exit 0
fi

# Split audio into chunks
echo "✂️  Splitting into ${CHUNK_LENGTH}s chunks..."
ffmpeg -i "$AUDIO_FILE" \
  -f segment \
  -segment_time "$CHUNK_LENGTH" \
  -c copy \
  -loglevel warning \
  "$TEMP_DIR/chunk_%03d.ogg"

CHUNKS=("$TEMP_DIR"/chunk_*.ogg)
NUM_CHUNKS=${#CHUNKS[@]}

echo "📦 Created $NUM_CHUNKS chunks"
echo ""

# Transcribe each chunk
FINAL_TRANSCRIPT="$TEMP_DIR/final_transcript.txt"
> "$FINAL_TRANSCRIPT"  # clear file

for i in "${!CHUNKS[@]}"; do
  CHUNK="${CHUNKS[$i]}"
  CHUNK_NUM=$((i + 1))
  
  echo "[$CHUNK_NUM/$NUM_CHUNKS] Transcribing chunk..."
  
  whisper "$CHUNK" \
    --model "$MODEL" \
    --language "$LANG" \
    --output_format txt \
    --output_dir "$TEMP_DIR" \
    >/dev/null 2>&1
  
  # Append to final transcript
  CHUNK_BASE=$(basename "$CHUNK" .ogg)
  cat "$TEMP_DIR/${CHUNK_BASE}.txt" >> "$FINAL_TRANSCRIPT"
  echo "" >> "$FINAL_TRANSCRIPT"  # newline between chunks
  
  # Progress indicator
  PERCENT=$((CHUNK_NUM * 100 / NUM_CHUNKS))
  echo "  Progress: ${PERCENT}%"
done

# Copy final transcript to output dir
AUDIO_BASE=$(basename "$AUDIO_FILE" | sed 's/\.[^.]*$//')
OUTPUT_FILE="$OUTPUT_DIR/${AUDIO_BASE}.txt"
cp "$FINAL_TRANSCRIPT" "$OUTPUT_FILE"

echo ""
echo "✅ Transcription complete!"
echo "📄 Output: $OUTPUT_FILE"
