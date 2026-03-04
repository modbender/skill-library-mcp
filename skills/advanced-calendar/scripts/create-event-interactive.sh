#!/bin/bash

# Interactive calendar event creator that asks for reminder preferences

echo "📅 创建新的日历事件"
echo "=================="

# Get event title
echo -n "请输入事件标题: "
read title

# Get event date
echo -n "请输入日期 (格式: YYYY-MM-DD, 例如: 2026-02-15): "
read date

# Get event time
echo -n "请输入时间 (格式: HH:MM, 例如: 14:30): "
read time

# Get event duration
echo -n "请输入持续时间 (分钟, 例如: 60, 默认: 60): "
read duration
if [ -z "$duration" ]; then
    duration=60
fi

# Get location
echo -n "请输入地点 (可选): "
read location

# Get description
echo -n "请输入描述 (可选): "
read description

# Ask about reminders
echo ""
echo "🔔 提醒设置"
echo "============"
echo "您希望提前多久收到提醒?"
echo "1) 5分钟"
echo "2) 15分钟" 
echo "3) 30分钟"
echo "4) 1小时"
echo "5) 3小时"
echo "6) 12小时"
echo "7) 1天"
echo "8) 3天"
echo "9) 自定义时间"
echo ""

echo -n "请选择 (1-9, 默认: 4): "
read choice

case $choice in
    1) reminder=5 ;;
    2) reminder=15 ;;
    3) reminder=30 ;;
    4) reminder=60 ;;
    5) reminder=180 ;;
    6) reminder=720 ;;
    7) reminder=1440 ;;
    8) reminder=4320 ;;
    9) 
        echo -n "请输入提前多少分钟提醒: "
        read reminder
        ;;
    *)
        reminder=60
        ;;
esac

# Build the command
cmd="/home/ubuntu/.openclaw/workspace/skills/calendar/scripts/calendar.sh create --title \"$title\" --date $date --time $time --duration $duration"

if [ -n "$location" ]; then
    cmd="$cmd --location \"$location\""
fi

if [ -n "$description" ]; then
    cmd="$cmd --description \"$description\""
fi

if [ -n "$reminder" ]; then
    cmd="$cmd --reminder $reminder"
fi

# Execute the command
echo ""
echo "正在创建事件..."
eval $cmd

echo ""
echo "✅ 事件创建成功！"