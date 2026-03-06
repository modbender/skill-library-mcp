#!/bin/bash
# terminate-instance.sh - 销毁腾讯云 CVM 实例

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../common.sh"

show_help() {
    print_help_header "terminate-instance.sh" "销毁腾讯云 CVM 实例"
    cat <<EOF
  --instance-id <id>      实例 ID（必需）
  --region <region>       地域
  --force                 跳过确认
  -h, --help              显示帮助

警告: 此操作不可逆！

示例:
  $0 --instance-id ins-xxx

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

# 危险操作确认
echo ""
warn "========== 危险操作 =========="
warn "即将销毁: $INSTANCE_ID"
warn "地域: $REGION"
warn "此操作不可逆！"
warn "=============================="
echo ""

if [[ "$FORCE" != "true" ]]; then
    confirm "确认销毁?" || { info "已取消"; exit 0; }
    
    read -p "请输入实例 ID 确认: " -r confirm_id
    [[ "$confirm_id" != "$INSTANCE_ID" ]] && { error "ID 不匹配，已取消"; exit 1; }
fi

info "销毁实例 $INSTANCE_ID ..."
execute_tccli cvm TerminateInstances --region "$REGION" --InstanceIds "[\"$INSTANCE_ID\"]" > /dev/null

success "销毁请求已发送"

# 删除本地密码记录
delete_instance_password "$INSTANCE_ID" 2>/dev/null || true
