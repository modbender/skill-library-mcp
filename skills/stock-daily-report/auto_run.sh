#!/bin/bash
# A 股每日投资报告 Pro - 自动运行脚本
# 执行时间：每个交易日 9:25（集合竞价后，开盘前）

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="/tmp/stock-report-pro.log"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

echo "========================================" >> $LOG_FILE
echo "执行时间：$TIMESTAMP" >> $LOG_FILE
echo "========================================" >> $LOG_FILE

# 运行报告生成脚本
python3 "$SCRIPT_DIR/generate_report.py" >> $LOG_FILE 2>&1

if [ $? -eq 0 ]; then
    echo "✅ 报告生成成功" >> $LOG_FILE
else
    echo "❌ 报告生成失败" >> $LOG_FILE
fi

echo "" >> $LOG_FILE
