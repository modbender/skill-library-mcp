#!/bin/bash
# Jarvis TTS 语音合成 - Shell 封装
# 用法：./jarvis-tts.sh "要说的内容" [--voice 语音名称]

if [ -z "$1" ]; then
    echo "用法：$0 \"要说的内容\" [--voice 语音名称]"
    exit 1
fi

python3 "$(dirname "$0")/jarvis-tts.py" "$@"
