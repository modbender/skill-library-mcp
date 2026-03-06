#!/bin/bash
# start-instance.sh - 启动腾讯云 CVM 实例

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../common.sh"

show_help() {
    print_help_header "start-instance.sh" "启动腾讯云 CVM 实例"
    cat <<EOF
  --instance-id <id>      实例 ID（必需）
  --region <region>       地域
  -h, --help              显示帮助

示例:
  $0 --instance-id ins-xxx

EOF
}

check_api_prerequisites
load_defaults

INSTANCE_ID=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --instance-id) INSTANCE_ID="$2"; shift 2 ;;
        --region)      REGION="$2"; shift 2 ;;
        -h|--help)     show_help; exit 0 ;;
        *)             error "未知参数: $1"; exit 1 ;;
    esac
done

[[ -z "$INSTANCE_ID" ]] && { error "缺少: --instance-id"; exit 1; }
validate_region "$REGION"

info "启动实例 $INSTANCE_ID ..."
execute_tccli cvm StartInstances --region "$REGION" --InstanceIds "[\"$INSTANCE_ID\"]" > /dev/null

success "启动请求已发送"
info "请稍后查询实例状态确认启动完成"
