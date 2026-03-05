#!/bin/bash
# AI新闻日报 Skill 安装脚本

echo "Installing ai-news-daily skill..."

# 检查Python版本
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then 
    echo "Error: Python 3.8+ required, found $python_version"
    exit 1
fi

# 安装依赖
echo "Installing dependencies..."
pip3 install -r requirements.txt -q

echo "ai-news-daily skill installed successfully!"
echo ""
echo "Usage:"
echo "  openclaw skills run ai-news-daily    # 获取今日AI新闻"
echo "  openclaw skills cron ai-news-daily   # 设置定时任务"
