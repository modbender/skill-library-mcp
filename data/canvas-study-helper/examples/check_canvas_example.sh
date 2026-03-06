#!/bin/bash
# Canvas 检查示例脚本
# 复制此脚本并配置你的课程 ID

# 配置
export CANVAS_COOKIE_FILE="${HOME}/.canvas_cookie"

# 课程 ID 配置（替换为你的课程 ID）
declare -A COURSES=(
    ["1234"]="Course Name 1"
    ["5678"]="Course Name 2"
    ["9012"]="Course Name 3"
)

# Canvas 域名（替换为你的学校域名）
CANVAS_DOMAIN="your-institution.instructure.com"

# 加载 Cookie
if [ -f "$CANVAS_COOKIE_FILE" ]; then
    source "$CANVAS_COOKIE_FILE"
    export CANVAS_COOKIE="canvas_session=${canvas_session}; log_session_id=${log_session_id}"
else
    echo "错误：Cookie 文件不存在"
    echo "请创建 ${CANVAS_COOKIE_FILE}"
    exit 1
fi

echo "Canvas 课程检查"
echo "==============="

# 遍历课程
for course_id in "${!COURSES[@]}"; do
    course_name="${COURSES[$course_id]}"
    
    echo
    echo "📚 ${course_name}"
    echo "-----------------------------------"
    
    # 检查公告
    echo "📢 最近公告："
    curl -sL -b "$CANVAS_COOKIE" \
        "https://${CANVAS_DOMAIN}/api/v1/announcements?context_codes[]=course_${course_id}&per_page=5" | \
        python3 -c "
import sys, json
data = json.load(sys.stdin)
for a in data[:3]:
    title = a.get('title', 'N/A')
    date = a.get('created_at', '')[:10]
    print(f'  [{date}] {title}')
" 2>/dev/null
    
    # 检查作业
    echo "📋 近期作业："
    curl -sL -b "$CANVAS_COOKIE" \
        "https://${CANVAS_DOMAIN}/api/v1/courses/${course_id}/assignments?per_page=20" | \
        python3 -c "
import sys, json
data = json.load(sys.stdin)
for a in data[:5]:
    name = a.get('name', 'N/A')
    due = a.get('due_at', 'N/A')
    if due and due != 'N/A':
        due = due[:10]
    print(f'  {name} - 截止：{due}')
" 2>/dev/null
done

echo
echo "✅ 检查完成"
