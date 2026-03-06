#!/bin/bash
###############################################################################
# AI内容每日自动化收集与推送脚本
# 用法: ./daily-ai-pipeline.sh [日期，默认今天]
###############################################################################

set -e

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIPELINE_DIR="$(dirname "$SCRIPT_DIR")"
DATE="${1:-$(date +%Y-%m-%d)}"
OUTPUT_DIR="$PIPELINE_DIR/collected/$DATE"
FILTERED_DIR="$PIPELINE_DIR/filtered/$DATE"
REPORT_FILE="$FILTERED_DIR/TOP10-daily-report.md"

# 飞书配置（从环境变量读取）
FEISHU_USER="${FEISHU_USER:-REPLACE_ME}"

echo "========== AI内容每日收集与推送 =========="
echo "日期: $DATE"
echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 创建目录
mkdir -p "$OUTPUT_DIR" "$FILTERED_DIR"

###############################################################################
# 步骤1: 数据收集
###############################################################################
echo "📡 步骤1: 收集数据..."

# 1.1 收集HN和TechCrunch
echo "   - 收集 Hacker News + TechCrunch..."
cd "$PIPELINE_DIR"
"$SCRIPT_DIR/collect-v4.sh" "$DATE" > "$OUTPUT_DIR/collection.log" 2>&1 || true

# 1.2 生成Twitter收集任务
echo "   - 生成Twitter收集任务..."
cat > "$OUTPUT_DIR/twitter-tasks.sh" << 'EOF'
#!/bin/bash
# Twitter P0账号收集命令

echo "🐦 Twitter收集指南"
echo ""
echo "请执行以下命令收集Twitter内容:"
echo ""
echo "# P0核心账号"
echo "browser open \"https://x.com/sama\""
echo "wait 3000"
echo "browser snapshot"
echo ""
echo "browser open \"https://x.com/karpathy\""
echo "wait 3000"
echo "browser snapshot"
echo ""
echo "browser open \"https://x.com/ylecun\""
echo "wait 3000"
echo "browser snapshot"
echo ""
echo "browser open \"https://x.com/OpenAI\""
echo "wait 3000"
echo "browser snapshot"
echo ""
echo "browser open \"https://x.com/DrJimFan\""
echo "wait 3000"
echo "browser snapshot"
echo ""
echo "browser open \"https://x.com/gdb\""
echo "wait 3000"
echo "browser snapshot"
echo ""
echo "# 搜索热门话题"
echo "browser open \"https://x.com/search?q=AI+GPT+Claude&f=live\""
echo "wait 5000"
echo "browser snapshot"
EOF

chmod +x "$OUTPUT_DIR/twitter-tasks.sh"

echo "   ✅ 数据收集完成"
echo ""

###############################################################################
# 步骤2: 生成AI分析任务文件
###############################################################################
echo "🤖 步骤2: 准备AI分析..."

# 读取收集到的数据
RAW_JSON="$OUTPUT_DIR/raw-content.json"
RAW_MD="$OUTPUT_DIR/raw-content.md"

# 统计数量
if [[ -f "$RAW_JSON" ]]; then
    TOTAL_COUNT=$(jq '[.sources[].items | length] | add // 0' "$RAW_JSON")
    echo "   - 共收集 $TOTAL_COUNT 条内容"
else
    TOTAL_COUNT=0
    echo "   - 暂无数据"
fi

# 生成AI分析任务
cat > "$FILTERED_DIR/ai-analysis-task.md" << EOF
# AI内容分析任务 - $DATE

## 待分析内容

数据来源:
- Hacker News: API获取
- TechCrunch: RSS获取
- Twitter: 手动/browser收集

原始数据:
- JSON: $RAW_JSON
- Markdown: $RAW_MD

## 分析要求

### 评分维度（每项1-10分）
1. 时效性: 是否最新，是否在热度期内
2. 话题性: 是否热门，社交传播潜力
3. 专业性: 信息深度，是否经得起解读
4. 公众号适合度: 是否适合写成公众号文章
5. 中文受众相关性: 对中国读者是否有价值

### 综合评分计算
综合评分 = (时效性 + 话题性 + 专业性 + 公众号适合度 + 中文受众相关性) / 5

### 推荐标准
- 强烈推荐: 8.0+
- 推荐: 7.0-8.0
- 可考虑: 6.0-7.0
- 不推荐: <6.0

### 输出格式要求

为每个推荐选题输出:

\`\`\`
## 选题 [序号]: [标题]

| 字段 | 内容 |
|------|------|
| **建议选题** | 《具体文章标题》 |
| **写作角度** | ① 角度一: xxx ② 角度二: xxx ③ 角度三: xxx |
| **类型** | 热点分析/工具测评/技术教程/行业观察/投资分析 |
| **时效性** | ⭐⭐⭐⭐⭐/⭐⭐⭐⭐/⭐⭐⭐ |
| **受众** | 具体受众群体 |
| **推荐理由** | 详细推荐理由，包含热度和价值分析 |
| **参考链接** | https://... |

\`\`\`

## 执行命令

请在OpenClaw中执行:

\`\`\`
请分析 $RAW_MD 和 $RAW_JSON 中的内容。

按照上述评分标准，筛选出TOP 10推荐选题。
要求:
1. 只输出评分≥6.5分的选题
2. 按综合评分从高到低排序
3. 每个选题必须包含所有7个字段
4. 写作角度提供3个不同方向
5. 生成格式化的Markdown报告

保存结果到: $REPORT_FILE
\`\`\`
EOF

echo "   ✅ AI分析任务文件已生成: $FILTERED_DIR/ai-analysis-task.md"
echo ""

###############################################################################
# 步骤3: 生成飞书推送模板
###############################################################################
echo "📱 步骤3: 准备飞书推送模板..."

cat > "$FILTERED_DIR/feishu-message-template.md" << EOF
📋 今日AI选题推荐 - $DATE

> ⏰ 收集时间: $(date '+%H:%M')
> 📊 数据来源: HN + TechCrunch + Twitter
> 🤖 AI筛选: TOP 10推荐

---

（AI分析完成后，此处将填入TOP 10选题内容）

---

💡 下一步:
1. 查看详细报告: $REPORT_FILE
2. 选择今日选题开始写作
3. 访问参考链接获取更多信息

*自动化收集系统*
EOF

echo "   ✅ 飞书模板已生成"
echo ""

###############################################################################
# 步骤4: 生成完整报告框架
###############################################################################
echo "📝 步骤4: 生成报告框架..."

cat > "$REPORT_FILE" << EOF
# 📋 今日AI选题推荐 - $DATE

> ⏰ 收集时间: $(date '+%Y-%m-%d %H:%M:%S')  
> 📊 数据来源: Hacker News + TechCrunch + Twitter  
> 🤖 AI智能筛选: TOP 10推荐

---

## 数据汇总

- 收集内容: $TOTAL_COUNT 条
- 筛选结果: TOP 10推荐
- 更新频率: 每日8:00

---

## 🏆 TOP 10 推荐选题

（AI分析后将填入具体内容）

---

*报告生成时间: $(date '+%Y-%m-%d %H:%M:%S')*  
*系统: AI内容收集流水线*
EOF

echo "   ✅ 报告框架已生成: $REPORT_FILE"
echo ""

###############################################################################
# 完成
###############################################################################
echo "========== 准备阶段完成 =========="
echo ""
echo "📁 输出文件:"
echo "   - 原始数据: $OUTPUT_DIR/"
echo "   - 分析任务: $FILTERED_DIR/ai-analysis-task.md"
echo "   - 报告模板: $REPORT_FILE"
echo ""
echo "🚀 下一步:"
echo "   1. 执行Twitter收集任务 (如需)"
echo "      bash $OUTPUT_DIR/twitter-tasks.sh"
echo ""
echo "   2. 运行AI分析生成TOP 10"
echo "      (在OpenClaw中执行分析任务)"
echo ""
echo "   3. 发送飞书消息"
echo "      (分析完成后自动发送)"
echo ""
