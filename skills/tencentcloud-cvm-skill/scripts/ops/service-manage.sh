#!/bin/bash
# service-manage.sh - 远程服务管理

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../common.sh"

show_help() {
    print_help_header "service-manage.sh" "远程服务管理（systemctl）"
    cat <<EOF
  --instance-id <id>      实例 ID（自动获取密码和 IP）
  --host <ip>             IP 地址
  --user <user>           用户名，默认 root
  --password <pwd>        密码
  --service <name>        服务名（必需）
  --action <act>          操作: status|start|stop|restart|enable|disable
  -h, --help              显示帮助

示例:
  $0 --instance-id ins-xxx --service nginx --action status
  $0 --instance-id ins-xxx --service nginx --action restart

EOF
}

check_ssh_prerequisites

INSTANCE_ID="" HOST="" USER="root" PORT=22 PASSWORD="" SERVICE="" ACTION="status"

while [[ $# -gt 0 ]]; do
    case $1 in
        --instance-id) INSTANCE_ID="$2"; shift 2 ;;
        --host)        HOST="$2"; shift 2 ;;
        --user)        USER="$2"; shift 2 ;;
        --password)    PASSWORD="$2"; shift 2 ;;
        --service)     SERVICE="$2"; shift 2 ;;
        --action)      ACTION="$2"; shift 2 ;;
        -h|--help)     show_help; exit 0 ;;
        *)             error "未知参数: $1"; exit 1 ;;
    esac
done

[[ -z "$SERVICE" ]] && { error "缺少必需参数: --service"; exit 1; }
[[ ! "$ACTION" =~ ^(status|start|stop|restart|enable|disable)$ ]] && { error "无效操作: $ACTION"; exit 1; }

resolve_ops_connection "$INSTANCE_ID" "$HOST" "$PASSWORD" || exit 1
HOST="$OPS_HOST"
PASSWORD="$OPS_PASSWORD"

info "在 $HOST 执行: systemctl $ACTION $SERVICE"

sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p "$PORT" "$USER@$HOST" "systemctl $ACTION $SERVICE"

success "服务操作完成"
