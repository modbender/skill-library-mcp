#!/bin/bash
# log-viewer.sh - 查看远程服务器日志

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../common.sh"

show_help() {
    print_help_header "log-viewer.sh" "查看远程服务器日志"
    cat <<EOF
  --instance-id <id>      实例 ID（自动获取密码和 IP）
  --host <ip>             IP 地址
  --user <user>           用户名，默认 root
  --password <pwd>        密码
  --file <path>           日志文件路径，默认 /var/log/syslog
  --lines <n>             显示行数，默认 100
  --follow                实时跟踪
  --filter <pattern>      过滤关键字
  -h, --help              显示帮助

示例:
  $0 --instance-id ins-xxx --file /var/log/nginx/access.log
  $0 --instance-id ins-xxx --file /var/log/syslog --filter error --lines 50

EOF
}

check_ssh_prerequisites

INSTANCE_ID="" HOST="" USER="root" PORT=22 PASSWORD=""
LOG_FILE="/var/log/syslog" LINES=100 FOLLOW=false FILTER=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --instance-id) INSTANCE_ID="$2"; shift 2 ;;
        --host)        HOST="$2"; shift 2 ;;
        --user)        USER="$2"; shift 2 ;;
        --password)    PASSWORD="$2"; shift 2 ;;
        --file)        LOG_FILE="$2"; shift 2 ;;
        --lines)       LINES="$2"; shift 2 ;;
        --follow)      FOLLOW=true; shift ;;
        --filter)      FILTER="$2"; shift 2 ;;
        -h|--help)     show_help; exit 0 ;;
        *)             error "未知参数: $1"; exit 1 ;;
    esac
done

resolve_ops_connection "$INSTANCE_ID" "$HOST" "$PASSWORD" || exit 1
HOST="$OPS_HOST"
PASSWORD="$OPS_PASSWORD"

# 构建命令
if [[ "$FOLLOW" == "true" ]]; then
    CMD="tail -f $LOG_FILE"
    [[ -n "$FILTER" ]] && CMD="$CMD | grep --line-buffered -i '$FILTER'"
    info "实时跟踪 $HOST:$LOG_FILE (Ctrl+C 退出)..."
else
    CMD="tail -n $LINES $LOG_FILE"
    [[ -n "$FILTER" ]] && CMD="$CMD | grep -i '$FILTER'"
    info "查看 $HOST:$LOG_FILE (最后 $LINES 行)..."
fi

echo ""
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p "$PORT" "$USER@$HOST" "$CMD"
