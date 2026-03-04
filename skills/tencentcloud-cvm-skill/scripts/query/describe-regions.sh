#!/bin/bash
# 查询腾讯云地域列表
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../common.sh"

show_help() {
    cat <<EOF
用法: $(basename "$0") [选项]

查询腾讯云支持的地域列表

选项:
  --available    仅显示可用地域
  --json         输出原始 JSON
  -h, --help     显示帮助

示例:
  $(basename "$0")              # 查询所有地域
  $(basename "$0") --available  # 仅查询可用地域
EOF
}

# 参数解析
AVAILABLE_ONLY=false
JSON_OUTPUT=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --available) AVAILABLE_ONLY=true; shift ;;
        --json) JSON_OUTPUT=true; shift ;;
        -h|--help) show_help; exit 0 ;;
        *) error "未知选项: $1"; show_help; exit 1 ;;
    esac
done

# 检查依赖
check_api_prerequisites

# 查询地域
info "查询地域列表..."
result=$(execute_tccli cvm DescribeRegions)

if [[ "$JSON_OUTPUT" == "true" ]]; then
    echo "$result" | jq '.'
    exit 0
fi

# 过滤并格式化输出
if [[ "$AVAILABLE_ONLY" == "true" ]]; then
    regions=$(echo "$result" | jq -r '.RegionSet[] | select(.RegionState == "AVAILABLE") | "\(.Region)\t\(.RegionName)"')
else
    regions=$(echo "$result" | jq -r '.RegionSet[] | "\(.Region)\t\(.RegionName)\t\(.RegionState)"')
fi

total=$(echo "$result" | jq '.TotalCount')
available=$(echo "$result" | jq '[.RegionSet[] | select(.RegionState == "AVAILABLE")] | length')

print_section "地域列表"
if [[ "$AVAILABLE_ONLY" == "true" ]]; then
    printf "%-20s %s\n" "地域ID" "地域名称"
    printf "%-20s %s\n" "------" "--------"
    echo "$regions" | while IFS=$'\t' read -r region name; do
        printf "%-20s %s\n" "$region" "$name"
    done
else
    printf "%-20s %-20s %s\n" "地域ID" "地域名称" "状态"
    printf "%-20s %-20s %s\n" "------" "--------" "----"
    echo "$regions" | while IFS=$'\t' read -r region name state; do
        printf "%-20s %-20s %s\n" "$region" "$name" "$state"
    done
fi

echo ""
success "共 $total 个地域，$available 个可用"
