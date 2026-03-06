#!/bin/bash
# system-info.sh - 获取远程服务器系统信息

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../common.sh"

show_help() {
    print_help_header "system-info.sh" "获取远程服务器系统信息"
    cat <<EOF
  --instance-id <id>      实例 ID（自动获取密码和 IP）
  --host <ip>             IP 地址
  --user <user>           用户名，默认 root
  --password <pwd>        密码
  -h, --help              显示帮助

示例:
  $0 --instance-id ins-xxx

EOF
}

check_ssh_prerequisites

INSTANCE_ID="" HOST="" USER="root" PORT=22 PASSWORD=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --instance-id) INSTANCE_ID="$2"; shift 2 ;;
        --host)        HOST="$2"; shift 2 ;;
        --user)        USER="$2"; shift 2 ;;
        --password)    PASSWORD="$2"; shift 2 ;;
        -h|--help)     show_help; exit 0 ;;
        *)             error "未知参数: $1"; exit 1 ;;
    esac
done

resolve_ops_connection "$INSTANCE_ID" "$HOST" "$PASSWORD" || exit 1
HOST="$OPS_HOST"
PASSWORD="$OPS_PASSWORD"

info "获取 $HOST 系统信息..."

sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p "$PORT" "$USER@$HOST" << 'REMOTE'
echo ""
echo "========== 系统信息 =========="
echo "主机名:     $(hostname)"
echo "系统:       $(cat /etc/os-release 2>/dev/null | grep PRETTY_NAME | cut -d'"' -f2 || uname -s)"
echo "内核:       $(uname -r)"
echo "架构:       $(uname -m)"
echo "运行时间:   $(uptime -p 2>/dev/null || uptime)"

echo ""
echo "========== CPU =========="
echo "型号:       $(grep 'model name' /proc/cpuinfo | head -1 | cut -d':' -f2 | xargs)"
echo "核数:       $(nproc)"
echo "使用率:     $(top -bn1 | grep 'Cpu(s)' | awk '{print $2}')%"

echo ""
echo "========== 内存 =========="
free -h | awk 'NR==1{print "            "$1"    "$2"    "$3} NR==2{print "内存:       "$1"    "$2"    "$3}'

echo ""
echo "========== 磁盘 =========="
df -h | grep -E '^/dev|Filesystem' | head -10

echo ""
echo "========== 网络 =========="
echo "内网 IP:    $(hostname -I | awk '{print $1}')"
echo "外网 IP:    $(curl -s --connect-timeout 3 ifconfig.me 2>/dev/null || echo '获取失败')"

echo ""
echo "========== 负载 =========="
echo "系统负载:   $(cat /proc/loadavg | awk '{print $1, $2, $3}')"
echo "进程数:     $(ps aux | wc -l)"
REMOTE

success "系统信息获取完成"
