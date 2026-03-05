#!/bin/bash
# network-check.sh - 远程服务器网络检查

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../common.sh"

show_help() {
    print_help_header "network-check.sh" "远程服务器网络检查"
    cat <<EOF
  --instance-id <id>      实例 ID（自动获取密码和 IP）
  --host <ip>             IP 地址
  --user <user>           用户名，默认 root
  --password <pwd>        密码
  --target <host>         连通性测试目标
  -h, --help              显示帮助

示例:
  $0 --instance-id ins-xxx
  $0 --instance-id ins-xxx --target www.baidu.com

EOF
}

check_ssh_prerequisites

INSTANCE_ID="" HOST="" USER="root" PORT=22 PASSWORD="" TARGET=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --instance-id) INSTANCE_ID="$2"; shift 2 ;;
        --host)        HOST="$2"; shift 2 ;;
        --user)        USER="$2"; shift 2 ;;
        --password)    PASSWORD="$2"; shift 2 ;;
        --target)      TARGET="$2"; shift 2 ;;
        -h|--help)     show_help; exit 0 ;;
        *)             error "未知参数: $1"; exit 1 ;;
    esac
done

resolve_ops_connection "$INSTANCE_ID" "$HOST" "$PASSWORD" || exit 1
HOST="$OPS_HOST"
PASSWORD="$OPS_PASSWORD"

info "检查 $HOST 网络状态..."

sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p "$PORT" "$USER@$HOST" << REMOTE
echo ""
echo "========== 网络接口 =========="
ip addr show 2>/dev/null | grep -E "^[0-9]+:|inet " || ifconfig 2>/dev/null | grep -E "^[a-z]|inet "

echo ""
echo "========== 路由表 =========="
ip route show 2>/dev/null || route -n 2>/dev/null

echo ""
echo "========== DNS =========="
cat /etc/resolv.conf | grep -v "^#"

echo ""
echo "========== 监听端口 =========="
ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null

echo ""
echo "========== 活跃连接 TOP 10 =========="
ss -tn 2>/dev/null | awk 'NR>1 {print \$5}' | cut -d: -f1 | sort | uniq -c | sort -rn | head -10

echo ""
echo "========== 外网连通性 =========="
ping -c 2 -W 2 114.114.114.114 &>/dev/null && echo "114.114.114.114: OK" || echo "114.114.114.114: FAIL"
ping -c 2 -W 2 8.8.8.8 &>/dev/null && echo "8.8.8.8: OK" || echo "8.8.8.8: FAIL"

if [ -n "$TARGET" ]; then
    echo ""
    echo "========== 目标测试: $TARGET =========="
    ping -c 3 -W 2 $TARGET
fi
REMOTE

success "网络检查完成"
