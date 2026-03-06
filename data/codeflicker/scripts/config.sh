#!/bin/bash
# 配置 CodeFlicker
# 用法: config.sh [model|smallModel|planModel|visionModel|approvalMode] [值]

KEY="$1"
VALUE="$2"

if [ -z "$KEY" ]; then
    echo "用法: config.sh <配置项> [值]"
    echo ""
    echo "配置项:"
    echo "  model           主模型 (如 glm-5)"
    echo "  smallModel      轻量模型 (如 claude-haiku-4.5)"
    echo "  planModel       规划模型 (如 claude-4.5-sonnet)"
    echo "  visionModel     视觉模型 (如 claude-4.5-sonnet)"
    echo "  approvalMode    审批模式 (default|autoEdit|yolo)"
    echo ""
    echo "示例:"
    echo "  config.sh model glm-5"
    echo "  config.sh approvalMode yolo"
    echo "  config.sh list"
    exit 0
fi

if [ "$KEY" = "list" ]; then
    flickcli config list -g
    exit 0
fi

if [ -z "$VALUE" ]; then
    flickcli config get "$KEY"
else
    flickcli config set -g "$KEY" "$VALUE"
    echo "✅ 已设置 $KEY = $VALUE"
fi