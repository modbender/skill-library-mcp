#!/bin/bash
# describe-vpcs.sh - 查询腾讯云 VPC 列表

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../common.sh"

show_help() {
    print_help_header "describe-vpcs.sh" "查询腾讯云 VPC 列表"
    cat <<EOF
  --region <region>       地域，默认 $DEFAULT_REGION
  --vpc-id <id>           按 VPC ID 过滤
  --limit <n>             返回数量，默认 20
  -h, --help              显示帮助

示例:
  $0
  $0 --vpc-id vpc-xxx

EOF
}

check_api_prerequisites
load_defaults

VPC_ID="" LIMIT=20

while [[ $# -gt 0 ]]; do
    case $1 in
        --region)  REGION="$2"; shift 2 ;;
        --vpc-id)  VPC_ID="$2"; shift 2 ;;
        --limit)   LIMIT="$2"; shift 2 ;;
        -h|--help) show_help; exit 0 ;;
        *)         error "未知参数: $1"; exit 1 ;;
    esac
done

validate_region "$REGION"

info "查询 VPC (地域: $REGION)..."

ARGS="--region $REGION --Limit $LIMIT"
[[ -n "$VPC_ID" ]] && ARGS="$ARGS --VpcIds '[\"$VPC_ID\"]'"

result=$(eval "execute_tccli vpc DescribeVpcs $ARGS")

total=$(echo "$result" | jq -r '.TotalCount')
print_section "VPC 列表 (共 $total 个)"
echo ""

echo "$result" | jq -r '.VpcSet[] | 
    "VPC ID:     \(.VpcId)\n" +
    "名称:       \(.VpcName)\n" +
    "CIDR:       \(.CidrBlock)\n" +
    "默认:       \(if .IsDefault then "是" else "否" end)\n" +
    "----------------------------------------"'

success "查询完成"
