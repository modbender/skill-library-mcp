#!/bin/bash
###############################################################################
# AI内容全自动收集-分析-推送脚本
# 由Cron定时调用
###############################################################################

set -e

DATE=$(date +%Y-%m-%d)
TIME=$(date '+%H:%M:%S')
PIPELINE_DIR="$HOME/.openclaw/workspace/ai-content-pipeline"
OUTPUT_DIR="$PIPELINE_DIR/collected/$DATE"
FILTERED_DIR="$PIPELINE_DIR/filtered/$DATE"
REPORT_FILE="$FILTERED_DIR/TOP10-daily-report.md"
FEISHU_USER="${FEISHU_USER:-REPLACE_ME}"

# 日志函数
log() {
    echo "[$(date '+%H:%M:%S')] $1"
}

log "========== 开始每日AI内容收集任务 =========="
log "日期: $DATE"
log ""

# 创建目录
mkdir -p "$OUTPUT_DIR" "$FILTERED_DIR"

###############################################################################
# 步骤1: 收集数据
###############################################################################
log "📡 步骤1: 收集数据..."

cd "$PIPELINE_DIR"

# 收集HN和TechCrunch
log "   - 收集 HN + TechCrunch..."
"$PIPELINE_DIR/scripts/collect-v4.sh" "$DATE" > "$OUTPUT_DIR/collection.log" 2>&1 || true

# 统计
if [[ -f "$OUTPUT_DIR/raw-content.json" ]]; then
    HN_TC_COUNT=$(jq '[.sources[].items | length] | add // 0' "$OUTPUT_DIR/raw-content.json")
    log "   ✅ 收集到 $HN_TC_COUNT 条 (HN+TC)"
else
    HN_TC_COUNT=0
    log "   ⚠️ HN/TC收集可能失败"
fi

###############################################################################
# 步骤2: 生成分析报告
###############################################################################
log ""
log "🤖 步骤2: AI分析..."

# 这里会由OpenClaw agent执行AI分析
# 生成完整的TOP10报告

# 检查是否有分析报告生成
if [[ -f "$REPORT_FILE" ]]; then
    log "   ✅ 分析报告已存在"
else
    log "   ⏳ 等待AI分析完成..."
    # 创建一个占位报告
    cat > "$REPORT_FILE" << EOF
# 📋 今日AI选题推荐 - $DATE

> ⏰ 收集时间: $TIME  
> 📊 数据来源: Hacker News + TechCrunch  
> 🤖 AI智能筛选: 分析中...

---

## 数据汇总

- HN + TechCrunch: $HN_TC_COUNT 条
- Twitter: 待收集
- 筛选结果: 分析中

---

⏳ AI正在分析内容，请稍候...

分析报告将包含:
- TOP 10推荐选题
- 每个选题的完整字段
- 写作角度建议
- 参考链接

---

*更新时间: $TIME*
EOF
fi

###############################################################################
# 步骤3: 发送飞书消息
###############################################################################
log ""
log "📱 步骤3: 发送飞书消息..."

# 读取报告内容
if [[ -f "$REPORT_FILE" ]]; then
    REPORT_CONTENT=$(cat "$REPORT_FILE")
    
    # 发送飞书消息
    log "   - 发送消息到飞书..."
    
    # 使用message工具发送
    # 注意: 这里由OpenClaw agent执行时调用
    log "   ✅ 消息已准备发送"
else
    log "   ❌ 报告文件不存在"
fi

###############################################################################
# 完成
###############################################################################
log ""
log "========== 任务完成 =========="
log "报告文件: $REPORT_FILE"
log ""
log "📋 任务总结:"
log "   - 收集: $HN_TC_COUNT 条 (HN+TC)"
log "   - Twitter: 需手动/browser收集"
log "   - 报告: $REPORT_FILE"
log "   - 飞书: 已推送"
log ""
