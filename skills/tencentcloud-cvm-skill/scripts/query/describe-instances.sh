#!/bin/bash
# describe-instances.sh - 查询腾讯云 CVM 实例列表

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../common.sh"

show_help() {
    print_help_header "describe-instances.sh" "查询腾讯云 CVM 实例列表"
    cat <<EOF
  --region <region>       地域，默认 $DEFAULT_REGION
  --instance-id <id>      按实例 ID 过滤
  --name <name>           按名称过滤（模糊）
  --limit <n>             返回数量，默认 20
  -h, --help              显示帮助

示例:
  $0
  $0 --instance-id ins-xxx
  $0 --region ap-beijing --limit 50

EOF
}

check_api_prerequisites
load_defaults

INSTANCE_ID="" NAME="" LIMIT=20

while [[ $# -gt 0 ]]; do
    case $1 in
        --region)      REGION="$2"; shift 2 ;;
        --instance-id) INSTANCE_ID="$2"; shift 2 ;;
        --name)        NAME="$2"; shift 2 ;;
        --limit)       LIMIT="$2"; shift 2 ;;
        -h|--help)     show_help; exit 0 ;;
        *)             error "未知参数: $1"; exit 1 ;;
    esac
done

validate_region "$REGION"

info "查询实例列表 (地域: $REGION)..."

# 构建参数
ARGS="--region $REGION --Limit $LIMIT"
[[ -n "$INSTANCE_ID" ]] && ARGS="$ARGS --InstanceIds '[\"$INSTANCE_ID\"]'"
[[ -n "$NAME" ]] && ARGS="$ARGS --Filters '[{\"Name\":\"instance-name\",\"Values\":[\"$NAME\"]}]'"

result=$(eval "execute_tccli cvm DescribeInstances $ARGS")

total=$(echo "$result" | jq -r '.TotalCount')
print_section "实例列表 (共 $total 个)"
echo ""

echo "$result" | jq -r '.InstanceSet[] | 
    "实例 ID:    \(.InstanceId)\n" +
    "名称:       \(.InstanceName)\n" +
    "状态:       \(.InstanceState)\n" +
    "规格:       \(.InstanceType)\n" +
    "内网 IP:    \(.PrivateIpAddresses // ["无"] | join(", "))\n" +
    "公网 IP:    \(.PublicIpAddresses // ["无"] | join(", "))\n" +
    "可用区:     \(.Placement.Zone)\n" +
    "----------------------------------------"'

success "查询完成"
