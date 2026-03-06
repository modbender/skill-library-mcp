#!/bin/bash
# feishu-file 主脚本（使用Python后端）
# 用法: ./send_file.sh <文件路径> [文件名] [接收者ID]

set -e

WORKSPACE="/root/.openclaw/workspace"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 检查参数
if [ $# -lt 1 ]; then
    echo "❌ 用法: $0 <文件路径> [文件名] [接收者ID]"
    echo ""
    echo "示例:"
    echo "  $0 /path/to/file.pdf"
    echo "  $0 /path/to/file.pdf \"报告.pdf\""
    echo "  $0 /path/to/file.pdf \"报告.pdf\" \"ou_xxx\""
    exit 1
fi

FILE_PATH="$1"
FILE_NAME="${2:-$(basename "$FILE_PATH")}"
RECEIVER="${3:-${FEISHU_RECEIVER}}"

# 检查文件
if [ ! -f "$FILE_PATH" ]; then
    echo "❌ 文件不存在: $FILE_PATH"
    exit 1
fi

# 调用Python脚本
python3 "$SCRIPT_DIR/feishu_file_upload_fixed_v2.py" "$FILE_PATH" "$FILE_NAME"

if [ $? -eq 0 ]; then
    echo "✅ 文件发送完成!"
else
    echo "❌ 文件发送失败"
    exit 1
fi
