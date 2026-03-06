#!/bin/bash
# process-monitor.sh - 查看远程服务器进程信息

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../common.sh"

show_help() {
    print_help_header "process-monitor.sh" "查看远程服务器进程信息"
    cat <<EOF
  --instance-id <id>      实例 ID（自动获取密码和 IP）
  --host <ip>             IP 地址
  --user <user>           用户名，默认 root
  --password <pwd>        密码
  --top <n>               显示 TOP N 进程，默认 10
  --filter <name>         过滤进程名
  -h, --help              显示帮助

示例:
  $0 --instance-id ins-xxx
  $0 --instance-id ins-xxx --top 20 --filter nginx

EOF
}

check_ssh_prerequisites

INSTANCE_ID="" HOST="" USER="root" PORT=22 PASSWORD="" TOP_N=10 FILTER=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --instance-id) INSTANCE_ID="$2"; shift 2 ;;
        --host)        HOST="$2"; shift 2 ;;
        --user)        USER="$2"; shift 2 ;;
        --password)    PASSWORD="$2"; shift 2 ;;
        --top)         TOP_N="$2"; shift 2 ;;
        --filter)      FILTER="$2"; shift 2 ;;
        -h|--help)     show_help; exit 0 ;;
        *)             error "未知参数: $1"; exit 1 ;;
    esac
done

resolve_ops_connection "$INSTANCE_ID" "$HOST" "$PASSWORD" || exit 1
HOST="$OPS_HOST"
PASSWORD="$OPS_PASSWORD"

info "获取 $HOST 进程信息..."

sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p "$PORT" "$USER@$HOST" << REMOTE
echo ""
echo "========== CPU 占用 TOP $TOP_N =========="
ps aux --sort=-%cpu | head -$((TOP_N + 1))

echo ""
echo "========== 内存占用 TOP $TOP_N =========="
ps aux --sort=-%mem | head -$((TOP_N + 1))

if [ -n "$FILTER" ]; then
    echo ""
    echo "========== 进程过滤: $FILTER =========="
    ps aux | grep -i "$FILTER" | grep -v grep
fi

echo ""
echo "========== 系统资源 =========="
echo "进程总数:   \$(ps aux | wc -l)"
echo "运行中:     \$(ps aux | awk '\$8=="R"' | wc -l)"
echo "僵尸进程:   \$(ps aux | awk '\$8=="Z"' | wc -l)"
echo "系统负载:   \$(cat /proc/loadavg | awk '{print \$1, \$2, \$3}')"
REMOTE

success "进程信息获取完成"
