#!/bin/bash
# 列出Notion中的最近文章

SCRIPT_DIR="$(dirname "$0")"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$SKILL_DIR/config.json"

# 加载配置
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ 配置文件不存在: $CONFIG_FILE"
    exit 1
fi

# 从配置读取API密钥
API_KEY=$(grep -o '"api_key": "[^"]*' "$CONFIG_FILE" 2>/dev/null | cut -d'"' -f4)
TIMEZONE=$(grep -o '"timezone": "[^"]*' "$CONFIG_FILE" 2>/dev/null | cut -d'"' -f4)

# 设置默认值
[ -z "$TIMEZONE" ] && TIMEZONE="Asia/Shanghai"

# 检查API密钥
if [ -z "$API_KEY" ] || [ "$API_KEY" = "ntn_your_api_key_here" ]; then
    echo "❌ 请先在config.json中配置正确的Notion API密钥"
    exit 1
fi

echo "📋 列出Notion最近文章"
echo "========================================"
echo "时区: $TIMEZONE"
echo "API密钥: ${API_KEY:0:10}..."
echo "========================================"
echo ""

# 搜索最近的文章
echo "🔍 搜索最近编辑的文章..."
RESPONSE=$(curl -s -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {
      "value": "page",
      "property": "object"
    },
    "sort": {
      "direction": "descending",
      "timestamp": "last_edited_time"
    },
    "page_size": 10
  }')

# 检查响应
if echo "$RESPONSE" | grep -q '"object":"list"'; then
    echo "✅ 成功获取文章列表"
    echo ""
    
    # 提取文章信息
    echo "📄 最近10篇文章:"
    echo ""
    
    # 使用jq解析JSON（如果可用），否则使用grep
    if command -v jq >/dev/null 2>&1; then
        echo "$RESPONSE" | jq -r '.results[] | "\(.last_edited_time) | \(.id) | \(.properties["标题"]?.title[0]?.plain_text // .properties["Title"]?.title[0]?.plain_text // "未命名页面")"' | while read -r line; do
            # 解析时间
            TIME_PART=$(echo "$line" | cut -d'|' -f1 | xargs)
            PAGE_ID=$(echo "$line" | cut -d'|' -f2 | xargs)
            TITLE=$(echo "$line" | cut -d'|' -f3- | xargs)
            
            # 转换时间格式
            LOCAL_TIME=$(TZ="$TIMEZONE" date -d "$TIME_PART" '+%Y-%m-%d %H:%M' 2>/dev/null || echo "$TIME_PART")
            
            echo "  📝 $TITLE"
            echo "     🆔 ${PAGE_ID:0:8}..."
            echo "     🕒 $LOCAL_TIME"
            echo ""
        done
    else
        # 简单解析
        echo "$RESPONSE" | grep -E '"last_edited_time":"[^"]+"|"id":"[^"]+"|"plain_text":"[^"]+"' | \
        while read -r line1 && read -r line2 && read -r line3; do
            TIME=$(echo "$line1" | cut -d'"' -f4)
            ID=$(echo "$line2" | cut -d'"' -f4)
            TITLE=$(echo "$line3" | cut -d'"' -f4)
            
            LOCAL_TIME=$(TZ="$TIMEZONE" date -d "$TIME" '+%Y-%m-%d %H:%M' 2>/dev/null || echo "$TIME")
            
            echo "  📝 $TITLE"
            echo "     🆔 ${ID:0:8}..."
            echo "     🕒 $LOCAL_TIME"
            echo ""
        done
    fi
    
    # 统计总数
    TOTAL=$(echo "$RESPONSE" | grep -o '"has_more":[^,]*' | head -1 | grep -o '[0-9]*')
    if [ -n "$TOTAL" ] && [ "$TOTAL" -gt 10 ]; then
        echo "📊 提示: 还有更多文章（共 $TOTAL+ 篇）"
    fi
    
else
    echo "❌ 获取文章列表失败"
    echo "响应:"
    echo "$RESPONSE" | head -5
fi

echo ""
echo "========================================"
echo "📋 使用完整Python检查器获取更多信息:"
echo "   python3 $SCRIPT_DIR/real_notion_checker.py"
echo "========================================"