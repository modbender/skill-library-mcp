#!/bin/bash
# CueCue Monitor - 创建监控项（本地存储版本）
# 方案A：纯本地存储，不调用 CueCue API

set -e

CUECUE_BASE_URL="${CUECUE_BASE_URL:-https://cuecue.cn}"

MONITOR_CONFIG="$1"
OUTPUT_FILE="${2:-/tmp/monitor_create_result.json}"
CHAT_ID="${CHAT_ID:-${FEISHU_CHAT_ID:-default}}"

if [ -z "$MONITOR_CONFIG" ]; then
    echo '{"error": "Monitor configuration is required"}' >&2
    exit 1
fi

# 如果是文件路径，读取内容
if [ -f "$MONITOR_CONFIG" ]; then
    MONITOR_CONFIG=$(cat "$MONITOR_CONFIG")
fi

echo "🔧 正在创建监控项..." >&2

# 解析监控配置
TITLE=$(echo "$MONITOR_CONFIG" | jq -r '.title // "未命名监控"')
SYMBOL=$(echo "$MONITOR_CONFIG" | jq -r '.related_asset_symbol // .symbol // ""')
CATEGORY=$(echo "$MONITOR_CONFIG" | jq -r '.category // "Data"')
SIGNIFICANCE=$(echo "$MONITOR_CONFIG" | jq -r '.significance // "Medium"')
SOURCE=$(echo "$MONITOR_CONFIG" | jq -r '.target_source // .source // ""')
CRON=$(echo "$MONITOR_CONFIG" | jq -r '.frequency_cron // .frequency // "0 9 * * 1-5"')
START_DATE=$(echo "$MONITOR_CONFIG" | jq -r '.start_date // ""')
TRIGGER=$(echo "$MONITOR_CONFIG" | jq -r '.semantic_trigger // .trigger_condition // ""')
REASON=$(echo "$MONITOR_CONFIG" | jq -r '.reason_for_user // .description // ""')
SEARCH_QUERY=$(echo "$MONITOR_CONFIG" | jq -r '.search_query // ""')

echo "  📊 监控: $TITLE" >&2
echo "  🏷️  标的: $SYMBOL" >&2
echo "  📅 频率: $CRON" >&2

# 生成唯一监控ID（使用时间戳+随机数）
MONITOR_ID="monitor_$(date +%s%N | cut -c1-16)_$(openssl rand -hex 4 2>/dev/null || echo $RANDOM)"

# 确保本地监控目录存在
LOCAL_MONITORS_DIR="$HOME/.cuecue/users/$CHAT_ID/monitors"
mkdir -p "$LOCAL_MONITORS_DIR"

# 构建完整的监控配置
FULL_CONFIG=$(jq -n \
    --arg id "$MONITOR_ID" \
    --arg title "$TITLE" \
    --arg symbol "$SYMBOL" \
    --arg category "$CATEGORY" \
    --arg significance "$SIGNIFICANCE" \
    --arg source "$SOURCE" \
    --arg frequency "$CRON" \
    --arg start_date "$START_DATE" \
    --arg trigger "$TRIGGER" \
    --arg description "$REASON" \
    --arg search_query "$SEARCH_QUERY" \
    --arg created_at "$(date -Iseconds)" \
    --arg status "active" \
    '{
        monitor_id: $id,
        title: $title,
        symbol: $symbol,
        category: $category,
        significance: $significance,
        source: $source,
        frequency: $frequency,
        start_date: $start_date,
        trigger_condition: $trigger,
        description: $description,
        search_query: $search_query,
        created_at: $created_at,
        status: $status
    }')

# 保存到本地文件
LOCAL_MONITOR_FILE="$LOCAL_MONITORS_DIR/${MONITOR_ID}.json"
echo "$FULL_CONFIG" > "$LOCAL_MONITOR_FILE"

# 构建返回结果
RESULT=$(jq -n \
    --arg id "$MONITOR_ID" \
    --arg title "$TITLE" \
    --arg file "$LOCAL_MONITOR_FILE" \
    --argjson success true \
    '{
        success: $success,
        monitor_id: $id,
        title: $title,
        local_file: $file,
        message: "监控项创建成功"
    }')

# 保存结果到输出文件
echo "$RESULT" > "$OUTPUT_FILE"

echo "  ✅ 监控创建成功！ID: $MONITOR_ID" >&2
echo "  💾 本地配置已保存: $LOCAL_MONITOR_FILE" >&2

echo "$RESULT"
