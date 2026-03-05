#!/bin/bash
# update-instance-ip.sh - 更新实例 IP 地址

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../common.sh"

show_help() {
    print_help_header "update-instance-ip.sh" "更新实例 IP 到本地存储"
    cat <<EOF
  --instance-id <id>      实例 ID（必需）
  --host <ip>             IP 地址
  --auto                  自动从 API 获取
  -h, --help              显示帮助

示例:
  $0 --instance-id ins-xxx --host 1.2.3.4
  $0 --instance-id ins-xxx --auto

EOF
}

check_jq_installed

INSTANCE_ID="" HOST="" AUTO=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --instance-id) INSTANCE_ID="$2"; shift 2 ;;
        --host)        HOST="$2"; shift 2 ;;
        --auto)        AUTO=true; shift ;;
        -h|--help)     show_help; exit 0 ;;
        *)             error "未知参数: $1"; exit 1 ;;
    esac
done

[[ -z "$INSTANCE_ID" ]] && { error "缺少: --instance-id"; exit 1; }

# 自动获取 IP
if [[ "$AUTO" == "true" ]]; then
    check_api_prerequisites
    
    info "从 API 获取实例 IP..."
    
    REGION=$(jq -r --arg id "$INSTANCE_ID" '.[$id].region // empty' "$CVM_PASSWORD_FILE" 2>/dev/null)
    [[ -z "$REGION" ]] && { REGION="$DEFAULT_REGION"; warn "使用默认地域: $REGION"; }
    
    result=$(execute_tccli cvm DescribeInstances --region "$REGION" --InstanceIds "[\"$INSTANCE_ID\"]")
    
    HOST=$(echo "$result" | jq -r '.InstanceSet[0].PublicIpAddresses[0] // empty')
    if [[ -z "$HOST" ]]; then
        HOST=$(echo "$result" | jq -r '.InstanceSet[0].PrivateIpAddresses[0] // empty')
        [[ -n "$HOST" ]] && warn "无公网 IP，使用内网 IP"
    fi
    
    [[ -z "$HOST" ]] && { error "无法获取 IP"; exit 1; }
    success "获取到 IP: $HOST"
fi

[[ -z "$HOST" ]] && { error "缺少: --host 或 --auto"; exit 1; }

update_instance_host "$INSTANCE_ID" "$HOST"
