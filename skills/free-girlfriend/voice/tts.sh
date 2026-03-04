#!/bin/bash
# 免费 TTS 语音生成脚本

TEXT="$1"
OUTPUT="${2:-output.mp3}"
VOICE="${3:-zh-CN-XiaoxiaoNeural}"

if [ -z "$TEXT" ]; then
  echo "用法: $0 <文本> [输出文件] [音色]"
  echo "可用音色："
  echo "  zh-CN-XiaoxiaoNeural  - 温暖女声（默认）"
  echo "  zh-CN-XiaoyiNeural    - 活泼女声"
  exit 1
fi

edge-tts --voice "$VOICE" --text "$TEXT" --write-media "$OUTPUT"
echo "✅ 语音已生成: $OUTPUT"
