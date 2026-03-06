#!/bin/bash
# 查询腾讯云镜像列表
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../common.sh"

show_help() {
    cat <<EOF
用法: $(basename "$0") [选项]

查询腾讯云镜像列表

选项:
  --region <region>           地域，默认 $DEFAULT_REGION
  --instance-type <type>      指定实例机型，返回与该机型兼容的镜像（重要！）
                              示例: S5.MEDIUM2, SA2.SMALL1
  --platform <platform>       平台: TencentOS/CentOS/Ubuntu/Debian
  --image-type <type>         类型: PUBLIC_IMAGE/PRIVATE_IMAGE/SHARED_IMAGE
  --image-id <id>             指定镜像 ID 查询
  --name <name>               按镜像名称模糊搜索
  --limit <n>                 返回数量，默认 20
  --json                      输出原始 JSON
  -h, --help                  显示帮助

重要说明:
  机型与镜像存在兼容性限制，创建实例时建议先用 --instance-type 查询兼容镜像。
  工作流程: 
    1. describe-instance-types.sh 选择机型
    2. describe-images.sh --instance-type <机型> 查询兼容镜像
    3. create-instance.sh --instance-type <机型> --image-id <镜像>

示例:
  $(basename "$0")                                    # 查询公共镜像
  $(basename "$0") --instance-type S5.MEDIUM2        # 查询 S5.MEDIUM2 兼容的镜像
  $(basename "$0") --instance-type SA2.SMALL1 --platform Ubuntu  # 组合过滤
  $(basename "$0") --platform CentOS --limit 10      # 按平台过滤
EOF
}

# 检查依赖
check_api_prerequisites
load_defaults

# 参数
INSTANCE_TYPE="" PLATFORM="" IMAGE_TYPE="PUBLIC_IMAGE" IMAGE_ID="" NAME="" LIMIT=20 JSON_OUTPUT=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --region) REGION="$2"; shift 2 ;;
        --instance-type) INSTANCE_TYPE="$2"; shift 2 ;;
        --platform) PLATFORM="$2"; shift 2 ;;
        --image-type|--type) IMAGE_TYPE="$2"; shift 2 ;;
        --image-id) IMAGE_ID="$2"; shift 2 ;;
        --name) NAME="$2"; shift 2 ;;
        --limit) LIMIT="$2"; shift 2 ;;
        --json) JSON_OUTPUT=true; shift ;;
        -h|--help) show_help; exit 0 ;;
        *) error "未知选项: $1"; show_help; exit 1 ;;
    esac
done

validate_region "$REGION"
[[ -n "$PLATFORM" ]] && validate_platform "$PLATFORM"

# 构建查询参数
EXTRA_ARGS=()
EXTRA_ARGS+=(--Limit "$LIMIT")

# 指定实例机型（查询兼容镜像）
if [[ -n "$INSTANCE_TYPE" ]]; then
    EXTRA_ARGS+=(--InstanceType "$INSTANCE_TYPE")
    info "查询与机型 $INSTANCE_TYPE 兼容的镜像 (地域: $REGION)..."
else
    info "查询镜像 (地域: $REGION, 类型: $IMAGE_TYPE)..."
fi

# 构建过滤条件
FILTERS=()
FILTERS+=("{\"Name\":\"image-type\",\"Values\":[\"$IMAGE_TYPE\"]}")
[[ -n "$PLATFORM" ]] && FILTERS+=("{\"Name\":\"platform\",\"Values\":[\"$PLATFORM\"]}")
[[ -n "$IMAGE_ID" ]] && FILTERS+=("{\"Name\":\"image-id\",\"Values\":[\"$IMAGE_ID\"]}")
[[ -n "$NAME" ]] && FILTERS+=("{\"Name\":\"image-name\",\"Values\":[\"$NAME\"]}")

FILTERS_JSON=$(IFS=,; echo "[${FILTERS[*]}]")
EXTRA_ARGS+=(--Filters "$FILTERS_JSON")

result=$(execute_tccli cvm DescribeImages --region "$REGION" "${EXTRA_ARGS[@]}")

if [[ "$JSON_OUTPUT" == "true" ]]; then
    echo "$result" | jq '.'
    exit 0
fi

# 格式化输出
total=$(echo "$result" | jq -r '.TotalCount')
returned=$(echo "$result" | jq '.ImageSet | length')

if [[ -n "$INSTANCE_TYPE" ]]; then
    print_section "兼容 $INSTANCE_TYPE 的镜像 (共 $total 个)"
else
    print_section "镜像列表 (共 $total 个)"
fi

echo ""
printf "%-20s %-12s %-8s %s\n" "镜像ID" "平台" "架构" "名称"
printf "%-20s %-12s %-8s %s\n" "------" "----" "----" "----"

echo "$result" | jq -r '.ImageSet[] | "\(.ImageId)\t\(.Platform)\t\(.Architecture)\t\(.ImageName)"' | \
    while IFS=$'\t' read -r id platform arch name; do
        # 截断过长的名称
        [[ ${#name} -gt 40 ]] && name="${name:0:37}..."
        printf "%-20s %-12s %-8s %s\n" "$id" "$platform" "$arch" "$name"
    done

echo ""
if [[ -n "$INSTANCE_TYPE" ]]; then
    success "共 $total 个兼容镜像，返回 $returned 个"
    echo ""
    info "提示: 使用 --image-id <ID> 查看镜像详情"
else
    success "共 $total 个镜像，返回 $returned 个"
fi
