#!/bin/bash
# describe-subnets.sh - 查询腾讯云子网列表

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../common.sh"

show_help() {
    print_help_header "describe-subnets.sh" "查询腾讯云子网列表"
    cat <<EOF
  --region <region>       地域，默认 $DEFAULT_REGION
  --vpc-id <id>           按 VPC ID 过滤
  --subnet-id <id>        按子网 ID 过滤
  --zone <zone>           按可用区过滤
  --limit <n>             返回数量，默认 20
  -h, --help              显示帮助

示例:
  $0
  $0 --vpc-id vpc-xxx
  $0 --zone ap-guangzhou-3

EOF
}

check_api_prerequisites
load_defaults

VPC_ID="" SUBNET_ID="" ZONE="" LIMIT=20

while [[ $# -gt 0 ]]; do
    case $1 in
        --region)    REGION="$2"; shift 2 ;;
        --vpc-id)    VPC_ID="$2"; shift 2 ;;
        --subnet-id) SUBNET_ID="$2"; shift 2 ;;
        --zone)      ZONE="$2"; shift 2 ;;
        --limit)     LIMIT="$2"; shift 2 ;;
        -h|--help)   show_help; exit 0 ;;
        *)           error "未知参数: $1"; exit 1 ;;
    esac
done

validate_region "$REGION"

info "查询子网 (地域: $REGION)..."

ARGS="--region $REGION --Limit $LIMIT"
[[ -n "$SUBNET_ID" ]] && ARGS="$ARGS --SubnetIds '[\"$SUBNET_ID\"]'"

# 构建过滤条件
FILTERS=()
[[ -n "$VPC_ID" ]] && FILTERS+=("{\"Name\":\"vpc-id\",\"Values\":[\"$VPC_ID\"]}")
[[ -n "$ZONE" ]] && FILTERS+=("{\"Name\":\"zone\",\"Values\":[\"$ZONE\"]}")

if [[ ${#FILTERS[@]} -gt 0 ]]; then
    FILTERS_JSON=$(IFS=,; echo "[${FILTERS[*]}]")
    ARGS="$ARGS --Filters '$FILTERS_JSON'"
fi

result=$(eval "execute_tccli vpc DescribeSubnets $ARGS")

total=$(echo "$result" | jq -r '.TotalCount')
print_section "子网列表 (共 $total 个)"
echo ""

echo "$result" | jq -r '.SubnetSet[] | 
    "子网 ID:    \(.SubnetId)\n" +
    "名称:       \(.SubnetName)\n" +
    "VPC:        \(.VpcId)\n" +
    "CIDR:       \(.CidrBlock)\n" +
    "可用区:     \(.Zone)\n" +
    "可用 IP:    \(.AvailableIpAddressCount)\n" +
    "----------------------------------------"'

success "查询完成"
