#!/bin/bash
# LifeLog Enhanced Recorder v3.0
# 支持内容类型识别 + 生活/任务分离

NOTION_KEY="ntn_u6470328110RTrO6nvdJt5D3YBVYRTkbukysWQUHBGd7JD"
DATABASE_ID="30b181a95f2e80639966c2b9d93b69cb"
API_VERSION="2022-06-28"
SPEC_FILE="/root/.openclaw/workspace/docs/lifelog-spec.md"

# 读取规范文件
load_spec() {
    if [ -f "$SPEC_FILE" ]; then
        echo "✅ 已加载规范: $SPEC_FILE"
    else
        echo "⚠️ 规范文件不存在: $SPEC_FILE"
    fi
}

# 获取今天的日期（带时间戳）
get_timestamp() {
    date "+📅 %Y-%m-%d %H:%M"
}

# 内容类型识别
detect_content_type() {
    local content="$1"
    
    # 任务指令关键词
    local task_keywords="设置|提醒|安装|创建|删除|修改|更新|帮我|请|todo|待办|提醒我"
    
    # 个人生活关键词
    local life_keywords="今天|昨天|明天|起床|睡觉|吃饭|工作|学习|论文|运动|情绪|心情|感受|生活|做了|干了"
    
    # 检查是否包含任务指令
    if echo "$content" | grep -qE "$task_keywords"; then
        if echo "$content" | grep -qE "提醒我|设置.*提醒"; then
            echo "TASK"
        else
            echo "MIXED"
        fi
    elif echo "$content" | grep -qE "$life_keywords"; then
        echo "LIFE"
    else
        local has_time_info=$(echo "$content" | grep -cE "[0-9]+点|[0-9]+:[0-9]|上午|下午|晚上")
        local has_emotion=$(echo "$content" | grep -cE "开心|疲惫|焦虑|充实|愧疚|心情|感受")
        
        if [ "$has_time_info" -gt 0 ] || [ "$has_emotion" -gt 0 ]; then
            echo "LIFE"
        else
            echo "OTHER"
        fi
    fi
}

# 分析生活内容
analyze_life() {
    local content="$1"
    local emotions=""
    local event_type=""
    local location="未知"
    
    # 情绪分析
    if echo "$content" | grep -qE "开心|高兴|愉快|兴奋|满足|充实|不错|挺好|顺利"; then
        emotions="${emotions}开心,"
    fi
    if echo "$content" | grep -qE "疲惫|累|困|疲劳|无力|困倦"; then
        emotions="${emotions}疲惫,"
    fi
    if echo "$content" | grep -qE "焦虑|担心|紧张|压力|烦躁"; then
        emotions="${emotions}焦虑,"
    fi
    if echo "$content" | grep -qE "愧疚|后悔|遗憾|抱歉"; then
        emotions="${emotions}愧疚,"
    fi
    emotions="${emotions%,}"
    [ -z "$emotions" ] && emotions="一般"
    
    # 事件分类
    if echo "$content" | grep -qE "论文|学习|读书|上课|考试"; then
        event_type="学习"
    elif echo "$content" | grep -qE "工作|项目|代码|开发|会议|服务器|编程"; then
        event_type="工作"
    elif echo "$content" | grep -qE "运动|跑步|健身|游泳|骑车"; then
        event_type="运动"
    elif echo "$content" | grep -qE "睡觉|休息|睡眠|午睡"; then
        event_type="休息"
    elif echo "$content" | grep -qE "吃饭|餐饮|美食|外卖|做饭"; then
        event_type="餐饮"
    elif echo "$content" | grep -qE "娱乐|游戏|电影|电视剧|视频"; then
        event_type="娱乐"
    elif echo "$content" | grep -qE "购物|买|消费|花钱"; then
        event_type="消费"
    else
        event_type="日常"
    fi
    
    # 地点
    if echo "$content" | grep -qE "家里|在家|卧室|床|客厅"; then
        location="家里"
    elif echo "$content" | grep -qE "公司|办公室"; then
        location="公司"
    elif echo "$content" | grep -qE "学校|图书馆|实验室|教室"; then
        location="学校"
    elif echo "$content" | grep -qE "咖啡厅|星巴克|奶茶店"; then
        location="咖啡厅"
    fi
    
    echo "{\"emotions\":\"$emotions\",\"event_type\":\"$event_type\",\"location\":\"$location\"}"
}

# 创建日记条目
create_entry() {
    local content="$1"
    
    # 加载规范
    load_spec
    
    # 检测内容类型
    local content_type=$(detect_content_type "$content")
    
    case "$content_type" in
        "LIFE")
            echo "✅ 识别为：个人生活内容"
            ;;
        "TASK")
            echo "🎯 识别为：任务指令"
            echo "💡 提示：任务指令会直接执行，不会记录到日记"
            return
            ;;
        "MIXED")
            echo "⚠️ 识别为：混合内容"
            echo "📝 将提取生活部分记录到日记"
            ;;
        *)
            echo "❓ 内容类型不确定，先记录再说"
            ;;
    esac
    
    # 获取今天日期 (支持参数指定，或自动检测内容中的昨天/今天)
    local today
    if [ -n "$2" ]; then
        today="$2"
    else
        today=$(detect_date "$content")
    fi
    local timestamp=$(get_timestamp)
    
    # 格式化内容
    local formatted="$timestamp"$'\n'"$content"
    
    # 分析
    local analysis=$(analyze_life "$content")
    local emotions=$(echo "$analysis" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['emotions'])")
    local event_type=$(echo "$analysis" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['event_type'])")
    local location=$(echo "$analysis" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['location'])")
    
    # 转换情绪
    local emotion_json=""
    IFS=',' read -ra EMOTIONS <<< "$emotions"
    for emo in "${EMOTIONS[@]}"; do
        [ -n "$emo" ] && emotion_json="${emotion_json}{\"name\": \"$emo\"},"
    done
    emotion_json="${emotion_json%,}"
    
    echo ""
    echo "📊 分析结果："
    echo "   情绪: $emotions"
    echo "   事件: $event_type"
    echo "   地点: $location"
    echo ""
    
    # 保存到Notion - 使用 rich_text 类型
    local response=$(curl -s -X POST "https://api.notion.com/v1/pages" \
        -H "Authorization: Bearer $NOTION_KEY" \
        -H "Notion-Version: $API_VERSION" \
        -H "Content-Type: application/json" \
        -d "{
            \"parent\": {\"database_id\": \"$DATABASE_ID\"},
            \"properties\": {
                \"日期\": {\"title\": [{\"text\": {\"content\": \"$today\"}}]},
                \"原文\": {\"rich_text\": [{\"text\": {\"content\": \"$(echo "$formatted" | head -1000 | tr '\n' ' ' | sed 's/\"/\\\"/g')\"}}]},
                \"情绪状态\": {\"rich_text\": [{\"text\": {\"content\": \"$emotions\"}}]},
                \"主要事件\": {\"rich_text\": [{\"text\": {\"content\": \"$event_type\"}}]},
                \"位置\": {\"rich_text\": [{\"text\": {\"content\": \"$location\"}}]}
            }
        }")
    
    if echo "$response" | grep -q "object.*page"; then
        local url=$(echo "$response" | python3 -c "import sys,json; print(json.load(sys.stdin).get('url', 'Unknown'))")
        echo "✅ 已保存到 LifeLog"
        echo "🔗 $url"
    else
        echo "❌ 保存失败: $response"
    fi
}

export -f create_entry load_spec detect_content_type analyze_life

# 自动检测内容中的日期 (增强版，支持多种格式)
detect_date() {
    local content="$1"
    local today=$(date "+%Y-%m-%d")
    local yesterday=$(date -d "yesterday" "+%Y-%m-%d")
    local day_before=$(date -d "yesterday -1 day" "+%Y-%m-%d")
    
    # 检测具体日期格式：3月3日、03月03日、3.3、03.3
    if echo "$content" | grep -qE "[0-9]{1,2}月[0-9]{1,2}日"; then
        local month=$(echo "$content" | grep -oE "[0-9]{1,2}月[0-9]{1,2}日" | head -1 | sed 's/月.*//')
        local day=$(echo "$content" | grep -oE "[0-9]{1,2}月[0-9]{1,2}日" | head -1 | sed 's/.*月//' | sed 's/日//')
        printf "2026-%02d-%02d" "$month" "$day"
    # 检测大前天/前天
    elif echo "$content" | grep -qE "大前天"; then
        date -d "yesterday -2 day" "+%Y-%m-%d"
    elif echo "$content" | grep -qE "前天|前一天"; then
        echo "$day_before"
    # 检测昨天
    elif echo "$content" | grep -qE "昨天|昨日"; then
        echo "$yesterday"
    # 检测大后天/后天
    elif echo "$content" | grep -qE "大后天"; then
        date -d "tomorrow +2 day" "+%Y-%m-%d"
    elif echo "$content" | grep -qE "后天"; then
        date -d "tomorrow +1 day" "+%Y-%m-%d"
    # 检测明天
    elif echo "$content" | grep -qE "明天|明日"; then
        date -d "tomorrow" "+%Y-%m-%d"
    # 检测今天
    elif echo "$content" | grep -qE "今天|今日|刚才|刚刚|现在"; then
        echo "$today"
    else
        # 默认返回昨天（用户回忆往事时通常是说昨天）
        echo "$yesterday"
    fi
}

# 从文件读取内容 (支持长内容)
read_content_from_file() {
    local file="$1"
    if [ -f "$file" ]; then
        cat "$file"
    else
        echo ""
    fi
}

# 执行记录
# 支持三种方式：
# 1. lifelog-recorder.sh "内容" - 直接传内容
# 2. lifelog-recorder.sh -f file.txt - 从文件读取
# 3. lifelog-recorder.sh - - 从stdin读取
if [ "$1" = "-f" ] && [ -n "$2" ]; then
    content=$(cat "$2")
    create_entry "$content" ""
elif [ "$1" = "-" ]; then
    content=$(cat)
    create_entry "$content" ""
else
    create_entry "$1" ""
fi
