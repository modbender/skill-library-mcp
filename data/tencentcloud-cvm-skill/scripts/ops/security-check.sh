#!/bin/bash
# security-check.sh - 远程服务器安全检查

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../common.sh"

show_help() {
    print_help_header "security-check.sh" "远程服务器安全检查"
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

info "对 $HOST 进行安全检查..."

sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p "$PORT" "$USER@$HOST" << 'REMOTE'
echo ""
echo "========== SSH 配置 =========="
echo -n "Root 登录:    "; grep -E "^PermitRootLogin" /etc/ssh/sshd_config 2>/dev/null || echo "默认允许"
echo -n "密码认证:     "; grep -E "^PasswordAuthentication" /etc/ssh/sshd_config 2>/dev/null || echo "默认启用"
echo -n "SSH 端口:     "; grep -E "^Port" /etc/ssh/sshd_config 2>/dev/null || echo "22"

echo ""
echo "========== 防火墙 =========="
if command -v ufw &>/dev/null; then
    ufw status 2>/dev/null | head -5
elif command -v firewall-cmd &>/dev/null; then
    firewall-cmd --state 2>/dev/null
else
    iptables -L -n 2>/dev/null | head -10 || echo "无法获取"
fi

echo ""
echo "========== 监听端口 =========="
ss -tlnp 2>/dev/null | head -15 || netstat -tlnp 2>/dev/null | head -15

echo ""
echo "========== 最近登录 =========="
last -10 2>/dev/null || echo "无法获取"

echo ""
echo "========== 失败登录 =========="
grep -i "failed\|invalid" /var/log/auth.log 2>/dev/null | tail -5 || \
grep -i "failed\|invalid" /var/log/secure 2>/dev/null | tail -5 || \
echo "无记录"

echo ""
echo "========== 可疑进程 =========="
ps aux | grep -E "nc -l|ncat|cryptominer|xmrig" | grep -v grep || echo "未发现"

echo ""
echo "========== 定时任务 =========="
crontab -l 2>/dev/null || echo "无"

echo ""
echo "========== 可登录用户 =========="
grep -E "/bin/bash|/bin/sh" /etc/passwd | cut -d: -f1,3
REMOTE

success "安全检查完成"
