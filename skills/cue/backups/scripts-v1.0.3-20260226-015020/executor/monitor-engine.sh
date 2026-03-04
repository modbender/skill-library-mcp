#!/bin/bash
# Monitor Engine - 监控执行主控
# 级联执行：Search → Browser-use

set -e

MONITOR_ID="$1"
CONFIG_FILE="$2"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXECUTOR_DIR="$SCRIPT_DIR"

if [ -z "$MONITOR_ID" ] || [ -z "$CONFIG_FILE" ]; then
    echo '{"error": "Monitor ID and config file required"}'
    exit 1
fi

if [ ! -f "$CONFIG_FILE" ]; then
    echo "{\"error\": \"Config file not found: $CONFIG_FILE\"}"
    exit 1
fi

# 加载监控配置（支持多种字段名格式）
TITLE=$(jq -r '.title // "未命名监控"' "$CONFIG_FILE")
SOURCE=$(jq -r '.target_source // .source // ""' "$CONFIG_FILE")
TRIGGER_CONDITION=$(jq -r '.semantic_trigger // .trigger_condition // ""' "$CONFIG_FILE")
CATEGORY=$(jq -r '.category // "Data"' "$CONFIG_FILE")
SYMBOL=$(jq -r '.symbol // ""' "$CONFIG_FILE")

echo "🔔 监控执行: $TITLE"
echo "   监控ID: $MONITOR_ID"
echo "   信源: $SOURCE"
echo "   触发条件: $TRIGGER_CONDITION"
echo ""

# 执行层级控制
EXECUTION_RESULT=""
CONFIDENCE=0

# ===========================================
# Layer 1: Integrated Search (Tavily + QVeris)
# ===========================================
echo "📡 Layer 1: 尝试通过智能搜索获取信息..."

# 优先使用整合执行器（根据类别自动选择数据源）
if [ -f "$EXECUTOR_DIR/integrated-search.sh" ]; then
    LAYER1_RESULT=$($EXECUTOR_DIR/integrated-search.sh "$SOURCE" "$TRIGGER_CONDITION" "$CATEGORY" "$SYMBOL" 2>&1)
    LAYER1_EXIT=$?
else
    # 回退到传统 search-executor
    LAYER1_RESULT=$($EXECUTOR_DIR/search-executor.sh "$SOURCE" "$TRIGGER_CONDITION" 2>&1)
    LAYER1_EXIT=$?
fi

if [ $LAYER1_EXIT -eq 0 ] && [ -n "$LAYER1_RESULT" ]; then
    echo "✅ Layer 1 成功获取信息"
    EXECUTION_RESULT="$LAYER1_RESULT"
    CONFIDENCE=80
else
    echo "⚠️  Layer 1 未能获取足够信息"
    echo "   原因: ${LAYER1_RESULT:-未返回数据}"
fi

# ===========================================
# Layer 2: Condition Evaluation
# ===========================================
if [ $CONFIDENCE -gt 0 ]; then
    echo ""
    echo "🔍 Layer 2: 评估触发条件..."
    
    # 使用 AI 判断条件是否满足
    EVAL_PROMPT=$(cat << EOF
请根据以下信息判断是否满足监控触发条件：

监控标题: $TITLE
触发条件: $TRIGGER_CONDITION
获取到的信息: $EXECUTION_RESULT

请回答：
1. 条件是否满足？（是/否/不确定）
2. 置信度（0-100）
3. 简要说明理由

格式：满足|置信度|理由
EOF
)
    
    # 调用 AI 评估（简化版，实际使用 API）
    EVAL_RESULT=$(echo "$EVAL_PROMPT" | head -c 1000)
    
    # 简化判断逻辑（关键词匹配）
    if echo "$EXECUTION_RESULT" | grep -qiE "(上涨|突破|超过|大于|达到|满足|触发|符合)"; then
        CONDITION_MET="true"
        echo "✅ 条件满足！"
    else
        CONDITION_MET="false"
        echo "⏳ 条件未满足"
    fi
fi

# ===========================================
# Layer 3: Browser-use Agent (Fallback)
# ===========================================
if [ $CONFIDENCE -eq 0 ] || [ "$CONDITION_MET" = "uncertain" ]; then
    echo ""
    echo "🌐 Layer 3: 使用 Browser-use Agent..."
    
    LAYER3_RESULT=$($EXECUTOR_DIR/browser-executor.sh "$SOURCE" "$TRIGGER_CONDITION" 2>&1)
    LAYER3_EXIT=$?
    
    if [ $LAYER3_EXIT -eq 0 ] && [ -n "$LAYER3_RESULT" ]; then
        echo "✅ Layer 3 成功获取信息"
        EXECUTION_RESULT="$LAYER3_RESULT"
        CONFIDENCE=90
        
        # 重新评估条件
        if echo "$EXECUTION_RESULT" | grep -qiE "(上涨|突破|超过|大于|达到|满足|触发|符合)"; then
            CONDITION_MET="true"
            echo "✅ 条件满足！"
        else
            CONDITION_MET="false"
            echo "⏳ 条件未满足"
        fi
    else
        echo "❌ Layer 3 也未能获取信息"
        echo "   监控执行失败，将在下次调度时重试"
        exit 1
    fi
fi

# ===========================================
# 结果输出
# ===========================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$CONDITION_MET" = "true" ]; then
    echo "🚨 监控触发: $TITLE"
    echo ""
    echo "📊 执行结果:"
    echo "$EXECUTION_RESULT" | head -20
    echo ""
    echo "✅ 触发条件已满足，发送通知..."
    
    # 构建通知消息
    NOTIFICATION=$(cat << EOF
🚨 **监控触发: $TITLE**

📊 **触发条件:**
$TRIGGER_CONDITION

📋 **执行结果:**
$EXECUTION_RESULT

⏰ **触发时间:** $(date '+%Y-%m-%d %H:%M:%S')

---
*监控ID: $MONITOR_ID*
EOF
)
    
    # 发送通知
    echo "$NOTIFICATION" > "/tmp/monitor_notification_${MONITOR_ID}.txt"
    echo "   通知已保存: /tmp/monitor_notification_${MONITOR_ID}.txt"
    
    # 输出结果
    jq -n \
        --arg monitor_id "$MONITOR_ID" \
        --arg title "$TITLE" \
        --arg condition "$TRIGGER_CONDITION" \
        --arg result "$EXECUTION_RESULT" \
        --arg triggered "true" \
        '{monitor_id: $monitor_id, title: $title, triggered: $triggered, result: $result}'
    
else
    echo "✓ 监控正常: $TITLE"
    echo "  条件未满足，继续监控"
    
    jq -n \
        --arg monitor_id "$MONITOR_ID" \
        --arg title "$TITLE" \
        --arg triggered "false" \
        '{monitor_id: $monitor_id, title: $title, triggered: $triggered}'
fi
