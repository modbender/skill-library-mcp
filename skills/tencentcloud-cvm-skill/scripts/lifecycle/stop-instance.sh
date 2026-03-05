#!/bin/bash
# stop-instance.sh - 停止腾讯云 CVM 实例

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../common.sh"

show_help() {
    print_help_header "stop-instance.sh" "停止腾讯云 CVM 实例"
    cat <<EOF
  --instance-id <id>      实例 ID（必需）
  --region <region>       地域
  --force                 强制停止
  -h, --help              显示帮助

示例:
  $0 --instance-id ins-xxx
  $0 --instance-id ins-xxx --force

EOF
}

check_api_prerequisites
load_defaults

INSTANCE_ID="" FORCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --instance-id) INSTANCE_ID="$2"; shift 2 ;;
        --region)      REGION="$2"; shift 2 ;;
        --force)       FORCE=true; shift ;;
        -h|--help)     show_help; exit 0 ;;
        *)             error "未知参数: $1"; exit 1 ;;
    esac
done

[[ -z "$INSTANCE_ID" ]] && { error "缺少: --instance-id"; exit 1; }
validate_region "$REGION"

STOP_TYPE="SOFT_FIRST"
[[ "$FORCE" == "true" ]] && STOP_TYPE="HARD"

info "停止实例 $INSTANCE_ID (模式: $STOP_TYPE)..."
execute_tccli cvm StopInstances --region "$REGION" --InstanceIds "[\"$INSTANCE_ID\"]" --StopType "$STOP_TYPE" > /dev/null

success "停止请求已发送"
