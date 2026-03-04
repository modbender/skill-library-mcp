#!/bin/bash
# A 股每日投资报告 Pro - 自动运行并推送到飞书
# 执行时间：每个交易日 9:25（集合竞价后，开盘前）

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="/tmp/stock-report-pro.log"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

echo "========================================" >> $LOG_FILE
echo "执行时间：$TIMESTAMP" >> $LOG_FILE
echo "========================================" >> $LOG_FILE

# 生成报告（HTML + 图片）
python3 "$SCRIPT_DIR/generate_report.py" --format both >> $LOG_FILE 2>&1

if [ $? -eq 0 ]; then
    echo "✅ 报告生成成功" >> $LOG_FILE
    
    # 获取最新的图片文件
    DATE_STR=$(date +%Y%m%d)
    IMAGE_FILE="$SCRIPT_DIR/../stock-report-${DATE_STR}.png"
    
    # 如果配置文件指定了 output_dir，使用配置的路径
    if [ -f "$SCRIPT_DIR/config.json" ]; then
        OUTPUT_DIR=$(python3 -c "import json; print(json.load(open('$SCRIPT_DIR/config.json')).get('output_dir', '/tmp'))" 2>/dev/null)
        IMAGE_FILE="${OUTPUT_DIR}/stock-report-${DATE_STR}.png"
    fi
    
    # 推送到飞书
    if [ -f "$IMAGE_FILE" ]; then
        echo "📤 推送到飞书：$IMAGE_FILE" >> $LOG_FILE
        
        # 使用 message 工具推送
        # 注意：这里需要调用 openclaw message 命令
        # 由于是 cron 环境，使用 openclaw CLI
        openclaw message send --channel feishu --media "$IMAGE_FILE" --message "📈 A 股每日投资报告 - $(date +%Y年%m月%d日)" >> $LOG_FILE 2>&1
        
        if [ $? -eq 0 ]; then
            echo "✅ 飞书推送成功" >> $LOG_FILE
        else
            echo "❌ 飞书推送失败" >> $LOG_FILE
        fi
    else
        echo "⚠️ 图片文件不存在：$IMAGE_FILE" >> $LOG_FILE
    fi
else
    echo "❌ 报告生成失败" >> $LOG_FILE
fi

echo "" >> $LOG_FILE
