#!/bin/bash
set -e

DEFAULT_OUTPUT="$HOME/openclaw_audio.mp3"

# 提取视频音频
extract_audio() {
    local input="$1"
    local output="${2:-$DEFAULT_OUTPUT}"
    echo "ffmpeg -y -i $input -vn -acodec mp3 $output"
}

# 调整音量
adjust_volume() {
    local input="$1"
    local volume="$2"
    local output="${3:-$DEFAULT_OUTPUT}"
    local vol=$(echo "scale=2; $volume/100" | bc)
    echo "ffmpeg -y -i $input -filter:a \"volume=$vol\" $output"
}

# 自然语言解析
parse_natural_language() {
    local cmd="$1"
    local output="${2:-$DEFAULT_OUTPUT}"
    
    if echo "$cmd" | grep -E "提取音频|视频转音频"; then
        local input=$(echo "$cmd" | grep -oP "~/[^ ]+\.mp4" | head -1)
        extract_audio "$input" "$output"
    elif echo "$cmd" | grep -E "调整音量|加大音量|减小音量"; then
        local input=$(echo "$cmd" | grep -oP "~/[^ ]+\.(mp3|wav)" | head -1)
        local volume=$(echo "$cmd" | grep -oP "音量\d+" | sed 's/音量//' | head -1 || echo "50")
        adjust_volume "$input" "$volume" "$output"
    else
        echo "$cmd"
    fi
}

# 主逻辑
COMMAND="$1"
OUTPUT="${2:-$DEFAULT_OUTPUT}"

AUDIO_CMD=$(parse_natural_language "$COMMAND" "$OUTPUT")
echo "[OpenClaw] 执行音频命令：$AUDIO_CMD"
eval "$AUDIO_CMD"

echo "[OpenClaw] 音频处理完成：$OUTPUT"
echo "$OUTPUT"
