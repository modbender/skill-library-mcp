#!/bin/bash
# Enhanced Video Upscale Wrapper Script
# Supports Real-ESRGAN and Waifu2x with progress tracking and job IDs
# Usage: ./upscale_video.sh INPUT_PATH OUTPUT_PATH MODE [PRESET] [ENGINE] [JOB_ID]

set -euo pipefail

# Get script directory for relative paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

INPUT_PATH="$1"
OUTPUT_PATH="$2"
MODE="${3:-real}"
PRESET="${4:-fast}"
ENGINE="${5:-}"  # auto-detect based on mode
JOB_ID="${6:-}"  # optional job ID

# Generate job ID if not provided
if [ -z "$JOB_ID" ]; then
    JOB_ID="job_$(date +%s)_$RANDOM"
fi

# Config
MAX_DURATION_MINUTES=5
CACHE_DIR="${VIDEO_UPSCALE_CACHE:-${HOME}/.openclaw/cache/video-upscale}"
SAFE_UPSCALE_THRESHOLD_WIDTH=1920

# Paths relative to script location
REALESRGAN_DIR="$SCRIPT_DIR"
WAIFU2X_DIR="$SCRIPT_DIR/../waifu2x-ncnn-vulkan/waifu2x-ncnn-vulkan-20220728-ubuntu"

# Allow override via environment variables
[ -n "${VIDEO_UPSCALE_REALESRGAN:-}" ] && REALESRGAN_DIR="$VIDEO_UPSCALE_REALESRGAN"
[ -n "${VIDEO_UPSCALE_WAIFU2X:-}" ] && WAIFU2X_DIR="$VIDEO_UPSCALE_WAIFU2X"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Status output functions
echo "JOB_ID: $JOB_ID"

error_exit() {
    echo "STATUS: ERROR: $1"
    exit 1
}

# Validate
[ -z "$INPUT_PATH" ] || [ -z "$OUTPUT_PATH" ] && error_exit "Usage: $0 INPUT_PATH OUTPUT_PATH [MODE] [PRESET] [ENGINE] [JOB_ID]"
[ -f "$INPUT_PATH" ] || error_exit "Input file not found: $INPUT_PATH"

# Auto-detect engine based on mode
if [ -z "$ENGINE" ]; then
    if [ "$MODE" = "anime" ]; then
        ENGINE="waifu2x"
    else
        ENGINE="realesrgan"
    fi
fi
echo "PHASE: STARTING"
log_info "Using engine: $ENGINE"

# Create cache dir
mkdir -p "$CACHE_DIR"

# Cache key (include job_id to avoid conflicts)
INPUT_HASH=$(md5sum "$INPUT_PATH" | cut -d' ' -f1)
CACHE_KEY="${INPUT_HASH}_${MODE}_${PRESET}_${ENGINE}"
CACHED_OUTPUT="${CACHE_DIR}/${CACHE_KEY}.mp4"

# Check cache
if [ -f "$CACHED_OUTPUT" ]; then
    log_info "Found cached result"
    cp "$CACHED_OUTPUT" "$OUTPUT_PATH"
    echo "STATUS: OK"
    echo "UPSCALED_VIDEO: $OUTPUT_PATH"
    echo "(Reused from cache)"
    exit 0
fi

# Safety checks
log_info "Checking video properties..."
DURATION_SEC=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$INPUT_PATH")
DURATION_MIN=$(echo "$DURATION_SEC / 60" | bc -l)
WIDTH=$(ffprobe -v error -select_streams v:0 -show_entries stream=width -of csv=p=0 "$INPUT_PATH")
HEIGHT=$(ffprobe -v error -select_streams v:0 -show_entries stream=height -of csv=p=0 "$INPUT_PATH")

log_info "Video: ${WIDTH}x${HEIGHT}, Duration: ${DURATION_MIN} min"

if (( $(echo "$DURATION_MIN > $MAX_DURATION_MINUTES" | bc -l) )); then
    error_exit "Duration too long (${DURATION_MIN} min > ${MAX_DURATION_MINUTES} min). Ask user to confirm or trim."
fi

# Upscale factor
UPSCALE_FACTOR=2
if [ "$PRESET" = "high" ] && [ "$WIDTH" -lt "$SAFE_UPSCALE_THRESHOLD_WIDTH" ]; then
    UPSCALE_FACTOR=4
fi

# Determine model
case "$MODE" in
    anime) 
        MODEL_NAME="realesrgan-x4plus-anime"
        WAIFU2X_MODEL_PATH="$WAIFU2X_DIR/models-cunet"
        ;;
    real|*) 
        MODEL_NAME="realesrgan-x4plus"
        WAIFU2X_MODEL_PATH="$WAIFU2X_DIR/models-upconv_7_photo"
        ;;
esac
log_info "Mode: $MODE, Upscale: ${UPSCALE_FACTOR}x"

# FPS
FPS=$(ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate -of csv=p=0 "$INPUT_PATH")
if [[ "$FPS" == *"/"* ]]; then
    FPS=$(echo "$FPS" | bc -l | xargs printf "%.0f")
fi
[ -z "$FPS" ] && FPS=30

# Encoding settings
case "$PRESET" in
    high) CRF=16; FFPRESET="slow" ;;
    fast|*) CRF=20; FFPRESET="fast" ;;
esac
log_info "Preset: $PRESET (CRF=$CRF)"

# Temp dir with job ID
TEMP_DIR=$(mktemp -d "/tmp/openclaw-upscale-${JOB_ID}-XXXXXX")
trap "rm -rf $TEMP_DIR" EXIT

# Extract frames
echo "PHASE: EXTRACTING_FRAMES"
log_info "Extracting frames..."
ffmpeg -y -i "$INPUT_PATH" -q:v 1 "$TEMP_DIR/frame_%08d.png" 2>&1 | tail -3
FRAME_COUNT=$(ls -1 "$TEMP_DIR"/frame_*.png 2>/dev/null | wc -l)
[ "$FRAME_COUNT" -eq 0 ] && error_exit "No frames extracted"
echo "FRAMES_TOTAL: $FRAME_COUNT"
log_info "Extracted $FRAME_COUNT frames"

# Upscale
echo "PHASE: UPSCALING"
log_info "Upscaling frames..."
FRAME_NUM=0

# Calculate progress threshold (every 10%)
PROGRESS_THRESHOLD=$((FRAME_COUNT / 10))
[ $PROGRESS_THRESHOLD -eq 0 ] && PROGRESS_THRESHOLD=1

if [ "$ENGINE" = "waifu2x" ]; then
    for frame in "$TEMP_DIR"/frame_*.png; do
        FRAME_NUM=$((FRAME_NUM + 1))
        "$WAIFU2X_DIR/waifu2x-ncnn-vulkan" -i "$frame" -o "$frame" -n 0 -s "$UPSCALE_FACTOR" -m "$WAIFU2X_MODEL_PATH" -f png 2>/dev/null
        if [ $((FRAME_NUM % PROGRESS_THRESHOLD)) -eq 0 ]; then
            echo "PROGRESS: $FRAME_NUM/$FRAME_COUNT"
        fi
    done
else
    for frame in "$TEMP_DIR"/frame_*.png; do
        FRAME_NUM=$((FRAME_NUM + 1))
        "$REALESRGAN_DIR/realesrgan-ncnn-vulkan" -i "$frame" -o "$frame" -n "$MODEL_NAME" -s "$UPSCALE_FACTOR" -f png 2>/dev/null
        if [ $((FRAME_NUM % PROGRESS_THRESHOLD)) -eq 0 ]; then
            echo "PROGRESS: $FRAME_NUM/$FRAME_COUNT"
        fi
    done
fi

echo "PROGRESS: $FRAME_COUNT/$FRAME_COUNT"
log_info "Upscaling complete"

# Re-encode
echo "PHASE: ENCODING"
log_info "Re-encoding video..."
HAS_AUDIO=$(ffprobe -v error -select_streams a:0 -show_entries stream=codec_type -of csv=p=0 "$INPUT_PATH")

if [ -n "$HAS_AUDIO" ]; then
    ffmpeg -y -framerate "$FPS" -i "$TEMP_DIR/frame_%08d.png" -i "$INPUT_PATH" \
        -map 0:v:0 -map 1:a:0 \
        -c:v libx264 -preset "$FFPRESET" -crf "$CRF" -pix_fmt yuv420p -movflags +faststart \
        -c:a aac -b:a 128k \
        "$OUTPUT_PATH" 2>&1 | tail -5
else
    ffmpeg -y -framerate "$FPS" -i "$TEMP_DIR/frame_%08d.png" \
        -c:v libx264 -preset "$FFPRESET" -crf "$CRF" -pix_fmt yuv420p -movflags +faststart \
        "$OUTPUT_PATH" 2>&1 | tail -5
fi

[ ! -s "$OUTPUT_PATH" ] && error_exit "Failed to create output"

# Cache
cp "$OUTPUT_PATH" "$CACHED_OUTPUT"

echo "PHASE: DONE"
log_info "Done! Size: $(ls -lh "$OUTPUT_PATH" | awk '{print $5}')"

echo "STATUS: OK"
echo "UPSCALED_VIDEO: $OUTPUT_PATH"
