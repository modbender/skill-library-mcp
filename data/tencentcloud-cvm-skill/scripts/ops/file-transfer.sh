#!/bin/bash
# file-transfer.sh - 文件上传/下载

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../common.sh"

show_help() {
    print_help_header "file-transfer.sh" "远程文件上传/下载"
    cat <<EOF
  --instance-id <id>      实例 ID（自动获取密码和 IP）
  --host <ip>             IP 地址
  --user <user>           用户名，默认 root
  --password <pwd>        密码
  --upload                上传模式
  --download              下载模式
  --local <path>          本地路径（必需）
  --remote <path>         远程路径（必需）
  -h, --help              显示帮助

示例:
  # 上传
  $0 --instance-id ins-xxx --upload --local ./app.tar.gz --remote /opt/
  # 下载
  $0 --instance-id ins-xxx --download --remote /var/log/app.log --local ./

EOF
}

check_ssh_prerequisites

INSTANCE_ID="" HOST="" USER="root" PORT=22 PASSWORD=""
MODE="" LOCAL_PATH="" REMOTE_PATH=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --instance-id) INSTANCE_ID="$2"; shift 2 ;;
        --host)        HOST="$2"; shift 2 ;;
        --user)        USER="$2"; shift 2 ;;
        --password)    PASSWORD="$2"; shift 2 ;;
        --upload)      MODE="upload"; shift ;;
        --download)    MODE="download"; shift ;;
        --local)       LOCAL_PATH="$2"; shift 2 ;;
        --remote)      REMOTE_PATH="$2"; shift 2 ;;
        -h|--help)     show_help; exit 0 ;;
        *)             error "未知参数: $1"; exit 1 ;;
    esac
done

[[ -z "$MODE" ]] && { error "请指定 --upload 或 --download"; exit 1; }
[[ -z "$LOCAL_PATH" ]] && { error "缺少 --local"; exit 1; }
[[ -z "$REMOTE_PATH" ]] && { error "缺少 --remote"; exit 1; }

resolve_ops_connection "$INSTANCE_ID" "$HOST" "$PASSWORD" || exit 1
HOST="$OPS_HOST"
PASSWORD="$OPS_PASSWORD"

SCP_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -P $PORT"

if [[ "$MODE" == "upload" ]]; then
    [[ ! -e "$LOCAL_PATH" ]] && { error "本地文件不存在: $LOCAL_PATH"; exit 1; }
    info "上传 $LOCAL_PATH -> $HOST:$REMOTE_PATH ..."
    
    if [[ -d "$LOCAL_PATH" ]]; then
        sshpass -p "$PASSWORD" scp -r $SCP_OPTS "$LOCAL_PATH" "$USER@$HOST:$REMOTE_PATH"
    else
        sshpass -p "$PASSWORD" scp $SCP_OPTS "$LOCAL_PATH" "$USER@$HOST:$REMOTE_PATH"
    fi
    [[ $? -eq 0 ]] && success "上传完成" || { error "上传失败"; exit 1; }
else
    info "下载 $HOST:$REMOTE_PATH -> $LOCAL_PATH ..."
    sshpass -p "$PASSWORD" scp -r $SCP_OPTS "$USER@$HOST:$REMOTE_PATH" "$LOCAL_PATH"
    [[ $? -eq 0 ]] && success "下载完成" || { error "下载失败"; exit 1; }
fi
