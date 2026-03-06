#!/bin/bash
###############################################################################
# AI内容分析脚本 - 调用OpenClaw进行智能筛选
# 用法: ./analyze.sh [日期，格式YYYY-MM-DD，默认为今天]
###############################################################################

set -e

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIPELINE_DIR="$(dirname "$SCRIPT_DIR")"
DATE="${1:-$(date +%Y-%m-%d)}"

# 目录
COLLECTED_DIR="$PIPELINE_DIR/collected/$DATE"
FILTERED_DIR="$PIPELINE_DIR/filtered/$DATE"
mkdir -p "$FILTERED_DIR"

# 文件
RAW_JSON="$COLLECTED_DIR/raw-content.json"
OUTPUT_JSON="$FILTERED_DIR/analyzed-content.json"
OUTPUT_MD="$FILTERED_DIR/wechat-worthy.md"
LOG_FILE="$FILTERED_DIR/analysis.log"

# 初始化日志
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 检查原始数据是否存在
if [[ ! -f "$RAW_JSON" ]]; then
    echo "❌ 错误: 未找到原始数据文件 $RAW_JSON"
    echo "请先运行 collect.sh 收集数据"
    exit 1
fi

log "========== AI内容分析开始 =========="
log "日期: $DATE"
log "输入: $RAW_JSON"
log "输出: $FILTERED_DIR"

# 统计原始数据
TOTAL_RAW=$(jq '[.sources[].items | length] | add' "$RAW_JSON")
log "待分析内容: $TOTAL_RAW 条"

# 提取所有内容项，准备分析
jq '[.sources[].items[] | {
    title: .title,
    url: (.url // .hn_url // .permalink),
    source: (.source // .domain // "unknown"),
    author: (.author // "unknown"),
    hotness: (.points // .upvotes // 0),
    comments: (.comments // 0)
}]' "$RAW_JSON" > "$FILTERED_DIR/extracted-items.json"

log "已提取内容到 extracted-items.json"

# 创建分析任务说明
cat > "$FILTERED_DIR/analysis-task.md" << 'EOF'
# AI内容分析任务

你是一个资深的新媒体内容策划专家，专门负责判断AI内容是否适合公众号文章。

## 分析维度

请从以下5个维度评分（1-10分）：

1. **时效性** (Timeliness)
   - 10分: 当天/24小时内的新内容
   - 7-9分: 2-3天内的内容
   - 4-6分: 一周内
   - 1-3分: 较旧的内容

2. **话题性** (Topic Value)
   - 是否会引起读者兴趣和讨论
   - 社交传播潜力
   - 争议度适中（不要太有争议）

3. **专业性/深度** (Profundity)
   - 信息量是否充足
   - 是否有独特见解或数据
   - 是否经得起深度解读

4. **公众号适合度** (WeChat Fit)
   - 是否适合写成公众号文章格式
   - 是否有明确的观点/结论
   - 配图/案例是否丰富

5. **中文受众相关性** (Chinese Relevance)
   - 对中国读者是否有价值
   - 是否有国内应用场景
   - 是否能引发共鸣

## 推荐标准

- **强烈推荐** (8-10分): 值得立即写
- **推荐** (7-8分): 可以考虑写
- **不推荐** (<7分): 暂不考虑

## 输出格式

对每条内容输出：

```
### {序号}. {标题}
- **综合评分**: {平均分}/10
- **各维度评分**:
  - 时效性: {分}
  - 话题性: {分}
  - 专业性: {分}
  - 公众号适合度: {分}
  - 中文受众相关性: {分}
- **原链接**: {url}
- **推荐理由**: {一句话说明为什么推荐}
- **建议写作角度**: {从什么角度写这篇文章}
- **目标受众**: {适合哪些读者}
- **是否推荐**: {是/否}
```

## 待分析内容

EOF

# 将提取的内容附加到任务文件
cat >> "$FILTERED_DIR/analysis-task.md" << EOF

共 $TOTAL_RAW 条内容：

EOF

jq -r '.[] | "### \(.title)\n- 链接: \(.url)\n- 来源: \(.source)\n- 热度: \(.hotness)"' "$FILTERED_DIR/extracted-items.json" >> "$FILTERED_DIR/analysis-task.md"

log "分析任务文件已生成: $FILTERED_DIR/analysis-task.md"
log "内容已准备好，等待AI分析..."

# 创建输出模板
cat > "$OUTPUT_MD" << EOF
# 公众号选题推荐 - $DATE

> 分析时间: $(date '+%Y-%m-%d %H:%M:%S')  
> 数据来源: Hacker News, Reddit  
> 原始条目: $TOTAL_RAW 条  
> 筛选状态: 等待AI分析完成

---

## 🏆 Top 推荐

*分析完成后将显示推荐内容*

---

## 📋 分析说明

此文件由AI自动分析生成。要查看分析结果，请：

1. 使用 OpenClaw 的 \\\`sessions_spawn\\\` 工具调用AI分析
2. 或手动分析 \\\`$FILTERED_DIR/analysis-task.md\\\`

---

**自动分析命令示例**:

\\\`\\\`\\\`
任务: 请分析 $FILTERED_DIR/analysis-task.md 中的内容，
按照评分标准筛选出适合公众号的AI选题，
输出格式化的推荐列表到 $OUTPUT_MD
\\\`\\\`\\\`

EOF

log "输出模板已生成: $OUTPUT_MD"
log "========== 准备完成，等待AI分析 =========="

echo ""
echo "✅ 分析准备完成!"
echo "📁 输出目录: $FILTERED_DIR"
echo "📄 分析任务: $FILTERED_DIR/analysis-task.md"
echo "📊 待分析内容: $TOTAL_RAW 条"
echo ""
echo "下一步: 使用 OpenClaw 的 sessions_spawn 工具执行AI分析"
echo "  或运行: openclaw agent --message \"分析 $FILTERED_DIR/analysis-task.md 并输出到 $OUTPUT_MD\""
