#!/bin/bash
# 根据使用场景智能推荐服务器配置
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../common.sh"

show_help() {
    cat <<EOF
用法: $(basename "$0") [选项]

根据使用场景智能推荐服务器配置

选项:
  --scene <scene>         使用场景（见下方列表）
  --region <region>       地域，默认 $DEFAULT_REGION
  --list-scenes           列出所有预设场景
  -h, --help              显示帮助

预设场景:
  blog-small      个人博客/小型网站 (日PV < 5000)
  blog-medium     中型博客/企业官网 (日PV 5000-50000)
  web-small       小型 Web 应用 (日PV < 10000)
  web-medium      中型 Web 应用 (日PV 10000-100000)
  web-large       大型 Web 应用 (日PV > 100000)
  api-small       小型 API 服务 (QPS < 100)
  api-medium      中型 API 服务 (QPS 100-1000)
  dev             开发测试环境
  database-small  小型数据库 (数据量 < 10GB)
  database-medium 中型数据库 (数据量 10-100GB)
  ai-inference    AI 推理服务

示例:
  $(basename "$0") --scene blog-small
  $(basename "$0") --scene web-medium --region ap-shanghai
  $(basename "$0") --list-scenes
EOF
}

list_scenes() {
    cat <<EOF
可用场景列表:

场景ID            适用场景                    推荐配置              预估月费
─────────────────────────────────────────────────────────────────────────────
blog-small        个人博客 (日PV<5K)          1核1G                 ~¥30
blog-medium       中型博客 (日PV 5K-50K)      2核4G                 ~¥100
web-small         小型Web (日PV<10K)          2核2G                 ~¥60
web-medium        中型Web (日PV 10K-100K)     4核8G                 ~¥200
web-large         大型Web (日PV>100K)         8核16G                ~¥400
api-small         小型API (QPS<100)           2核4G                 ~¥100
api-medium        中型API (QPS 100-1000)      4核8G                 ~¥200
dev               开发测试                     2核2G                 ~¥60
database-small    小型数据库 (<10GB)          2核4G + 50G数据盘     ~¥130
database-medium   中型数据库 (10-100GB)       4核16G + 200G数据盘   ~¥350
ai-inference      AI推理                       8核32G                ~¥600
─────────────────────────────────────────────────────────────────────────────

使用: $(basename "$0") --scene <场景ID>
EOF
}

# 场景配置映射
get_scene_config() {
    local scene="$1"
    
    case "$scene" in
        blog-small)
            SCENE_NAME="个人博客/小型网站"
            SCENE_DESC="适合日访问量 5000 以下的个人博客、小型展示网站"
            REC_CPU=1
            REC_MEM=1
            REC_INSTANCE_FAMILIES="SA2 S5"
            REC_DISK_SIZE=20
            REC_DATA_DISK=""
            REC_PLATFORM="TencentOS"
            ;;
        blog-medium)
            SCENE_NAME="中型博客/企业官网"
            SCENE_DESC="适合日访问量 5000-50000 的博客、企业官网、小型电商"
            REC_CPU=2
            REC_MEM=4
            REC_INSTANCE_FAMILIES="SA2 S5"
            REC_DISK_SIZE=40
            REC_DATA_DISK=""
            REC_PLATFORM="TencentOS"
            ;;
        web-small)
            SCENE_NAME="小型 Web 应用"
            SCENE_DESC="适合日 PV 10000 以下的 Web 应用、小程序后端"
            REC_CPU=2
            REC_MEM=2
            REC_INSTANCE_FAMILIES="SA2 S5"
            REC_DISK_SIZE=40
            REC_DATA_DISK=""
            REC_PLATFORM="TencentOS"
            ;;
        web-medium)
            SCENE_NAME="中型 Web 应用"
            SCENE_DESC="适合日 PV 10000-100000 的 Web 应用、API 网关"
            REC_CPU=4
            REC_MEM=8
            REC_INSTANCE_FAMILIES="S5 SA3"
            REC_DISK_SIZE=50
            REC_DATA_DISK=""
            REC_PLATFORM="TencentOS"
            ;;
        web-large)
            SCENE_NAME="大型 Web 应用"
            SCENE_DESC="适合日 PV 100000 以上的高并发 Web 应用"
            REC_CPU=8
            REC_MEM=16
            REC_INSTANCE_FAMILIES="S5 S6"
            REC_DISK_SIZE=50
            REC_DATA_DISK=""
            REC_PLATFORM="TencentOS"
            ;;
        api-small)
            SCENE_NAME="小型 API 服务"
            SCENE_DESC="适合 QPS 100 以下的 API 服务、微服务节点"
            REC_CPU=2
            REC_MEM=4
            REC_INSTANCE_FAMILIES="SA2 S5"
            REC_DISK_SIZE=40
            REC_DATA_DISK=""
            REC_PLATFORM="TencentOS"
            ;;
        api-medium)
            SCENE_NAME="中型 API 服务"
            SCENE_DESC="适合 QPS 100-1000 的 API 服务、中型微服务集群"
            REC_CPU=4
            REC_MEM=8
            REC_INSTANCE_FAMILIES="S5 SA3"
            REC_DISK_SIZE=50
            REC_DATA_DISK=""
            REC_PLATFORM="TencentOS"
            ;;
        dev)
            SCENE_NAME="开发测试环境"
            SCENE_DESC="适合开发、测试、学习用途"
            REC_CPU=2
            REC_MEM=2
            REC_INSTANCE_FAMILIES="SA2 S5"
            REC_DISK_SIZE=40
            REC_DATA_DISK=""
            REC_PLATFORM="Ubuntu"
            ;;
        database-small)
            SCENE_NAME="小型数据库"
            SCENE_DESC="适合数据量 10GB 以下的 MySQL/PostgreSQL/MongoDB"
            REC_CPU=2
            REC_MEM=4
            REC_INSTANCE_FAMILIES="S5 SA3"
            REC_DISK_SIZE=40
            REC_DATA_DISK=50
            REC_PLATFORM="TencentOS"
            ;;
        database-medium)
            SCENE_NAME="中型数据库"
            SCENE_DESC="适合数据量 10-100GB 的数据库，需要较好的 IO 性能"
            REC_CPU=4
            REC_MEM=16
            REC_INSTANCE_FAMILIES="S5 S6"
            REC_DISK_SIZE=50
            REC_DATA_DISK=200
            REC_PLATFORM="TencentOS"
            ;;
        ai-inference)
            SCENE_NAME="AI 推理服务"
            SCENE_DESC="适合中小规模 AI 模型推理（CPU）"
            REC_CPU=8
            REC_MEM=32
            REC_INSTANCE_FAMILIES="S5 S6 M5"
            REC_DISK_SIZE=50
            REC_DATA_DISK=100
            REC_PLATFORM="Ubuntu"
            ;;
        *)
            error "未知场景: $scene"
            echo "使用 --list-scenes 查看可用场景"
            exit 1
            ;;
    esac
}

# 查找可用实例类型
find_instance_type() {
    local region="$1" zone="$2" cpu="$3" mem="$4" families="$5"
    
    # 遍历推荐的实例族
    for family in $families; do
        # 查询该族的实例类型
        local result
        result=$(tccli cvm DescribeInstanceTypeConfigs --region "$region" \
            --Filters "[{\"Name\":\"zone\",\"Values\":[\"$zone\"]},{\"Name\":\"instance-family\",\"Values\":[\"$family\"]}]" 2>/dev/null || echo '{"InstanceTypeConfigSet":[]}')
        
        # 查找匹配 CPU 和内存的实例类型
        local instance_type
        instance_type=$(echo "$result" | jq -r --argjson cpu "$cpu" --argjson mem "$mem" \
            '.InstanceTypeConfigSet[] | select(.CPU == $cpu and .Memory == $mem) | .InstanceType' | head -1)
        
        if [[ -n "$instance_type" ]]; then
            echo "$instance_type"
            return 0
        fi
    done
    
    # 如果精确匹配失败，尝试找接近的配置
    for family in $families; do
        local result
        result=$(tccli cvm DescribeInstanceTypeConfigs --region "$region" \
            --Filters "[{\"Name\":\"zone\",\"Values\":[\"$zone\"]},{\"Name\":\"instance-family\",\"Values\":[\"$family\"]}]" 2>/dev/null || echo '{"InstanceTypeConfigSet":[]}')
        
        # 找 CPU >= 推荐且内存 >= 推荐的最小配置
        local instance_type
        instance_type=$(echo "$result" | jq -r --argjson cpu "$cpu" --argjson mem "$mem" \
            '[.InstanceTypeConfigSet[] | select(.CPU >= $cpu and .Memory >= $mem)] | sort_by(.CPU, .Memory) | .[0].InstanceType // empty')
        
        if [[ -n "$instance_type" ]]; then
            echo "$instance_type"
            return 0
        fi
    done
    
    return 1
}

# 查找可用镜像
find_image() {
    local region="$1" instance_type="$2" platform="$3"
    
    local result
    result=$(tccli cvm DescribeImages --region "$region" \
        --InstanceType "$instance_type" \
        --Filters "[{\"Name\":\"image-type\",\"Values\":[\"PUBLIC_IMAGE\"]},{\"Name\":\"platform\",\"Values\":[\"$platform\"]}]" \
        --Limit 10 2>/dev/null || echo '{"ImageSet":[]}')
    
    # 优先选择最新的 LTS/稳定版
    local image_id
    image_id=$(echo "$result" | jq -r '.ImageSet[0].ImageId // empty')
    
    if [[ -n "$image_id" ]]; then
        local image_name
        image_name=$(echo "$result" | jq -r '.ImageSet[0].ImageName // empty')
        echo "$image_id|$image_name"
        return 0
    fi
    
    return 1
}

# 获取默认 VPC 和子网
get_default_vpc() {
    local region="$1" zone="$2"
    
    # 查询 VPC
    local vpc_result
    vpc_result=$(tccli vpc DescribeVpcs --region "$region" --Limit 10 2>/dev/null || echo '{"VpcSet":[]}')
    local vpc_id
    vpc_id=$(echo "$vpc_result" | jq -r '.VpcSet[0].VpcId // empty')
    
    [[ -z "$vpc_id" ]] && return 1
    
    # 查询该可用区的子网
    local subnet_result
    subnet_result=$(tccli vpc DescribeSubnets --region "$region" \
        --Filters "[{\"Name\":\"vpc-id\",\"Values\":[\"$vpc_id\"]},{\"Name\":\"zone\",\"Values\":[\"$zone\"]}]" 2>/dev/null || echo '{"SubnetSet":[]}')
    local subnet_id
    subnet_id=$(echo "$subnet_result" | jq -r '.SubnetSet[0].SubnetId // empty')
    
    [[ -z "$subnet_id" ]] && return 1
    
    echo "$vpc_id|$subnet_id"
}

# 获取默认安全组
get_default_sg() {
    local region="$1"
    
    local sg_result
    sg_result=$(tccli vpc DescribeSecurityGroups --region "$region" --Limit 10 2>/dev/null || echo '{"SecurityGroupSet":[]}')
    local sg_id
    sg_id=$(echo "$sg_result" | jq -r '.SecurityGroupSet[0].SecurityGroupId // empty')
    
    [[ -z "$sg_id" ]] && return 1
    echo "$sg_id"
}

# 获取可用区
get_available_zone() {
    local region="$1"
    
    local zone_result
    zone_result=$(tccli cvm DescribeZones --region "$region" 2>/dev/null || echo '{"ZoneSet":[]}')
    local zone
    zone=$(echo "$zone_result" | jq -r '.ZoneSet[] | select(.ZoneState == "AVAILABLE") | .Zone' | head -1)
    
    [[ -z "$zone" ]] && return 1
    echo "$zone"
}

#=============================================================================
# 主流程
#=============================================================================

check_api_prerequisites
load_defaults

SCENE="" LIST_SCENES=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --scene) SCENE="$2"; shift 2 ;;
        --region) REGION="$2"; shift 2 ;;
        --list-scenes) LIST_SCENES=true; shift ;;
        -h|--help) show_help; exit 0 ;;
        *) error "未知选项: $1"; show_help; exit 1 ;;
    esac
done

if [[ "$LIST_SCENES" == "true" ]]; then
    list_scenes
    exit 0
fi

if [[ -z "$SCENE" ]]; then
    error "请指定场景: --scene <scene>"
    echo ""
    list_scenes
    exit 1
fi

validate_region "$REGION"

# 获取场景配置
get_scene_config "$SCENE"

print_section "场景分析"
echo "场景:     $SCENE_NAME"
echo "说明:     $SCENE_DESC"
echo ""
echo "推荐配置: ${REC_CPU}核 ${REC_MEM}GB"
echo "系统盘:   ${REC_DISK_SIZE}GB"
[[ -n "$REC_DATA_DISK" ]] && echo "数据盘:   ${REC_DATA_DISK}GB"
echo "系统:     $REC_PLATFORM"
echo "=================================="
echo ""

info "正在查询可用资源 (地域: $REGION)..."

# Step 1: 获取可用区
ZONE=$(get_available_zone "$REGION")
if [[ -z "$ZONE" ]]; then
    error "未找到可用区"
    exit 1
fi
success "可用区: $ZONE"

# Step 2: 查找实例类型
INSTANCE_TYPE=$(find_instance_type "$REGION" "$ZONE" "$REC_CPU" "$REC_MEM" "$REC_INSTANCE_FAMILIES")
if [[ -z "$INSTANCE_TYPE" ]]; then
    error "未找到合适的实例类型"
    echo "请尝试其他地域或手动选择配置"
    exit 1
fi
success "实例类型: $INSTANCE_TYPE"

# Step 3: 查找镜像
IMAGE_INFO=$(find_image "$REGION" "$INSTANCE_TYPE" "$REC_PLATFORM")
if [[ -z "$IMAGE_INFO" ]]; then
    error "未找到兼容镜像"
    exit 1
fi
IMAGE_ID=$(echo "$IMAGE_INFO" | cut -d'|' -f1)
IMAGE_NAME=$(echo "$IMAGE_INFO" | cut -d'|' -f2)
success "镜像: $IMAGE_ID ($IMAGE_NAME)"

# Step 4: 获取网络配置
VPC_INFO=$(get_default_vpc "$REGION" "$ZONE")
if [[ -z "$VPC_INFO" ]]; then
    error "未找到可用的 VPC/子网"
    echo "请先创建 VPC 和子网，或使用 describe-vpcs.sh 查询"
    exit 1
fi
VPC_ID=$(echo "$VPC_INFO" | cut -d'|' -f1)
SUBNET_ID=$(echo "$VPC_INFO" | cut -d'|' -f2)
success "VPC: $VPC_ID"
success "子网: $SUBNET_ID"

# Step 5: 获取安全组
SG_ID=$(get_default_sg "$REGION")
if [[ -z "$SG_ID" ]]; then
    error "未找到安全组"
    echo "请先创建安全组"
    exit 1
fi
success "安全组: $SG_ID"

echo ""
print_section "推荐配置汇总"
cat <<EOF
场景:       $SCENE_NAME
地域:       $REGION
可用区:     $ZONE
实例类型:   $INSTANCE_TYPE (${REC_CPU}核${REC_MEM}G)
镜像:       $IMAGE_ID
            ($IMAGE_NAME)
系统盘:     ${REC_DISK_SIZE}GB
数据盘:     ${REC_DATA_DISK:-不创建}
VPC:        $VPC_ID
子网:       $SUBNET_ID
安全组:     $SG_ID
计费:       按量付费
EOF
echo "=================================="
echo ""

confirm "是否使用此配置创建实例?" || { info "已取消"; exit 0; }

# 构建创建命令
CREATE_ARGS="--region $REGION --zone $ZONE --instance-type $INSTANCE_TYPE --image-id $IMAGE_ID --vpc-id $VPC_ID --subnet-id $SUBNET_ID --sg-id $SG_ID --disk-size $REC_DISK_SIZE"
[[ -n "$REC_DATA_DISK" ]] && CREATE_ARGS="$CREATE_ARGS --data-disk-size $REC_DATA_DISK"

# 调用创建脚本
echo ""
exec "$SCRIPT_DIR/create-instance.sh" $CREATE_ARGS
