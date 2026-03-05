#!/bin/bash
# common.sh - 腾讯云 CVM 运维工具公共函数库
# 提供日志、检查、API 调用、SSH 连接等通用功能

set -o pipefail

#=============================================================================
# 常量定义
#=============================================================================

# 颜色
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

# 默认配置
readonly DEFAULT_REGION="ap-guangzhou"
readonly DEFAULT_CHARGE_TYPE="POSTPAID_BY_HOUR"
readonly DEFAULT_DISK_SIZE=20
readonly DEFAULT_DATA_DISK_SIZE=50
readonly DEFAULT_SSH_PORT=22
readonly DEFAULT_SSH_USER="root"

# 密码存储
CVM_PASSWORD_FILE="${TENCENT_CVM_PASSWORD_FILE:-$HOME/.tencent_cvm_passwords}"

# 支持的地域和平台
readonly SUPPORTED_REGIONS=("ap-beijing" "ap-shanghai" "ap-guangzhou" "ap-chengdu" "ap-nanjing" "ap-hongkong")
readonly SUPPORTED_PLATFORMS=("TencentOS" "CentOS" "Ubuntu" "Debian")

#=============================================================================
# 日志函数
#=============================================================================

info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
error()   { echo -e "${RED}[ERROR]${NC} $1" >&2; }

# 带分隔线的标题输出
print_section() {
    local title="$1"
    echo ""
    echo "========== $title =========="
}

#=============================================================================
# 依赖检查
#=============================================================================

# 检查 Python（tccli 依赖）
check_python_installed() {
    local python_cmd=""
    if command -v python3 &>/dev/null; then
        python_cmd="python3"
    elif command -v python &>/dev/null; then
        python_cmd="python"
    else
        error "Python 未安装，tccli 需要 Python 2.7+"
        echo "安装方式: brew install python3 (macOS) | apt install python3 (Linux)"
        exit 1
    fi
    
    local version major minor
    version=$($python_cmd -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    major=$(echo "$version" | cut -d. -f1)
    minor=$(echo "$version" | cut -d. -f2)
    
    if [[ "$major" -lt 2 ]] || { [[ "$major" -eq 2 ]] && [[ "$minor" -lt 7 ]]; }; then
        error "Python 版本过低: $version，需要 2.7+"
        exit 1
    fi
}

# 检查 tccli
check_tccli_installed() {
    check_python_installed
    if ! command -v tccli &>/dev/null; then
        error "tccli 未安装"
        echo "安装方式: pip install tccli"
        exit 1
    fi
}

# 检查 jq
check_jq_installed() {
    if ! command -v jq &>/dev/null; then
        error "jq 未安装"
        echo "安装方式: brew install jq (macOS) | apt install jq (Linux)"
        exit 1
    fi
}

# 检查 sshpass（SSH 密码认证需要）
check_sshpass_installed() {
    if ! command -v sshpass &>/dev/null; then
        error "sshpass 未安装（SSH 密码认证需要）"
        echo ""
        echo "安装方式:"
        echo "  macOS:   brew install hudochenkov/sshpass/sshpass"
        echo "  Ubuntu:  sudo apt install sshpass"
        echo "  CentOS:  sudo yum install sshpass"
        exit 1
    fi
}

# 检查腾讯云凭证
check_credentials() {
    [[ -z "$TENCENTCLOUD_SECRET_ID" ]] && { error "环境变量 TENCENTCLOUD_SECRET_ID 未设置"; exit 1; }
    [[ -z "$TENCENTCLOUD_SECRET_KEY" ]] && { error "环境变量 TENCENTCLOUD_SECRET_KEY 未设置"; exit 1; }
}

# API 操作前置检查
check_api_prerequisites() {
    check_tccli_installed
    check_jq_installed
    check_credentials
}

# SSH 操作前置检查
check_ssh_prerequisites() {
    check_jq_installed
    check_sshpass_installed
}

#=============================================================================
# 验证函数
#=============================================================================

# 验证地域
validate_region() {
    local region="$1"
    for r in "${SUPPORTED_REGIONS[@]}"; do
        [[ "$region" == "$r" ]] && return 0
    done
    error "不支持的地域: $region"
    echo "支持的地域: ${SUPPORTED_REGIONS[*]}"
    exit 1
}

# 验证镜像平台
validate_platform() {
    local platform="$1"
    for p in "${SUPPORTED_PLATFORMS[@]}"; do
        [[ "$platform" == "$p" ]] && return 0
    done
    error "不支持的平台: $platform"
    echo "支持的平台: ${SUPPORTED_PLATFORMS[*]}"
    exit 1
}

#=============================================================================
# 配置管理
#=============================================================================

# 加载默认配置（从环境变量）
load_defaults() {
    REGION="${TENCENT_CVM_DEFAULT_REGION:-$DEFAULT_REGION}"
    ZONE="${TENCENT_CVM_DEFAULT_ZONE:-}"
    INSTANCE_TYPE="${TENCENT_CVM_DEFAULT_INSTANCE_TYPE:-}"
    IMAGE_ID="${TENCENT_CVM_DEFAULT_IMAGE_ID:-}"
    DISK_SIZE="${TENCENT_CVM_DEFAULT_DISK_SIZE:-$DEFAULT_DISK_SIZE}"
    DATA_DISK_SIZE="${TENCENT_CVM_DEFAULT_DATA_DISK_SIZE:-}"
    VPC_ID="${TENCENT_CVM_DEFAULT_VPC_ID:-}"
    SUBNET_ID="${TENCENT_CVM_DEFAULT_SUBNET_ID:-}"
    SG_ID="${TENCENT_CVM_DEFAULT_SG_ID:-}"
    CHARGE_TYPE="${TENCENT_CVM_DEFAULT_CHARGE_TYPE:-$DEFAULT_CHARGE_TYPE}"
}

# 从 JSON 配置文件加载
load_config_file() {
    local config_file="$1"
    [[ ! -f "$config_file" ]] && { error "配置文件不存在: $config_file"; exit 1; }
    
    REGION=$(jq -r '.Region // empty' "$config_file")
    ZONE=$(jq -r '.Placement.Zone // empty' "$config_file")
    INSTANCE_TYPE=$(jq -r '.InstanceType // empty' "$config_file")
    IMAGE_ID=$(jq -r '.ImageId // empty' "$config_file")
    DISK_SIZE=$(jq -r '.SystemDisk.DiskSize // empty' "$config_file")
    DATA_DISK_SIZE=$(jq -r '.DataDisks[0].DiskSize // empty' "$config_file")
    VPC_ID=$(jq -r '.VirtualPrivateCloud.VpcId // empty' "$config_file")
    SUBNET_ID=$(jq -r '.VirtualPrivateCloud.SubnetId // empty' "$config_file")
    SG_ID=$(jq -r '.SecurityGroupIds[0] // empty' "$config_file")
    CHARGE_TYPE=$(jq -r '.InstanceChargeType // empty' "$config_file")
    INSTANCE_NAME=$(jq -r '.InstanceName // empty' "$config_file")
    
    load_defaults  # 用默认值填充空值
}

# 显示当前配置
show_current_defaults() {
    print_section "当前配置"
    cat <<EOF
地域:       ${REGION:-未设置}
可用区:     ${ZONE:-未设置}
实例规格:   ${INSTANCE_TYPE:-未设置}
镜像 ID:    ${IMAGE_ID:-未设置}
系统盘:     ${DISK_SIZE}GB
数据盘:     ${DATA_DISK_SIZE:-不创建}
VPC:        ${VPC_ID:-未设置}
子网:       ${SUBNET_ID:-未设置}
安全组:     ${SG_ID:-未设置}
计费类型:   ${CHARGE_TYPE}
EOF
    echo "=================================="
}

#=============================================================================
# 密码生成与管理
#=============================================================================

# 生成符合腾讯云要求的随机密码（12-30位，包含大小写、数字、特殊字符）
generate_password() {
    local length=${1:-16}
    local upper="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    local lower="abcdefghijklmnopqrstuvwxyz"
    local digits="0123456789"
    local special="!@#\$%^&*"
    local all="${upper}${lower}${digits}${special}"
    
    # 确保至少包含每种字符
    local password=""
    password+="${upper:RANDOM%${#upper}:1}"
    password+="${lower:RANDOM%${#lower}:1}"
    password+="${digits:RANDOM%${#digits}:1}"
    password+="${special:RANDOM%${#special}:1}"
    
    # 填充并打乱
    for ((i=4; i<length; i++)); do
        password+="${all:RANDOM%${#all}:1}"
    done
    echo "$password" | fold -w1 | shuf | tr -d '\n'
}

# 初始化密码文件
init_password_file() {
    if [[ ! -f "$CVM_PASSWORD_FILE" ]]; then
        echo '{}' > "$CVM_PASSWORD_FILE"
        chmod 600 "$CVM_PASSWORD_FILE"
    fi
}

# 保存实例密码
save_instance_password() {
    local instance_id="$1" password="$2" host="${3:-}" region="${4:-}"
    init_password_file
    
    local current_data instance_info new_data
    current_data=$(cat "$CVM_PASSWORD_FILE" 2>/dev/null || echo '{}')
    
    instance_info=$(jq -n \
        --arg pwd "$password" \
        --arg host "$host" \
        --arg region "$region" \
        --arg created "$(date '+%Y-%m-%d %H:%M:%S')" \
        '{password: $pwd, host: $host, region: $region, created_at: $created}')
    
    new_data=$(echo "$current_data" | jq --arg id "$instance_id" --argjson info "$instance_info" '. + {($id): $info}')
    echo "$new_data" > "$CVM_PASSWORD_FILE"
    
    success "实例 $instance_id 密码已保存"
    info "密码: $password"
}

# 更新实例 IP
update_instance_host() {
    local instance_id="$1" host="$2"
    [[ ! -f "$CVM_PASSWORD_FILE" ]] && { error "密码文件不存在"; return 1; }
    
    local current_data exists new_data
    current_data=$(cat "$CVM_PASSWORD_FILE")
    exists=$(echo "$current_data" | jq --arg id "$instance_id" 'has($id)')
    
    [[ "$exists" != "true" ]] && { error "实例 $instance_id 不存在"; return 1; }
    
    new_data=$(echo "$current_data" | jq --arg id "$instance_id" --arg host "$host" '.[$id].host = $host')
    echo "$new_data" > "$CVM_PASSWORD_FILE"
    success "实例 $instance_id IP 已更新为 $host"
}

# 获取实例密码
get_instance_password() {
    local instance_id="$1"
    [[ ! -f "$CVM_PASSWORD_FILE" ]] && { error "密码文件不存在"; return 1; }
    
    local password
    password=$(jq -r --arg id "$instance_id" '.[$id].password // empty' "$CVM_PASSWORD_FILE")
    
    if [[ -z "$password" ]]; then
        error "未找到实例 $instance_id 的密码"
        echo "可用实例: $(jq -r 'keys | join(", ")' "$CVM_PASSWORD_FILE")" >&2
        return 1
    fi
    echo "$password"
}

# 获取实例 IP
get_instance_host() {
    local instance_id="$1"
    [[ ! -f "$CVM_PASSWORD_FILE" ]] && return 1
    jq -r --arg id "$instance_id" '.[$id].host // empty' "$CVM_PASSWORD_FILE"
}

# 获取实例完整信息
get_instance_info() {
    local instance_id="$1"
    [[ ! -f "$CVM_PASSWORD_FILE" ]] && { error "密码文件不存在"; return 1; }
    
    local info
    info=$(jq --arg id "$instance_id" '.[$id] // empty' "$CVM_PASSWORD_FILE")
    [[ -z "$info" || "$info" == "null" ]] && { error "未找到实例 $instance_id"; return 1; }
    echo "$info"
}

# 列出所有保存的实例
list_saved_instances() {
    [[ ! -f "$CVM_PASSWORD_FILE" ]] && { warn "暂无保存的实例"; return 0; }
    
    print_section "已保存的实例"
    jq -r 'to_entries[] | "  \(.key)  \(.value.host // "-")  \(.value.region // "-")"' "$CVM_PASSWORD_FILE"
    echo "=================================="
}

# 删除实例密码记录
delete_instance_password() {
    local instance_id="$1"
    [[ ! -f "$CVM_PASSWORD_FILE" ]] && { error "密码文件不存在"; return 1; }
    
    local new_data
    new_data=$(jq --arg id "$instance_id" 'del(.[$id])' "$CVM_PASSWORD_FILE")
    echo "$new_data" > "$CVM_PASSWORD_FILE"
    success "已删除实例 $instance_id"
}

#=============================================================================
# 工具函数
#=============================================================================

# 用户确认
confirm() {
    local message="${1:-确认继续?}"
    read -p "$message [y/N]: " -r response
    [[ "$response" =~ ^[yY]([eE][sS])?$ ]]
}

# 帮助信息头部
print_help_header() {
    local script_name="$1" description="$2"
    cat <<EOF

用法: $script_name [选项]

$description

选项:
EOF
}

#=============================================================================
# API 调用
#=============================================================================

# 执行 tccli 命令（带错误处理）
execute_tccli() {
    local result exit_code error_code error_message
    
    result=$(tccli "$@" 2>&1)
    exit_code=$?
    
    if [[ $exit_code -ne 0 ]]; then
        error "tccli 命令执行失败"
        echo "$result" >&2
        exit 1
    fi
    
    # 检查 API 错误
    error_code=$(echo "$result" | jq -r '.Error.Code // empty' 2>/dev/null)
    if [[ -n "$error_code" ]]; then
        error_message=$(echo "$result" | jq -r '.Error.Message // "未知错误"')
        error "API 错误: [$error_code] $error_message"
        exit 1
    fi
    
    echo "$result"
}

#=============================================================================
# SSH 连接
#=============================================================================

# 解析运维连接参数，设置 OPS_HOST 和 OPS_PASSWORD
resolve_ops_connection() {
    local instance_id="$1" host="$2" password="$3"
    
    OPS_HOST="$host"
    OPS_PASSWORD="$password"
    
    if [[ -n "$instance_id" ]]; then
        # 获取密码
        if [[ -z "$OPS_PASSWORD" ]]; then
            OPS_PASSWORD=$(get_instance_password "$instance_id") || return 1
        fi
        # 获取 IP
        if [[ -z "$OPS_HOST" ]]; then
            OPS_HOST=$(get_instance_host "$instance_id")
            if [[ -z "$OPS_HOST" ]]; then
                error "实例 $instance_id 未设置 IP"
                echo "请先执行: ./scripts/utils/update-instance-ip.sh --instance-id $instance_id --auto"
                return 1
            fi
        fi
    fi
    
    [[ -z "$OPS_HOST" ]] && { error "缺少目标主机 (--instance-id 或 --host)"; return 1; }
    [[ -z "$OPS_PASSWORD" ]] && { error "缺少密码 (--instance-id 或 --password)"; return 1; }
    return 0
}

# 构建 SSH 命令
build_ssh_cmd() {
    local host="$1" password="$2" user="${3:-root}" port="${4:-22}"
    echo "sshpass -p '$password' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p $port $user@$host"
}

# 构建 SCP 选项
build_scp_opts() {
    local port="${1:-22}"
    echo "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -P $port"
}

# 兼容旧函数名
check_prerequisites() { check_api_prerequisites; }
