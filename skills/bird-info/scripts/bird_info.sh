#!/bin/bash

# Bird Info Skill - Main Entry Point
# Query bird information from dongniao.net using web_fetch

set -e

BIRD_NAME="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -z "$BIRD_NAME" ]; then
    echo "用法：bird-info <鸟名>"
    echo "示例：bird-info '麻雀' 或 bird-info 'Sparrow'"
    echo ""
    echo "或者在 OpenClaw 对话中直接说："
    echo "  - 帮我查一下麻雀的信息"
    echo "  - 查询绿孔雀的详细资料"
    exit 1
fi

# Run the Python skill
python3 "$SCRIPT_DIR/bird_info_skill.py" "$BIRD_NAME"
