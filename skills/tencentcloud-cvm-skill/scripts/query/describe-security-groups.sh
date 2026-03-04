#!/bin/bash
# describe-security-groups.sh - 查询腾讯云安全组列表

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../common.sh"

show_help() {
    print_help_header "describe-security-groups.sh" "查询腾讯云安全组列表"
    cat <<EOF
  --region <region>       地域，默认 $DEFAULT_REGION
  --sg-id <id>            按安全组 ID 过滤
  --name <name>           按名称过滤（模糊）
  --limit <n>             返回数量，默认 20
  -h, --help              显示帮助

示例:
  $0
  $0 --sg-id sg-xxx
  $0 --name default

EOF
}

check_api_prerequisites
load_defaults

SG_ID="" SG_NAME="" LIMIT=20

while [[ $# -gt 0 ]]; do
    case $1 in
        --region)  REGION="$2"; shift 2 ;;
        --sg-id)   SG_ID="$2"; shift 2 ;;
        --name)    SG_NAME="$2"; shift 2 ;;
        --limit)   LIMIT="$2"; shift 2 ;;
        -h|--help) show_help; exit 0 ;;
        *)         error "未知参数: $1"; exit 1 ;;
    esac
done

validate_region "$REGION"

info "查询安全组 (地域: $REGION)..."

ARGS="--region $REGION --Limit $LIMIT"
[[ -n "$SG_ID" ]] && ARGS="$ARGS --SecurityGroupIds '[\"$SG_ID\"]'"
[[ -n "$SG_NAME" ]] && ARGS="$ARGS --Filters '[{\"Name\":\"security-group-name\",\"Values\":[\"$SG_NAME\"]}]'"

result=$(eval "execute_tccli vpc DescribeSecurityGroups $ARGS")

total=$(echo "$result" | jq -r '.TotalCount')
print_section "安全组列表 (共 $total 个)"
echo ""

echo "$result" | jq -r '.SecurityGroupSet[] | 
    "安全组 ID:  \(.SecurityGroupId)\n" +
    "名称:       \(.SecurityGroupName)\n" +
    "描述:       \(.SecurityGroupDesc // "无")\n" +
    "默认:       \(if .IsDefault then "是" else "否" end)\n" +
    "----------------------------------------"'

success "查询完成"
