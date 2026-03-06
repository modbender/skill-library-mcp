#!/bin/bash
# Canvas 课程检查脚本
# 功能：检查公告、作业、文件
# 依赖：curl, python3, jq

set -e

# 配置
CANVAS_COOKIE_FILE="${HOME}/.canvas_cookie"
COURSE_IDS=()  # 用户需要自行配置课程 ID
OUTPUT_DIR="${HOME}/canvas_downloads"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查 Cookie 文件
if [ ! -f "$CANVAS_COOKIE_FILE" ]; then
    echo -e "${RED}错误：Cookie 文件不存在${NC}"
    echo "请创建 ${CANVAS_COOKIE_FILE}，包含："
    echo "  canvas_session=YOUR_SESSION"
    echo "  log_session_id=YOUR_LOG_SESSION"
    exit 1
fi

# 加载 Cookie
source "$CANVAS_COOKIE_FILE"
CANVAS_COOKIE="canvas_session=${canvas_session}; log_session_id=${log_session_id}"

# Canvas 域名（用户需要自行配置）
CANVAS_DOMAIN="your-institution.instructure.com"

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 检查课程
check_course() {
    local course_id=$1
    local course_name=$2
    
    echo -e "\n${BLUE}═══════════════════════════════════════${NC}"
    echo -e "${BLUE}📚 ${course_name} (ID: ${course_id})${NC}"
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
    
    # 检查公告（过去 14 天）
    echo -e "\n${YELLOW}📢 最近公告：${NC}"
    curl -sL -b "$CANVAS_COOKIE" \
        "https://${CANVAS_DOMAIN}/api/v1/announcements?context_codes[]=course_${course_id}&per_page=10" | \
        python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if not data:
        print('  无新公告')
    for a in data[:5]:
        title = a.get('title', 'N/A')
        date = a.get('created_at', '')[:10]
        print(f'  📌 [{date}] {title}')
except:
    print('  无法获取公告')
" 2>/dev/null
    
    # 检查作业（未来 14 天 + 过去 5 天）
    echo -e "\n${YELLOW}📋 作业：${NC}"
    curl -sL -b "$CANVAS_COOKIE" \
        "https://${CANVAS_DOMAIN}/api/v1/courses/${course_id}/assignments?per_page=50" | \
        python3 -c "
import sys, json
from datetime import datetime, timedelta
try:
    data = json.load(sys.stdin)
    now = datetime.now()
    upcoming = []
    for a in data:
        due = a.get('due_at')
        if due:
            due_date = datetime.fromisoformat(due.replace('Z', '+00:00'))
            due_local = due_date.astimezone().replace(tzinfo=None)
            if now - timedelta(days=5) <= due_date.replace(tzinfo=None) <= now + timedelta(days=14):
                upcoming.append((a.get('name', 'N/A'), due_local.strftime('%Y-%m-%d')))
    
    if not upcoming:
        print('  无近期作业')
    else:
        for name, due in sorted(upcoming, key=lambda x: x[1]):
            print(f'  📝 {name} - 截止：{due}')
except:
    print('  无法获取作业')
" 2>/dev/null
    
    # 检查文件
    echo -e "\n${YELLOW}📁 最近文件：${NC}"
    curl -sL -b "$CANVAS_COOKIE" \
        "https://${CANVAS_DOMAIN}/api/v1/courses/${course_id}/files?per_page=20" | \
        python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if not data:
        print('  无文件')
    for f in data[:5]:
        name = f.get('display_name', 'N/A')
        date = f.get('created_at', '')[:10]
        print(f'  📄 [{date}] {name}')
except:
    print('  无法获取文件')
" 2>/dev/null
}

# 主函数
main() {
    echo -e "${GREEN}╔═══════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║   Canvas 课程检查                      ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════╝${NC}"
    echo
    echo -e "时间：$(date '+%Y-%m-%d %H:%M:%S')"
    
    if [ ${#COURSE_IDS[@]} -eq 0 ]; then
        echo -e "${RED}错误：未配置课程 ID${NC}"
        echo "请在脚本中配置 COURSE_IDS 数组"
        exit 1
    fi
    
    # 遍历课程
    for course_id in "${COURSE_IDS[@]}"; do
        # 这里可以添加课程名称映射
        case $course_id in
            2679) check_course "$course_id" "DSAA2012 - Deep Learning" ;;
            2799) check_course "$course_id" "AIAA2711 - Mathematics for AI" ;;
            2888) check_course "$course_id" "AIAA3053 - Reinforcement Learning" ;;
            *) check_course "$course_id" "Course ${course_id}" ;;
        esac
    done
    
    echo -e "\n${GREEN}✅ 检查完成${NC}"
}

# 运行
main "$@"
