#!/bin/bash
# doubao_skill.sh - OpenClaw Skill 包装器
# 将 shell 脚本包装成 OpenClaw 兼容的 skill

set -euo pipefail

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="${SCRIPT_DIR}/../data"

# 确保 data 目录存在
mkdir -p "${DATA_DIR}"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查环境变量
if [ -z "${ARK_API_KEY:-}" ]; then
    echo -e "${RED}错误${NC}: ARK_API_KEY 环境变量未设置"
    echo "请执行: export ARK_API_KEY=\"your_api_key\""
    exit 1
fi

# 主函数：执行 skill
execute_skill() {
    local action="$1"
    shift
    
    case "$action" in
        img)
            local prompt="$1"
            if [ -z "$prompt" ]; then
                echo "{\"status\":\"error\",\"error\":\"Missing prompt parameter\"}"
                exit 1
            fi
            "${SCRIPT_DIR}/doubao.sh" img "$prompt"
            ;;
        
        edit)
            local image_url="$1"
            local prompt="${2:-remove watermark, keep main content}"
            if [ -z "$image_url" ]; then
                echo "{\"status\":\"error\",\"error\":\"Missing image_url parameter\"}"
                exit 1
            fi
            "${SCRIPT_DIR}/doubao.sh" edit "$image_url" "$prompt"
            ;;
        
        vid)
            local prompt="$1"
            local sync_mode="${2:-async}"
            if [ -z "$prompt" ]; then
                echo "{\"status\":\"error\",\"error\":\"Missing prompt parameter\"}"
                exit 1
            fi
            "${SCRIPT_DIR}/doubao.sh" vid "$prompt" "$sync_mode"
            ;;
        
        status)
            local task_id="$1"
            if [ -z "$task_id" ]; then
                echo "{\"status\":\"error\",\"error\":\"Missing task_id parameter\"}"
                exit 1
            fi
            "${SCRIPT_DIR}/doubao.sh" status "$task_id"
            ;;
        
        *)
            echo "{\"status\":\"error\",\"error\":\"Unknown action: $action. Supported: img, edit, vid, status\"}"
            exit 1
            ;;
    esac
}

# 辅助函数：显示帮助
show_help() {
    cat <<'HELP'
用法: ./doubao_skill.sh <action> [options...]

Actions:
  img <prompt>                        文生图
  edit <image_url> [prompt]           图片编辑（去除水印）
  vid <prompt> [sync|async]          文生视频（默认: async）
  status <task_id>                     查询任务状态
  help                                显示此帮助信息

Examples:
  ./doubao_skill.sh img "一只可爱的小猫"
  ./doubao_skill.sh edit "https://..." "remove watermark"
  ./doubao_skill.sh vid "一个人在跳舞" sync
  ./doubao_skill.sh status "task_xxxxx"

Environment Variables:
  ARK_API_KEY                          (必需) Volcengine ARK API 密钥

HELP
}

# 主函数
main() {
    # 显示帮助
    if [ $# -lt 1 ]; then
        show_help
        exit 1
    fi
    
    local action="$1"
    
    if [ "$action" = "help" ] || [ "$action" = "--help" ] || [ "$action" = "-h" ]; then
        show_help
        exit 0
    fi
    
    # 执行 skill
    execute_skill "$@"
}

# 执行主函数
main "$@"
