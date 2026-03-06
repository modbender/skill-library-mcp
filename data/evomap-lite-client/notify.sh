#!/bin/bash
# EvoMap 任务执行结果通知脚本
# 用法：notify.sh <状态> [任务 ID] [详细信息]

STATUS="$1"
TASK_ID="$2"
DETAILS="$3"

TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
LOG_FILE="/tmp/evomap-notify.log"

# 根据状态构建消息
case "$STATUS" in
    "NO_TASKS")
        TITLE="⏳ 暂无任务"
        CONTENT="EvoMap 定时检查完成，当前没有可用任务。"
        ;;
    "SUCCESS")
        TITLE="✅ 任务完成"
        CONTENT="任务 ID: ${TASK_ID}\n已成功处理并完成任务！"
        ;;
    "CLAIM_FAILED")
        TITLE="❌ 认领失败"
        CONTENT="任务 ID: ${TASK_ID}\n认领任务时出错。"
        ;;
    "PUBLISH_FAILED")
        TITLE="❌ 发布失败"
        CONTENT="任务 ID: ${TASK_ID}\n发布解决方案时出错。"
        ;;
    "COMPLETE_FAILED")
        TITLE="❌ 完成失败"
        CONTENT="任务 ID: ${TASK_ID}\n完成任务时出错。"
        ;;
    "ERROR")
        TITLE="⚠️ 执行错误"
        CONTENT="执行过程中发生错误：${DETAILS}"
        ;;
    *)
        TITLE="📋 执行完成"
        CONTENT="状态：${STATUS}"
        ;;
esac

FULL_MESSAGE="${TITLE}\n\n${CONTENT}\n\n执行时间：${TIMESTAMP}"

# 写入通知日志
echo "[$TIMESTAMP] 通知：$STATUS - $TASK_ID" >> $LOG_FILE

# 使用 Node.js 脚本发送飞书消息
cd /root/.openclaw/workspace/skills/evomap-lite-client
node send-notify.js "$STATUS" "$TASK_ID" "$TITLE" "$CONTENT" "$TIMESTAMP"

echo "通知已发送：$STATUS"
