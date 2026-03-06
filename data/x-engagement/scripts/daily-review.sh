#!/bin/bash

# x-engagement 每日复盘脚本
# 时间：每天晚上 22:00

TODAY=$(date +%Y-%m-%d)
DATA_FILE="data/engagement/${TODAY}.json"
PLAYBOOK="playbooks/comment-strategies.md"

echo "=== x-engagement 每日复盘 ==="
echo "日期: ${TODAY}"
echo ""

# 检查数据文件是否存在
if [ ! -f "$DATA_FILE" ]; then
    echo "⚠️ 今日无评论数据"
    exit 0
fi

# 读取今日数据
echo "📊 今日评论统计："
COMMENT_COUNT=$(jq 'length' "$DATA_FILE")
SUCCESS_COUNT=$(jq '[.[] | select(.result == "success")] | length' "$DATA_FILE")
ERROR_COUNT=$(jq '[.[] | select(.result == "error")] | length' "$DATA_FILE")

echo "- 总评论数: ${COMMENT_COUNT}"
echo "- 成功: ${SUCCESS_COUNT}"
echo "- 错误: ${ERROR_COUNT}"
echo ""

# 显示评论详情
echo "📝 评论详情："
jq -r '.[] | "- \(.time) @\(.author): \"\(.comment)\" [\(.result)]"' "$DATA_FILE"
echo ""

# 分析有效策略
echo "✅ 有效策略："
jq -r '.[] | select(.result == "success") | "- \"\(.comment)\" - \(.tweet_type) - \(.language)"' "$DATA_FILE"
echo ""

# 分析错误
if [ "$ERROR_COUNT" -gt 0 ]; then
    echo "❌ 错误分析："
    jq -r '.[] | select(.result == "error") | "- \"\(.comment)\" - \(.notes)"' "$DATA_FILE"
    echo ""
fi

# 生成建议
echo "💡 优化建议："
echo "- 查看 playbooks/comment-strategies.md 了解有效策略"
echo "- 查看 playbooks/changelog.md 了解最新变更"
echo "- 明天避免重复错误"

echo ""
echo "✓ 复盘完成"
