#!/bin/bash
# LifeLog Recorder - 实时记录单条消息到 Notion（只记录日常生活）
# 使用前请配置下方的 NOTION_KEY 和 DATABASE_ID

# ===== 配置区域 =====
# 请替换为你的 Notion API Key (Integration Token)
NOTION_KEY="YOUR_NOTION_API_KEY"
# 请替换为你的 Notion Database ID
DATABASE_ID="YOUR_DATABASE_ID"
# ====================

API_VERSION="2022-06-28"

# 参数：消息内容
CONTENT="$1"

# 智能解析消息中的日期
parse_date_from_content() {
    local content="$1"
    local today=$(date +%Y-%m-%d)
    
    # 今天
    if echo "$content" | grep -qE "^(今天|今日|今儿)"; then
        echo "$today"
        return
    fi
    
    # 昨天
    if echo "$content" | grep -qE "^(昨天|昨日|昨儿)"; then
        date -d "yesterday" +%Y-%m-%d
        return
    fi
    
    # 前天
    if echo "$content" | grep -qE "^(前天)"; then
        date -d "2 days ago" +%Y-%m-%d
        return
    fi
    
    # 明天
    if echo "$content" | grep -qE "^(明天|明日|明儿)"; then
        date -d "tomorrow" +%Y-%m-%d
        return
    fi
    
    # 后天
    if echo "$content" | grep -qE "^(后天)"; then
        date -d "2 days" +%Y-%m-%d
        return
    fi
    
    # 具体日期格式：2026-02-22, 2026年2月22日, 2月22日, 02-22
    if echo "$content" | grep -qE "[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}"; then
        echo "$content" | grep -oE "[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}" | head -1
        return
    fi
    
    if echo "$content" | grep -qE "[0-9]{1,2}月[0-9]{1,2}日"; then
        local month=$(echo "$content" | grep -oE "[0-9]{1,2}月[0-9]{1,2}日" | head -1 | grep -oE "[0-9]{1,2}")
        local day=$(echo "$content" | grep -oE "[0-9]{1,2}日" | head -1 | grep -oE "[0-9]{1,2}")
        local year=$(date +%Y)
        echo "$year-$(printf "%02d" $month)-$(printf "%02d" $day)"
        return
    fi
    
    # 没识别到，返回今天
    echo "$today"
}

# 解析目标日期
TARGET_DATE=$(parse_date_from_content "$CONTENT")
TODAY=$(date +%Y-%m-%d)

# 判断是否为补录（说的日期不是今天）
IS_BACKDATE=false
if [ "$TARGET_DATE" != "$TODAY" ]; then
    IS_BACKDATE=true
fi

echo "📅 识别到日期: $TARGET_DATE (今天: $TODAY, 补录: $IS_BACKDATE)"

# 时间戳：补录的会带 🔁 标记
if [ "$IS_BACKDATE" = true ]; then
    TIMESTAMP=$(date "+📅 %Y-%m-%d %H:%M 🔁补录")
else
    TIMESTAMP=$(date "+📅 %Y-%m-%d %H:%M")
fi

if [ -z "$CONTENT" ]; then
    echo "❌ 消息内容不能为空"
    exit 1
fi

# 检查是否为纯工作指令（不记录）
# 注意：包含感想、吐槽、心情的内容即使提到工作也应该记录
is_work_content() {
    local content="$1"
    # 只过滤纯粹的工作指令，不过滤带有生活感想的内容
    # 如果同时包含情绪/感受词汇，则不算纯工作内容
    local emotion_keywords="觉得|感觉|累|烦|开心|有趣|抽象|无语|好玩|难受|爽|想|希望|花了|搞了|折腾"
    if echo "$content" | grep -qE "$emotion_keywords"; then
        return 1  # 有情绪表达，不是纯工作内容，应该记录
    fi
    
    local work_keywords="帮我写代码|修改代码|部署服务|启动服务器|运行测试|git push|编译"
    if echo "$content" | grep -qE "$work_keywords"; then
        return 0  # 纯工作指令
    fi
    return 1
}

# 检查是否为测试/确认类消息（不记录）
is_test_or_ack() {
    local content="$1"
    # 测试类消息
    if echo "$content" | grep -qE "^测试|^试一下|测试一下|测试测试"; then
        return 0
    fi
    # 特别短的确认消息（小于4个字符）
    if [ ${#content} -lt 4 ]; then
        return 0
    fi
    return 1
}

# 检查是否为配置/系统消息（不记录）
is_system_message() {
    local content="$1"
    local sys_keywords="设置记录|配置Notion|修改LifeLog|记录方式|修改偏好"
    
    if echo "$content" | grep -qE "$sys_keywords"; then
        return 0
    fi
    return 1
}

# 判断是否需要记录
if is_work_content "$CONTENT"; then
    echo "⏭️ 跳过工作内容: ${CONTENT:0:30}..."
    exit 0
fi

if is_system_message "$CONTENT"; then
    echo "⏭️ 跳过系统消息: ${CONTENT:0:30}..."
    exit 0
fi

if is_test_or_ack "$CONTENT"; then
    echo "⏭️ 跳过测试/确认消息: ${CONTENT:0:30}..."
    exit 0
fi

# 1. 检查今天是否已有记录
echo "🔍 检查 $TARGET_DATE 是否有记录..."

RESPONSE=$(curl -s -X POST "https://api.notion.com/v1/databases/$DATABASE_ID/query" \
    -H "Authorization: Bearer $NOTION_KEY" \
    -H "Notion-Version: $API_VERSION" \
    -H "Content-Type: application/json" \
    -d "{\"filter\": { \"property\": \"日期\", \"title\": { \"equals\": \"$TARGET_DATE\" } }, \"page_size\": 1}")

COUNT=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('results',[])))")

if [ "$COUNT" -gt 0 ]; then
    # 已有记录，追加原文
    PAGE_ID=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['results'][0]['id'])")
    EXISTING=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['results'][0]['properties'].get('原文',{}).get('rich_text',[{}])[0].get('plain_text',''))")
    
    # 拼接新旧内容
    NEW_CONTENT="${EXISTING}"$'\n'"${TIMESTAMP} ${CONTENT}"
    
    echo "📝 追加到现有记录 ${PAGE_ID:0:8}"
    echo "   原有: ${EXISTING:0:50}..."
    echo "   新增: ${CONTENT}"
    
    # 更新原文字段
    RESULT=$(curl -s -X PATCH "https://api.notion.com/v1/pages/$PAGE_ID" \
        -H "Authorization: Bearer $NOTION_KEY" \
        -H "Notion-Version: $API_VERSION" \
        -H "Content-Type: application/json" \
        -d "{
            \"properties\": {
                \"原文\": { \"rich_text\": [{ \"text\": { \"content\": \"$(echo "$NEW_CONTENT" | head -1000 | tr '\n' ' ' | sed 's/\"/\\\"/g')\" } }] }
            }
        }")
    
    # 检查是否包含 page 对象
    if echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print('OK' if d.get('object')=='page' else 'FAIL')" 2>/dev/null | grep -q "OK"; then
        echo "NOTION_OK"
    else
        echo "NOTION_FAIL: $RESULT"
    fi
else
    # 没有记录，创建新记录
    FORMATTED="${TIMESTAMP} ${CONTENT}"
    
    echo "🆕 创建新记录"
    echo "   内容: ${FORMATTED}"
    
    RESULT=$(curl -s -X POST "https://api.notion.com/v1/pages" \
        -H "Authorization: Bearer $NOTION_KEY" \
        -H "Notion-Version: $API_VERSION" \
        -H "Content-Type: application/json" \
        -d "{
            \"parent\": { \"database_id\": \"$DATABASE_ID\" },
            \"properties\": {
                \"日期\": { \"title\": [{ \"text\": { \"content\": \"$TARGET_DATE\" } }] },
                \"原文\": { \"rich_text\": [{ \"text\": { \"content\": \"$FORMATTED\" } }] }
            }
        }")
    
    if echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print('OK' if d.get('object')=='page' else 'FAIL')" 2>/dev/null | grep -q "OK"; then
        echo "NOTION_OK"
    else
        echo "NOTION_FAIL"
    fi
fi
