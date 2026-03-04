#!/bin/bash
# B 站视频播放 - Shell 封装
# 用法：./bilibili-player.sh "搜索关键词"

if [ -z "$1" ]; then
    echo "用法：$0 \"搜索关键词\""
    exit 1
fi

python3 "$(dirname "$0")/bilibili-player.py" "$@"
