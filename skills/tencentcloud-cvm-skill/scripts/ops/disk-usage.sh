#!/bin/bash
# disk-usage.sh - 检查远程服务器磁盘使用情况

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../common.sh"

show_help() {
    print_help_header "disk-usage.sh" "检查远程服务器磁盘使用情况"
    cat <<EOF
  --instance-id <id>      实例 ID（自动获取密码和 IP）
  --host <ip>             IP 地址
  --user <user>           用户名，默认 root
  --password <pwd>        密码
  --threshold <n>         告警阈值（百分比），默认 80
  -h, --help              显示帮助

示例:
  $0 --instance-id ins-xxx
  $0 --instance-id ins-xxx --threshold 90

EOF
}

check_ssh_prerequisites

INSTANCE_ID="" HOST="" USER="root" PORT=22 PASSWORD="" THRESHOLD=80

while [[ $# -gt 0 ]]; do
    case $1 in
        --instance-id) INSTANCE_ID="$2"; shift 2 ;;
        --host)        HOST="$2"; shift 2 ;;
        --user)        USER="$2"; shift 2 ;;
        --password)    PASSWORD="$2"; shift 2 ;;
        --threshold)   THRESHOLD="$2"; shift 2 ;;
        -h|--help)     show_help; exit 0 ;;
        *)             error "未知参数: $1"; exit 1 ;;
    esac
done

resolve_ops_connection "$INSTANCE_ID" "$HOST" "$PASSWORD" || exit 1
HOST="$OPS_HOST"
PASSWORD="$OPS_PASSWORD"

info "检查 $HOST 磁盘使用情况 (告警阈值: ${THRESHOLD}%)..."

sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p "$PORT" "$USER@$HOST" << REMOTE
echo ""
echo "========== 磁盘使用情况 =========="
df -h | head -1
df -h | grep -E '^/dev' | while read line; do
    usage=\$(echo "\$line" | awk '{print \$5}' | tr -d '%')
    if [ "\$usage" -ge "$THRESHOLD" ]; then
        echo -e "\033[0;31m\$line [警告]\033[0m"
    else
        echo "\$line"
    fi
done

echo ""
echo "========== 大文件 TOP 10 =========="
find / -type f -size +100M 2>/dev/null | head -10 | xargs ls -lh 2>/dev/null || echo "无大文件"

echo ""
echo "========== 目录空间 TOP 10 =========="
du -sh /* 2>/dev/null | sort -rh | head -10
REMOTE

success "磁盘检查完成"
