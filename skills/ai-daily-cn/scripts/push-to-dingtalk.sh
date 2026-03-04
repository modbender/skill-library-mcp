#!/bin/bash
# AI 日报推送脚本 - 推送到钉钉群

TODAY=$(date +%Y-%m-%d)
REPORT_FILE="/home/admin/.openclaw/workspace/skills/ai-daily/output/AI-Daily-${TODAY}.md"

if [ ! -f "$REPORT_FILE" ]; then
    echo "❌ 未找到今日日报文件：$REPORT_FILE"
    exit 1
fi

echo "📰 准备推送 ${TODAY} AI 日报到钉钉群..."

# 读取日报内容（前 60 行作为摘要）
SUMMARY=$(head -60 "$REPORT_FILE")

# 构建消息内容
MESSAGE="📰 **AI 大模型日报 | ${TODAY}**

${SUMMARY}

---
*完整报告：/home/admin/.openclaw/workspace/skills/ai-daily/output/AI-Daily-${TODAY}.md*"

# 使用 OpenClaw sessions_send 发送到当前 dingtalk 会话
openclaw sessions send --session "agent:main:dingtalk:group:cid+sxosobsr081ckhs0jpsqw==" --message "$MESSAGE"

if [ $? -eq 0 ]; then
    echo "✅ AI 日报已推送到钉钉群"
else
    echo "⚠️ 推送失败，请检查 Gateway 状态"
fi
