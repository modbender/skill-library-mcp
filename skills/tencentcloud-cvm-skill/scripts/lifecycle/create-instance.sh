#!/bin/bash
# 创建腾讯云 CVM 实例（四步流程：确认参数 → 询价 → 预检查 → 创建）
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../common.sh"

show_help() {
    cat <<EOF
用法: $(basename "$0") [选项]

创建腾讯云 CVM 实例

流程: 确认参数 → 询价确认 → 参数预检查 → 实际创建

选项:
  --region <region>       地域，默认 $DEFAULT_REGION
  --zone <zone>           可用区（必需）
  --instance-type <type>  实例规格（必需）
  --image-id <id>         镜像 ID（必需）
  --name <name>           实例名称，默认自动生成
  --disk-size <n>         系统盘大小(GB)，默认 $DEFAULT_DISK_SIZE
  --data-disk-size <n>    数据盘大小(GB)，不指定则不创建
  --vpc-id <id>           VPC ID（必需）
  --subnet-id <id>        子网 ID（必需）
  --sg-id <id>            安全组 ID（必需）
  --charge-type <type>    计费: POSTPAID_BY_HOUR(默认)/PREPAID
  --config <file>         JSON 配置文件
  -h, --help              显示帮助

默认配置:
  - 公网 IP: 自动分配 (5Mbps, 按流量计费)
  - 密码: 自动生成并保存到本地

示例:
  $(basename "$0") --zone ap-guangzhou-3 --instance-type S5.MEDIUM2 \\
    --image-id img-xxx --vpc-id vpc-xxx --subnet-id subnet-xxx --sg-id sg-xxx
EOF
}

check_api_prerequisites
load_defaults

INSTANCE_NAME="" CONFIG_FILE=""
DATA_DISK_SIZE=""  # 默认不创建数据盘

while [[ $# -gt 0 ]]; do
    case "$1" in
        --region) REGION="$2"; shift 2 ;;
        --zone) ZONE="$2"; shift 2 ;;
        --instance-type) INSTANCE_TYPE="$2"; shift 2 ;;
        --image-id) IMAGE_ID="$2"; shift 2 ;;
        --name) INSTANCE_NAME="$2"; shift 2 ;;
        --disk-size) DISK_SIZE="$2"; shift 2 ;;
        --data-disk-size) DATA_DISK_SIZE="$2"; shift 2 ;;
        --vpc-id) VPC_ID="$2"; shift 2 ;;
        --subnet-id) SUBNET_ID="$2"; shift 2 ;;
        --sg-id) SG_ID="$2"; shift 2 ;;
        --charge-type) CHARGE_TYPE="$2"; shift 2 ;;
        --config) CONFIG_FILE="$2"; shift 2 ;;
        -h|--help) show_help; exit 0 ;;
        *) error "未知选项: $1"; show_help; exit 1 ;;
    esac
done

# 加载配置文件
[[ -n "$CONFIG_FILE" ]] && { info "加载配置: $CONFIG_FILE"; load_config_file "$CONFIG_FILE"; }

validate_region "$REGION"

# 检查必需参数
missing=()
[[ -z "$ZONE" ]] && missing+=("--zone")
[[ -z "$INSTANCE_TYPE" ]] && missing+=("--instance-type")
[[ -z "$IMAGE_ID" ]] && missing+=("--image-id")
[[ -z "$VPC_ID" ]] && missing+=("--vpc-id")
[[ -z "$SUBNET_ID" ]] && missing+=("--subnet-id")
[[ -z "$SG_ID" ]] && missing+=("--sg-id")

if [[ ${#missing[@]} -gt 0 ]]; then
    error "缺少必需参数: ${missing[*]}"
    echo ""
    echo "获取参数值："
    echo "  机型:   ./scripts/query/describe-instance-types.sh --zone <zone>"
    echo "  镜像:   ./scripts/query/describe-images.sh --instance-type <type>"
    echo "  VPC:    ./scripts/query/describe-vpcs.sh"
    echo "  子网:   ./scripts/query/describe-subnets.sh --vpc-id <vpc>"
    echo "  安全组: ./scripts/query/describe-security-groups.sh"
    exit 1
fi

# 自动生成名称和密码
[[ -z "$INSTANCE_NAME" ]] && INSTANCE_NAME="cvm-$(date +%Y%m%d%H%M%S)"
PASSWORD=$(generate_password)

# 构建公共 API 参数
PLACEMENT="{\"Zone\":\"$ZONE\"}"
SYSTEM_DISK="{\"DiskType\":\"CLOUD_PREMIUM\",\"DiskSize\":$DISK_SIZE}"
VPC="{\"VpcId\":\"$VPC_ID\",\"SubnetId\":\"$SUBNET_ID\"}"
SECURITY_GROUPS="[\"$SG_ID\"]"
LOGIN_SETTINGS="{\"Password\":\"$PASSWORD\"}"
INTERNET_ACCESSIBLE="{\"InternetChargeType\":\"TRAFFIC_POSTPAID_BY_HOUR\",\"InternetMaxBandwidthOut\":5,\"PublicIpAssigned\":true}"

# 数据盘参数
DATA_DISKS=""
[[ -n "$DATA_DISK_SIZE" ]] && DATA_DISKS="[{\"DiskType\":\"CLOUD_PREMIUM\",\"DiskSize\":$DATA_DISK_SIZE}]"

#=============================================================================
# Step 1: 确认参数
#=============================================================================
print_section "Step 1/4: 确认配置"
cat <<EOF
名称:       $INSTANCE_NAME
地域:       $REGION
可用区:     $ZONE
规格:       $INSTANCE_TYPE
镜像:       $IMAGE_ID
系统盘:     ${DISK_SIZE}GB (CLOUD_PREMIUM)
数据盘:     ${DATA_DISK_SIZE:-不创建}
VPC:        $VPC_ID
子网:       $SUBNET_ID
安全组:     $SG_ID
计费:       $CHARGE_TYPE
公网:       自动分配 (5Mbps, 按流量计费)
密码:       $PASSWORD
EOF
echo "=================================="

confirm "配置确认无误?" || { info "已取消"; exit 0; }

#=============================================================================
# Step 2: 询价
#=============================================================================
print_section "Step 2/4: 询价"
info "正在查询价格..."

# 构建询价命令
INQUIRY_CMD=(tccli cvm InquiryPriceRunInstances --region "$REGION"
    --Placement "$PLACEMENT"
    --InstanceType "$INSTANCE_TYPE"
    --ImageId "$IMAGE_ID"
    --SystemDisk "$SYSTEM_DISK"
    --VirtualPrivateCloud "$VPC"
    --InternetAccessible "$INTERNET_ACCESSIBLE"
    --InstanceChargeType "$CHARGE_TYPE"
)
[[ -n "$DATA_DISKS" ]] && INQUIRY_CMD+=(--DataDisks "$DATA_DISKS")

inquiry_result=$("${INQUIRY_CMD[@]}" 2>&1)

# 检查询价是否成功
error_code=$(echo "$inquiry_result" | jq -r '.Error.Code // empty')
if [[ -n "$error_code" ]]; then
    error "询价失败: [$error_code] $(echo "$inquiry_result" | jq -r '.Error.Message')"
    exit 1
fi

# 解析价格
if [[ "$CHARGE_TYPE" == "PREPAID" ]]; then
    # 包年包月
    original_price=$(echo "$inquiry_result" | jq -r '.Price.InstancePrice.OriginalPrice // 0')
    discount_price=$(echo "$inquiry_result" | jq -r '.Price.InstancePrice.DiscountPrice // 0')
    bandwidth_price=$(echo "$inquiry_result" | jq -r '.Price.BandwidthPrice.OriginalPrice // 0')
    echo ""
    echo "实例价格:   ￥${discount_price} (原价 ￥${original_price})"
    echo "带宽价格:   按流量计费"
    echo "总价:       ￥${discount_price}"
else
    # 按量计费
    unit_price=$(echo "$inquiry_result" | jq -r '.Price.InstancePrice.UnitPrice // 0')
    unit_price_discount=$(echo "$inquiry_result" | jq -r '.Price.InstancePrice.UnitPriceDiscount // 0')
    charge_unit=$(echo "$inquiry_result" | jq -r '.Price.InstancePrice.ChargeUnit // "HOUR"')
    echo ""
    echo "实例价格:   ￥${unit_price_discount}/小时 (原价 ￥${unit_price}/小时)"
    echo "带宽价格:   按流量计费 (￥0.80/GB)"
    echo "预估日费:   ￥$(echo "$unit_price_discount * 24" | bc) (不含流量)"
fi
echo ""

confirm "价格确认，继续创建?" || { info "已取消"; exit 0; }

#=============================================================================
# Step 3: DryRun 预检查
#=============================================================================
print_section "Step 3/4: 参数预检查"
info "正在验证参数合法性..."

# 构建 DryRun 命令
DRYRUN_CMD=(tccli cvm RunInstances --region "$REGION"
    --Placement "$PLACEMENT"
    --InstanceType "$INSTANCE_TYPE"
    --ImageId "$IMAGE_ID"
    --InstanceName "$INSTANCE_NAME"
    --SystemDisk "$SYSTEM_DISK"
    --VirtualPrivateCloud "$VPC"
    --SecurityGroupIds "$SECURITY_GROUPS"
    --InstanceChargeType "$CHARGE_TYPE"
    --LoginSettings "$LOGIN_SETTINGS"
    --InternetAccessible "$INTERNET_ACCESSIBLE"
    --DryRun True
)
[[ -n "$DATA_DISKS" ]] && DRYRUN_CMD+=(--DataDisks "$DATA_DISKS")

dryrun_result=$("${DRYRUN_CMD[@]}" 2>&1)

# DryRun 成功时返回 DryRunOperation 错误码
error_code=$(echo "$dryrun_result" | jq -r '.Error.Code // empty')
if [[ "$error_code" == "DryRunOperation" ]]; then
    success "参数验证通过"
elif [[ -n "$error_code" ]]; then
    error "参数验证失败: [$error_code] $(echo "$dryrun_result" | jq -r '.Error.Message')"
    exit 1
else
    success "参数验证通过"
fi

#=============================================================================
# Step 4: 实际创建
#=============================================================================
print_section "Step 4/4: 创建实例"

confirm "开始创建实例?" || { info "已取消"; exit 0; }

info "正在创建实例..."

# 构建创建命令
CREATE_CMD=(tccli cvm RunInstances --region "$REGION"
    --Placement "$PLACEMENT"
    --InstanceType "$INSTANCE_TYPE"
    --ImageId "$IMAGE_ID"
    --InstanceName "$INSTANCE_NAME"
    --SystemDisk "$SYSTEM_DISK"
    --VirtualPrivateCloud "$VPC"
    --SecurityGroupIds "$SECURITY_GROUPS"
    --InstanceChargeType "$CHARGE_TYPE"
    --LoginSettings "$LOGIN_SETTINGS"
    --InternetAccessible "$INTERNET_ACCESSIBLE"
)
[[ -n "$DATA_DISKS" ]] && CREATE_CMD+=(--DataDisks "$DATA_DISKS")

create_result=$("${CREATE_CMD[@]}" 2>&1)

# 检查创建结果
error_code=$(echo "$create_result" | jq -r '.Error.Code // empty')
if [[ -n "$error_code" ]]; then
    error "创建失败: [$error_code] $(echo "$create_result" | jq -r '.Error.Message')"
    exit 1
fi

INSTANCE_ID=$(echo "$create_result" | jq -r '.InstanceIdSet[0]')

echo ""
success "实例创建成功!"
echo ""
echo "=================================="
echo "实例 ID:  $INSTANCE_ID"
echo "密码:     $PASSWORD"
echo "=================================="

# 保存密码到本地文件
save_instance_password "$INSTANCE_ID" "$PASSWORD" "" "$REGION"

echo ""
info "后续操作:"
echo "  1. 等待实例运行后更新 IP:"
echo "     ./scripts/utils/update-instance-ip.sh --instance-id $INSTANCE_ID --auto"
echo ""
echo "  2. SSH 连接:"
echo "     ./scripts/ops/ssh-connect.sh --instance-id $INSTANCE_ID"
