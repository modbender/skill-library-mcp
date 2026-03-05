#!/bin/bash
# 查询腾讯云实例机型配置
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../common.sh"

show_help() {
    cat <<EOF
用法: $(basename "$0") [选项]

查询腾讯云实例机型配置列表

选项:
  --region <region>     地域，默认 $DEFAULT_REGION
  --zone <zone>         按可用区过滤，如 ap-guangzhou-6
  --family <family>     按机型系列过滤，如 S5, S6, SA2, M5
  --type <type>         按实例类型过滤，如 S5.MEDIUM2
  --json                输出原始 JSON
  -h, --help            显示帮助

示例:
  $(basename "$0")                              # 查询默认地域所有机型
  $(basename "$0") --zone ap-guangzhou-3        # 查询指定可用区机型
  $(basename "$0") --family S5                  # 查询 S5 系列机型
  $(basename "$0") --family S5 --zone ap-guangzhou-3  # 组合过滤
EOF
}

# 检查依赖
check_api_prerequisites
load_defaults

# 参数
ZONE="" FAMILY="" TYPE="" JSON_OUTPUT=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --region) REGION="$2"; shift 2 ;;
        --zone) ZONE="$2"; shift 2 ;;
        --family) FAMILY="$2"; shift 2 ;;
        --type) TYPE="$2"; shift 2 ;;
        --json) JSON_OUTPUT=true; shift ;;
        -h|--help) show_help; exit 0 ;;
        *) error "未知选项: $1"; show_help; exit 1 ;;
    esac
done

validate_region "$REGION"

# 构建过滤条件
FILTERS=()
[[ -n "$ZONE" ]] && FILTERS+=("{\"Name\":\"zone\",\"Values\":[\"$ZONE\"]}")
[[ -n "$FAMILY" ]] && FILTERS+=("{\"Name\":\"instance-family\",\"Values\":[\"$FAMILY\"]}")
[[ -n "$TYPE" ]] && FILTERS+=("{\"Name\":\"instance-type\",\"Values\":[\"$TYPE\"]}")

info "查询实例机型 (地域: $REGION)..."

if [[ ${#FILTERS[@]} -gt 0 ]]; then
    FILTERS_JSON=$(IFS=,; echo "[${FILTERS[*]}]")
    result=$(execute_tccli cvm DescribeInstanceTypeConfigs --region "$REGION" --Filters "$FILTERS_JSON")
else
    result=$(execute_tccli cvm DescribeInstanceTypeConfigs --region "$REGION")
fi

if [[ "$JSON_OUTPUT" == "true" ]]; then
    echo "$result" | jq '.'
    exit 0
fi

# 格式化输出
total=$(echo "$result" | jq '.InstanceTypeConfigSet | length')

print_section "实例机型列表"
printf "%-20s %-10s %6s %8s %s\n" "机型" "系列" "CPU" "内存" "可用区"
printf "%-20s %-10s %6s %8s %s\n" "----" "----" "---" "----" "------"

echo "$result" | jq -r '.InstanceTypeConfigSet[] | "\(.InstanceType)\t\(.InstanceFamily)\t\(.CPU)\t\(.Memory)\t\(.Zone)"' | \
    sort -t$'\t' -k2,2 -k3,3n | \
    while IFS=$'\t' read -r type family cpu mem zone; do
        printf "%-20s %-10s %4s核 %6sGB %s\n" "$type" "$family" "$cpu" "$mem" "$zone"
    done

echo ""
success "共 $total 个机型"
