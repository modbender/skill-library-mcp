#!/bin/bash
# LifeLog Update - 将分析结果写回 Notion
# 用法: lifelog-update.sh <page_id> <情绪状态> <主要事件> <位置> <人员>
# 使用前请配置下方的 NOTION_KEY

# ===== 配置区域 =====
NOTION_KEY="YOUR_NOTION_API_KEY"
# ====================

API_VERSION="2022-06-28"

PAGE_ID="$1"
EMOTION="$2"
EVENTS="$3"
LOCATION="$4"
PEOPLE="$5"

if [ -z "$PAGE_ID" ] || [ -z "$EMOTION" ]; then
    echo "用法: lifelog-update.sh <page_id> <情绪状态> <主要事件> <位置> <人员>"
    exit 1
fi

# 转义 JSON 特殊字符
escape_json() {
    echo "$1" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip()))" | sed 's/^"//;s/"$//'
}

E_EMOTION=$(escape_json "$EMOTION")
E_EVENTS=$(escape_json "$EVENTS")
E_LOCATION=$(escape_json "$LOCATION")
E_PEOPLE=$(escape_json "$PEOPLE")

RESULT=$(curl -s -X PATCH "https://api.notion.com/v1/pages/$PAGE_ID" \
    -H "Authorization: Bearer $NOTION_KEY" \
    -H "Notion-Version: $API_VERSION" \
    -H "Content-Type: application/json" \
    -d "{
        \"properties\": {
            \"情绪状态\": { \"rich_text\": [{ \"text\": { \"content\": \"$E_EMOTION\" } }] },
            \"主要事件\": { \"rich_text\": [{ \"text\": { \"content\": \"$E_EVENTS\" } }] },
            \"位置\": { \"rich_text\": [{ \"text\": { \"content\": \"$E_LOCATION\" } }] },
            \"人员\": { \"rich_text\": [{ \"text\": { \"content\": \"$E_PEOPLE\" } }] }
        }
    }")

if echo "$RESULT" | grep -q '"object": "page"'; then
    echo "✅ 已更新 Notion 页面 $PAGE_ID"
else
    echo "❌ 更新失败: $RESULT"
    exit 1
fi
