#!/bin/bash
# 使用 mcporter 查询车站代码
# 用法: get-station-code.sh <城市名或车站名>

set -e

NAME="$1"
CONFIG_FILE="${2:-$HOME/.mcporter/mcporter.json}"

if [ -z "$NAME" ]; then
    echo "用法: get-station-code.sh <城市名或车站名>"
    echo "示例: get-station-code.sh 上海"
    echo "示例: get-station-code.sh 上海虹桥"
    exit 1
fi

echo "查询: $NAME 的车站代码"
echo ""

# 尝试先按车站名查询
mcporter call 12306.get-station-code-by-names \
  stationNames="$NAME" \
  --config "$CONFIG_FILE" 2>/dev/null || {
    # 失败则按城市查询
    mcporter call 12306.get-station-code-of-citys \
      citys="$NAME" \
      --config "$CONFIG_FILE"
  }