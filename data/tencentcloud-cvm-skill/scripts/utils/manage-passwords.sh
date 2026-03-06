#!/bin/bash
# manage-passwords.sh - 管理实例密码存储

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../common.sh"

show_help() {
    print_help_header "manage-passwords.sh" "管理实例密码存储"
    cat <<EOF
操作:
  --list                  列出所有实例
  --show <id>             显示实例详情
  --add <id>              添加实例密码
  --delete <id>           删除实例记录
  --update-ip <id>        更新实例 IP

添加/更新参数:
  --password <pwd>        密码
  --host <ip>             IP 地址
  --region <region>       地域

示例:
  $0 --list
  $0 --show ins-xxx
  $0 --add ins-xxx --password 'xxx' --host 1.2.3.4
  $0 --delete ins-xxx

EOF
}

check_jq_installed

ACTION="" INSTANCE_ID="" PASSWORD="" HOST="" REGION=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --list)      ACTION="list"; shift ;;
        --show)      ACTION="show"; INSTANCE_ID="$2"; shift 2 ;;
        --add)       ACTION="add"; INSTANCE_ID="$2"; shift 2 ;;
        --delete)    ACTION="delete"; INSTANCE_ID="$2"; shift 2 ;;
        --update-ip) ACTION="update"; INSTANCE_ID="$2"; shift 2 ;;
        --password)  PASSWORD="$2"; shift 2 ;;
        --host)      HOST="$2"; shift 2 ;;
        --region)    REGION="$2"; shift 2 ;;
        -h|--help)   show_help; exit 0 ;;
        *)           error "未知参数: $1"; exit 1 ;;
    esac
done

[[ -z "$ACTION" ]] && { error "请指定操作"; show_help; exit 1; }

case "$ACTION" in
    list)
        list_saved_instances
        ;;
    show)
        [[ -z "$INSTANCE_ID" ]] && { error "缺少实例 ID"; exit 1; }
        info=$(get_instance_info "$INSTANCE_ID") || exit 1
        print_section "实例 $INSTANCE_ID"
        echo "$info" | jq -r '"  密码: \(.password)\n  IP: \(.host // "未设置")\n  地域: \(.region // "未设置")\n  创建: \(.created_at // "未知")"'
        echo "=================================="
        ;;
    add)
        [[ -z "$INSTANCE_ID" ]] && { error "缺少实例 ID"; exit 1; }
        [[ -z "$PASSWORD" ]] && { error "缺少 --password"; exit 1; }
        save_instance_password "$INSTANCE_ID" "$PASSWORD" "$HOST" "$REGION"
        ;;
    update)
        [[ -z "$INSTANCE_ID" ]] && { error "缺少实例 ID"; exit 1; }
        [[ -z "$HOST" ]] && { error "缺少 --host"; exit 1; }
        update_instance_host "$INSTANCE_ID" "$HOST"
        ;;
    delete)
        [[ -z "$INSTANCE_ID" ]] && { error "缺少实例 ID"; exit 1; }
        confirm "确认删除 $INSTANCE_ID?" && delete_instance_password "$INSTANCE_ID"
        ;;
esac
