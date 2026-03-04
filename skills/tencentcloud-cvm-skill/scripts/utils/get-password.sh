#!/bin/bash
# get-password.sh - 获取实例密码

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../common.sh"

show_help() {
    print_help_header "get-password.sh" "获取已保存的实例密码"
    cat <<EOF
  --instance-id <id>      实例 ID（必需）
  --show-all              显示完整信息
  -h, --help              显示帮助

示例:
  $0 --instance-id ins-xxx
  $0 --instance-id ins-xxx --show-all

EOF
}

check_jq_installed

INSTANCE_ID="" SHOW_ALL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --instance-id) INSTANCE_ID="$2"; shift 2 ;;
        --show-all)    SHOW_ALL=true; shift ;;
        -h|--help)     show_help; exit 0 ;;
        *)             error "未知参数: $1"; exit 1 ;;
    esac
done

[[ -z "$INSTANCE_ID" ]] && { error "缺少: --instance-id"; exit 1; }

if [[ "$SHOW_ALL" == "true" ]]; then
    info=$(get_instance_info "$INSTANCE_ID") || exit 1
    print_section "实例 $INSTANCE_ID"
    echo "$info" | jq -r '"  密码: \(.password)\n  IP: \(.host // "未设置")\n  地域: \(.region // "未设置")"'
    echo "=================================="
else
    password=$(get_instance_password "$INSTANCE_ID") || exit 1
    echo "$password"
fi
