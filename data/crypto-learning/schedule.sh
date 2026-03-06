#!/bin/bash
# 加密货币学习计划 - 每日推送脚本
# 通过 OpenClaw cron 每天早上9点执行

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 获取今日学习内容
CONTENT=$(python3 crypto_learning.py next)

# 发送到 Telegram（使用 OpenClaw message 工具）
# 注意：这里需要根据实际配置调整 channel 和 target
# 假设通过 OpenClaw 的 message 工具发送

# 方式1：如果通过 cron 的 agentTurn 发送系统事件
echo "$CONTENT" > /tmp/crypto-learning-today.txt

# 方式2：直接调用 openclaw 命令发送（如果支持）
# openclaw message send --channel telegram --to 8550833012 --message "$CONTENT"

# 输出内容（用于调试）
echo "$CONTENT"
