#!/bin/bash
# EvoMap 资产包自动发布脚本 - 每 2 小时执行一次
# 日志文件：/tmp/evomap-publish.log

LOG_FILE="/tmp/evomap-publish.log"
SKILL_DIR="$HOME/.openclaw/workspace/skills/evomap-lite-client"
NODE_ID="node_5dc63a58060a291a"
NODE_PATH="/root/.nvm/versions/node/v22.22.0/bin/node"

echo "========================================" >> $LOG_FILE
echo "执行时间：$(date)" >> $LOG_FILE
echo "========================================" >> $LOG_FILE

cd $SKILL_DIR

# 执行发布，最多尝试 20 次
export A2A_NODE_ID=$NODE_ID
export PATH="$NODE_PATH:$PATH"
result=$(for i in $(seq 1 20); do
    echo "尝试 $i/20..." >> $LOG_FILE
    output=$($NODE_PATH publish-asset-v2.js 2>&1)
    echo "$output" >> $LOG_FILE
    
    if echo "$output" | grep -q "发布成功\|published\|status.*published"; then
        echo "✅ 发布成功！" >> $LOG_FILE
        echo "SUCCESS: 发布成功"
        exit 0
    fi
    
    # 等待 3-6 秒后重试
    sleep $((3 + RANDOM % 4))
done

echo "❌ 所有尝试均失败" >> $LOG_FILE
echo "FAILED: 发布失败")

# 记录结果
echo "最终结果：$result" >> $LOG_FILE
echo "" >> $LOG_FILE
