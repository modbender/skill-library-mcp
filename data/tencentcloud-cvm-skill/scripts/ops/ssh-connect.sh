#!/bin/bash
# ssh-connect.sh - SSH 连接到 CVM 实例

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../common.sh"

show_help() {
    print_help_header "ssh-connect.sh" "SSH 连接到 CVM 实例"
    cat <<EOF
  --instance-id <id>      实例 ID（自动获取密码和 IP）
  --host <ip>             IP 地址（覆盖保存的 IP）
  --user <user>           用户名，默认 root
  --port <port>           端口，默认 22
  --password <pwd>        密码（覆盖保存的密码）
  -h, --help              显示帮助

示例:
  $0 --instance-id ins-xxx
  $0 --instance-id ins-xxx --host 1.2.3.4
  $0 --host 1.2.3.4 --password 'xxx'

EOF
}

# 前置检查
check_ssh_prerequisites

# 参数
INSTANCE_ID="" HOST="" USER="root" PORT=22 PASSWORD=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --instance-id) INSTANCE_ID="$2"; shift 2 ;;
        --host)        HOST="$2"; shift 2 ;;
        --user)        USER="$2"; shift 2 ;;
        --port)        PORT="$2"; shift 2 ;;
        --password)    PASSWORD="$2"; shift 2 ;;
        -h|--help)     show_help; exit 0 ;;
        *)             error "未知参数: $1"; exit 1 ;;
    esac
done

# 解析连接信息
resolve_ops_connection "$INSTANCE_ID" "$HOST" "$PASSWORD" || exit 1
HOST="$OPS_HOST"
PASSWORD="$OPS_PASSWORD"

# 连接
info "连接到 $USER@$HOST:$PORT ..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p "$PORT" "$USER@$HOST"
