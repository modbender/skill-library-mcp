#!/bin/bash
# 使用 mcporter 查询下午火车票（12:00-18:00）
# 用法: query-afternoon.sh <日期> <出发站代码> <到达站代码>

set -e

DATE="$1"
FROM_STATION="$2"
TO_STATION="$3"
CONFIG_FILE="${4:-$HOME/.mcporter/mcporter.json}"

if [ -z "$DATE" ] || [ -z "$FROM_STATION" ] || [ -z "$TO_STATION" ]; then
    echo "用法: query-afternoon.sh <日期(YYYY-MM-DD)> <出发站代码> <到达站代码> [配置文件路径]"
    echo "示例: query-afternoon.sh 2026-02-18 SHH KYH"
    exit 1
fi

echo "查询: $DATE 下午班次 (12:00-18:00) 从 $FROM_STATION 到 $TO_STATION"
echo ""

mcporter call 12306.get-tickets \
  date="$DATE" \
  fromStation="$FROM_STATION" \
  toStation="$TO_STATION" \
  trainFilterFlags="GD" \
  earliestStartTime=12 \
  latestStartTime=18 \
  sortFlag="startTime" \
  format="text" \
  --config "$CONFIG_FILE"