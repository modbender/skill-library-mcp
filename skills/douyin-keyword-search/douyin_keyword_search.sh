#!/bin/bash
# 抖音关键词搜索抓取技能

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/douyin_keyword_search.py"

# 检查 Python 脚本是否存在
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "错误：找不到 Python 脚本: $PYTHON_SCRIPT"
    exit 1
fi

# 调用 Python 脚本，传递所有参数
python "$PYTHON_SCRIPT" "$@"