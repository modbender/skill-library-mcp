#!/bin/bash
# 使用 mcporter 查询火车票
# 用法: query-tickets.sh <日期> <出发站代码> <到达站代码> [可选参数]

set -e

DATE="$1"
FROM_STATION="$2"
TO_STATION="$3"
CONFIG_FILE="${4:-$HOME/.mcporter/mcporter.json}"

# 检查参数
if [ -z "$DATE" ] || [ -z "$FROM_STATION" ] || [ -z "$TO_STATION" ]; then
    echo "用法: query-tickets.sh <日期(YYYY-MM-DD)> <出发站代码> <到达站代码> [配置文件路径]"
    echo "示例: query-tickets.sh 2026-02-18 SHH KYH"
    exit 1
fi

echo "查询: $DATE 从 $FROM_STATION 到 $TO_STATION 的列车"
echo ""

mcporter call 12306.get-tickets \
  date="$DATE" \
  fromStation="$FROM_STATION" \
  toStation="$TO_STATION" \
  trainFilterFlags="GD" \
  sortFlag="startTime" \
  format="text" \
  --config "$CONFIG_FILE"