#!/bin/bash
# describe-zones.sh - 查询腾讯云可用区列表

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../common.sh"

show_help() {
    print_help_header "describe-zones.sh" "查询腾讯云可用区列表"
    cat <<EOF
  --region <region>       地域，默认 $DEFAULT_REGION
  -h, --help              显示帮助

示例:
  $0
  $0 --region ap-beijing

EOF
}

check_api_prerequisites
load_defaults

while [[ $# -gt 0 ]]; do
    case $1 in
        --region)  REGION="$2"; shift 2 ;;
        -h|--help) show_help; exit 0 ;;
        *)         error "未知参数: $1"; exit 1 ;;
    esac
done

validate_region "$REGION"

info "查询可用区 (地域: $REGION)..."

result=$(execute_tccli cvm DescribeZones --region "$REGION")

print_section "可用区列表"
echo "$result" | jq -r '.ZoneSet[] | "  \(.Zone)  \(.ZoneName)  \(.ZoneState)"'
echo ""
success "查询完成"
